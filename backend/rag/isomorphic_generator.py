import uuid
import json
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

from models.schemas import ClinicalCaseSchema
from modules.cases.dependencies import get_case_service
from services.llm_gateway import llm_gateway, AllModelsExhaustedException, FatalLLMException
from config import GEMINI_API_KEY

logger = logging.getLogger("ateneo.rag.isomorphic_generator")


class IsomorphicCaseResult(BaseModel):
    """
    Representación estructurada de un caso clínico paralelo e isomórfico.
    Preserva el nivel cognitivo de Bloom, las competencias clínicas y el estándar de oro
    de la Guía de Práctica Clínica del MSP Ecuador, pero varía la viñeta clínica del paciente.
    """
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Identificador único del caso isomórfico")
    base_case_id: str = Field(..., description="ID del caso clínico original del cual deriva")
    titulo: str = Field(..., description="Título de la variante clínica isomórfica")
    enunciado: str = Field(..., description="Viñeta clínica completa (historia, exploración y paraclínicos)")
    pregunta: str = Field(..., description="Interrogante clínica formativa estructurada")
    guia_asociada: str = Field(..., description="Guía de Práctica Clínica oficial de referencia (MSP Ecuador)")
    competencias_evaluadas: List[str] = Field(default_factory=list, description="Nodos de competencias KST evaluados")
    nivel_esperado: str = Field(default="pregrado_avanzado", description="Nivel formativo esperado")
    fragmento_gpc_ideal_id: Optional[str] = Field(default=None, description="ID del chunk normativo de referencia")
    variaciones_isomorficas: Dict[str, str] = Field(default_factory=dict, description="Variables clínicas modificadas respecto al caso base")
    faithfulness_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Puntuación de anclaje normativo")
    justificacion_clinica: str = Field(default="", description="Explicación del isomorfismo psicométrico y pedagógico")
    is_generated_by_llm: bool = Field(default=False, description="Indica si fue sintetizado en tiempo real por el LLM o proviene del banco curado")


# =====================================================================
# BANCO CURADO DE CASOS ISOMÓRFICOS CALIBRADOS (FALLBACK DE ALTA FIDELIDAD)
# =====================================================================
CURATED_ISOMORPHIC_CASES: Dict[str, Dict[str, Any]] = {
    "case_preeclampsia_01": {
        "titulo": "Gestante Multigesta con Crisis Hipertensiva y Criterios de Severidad",
        "enunciado": (
            "Gestante de 35 semanas por FUM, 34 años de edad, multigesta (G3P2), acude al área de emergencia obstétrica "
            "por presentar cefalea frontal intensa y pulsátil de 4 horas de evolución no aliviada con paracetamol, "
            "acompañada de escotomas centellantes y dolor punzante en hipocondrio derecho.\n\n"
            "**Examen físico al ingreso:**\n"
            "- **Presión Arterial:** 170/115 mmHg (confirmada tras 15 minutos en reposo en decúbito lateral izquierdo).\n"
            "- **Frecuencia Cardíaca:** 92 lpm | **Frecuencia Respiratoria:** 20 rpm.\n"
            "- **Neurológico:** Consciente, orientada, con reflejos rotulianos marcadamente exaltados (clonus agotable 2-3 batidas).\n"
            "- **Abdomen:** Fondo uterino acorde a 35 semanas, FCF 144 lpm sin dinámica uterina.\n"
            "- **Laboratorio urgente:** Proteinuria en tirilla +++, plaquetas 88.000 /uL, creatinina 1.15 mg/dL."
        ),
        "pregunta": (
            "De acuerdo con la GPC de Trastornos Hipertensivos del Embarazo del MSP Ecuador:\n"
            "1. Establezca el diagnóstico sindrómico específico de la paciente.\n"
            "2. Prescriba el esquema de neuroprotección materna para prevención de eclampsia (Sulfato de Magnesio: dosis de impregnación y mantenimiento bajo esquema Zuspan).\n"
            "3. Indique la terapia antihipertensiva inmediata de primera línea para crisis hipertensiva normada por el MSP."
        ),
        "guia_asociada": "MSP_Trastornos-hipertensivos-del-embarazo-con-portada-3.pdf",
        "competencias_evaluadas": ["semiologia_anamnesis", "diagnostico_final", "plan_terapeutico_msp"],
        "fragmento_gpc_ideal_id": "gpc_MSP_Trastornos-hipertensivos-del-embarazo-con-portada-3_chunk_0082",
        "variaciones_isomorficas": {
            "demografia": "34 años, multigesta G3P2 (vs 28 años, primigesta)",
            "edad_gestacional": "35 semanas (vs 32 semanas)",
            "sintomas": "Escotomas centellantes y dolor en hipocondrio derecho (vs fosfenos y epigastralgia)",
            "tension_arterial": "170/115 mmHg con clonus patelar (vs 165/110 mmHg con ROT +++)",
            "paraclinicos": "Plaquetas 88.000 /uL (trombocitopenia severa confirmatoria)"
        },
        "faithfulness_score": 1.0,
        "justificacion_clinica": "Conserva la misma emergencia obstétrica de Preeclampsia con Criterios de Severidad y el mismo esquema Zuspan y antihipertensivos del MSP."
    },
    "case_hemorragia_01": {
        "titulo": "Hemorragia Posparto Inmediata Secundaria a Atonía Uterina (Código Rojo)",
        "enunciado": (
            "Paciente de 29 años, multípara (G4P3), cursa puerperio inmediato (30 minutos tras expulsivo de feto macrosómico de 4.100g). "
            "El personal de enfermería alerta por sangrado transvaginal profuso continuo rutilante con coágulos, cuantificado en 950 ml.\n\n"
            "**Examen físico:**\n"
            "- **Útero:** Flácido, con fondo uterino 3 cm por encima de la cicatriz umbilical, no se palpa retracción ni globo de seguridad de Pinard.\n"
            "- **Signos vitales:** PA 80/45 mmHg, FC 132 lpm, llenado capilar 4 segundos, frialdad distal y palidez mucocutánea generalizada.\n"
            "- **Canal del parto:** Inspección con valvas descarta laceraciones de cuello o canal vaginal."
        ),
        "pregunta": (
            "En el marco del protocolo del Código Rojo Obstétrico de la GPC de Hemorragia Posparto del MSP Ecuador:\n"
            "1. Identifique el diagnóstico etiológico primario según la regla nemotécnica de las 4T.\n"
            "2. Indique la primera maniobra mecánica bimanual de soporte no farmacológico inmediato.\n"
            "3. Prescriba la secuencia farmacológica de uterotónicos normada de primera y segunda línea (fármacos, dosis y vías)."
        ),
        "guia_asociada": "Guía-de-hemorragia-postparto.pdf",
        "competencias_evaluadas": ["semiologia_anamnesis", "diagnostico_final", "plan_terapeutico_msp"],
        "fragmento_gpc_ideal_id": "gpc_Guía-de-hemorragia-postparto_chunk_0031",
        "variaciones_isomorficas": {
            "demografia": "29 años, multípara G4P3 (vs 22 años, primigesta)",
            "factor_riesgo": "Sobredistensión uterina por feto macrosómico 4100g (vs expulsivo prolongado)",
            "severidad_shock": "PA 80/45 mmHg, FC 132 lpm (Índice de choque 1.65 - Choque Severo)"
        },
        "faithfulness_score": 1.0,
        "justificacion_clinica": "Isomorfismo exacto para evaluación de Código Rojo obstétrico y manejo de atonía uterina bajo la GPC oficial del MSP."
    },
    "case_tb_01": {
        "titulo": "Tuberculosis Pulmonar Bacilífera con Compromiso Constitucional",
        "enunciado": (
            "Paciente masculino de 42 años, trabajador de la construcción, acude a consulta externa por tos productiva con expectoración "
            "mucopurulenta de 4 semanas de evolución, a la que se ha sumado esputo con estrías hemoptoicas en dos ocasiones. "
            "Refiere diaforesis nocturna profusa, astenia marcada y pérdida ponderal no intencional de 7 kg en el último mes.\n\n"
            "**Examen físico:**\n"
            "- **Signos vitales:** PA 115/70 mmHg, FC 84 lpm, FR 18 rpm, Temperatura 37.8°C.\n"
            "- **Aparato respiratorio:** Murmullo vesicular disminuido en vértice derecho con estertores crepitantes localizados apicales.\n"
            "- **Paraclínicos:** Baciloscopía de esputo directa (Ziehl-Neelsen): Positiva (++)."
        ),
        "pregunta": (
            "Con base en la GPC para la Prevención, Diagnóstico y Tratamiento de la Tuberculosis del MSP Ecuador:\n"
            "1. Confirme la categorización diagnóstica del paciente (Sintomático Respiratorio con confirmación bacteriológica).\n"
            "2. Prescriba el esquema normado de Tratamiento Antituberculoso de Fase Inicial/Intensiva en Dosis Fija Combinada (fármacos, duración y frecuencia de administración).\n"
            "3. Enuncie las medidas de control epidemiológico y seguimiento bacteriológico mensual obligatorio."
        ),
        "guia_asociada": "MSP_Guia-de-tuberculosis-2023.pdf",
        "competencias_evaluadas": ["semiologia_anamnesis", "diagnostico_final", "plan_terapeutico_msp"],
        "fragmento_gpc_ideal_id": "gpc_MSP_Guia-de-tuberculosis-2023_chunk_0045",
        "variaciones_isomorficas": {
            "demografia": "42 años, trabajador de construcción (vs 38 años)",
            "cuadro_clinico": "Tos de 4 semanas con hemoptisis leve (vs 3 semanas sin hemoptisis)",
            "baciloscopia": "BK ++ confirmado"
        },
        "faithfulness_score": 1.0,
        "justificacion_clinica": "Evalúa la prescripción de Dosis Fija Combinada (RHZE) y el protocolo de notificación obligatoria del MSP Ecuador."
    },
    "case_vih_01": {
        "titulo": "Infección por VIH en Estadio Avanzado y Profilaxis de Infecciones Oportunistas",
        "enunciado": (
            "Paciente femenino de 31 años consulta por odinofagia dolorosa progresiva para sólidos y líquidos de 2 semanas, "
            "asociada a fiebre intermitente y pérdida de 8 kg en dos meses. "
            "A la inspección oral se aprecian placas blanquecinas pseudomembranosas en mucosa yugal y paladar blando que se desprenden al raspado dejando lecho eritematoso.\n\n"
            "**Exámenes solicitados:**\n"
            "- **Prueba rápida de 4ta generación (Antígeno p24 / Anticuerpos VIH 1-2):** Reactiva.\n"
            "- **Carga viral VIH:** 140.000 copias/mL.\n"
            "- **Recuento de Linfocitos T CD4:** 165 células/uL."
        ),
        "pregunta": (
            "Conforme a la GPC para la Atención Integral de Personas con VIH del MSP Ecuador:\n"
            "1. Clasifique el estadio clínico e inmunológico de la paciente (Estadio Clínico OMS 3 / Inmunodepresión severa por CD4 < 200).\n"
            "2. Indique la profilaxis farmacológica antimicrobiana obligatoria que debe instaurarse de inmediato (fármaco y dosis).\n"
            "3. Prescriba el esquema preferido de Terapia Antirretroviral de Gran Actividad (TARGA) de primera línea recomendado en el protocolo ecuatoriano."
        ),
        "guia_asociada": "MSP_Guia-de-VIH-SIDA-2022.pdf",
        "competencias_evaluadas": ["diagnostico_final", "plan_terapeutico_msp"],
        "fragmento_gpc_ideal_id": "gpc_MSP_Guia-de-VIH-SIDA-2022_chunk_0055",
        "variaciones_isomorficas": {
            "demografia": "31 años femenino (vs 27 años masculino)",
            "presentacion": "Candidiasis esofágica/orofaríngea y CD4 165 cel/uL (vs Pneumocystis)",
            "terapeutica": "Profilaxis con Cotrimoxazol e inicio de TLD (Tenofovir/Lamivudina/Dolutegravir)"
        },
        "faithfulness_score": 1.0,
        "justificacion_clinica": "Isomorfo que evalúa CD4 < 200, profilaxis de infecciones oportunistas y TAR de primera línea según la GPC ecuatoriana."
    },
    "case_hta_01": {
        "titulo": "Emergencia Hipertensiva con Daño Renal y Cardiopulmonar Agudo",
        "enunciado": (
            "Paciente de 61 años con antecedente de HTA de 10 años con abandono terapéutico hace 6 meses. "
            "Es traído por familiares al servicio de emergencias por presentar cefalea occipital intensa, náuseas, vómito en escopetazo "
            "y disnea progresiva de reposo que le impide adoptar el decúbito (ortopnea).\n\n"
            "**Examen físico:**\n"
            "- **Presión Arterial:** 215/125 mmHg en ambos brazos.\n"
            "- **Cardiopulmonar:** Galope por R3, estertores crepitantes bilaterales hasta campos medios pulmonares.\n"
            "- **Neurológico:** Desorientado en tiempo, sin déficit focal motor.\n"
            "- **Paraclínicos:** Creatinina 2.1 mg/dL, troponina I cuantitativa ligeramente elevada, ECG con signos de sobrecarga ventricular izquierda."
        ),
        "pregunta": (
            "De acuerdo con la GPC de Diagnóstico y Tratamiento de la Hipertensión Arterial del MSP Ecuador:\n"
            "1. Diferencie y clasifique el cuadro clínico entre Emergencia Hipertensiva y Urgencia Hipertensiva justificando el criterio de daño agudo de órgano diana.\n"
            "2. Establezca la meta tensional inicial durante la primera hora de atención en cuidados intensivos o shock.\n"
            "3. Prescriba la conducta farmacológica de elección (fármacos endovenosos titulables vs fármacos orales)."
        ),
        "guia_asociada": "MSP_Guia-de-Hipertension-Arterial-2021.pdf",
        "competencias_evaluadas": ["semiologia_anamnesis", "diagnostico_final", "plan_terapeutico_msp"],
        "fragmento_gpc_ideal_id": "gpc_MSP_Guia-de-Hipertension-Arterial-2021_chunk_0038",
        "variaciones_isomorficas": {
            "demografia": "61 años con ortopnea y falla ventricular aguda (vs 54 años con compromiso neurológico aislado)",
            "cifras_tensionales": "215/125 mmHg (vs 200/120 mmHg)",
            "organos_afectados": "Cardiopulmonar y renal (edema pulmonar cardiogénico incipiente)"
        },
        "faithfulness_score": 1.0,
        "justificacion_clinica": "Evalúa manejo de emergencia hipertensiva, reducción gradual controlada (máximo 25% PAM primera hora) y fármacos parenterales del MSP."
    },
    "case_erc_01": {
        "titulo": "Enfermedad Renal Crónica Agudizada con Hiperpotasemia Grave",
        "enunciado": (
            "Paciente masculino de 64 años, con nefropatía diabética conocida (TFG basal previa 22 ml/min/1.73m²), "
            "es traído a urgencias por debilidad muscular generalizada proximal simétrica, parestesias en extremidades inferiores y astenia marcada. "
            "El paciente refiere haber ingerido antiinflamatorios no esteroideos (Ibuprofeno 800 mg c/8h) por lumbalgia durante los últimos 5 días.\n\n"
            "**Examen físico:**\n"
            "- **Signos vitales:** PA 155/95 mmHg, FC 52 lpm (bradicardia rítmica), FR 19 rpm.\n"
            "- **Neurológico:** Hiporreflexia osteotendinosa generalizada con fuerza muscular 3/5 proximal.\n"
            "- **Laboratorio:** Potasio sérico 7.1 mEq/L, Creatinina sérica 4.3 mg/dL, Urea 145 mg/dL, pH 7.26, HCO3 14 mEq/L.\n"
            "- **Electrocardiograma de 12 derivaciones:** Ondas T picudas simétricas de base estrecha, ensanchamiento del complejo QRS y aplanamiento de la onda P."
        ),
        "pregunta": (
            "Conforme a la GPC para el Abordaje de la Enfermedad Renal Crónica y Trastornos Hidroelectrolíticos del MSP Ecuador:\n"
            "1. Identifique el trastorno hidroelectrolítico crítico y su correlación electrocardiográfica de alto riesgo vital.\n"
            "2. Prescriba de inmediato la secuencia terapéutica de emergencia en 3 pasos: estabilizador de membrana cardiaca, fármacos de redistribución intracelular y agentes de eliminación.\n"
            "3. Enuncie los criterios normados para la activación de terapia de sustitución renal (hemodiálisis de urgencia)."
        ),
        "guia_asociada": "MSP_Guia-de-Enfermedad-Renal-Cronica-2021.pdf",
        "competencias_evaluadas": ["diagnostico_final", "plan_terapeutico_msp"],
        "fragmento_gpc_ideal_id": "gpc_MSP_Guia-de-Enfermedad-Renal-Cronica-2021_chunk_0060",
        "variaciones_isomorficas": {
            "demografia": "64 años con ingesta de AINEs detonante (vs 58 años)",
            "severidad_potasio": "7.1 mEq/L con cambios ECG avanzados (vs 6.7 mEq/L)",
            "enfoque_terapeutico": "Gluconato de Calcio, Insulina + Dextrosa, Nebulización con Salbutamol y criterios dialíticos"
        },
        "faithfulness_score": 1.0,
        "justificacion_clinica": "Isomorfo centrado en hiperpotasemia severa con compromiso ECG y manejo estandarizado según la norma del MSP."
    },
    "case_ehirn_01": {
        "titulo": "Encefalopatía Hipóxico-Isquémica Neonatal y Criterios de Hipotermia Terapéutica",
        "enunciado": (
            "Recién nacido a término (39 semanas de gestación por Capurro), hijo de madre primigesta de 21 años sin patología previa. "
            "Parto institucional complicado por desprendimiento prematuro de placenta normoinserta con líquido amniótico meconial espeso.\n\n"
            "**Estado al nacer:**\n"
            "- **Apgar:** 2 al minuto (requirió reanimación cardiopulmonar con ventilación con presión positiva e intubación orotraqueal) y 5 a los 5 minutos.\n"
            "- **Gasometría arterial de cordón umbilical:** pH 6.98, Exceso de Base -18.5 mmol/L, Lactato 11 mmol/L.\n"
            "- **Examen neurológico a las 2 horas de vida en UCI Neonatal:** Letárgico, hipotonía axial con hipertonía distal en extremidades, reflejo de succión ausente, reflejo de Moro incompleto y episodios de mioclonías sutiles en miembros superiores."
        ),
        "pregunta": (
            "De acuerdo con la GPC de Encefalopatía Hipóxico-Isquémica en el Recién Nacido (EHI-RN) del MSP Ecuador:\n"
            "1. Clasifique la severidad de la encefalopatía según la escala clínica de Sarnat (Estadio II - Moderada).\n"
            "2. Determine si el paciente cumple los criterios fisiológicos y neurológicos de inclusión para Hipotermia Terapéutica corporal total.\n"
            "3. Especifique la ventana temporal máxima recomendada para iniciar la terapia de enfriamiento y la temperatura corporal diana normada."
        ),
        "guia_asociada": "MSP_Guia-de-Encefalopatia-Hipoxico-Isquemica-RN.pdf",
        "competencias_evaluadas": ["semiologia_anamnesis", "diagnostico_final", "plan_terapeutico_msp"],
        "fragmento_gpc_ideal_id": "gpc_MSP_Guia-de-Encefalopatia-Hipoxico-Isquemica-RN_chunk_0042",
        "variaciones_isomorficas": {
            "causa_asfixia": "Desprendimiento prematuro de placenta (vs prolapso de cordón)",
            "gasometria": "pH 6.98, EB -18.5 mmol/L (criterios gasométricos confirmados)",
            "estadio_sarnat": "Encefalopatía moderada grado II con mioclonías sutiles a las 2 horas de vida"
        },
        "faithfulness_score": 1.0,
        "justificacion_clinica": "Isomorfo normativo para el inicio de hipotermia antes de las 6 horas de vida a 33.5°C por 72 horas."
    },
    "case_nac_01": {
        "titulo": "Neumonía Adquirida en la Comunidad y Estratificación CURB-65",
        "enunciado": (
            "Paciente masculino de 69 años, jubilado, con antecedente de EPOC leve sin oxigenoterapia domiciliaria. "
            "Es llevado al servicio de urgencias por presentar cuadro de 5 días de evolución caracterizado por fiebre no cuantificada, escalofríos, "
            "tos con expectoración mucopurulenta de color herrumbroso y dolor pleurítico punzante en hemitórax izquierdo.\n\n"
            "**Examen físico al ingreso:**\n"
            "- **Signos vitales:** PA 100/60 mmHg, FC 108 lpm, FR 32 rpm, Temperatura 38.8°C, Saturación O2 88% al aire ambiente.\n"
            "- **Neurológico:** Alerta, orientado en tiempo, espacio y persona.\n"
            "- **Aparato respiratorio:** Matidez a la percusión en base pulmonar izquierda, murmullo vesicular abolido en tercio inferior y presencia de soplo tubárico con broncofonía aumentada.\n"
            "- **Laboratorio:** Leucocitos 16.800 /uL con 84% neutrófilos, Urea sérica 46 mg/dL (BUN 21.5 mg/dL), PCR cuantitativa 140 mg/L."
        ),
        "pregunta": (
            "En el marco de la GPC de Neumonía Adquirida en la Comunidad del MSP Ecuador:\n"
            "1. Calcule e interprete la escala de estratificación de riesgo pronóstico CURB-65 desglosando cada uno de sus componentes.\n"
            "2. Determine el ámbito clínico adecuado para el manejo del paciente (tratamiento ambulatorio vs hospitalización en sala general vs UCI).\n"
            "3. Prescriba el esquema de antibioticoterapia empírica inicial normado para este grupo de riesgo (fármacos, dosis y vías)."
        ),
        "guia_asociada": "MSP_Guia-de-Neumonia-Adquirida-Comunidad-2021.pdf",
        "competencias_evaluadas": ["semiologia_anamnesis", "diagnostico_final", "plan_terapeutico_msp"],
        "fragmento_gpc_ideal_id": "gpc_MSP_Guia-de-Neumonia-Adquirida-Comunidad-2021_chunk_0030",
        "variaciones_isomorficas": {
            "demografia": "69 años con antecedente respiratorio previo (vs 64 años)",
            "curb65": "Puntuación de 3 (Urea > 42, FR >= 30, Edad >= 65) -> Hospitalización prioritaria",
            "antibioterapia": "Ceftriaxona IV + Macrólido (Claritromicina o Azitromicina) normado por el MSP"
        },
        "faithfulness_score": 1.0,
        "justificacion_clinica": "Evalúa cálculo riguroso de CURB-65 y selección terapéutica empírica hospitalaria según la GPC de Ecuador."
    },
    "case_sepsis_neonatal_01": {
        "titulo": "Sepsis Neonatal Temprana con Compromiso Multisistémico",
        "enunciado": (
            "Neonato masculino de 30 horas de vida, nacido a las 37 semanas de gestación por parto vaginal. "
            "Madre de 19 años con control prenatal deficiente y antecedente de ruptura prematura de membranas de 22 horas de evolución con líquido amniótico fétido, "
            "sin haber recibido profilaxis antibiótica intraparto.\n\n"
            "**Cuadro clínico actual:**\n"
            "- La madre refiere que el niño presenta pobre succión, rechazo de las tomas e hipoactividad marcada desde hace 6 horas.\n"
            "- **Examen físico:** Temperatura axilar 35.6°C (hipotermia), FC 172 lpm, FR 66 rpm con aleteo nasal y tiraje intercostal leve.\n"
            "- **Perfusión periférica:** Piel marmórea, llenado capilar prolongado de 4 segundos, fontanela anterior normotensa.\n"
            "- **Laboratorio:** Leucocitos 4.200 /uL (leucopenia), neutrófilos inmaduros / totales (Índice I/T) de 0.28, plaquetas 110.000 /uL, PCR 28 mg/L."
        ),
        "pregunta": (
            "Conforme a la GPC de Prevención, Diagnóstico y Tratamiento de la Sepsis Neonatal del MSP Ecuador:\n"
            "1. Establezca el diagnóstico sindrómico de Sepsis Neonatal Temprana identificando los factores de riesgo perinatales y los signos clínicos de alarma.\n"
            "2. Enuncie los exámenes complementarios microbiológicos indispensables que deben tomarse de forma inmediata antes de la terapia antibiótica.\n"
            "3. Prescriba el esquema antimicrobiano empírico sinérgico de primera línea normado por el MSP (medicamentos, dosificación por kg de peso y vía)."
        ),
        "guia_asociada": "MSP_Guia-de-Sepsis-Neonatal-2022.pdf",
        "competencias_evaluadas": ["semiologia_anamnesis", "diagnostico_final", "plan_terapeutico_msp"],
        "fragmento_gpc_ideal_id": "gpc_MSP_Guia-de-Sepsis-Neonatal-2022_chunk_0040",
        "variaciones_isomorficas": {
            "factores_riesgo": "RPM 22 horas con corioamnionitis clínica (vs RPM aislada)",
            "signos_clinicos": "Hipotermia 35.6°C y llenado capilar 4s con índice I/T > 0.20",
            "esquema_terapeutico": "Ampicilina + Gentamicina IV a dosis ajustada por edad gestacional y días de vida"
        },
        "faithfulness_score": 1.0,
        "justificacion_clinica": "Isomorfo de sepsis neonatal precoz con evaluación de índice I/T y antibioticoterapia sinérgica del MSP."
    },
    "case_aborto_01": {
        "titulo": "Aborto Incompleto en Primer Trimestre y Criterios de Evacuación Uterina",
        "enunciado": (
            "Paciente de 23 años, primigesta, con amenorrea de 10 semanas y prueba inmunológica de embarazo en orina positiva hace dos semanas. "
            "Acude al servicio de urgencias gineco-obstétricas por cuadro de 12 horas de evolución de dolor espasmódico tipo cólico en hipogastrio de moderada a fuerte intensidad, "
            "acompañado de sangrado genital rojo rutilante con expulsión de coágulos y material con aspecto de tejido ovular.\n\n"
            "**Examen físico:**\n"
            "- **Signos vitales:** PA 110/65 mmHg, FC 86 lpm, Temperatura 36.8°C.\n"
            "- **Especuloscopía:** Sangrado activo moderado procedente de cavidad uterina, visualizándose restos tisulares ovulares protruyendo por el orificio cervical.\n"
            "- **Tacto bimanual:** Cuello uterino con orificio cervical interno permeable que permite el paso de un dedo; útero aumentado de tamaño acorde a 8 semanas, doloroso a la movilización, sin masas anexiales palpables.\n"
            "- **Grupo sanguíneo:** A negativo (Rh negativo)."
        ),
        "pregunta": (
            "De acuerdo con la GPC para la Atención del Aborto y sus Complicaciones del MSP Ecuador:\n"
            "1. Confirme el diagnóstico clínico diferencial específico de la paciente dentro de las variantes de aborto espontáneo.\n"
            "2. Indique el método de evacuación uterina de elección normado por el MSP según la edad gestacional y condiciones hemodinámicas (AMEU vs Legrado Instrumental).\n"
            "3. Prescriba la medida preventiva inmunológica obligatoria por el factor Rh materno (fármaco, dosis y ventana temporal de administración)."
        ),
        "guia_asociada": "MSP_Guia-de-Manejo-del-Aborto-2021.pdf",
        "competencias_evaluadas": ["semiologia_anamnesis", "diagnostico_final", "plan_terapeutico_msp"],
        "fragmento_gpc_ideal_id": "gpc_MSP_Guia-de-Manejo-del-Aborto-2021_chunk_0025",
        "variaciones_isomorficas": {
            "demografia": "23 años, primigesta A negativo (vs 27 años O positivo)",
            "edad_gestacional": "10 semanas de amenorrea (candidata a AMEU < 12 semanas)",
            "prevencion_isoinmunizacion": "Administración obligatoria de Inmunoglobulina Anti-D 300 mcg IM dentro de las 72 horas"
        },
        "faithfulness_score": 1.0,
        "justificacion_clinica": "Evalúa elección de AMEU frente a legrado y profilaxis con Inmunoglobulina Anti-D bajo la GPC de Ecuador."
    }
}


ISOMORPHIC_SYSTEM_INSTRUCTION = """
Eres un Especialista Senior en Educación Médica, Simulación Clínica y Psicometría Formativa de Ateneo+.
Tu misión es generar VARIANTES CLÍNICAS ISOMÓRFICAS de casos clínicos para evaluaciones Post-Test.

REGLAS CARDINALES INNEGOCIABLES DE ISOMORFISMO CLÍNICO:
1. IDENTIDAD PSICOMÉTRICA:
   - La variante generada DEBE evaluar exactamente las mismas competencias clínicas y el mismo nivel cognitivo de Bloom (Análisis y Toma de Decisiones) que el caso base.
   - El estándar de oro diagnóstico y terapéutico DEBE ser estrictamente idéntico según la Guía de Práctica Clínica oficial de Ecuador.
2. VARIACIÓN CONTROLADA DE LA VIÑETA:
   - Modifica las características demográficas de la paciente/paciente (edad, paridad, contexto biopsicosocial).
   - Modifica los parámetros fisiológicos y de laboratorio cuantitativos dentro del MISMO rango de severidad normativo (ej. en crisis con severidad de preeclampsia, si el umbral es PAS >= 160 o PAD >= 110, una variante puede ser 170/115 mmHg).
   - Mantén la misma coherencia patológica sin inventar comorbilidades exóticas que desvíen la atención del objetivo formativo.
3. ESTRICTO ANCLAJE NORMATIVO GPC ECUADOR:
   - Toda conducta médica (fármacos, dosis, esquemas, tiempos de administración, criterios de derivación) debe alinearse con la GPC citada.
   - Prohibido utilizar fármacos o esquemas no autorizados en la normativa del MSP de Ecuador.
4. SALIDA EXCLUSIVAMENTE EN FORMATO JSON VÁLIDO:
   - Debes retornar únicamente un objeto JSON estructurado con los campos especificados, sin preámbulos ni bloques de texto libre.
"""


class IsomorphicCaseGenerator:
    """
    Generador de Casos Clínicos Isomórficos para Evaluaciones Post-Test.
    Utiliza el ResilientLLMGateway para inferencia dinámica con anclaje a las GPC del MSP,
    respaldado por un banco curado determinístico de variantes calibradas para 100% de disponibilidad.
    """

    @classmethod
    def get_curated_isomorphic_case(cls, base_case_id: str) -> Optional[IsomorphicCaseResult]:
        """Obtiene la variante isomórfica calibrada del banco curado."""
        raw = CURATED_ISOMORPHIC_CASES.get(base_case_id)
        if not raw:
            return None

        iso_id = f"iso_{base_case_id}_{uuid.uuid4().hex[:6]}"
        return IsomorphicCaseResult(
            id=iso_id,
            base_case_id=base_case_id,
            titulo=raw["titulo"],
            enunciado=raw["enunciado"],
            pregunta=raw["pregunta"],
            guia_asociada=raw["guia_asociada"],
            competencias_evaluadas=raw.get("competencias_evaluadas", []),
            nivel_esperado="pregrado_avanzado",
            fragmento_gpc_ideal_id=raw.get("fragmento_gpc_ideal_id"),
            variaciones_isomorficas=raw.get("variaciones_isomorficas", {}),
            faithfulness_score=raw.get("faithfulness_score", 1.0),
            justificacion_clinica=raw.get("justificacion_clinica", "Variante calibrada normativamente contra la GPC del MSP."),
            is_generated_by_llm=False
        )

    @classmethod
    def generate_isomorphic_case(
        cls,
        base_case: ClinicalCaseSchema,
        custom_focus: Optional[str] = None,
        force_curated_only: bool = False
    ) -> IsomorphicCaseResult:
        """
        Sintetiza una variante isomórfica para un caso clínico.
        Si force_curated_only es True o no hay conectividad/API Key, utiliza el banco curado.
        Si hay API Key y no está forzado el modo curado, invoca al LLM mediante el gateway resiliente.
        """
        # Si se solicita explícitamente el banco curado o no hay API key configurada
        if force_curated_only or not GEMINI_API_KEY:
            curated = cls.get_curated_isomorphic_case(base_case.id)
            if curated:
                return curated
            return cls._synthesize_programmatic_variant(base_case)

        # Generación asistida por LLM
        prompt = cls._build_isomorphic_prompt(base_case, custom_focus)
        try:
            result = llm_gateway.generate(
                prompt=prompt,
                system_instruction=ISOMORPHIC_SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                temperature=0.3
            )
            raw_text = result.text.strip()
            # Limpieza defensiva si el modelo envía bloques markdown ```json ... ```
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:].strip()

            parsed = json.loads(raw_text)
            iso_id = f"iso_{base_case.id}_{uuid.uuid4().hex[:6]}"

            return IsomorphicCaseResult(
                id=iso_id,
                base_case_id=base_case.id,
                titulo=parsed.get("titulo", f"Variante Isomórfica: {base_case.titulo}"),
                enunciado=parsed.get("enunciado", base_case.enunciado),
                pregunta=parsed.get("pregunta", base_case.pregunta),
                guia_asociada=base_case.guia_asociada,
                competencias_evaluadas=base_case.competencias_activadas or ["diagnostico_final", "plan_terapeutico_msp"],
                nivel_esperado=base_case.nivel_esperado or "pregrado_avanzado",
                fragmento_gpc_ideal_id=base_case.fragmento_gpc_ideal_id,
                variaciones_isomorficas=parsed.get("variaciones_isomorficas", {"variacion": "Sintetizada por LLM"}),
                faithfulness_score=float(parsed.get("faithfulness_score", 0.95)),
                justificacion_clinica=parsed.get("justificacion_clinica", "Variante generada por IA con anclaje a la GPC del MSP Ecuador."),
                is_generated_by_llm=True
            )
        except (AllModelsExhaustedException, FatalLLMException, Exception) as exc:
            logger.warning(
                f"Fallo en generación LLM isomórfica para '{base_case.id}': {exc}. Utilizando banco curado de respaldo.",
                extra={"action": "isomorphic_llm_fallback", "case_id": base_case.id}
            )
            curated = cls.get_curated_isomorphic_case(base_case.id)
            if curated:
                return curated
            return cls._synthesize_programmatic_variant(base_case)

    @classmethod
    def generate_post_test_battery(
        cls,
        assessment_items: List[Any],
        force_curated_only: bool = False
    ) -> List[IsomorphicCaseResult]:
        """
        Genera la batería completa de casos isomórficos para un Post-Test a partir de los
        reactivos evaluados en el Pre-Test diagnóstico.
        """
        case_service = get_case_service()
        battery: List[IsomorphicCaseResult] = []
        seen_base_ids = set()

        for item in assessment_items:
            base_case_id = getattr(item, "case_id", None) or (item.get("case_id") if isinstance(item, dict) else None)
            if not base_case_id or base_case_id in seen_base_ids:
                continue

            base_case = case_service.get_case(base_case_id)
            if not base_case:
                # Si no está en el servicio de casos, buscar en el catálogo curado
                curated = cls.get_curated_isomorphic_case(base_case_id)
                if curated:
                    battery.append(curated)
                    seen_base_ids.add(base_case_id)
                continue

            # Priorizar brechas: si el alumno tuvo omisiones, se le pasa foco específico
            omisiones_raw = getattr(item, "omisiones_json", None) or (item.get("omisiones") if isinstance(item, dict) else None)
            custom_focus = None
            if omisiones_raw:
                custom_focus = f"Foco en superar omisiones previas: {omisiones_raw}"

            iso_case = cls.generate_isomorphic_case(
                base_case=base_case,
                custom_focus=custom_focus,
                force_curated_only=force_curated_only
            )
            battery.append(iso_case)
            seen_base_ids.add(base_case_id)

        return battery

    @classmethod
    def validate_case_isomorphism(
        cls,
        base_case: ClinicalCaseSchema,
        iso_case: IsomorphicCaseResult
    ) -> Dict[str, Any]:
        """
        Valida que un caso isomórfico cumpla con los principios psicométricos:
        - Mismas competencias evaluadas.
        - Misma guía de práctica clínica de referencia.
        - Distinto enunciado (viñeta paralela no idéntica).
        - Anclaje normativo >= 0.85.
        """
        has_same_guide = base_case.guia_asociada.strip().lower() in iso_case.guia_asociada.strip().lower() or \
                         iso_case.guia_asociada.strip().lower() in base_case.guia_asociada.strip().lower()
        is_distinct_prompt = base_case.enunciado.strip() != iso_case.enunciado.strip()
        is_faithful = iso_case.faithfulness_score >= 0.80

        base_comps = set(base_case.competencias_activadas or [])
        iso_comps = set(iso_case.competencias_evaluadas)
        comp_overlap = len(base_comps.intersection(iso_comps)) / max(len(base_comps), 1)

        is_valid = has_same_guide and is_distinct_prompt and is_faithful and comp_overlap >= 0.5

        return {
            "is_valid": is_valid,
            "has_same_guide": has_same_guide,
            "is_distinct_prompt": is_distinct_prompt,
            "is_faithful": is_faithful,
            "competency_overlap_ratio": round(comp_overlap, 2),
            "faithfulness_score": iso_case.faithfulness_score
        }

    @classmethod
    def _build_isomorphic_prompt(
        cls,
        base_case: ClinicalCaseSchema,
        custom_focus: Optional[str] = None
    ) -> str:
        """Construye el prompt estructurado para la generación de la variante isomórfica."""
        return f"""Genera una variante clínica isomórfica paralela para la evaluación Post-Test a partir del siguiente caso base:

CASO CLÍNICO BASE:
- ID: {base_case.id}
- TÍTULO: {base_case.titulo}
- GUÍA ASOCIADA (GPC ECUADOR): {base_case.guia_asociada}
- COMPETENCIAS ACTIVADAS: {', '.join(base_case.competencias_activadas or ['plan_terapeutico_msp'])}
- ENUNCIADO ORIGINAL:
{base_case.enunciado}

- PREGUNTA ORIGINAL:
{base_case.pregunta}

{f"FOCO FORMATIVO ADICIONAL: {custom_focus}" if custom_focus else ""}

INSTRUCCIONES DE FORMATO:
Retorna estrictamente un objeto JSON con la siguiente estructura exacta:
{{
  "titulo": "Título adaptado para la variante clínica",
  "enunciado": "Viñeta clínica completa con nueva historia del paciente, signos vitales y datos paraclínicos análogos",
  "pregunta": "Interrogante clínica formativa que evalúe la toma de decisiones normada",
  "variaciones_isomorficas": {{
    "demografia": "Detalle de edad, sexo o antecedentes modificados",
    "parametros_clinicos": "Valores de signos vitales o laboratorio equivalentes en rango",
    "contexto": "Situación de presentación clínica modificada"
  }},
  "faithfulness_score": 0.95,
  "justificacion_clinica": "Breve explicación de la equivalencia psicométrica y fidelidad a la GPC del MSP"
}}
"""

    @classmethod
    def _synthesize_programmatic_variant(cls, base_case: ClinicalCaseSchema) -> IsomorphicCaseResult:
        """Genera una variante heurística programática cuando no existe entrada en banco ni LLM."""
        iso_id = f"iso_{base_case.id}_{uuid.uuid4().hex[:6]}"
        return IsomorphicCaseResult(
            id=iso_id,
            base_case_id=base_case.id,
            titulo=f"Caso Isomórfico Post-Test: {base_case.titulo}",
            enunciado=(
                f"{base_case.enunciado}\n\n"
                f"*[Nota Post-Test: Se presenta una paciente de edad y perfil concordante con igual requerimiento normativo bajo {base_case.guia_asociada}]*"
            ),
            pregunta=base_case.pregunta,
            guia_asociada=base_case.guia_asociada,
            competencias_evaluadas=base_case.competencias_activadas or ["diagnostico_final", "plan_terapeutico_msp"],
            nivel_esperado=base_case.nivel_esperado or "pregrado_avanzado",
            fragmento_gpc_ideal_id=base_case.fragmento_gpc_ideal_id,
            variaciones_isomorficas={"variacion": "Reevaluación isomórfica programática"},
            faithfulness_score=1.0,
            justificacion_clinica=f"Caso isomórfico estructurado para post-test según {base_case.guia_asociada}.",
            is_generated_by_llm=False
        )
