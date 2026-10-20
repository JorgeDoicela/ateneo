"""
Generador Maestro del Documento Word Oficial y Exhaustivo (DOCX)
Ateneo+: Dossier Integral de Investigacion, Ingenieria de Software, MLOps, Transformers,
Extraccion de Datos, Psicometria, Impacto Pedagogico en Ecuador, Protocolos de Reproducibilidad,
Hoja de Ruta de Escalabilidad y Ponencia Magistral CAISEB (40 min).
"""

import os
import sys
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

SCRIPT_DIR = Path(__file__).resolve().parent
MODULE_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = MODULE_DIR.parent.parent

DOCX_OUTPUT = MODULE_DIR / "ATENEO_DOSSIER_TECNICO_Y_PONENCIA_CAISEB.docx"

# Colores Institucionales Ateneo+ / CAISEB
COLOR_NAVY = RGBColor(15, 76, 129)       # #0f4c81 - Azul Petroleo / Navy Institucional
COLOR_BLUE = RGBColor(37, 99, 235)       # #2563eb - Azul Royal Medico
COLOR_DARK = RGBColor(30, 41, 59)        # #1e293b - Pizarra Oscuro Texto
COLOR_MUTED = RGBColor(100, 116, 139)    # #64748b - Gris Neutro Subtitulos
COLOR_GREEN = RGBColor(4, 120, 87)       # #047857 - Verde Clinico
COLOR_CYAN = RGBColor(8, 145, 178)       # #0891b2 - Cyan Clinico

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def add_callout_box(doc, text, title="NOTA TECNICA / DISCURSO CLAVE"):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F0F4F9")
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="2563EB"/>'
        f'<w:top w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    run_t = p.add_run(f"{title}: ")
    run_t.font.name = "Arial"
    run_t.font.size = Pt(10)
    run_t.font.bold = True
    run_t.font.color.rgb = COLOR_NAVY
    
    run_b = p.add_run(text)
    run_b.font.name = "Arial"
    run_b.font.size = Pt(9.5)
    run_b.font.italic = True
    run_b.font.color.rgb = COLOR_DARK
    
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_after = Pt(4)

def add_heading_1(doc, text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(18)
    h.paragraph_format.space_after = Pt(6)
    h.paragraph_format.keep_with_next = True
    r = h.add_run(text)
    r.font.name = "Arial"
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = COLOR_NAVY
    return h

def add_heading_2(doc, text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(13)
    h.paragraph_format.space_after = Pt(4)
    h.paragraph_format.keep_with_next = True
    r = h.add_run(text)
    r.font.name = "Arial"
    r.font.size = Pt(12.5)
    r.font.bold = True
    r.font.color.rgb = COLOR_BLUE
    return h

def add_heading_3(doc, text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(9)
    h.paragraph_format.space_after = Pt(3)
    h.paragraph_format.keep_with_next = True
    r = h.add_run(text)
    r.font.name = "Arial"
    r.font.size = Pt(10.5)
    r.font.bold = True
    r.font.color.rgb = COLOR_DARK
    return h

def add_body_paragraph(doc, text, bold_prefix=None, space_after=5):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Arial"
        r_pre.font.size = Pt(10)
        r_pre.font.bold = True
        r_pre.font.color.rgb = COLOR_DARK
        
    r = p.add_run(text)
    r.font.name = "Arial"
    r.font.size = Pt(10)
    r.font.color.rgb = COLOR_DARK
    return p

def add_bullet_item(doc, text, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Arial"
        r_pre.font.size = Pt(9.5)
        r_pre.font.bold = True
        r_pre.font.color.rgb = COLOR_DARK
        
    r = p.add_run(text)
    r.font.name = "Arial"
    r.font.size = Pt(9.5)
    r.font.color.rgb = COLOR_DARK
    return p

def add_image_with_caption(doc, rel_path, caption, width_in=6.0):
    full_path = PROJECT_ROOT / rel_path if not Path(rel_path).is_absolute() else Path(rel_path)
    if not full_path.exists():
        print(f"Advertencia: No existe imagen {full_path}")
        return
        
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(8)
    p_img.paragraph_format.space_after = Pt(3)
    p_img.paragraph_format.keep_with_next = True
    run_img = p_img.add_run()
    run_img.add_picture(str(full_path), width=Inches(width_in))
    
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(0)
    p_cap.paragraph_format.space_after = Pt(10)
    r_cap = p_cap.add_run(caption)
    r_cap.font.name = "Arial"
    r_cap.font.size = Pt(8.5)
    r_cap.font.italic = True
    r_cap.font.color.rgb = COLOR_MUTED

def main():
    print(f"Iniciando compilacion del Dossier Integral, Exhaustivo y Metodologico Word en: {DOCX_OUTPUT}")
    doc = Document()
    
    # Configuracion de margenes de pagina A4 (1 pulgada en todos los bordes)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
        # Encabezado sutil
        header = section.header
        p_hdr = header.paragraphs[0]
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_hdr = p_hdr.add_run("ATENEO+ | Dossier Integral de Investigacion, Ingenieria y Ponencia CAISEB")
        r_hdr.font.name = "Arial"
        r_hdr.font.size = Pt(8)
        r_hdr.font.color.rgb = COLOR_MUTED
        
        # Pie de pagina institucional
        footer = section.footer
        p_ftr = footer.paragraphs[0]
        p_ftr.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_ftr = p_ftr.add_run("Ateneo+ v1.0.0 — Simulador Clinico Multimodal & RAG Formativo GPC Ecuador — Confidencial / Material de Ponencia")
        r_ftr.font.name = "Arial"
        r_ftr.font.size = Pt(8)
        r_ftr.font.color.rgb = COLOR_MUTED

    # =========================================================================
    # PORTADA INSTITUCIONAL
    # =========================================================================
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(16)
    p_inst.paragraph_format.space_after = Pt(4)
    r_inst = p_inst.add_run("CONGRESO ACADEMICO INTERNACIONAL DE INNOVACION EN SALUD, EDUCACION Y BIENESTAR (CAISEB 2026)")
    r_inst.font.name = "Arial"
    r_inst.font.size = Pt(11)
    r_inst.font.bold = True
    r_inst.font.color.rgb = COLOR_NAVY
    
    p_subinst = doc.add_paragraph()
    p_subinst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_subinst.paragraph_format.space_after = Pt(20)
    r_subinst = p_subinst.add_run("DOSSIER TECNICO, CIENTIFICO, METODOLOGICO Y GUIA DE PONENCIA MAGISTRAL (40 MINUTOS)")
    r_subinst.font.name = "Arial"
    r_subinst.font.size = Pt(9.5)
    r_subinst.font.color.rgb = COLOR_MUTED
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(16)
    r_title = p_title.add_run("SIMULADOR CLINICO MULTIMODAL BASADO EN INTELIGENCIA ARTIFICIAL Y RAG PARA EL ENTRENAMIENTO FORMATIVO Y ANALITICA DEL APRENDIZAJE MEDICO EN ECUADOR")
    r_title.font.name = "Arial"
    r_title.font.size = Pt(17)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_NAVY
    
    p_logo = doc.add_paragraph()
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_logo.paragraph_format.space_after = Pt(18)
    logo_path = PROJECT_ROOT / "backend" / "cases_data" / "images" / "ateneo.png"
    if logo_path.exists():
        p_logo.add_run().add_picture(str(logo_path), width=Inches(1.4))
        
    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.space_after = Pt(4)
    r_autores = p_meta.add_run("AUTORES E INVESTIGADORES:\n")
    r_autores.font.bold = True
    r_autores.font.size = Pt(10)
    r_autores.font.color.rgb = COLOR_NAVY
    
    r_inv1 = p_meta.add_run("Tnlgo. Jorge Ismael Doicela Molina (Investigador — Arquitectura de Software, MLOps e IA en Salud)\n")
    r_inv1.font.size = Pt(10)
    r_inv1.font.bold = True
    r_inv1.font.color.rgb = COLOR_DARK
    
    r_inv2 = p_meta.add_run("Mgtr. Estefani Angelica Sanchez Morales (Investigadora — Educacion Medica, Metodologia y Validacion Clinica)\n")
    r_inv2.font.size = Pt(10)
    r_inv2.font.bold = True
    r_inv2.font.color.rgb = COLOR_DARK
    
    p_fil = doc.add_paragraph()
    p_fil.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_fil.paragraph_format.space_after = Pt(20)
    r_fil = p_fil.add_run("Filiacion: Ateneo+\nQuito, Ecuador — Octubre 2026")
    r_fil.font.size = Pt(9)
    r_fil.font.italic = True
    r_fil.font.color.rgb = COLOR_MUTED
    
    doc.add_page_break()

    # =========================================================================
    # SECCION 1: ANTECEDENTES HISTORICOS Y CRISIS DE LA EDUCACION MEDICA EN ECUADOR
    # =========================================================================
    add_heading_1(doc, "1. ANTECEDENTES HISTORICOS Y CRISIS DE LA EDUCACION MEDICA EN ECUADOR")
    
    add_body_paragraph(
        doc,
        "La ensenanza de la medicina clinica en el Ecuador ha estado historicamente condicionada por una brecha metodologica estructural. "
        "Tradicionalmente, la formacion de competencias diagnosticas y terapeuticas se ha apoyado en dos esquemas pedagogicos convencionales: "
        "1) Centros de simulacion basados en maniquies mecatronicos de alto costo (modelos tipo Laerdal o Gaumard), cuya adquisicion e importacion "
        "exige inversiones institucionales superiores a los $80,000 - $150,000 USD por estacion, restringiendo su presencia a unas pocas facultades de elite "
        "en Quito, Guayaquil y Cuenca, y marginando a las universidades provinciales; y 2) El Aprendizaje Basado en Problemas (ABP / PBL) en soporte "
        "de papel o fichas estaticas, caracterizado por una evaluacion retrospectiva, subjetiva, carente de interactividad en tiempo real y limitada "
        "a respuestas de opcion multiple desprovistas de razonamiento clinico abierto.",
        bold_prefix="Antecedentes y Limitaciones de la Simulacion Tradicional: "
    )
    
    add_body_paragraph(
        doc,
        "Segun las auditorias del Consejo de Aseguramiento de la Calidad de la Educacion Superior (CACES) sobre el Examen de Habilitacion para el "
        "Ejercicio Profesional (EHEP) de medicos cirujanos, y los informes epidemiologicos del Instituto Nacional de Estadistica y Censos (INEC) "
        "junto al Ministerio de Salud Publica (MSP), el internado rotativo representa un periodo critico de alta vulnerabilidad. "
        "Las principales causas de muerte materna evitable (Hemorragia Posparto - Codigo Rojo y Preeclampsia Severa) y de morbimortalidad neonatal "
        "(Sepsis Neonatal Temprana y Encefalopatia Hipoxico-Isquemica) presentan una letalidad atribuible en un 42.4% a demoras en la identificacion sindromica "
        "y discrepancias severas en la dosificacion farmacologica por parte de medicos en formacion de primer contacto.",
        bold_prefix="Epidemiologia y Auditoria de Error Medico en Internado: "
    )
    
    add_body_paragraph(
        doc,
        "Durante las guardias hospitalarias de 24 a 36 horas en hospitales cantonales distritales (Segundo Nivel) y centros de salud rurales (Primer Nivel), "
        "un medico tratante supervisa simultaneamente entre 12 y 18 internos rotativos. La tutoria individualizada a pie de cama (bedside teaching) resulta "
        "imposible de sostener de forma continua. La retroalimentacion docente se torna episodica, verbalmente informal, punitiva y heterogenea, "
        "generando en el estudiante sindrome de burnout, temor al error iatrogenico en paciente real y dependencia de busquedas improvisadas en internet.",
        bold_prefix="La Realidad Asistencial del Interno Rotativo: "
    )

    add_callout_box(
        doc,
        "En la ponencia magistral, se debe enfatizar este antecedente: un interno rotativo a las 03:00 a.m. en una sala de partos rural "
        "no cuenta con un simulador mecatronico de $100,000 dolares ni con un especialista a su lado. Requiere haber entrenado su juicio clinico "
        "decenas de veces contra los algoritmos exactos de la GPC del MSP. Ateneo+ democratiza ese entrenamiento de grado hospitalario en el bolsillo del estudiante.",
        title="MENSAJE DE APERTURA MAGISTRAL (MINUTO 00:00 - 04:00)"
    )

    # =========================================================================
    # SECCION 2: COMO AYUDAR A LOS ESTUDIANTES DE MEDICINA EN ECUADOR
    # =========================================================================
    add_heading_1(doc, "2. COMO AYUDAR A LOS ESTUDIANTES DE MEDICINA EN ECUADOR: EL ROL DE ATENEO+")
    
    add_body_paragraph(
        doc,
        "Ateneo+ fue concebido desde sus cimientos como una herramienta de transformacion pedagogica formativa no punitiva, disenada explicitamente "
        "para derribar las barreras que enfrentan los estudiantes de medicina e internos rotativos en el sistema sanitario ecuatoriano:",
        bold_prefix="Propuesta de Valor Formativo: "
    )
    
    add_bullet_item(doc, "Entorno de Entrenamiento Seguro Sin Riesgo Iatrogenico: Permite al estudiante cometer errores de dosificacion, solicitar paraclinicos innecesarios o fallar en el diagnostico dentro de un entorno digital controlado, visualizando la evolucion fisiopatologica adversa del paciente sin comprometer la vida de un ser humano real.", bold_prefix="1. Seguridad Psicologica del Estudiante: ")
    add_bullet_item(doc, "Andamiaje Socratico Inmediato (Debriefing SSE): En lugar de calificar con un simple 'incorrecto', el sistema genera preguntas de orientacion clinica en tiempo real token a token guiando al alumno a reconocer el mecanismo fisiopatologico de su omision (ej. vasodilatacion extrema o bloqueo neuromuscular por exceso de magnesio).", bold_prefix="2. Retroalimentacion Socrática Inmediata: ")
    add_bullet_item(doc, "Anclaje Bedside Estricto al Cuadro Nacional de Medicamentos Basicos (CNMB): Entrena al estudiante a prescribir exclusivamente los farmacos que realmente existen y estan autorizados para el primer y segundo nivel en los centros del MSP e IESS, evitando la frustracion y el peligro de recetar moleculas de tercera linea inexistentes en la red publica.", bold_prefix="3. Realismo de la Farmacopea Local: ")
    add_bullet_item(doc, "Instruccion Adaptativa Personalizada en la ZDP: El estudiante no pierde tiempo resolviendo casos triviales que ya domina ni se frustra con escenarios para los que aun carece de prerrequisitos basicos; el sistema prescribe dinamicamente el siguiente caso en su umbral optimo de aprendizaje segun su vector cognitivo BKT.", bold_prefix="4. Trayectoria Curricular Óptima: ")
    add_bullet_item(doc, "Preparacion de Alto Impacto para el EHEP (CACES) y la Medicatura Rural: El acervo de casos aborda exactamente los 4 ejes normativos que componen el banco de evaluacion nacional del CACES y las patologias de mayor prevalencia en la medicatura rural obligatoria (salud materno-neonatal, tuberculosis, neumonias y enfermedades cronicas).", bold_prefix="5. Acreditación y Ejercicio Profesional: ")

    # =========================================================================
    # SECCION 3: LIMITES DE LA IA GENERALISTA Y EL PELIGRO DE LA ALUCINACION MEDICA
    # =========================================================================
    add_heading_1(doc, "3. LIMITES DE LA IA GENERALISTA Y EL PELIGRO DE LA ALUCINACION MEDICA")
    
    add_body_paragraph(
        doc,
        "La irrupcion de Modelos de Lenguaje Grande (LLMs) fundacionales comerciales (como OpenAI GPT-4o, Google Gemini Pro o Anthropic Claude) "
        "ha generado la falsa percepcion de que un chatbot generalista puede fungir como evaluador o tutor del juicio clinico. "
        "La investigacion cientifica rigurosa y las pruebas empiricas ejecutadas en la linea de base de este proyecto demuestran que el uso directo "
        "de LLMs genericos en configuracion Zero-Shot o Few-Shot en medicina comporta riesgos criticos inaceptables:",
        bold_prefix="Diagnostico de Riesgo Tecnologico: "
    )
    
    add_bullet_item(doc, "Tasa de Alucinacion Evaluativa Masiva (45.8% en Baseline): En pruebas controladas con respuestas clinicas que contenian omisiones graves o dosis toxicas, los modelos comerciales no anclados aprobaron conductas iatrogenicas debido a un sesgo de complacencia (sycophancy) y completitud sintactica probabilistica.", bold_prefix="1. Alucinacion Evaluativa: ")
    add_bullet_item(doc, "Desajuste Jurisdiccional y Farmacopea Incompatible: Los modelos fundacionales estan pre-entrenados preponderantemente sobre literatura anglosajona (guias NICE del Reino Unido o directrices de la AHA/ACC de EE. UU.). Al evaluar a un interno ecuatoriano, sugieren o exigen medicamentos de tercera linea de alto costo no disponibles en el Cuadro Nacional de Medicamentos Basicos (CNMB del CONASA) o contradicen los esquemas ministeriales oficiales (ej. pautas de fluidoterapia en shock hipovolemico obstetrico).", bold_prefix="2. Desfase con el CNMB: ")
    add_bullet_item(doc, "Ausencia Absoluta de Trazabilidad Forense y No Repudio: Ante una discrepancia con el docente o una calificacion formativa cuestionada, un modelo comercial no puede certificar con certeza matematica el numero de pagina fisica, acuerdo ministerial y parrafo oficial que respalda la penalizacion, impidiendo su adopcion en procesos de acreditacion universitaria (CACES).", bold_prefix="3. Carencia de Trazabilidad: ")
    add_bullet_item(doc, "Deriva de Versiones (Model Drift) y Dependencia Externa: Las APIs comerciales de terceros sufren cambios continuos de pesos, descontinuaciones imprevistas de endpoints y variabilidad de temperatura que destruyen la reproducibilidad cientifica exigida por revistas de primer cuartil (Q1).", bold_prefix="4. Falta de Reproducibilidad: ")

    # =========================================================================
    # SECCION 4: TEORIA Y ARQUITECTURA DE TRANSFORMERS Y MODELOS DE EMBEDDINGS (BGE-M3)
    # =========================================================================
    add_heading_1(doc, "4. TEORIA Y ARQUITECTURA DE TRANSFORMERS Y MODELOS DE EMBEDDINGS")
    
    add_body_paragraph(
        doc,
        "Para comprender por que Ateneo+ supera radicalmente a las alternativas comerciales, es imperativo desglosar la arquitectura interna "
        "del mecanismo de atencion y los modelos de representacion vectorial empleados.",
        bold_prefix="Fundamentos de Deep Learning: "
    )
    
    add_heading_2(doc, "4.1 El Mecanismo de Auto-Atencion Escalada (Scaled Dot-Product Attention)")
    add_body_paragraph(
        doc,
        "La arquitectura Transformer (Vaswani et al., 2017) descansa sobre el calculo del alineamiento contextual de representaciones densas. "
        "Dada una secuencia de entrada proyectada en matrices de Consulta (Query, Q), Llave (Key, K) y Valor (Value, V) en un espacio de dimension d_k:",
        bold_prefix="Formulacion Matematica: "
    )
    
    add_callout_box(
        doc,
        "Attention(Q, K, V) = softmax( (Q * K^T) / sqrt(d_k) ) * V\n\n"
        "Donde d_k representa la dimensionalidad de las llaves. El factor de escala 1 / sqrt(d_k) previene que el producto escalar "
        "crezca en magnitudes excesivas para dimensiones elevadas, lo cual empujaria la funcion softmax hacia regiones de gradientes infinitesimales (vanishing gradients).",
        title="ECUACION CANONICA DE AUTO-ATENCION"
    )
    
    add_body_paragraph(
        doc,
        "En la arquitectura Multi-Head Attention, este mecanismo se paraleliza a lo largo de h cabezas independientes, permitiendo al modelo atender simultaneamente "
        "a informacion procedente de diferentes subespacios de representacion en distintas posiciones. En el contexto clinico de Ateneo+, una cabeza aprende a ligar "
        "un signo de alarma (ej. 'epigastralgia en barra') con una complicacion subyacente (ej. 'hematoma subcapsular hepatico en Sindrome HELLP'), mientras otra cabeza "
        "atiende a la contraindicacion posologica correspondiente.",
        bold_prefix="Multi-Head Attention en Razonamiento Clinico: "
    )

    add_heading_2(doc, "4.2 Arquitectura del Transformer de Embeddings BAAI/bge-m3")
    add_body_paragraph(
        doc,
        "El modelo seleccionado como columna vertebral del recuperador es BAAI/bge-m3 (Chen et al., 2024), un Transformer multilingue de 568 millones de parametros "
        "organizado en 24 capas de codificador con 16 cabezas de atencion y una dimension oculta latente de 1,024 dimensiones. A diferencia de los encoders BERT clasicos, "
        "BGE-M3 introduce tres capacidades cardinales denominadas M3 (Multi-Functionality, Multi-Linguality, Multi-Granularity):",
        bold_prefix="Caracteristicas del Backbone BGE-M3: "
    )
    
    add_bullet_item(doc, "Representacion Densa (Dense Retrieval): Mapea la consulta clinica completa a un unico vector latente normalizado en norma L2 (||e||_2 = 1) de 1,024 dimensiones, capturando la intencion semantica profunda y la sinonimia medica global.", bold_prefix="1. Rama Densa: ")
    add_bullet_item(doc, "Representacion Dispersa Multilingue (Lexical / Sparse Weighting): Genera ponderaciones de importancia de terminos especificos (similar a un TF-IDF neuronal o SPLADE) directamente en el espacio de vocabulario, otorgando pesos elevados a farmacos unicos, acronimos y dosis exactas.", bold_prefix="2. Rama Dispersa: ")
    add_bullet_item(doc, "Representacion Multi-Vectorial (ColBERT-style Multi-Vector): Preserva embeddings a nivel de token para ejecucion de MaxSim (atencion cruzada tardia), resolviendo discrepancias finas entre documentos tecnicos densamente estructurados.", bold_prefix="3. Rama Multi-Vector: ")
    add_bullet_item(doc, "Soporte de Longitud Extendida: Admite ventanas de contexto de hasta 8,192 tokens nativos, lo que garantiza que ninguna tabla de dosificacion farmacologica compleja o algoritmo de triaje deba ser mutilado durante el chunking.", bold_prefix="4. Contexto Amplio: ")

    # =========================================================================
    # SECCION 5: PROCEDIMIENTO DE INGENIERIA: PIPELINE DE EXTRACCION Y CURACION DE DATOS
    # =========================================================================
    add_heading_1(doc, "5. PROCEDIMIENTO DE INGENIERIA: PIPELINE DE EXTRACCION Y CURACION DE DATOS")
    
    add_body_paragraph(
        doc,
        "La construccion de la base de conocimiento normativo no fue un proceso manual ni ad-hoc; se diseno e implemento un pipeline "
        "de ingenieria de datos automatizado, riguroso y determinista en Python y C++.",
        bold_prefix="Procedimiento Paso a Paso de Ingesta: "
    )
    
    add_heading_2(doc, "5.1 Clasificacion Nosologica y Depuracion Canonica (42 GPCs Oficiales)")
    add_body_paragraph(
        doc,
        "A traves del modulo backend/ingestion_v2/01_classify_and_inventory_corpus.py, se inventariaron y sellaron con hash SHA-256 inmutable "
        "las directrices ministeriales emitidas entre 2013 y 2019. Se descartaron 3 documentos no prescriptivos (triptico de bolsillo, cartilla ciudadana "
        "y folleto de diabetes gestacional sin texto digital), preservando exactamente 42 Guias de Practica Clinica oficiales con texto tecnico integro. "
        "Cada documento fue clasificado bajo la Clasificacion Internacional de Enfermedades (CIE-10 / CIE-11) y asignado a 4 ejes normativos ministeriales: "
        "1) Urgencias Obstetricas (11 guias); 2) Infecciones Respiratorias y Pediatria (11 guias); 3) Urgencias Cardiovasculares y Metabolicas (2 guias); "
        "y 4) Soporte Cronicos, Oncologia y Salud Mental (18 guias). El manifiesto resultante reside en backend/data/corpus_manifest.json.",
        bold_prefix="Fase 1 - Inventario Criptográfico: "
    )
    
    add_heading_2(doc, "5.2 Extraccion Nativa con Deteccion de Paginacion Fisica Real (PyMuPDF C++)")
    add_body_paragraph(
        doc,
        "Implementada en backend/ingestion_v2/02_extract_corpus_native.py. Para resolver el desfase de paginacion que invalida las citas de RAG "
        "en auditorias legales, el extractor examina la coordenada espacial inferior (y >= 0.82 de la altura de pagina). "
        "Si detecta guarismos impresos reales, extrae el numero de pagina fisica descartando la numeracion romana preliminar. "
        "Cada pagina se estructura con comentarios delimitadores estandarizados:",
        bold_prefix="Fase 2 - Extracción de Alta Fidelidad: "
    )
    
    add_callout_box(
        doc,
        "<!-- GPC_PAGE_START | NUMERO_PDF: 14 | PAGINA_IMPRESA: 14 | GUIA: Aborto-terapeutico.pdf -->\n"
        "[Contenido clinico normativo integro]\n"
        "<!-- GPC_PAGE_END | NUMERO_PDF: 14 -->\n\n"
        "Esta estructura garantiza que cuando el evaluador emite una cita como 'GPC Preeclampsia, Seccion 12.8, Pagina 40', "
        "el revisor o estudiante abre el PDF fisico y encuentra la directriz exactamente en la pagina 40 impresa.",
        title="DELIMITADOR CANONICO DE PAGINACION REAL"
    )

    add_heading_2(doc, "5.3 Extraccion Matricial de Tablas Clinicas Complejas en Markdown")
    add_body_paragraph(
        doc,
        "Los esquemas posologicos pierden toda coherencia semantica si se aplanan a texto corrido sin estructura de columnas. "
        "El pipeline de Ateneo+ ejecuta el algoritmo de deteccion matricial page.find_tables(), deduplica bboxes espaciales y renderiza tablas Markdown nativas "
        "con separadores '|---|---|' y preservacion de saltos internos con etiquetas <br>. "
        "Total de matrices clinicas extraidas sin perdida: 3,201 tablas normativas sobre 3,438 paginas procesadas.",
        bold_prefix="Preservacion Estructural: "
    )

    add_heading_2(doc, "5.4 Token Chunking Semantico e Indivisible (7,052 Chunks)")
    add_body_paragraph(
        doc,
        "A traves de backend/ingestion_v2/03_token_chunker.py, el texto se fragmenta utilizando el tokenizador formal de BGE-M3. "
        "Se calibraron fragmentos de 512 tokens con 128 tokens de solapamiento. "
        "Regla de Indivisibilidad Clinica: Ninguna tabla de dosificacion, esquema terapeutico o arbol de decision se fragmenta a la mitad. "
        "Si una tabla normativa ocupa hasta 768 tokens, el chunker expande dinamicamente la ventana para preservarla como una unidad cognitiva unica. "
        "El corpus consolidado consta de 7,052 fragmentos normativos catalogados con codigo CIE-10/CIE-11, acuerdo ministerial y hash criptografico SHA-256.",
        bold_prefix="Fase 3 - Segmentación Semántica: "
    )

    # =========================================================================
    # SECCION 6: PROCEDIMIENTO DE MINERIA DE NEGATIVOS Y FINE-TUNING EN GPU A100
    # =========================================================================
    add_heading_1(doc, "6. PROCEDIMIENTO DE MINERIA DE NEGATIVOS Y FINE-TUNING EN GPU A100")
    
    add_body_paragraph(
        doc,
        "Para lograr que el modelo de embeddings BGE-M3 diferencie sutilezas clinicas complejas entre patologias de una misma especialidad, "
        "se ejecuto un procedimiento de mineria semantica en dos etapas y fine-tuning supervisado:",
        bold_prefix="Pipeline de Ajuste Contrastivo: "
    )
    
    add_heading_2(doc, "6.1 Mineria Semantica en Dos Etapas (Two-Stage Dense Hard Negative Mining)")
    add_body_paragraph(
        doc,
        "Implementado en backend/ingestion_v2/04_mine_hard_negatives.py. A diferencia del filtro superficial de Jaccard que contaminaba "
        "el entrenamiento con nombres de ex-ministros o tablas de contenido, el algoritmo v2 opera en dos etapas defensivas:",
        bold_prefix="Fase 4 - Minería de Negativos: "
    )
    add_bullet_item(doc, "Etapa 1 (Filtro Lexico BM25Okapi): Recupera los Top-40 candidatos con mayor senal léxica ante cada consulta clinica contextualizada.", bold_prefix="Filtro BM25: ")
    add_bullet_item(doc, "Filtro Defensivo Anti-Falsos Negativos (6 Reglas): 1) Exclusion de identidad (c != p); 2) Exclusion intra-seccion (misma guia y seccion descartadas); 3) Solapamiento Jaccard de bigramas < 65%; 4) Exclusion de paginas de creditos e ISBN; 5) Exclusion de indices con alta densidad de digitos (> 15% de lineas con numeros); y 6) Exclusion de listas de autores con >= 4 cargos medicos.", bold_prefix="Filtro Defensivo: ")
    add_bullet_item(doc, "Etapa 2 (Re-ranking Semantico en Lote): Computa los embeddings BGE-M3 de los candidatos validos y selecciona el hard negative optimo n* mediante maxima similitud coseno en espacio latente de 1,024 dimensiones.", bold_prefix="Re-ranking Denso: ")

    add_heading_2(doc, "6.2 Curacion Ciega del Ground Truth y Certificacion Kappa")
    add_body_paragraph(
        doc,
        "Implementado en backend/ingestion_v2/05_build_ground_truth_pool.py. Se construyo un banco balanceado de 160 pares evaluados bajo "
        "un protocolo Likert ordinal de tres niveles: 0 (Irrelevante/Contradictorio), 1 (Contextual) y 2 (Gold Standard normativo vinculante). "
        "Dos facultativos especialistas evaluaron en doble ciego independiente los pares, alcanzando un coeficiente Kappa Ponderado Cuadratico "
        "de Cohen kw = 0.9531 con 91.25% de acuerdo simple observado (Po) y cero discrepancias mayores (0 <-> 2), superando el umbral de aceptacion cientifica (kw >= 0.80).",
        bold_prefix="Fase 5 - Ground Truth Certificado: "
    )

    add_heading_2(doc, "6.3 Entrenamiento Supervisado con MNRL en GPU NVIDIA A100")
    add_body_paragraph(
        doc,
        "Implementado en backend/ingestion_v2/06_train_bge_m3.py y colab_fase6_train_bge_m3.ipynb. "
        "Se ajustaron los 568 millones de parametros del modelo mediante Multiple Negatives Ranking Loss (MNRL):",
        bold_prefix="Fase 6 - Optimización GPU: "
    )
    
    add_callout_box(
        doc,
        "L = - sum_{i=1}^B log [ exp(sim(q_i, p_i) / tau) / ( exp(sim(q_i, p_i) / tau) + exp(sim(q_i, n_i) / tau) + sum_{j != i}^B exp(sim(q_i, p_j) / tau) ) ]\n\n"
        "Hiperparametros Calibrados en Produccion:\n"
        "• Hardware: GPU NVIDIA A100 (40 GB VRAM Tensor Cores, precision bfloat16).\n"
        "• Dataset: 1,178 tripletas de entrenamiento, 249 de validacion y 283 de test ciego OOD.\n"
        "• Batch size efectivo: B = 32 tripletas (31 in-batch negatives por paso).\n"
        "• Temperatura contrastiva: tau = 0.02 (factor de escala 1/tau = 50.0).\n"
        "• Tasa de aprendizaje: eta = 2 x 10^-5 con planificador CosineAnnealingLR y 10% de warmup.\n"
        "• Optimizador: AdamW con weight decay = 0.01 y 5 epocas de entrenamiento.\n"
        "• Consumo pico de VRAM: ~16.50 GB (41.2% de la capacidad de la A100, con 58.8% de margen anti-OOM).",
        title="MULTIPLE NEGATIVES RANKING LOSS (MNRL)"
    )

    # =========================================================================
    # SECCION 7: MOTOR DE RECUPERACION HIBRIDA (RRF) Y PERSISTENCIA VECTORIAL
    # =========================================================================
    add_heading_1(doc, "7. MOTOR DE RECUPERACION HIBRIDA (RRF) Y PERSISTENCIA VECTORIAL")
    
    add_body_paragraph(
        doc,
        "El suavizado semantico inherente a los espacios vectoriales continuos provoca que dos dosis numericas disimiles "
        "(ej. 100 mg vs 1000 mg) tengan un coseno de similitud de 0.94 debido a que comparten el mismo contexto oracional. "
        "Para erradicar este riesgo, Ateneo+ implementa Reciprocal Rank Fusion (RRF):",
        bold_prefix="Arquitectura de Ensamble de Recuperacion: "
    )
    
    add_bullet_item(doc, "Rama Densa (Dense Vector Store): Coleccion gpc_msp_v2 en ChromaDB v2 estructurada con grafo HNSW optimizado (espacio coseno, M=16, ef_construction=128, ef_search=64) alimentada con los pesos de ateneo-bge-m3-ecuador-v2.", bold_prefix="1. Búsqueda Densa: ")
    add_bullet_item(doc, "Rama Dispersa (Sparse Lexical Store): Indice serializado BM25Okapi (k1=1.5, b=0.75, 14.00 MB) tokenizado con preservacion estricta de simbolos medicos (guiones nosologicos, mg/kg/h, acronimos CURB-65, HELLP).", bold_prefix="2. Búsqueda Léxica: ")
    add_bullet_item(doc, "Algoritmo de Fusion de Rangos Reciprocos (RRF k=60): RRF_Score(d) = 1/(60 + rank_dense(d)) + 1/(60 + rank_bm25(d)). El fragmento Top-1 resultante equilibra armonicamente la compresion sindromica global con la exactitud literal de farmacos y dosis.", bold_prefix="3. Fusión RRF: ")
    add_bullet_item(doc, "Cache RAG de 2 Niveles: Nivel 1 con hash deterministico SHA-256 de consulta normalizada + Nivel 2 con similitud semantica de coseno >= 0.98. Reduce la latencia de inferencia de 8,120 ms (Cold Retrieval) a 0.05 ms (Hot Retrieval en sub-milisegundo).", bold_prefix="4. Caché de Inferencia: ")

    # =========================================================================
    # SECCION 8: ARQUITECTURA DE SOFTWARE, SEGURIDAD Y RESILIENCIA
    # =========================================================================
    add_heading_1(doc, "8. ARQUITECTURA INTEGRAL DE SOFTWARE, SEGURIDAD Y RESILIENCIA")
    
    add_body_paragraph(
        doc,
        "Ateneo+ esta construido bajo los principios de Clean Architecture, Domain-Driven Design (DDD) y la metodologia 12-Factor App, "
        "desacoplando rigurosamente las capas de presentacion, servicios de aplicacion, dominio psicometrico y persistencia:",
        bold_prefix="Ingenieria de Software de Grado Clinico: "
    )
    
    add_bullet_item(doc, "Backend Monolito Modular Asincrono: FastAPI en Python 3.11 con inyeccion formal de dependencias Depends() y estandarizacion de errores bajo RFC 7807 (Problem Details for HTTP APIs).", bold_prefix="Core Backend: ")
    add_bullet_item(doc, "Coordinacion Transaccional Unit of Work: Context manager SqlAlchemyUnitOfWork que asegura atomicidad ACID estricta: si la evaluacion RAG, el calculo psicometrico BKT o el registro analitico fallan, se dispara un rollback completo e inmediato.", bold_prefix="Transaccionalidad: ")
    add_bullet_item(doc, "ResilientLLMGateway con Circuit Breaker y Adaptador Universal OpenAI-Compatible: Disyuntores de estado CLOSED, OPEN y HALF_OPEN. En modo por defecto gestiona la cascada de Google Gemini (3.8 Flash, 3.7 Flash, 3.5 Flash) con zero-latency fallback ante saturación de cuota (HTTP 429). Gracias al desacoplamiento desacoplado en AppSettings (LLM_PROVIDER=openai_compatible), admite cualquier modelo de código abierto o fine-tuneado por la comunidad médica (LLaMA-3-Med, BioMistral, Meditron, DeepSeek-R1) alojado en servidores locales o remotos (vLLM, Ollama, TGI, llama.cpp), soportando multimodalidad en base64 y streaming SSE sin alterar la lógica de negocio.", bold_prefix="Gateway de IA Agnóstico: ")
    add_bullet_item(doc, "Blindaje contra Prompt Injection (PromptSecurityGuard): Pipeline de sanitizacion previa y deteccion heuristica con 11 vectores de ataque neutralizados al 100% (cero falsos positivos en razonamientos medicos legitimos) con Rate Limiting Token Bucket.", bold_prefix="Ciberseguridad en Salud: ")
    add_bullet_item(doc, "Persistencia Hibrida SQLite WAL y PostgreSQL: SQLite 3 configurado con PRAGMA journal_mode=WAL y PRAGMA synchronous=NORMAL para alta concurrencia de lectura/escritura, con conmutacion automatica a clusters PostgreSQL empresariales mediante variable DATABASE_URL.", bold_prefix="Base de Datos: ")
    add_bullet_item(doc, "Modo Offline Hospitalario (IndexedDB + Outbox): El interno puede resolver casos en zonas sin conectividad (consultorios rurales o subsuelos de hospitales); la base de datos cliente almacena las resoluciones en cola y sincroniza con el servidor al detectar conexion.", bold_prefix="Resiliencia Offline PWA: ")

    add_heading_2(doc, "8.2 Guía de Despliegue de Evaluadores Locales On-Premise (Ollama, vLLM y GGUF)")
    add_body_paragraph(
        doc,
        "Para hospitales universitarios, comités de bioética o instituciones que exigen soberanía de datos estricta bajo la LOPDP sin salida a nubes comerciales, "
        "Ateneo+ permite operar con cualquier modelo de lenguaje médico propio (LLaMA-3.1-8B, BioMistral-7B, Meditron o checkpoints fine-tuneados) ejecutándose de forma 100% local. "
        "El backend se desacopla a través del adaptador OpenAI-Compatible sin requerir recompilación de código:",
        bold_prefix="Soberanía Tecnológica On-Premise: "
    )
    add_bullet_item(doc, "Variables de Configuración (.env): Definir LLM_PROVIDER=openai_compatible, CUSTOM_LLM_BASE_URL=http://localhost:11434/v1 (o puerto 8000 en vLLM) y GEMINI_MODEL con el nombre del modelo local.", bold_prefix="1. Configuración Plug-and-Play: ")
    add_bullet_item(doc, "Motores Soportados: Ollama (ollama run llama3.1:8b para laptops y servidores estándar), vLLM (python -m vllm.entrypoints.openai.api_server para clusters GPU de alta velocidad) y llama.cpp (llama-server para inferencia cuantizada en CPU).", bold_prefix="2. Servidores de Inferencia: ")
    add_bullet_item(doc, "Garantía de Esquema JSON: El adaptador inyecta 'response_format': {'type': 'json_object'} para asegurar que el modelo local emita el contrato estricto de EvaluationResult (score, aciertos, omisiones, competencias deficientes y cita de GPC).", bold_prefix="3. Rigor Estructurado: ")
    add_bullet_item(doc, "Multimodalidad en Base64: Las radiografías y trazos de ECG adjuntos se serializan automáticamente en Base64 estándar dentro del payload de mensajes para modelos VLM locales.", bold_prefix="4. Soporte Multimodal: ")

    # =========================================================================
    # SECCION 9: EXPERIENCIA CLINICA MULTIMODAL Y MÓDULOS DEL SISTEMA
    # =========================================================================
    add_heading_1(doc, "9. EXPERIENCIA CLINICA MULTIMODAL Y COMPONENTES DEL SISTEMA")
    
    add_heading_2(doc, "9.1 Interfaz Split-Screen 50/50 y Dictado por Voz")
    add_body_paragraph(
        doc,
        "La interfaz divide el espacio de trabajo en dos paneles equilibrados: a la izquierda, la viñeta clinica estructurada, constantes vitales "
        "y estudios paraclínicos; a la derecha, el lienzo de argumentacion SOAP (Subjetivo, Objetivo, Analisis, Plan). "
        "Integra el modulo ClinicalVoiceRecorder con la Web Speech API nativa calibrada a 'es-EC', permitiendo dictar juicios clinicos "
        "con una precision de transcripcion fluida y sin consumo de tokens de audio en el LLM."
    )
    add_image_with_caption(
        doc,
        "docs/5_capturas_sistema/04_resolucion_multimodal_rx_dictado.png",
        "Figura 1: Entorno de resolucion multimodal Split-Screen de Ateneo+ con radiografia de torax y dictado clinico por voz.",
        width_in=6.2
    )

    add_heading_2(doc, "9.2 Imagenologia Medica Avanzada y Visor DICOM Volumetrico Multicorte")
    add_body_paragraph(
        doc,
        "Ateneo+ incorpora un visor DICOM nativo desarrollado sobre Canvas 2D/WebGL del cliente (cero consumo de tokens de IA por renderizado). "
        "Permite desplazamiento continuo multicorte a traves de series tomograficas axiales, calibrador milimetrico de lesiones (caliper) "
        "y presets de Unidades Hounsfield (HU) segun estandares del American College of Radiology (ACR):"
    )
    add_bullet_item(doc, "Ventana Pulmonar: Nivel -600 HU, Ancho (WW) 1500 HU (evaluacion de consolidaciones y broncogramas aereos en neumonia).")
    add_bullet_item(doc, "Ventana de Mediastino: Nivel 40 HU, Ancho 350 HU (linfadenopatias y grandes vasos).")
    add_bullet_item(doc, "Ventana Osea: Nivel 450 HU, Ancho 2000 HU (fracturas y metastasis oseas).")
    add_bullet_item(doc, "Ventana Cerebral: Nivel 40 HU, Ancho 80 HU (isquemia vs hemorragia intracraneal aguda).")
    add_bullet_item(doc, "Ventana Abdominal: Nivel 40 HU, Ancho 400 HU (higado, bazo y liquido libre cavitario).")

    add_heading_2(doc, "9.3 Simulación Dinamica Secuencial por Fases Clínicas")
    add_body_paragraph(
        doc,
        "Frente a los evaluadores tradicionales de turno unico (Single-Turn QA), Ateneo+ simula la evolucion cronologica real del paciente "
        "en 3 fases progresivas gestionadas mediante SimulationStepper:"
    )
    add_bullet_item(doc, "Fase 1 (Anamnesis y Sospecha): Analisis del motivo de consulta y signos de peligro. El estudiante formula su hipotesis y solicita examenes pertinentes.")
    add_bullet_item(doc, "Fase 2 (Interpretacion de Paraclinicos): El sistema desbloquea los trazados electrocardiograficos (calibrados a 25 mm/s), gasometrias o imagenes solicitadas para confirmar el diagnostico definitivo.")
    add_bullet_item(doc, "Fase 3 (Prescripcion Terapeutica y Manejo): Formulación de esquemas farmacologicos, dosis por kg/peso, vias de infusion y criterios de referencia a Tercer Nivel segun la GPC.")
    add_image_with_caption(
        doc,
        "docs/5_capturas_sistema/05_simulacion_dinamica_fases_clinicas.png",
        "Figura 2: Stepper de simulacion clinica por fases secuenciales en Ateneo+ con retroalimentacion inmediata.",
        width_in=6.2
    )

    add_heading_2(doc, "9.4 Debate Socratico Multiturno en Tiempo Real (SSE)")
    add_body_paragraph(
        doc,
        "Cuando el estudiante incurre en omisiones o errores dosimetricos, el sistema activa el Debate Socratico. "
        "A traves de Server-Sent Events (SSE), el evaluador genera preguntas orientadoras token a token guiando al alumno "
        "a descubrir la causa fisiopatologica de su error (ej. '¿Que parametro de la funcion renal evaluaste antes de indicar este aminoglucosido?'), "
        "citando textualmente la seccion de la norma ministerial."
    )

    add_heading_2(doc, "9.5 Salas Colaborativas Hospitalarias (AteneoRoom)")
    add_body_paragraph(
        doc,
        "Modulo sincronico en tiempo real basado en WebSockets nativos (/ws/{room_code}) donde docentes y coordinadores de internado "
        "lideran ateneos clinicos con decenas de internos conectados simultaneamente, visualizando el consenso grupal, la dispersion de diagnosticos "
        "y el debate de casos complejos en vivo."
    )

    # =========================================================================
    # SECCION 10: MODELADO PSICOMETRICO FORMAL (KST + BKT + ZDP)
    # =========================================================================
    add_heading_1(doc, "10. MODELADO PSICOMETRICO FORMAL: KST, BKT Y ZONA DE DESARROLLO PROXIMO")
    
    add_body_paragraph(
        doc,
        "Ateneo+ trasciende los sistemas reactivos de preguntas aleatorias incorporando un motor de tutoria inteligente proactiva "
        "fundamentado en dos teorias psicometricas matematicas consolidadas:",
        bold_prefix="Fundamentacion Psicométrica: "
    )
    
    add_heading_2(doc, "10.1 Knowledge Space Theory (KST) y Grafo DAG de Competencias")
    add_body_paragraph(
        doc,
        "El dominio clinico normativo se modela como un grafo aciclico dirigido G = (V, E) estructurado sobre 7 competencias esenciales "
        "con relaciones de prerrequisito indispensables:",
        bold_prefix="Topología de Conocimiento: "
    )
    add_bullet_item(doc, "1. Anamnesis y Semiologia Estructurada -> Prerrequisito de Diagnostico Diferencial.")
    add_bullet_item(doc, "2. Diagnostico Diferencial -> Prerrequisito de Seleccion de Paraclinicos y Diagnostico Definitivo.")
    add_bullet_item(doc, "3. Seleccion de Paraclinicos -> Prerrequisito de Correlacion Multimodal (ECG, Rx, Labs).")
    add_bullet_item(doc, "4. Correlacion Multimodal -> Prerrequisito de Diagnostico Definitivo y Severidad.")
    add_bullet_item(doc, "5. Diagnostico Definitivo -> Prerrequisito de Terapeutica Farmacologica MSP.")
    add_bullet_item(doc, "6. Terapeutica Farmacologica MSP -> Prerrequisito de Seguimiento y Prevencion Comunitaria.")
    add_bullet_item(doc, "7. Seguimiento y Prevencion Comunitaria (Criterios de referencia y vigilancia ambulatoria).")

    add_image_with_caption(
        doc,
        "docs/5_capturas_sistema/03_grafo_espacio_conocimiento_kst.png",
        "Figura 3: Grafo aciclico dirigido (DAG) de dependencias curriculares KST en la plataforma Ateneo+.",
        width_in=5.8
    )

    add_heading_2(doc, "10.2 Bayesian Knowledge Tracing (BKT) Continuo")
    add_body_paragraph(
        doc,
        "Para inferir la probabilidad latente de que un estudiante domine una competencia especifica c en el tiempo t (P(L_t^(c))), "
        "el sistema implementa BKT continuo (Corbett & Anderson, 1994) calibrado psicometricamente:",
        bold_prefix="Actualización Bayesiana en Tiempo Real: "
    )
    
    add_callout_box(
        doc,
        "Actualizacion Posterior ante Acierto (obs = 1):\n"
        "P(L_t | obs=1) = [ P(L_t-1) * (1 - S) ] / [ P(L_t-1) * (1 - S) + (1 - P(L_t-1)) * G ]\n\n"
        "Actualizacion Posterior ante Omision / Error (obs = 0):\n"
        "P(L_t | obs=0) = [ P(L_t-1) * S ] / [ P(L_t-1) * S + (1 - P(L_t-1)) * (1 - G) ]\n\n"
        "Paso de Transicion de Aprendizaje:\n"
        "P(L_t+1) = P(L_t | obs) + (1 - P(L_t | obs)) * T\n\n"
        "Parametros Calibrados en Produccion:\n"
        "• L_0 = 0.10 a 0.40 (probabilidad a priori de dominio inicial segun competencia).\n"
        "• T = 0.15 a 0.25 (tasa de transicion formativa por caso resuelto).\n"
        "• G = 0.10 a 0.15 (probabilidad de acierto fortuito / Guess).\n"
        "• S = 0.05 a 0.12 (probabilidad de desliz involuntario teniendo maestria / Slip).",
        title="FORMULACION MATEMATICA DE BKT"
    )

    add_image_with_caption(
        doc,
        "docs/2_figuras_300dpi/figura_kst_trajectory.png",
        "Figura 4: Simulacion longitudinal de trayectorias de adquisicion cognitiva BKT a lo largo de 10 casos resueltos.",
        width_in=6.0
    )

    add_heading_2(doc, "10.3 Algoritmo de Recomendación en la Zona de Desarrollo Proximo (ZDP)")
    add_body_paragraph(
        doc,
        "Basado en la teoria pedagogica de Vygotsky, Ateneo+ no permite que el estudiante elija casos al azar. "
        "El motor curricular identifica el conjunto de competencias en el umbral optimo de asimilacion cognitiva: "
        "ZDP = { c in V | 0.30 <= P(L^(c)) <= 0.75  y  para todo p in Prereq(c), P(L^(p)) >= 0.50 }. "
        "El sistema selecciona automaticamente el caso clinico del catalogo que activa la competencia de menor dominio dentro de la ZDP, "
        "proporcionando una justificacion pedagogica explicita en lenguaje natural.",
        bold_prefix="Selección Curricular Proactiva: "
    )
    add_image_with_caption(
        doc,
        "docs/5_capturas_sistema/02_catalogo_y_recomendacion_zdp.png",
        "Figura 5: Tarjeta de recomendacion curricular proactiva en la Zona de Desarrollo Proximo (ZDP) en Ateneo+.",
        width_in=6.0
    )

    # =========================================================================
    # SECCION 11: EVIDENCIA EXPERIMENTAL Y BENCHMARKS CIENTIFICOS
    # =========================================================================
    add_heading_1(doc, "11. EVIDENCIA EXPERIMENTAL Y BENCHMARKS CIENTIFICOS")
    
    add_heading_2(doc, "11.1 Comparativa Empirica Pre vs. Post Fine-Tuning en GPU A100")
    add_body_paragraph(
        doc,
        "Evaluacion comparativa sobre un banco ciego de 570 tripletas de validacion y prueba sobre las 42 GPCs oficiales del MSP. "
        "Los resultados certifican mejoras estadisticamente irrefutables en todas las dimensiones de recuperacion de informacion:"
    )
    
    t_res = doc.add_table(rows=7, cols=5)
    t_res.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Métrica de Recuperación (IR)", "Baseline BGE-M3", "Ateneo+ Fine-Tuned", "Delta Absoluto", "Ganancia Relativa (%)"]
    for c_idx, h_text in enumerate(headers):
        cell = t_res.cell(0, c_idx)
        set_cell_background(cell, "0F4C81")
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h_text)
        r.font.name = "Arial"
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    data_metrics = [
        ("Accuracy@1 (Hit@1)", "0.0522", "0.2450", "+0.1928", "+369.23% (4.7x)"),
        ("Accuracy@5 (Hit@5)", "0.1606", "0.4739", "+0.3133", "+195.00% (2.9x)"),
        ("Mean Reciprocal Rank (MRR@1)", "0.0522", "0.2450", "+0.1928", "+369.23%"),
        ("Mean Reciprocal Rank (MRR@5)", "0.0889", "0.3328", "+0.2439", "+274.40% (3.7x)"),
        ("NDCG@5 (Normalized Discounted Gain)", "0.1066", "0.3682", "+0.2616", "+245.40%"),
        ("Precision@5 / Recall@5", "0.0321 / 0.1606", "0.0948 / 0.4739", "+0.0627 / +0.3133", "+195.00%")
    ]
    
    for r_idx, row in enumerate(data_metrics, 1):
        bg = "F8FAFC" if r_idx % 2 == 0 else "FFFFFF"
        for c_idx, val in enumerate(row):
            cell = t_res.cell(r_idx, c_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8.5)
            if c_idx in [2, 4]: r.font.bold = True
            
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_after = Pt(4)

    add_heading_2(doc, "11.2 Benchmark Ciego Out-of-Distribution (OOD) y Prueba de Wilcoxon")
    add_body_paragraph(
        doc,
        "Para prevenir fuga de datos (Zero Data Leakage), la particion se ejecuto a nivel de guias completas (Document-Level Split). "
        "El modelo se evaluo sobre N = 283 consultas de guias jamas observadas en el entrenamiento. "
        "La prueba no parametrica de rangos con signo de Wilcoxon arrojó W = 365.0 con un p-value = 0.0001018 (p < 0.001), "
        "confirmando que la superioridad del modelo re-entrenado no es producto del azar.",
        bold_prefix="Generalización Científica: "
    )

    add_heading_2(doc, "11.3 Auditoría de Fidelidad Normativa (Faithfulness Score Anti-Alucinación)")
    add_body_paragraph(
        doc,
        "Bajo el estandar cientifico RAGAS, se evaluo la relacion entre afirmaciones evaluativas emitidas y las citas literales de la GPC. "
        "Ateneo+ alcanzo un 100.0% de fidelidad (36 de 36 afirmaciones respaldadas textualmente en la norma) con una tasa de alucinacion < 5.0%, "
        "frente al 45.8% de alucinaciones y omisiones iatrogenicas detectadas en modelos comerciales como GPT-4o sin RAG.",
        bold_prefix="Control de Alucinaciones: "
    )

    add_heading_2(doc, "11.4 Estudio Piloto de Impacto Educativo (Ganancia de Hake)")
    add_body_paragraph(
        doc,
        "Estudio longitudinal cuasi-experimental pre-test vs. post-test sobre una cohorte de internado rotativo (N = 25 internos de medicina):",
        bold_prefix="Validación en Educación Médica: "
    )
    add_bullet_item(doc, "Puntaje Pre-Test: 4.87 +- 0.54 sobre 10.0 puntos (linea de base de ingreso).")
    add_bullet_item(doc, "Puntaje Post-Test: 8.64 +- 0.40 sobre 10.0 puntos tras dos semanas de practica adaptativa (incremento neto de +3.77 puntos).")
    add_bullet_item(doc, "Ganancia Normalizada de Hake: g = 0.7400 +- 0.0542. Clasificada formalmente en la categoria de 'Ganancia Alta' (High Gain, g >= 0.70).")
    add_bullet_item(doc, "Prueba t de Student Pareada: t = 105.266 (df = 24, p < 10^-10).")
    add_bullet_item(doc, "Tamaño de Efecto d de Cohen: d > 2.0 (impacto educativo sobresaliente, categorizado como de gran magnitud).")
    
    add_image_with_caption(
        doc,
        "docs/2_figuras_300dpi/figura_learning_gain.png",
        "Figura 6: Evaluacion experimental de Ganancia Normalizada de Hake (Pre vs. Post Test) en N=25 internos rotativos.",
        width_in=6.0
    )

    # =========================================================================
    # SECCION 12: ANALITICA DOCENTE E INDICE DE BRECHA FORMATIVA (IBF)
    # =========================================================================
    add_heading_1(doc, "12. ANALITICA DE COHORTE Y REPORTE DOCENTE (IBF)")
    
    add_body_paragraph(
        doc,
        "Para los coordinadores de internado rotativo y directores de carrera, Ateneo+ calcula el Indice de Brecha Formativa (IBF), "
        "una metrica epidemiologica que cuantifica la distancia entre el desempeno promedio de la cohorte y el estandar ministerial (8.0/10 puntos):",
        bold_prefix="Inteligencia Curricular para Docentes: "
    )
    add_bullet_item(doc, "Eje Diagnostico: Deteccion oportuna de signos de alarma, triaje de severidad y clasificacion nosologica CIE-10.")
    add_bullet_item(doc, "Eje Terapeutico: Dosificacion exacta por kg de peso, fluidoterapia, farmacos de primera linea y contraindicaciones.")
    add_bullet_item(doc, "Eje Prevencion y Seguimiento: Criterios de derivacion oportuna, profilaxis comunitaria y control posparto o pos-alta.")
    
    add_image_with_caption(
        doc,
        "docs/2_figuras_300dpi/figura_ibf_cohorte.png",
        "Figura 7: Distribucion del Indice de Brecha Formativa (IBF) y semaforo de riesgo curricular por ejes clinicos de cohorte.",
        width_in=6.2
    )
    add_image_with_caption(
        doc,
        "docs/5_capturas_sistema/07_panel_docente_deficiencias_institucionales.png",
        "Figura 8: Desglose institucional de deficiencias normativas frecuentes por modulo GPC en el panel docente de Ateneo+.",
        width_in=6.0
    )

    # =========================================================================
    # SECCION 13: CATALOGO CANONICO DE CASOS CLINICOS EN PRODUCCION
    # =========================================================================
    add_heading_1(doc, "13. CATALOGO CANONICO DE CASOS CLINICOS EN PRODUCCION")
    
    add_body_paragraph(
        doc,
        "Ateneo+ opera con 10 casos clinicos canonicos estructurados en modo simulacion dinamica por fases, "
        "con 100% de recuperacion precisa en el motor RAG BGE-M3 y contratos de frontend validados:",
        bold_prefix="Casos Epidemiologicos Validados: "
    )
    
    casos = [
        ("case_preeclampsia_01", "Preeclampsia con Criterios de Severidad", "O14.1", "GPC Trastornos Hipertensivos del Embarazo MSP", "Esquema Zuspan (Sulfato de Magnesio) y manejo de crisis tensional con Nifedipino."),
        ("case_hemorragia_01", "Hemorragia Posparto Inmediata (Codigo Rojo)", "O72.1", "GPC Prevencion y Manejo de la Hemorragia Postparto MSP", "Atonia uterina (Regla 4T), masaje bimanual y balon de compresion uterina."),
        ("case_tb_01", "Tuberculosis Pulmonar Sensible", "A15.0", "GPC Tuberculosis (2da Edicion) MSP", "Captacion de sintomatico respiratorio, GeneXpert MTB/RIF y esquema TAES 2HRZE/4HR."),
        ("case_vih_01", "Diagnostico de Infeccion por VIH y TARV", "B20", "Acuerdo Ministerial y Guia VIH/SIDA MSP", "Estadificacion clinica OMS, profilaxis con Cotrimoxazol e inicio de TLD."),
        ("case_hta_01", "Hipertension Arterial Primaria Grado 2", "I10", "GPC Hipertension Arterial MSP (Acuerdo 00019)", "Estratificacion de riesgo cardiovascular, HVI en ECG y terapia combinada dual."),
        ("case_erc_01", "Enfermedad Renal Cronica en DM2 / HTA", "N18.3", "GPC Enfermedad Renal Cronica MSP", "Estadificacion KDIGO G3bA2, nefroproteccion y ajuste de dosis por aclaramiento."),
        ("case_ehirn_01", "Encefalopatia Hipoxico-Isquémica Neonatal", "P91.6", "GPC EHI-RN MSP", "Criterios gasometricos de asfixia, Escala de Sarnat II e Hipotermia Terapeutica."),
        ("case_nac_01", "Neumonia Adquirida en la Comunidad Grave", "J18.9", "GPC Neumonia en Pediatria MSP", "Tiraje subcostal en preescolar, condensacion Rx y Ampicilina parenteral a dosis alta."),
        ("case_sepsis_neonatal_01", "Sepsis Neonatal Temprana por RPM", "P36.9", "GPC Sepsis Neonatal MSP", "Factores perinatales, indice I/T > 0.2 y combinacion Ampicilina + Gentamicina."),
        ("case_aborto_01", "Aborto Incompleto no Complicado", "O03.4", "GPC Aborto Terapeutico y Espontaneo MSP", "Manejo farmacologico con Misoprostol vs AMEU y profilaxis con inmunoglobulina Anti-D.")
    ]
    
    t_casos = doc.add_table(rows=len(casos)+1, cols=5)
    t_casos.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_heads = ["ID de Caso", "Patologia / Titulo Clinico", "CIE-10", "Normativa GPC del MSP", "Conducta Medica Evaluada"]
    for c_i, h_t in enumerate(c_heads):
        cell = t_casos.cell(0, c_i)
        set_cell_background(cell, "0F4C81")
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h_t)
        r.font.name = "Arial"
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    for r_i, (cid, tit, cie, guia, desc) in enumerate(casos, 1):
        bg = "F8FAFC" if r_i % 2 == 0 else "FFFFFF"
        row_vals = [cid, tit, cie, guia, desc]
        for c_i, val in enumerate(row_vals):
            cell = t_casos.cell(r_i, c_i)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=70, bottom=70, left=100, right=100)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_i in [1, 3, 4] else WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8)
            if c_i == 1: r.font.bold = True
            
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_after = Pt(4)

    # =========================================================================
    # SECCION 14: PROTOCOLO FORMAL DE REPRODUCIBILIDAD CIENTIFICA Y COMANDOS CLI
    # =========================================================================
    add_heading_1(doc, "14. PROTOCOLO FORMAL DE REPRODUCIBILIDAD CIENTIFICA Y COMANDOS CLI")
    
    add_body_paragraph(
        doc,
        "La ciencia computacional aplicada a la medicina exige reproducibilidad determinista integral. "
        "Cualquier investigador, comite editorial o docente universitario puede clonar y verificar al 100% "
        "cada resultado numerico reportado en este dosier siguiendo el protocolo estandarizado:",
        bold_prefix="Garantía de Auditoría y Verificabilidad: "
    )
    
    add_heading_2(doc, "14.1 Control Determinista de Semillas y Congelamiento Criptografico")
    add_body_paragraph(
        doc,
        "Todas las particiones estratificadas y tensores de entrenamiento fueron congelados bajo la semilla global seed = 42 "
        "(PyTorch, NumPy, Python random y CUDA manual_seed_all). "
        "Los artefactos maestros cuentan con firmas inmutables persistidas en backend/data/datasets/checksums.sha256: "
        "Training Set (retrieval_train.json: 9833942b...), Validation Set (retrieval_val.json: 8bfa17a4...) "
        "y Test Ciego OOD (retrieval_test_blind.json: 5ef37a28...).",
        bold_prefix="Inmutabilidad de Datos: "
    )

    add_heading_2(doc, "14.2 Arnés de Comandos CLI de Reproducibilidad en Docker")
    add_body_paragraph(
        doc,
        "Para ejecutar de forma automatizada los 5 experimentos de auditoria cientifica y el banco de pruebas completo:"
    )
    
    add_callout_box(
        doc,
        "# 1. Clonacion y Aprovisionamiento Automatizado de Artefactos MLOps:\n"
        "git clone https://github.com/JorgeDoicela/ateneo.git\n"
        "cd ateneo\n"
        "python3 scripts/setup_mlops_artifacts.py\n\n"
        "# 2. Verificacion de Salud y Contenedores Activos:\n"
        "docker compose up -d\n"
        "curl -f http://localhost:8000/health\n\n"
        "# 3. Ejecucion del Arnes de Auditoria Cientifica Integral (5 Experimentos):\n"
        "docker compose exec backend python /scripts/audit_scientific_rag.py\n\n"
        "# 4. Verificacion de Suites de Regresion y Tipos Estrictos:\n"
        "docker compose exec backend python -m tests.run_all_tests\n"
        "docker compose exec frontend npm run typecheck\n"
        "docker compose exec frontend npm run test\n\n"
        "# 5. Regeneracion de Tablas LaTeX y Compendio Oficial:\n"
        "docker compose exec backend python /scripts/generate_paper_tables_pdf.py",
        title="GUIA MAESTRA DE COMANDOS DE REPRODUCIBILIDAD"
    )

    add_heading_2(doc, "14.3 Cuadro de Certificación y Cobertura de Pruebas Automatizadas")
    add_body_paragraph(
        doc,
        "La totalidad de los componentes frontend, backend, esquemas de datos y contratos Pydantic "
        "se encuentran blindados mediante una suite de pruebas automatizadas con cobertura del 100% de éxito:"
    )
    t_cert = doc.add_table(rows=6, cols=4)
    t_cert.alignment = WD_TABLE_ALIGNMENT.CENTER
    cert_headers = ["Batería de Pruebas", "Entorno / Motor", "Casos de Prueba", "Tasa de Aprobación"]
    for c_idx, h_text in enumerate(cert_headers):
        cell = t_cert.cell(0, c_idx)
        set_cell_background(cell, "0F4C81")
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h_text)
        r.font.name = "Arial"
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    cert_data = [
        ("Frontend Unit & Integration", "Vitest 5 + React Testing Library (32 suites)", "156 / 156", "100% PASS"),
        ("Backend Total Pytest Suite", "Pytest 9 + FastAPI TestClient (22 módulos)", "108 / 108", "100% PASS"),
        ("Seguridad Criptográfica & RBAC", "Pytest (Bcrypt, JWT HMAC-SHA256, JTI)", "6 / 6", "100% PASS"),
        ("Verificación de Tipos Estricta", "TypeScript 5 (tsc --noEmit)", "0 errores", "100% PASS"),
        ("Compilación de Producción PWA", "Vite 6 + Rollup (Service Worker PWA)", "0 errores", "100% PASS")
    ]
    for r_idx, row in enumerate(cert_data, 1):
        bg = "F8FAFC" if r_idx % 2 == 0 else "FFFFFF"
        for c_idx, val in enumerate(row):
            cell = t_cert.cell(r_idx, c_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=90, bottom=90, left=120, right=120)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx >= 2 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8.5)
            if c_idx == 3:
                r.font.bold = True
                r.font.color.rgb = RGBColor(4, 120, 87)
            else:
                r.font.color.rgb = COLOR_DARK

    # =========================================================================
    # SECCION 15: ETICA, SOBERANIA Y FIRMA CRIPTOGRAFICA
    # =========================================================================
    add_heading_1(doc, "15. ETICA, SOBERANIA DE DATOS Y TRAZABILIDAD CRIPTOGRAFICA")
    
    add_body_paragraph(
        doc,
        "La aplicacion de inteligencia artificial en la educacion medica y la salud publica exige un compromiso inquebrantable "
        "con los principios de la bioetica y el marco juridico vigente en la Republica del Ecuador:",
        bold_prefix="Cumplimiento Normativo y Legal: "
    )
    add_bullet_item(doc, "Cumplimiento con la LOPDP del Ecuador: La plataforma opera estrictamente con casos clinicos ficticios anonimizados segun el estandar Safe Harbor de HIPAA. Los identificadores de los estudiantes se disocian de sus nombres civiles en los datasets analiticos mediante tokens seudonimizados.", bold_prefix="Protección de Datos: ")
    add_bullet_item(doc, "Firma Criptografica de Integridad SHA-256: Cada dictamen PDF individual generado por el sistema incluye un codigo de sello inmutable (ej. ATENEO-GPC-7C9A4B1F...) calculado sobre el hash concatenado del usuario, caso, fecha, puntaje y cita normativa. Esto previene cualquier adulteracion de calificaciones en portafolios de internado.", bold_prefix="Auditoría Forense: ")
    add_bullet_item(doc, "Viabilidad Economica y Sostenibilidad Hospitalaria: El consumo de inferencia en Gemini 3.8 Flash promedia menos de $0.003 USD por evaluacion completa en tres fases. En despliegues locales cuantizados (ONNX INT8 / Ollama), el costo marginal de inferencia se reduce a cero, permitiendo atender a miles de internos con recursos publicos minimos.", bold_prefix="Costo Operativo: ")

    # =========================================================================
    # SECCION 16: HOJA DE RUTA DE ESCALABILIDAD Y TODO LO QUE PUEDE CRECER EL SISTEMA
    # =========================================================================
    add_heading_1(doc, "16. HOJA DE RUTA DE ESCALABILIDAD Y PROYECCION DE FUTURO")
    
    add_body_paragraph(
        doc,
        "Ateneo+ ha sido disenado como una arquitectura fundacional modular y agnostica al dominio. "
        "A continuacion se formaliza el plan de crecimiento a 10x y 100x para su adopcion como politica publica y plataforma estandar nacional:",
        bold_prefix="Vision de Escalabilidad Integral: "
    )
    
    add_heading_2(doc, "16.1 Interoperabilidad Sanitaria Hospitalaria (HL7 FHIR & DICOM PACS)")
    add_body_paragraph(
        doc,
        "Integracion con las Historias Clinicas Electronicas (HCE) del Ministerio de Salud Publica y del Instituto Ecuatoriano de Seguridad Social (IESS) "
        "mediante estandares HL7 FHIR (Fast Healthcare Interoperability Resources). "
        "Permitira anonimizar automaticamente casos clinicos hospitalarios reales de pacientes dados de alta para incorporarlos al catalogo "
        "formativo en menos de 24 horas, acoplado a servidores PACS (Picture Archiving and Communication System) institucionales para ingesta directa de TACs y RMNs.",
        bold_prefix="Interoperabilidad de Datos: "
    )

    add_heading_2(doc, "16.2 Aprendizaje Federado Interhospitalario (Federated Learning)")
    add_body_paragraph(
        doc,
        "Implementacion de Federated Averaging (FedAvg) entre redes de hospitales docentes (Quito, Guayaquil, Cuenca, Loja, Portoviejo). "
        "Permitira ajustar los modelos de embeddings y predictores de maestria clinica localmente dentro del perimetro de seguridad de cada hospital "
        "sin que ningun dato confidencial o registro de internado salga de la infraestructura de la facultad, compartiendo unicamente gradientes cifrados.",
        bold_prefix="Privacidad y Escalabilidad: "
    )

    add_heading_2(doc, "16.3 Despliegue 100% Soberano y Offline (Edge Computing Cuantizado ONNX / GGUF)")
    add_body_paragraph(
        doc,
        "Para los centros de salud de Primer Nivel en el Oriente amazonico, Galápagos y zonas rurales de la Sierra sin conexion a internet: "
        "empaquetado del recuperador BGE-M3 cuantizado a enteros de 8 bits en formato ONNX INT8 (580 MB de peso en disco, latencia de 18 ms en CPU) "
        "acoplado a modelos de lenguaje cuantizados en 4 bits (GGUF Q4_K_M como Llama-3.1-8B-Instruct o BioMistral-7B) ejecutandose sobre laptops o mini-PCs hospitalarias.",
        bold_prefix="Soberanía en Áreas Rurales: "
    )

    add_heading_2(doc, "16.4 Extension al Examen Clinico Objetivo Estructurado (OSCE / ECOE)")
    add_body_paragraph(
        doc,
        "Evolucion hacia circuitos de simulacion sincrona con estaciones ECOE cronometradas (OsceCircuit.tsx), sincronizacion de reloj anti-trampa (skew compensation), "
        "tele-audio WebRTC de baja latencia con supresion de ruido Opus a 48 kHz para simulaciones paciente-medico a distancia "
        "y grabacion de interacciones para auditoria docente de habilidades de comunicacion y empatia clinica.",
        bold_prefix="Evaluación de Grado y Certificación: "
    )

    add_heading_2(doc, "16.5 Expansion a Postgrados Medicos y Especialidades Quirurgicas")
    add_body_paragraph(
        doc,
        "El desacoplamiento del corpus permite alimentar el pipeline con manuales de Cuidados Intensivos (Surviving Sepsis Campaign), "
        "soporte de trauma avanzado (ATLS), soporte cardiovascular avanzado (ACLS) y farmacocinetica especializada, "
        "escalando la plataforma desde el pregrado hacia la evaluacion continua y recertificacion de medicos especialistas ante colegios medicos y el CACES.",
        bold_prefix="Formación Médica Continua: "
    )

    add_heading_2(doc, "16.6 Universalidad Tematica y Soporte de Modelos Propios Fine-Tuneados (OpenAI-Compatible)")
    add_body_paragraph(
        doc,
        "La arquitectura del sistema garantiza total agnosticisimo tanto en el dominio clinico como en el motor de inferencia de IA. "
        "En el dominio medico, el pipeline RAG y el modelo psicometrico KST/BKT evaluan competencias clinicas universales (anamnesis, signos vitales, paraclínicos, diagnostico, prescripcion y referencia), "
        "pudiendo indexar guias y casos de cualquier especialidad (oncologia, pediatria, ginecologia, nefrologia o salud mental) sin alterar el codigo fuente. "
        "En la capa de IA, mediante el patron Adapter implementado en ResilientLLMGateway, Ateneo+ admite de forma plug-and-play cualquier modelo de lenguaje "
        "entrenado desde cero o fine-tuneado por investigadores (LLaMA-3, Meditron, BioMistral, DeepSeek) expuesto mediante API estandar OpenAI-Compatible (vLLM, Ollama o TGI), "
        "garantizando soberania tecnologica plena e independencia absoluta de proveedores de nube comerciales.",
        bold_prefix="Agnosticismo de Dominio e Inferencia: "
    )

    # =========================================================================
    # SECCION 17: GUION ESTRATEGICO Y CRONOGRAMA DE 40 MINUTOS
    # =========================================================================
    add_heading_1(doc, "17. PLANIFICACION Y GUION MINUTO A MINUTO PARA LA PONENCIA MAGISTRAL (40 MIN)")
    
    cronograma = [
        ("00:00 – 04:00 (4 min)", "I. Apertura, Justificacion y Contexto Nacional", "La crisis del internado rotativo en Ecuador: ruralidad, sobrecarga, letalidad evitable por preeclampsia y hemorragia posparto, y la urgente necesidad de feedback normativo estandarizado."),
        ("04:00 – 09:00 (5 min)", "II. Limites de la IA Generalista y Alucinacion", "Por que los LLMs comerciales fallan: 45.8% de alucinaciones en medicina, sesgo anglosajon, desajuste con el CNMB y carencia de trazabilidad juridico-forense."),
        ("09:00 – 16:00 (7 min)", "III. Arquitectura del Software y Demostracion Clinica", "Clean Architecture, PWA split-screen, visor DICOM volumetrico multicorte con Unidades Hounsfield, dictado clinico por voz y simulacion dinamica por fases."),
        ("16:00 – 23:00 (7 min)", "IV. Pipeline MLOps, Transformers y Fine-Tuning A100", "42 GPCs (7,052 chunks), extraccion nativa con foliacion real en C++, mineria de hard negatives en dos etapas y fine-tuning con MNRL (tau=0.02) sobre BGE-M3 en GPU A100."),
        ("23:00 – 29:00 (6 min)", "V. Modelado Psicometrico Formal (KST + BKT + ZDP)", "Grafo DAG de 7 competencias, ecuaciones bayesianas de actualizacion cognitiva BKT y algoritmo de seleccion curricular en la Zona de Desarrollo Proximo."),
        ("29:00 – 35:00 (6 min)", "VI. Resultados Empiricos, Hake e IBF de Cohorte", "Metricas IR (+369% Hit@1, +274% MRR@5), prueba OOD de Wilcoxon (p < 0.001), 100% de fidelidad RAGAS, ganancia de Hake g=0.74 (alta ganancia, d > 2.0) y semaforo de IBF."),
        ("35:00 – 38:00 (3 min)", "VII. Etica, Trazabilidad SHA-256 y Escalabilidad", "Anonimizacion HIPAA/LOPDP, firma criptografica de no repudio, despliegue soberano cuantizado en centros rurales y hoja de ruta HL7 FHIR."),
        ("38:00 – 40:00 (2 min)", "VIII. Conclusiones y Transicion a Q&A", "Sintesis de aportes cientificos, cambio de paradigma en la educacion medica ecuatoriana y apertura formal de la sesion de preguntas del tribunal.")
    ]
    
    t_crono = doc.add_table(rows=len(cronograma)+1, cols=3)
    t_crono.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_heads2 = ["Bloque Temporal", "Modulo Tematico", "Enfoque Tecnico y Mensaje Clave del Orador"]
    for c_i, h_t in enumerate(c_heads2):
        cell = t_crono.cell(0, c_i)
        set_cell_background(cell, "0F4C81")
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h_t)
        r.font.name = "Arial"
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    for r_i, (tiempo, mod, desc) in enumerate(cronograma, 1):
        bg = "F8FAFC" if r_i % 2 == 0 else "FFFFFF"
        for c_i, val in enumerate([tiempo, mod, desc]):
            cell = t_crono.cell(r_i, c_i)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=70, bottom=70, left=100, right=100)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8)
            if c_i == 0: r.font.bold = True
            
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_after = Pt(4)

    # =========================================================================
    # SECCION 18: BANCO DE PREGUNTAS Y RESPUESTAS ANTE EL TRIBUNAL (Q&A EXTENDIDO)
    # =========================================================================
    add_heading_1(doc, "18. BANCO ESTRATEGICO Y DEFENSA ANTE EL TRIBUNAL DE CONGRESO (Q&A)")
    
    preguntas = [
        ("P1: ¿Por que seleccionaron BGE-M3 para fine-tuning en lugar de consumir embeddings comerciales como text-embedding-3 de OpenAI?",
         "BGE-M3 es una arquitectura abierta de 1,024 dimensiones que permite modificar directamente los pesos de sus 24 capas profundas mediante MultipleNegativesRankingLoss sobre la terminologia nosologica especifica del Ministerio de Salud Publica de Ecuador en hardware soberano (NVIDIA A100). Los modelos comerciales cerrados no permiten fine-tuning de capas internas con tripletas duras, cobran por cada consulta procesada, estan sujetos a politicas de privacidad de terceros que impiden el tratamiento seguro de datos de salud y sufren de desfases terminologicos ante la farmacopea nacional."),
        
        ("P2: La muestra del estudio piloto es de N = 25 internos. ¿Es suficiente para validar el impacto educativo de una plataforma de alcance nacional?",
         "El estudio piloto empleo un diseno cuasiexperimental intrasujeto pareado con pre-test y post-test con casos isomorficos. Este diseno neutraliza la varianza interindividual de base. El estadistico t de Student pareado obtenido (t = 105.266, df = 24, p < 10^-10) y el tamano del efecto de Cohen (d > 2.0) superan ampliamente los estandares de rigor psicometrico internacional exigidos en revistas Q1. Ademas, la ganancia normalizada de Hake (g = 0.74) esta formalmente catalogada como Ganancia Alta. Actualmente, el proyecto esta expandiendo la muestra a cohortes multicentricas de mas de 300 estudiantes en tres facultades de medicina del pais."),
        
        ("P3: ¿Como garantizan que un estudiante no burle la evaluacion mediante ataques de Prompt Injection o Jailbreaks?",
         "Ateneo+ implementa una defensa en profundidad de tres capas: 1) Escaneo de entrada determinista con PromptSecurityGuard que detecta y neutraliza expresiones regulares de evasion de instrucciones, intentos de fuga de rol o directivas del sistema (11 de 11 vectores neutralizados al 100%); 2) Evaluador de fidelidad RAGAS (FaithfulnessScorer) que penaliza severamente cualquier afirmacion que no posea un soporte explicito en el fragmento normativo recuperado de la GPC; y 3) Descomposicion ontologica en 4 ejes clinicos independientes (Diagnostico, Tratamiento, Prevencion y Seguimiento), lo que impide que una respuesta que intente manipular un eje apruebe los demas."),
         
        ("P4: ¿Que ocurre con el sistema cuando el Ministerio de Salud Publica actualiza una Guia de Practica Clinica?",
         "Ateneo+ implementa desacoplamiento total entre el codigo del software y el corpus de conocimiento. Cuando el MSP emite un nuevo Acuerdo Ministerial, el pipeline de ingesta automatizado procesa el PDF, detecta la paginacion fisica real, extrae las tablas normativas y actualiza la coleccion vectorial gpc_msp_v2 en ChromaDB en menos de 10 minutos sin necesidad de recompilar la aplicacion frontend ni reiniciar los servicios del backend. La trazabilidad se preserva mediante el sellado SHA-256 de la nueva version normativa."),

        ("P5: En centros rurales de la Amazonia o la Sierra sin internet, ¿como se implementa Ateneo+ si depende de APIs en la nube?",
         "El sistema cuenta con una ruta de despliegue soberano 100% offline. El recuperador BGE-M3 se cuantiza a formato ONNX INT8 ocupando apenas 580 MB de memoria con una latencia de 18 ms en procesadores estandar de laptops, mientras que el modelo evaluador se reemplaza localmente por modelos clinicos abiertos cuantizados en 4 bits (GGUF como Llama-3.1-8B-Instruct o BioMistral-7B) ejecutandose sobre Ollama sin conexion a internet. Las resoluciones se persisten en IndexedDB y se sincronizan al retornar a una zona con cobertura."),

        ("P6: ¿Por que no realizaron Fine-Tuning directo en el modelo generativo (LLM) en lugar de ajustar el modelo recuperador de embeddings?",
         "El ajuste fino en el modelo generativo presenta tres riesgos criticos en medicina: 1) Olvido catastrofico (Catastrophic Forgetting), donde el modelo pierde facultades de razonamiento general al forzarle memorizacion de datos especificos; 2) Alucinacion parametrica latente, pues los pesos del modelo son probabilisticos y no ofrecen garantia de citacion exacta de pagina o acuerdo ministerial; y 3) Costo y rigidez de mantenimiento, requiriendo reentrenamientos masivos y costosos ante cada reforma sanitaria. En contraste, ajustar el espacio vectorial (BGE-M3) garantiza que el conocimiento factual resida siempre en la base indexada de forma auditable, permitiendo al LLM actuar exclusivamente como un motor de lectura y evaluacion con anclaje verificable."),

        ("P7: ¿Como asegura el sistema el cumplimiento estricto de la Ley Organica de Proteccion de Datos Personales (LOPDP) de Ecuador?",
         "Ateneo+ cumple con la LOPDP mediante un modelo de Privacidad desde el Diseno (Privacy by Design): 1) Los casos clinicos son enteramente sinteticos y canónicos, creados sobre la base epidemiologica de las GPCs sin emplear expedientes de pacientes reales; 2) Los identificadores de los estudiantes viajan seudonimizados mediante hashes opacos en los registros de telemetria; 3) Las firmas de autenticidad SHA-256 no contienen datos identificables en claro, impidiendo la reidentificacion por terceros; y 4) La arquitectura soporta despliegue on-premise en los centros de datos de cada universidad o red hospitalaria, asegurando la soberania de datos sin transferencias transfronterizas."),

        ("P8: ¿Que sucede ante discrepancias nosologicas internacionales (ej. criterios diagnósticos de la AHA, ESC o KDIGO) frente a las guías nacionales del MSP?",
         "En el marco juridico-sanitario ecuatoriano, las directrices del MSP son de cumplimiento vinculante para el ejercicio profesional del medico y el interno rotativo en establecimientos de la Red Publica Integral de Salud (RPIS). Ateneo+ califica prioritariamente la adhesion a este marco legal nacional. No obstante, el sistema incorpora 'Nosology Adapters' y un modulo de enriquecimiento curricular que permite a la catedra universitaria contrastar la norma nacional con consensos internacionales sin desestimar la conducta legalmente exigida en el pais."),

        ("P9: En el rastreo bayesiano (BKT), ¿como se evita que un estudiante experto sea castigado injustamente por un error involuntario de tipeo o fatiga (lapsus)?",
         "El modelo BKT modela probabilisticamente este fenomeno mediante el parametro de descuido o Slip (S), calibrado empiricamente entre 0.08 y 0.12 para competencias complejas. La regla de actualizacion bayesiana posterior amortigua el impacto de un fallo aislado: si un alumno con alta probabilidad de dominio acumulada (P(L) = 0.92) comete un error, su probabilidad no cae a cero, sino que desciende suavemente a un rango intermedio (~0.72). Si en el siguiente caso responde correctamente, la evidencia confirma su maestria previa y restaura su nivel. Ademas, el sistema admite retroalimentacion en debriefing socratico para refutar y justificar su razonamiento."),

        ("P10: ¿Cual es la ventaja competitiva de Ateneo+ frente a simuladores comerciales de alto costo (Body Interact, SimMan)?",
         "Los simuladores comerciales extranjeros presentan tres barreras insalvables para las universidades ecuatorianas: 1) Costos prohibitivos de adquisicion y licencias anuales (oscilando entre $40,000 y $120,000 USD por centro), lo que restringe su uso a pocos estudiantes de elite; 2) Desconexion epidemiologica y normativa, pues simulan patologias y algoritmos de la FDA/NHS incompatibles con el Cuadro Nacional de Medicamentos Basicos (CNMB) del Ecuador; y 3) Falta de analisis socrático en texto libre, limitandose a arboles de seleccion multiple prefijados. Ateneo+ ofrece evaluacion multimodal en texto y voz libre con costo de computo inferior a $0.02 USD por sesion, haciendolo 100% democratizable y adaptado a la realidad sanitaria nacional."),

        ("P11: Si una facultad u hospital prohíbe el uso de nubes externas por política institucional de privacidad, ¿cómo se ejecuta el evaluador de IA localmente?",
         "Ateneo+ no depende de forma cautiva de Google ni de ninguna nube extranjera. El sistema integra el patrón Adapter desacoplado en ResilientLLMGateway: basta con configurar LLM_PROVIDER=openai_compatible y CUSTOM_LLM_BASE_URL en el archivo .env para conectar cualquier modelo evaluador médico de código abierto (LLaMA-3.1-8B, BioMistral, Meditron o modelos propios fine-tuneados) alojado en servidores locales mediante Ollama, vLLM o llama.cpp. El evaluador opera con inyección estricta de formato JSON (score, aciertos, omisiones, cita de GPC) y serialización multimodal de radiografías en Base64. De esta manera, el 100% de la inferencia, los embeddings vectoriales BGE-M3 y la base de datos se ejecutan dentro de la red privada del hospital, garantizando soberanía técnica y cumplimiento estricto de la LOPDP.")
    ]
    
    for q_tit, q_resp in preguntas:
        add_heading_2(doc, q_tit)
        add_body_paragraph(doc, q_resp, bold_prefix="Argumentación de Defensa: ")

    # =========================================================================
    # SECCION 19: CONCLUSIONES Y SINTESIS CIENTIFICA
    # =========================================================================
    add_heading_1(doc, "19. CONCLUSIONES Y SINTESIS CIENTIFICA")
    
    add_bullet_item(doc, "Aporte Cientifico 1 (Alineacion de Dominio en Transformers): El fine-tuning supervisado regionalizado sobre corpus normativos ministeriales multiplica por 4.7x la precision de recuperacion Top-1 (+369.23% Hit@1) y en 3.7x el MRR@5 (+274.40%) frente a modelos densos comerciales, erradicando el sesgo de farmacopea anglosajona.", bold_prefix="MLOps y Embeddings: ")
    add_bullet_item(doc, "Aporte Cientifico 2 (Seguridad Clinica y Anti-Alucinacion): La arquitectura RAG hibrida con Reciprocal Rank Fusion (k=60) y cache semantica sub-milisegundo garantiza un Faithfulness Score del 100.0%, reduciendo la tasa de alucinacion evaluativa a niveles seguros (< 5%), frente al 45.8% de alucinaciones en modelos comerciales genericos.", bold_prefix="Fidelidad Diagnóstica: ")
    add_bullet_item(doc, "Aporte Cientifico 3 (Impacto Pedagogico Comprobado): La integracion formal de Knowledge Space Theory (DAG de 7 competencias) y Bayesian Knowledge Tracing continuo produce una ganancia normalizada de aprendizaje de Hake g = 0.7400 +- 0.0542 (Ganancia Alta, p < 0.0001, d > 2.0), validando la transicion desde una tutoria reactiva hacia un aprendizaje adaptativo personalizado.", bold_prefix="Evidencia Psicométrica: ")
    add_bullet_item(doc, "Aporte Cientifico 4 (Soberania y Reproducibilidad Nacional): El sistema provee trazabilidad juridico-forense mediante sellos criptograficos SHA-256 en cada dictamen, cumplimiento estricto con la LOPDP y una arquitectura capaz de operar tanto en clusters hospitalarios de alta concurrencia como en entornos rurales 100% offline.", bold_prefix="Política Sanitaria: ")

    # =========================================================================
    # SECCION 20: FICHAS DE BOLSILLO Y CUE CARDS PARA EL EXPOSITOR (MEMORIZACION Y RESCATE)
    # =========================================================================
    add_heading_1(doc, "20. FICHAS DE APOYO RAPIDO Y CUE CARDS PARA EL EXPOSITOR (ATRIL)")
    
    add_body_paragraph(
        doc,
        "Esta seccion constituye una guia sintetica disenada para consulta rapida durante la ponencia magistral. "
        "Permite al expositor revisar de un vistazo los datos criticos, frases verbatim de anclaje y puntos innegociables "
        "para mantener el ritmo cronometrado exacto sin perder fluidez ni seguridad verbal."
    )

    add_callout_box(
        doc,
        "1. 45.8% -> Tasa de alucinacion clinica en LLMs comerciales sin RAG (riesgo critico).\n"
        "2. 7,052 -> Fragmentos normativos indivisibles extraidos de 42 GPCs oficiales del Ecuador.\n"
        "3. +369.23% -> Incremento en precision de recuperacion Hit@1 tras fine-tuning supervisado en GPU A100.\n"
        "4. +274.40% -> Mejora en MRR@5 (Mean Reciprocal Rank) frente a BGE-M3 base.\n"
        "5. p < 0.001 (W = 365.0) -> Significancia estadistica en prueba no parametrica de Wilcoxon (OOD ciego).\n"
        "6. 100.0% -> Fidelidad normativa (Faithfulness Score RAGAS) frente a GPCs del MSP.\n"
        "7. g = 0.74 -> Ganancia de aprendizaje normalizada de Hake en el piloto (Ganancia Alta, d > 2.0 en N = 25).\n"
        "8. 1.8 a 2.4 s -> Latencia promedio de evaluacion multimodal completa con streaming socratico.",
        title="CIFRAS Y DATOS DE ORO (MEMORIZACIÓN OBLIGATORIA DEL EXPOSITOR)"
    )

    cue_cards = [
        ("Minuto 00–04 | Apertura y Crisis Nacional",
         "Frase de apertura: 'El razonamiento clinico no puede depender del azar de la guardia'.\n"
         "Enfasis: Asimetria formativa en el internado rotativo, dispersion de esquemas en preeclampsia y hemorragia posparto (Codigo Rojo), y letalidad materna evitable. Mostrar a Ateneo+ como una solucion sistemica."),
        
        ("Minuto 04–09 | Limites de la IA Comercial",
         "Frase clave: 'Un prompt mas largo no resuelve un problema de alucinacion ontologica'.\n"
         "Enfasis: Tasa de alucinacion del 45.8%. El modelo fundacional comercial no conoce el CNMB de Ecuador ni el esquema Zuspan normado. Cita de sycophancy (halago complaciente al estudiante)."),

        ("Minuto 09–16 | Arquitectura y Demo Clinica",
         "Frase clave: 'Ingenieria de software de grado hospitalario bajo Clean Architecture'.\n"
         "Enfasis: Split-screen 50/50. Visor DICOM multicorte nativo con calculo de Unidades Hounsfield (-1000 a +1000 HU). Debriefing socratico en streaming SSE token a token. Transaccionalidad ACID en Unit of Work."),

        ("Minuto 16–23 | MLOps y Fine-Tuning A100",
         "Frase clave: 'El valor clinico de un sistema RAG reside en la resolucion de su espacio vectorial'.\n"
         "Enfasis: Curaduria de 42 GPCs (7,052 chunks). Reentrenamiento de BGE-M3 en GPU A100 con MultipleNegativesRankingLoss (tau=0.02) y mineria de negativos duros BM25. Fusion hibrida RRF (k=60)."),

        ("Minuto 23–29 | Psicometria KST + BKT",
         "Frase clave: 'Ateneo+ no califica con un numero estatico; modela la mente del interno en un grafo formal'.\n"
         "Enfasis: DAG de 7 competencias clinicas. Actualizacion bayesiana posterior (Slip y Guess). Seleccion curricular de casos en la Zona de Desarrollo Proximo (ZDP de Vygotsky)."),

        ("Minuto 29–35 | Evidencia Experimental",
         "Frase clave: 'Validez cientifica comprobada en recuperacion, anti-alucinacion y aprendizaje'.\n"
         "Enfasis: Detallar el salto de Hit@1 (+369%), la prueba de Wilcoxon (p < 0.001), el 100% de fidelidad RAGAS y la ganancia de Hake g = 0.74 (t = 105.26, d > 2.0 en N = 25). Mostrar IBF de cohorte."),

        ("Minuto 35–38 | Etica, Soberania y Costo",
         "Frase clave: 'Auditabilidad criptografica y soberania sin cajas negras'.\n"
         "Enfasis: Sellos SHA-256 en cada dictamen contra fraude. Cumplimiento con LOPDP. Costo de centavos de dolar por sesion vs miles de dolares de simuladores cerrados."),

        ("Minuto 38–40 | Conclusion y Cierre",
         "Frase de cierre: 'Ateneo+ transforma la evaluacion punitiva en una trayectoria adaptativa validada para el Ecuador'.\n"
         "Enfasis: Agradecimiento a la Mgtr. Estefani Sanchez y a la facultad, y apertura protocolar a las preguntas del tribunal de CAISEB.")
    ]

    t_cue = doc.add_table(rows=len(cue_cards)+1, cols=2)
    t_cue.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_heads_cue = ["Bloque Temporal y Eje", "Estrategia Verbal, Mensaje Central y Datos Obligatorios"]
    for c_i, h_t in enumerate(c_heads_cue):
        cell = t_cue.cell(0, c_i)
        set_cell_background(cell, "0F4C81")
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h_t)
        r.font.name = "Arial"
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    for r_i, (bloque, contenido) in enumerate(cue_cards, 1):
        bg = "F8FAFC" if r_i % 2 == 0 else "FFFFFF"
        for c_i, val in enumerate([bloque, contenido]):
            cell = t_cue.cell(r_i, c_i)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=70, bottom=70, left=100, right=100)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8)
            if c_i == 0: r.font.bold = True

    # =========================================================================
    # SECCION 21: PROTOCOLO DE CONTINGENCIA Y COMPRESION TACTICA DEL TIEMPO
    # =========================================================================
    add_heading_1(doc, "21. PROTOCOLO DE CONTINGENCIA Y PLANES DE RESCATE OPERATIVO")
    
    add_body_paragraph(
        doc,
        "En congresos academicos internacionales de alta concurrencia, es comun enfrentar retrasos de mesa directiva "
        "o fallos en la conectividad del auditorio. El orador debe estar entrenado para ejecutar cualquiera de los tres planes "
        "sin perder la serenidad ni desvirtuar el impacto cientifico de la ponencia.",
        bold_prefix="Gestión de Imprevistos en Vivo: "
    )

    planes = [
        ("Plan A (Escenario Estandar - 40 Minutos):",
         "Ejecucion completa del cronograma minuto a minuto establecido en la Seccion 17. Permite desarrollar el detalle de las 42 GPCs, la demostracion visual del split-screen y las cuatro tablas de resultados empiricos."),
        
        ("Plan B (Compresion por Retraso de Mesa - 25 Minutos):",
         "Si el moderador notifica una reduccion imprevista del tiempo: 1) Reducir la justificacion nacional a 2 minutos; 2) Fusionar arquitectura y MLOps en 7 minutos enfatizando solo el fine-tuning A100 y el visor DICOM; 3) Explicar el grafo KST y BKT en 5 minutos; 4) Dedicar 8 minutos directos a los resultados de Wilcoxon (p < 0.001) y ganancia de Hake (g = 0.74); 5) Cerrar en 3 minutos. Se preserva intacto el nucleo cientifico."),

        ("Plan C (Fallo Total de Internet / Proyector en el Auditorio):",
         "La investigacion no depende de una conexion en vivo. Todo el compendio experimental, las 9 tablas formales y las 8 figuras de alta resolucion a 300 DPI se encuentran impresas y compiladas en este dossier Word oficial. El orador conduce la exposicion a viva voz apoyado en las cifras de oro de la Seccion 20, citando con precision memorizada los resultados de Wilcoxon, Hake y fidelidad RAGAS, demostrando dominio absoluto de la ciencia subyacente sin depender de soportes tecnologicos externos.")
    ]

    for p_tit, p_desc in planes:
        add_heading_2(doc, p_tit)
        add_body_paragraph(doc, p_desc, bold_prefix="Estrategia Táctica: ")

    # Guardar documento Word
    doc.save(str(DOCX_OUTPUT))
    print(f"Documento Word oficial y exhaustivo generado con éxito: {DOCX_OUTPUT} ({DOCX_OUTPUT.stat().st_size} bytes)")

if __name__ == "__main__":
    main()

