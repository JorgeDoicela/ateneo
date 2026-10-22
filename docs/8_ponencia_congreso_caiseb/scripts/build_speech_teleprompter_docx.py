# -*- coding: utf-8 -*-
"""
Generador del Guion Verbatim y Teleprompter Oficial para Ponencia Virtual (DOCX)
Congreso Académico Internacional de Innovación en Salud, Educación y Bienestar (CAISEB 2026)
Ateneo+: Simulador Clínico Multimodal con IA y RAG.

ROL: EXPOSITOR TÉCNICO Y ARQUITECTO DE SOFTWARE
Expositor: Tnlgo. Jorge Ismael Doicela Molina (Desarrollo, IA, MLOps, DevOps)
Coautora: Mgtr. Estefani Angélica Sánchez Morales (Metodología, Educación Médica y Validación Clínica)

NOTA DE SINCRONIZACIÓN:
Este documento está calibrado para la intervención técnica de Jorge Doicela.
La introducción, el marco médico-pedagógico, el diseño de la evaluación clínica,
los baremos del instrumento y los resultados de notas en internos son presentados
por la coautora (Mgtr. Sánchez). Este guion cubre con máxima profundidad la
ingeniería, modelos de IA, psicometría computacional, arquitectura de software,
infraestructura, benchmarks y la defensa técnica ante el tribunal.
"""

import sys
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

SCRIPT_DIR = Path(__file__).resolve().parent
MODULE_DIR = SCRIPT_DIR.parent
DOCX_OUTPUT = MODULE_DIR / "DISCURSO_PONENCIA_VIRTUAL_CAISEB.docx"

# Colores Institucionales Ateneo+ / CAISEB
COLOR_NAVY = RGBColor(15, 76, 129)       # #0f4c81 - Navy Institucional
COLOR_BLUE = RGBColor(37, 99, 235)       # #2563eb - Azul Royal Médico
COLOR_DARK = RGBColor(30, 41, 59)        # #1e293b - Pizarra Oscuro Texto
COLOR_MUTED = RGBColor(100, 116, 139)    # #64748b - Gris Neutro
COLOR_GREEN = RGBColor(4, 120, 87)       # #047857 - Verde Indicaciones Cues
COLOR_TEAL = RGBColor(13, 148, 136)      # #0d9488 - Teal Transiciones
COLOR_RED = RGBColor(185, 28, 28)        # #b91c1c - Alertas / Pausas de Respiración

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=180, right=180):
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

def add_slide_transition_banner(doc, slide_num, title, duration, screen_action):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.cell(0, 0)
    cell.width = Inches(6.8)
    set_cell_background(cell, "0F4C81")
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="36" w:space="0" w:color="2563EB"/>'
        f'<w:top w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(2)
    
    r_tag = p.add_run(f"DIAPOSITIVA {slide_num} | TIEMPO ESTIMADO: {duration}\n")
    r_tag.font.name = "Arial"
    r_tag.font.size = Pt(9.5)
    r_tag.font.bold = True
    r_tag.font.color.rgb = RGBColor(147, 197, 253)
    
    r_tit = p.add_run(f"{title}\n")
    r_tit.font.name = "Arial"
    r_tit.font.size = Pt(13)
    r_tit.font.bold = True
    r_tit.font.color.rgb = RGBColor(255, 255, 255)
    
    r_act = p.add_run(f"ACCIÓN EN PANTALLA: {screen_action}")
    r_act.font.name = "Arial"
    r_act.font.size = Pt(9.5)
    r_act.font.italic = True
    r_act.font.color.rgb = RGBColor(226, 232, 240)
    
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_after = Pt(4)

def add_cue_box(doc, text, label="INDICACIÓN DE CÁMARA Y VOZ"):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.cell(0, 0)
    cell.width = Inches(6.8)
    set_cell_background(cell, "F0FDF4")
    set_cell_margins(cell, top=100, bottom=100, left=180, right=180)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="047857"/>'
        f'<w:top w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    
    r_lbl = p.add_run(f"[{label}]: ")
    r_lbl.font.name = "Arial"
    r_lbl.font.size = Pt(9.5)
    r_lbl.font.bold = True
    r_lbl.font.color.rgb = COLOR_GREEN
    
    r_txt = p.add_run(text)
    r_txt.font.name = "Arial"
    r_txt.font.size = Pt(9.5)
    r_txt.font.italic = True
    r_txt.font.color.rgb = COLOR_DARK
    
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_after = Pt(3)

def add_spoken_paragraph(doc, text, bold_lead=None, pause_after=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(7)
    p.paragraph_format.line_spacing = 1.25
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    if bold_lead:
        r_lead = p.add_run(bold_lead + " ")
        r_lead.font.name = "Arial"
        r_lead.font.size = Pt(11.5)
        r_lead.font.bold = True
        r_lead.font.color.rgb = COLOR_NAVY
        
    r_body = p.add_run(text)
    r_body.font.name = "Arial"
    r_body.font.size = Pt(11.5)
    r_body.font.color.rgb = COLOR_DARK
    
    if pause_after:
        r_pause = p.add_run("  [PAUSA DE RESPIRACIÓN]")
        r_pause.font.name = "Arial"
        r_pause.font.size = Pt(9.5)
        r_pause.font.bold = True
        r_pause.font.color.rgb = COLOR_RED

def add_section_header(doc, text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(20)
    h.paragraph_format.space_after = Pt(6)
    h.paragraph_format.keep_with_next = True
    r = h.add_run(text)
    r.font.name = "Arial"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = COLOR_NAVY
    return h

def add_sub_header(doc, text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(12)
    h.paragraph_format.space_after = Pt(4)
    h.paragraph_format.keep_with_next = True
    r = h.add_run(text)
    r.font.name = "Arial"
    r.font.size = Pt(12.5)
    r.font.bold = True
    r.font.color.rgb = COLOR_BLUE
    return h

def build_teleprompter_document():
    doc = Document()
    
    # Configurar márgenes de página A4 / Carta para teleprompter
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)

    # =========================================================================
    # PORTADA INSTITUCIONAL DEL EXPOSITOR TÉCNICO
    # =========================================================================
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(10)
    p_title.paragraph_format.space_after = Pt(4)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t1 = p_title.add_run("GUION VERBATIM Y TELEPROMPTER OFICIAL\nDEL EXPOSITOR TÉCNICO\nCAISEB 2026\n")
    r_t1.font.name = "Arial"
    r_t1.font.size = Pt(18)
    r_t1.font.bold = True
    r_t1.font.color.rgb = COLOR_NAVY

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(12)
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t2 = p_sub.add_run("Simulador Clínico Multimodal Basado en Inteligencia Artificial y RAG para el Entrenamiento Formativo y Analítica del Aprendizaje Médico en Ecuador\n")
    r_t2.font.name = "Arial"
    r_t2.font.size = Pt(12)
    r_t2.font.italic = True
    r_t2.font.color.rgb = COLOR_MUTED

    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_after = Pt(14)
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_meta = p_meta.add_run(
        "Expositor Técnico: Tnlgo. Jorge Ismael Doicela Molina (Desarrollo de Software, IA, MLOps y DevOps)\n"
        "Coautora e Investigadora: Mgtr. Estefani Angélica Sánchez Morales (Metodología, Educación Médica y Validación Clínica)\n"
        "Modalidad: Ponencia Virtual Compartida (Bloque de Ingeniería, Modelos de IA e Infraestructura)\n"
        "Tiempo Estimado de Intervención Técnica: 12 a 15 Minutos + Ronda de Preguntas Técnicas del Tribunal (Q&A)"
    )
    r_meta.font.name = "Arial"
    r_meta.font.size = Pt(10)
    r_meta.font.bold = True
    r_meta.font.color.rgb = COLOR_DARK

    doc.add_page_break()

    # =========================================================================
    # GUÍA DE USO Y RESUMEN DE CIFRAS CLAVE PARA MEMORIZACIÓN DE RESPALDO
    # =========================================================================
    add_section_header(doc, "GUÍA DEL TELEPROMPTER Y CIFRAS CLAVE DE RESPALDO")
    
    add_cue_box(
        doc,
        "Coloca este documento en la mitad superior de la pantalla donde tengas tu cámara web, lo más cerca posible del lente físico. "
        "En la plataforma de videoconferencia (Zoom, Teams o Google Meet), comparte ÚNICAMENTE la ventana de Canva o PowerPoint de las diapositivas. "
        "Tu compañera iniciará con la introducción médica y el problema clínico. Al darte paso ('Doy la palabra al Tecnólogo Jorge Doicela...'), "
        "inicia inmediatamente la lectura fluida desde la Transición de Entrada. Utiliza el scroll suave y mantén mirada fija en la cámara.",
        label="CONFIGURACIÓN OPERATIVA EN PANTALLA DIVIDIDA"
    )

    add_sub_header(doc, "Cifras Clave Técnicas (Consulta Inmediata)")
    doc.add_paragraph(
        "• 42 Guías de Práctica Clínica del MSP Ecuador procesadas en 7,052 fragmentos normativos indivisibles.\n"
        "• Modelo Transformer de Embeddings BGE-M3 (1,024 dimensiones) con fine-tuning supervisado (MNRL) en GPU NVIDIA A100.\n"
        "• +369.23% de ganancia en precisión Top-1 (Hit@1) y +274.40% en MRR@5.\n"
        "• p < 0.001 (W = 365.0) en prueba no paramétrica de Wilcoxon sobre 283 consultas ciegas fuera de distribución (OOD).\n"
        "• 100.0% de fidelidad normativa en framework RAGAS (anclaje ministerial sin alucinación).\n"
        "• Búsqueda híbrida: BGE-M3 denso + BM25 Okapi disperso con Fusión de Rangos Recíprocos (RRF k=60).\n"
        "• Caché semántica en memoria de 0.05 ms y PromptSecurityGuard contra jailbreaks.\n"
        "• Grafo KST de 7 competencias clínicas con relaciones estrictas de prerrequisito.\n"
        "• BKT continuo con modelado bayesiano de parámetros Slip (desliz) y Guess (adivinación).\n"
        "• Split-Screen 50/50 y estructuración en los 4 ejes normativos del MSP (sustitutos de SOAP).\n"
        "• Visor DICOM volumétrico multicorte nativo en Canvas/GPU con Unidades Hounsfield (cero tokens de IA).\n"
        "• Salas sincrónicas AteneoRoom: WebSockets bidireccionales, 4 fases, motor de consenso CIE-10 y co-escritura con presencia activa.\n"
        "• Carrera formativa médica: 5 rangos formales y catálogo de 8 hitos clínicos con XP transaccional ACID (Unit of Work).\n"
        "• Generador de variantes isomórficas paralelas con IA para el Post-Test (evita sesgo de memorización).\n"
        "• Costo computacional inferior a 0.05 USD por simulación completa (frente a > $1,200/h físico).\n"
        "• Docker on-premise y cumplimiento riguroso de la Ley Orgánica de Protección de Datos Personales (LOPDP)."
    )

    doc.add_page_break()

    # =========================================================================
    # DISCURSO TÉCNICO DIAPOSITIVA POR DIAPOSITIVA
    # =========================================================================
    add_section_header(doc, "DISCURSO VERBATIM DEL EXPOSITOR TÉCNICO (JORGE DOICELA)")

    # -------------------------------------------------------------------------
    # TRANSICIÓN DE ENTRADA (TRAS LA EXPOSICIÓN DE LA COAUTORA)
    # -------------------------------------------------------------------------
    add_cue_box(
        doc,
        "Tu compañera acaba de exponer el problema clínico, la brecha de error médico y por qué fallan los LLMs genéricos en salud. "
        "Al escuchar que te cede la palabra ('Doy paso al Tecnólogo Jorge Doicela...'), toma el mando con voz enérgica, segura y profesional.",
        label="CUE DE ENTRADA — HANDOFF"
    )

    add_spoken_paragraph(
        doc,
        "Muchas gracias, Magíster Sánchez. Estimados miembros del tribunal y colegas: habiendo analizado la brecha clínica y el riesgo que "
        "implica la alucinación de los modelos genéricos en salud, permítanme explicarles cómo diseñamos la ingeniería de software y la arquitectura "
        "de inteligencia artificial de Ateneo+ para garantizar rigor científico, fidelidad normativa innegociable y respuesta en tiempo real.",
        bold_lead="Toma de la Palabra y Enfoque de Ingeniería:",
        pause_after=True
    )

    # -------------------------------------------------------------------------
    # DIAPOSITIVA 7 (CONTENIDO 3): PIPELINE RAG HÍBRIDO Y GENERACIÓN NORMATIVA
    # -------------------------------------------------------------------------
    add_slide_transition_banner(
        doc,
        slide_num="7 (Diapositiva 3 en Canva)",
        title="3. Pipeline RAG Híbrido y Generación Normativa",
        duration="3 minutos",
        screen_action="Mostrar diapositiva con el diagrama de 4 etapas: Ingesta Curada, Recuperación Híbrida RRF, Optimización/Resiliencia e Inferencia Multimodal."
    )

    add_cue_box(doc, "Habla como el arquitecto de software que construyó el pipeline. Explica con total dominio cada etapa.", label="INGENIERÍA")

    add_spoken_paragraph(
        doc,
        "El núcleo de Ateneo+ opera mediante un pipeline de Recuperación Aumentada por Generación (RAG) estructurado en cuatro etapas rigurosamente integradas.",
        bold_lead="Arquitectura del Motor RAG:"
    )

    add_spoken_paragraph(
        doc,
        "En la primera etapa, ejecutamos la ingesta y curación del corpus oficial: procesamos cuarenta y dos Guías de Práctica Clínica vigentes del Ministerio de Salud Pública de Ecuador. "
        "Utilizamos herramientas especializadas de bajo nivel para extraer el texto preservando la foliación física real del documento oficial y construimos un extractor matricial que convierte "
        "las tablas complejas de dosificación farmacológica a formato estructurado Markdown, generando siete mil cincuenta y dos fragmentos normativos indivisibles.",
        bold_lead="1. Ingesta y Curación Normativa:"
    )

    add_spoken_paragraph(
        doc,
        "En la segunda etapa, implementamos un motor de recuperación híbrida. ¿Por qué híbrido? Porque combinamos dos enfoques complementarios: "
        "por una parte, una búsqueda semántica densa utilizando nuestro propio modelo 'ateneo-bge-m3-ecuador-v2', ajustado mediante fine-tuning supervisado en una GPU NVIDIA A100 dedicada; "
        "y por otra parte, una búsqueda dispersa con el algoritmo BM25 Okapi en memoria para capturar coincidencias exactas de términos médicos, códigos CIE-10 y dosis específicas. "
        "Ambas ramas se fusionan mediante el algoritmo de Fusión de Rangos Recíprocos (RRF) con una constante de suavizado k igual a sesenta, logrando el equilibrio perfecto entre comprensión semántica y exactitud literal.",
        bold_lead="2. Recuperación Híbrida RRF:",
        pause_after=True
    )

    add_spoken_paragraph(
        doc,
        "En la tercera etapa, optimizamos la resiliencia del sistema. Incorporamos una caché semántica de dos niveles que responde en apenas cero punto cero cinco milisegundos "
        "ante consultas recurrentes, y un guardián de seguridad llamado PromptSecurityGuard que neutraliza al cien por ciento cualquier intento de inyección de prompts o jailbreak clínico. "
        "Además, mediante una pasarela desacoplada compatible con APIs estándar, la plataforma puede conectarse tanto a modelos avanzados en la nube como a modelos médicos de código abierto ejecutándose de forma local en servidores propios bajo Docker.",
        bold_lead="3. Optimización y Resiliencia:"
    )

    add_spoken_paragraph(
        doc,
        "Y en la cuarta etapa, la inferencia multimodal entrega al estudiante un debriefing socrático mediante streaming token a token vía Server-Sent Events (SSE), "
        "mostrando aciertos, omisiones y la referencia física exacta de la guía ministerial en menos de dos segundos.",
        bold_lead="4. Inferencia Multimodal y Streaming:"
    )

    # -------------------------------------------------------------------------
    # DIAPOSITIVA 8 (CONTENIDO 4): MODELADO PSICOMÉTRICO (KST Y BKT)
    # -------------------------------------------------------------------------
    add_slide_transition_banner(
        doc,
        slide_num="8 (Diapositiva 4 en Canva)",
        title="4. Modelado Psicométrico en Software: KST, BKT y Aprendizaje Adaptativo",
        duration="3 minutos",
        screen_action="Mostrar diapositiva con el grafo DAG de competencias clínicas y la gráfica comparativa de convergencia BKT (Ruta fija vs. Ruta adaptativa KST)."
    )

    add_cue_box(doc, "Enfatiza que la evaluación no es una nota estática del 1 al 10, sino un modelo cognitivo probabilístico en tiempo real.", label="MODELADO COGNITIVO")

    add_spoken_paragraph(
        doc,
        "Uno de los mayores aportes de ingeniería en Ateneo+ es que trasciende la simple asignación de una nota estática del uno al diez. "
        "Un diez en un examen tradicional puede ocultar que el estudiante no sabe dosificar un fármaco en una crisis, mientras que un seis no revela con precisión qué competencia específica falló.",
        bold_lead="Más Allá de la Nota Numérica:"
    )

    add_spoken_paragraph(
        doc,
        "Para modelar el conocimiento clínico en software, integramos dos marcos matemáticos consolidados: "
        "Primero, la Teoría de Espacios del Conocimiento (Knowledge Space Theory o KST), donde estructuramos la medicina en un grafo acíclico dirigido (DAG) de siete competencias clínicas secuenciales: "
        "desde la anamnesis y la semiología, pasando por el diagnóstico diferencial, la selección y correlación de exámenes paraclínicos, hasta el diagnóstico definitivo y el plan terapéutico normado. "
        "El motor algorítmico valida los prerrequisitos en código: el sistema jamás prescribe un caso de terapéutica avanzada si el alumno no ha demostrado maestría en el diagnóstico diferencial previo.",
        bold_lead="Grafo de Competencias KST:",
        pause_after=True
    )

    add_spoken_paragraph(
        doc,
        "Segundo, implementamos el Rastreo Bayesiano del Conocimiento continuo (Bayesian Knowledge Tracing o BKT). "
        "En cada interacción del estudiante, el motor recalcula la probabilidad latente de dominio de cada nodo del grafo. "
        "Y calibramos parámetros matemáticos de 'desliz' y 'adivinación' (Slip y Guess). "
        "Esto significa que si un interno que usualmente responde con excelencia comete un error involuntario de tipeo o un lapsus por fatiga de guardia, el sistema no reduce su dominio a cero; "
        "amortigua el descenso bayesiano hasta contrastar la siguiente evidencia.",
        bold_lead="Rastreo Bayesiano Continuo (BKT):"
    )

    add_spoken_paragraph(
        doc,
        "Como observan en la gráfica de convergencia, al comparar la ruta fija convencional frente a nuestra ruta adaptativa KST en la Zona de Desarrollo Próximo, "
        "los estudiantes alcanzan el umbral de maestría en apenas cuatro sesiones de entrenamiento, mientras que la ruta fija requirió ocho sesiones. "
        "Duplicamos la velocidad de adquisición de juicio clínico mediante prescripción adaptativa guiada por datos.",
        bold_lead="Convergencia en la ZDP:"
    )

    # -------------------------------------------------------------------------
    # DIAPOSITIVA 9 (CONTENIDO 5): SIMULACIÓN MULTIMODAL SPLIT-SCREEN
    # -------------------------------------------------------------------------
    add_slide_transition_banner(
        doc,
        slide_num="9 (Diapositiva 5 en Canva)",
        title="5. Simulación Multimodal Split-Screen y Dictado por Voz",
        duration="2 minutos 30 segundos",
        screen_action="Mostrar diapositiva con la captura real del entorno Split-Screen de Ateneo+, destacando el visor paraclínico y el lienzo estructurado."
    )

    add_cue_box(doc, "Señala la interfaz con orgullo de desarrollador. Enfatiza la calidad de producto terminado de grado hospitalario.", label="DEMOSTRACIÓN DE SOFTWARE")

    add_spoken_paragraph(
        doc,
        "En esta diapositiva pueden observar la estación de trabajo clínica de Ateneo+. "
        "Diseñamos un entorno dividido en pantalla partida al cincuenta por ciento, emulando las consolas de diagnóstico hospitalarias modernas.",
        bold_lead="Entorno de Trabajo Split-Screen:"
    )

    add_spoken_paragraph(
        doc,
        "En el panel izquierdo, el estudiante examina el expediente del paciente: constantes vitales dinámicas y estudios paraclínicos multimodales integrados, "
        "tales como radiografías digitales de tórax en neumonía o tuberculosis, trazados electrocardiográficos de doce derivaciones calibrados a veinticinco milímetros por segundo en hipertensión, "
        "paneles laboratoriales con plaquetometría y transaminasas en preeclampsia severa, y coagulogramas de urgencia. "
        "Además, desarrollamos un visor DICOM volumétrico nativo ejecutado directamente sobre Canvas y GPU del navegador, permitiendo desplazamiento continuo multicorte "
        "y calibración de Unidades Hounsfield según estándares del American College of Radiology, con cero consumo de tokens de IA por renderizado.",
        bold_lead="Panel Clínico Multimodal y Visor DICOM:",
        pause_after=True
    )

    add_spoken_paragraph(
        doc,
        "En el panel derecho, el estudiante formula su juicio clínico estructurado no en notas libres ambiguas, sino en los cuatro ejes formativos normativos del Ministerio de Salud Pública: "
        "1) Diagnóstico y Estratificación de Severidad; 2) Plan Terapéutico y Farmacología conforme al Cuadro Nacional de Medicamentos Básicos; "
        "3) Prevención y Control de Factores de Riesgo; y 4) Criterios de Seguimiento y Referencia a Tercer Nivel. "
        "E integramos el módulo ClinicalVoiceRecorder con la Web Speech API nativa calibrada a fonética ecuatoriana ('es-EC'), permitiendo dictar la nota clínica con total fluidez.",
        bold_lead="Los 4 Ejes Normativos del MSP y Dictado por Voz:"
    )

    # -------------------------------------------------------------------------
    # DIAPOSITIVA 9B: ATENEOROOM Y CARRERA FORMATIVA MÉDICA
    # -------------------------------------------------------------------------
    add_slide_transition_banner(
        doc,
        slide_num="9B (Módulo de Colaboración y Mérito)",
        title="5B. Salas Colaborativas Hospitalarias (AteneoRoom) y Gamificación Médica",
        duration="2 minutos 30 segundos",
        screen_action="Mostrar diapositiva con el panel de AteneoRoom en WebSockets (4 fases sincrónicas) y el sendero de hitos clínicos con XP."
    )

    add_cue_box(doc, "Destaca la ingeniería detrás de la colaboración multiusuario en tiempo real y el mérito formativo.", label="CONCURRENCIA Y MÉRITO")

    add_spoken_paragraph(
        doc,
        "Para simular las reuniones de entrega de guardia y juntas hospitalarias, desarrollamos el subsistema AteneoRoom: salas sincrónicas colaborativas multiusuario "
        "construidas sobre WebSockets bidireccionales nativos en FastAPI y React 18.",
        bold_lead="Salas Sincrónicas AteneoRoom con WebSockets:"
    )

    add_spoken_paragraph(
        doc,
        "AteneoRoom opera bajo un protocolo estricto de cuatro fases sincrónicas gobernadas por el docente: Espera o Lobby con código de acceso institucional, "
        "Resolución Activa, Discusión y Debate de cohorte, y Consenso Analítico de Cierre. "
        "En la modalidad individual, el sistema segrega la analítica y oculta las respuestas de los compañeros durante la resolución para neutralizar el sesgo de anclaje diagnóstico. "
        "En la modalidad grupal, habilita un lienzo de co-escritura en tiempo real con bloqueo optimista de párrafos y detección de presencia activa ('Redactando...'). "
        "El motor calcula al instante el promedio de sala, el porcentaje de quórum sobre el diagnóstico CIE-10 y las brechas normativas frente a las GPC.",
        bold_lead="Dinámica de 4 Fases y Motor de Consenso:",
        pause_after=True
    )

    add_spoken_paragraph(
        doc,
        "Y para impulsar la adherencia del estudiante sin caer en mecánicas arcade o juegos infantiles, implementamos el Subsistema de Carrera Formativa Médica. "
        "El estudiante progresa a lo largo de una escala canónica de cinco rangos: desde Estudiante Clínico Inicial, Externo de Medicina, Interno Rotativo, "
        "Médico General Novel hasta Residente Clínico de Honor, acumulando Puntos de Experiencia Clínica (XP). "
        "El motor audita de forma transaccional ocho hitos clínicos normativos con persistencia ACID en SqlAlchemyUnitOfWork: desde el manejo acertado de un Código Rojo obstétrico "
        "hasta el apego normativo de excelencia superior a nueve sobre diez, desplegados en un sendero vertical sobrio tipo Journey Pathway.",
        bold_lead="Carrera Médica y Persistencia Transaccional ACID:"
    )

    # -------------------------------------------------------------------------
    # DIAPOSITIVA 10 (CONTENIDO 6): RESULTADOS TÉCNICOS Y BENCHMARKS IR
    # -------------------------------------------------------------------------
    add_slide_transition_banner(
        doc,
        slide_num="10 (Diapositiva 6 en Canva)",
        title="6. Resultados Técnicos: Benchmarks de Recuperación en GPU A100 y Supresión de Alucinación",
        duration="3 minutos",
        screen_action="Mostrar diapositiva con las tablas de métricas IR (+369% Hit@1, +274% MRR@5), la prueba de Wilcoxon y la fidelidad RAGAS."
    )

    add_cue_box(doc, "Momento cumbre de rigor científico. Lee las cifras con seguridad absoluta. Demuestra el impacto del fine-tuning.", label="EVIDENCIA TÉCNICA")

    add_spoken_paragraph(
        doc,
        "Pasemos ahora a la evidencia cuantitativa y a los benchmarks experimentales que validan la superioridad de esta arquitectura.",
        bold_lead="Validación Experimental de Inteligencia Artificial:"
    )

    add_spoken_paragraph(
        doc,
        "En la tabla comparativa contrastamos tres escenarios: el modelo comercial sin anclaje normativo, un RAG genérico sin fine-tuning, "
        "y nuestra arquitectura Ateneo+ re-entrenada con fine-tuning supervisado sobre GPU NVIDIA A100.",
        bold_lead="Comparativa de Rendimiento IR:"
    )

    add_spoken_paragraph(
        doc,
        "Los resultados de recuperación de información son contundentes: en la métrica Hit@1, que mide si el fragmento ministerial exacto aparece en la primerísima posición de búsqueda, "
        "obtuvimos un incremento del más trescientos sesenta y nueve punto veintitrés por ciento. "
        "Pasamos de un modesto cinco punto veintidós por ciento en el modelo base a un veinticuatro punto cincuenta por ciento, cuadruplicando la precisión en primera posición. "
        "Y en la métrica MRR@5, que mide la posición promedio de la evidencia clínica correcta, registramos un salto del más doscientos setenta y cuatro punto cuarenta por ciento, "
        "elevándose de cero punto cero ocho ochenta y nueve a cero punto treinta y tres veintiocho.",
        bold_lead="Salto Cuantitativo en Recuperación (IR):",
        pause_after=True
    )

    add_spoken_paragraph(
        doc,
        "Para certificar que este desempeño generalice en la práctica y no sea producto de sobreajuste o fuga de datos, sometimos el modelo a un benchmark ciego con doscientas ochenta y tres consultas "
        "fuera de distribución (Out-of-Distribution) sobre guías clínicas jamás observadas durante el entrenamiento. "
        "La prueba estadística no paramétrica de Wilcoxon arrojó un estadístico W de trescientos sesenta y cinco punto cero con un p-valor menor a cero punto cero cero uno, "
        "confirmando con máxima significancia estadística que la mejora es estructural, robusta e irrefutable.",
        bold_lead="Generalización Ciega de Wilcoxon:"
    )

    add_spoken_paragraph(
        doc,
        "Finalmente, auditamos la seguridad clínica mediante el estándar internacional RAGAS. "
        "Ateneo+ alcanzó un Faithfulness Score de fidelidad normativa del cien por ciento en las pruebas formales con una tasa de alucinación crítica inferior al cinco por ciento, "
        "suprimiendo de raíz el cuarenta y cinco punto ocho por ciento de alucinaciones y omisiones farmacológicas que presentan los modelos comerciales.",
        bold_lead="Supresión de Alucinaciones con RAGAS:"
    )

    # -------------------------------------------------------------------------
    # DIAPOSITIVA 12 (CONTENIDO 8): INFRAESTRUCTURA Y SOBERANÍA TECNOLÓGICA
    # -------------------------------------------------------------------------
    add_slide_transition_banner(
        doc,
        slide_num="12 (Diapositiva 8 en Canva)",
        title="8. Infraestructura, Soberanía Tecnológica y Cumplimiento LOPDP",
        duration="1 minuto 30 segundos",
        screen_action="Mostrar diapositiva destacando la arquitectura on-premise en Docker, la eficiencia de costos sub-0.05 USD y la custodia de datos según la LOPDP."
    )

    add_cue_box(doc, "Resalta el costo accesible para facultades públicas y el cumplimiento de la ley de datos ecuatoriana.", label="SOBERANÍA Y EFICIENCIA")

    add_spoken_paragraph(
        doc,
        "En términos de viabilidad económica y soberanía tecnológica, el costo computacional de una sesión clínica completa en Ateneo+ es inferior a cero punto cero cinco dólares, "
        "frente a los más de mil doscientos dólares por hora que demanda la operación de centros de simulación mecatrónicos tradicionales. "
        "Además, la plataforma está 100% contenerizada en Docker Compose para ser desplegada en centros de datos locales o servidores universitarios propios, "
        "garantizando la soberanía de la información y el cumplimiento estricto de la Ley Orgánica de Protección de Datos Personales del Ecuador.",
        bold_lead="Eficiencia Económica y Cumplimiento LOPDP:",
        pause_after=True
    )

    # -------------------------------------------------------------------------
    # DIAPOSITIVA 13 (CONTENIDO 9): HOJA DE RUTA TECNOLÓGICA Y CIERRE TÉCNICO
    # -------------------------------------------------------------------------
    add_slide_transition_banner(
        doc,
        slide_num="13 (Diapositiva 9 en Canva)",
        title="9. Hoja de Ruta Tecnológica y Cierre del Bloque de Ingeniería",
        duration="1 minuto 30 segundos",
        screen_action="Mostrar diapositiva con las 4 líneas de evolución técnica (50 escenarios, Nosology Adapters, HL7 FHIR y validación multicéntrica)."
    )

    add_cue_box(doc, "Cierre sólido de tu intervención técnica. Cede formalmente la palabra a tu coautora para los resultados pedagógicos.", label="CIERRE TÉCNICO")

    add_spoken_paragraph(
        doc,
        "En nuestra hoja de ruta técnica inmediata, estamos expandiendo la base a cincuenta escenarios normativos de atención primaria y medicina rural; "
        "estamos implementando 'Nosology Adapters' para admitir consensos internacionales complementarios sin fracturar la norma nacional; "
        "estamos desarrollando la capa de interoperabilidad con historias clínicas electrónicas bajo el estándar HL7 FHIR; "
        "y nos encontramos listos para iniciar la validación multicéntrica en cinco facultades de medicina del país.",
        bold_lead="Hoja de Ruta de Ingeniería e Interoperabilidad:",
        pause_after=True
    )

    add_spoken_paragraph(
        doc,
        "Con esto concluyo la exposición de la arquitectura técnica y los modelos de inteligencia artificial. "
        "Cedo nuevamente la palabra a mi coautora, la Magíster Estefani Sánchez, para la presentación de la metodología de evaluación, "
        "el instrumento clínico, los resultados en los médicos internos y las conclusiones finales del estudio.",
        bold_lead="Transición de Salida (Retorno a la Coautora):"
    )

    doc.add_page_break()


    # =========================================================================
    # PLAN B TÉCNICO: COMPRESIÓN TÁCTICA (6 A 8 MINUTOS)
    # =========================================================================
    add_section_header(doc, "PLAN B TÉCNICO: COMPRESIÓN TÁCTICA (6 A 8 MINUTOS)")
    
    add_cue_box(
        doc,
        "Utiliza esta sección condensada únicamente si el moderador anuncia recorte de tiempo para la exposición general. "
        "Resume la ingeniería y los benchmarks con máxima potencia en menos de 8 minutos.",
        label="USO ANTE RECORTE SEVERO DE TIEMPO"
    )

    add_spoken_paragraph(
        doc,
        "Muchas gracias. En el componente de ingeniería de software e inteligencia artificial de Ateneo+, resolvimos el problema de la alucinación médica comercial "
        "mediante una arquitectura RAG supervisada: curamos cuarenta y dos Guías de Práctica Clínica del Ministerio de Salud Pública generando siete mil cincuenta y dos fragmentos normativos indivisibles. "
        "Realizamos fine-tuning supervisado del modelo Transformer BGE-M3 en una GPU NVIDIA A100 dedicada y fusionamos búsqueda semántica densa y dispersa con Reciprocal Rank Fusion (k=60), "
        "respaldado por una caché de cero punto cero cinco milisegundos y un guardián de seguridad contra jailbreaks.",
        bold_lead="Bloque 1 | Arquitectura RAG Híbrida y Fine-Tuning en GPU A100:"
    )

    add_spoken_paragraph(
        doc,
        "En la dimensión psicométrica y de software, modelamos el razonamiento clínico sobre un grafo acíclico dirigido de siete competencias (KST) "
        "con actualización bayesiana continua (BKT), duplicando la velocidad de maestría en la Zona de Desarrollo Próximo. "
        "En la interfaz split-screen, el interno dictamina sobre los cuatro ejes normativos del MSP mediante voz o texto, interactúa con paraclínicos 2D y tomografías en visor DICOM Canvas GPU, "
        "debate en tiempo real en salas colaborativas AteneoRoom con WebSockets y progresa a través de cinco rangos de carrera médica con ocho hitos clínicos con persistencia transaccional ACID.",
        bold_lead="Bloque 2 | Modelado Cognitivo KST/BKT, Salas Sincrónicas y Carrera Médica:"
    )

    add_spoken_paragraph(
        doc,
        "Los benchmarks técnicos validan esta arquitectura de forma irrefutable: en la GPU A100 cuadruplicamos la precisión Top-1 con un salto del más trescientos sesenta y nueve por ciento en Hit@1 "
        "y más doscientos setenta y cuatro por ciento en MRR@5. La prueba no paramétrica de Wilcoxon sobre doscientas ochenta y tres consultas ciegas fuera de distribución "
        "arrojó significancia estadística con p menor a cero punto cero cero uno (W=365.0), alcanzando cien por ciento de fidelidad normativa en RAGAS. "
        "Todo esto con un costo menor a cinco centavos de dólar por sesión y despliegue on-premise bajo Docker para cumplimiento de la LOPDP. Muchas gracias.",
        bold_lead="Bloque 3 | Benchmarks IR, Wilcoxon, Eficiencia y Cierre:"
    )

    doc.add_page_break()

    # =========================================================================
    # BANCO DE DEFENSA TÉCNICA ANTE EL TRIBUNAL (Q&A COMPLETO - 16 PREGUNTAS)
    # =========================================================================
    add_section_header(doc, "BANCO DE RESPUESTAS TÉCNICAS VERBATIM ANTE EL TRIBUNAL (Q&A)")
    
    add_cue_box(
        doc,
        "Durante la sesión de preguntas, escucha atentamente al jurado. Identifica la temática técnica o metodológica de la duda "
        "y lee con serenidad la respuesta correspondiente. Todas están redactadas en primera persona desde tu autoridad como desarrollador.",
        label="DEFENSA ORAL ANTE EL JURADO"
    )

    qa_list = [
        ("Pregunta 1: ¿Por qué eligieron BGE-M3 para fine-tuning en lugar de embeddings de OpenAI o Google?",
         "Esa es una decisión clave de arquitectura. Los modelos comerciales de embeddings como los de OpenAI son cajas negras cerradas: cobran por cada petición en la nube, no permiten reentrenar sus capas profundas y sufren de desfases terminológicos frente al vocabulario epidemiológico ecuatoriano. BGE-M3, en cambio, es un modelo multilingüe de código abierto de mil veinticuatro dimensiones que admite representaciones densas y dispersas. Esto nos permitió someterlo a fine-tuning supervisado con la función MultipleNegativesRankingLoss directamente sobre nuestra GPU dedicada NVIDIA A100, logrando un espacio vectorial a la medida de la normativa sanitaria nacional y garantizando soberanía de datos on-premise."),

        ("Pregunta 2: Una muestra de 25 médicos internos en el piloto es pequeña. ¿Cómo garantizan validez estadística?",
         "Es una observación muy pertinente. El estudio piloto se diseñó bajo un esquema intra-sujeto pre-test y post-test pareado, lo que neutraliza la varianza inter-individual entre los participantes. La significancia estadística alcanzada con la prueba t pareada de Student arrojó un valor de ciento cinco punto doscientos sesenta y seis con veinticuatro grados de libertad y un p-valor menor a diez a la menos diez, con un tamaño de efecto d de Cohen mayor a dos punto cero, superando ampliamente los umbrales de rigor científico en educación médica. Además, la Ganancia de Hake de cero punto setenta y cuatro valida una ganancia alta. Actualmente estamos expandiendo el protocolo a más de trescientos estudiantes en cinco facultades de medicina para la validación multicéntrica."),

        ("Pregunta 3: ¿Cómo evita el sistema que un estudiante engañe a la IA usando 'prompt hacking' o términos incoherentes?",
         "Ateneo+ implementa una defensa en profundidad de tres barreras técnicas: Primero, el módulo PromptSecurityGuard realiza un escaneo léxico y sintáctico en tiempo real en la entrada para neutralizar intentos de fuga de rol o inyección de instrucciones. Segundo, el evaluador incorpora el framework RAGAS de fidelidad estricta, penalizando cualquier afirmación que no cuente con respaldo explícito en el fragmento recuperado de la GPC. Y tercero, la evaluación se desglosa ontológicamente en cuatro ejes clínicos independientes (diagnóstico, tratamiento, prevención y seguimiento); un texto incoherente no puede satisfacer simultáneamente los umbrales de los cuatro ejes."),

        ("Pregunta 4: ¿Qué ocurre si el Ministerio de Salud Pública actualiza o deroga una Guía de Práctica Clínica?",
         "La arquitectura del sistema desacopló por completo el código de la aplicación respecto a la base de conocimiento normativo. Si el Ministerio emite una nueva guía, nuestro pipeline de ingesta automatizado procesa el nuevo PDF, extrae las tablas y actualiza la colección vectorial en ChromaDB en menos de diez minutos, sin necesidad de modificar el frontend ni reiniciar el backend. Además, cada actualización se sella criptográficamente con un hash SHA-256 para preservar la trazabilidad histórica de versiones."),

        ("Pregunta 5: En zonas rurales o centros de salud de la Amazonía sin acceso a internet, ¿cómo funciona Ateneo+?",
         "Diseñamos el sistema pensando en la realidad de la ruralidad médica. El recuperador BGE-M3 se cuantiza a formato ONNX de ocho bits ocupando apenas quinientos ochenta megabytes de memoria con una latencia de dieciocho milisegundos en cualquier computadora estándar. Por su parte, el evaluador puede ejecutarse localmente con modelos clínicos abiertos cuantizados a cuatro bits mediante Ollama o vLLM sin internet. La aplicación frontend es una Progressive Web App (PWA) que almacena los casos y resoluciones en IndexedDB y los sincroniza de forma transparente en cuanto se recupera conectividad hospitalaria."),

        ("Pregunta 6: ¿Por qué no hicieron Fine-Tuning directo en el modelo generativo (LLM) en lugar de ajustar el recuperador?",
         "Hacer fine-tuning directo en los pesos generativos de un LLM en medicina presenta tres riesgos críticos: Primero, el olvido catastrófico (catastrophic forgetting), donde el modelo pierde facultades de razonamiento general al forzarle la memorización de datos específicos. Segundo, la persistencia de alucinación latente, ya que los pesos neuronales son probabilísticos y no ofrecen garantía de citación de página exacta. Y tercero, el costo prohibitivo de reentrenar un LLM ante cada cambio normativo. En contraste, ajustar el modelo recuperador vectorial (BGE-M3) garantiza que el conocimiento factual resida siempre en la base indexada de forma auditable, permitiendo al LLM actuar exclusivamente como un evaluador socrático con anclaje normativo innegociable."),

        ("Pregunta 7: ¿Cómo asegura el sistema el cumplimiento de la Ley Orgánica de Protección de Datos Personales (LOPDP)?",
         "Ateneo+ cumple con la LOPDP mediante el principio de Privacidad desde el Diseño: Primero, todos los casos clínicos son cien por ciento sintéticos y canónicos, generados a partir de los perfiles epidemiológicos de las guías sin usar historias clínicas reales de pacientes. Segundo, las identidades de los estudiantes viajan seudonimizadas con identificadores opacos en los registros de telemetría. Y tercero, la arquitectura soporta despliegue on-premise en los propios servidores del hospital o facultad, evitando transferencias internacionales de datos."),

        ("Pregunta 8: ¿Qué pasa si una guía ecuatoriana discrepa de consensos internacionales como la AHA o la Sociedad Europea de Cardiología?",
         "En el marco legal ecuatoriano, el médico interno y el profesional en funciones dentro de la Red Pública Integral de Salud está obligado deontológica y jurídicamente a cumplir las directrices vinculantes del Ministerio de Salud Pública. Por ello, Ateneo+ evalúa prioritariamente el estándar nacional. No obstante, el sistema incorpora 'Nosology Adapters' que permiten a la cátedra docente habilitar notas complementarias de guías internacionales sin perder la trazabilidad de la conducta legal exigida en el país."),

        ("Pregunta 9: En el rastreo bayesiano (BKT), ¿cómo se evita castigar injustamente a un interno por un lapsus o error de tipeo?",
         "Precisamente esa es la ventaja de utilizar Bayesian Knowledge Tracing frente a una regla estática. El modelo BKT incorpora el parámetro de desliz o 'Slip', que calibramos entre cero punto cero ocho y cero punto doce. Si un estudiante que ha demostrado alta maestría previa comete un fallo aislado, la actualización bayesiana no reduce su dominio a cero; amortigua el descenso a un rango intermedio. Si en la siguiente interacción responde correctamente, la evidencia confirma su maestría y restaura su curva de dominio."),

        ("Pregunta 10: ¿Cuál es la ventaja de Ateneo+ frente a simuladores comerciales como SimMan o Body Interact?",
         "Ateneo+ supera a los simuladores comerciales extranjeros en tres aspectos decisivos: Primero, el factor económico: los simuladores físicos cuestan decenas de miles de dólares en adquisición y licencias anuales, mientras que Ateneo+ opera a menos de cinco centavos de dólar por sesión en cualquier navegador. Segundo, la pertinencia territorial: los simuladores extranjeros evalúan algoritmos anglosajones desconectados de nuestra realidad hospitalaria. Y tercero, la evaluación del lenguaje libre: no limitamos al estudiante a elegir opciones prefijadas, sino que evaluamos su argumentación clínica real en texto y voz."),

        ("Pregunta 11: Si una institución prohíbe el uso de nubes externas por política de ciberseguridad, ¿cómo se implementa el sistema?",
         "La pasarela de inteligencia artificial de Ateneo+ implementa el patrón de arquitectura Adapter desacoplado. Basta con cambiar una sola variable de entorno para que el sistema deje de apuntar a APIs externas y se conecte a un servidor local ejecutando modelos abiertos como LLaMA-3.1, BioMistral o DeepSeek sobre vLLM u Ollama. De esta manera, el cien por ciento del procesamiento, los datos y las evaluaciones se quedan dentro de la red privada de la institución."),

        ("Pregunta 12: ¿Cómo garantizan que el Post-Test mida aprendizaje clínico real y no la memorización del Pre-Test?",
         "Para neutralizar el efecto de práctica repetida (testing effect), Ateneo+ utiliza su generador de casos isomórficos. El sistema no repite las viñetas clínicas basales; genera problemas funcionalmente equivalentes que evalúan exactamente las mismas competencias y la misma guía del MSP, pero variando la edad del paciente, la presentación de los paraclínicos y el contexto clínico. De esta manera, la Ganancia Normalizada de Hake refleja una auténtica transferencia de razonamiento clínico y no la memoria episódica del estudiante."),

        ("Pregunta 13: ¿Cómo opera el módulo de Salas Colaborativas Hospitalarias (AteneoRoom) y cómo previene el sesgo de anclaje diagnóstico?",
         "AteneoRoom simula las sesiones hospitalarias de ateneo clínico mediante WebSockets bidireccionales nativos estructurados en cuatro fases pedagógicas secuenciales: Espera o Lobby, Resolución Activa, Discusión y Debate de cohorte, y Consenso Analítico. Para evitar el sesgo de anclaje diagnóstico (anchoring bias), el sistema segrega la analítica de cohorte: durante la fase de resolución individual, el promedio de sala y las respuestas de los compañeros permanecen estrictamente ocultos para los estudiantes, revelándose únicamente cuando el docente moderador transiciona la sala a la fase de debate. En la modalidad grupal, integra un lienzo de co-escritura sincrónica con detección de presencia activa ('Redactando...') y bloqueo optimista de párrafos, calculando en tiempo real el porcentaje de quórum sobre el diagnóstico CIE-10 y las brechas normativas frente a las GPC del MSP."),

        ("Pregunta 14: ¿Cómo se estructura la evaluación diagnóstica de entrada (Pre-Test) y su correspondencia con el examen nacional del CACES?",
         "Para erradicar la subrepresentación de constructo (construct underrepresentation), el Pre-Test de Ateneo+ implementa un muestreo estratificado balanceado de un reactivo por cada una de las cuatro áreas troncales del Examen de Habilitación para el Ejercicio Profesional (EHEP) del CACES y las GPC del MSP: Ginecología y Obstetricia (Preeclampsia severa / Código Rojo), Pediatría y Neonatología (Sepsis neonatal temprana / Asma grave), Medicina Interna y Crónicos (Cetoacidosis diabética / Síndrome coronario) e Infectología y Salud Pública (Neumonía bacteriana grave / Dengue con signos de alarma). Cada área tiene una ponderación equitativa de dos punto cincuenta puntos sobre diez. Las omisiones detectadas alimentan un motor heurístico que pondera el riesgo psicométrico W_i = Severidad * (1.05 - P(L)) y prescribe tareas en tres ejes: lectura de la GPC, simulación en ZDP y debriefing socrático reflexivo."),

        ("Pregunta 15: ¿Por qué decidieron sustituir la metodología SOAP tradicional por los cuatro ejes normativos del MSP?",
         "La metodología SOAP tradicional (Subjetivo, Objetivo, Análisis, Plan) fue concebida para la redacción de notas de evolución en historias clínicas de soporte físico, pero no responde a la estructura analítica ni a los estándares de evaluación de competencias del Ministerio de Salud Pública de Ecuador ni del CACES. Las auditorías del internado rotativo y los baremos de evaluación formativa evalúan cuatro dimensiones clínicas específicas: 1) Diagnóstico sindrómico y estratificación de severidad; 2) Manejo terapéutico y dosificación farmacológica conforme al Cuadro Nacional de Medicamentos Básicos; 3) Prevención y control de factores de riesgo; y 4) Criterios de seguimiento, signos de alarma y referencia oportuna a la red hospitalaria. Al estructurar la argumentación del estudiante en estos cuatro ejes normativos, eliminamos contradicciones pedagógicas y alineamos el entrenamiento directamente con las competencias profesionales exigidas por la ley ecuatoriana."),

        ("Pregunta 16: ¿Cómo garantiza el subsistema de gamificación el mérito formativo médico sin trivializar el aprendizaje?",
         "En educación médica de alta fidelidad, la ludificación arcade (vidas, monedas virtuales o stickers) resulta contraproducente y trivializa situaciones clínicas críticas donde se debaten vidas humanas. Ateneo+ erradica esa superficialidad mediante una Carrera Formativa Médica basada estrictamente en mérito académico y Puntos de Experiencia Clínica (XP). La progresión abarca cinco rangos formales congruentes con la carrera médica: Estudiante Clínico Inicial, Externo de Medicina, Interno Rotativo, Médico General Novel y Residente Clínico de Honor. Los XP se obtienen exclusivamente mediante ocho hitos normativos auditados transaccionalmente con SqlAlchemyUnitOfWork (ej. manejo acertado de un Código Rojo materno, apego estricto a la GPC superior a 9.0 o superación de las tres fases secuenciales), desplegados en un sendero vertical sobrio tipo Journey Pathway con iconos médicos limpios y trazabilidad ACID.")
    ]

    for q_tit, q_resp in qa_list:
        add_sub_header(doc, q_tit)
        add_spoken_paragraph(doc, q_resp, bold_lead="Respuesta para el Expositor:")

    # Guardar documento Word
    doc.save(str(DOCX_OUTPUT))
    print(f"Documento Word de Teleprompter generado con éxito: {DOCX_OUTPUT} ({DOCX_OUTPUT.stat().st_size} bytes)")

if __name__ == "__main__":
    build_teleprompter_document()
