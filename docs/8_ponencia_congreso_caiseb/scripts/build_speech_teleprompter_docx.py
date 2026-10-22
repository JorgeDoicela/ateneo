# -*- coding: utf-8 -*-
"""
Generador del Guión Verbatim y Teleprompter Oficial para Ponencia Virtual (DOCX)
Congreso Académico Internacional de Innovación en Salud, Educación y Bienestar (CAISEB 2026)
Ateneo+: Simulador Clínico Multimodal con IA y RAG.

Autores:
- Tnlgo. Jorge Ismael Doicela Molina (Desarrollo, IA, DevOps)
- Mgtr. Estefani Angélica Sánchez Morales (Metodología y Validación Clínica)
"""

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
DOCX_OUTPUT = MODULE_DIR / "DISCURSO_PONENCIA_VIRTUAL_CAISEB.docx"

# Colores Institucionales
COLOR_NAVY = RGBColor(15, 76, 129)       # #0f4c81 - Navy Institucional
COLOR_BLUE = RGBColor(37, 99, 235)       # #2563eb - Azul Royal
COLOR_DARK = RGBColor(30, 41, 59)        # #1e293b - Texto Principal
COLOR_MUTED = RGBColor(100, 116, 139)    # #64748b - Gris Neutro
COLOR_GREEN = RGBColor(4, 120, 87)       # #047857 - Verde Cues
COLOR_TEAL = RGBColor(13, 148, 136)      # #0d9488 - Teal Transiciones
COLOR_RED = RGBColor(185, 28, 28)        # #b91c1c - Alertas / Pausas

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
    
    r_tag = p.add_run(f"DIAPOSITIVA {slide_num} | TIEMPO APROX: {duration}\n")
    r_tag.font.name = "Arial"
    r_tag.font.size = Pt(9.5)
    r_tag.font.bold = True
    r_tag.font.color.rgb = RGBColor(147, 197, 253) # Azul claro
    
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
    set_cell_background(cell, "F0FDF4") # Verde muy claro
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
    
    # Configurar márgenes de página (1 pulgada)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)

    # =========================================================================
    # PORTADA / TÍTULO PRINCIPAL
    # =========================================================================
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(10)
    p_title.paragraph_format.space_after = Pt(4)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t1 = p_title.add_run("GUION VERBATIM Y TELEPROMPTER OFICIAL\nPONENCIA VIRTUAL CAISEB 2026\n")
    r_t1.font.name = "Arial"
    r_t1.font.size = Pt(19)
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
        "Expositor Principal: Tnlgo. Jorge Ismael Doicela Molina (Desarrollo, IA, DevOps)\n"
        "Coautora e Investigadora: Mgtr. Estefani Angélica Sánchez Morales (Metodología y Educación Médica)\n"
        "Modalidad: Virtual Sincrónica | Duración Estimada: 35 a 40 Minutos de Exposición + Sesión de Q&A"
    )
    r_meta.font.name = "Arial"
    r_meta.font.size = Pt(10)
    r_meta.font.bold = True
    r_meta.font.color.rgb = COLOR_DARK

    doc.add_page_break()

    # =========================================================================
    # GUÍA DE USO DEL TELEPROMPTER VIRTUAL
    # =========================================================================
    add_section_header(doc, "GUÍA PRÁCTICA PARA LA LECTURA EN PANTALLA (MODO TELEPROMPTER)")
    
    add_cue_box(
        doc,
        "Coloca este documento en la mitad superior de tu pantalla principal, lo más cerca posible del lente físico de tu cámara web. "
        "Al compartir pantalla en Zoom, Teams o Google Meet, comparte únicamente la ventana de Canva o PowerPoint (NO tu pantalla completa). "
        "Así tendrás este texto frente a tus ojos sin que el público o el tribunal lo vean. "
        "Mantén una mirada constante hacia la cámara, utiliza el scroll suave del ratón y respira profundamente en los marcadores de pausa.",
        label="CONFIGURACIÓN VIRTUAL RECOMENDADA"
    )

    add_sub_header(doc, "Resumen de Cifras Clave (Memorización de Respaldo)")
    doc.add_paragraph(
        "• 42 Guías de Práctica Clínica del MSP Ecuador (7,052 fragmentos normativos extraídos con foliación física real).\n"
        "• 45.8% de alucinación clínica en modelos de IA comerciales sin anclaje normativo.\n"
        "• +369.23% de ganancia en precisión de recuperación Top-1 (Hit@1) tras fine-tuning en GPU A100.\n"
        "• +274.40% de mejora en MRR@5 (Mean Reciprocal Rank).\n"
        "• p < 0.001 (W = 365.0) en prueba de Wilcoxon sobre 283 consultas ciegas fuera de distribución (OOD).\n"
        "• 100.0% de fidelidad normativa en evaluación RAGAS (anclaje sin alucinación).\n"
        "• N = 25 médicos internos en el estudio piloto con diseño Pre vs. Post-Test.\n"
        "• g = 0.74 de ganancia de aprendizaje de Hake (catalogada como Ganancia Alta, t = 105.26, p < 0.0001, d > 2.0).\n"
        "• Salto cuantitativo: promedio de 4.87/10 a 8.64/10 (+77.4% de incremento).\n"
        "• Reducción del 88.6% en el Índice de Brecha Formativa (IBF global pasó de 0.4151 a 0.0496).\n"
        "• Ciclo Cerrado CACES: 4 áreas troncales evaluadas (balance 1:1:1:1 con 2.50 pts c/u) y planes prescriptivos heurísticos.\n"
        "• Salas Sincrónicas AteneoRoom: 4 fases pedagógicas sincronizadas mediante WebSockets con co-escritura en vivo.\n"
        "• Gamificación Médica: 5 rangos de carrera médica (Estudiante Inicial a Residente de Honor) y 8 hitos clínicos con XP.\n"
        "• Costo computacional inferior a 0.05 USD por sesión de simulación completa."
    )

    doc.add_page_break()

    # =========================================================================
    # GUIÓN COMPLETO DIAPOSITIVA POR DIAPOSITIVA
    # =========================================================================
    add_section_header(doc, "DISCURSO VERBATIM COMPLETO DIAPOSITIVA POR DIAPOSITIVA (40 MINUTOS)")

    # -------------------------------------------------------------------------
    # DIAPOSITIVA 1: BIENVENIDA CAISEB 2026
    # -------------------------------------------------------------------------
    add_slide_transition_banner(
        doc,
        slide_num="1",
        title="Carátula Oficial y Bienvenida al Congreso CAISEB 2026",
        duration="1 minuto",
        screen_action="Mostrar diapositiva institucional de bienvenida de CAISEB 2026."
    )
    
    add_cue_box(doc, "Tono formal, respetuoso y seguro. Sonríe ligeramente al iniciar el saludo institucional.", label="CÁMARA")

    add_spoken_paragraph(
        doc,
        "Muy buenos días con todos. Estimados miembros del comité organizador, honorable tribunal evaluador, colegas docentes, "
        "investigadores y profesionales de las ciencias de la salud y la tecnología: es un verdadero honor para nosotros participar en esta "
        "edición del Congreso Académico Internacional de Innovación en Salud, Educación y Bienestar (CAISEB 2026).",
        bold_lead="Saludo Protocolar:",
        pause_after=True
    )

    add_spoken_paragraph(
        doc,
        "El día de hoy venimos a compartir los resultados de una investigación interdisciplinaria que une la ingeniería de software de alto rendimiento, "
        "la inteligencia artificial aplicada y la educación médica formal en el contexto específico de la salud pública de nuestro país, el Ecuador.",
        bold_lead="Propósito de la Conferencia:"
    )

    # -------------------------------------------------------------------------
    # DIAPOSITIVA 2: VIDEO DE TRANSICIÓN / IDENTIDAD DINÁMICA
    # -------------------------------------------------------------------------
    add_slide_transition_banner(
        doc,
        slide_num="2",
        title="Video de Transición / Identidad Tecnológica Dinámica",
        duration="45 segundos",
        screen_action="Reproducir animación de video en pantalla completa (fondo dinámico) mientras introduces la visión del proyecto."
    )

    add_cue_box(doc, "Voz firme y pausada. Deja que el video corra fluidamente de fondo mientras hablas con calma.", label="VOZ")

    add_spoken_paragraph(
        doc,
        "La medicina contemporánea avanza a una velocidad vertiginosa. Sin embargo, en la práctica clínica hospitalaria, "
        "el mayor desafío sigue estando en el puente que conecta el conocimiento teórico de las aulas universitarias con la toma de decisiones "
        "críticas frente al paciente en la sala de emergencias.",
        bold_lead="Reflexión Inicial:",
        pause_after=True
    )

    add_spoken_paragraph(
        doc,
        "Para responder a esta necesidad, concebimos Ateneo+: un ecosistema inteligente de simulación clínica diseñado para transformar "
        "la forma en que los futuros médicos entrenan su razonamiento diagnóstico y terapéutico bajo estándares normativos estrictos.",
        bold_lead="Presentación del Ecosistema:"
    )

    # -------------------------------------------------------------------------
    # DIAPOSITIVA 3: PORTADA OFICIAL DEL PROYECTO
    # -------------------------------------------------------------------------
    add_slide_transition_banner(
        doc,
        slide_num="3",
        title="Portada Oficial de la Investigación y Equipo de Autores",
        duration="1 minuto 30 segundos",
        screen_action="Mostrar diapositiva con el título formal de la ponencia y los nombres de ambos investigadores."
    )

    add_spoken_paragraph(
        doc,
        "El título oficial de nuestro trabajo es: 'Simulador clínico multimodal basado en inteligencia artificial y RAG para el entrenamiento formativo "
        "y analítica del aprendizaje médico en Ecuador'.",
        bold_lead="Título Oficial de la Investigación:"
    )

    add_spoken_paragraph(
        doc,
        "Esta investigación fue desarrollada por un equipo de dos autores. Por un lado, mi coautora, la Magíster Estefani Angélica Sánchez Morales, "
        "investigadora a cargo del diseño metodológico, la validación clínica y el marco pedagógico de educación médica. "
        "Y por mi parte, Jorge Ismael Doicela Molina, Tecnólogo en Desarrollo de Software e investigador enfocado en Inteligencia Artificial, Ciberseguridad y DevOps, "
        "responsable de la arquitectura integral del sistema, el entrenamiento de los modelos de inteligencia artificial en GPU, el pipeline vectorial y el despliegue de la plataforma.",
        bold_lead="Equipo de Investigación:",
        pause_after=True
    )

    # -------------------------------------------------------------------------
    # DIAPOSITIVA 4: FICHA DE LOS INVESTIGADORES
    # -------------------------------------------------------------------------
    add_slide_transition_banner(
        doc,
        slide_num="4",
        title="Perfiles Técnicos y Académicos de los Investigadores",
        duration="1 minuto",
        screen_action="Mostrar diapositiva con las fichas de presentación, especialidades y roles en el proyecto."
    )

    add_spoken_paragraph(
        doc,
        "Como observan en pantalla, nuestro enfoque ha sido garantizar una sinergia perfecta entre el rigor clínico y la ingeniería informática. "
        "En mi rol técnico, diseñé toda la plataforma Ateneo+ desde cero: construyendo su arquitectura desacoplada, ejecutando el fine-tuning supervisado "
        "de modelos de lenguaje en aceleradores GPU, estructurando las bases de datos vectoriales y asegurando una infraestructura conteinerizada con altos estándares de ciberseguridad. "
        "La Magíster Sánchez, por su parte, calibró los escenarios médicos y coordinó las pruebas clínicas con los médicos internos de pregrado.",
        bold_lead="Sinergia Interdisciplinaria:"
    )

    # -------------------------------------------------------------------------
    # DIAPOSITIVA 5 (CONTENIDO 1): BRECHA FORMATIVA Y ERROR MÉDICO
    # -------------------------------------------------------------------------
    add_slide_transition_banner(
        doc,
        slide_num="5 (Diapositiva 1 en Canva)",
        title="1. Brecha Formativa y Error Médico en Salud",
        duration="2 minutos 30 segundos",
        screen_action="Mostrar diapositiva dividida en dos columnas: Desafío en el Internado Rotativo vs. Límites de la Simulación Tradicional."
    )

    add_cue_box(doc, "Tono sobrio y reflexivo. Enfatiza los datos de la OMS y el costo de los simuladores físicos.", label="ÉNFASIS")

    add_spoken_paragraph(
        doc,
        "Para comprender por qué creamos Ateneo+, debemos analizar con total franqueza la realidad formativa en nuestras facultades y hospitales. "
        "Según la Organización Mundial de la Salud, cada año se registran en el mundo más de dos punto seis millones de muertes prevenibles causadas por fallas "
        "en el diagnóstico y en la conducta terapéutica. Y una parte sustancial de este problema se origina en la curva inicial de aprendizaje.",
        bold_lead="El Desafío Clínico:",
        pause_after=True
    )

    add_spoken_paragraph(
        doc,
        "En el internado rotativo, los estudiantes enfrentan una intensa sobrecarga asistencial: con frecuencia encontramos entre doce y dieciocho internos "
        "por cada médico tratante de guardia. Esto provoca que la retroalimentación docente sea forzosamente tardía, fragmentada o incluso inexistente. "
        "Además, por razones éticas elementales y de seguridad del paciente, un estudiante en formación no puede practicar ensayo y error directamente sobre un ser humano en estado crítico.",
        bold_lead="Realidad Hospitalaria:"
    )

    add_spoken_paragraph(
        doc,
        "¿Y qué alternativas existen hoy en día? La simulación médica tradicional con maniquíes mecatrónicos de alta fidelidad cuesta entre cuarenta y cinco mil y ciento veinte mil dólares por unidad, "
        "haciéndola económicamente inaccesible para más del ochenta y cinco por ciento de nuestras facultades de medicina. "
        "Por otro lado, los maniquíes presentan un grave sesgo de casos: permiten escuchar un soplo cardíaco, pero no permiten que el estudiante exprese en lenguaje libre su razonamiento ante emergencias obstétricas complejas como el Código Rojo o la sepsis neonatal. "
        "Y finalmente, las evaluaciones tradicionales en papel carecen de trazabilidad analítica para medir competencias longitudinales.",
        bold_lead="Límites de la Simulación Física:",
        pause_after=True
    )

    # -------------------------------------------------------------------------
    # DIAPOSITIVA 6 (CONTENIDO 2): ¿POR QUÉ FALLAN LOS LLMS GENÉRICOS?
    # -------------------------------------------------------------------------
    add_slide_transition_banner(
        doc,
        slide_num="6 (Diapositiva 2 en Canva)",
        title="2. ¿Por qué los Modelos de Lenguaje Genéricos Fallan en Medicina?",
        duration="2 minutos 30 segundos",
        screen_action="Mostrar diapositiva comparativa: Riesgos de LLMs Comerciales vs. Solución Arquitectónica Ateneo+."
    )

    add_cue_box(doc, "Este punto es crucial ante el jurado de IA y médicos. Explica con claridad por qué un LLM genérico es peligroso.", label="ARGUMENTACIÓN TÉCNICA")

    add_spoken_paragraph(
        doc,
        "Ante esta falta de retroalimentación, en los últimos dos años miles de estudiantes de medicina han comenzado a consultar modelos comerciales generalistas "
        "como ChatGPT o Claude. Pero en el ámbito médico, utilizar estos modelos sin un control arquitectónico estricto es sumamente peligroso.",
        bold_lead="La Falsa Salida de la IA Genérica:"
    )

    add_spoken_paragraph(
        doc,
        "Los modelos comerciales presentan una tasa de alucinación clínica del cuarenta y cinco punto ocho por ciento en prescripción y dosificación cuando se usan de forma directa. "
        "Además, sufren de una absoluta desconexión territorial: fueron entrenados con literatura mayoritariamente anglosajona, por lo que prescriben fármacos o esquemas de la FDA estadounidense "
        "que ni siquiera constan en el Cuadro Nacional de Medicamentos Básicos del Ecuador. "
        "Y lo más grave: carecen de trazabilidad jurídica. No pueden justificar un dictamen citando la página, la sección y la tabla exacta de la normativa ministerial.",
        bold_lead="Peligros del Modelo Comercial:",
        pause_after=True
    )

    add_spoken_paragraph(
        doc,
        "La solución no consiste en escribir 'prompts más largos'. La solución radica en rediseñar la arquitectura: "
        "construir un sistema RAG (Generación Aumentada por Recuperación) con anclaje normativo estricto contra siete mil cincuenta y dos fragmentos de las Guías de Práctica Clínica "
        "del Ministerio de Salud Pública de Ecuador. En Ateneo+, cada dictamen evaluativo incluye la cita física verificable de la guía oficial, garantizando un cien por ciento de anclaje normativo "
        "y adaptando la prescripción a los niveles de atención de nuestra red pública de salud.",
        bold_lead="La Solución Ateneo+:"
    )

    # -------------------------------------------------------------------------
    # DIAPOSITIVA 7 (CONTENIDO 3): PIPELINE RAG HÍBRIDO Y GENERACIÓN NORMATIVA
    # -------------------------------------------------------------------------
    add_slide_transition_banner(
        doc,
        slide_num="7 (Diapositiva 3 en Canva)",
        title="3. Pipeline RAG Híbrido y Generación Normativa",
        duration="3 minutos",
        screen_action="Mostrar diapositiva de 4 columnas: Ingesta Curada, Recuperación RRF, Optimización/Resiliencia e Inferencia Multimodal."
    )

    add_cue_box(doc, "Habla con la seguridad del desarrollador que construyó el pipeline. Describe las 4 etapas con fluidez.", label="INGENIERÍA")

    add_spoken_paragraph(
        doc,
        "Permítanme explicarles cómo opera el motor tecnológico de Ateneo+ a través de cuatro etapas rigurosamente integradas.",
        bold_lead="Arquitectura del Pipeline:"
    )

    add_spoken_paragraph(
        doc,
        "En la primera etapa, ejecutamos la ingesta y curación del corpus oficial: procesamos cuarenta y dos Guías de Práctica Clínica vigentes del Ministerio de Salud Pública. "
        "Utilizamos herramientas especializadas en bajo nivel para extraer el texto preservando la foliación física real del PDF y construimos un extractor matricial que convierte "
        "las tablas complejas de dosificación farmacológica a formato estructurado Markdown, generando siete mil cincuenta y dos fragmentos normativos indivisibles.",
        bold_lead="1. Ingesta y Curación Normativa:"
    )

    add_spoken_paragraph(
        doc,
        "En la segunda etapa, implementamos un motor de recuperación híbrida. ¿Por qué híbrido? Porque combinamos dos enfoques complementarios: "
        "por una parte, una búsqueda semántica densa utilizando nuestro propio modelo 'ateneo-bge-m3-ecuador-v2', ajustado con fine-tuning supervisado en una GPU NVIDIA A100; "
        "y por otra parte, una búsqueda dispersa con el algoritmo BM25 Okapi en memoria para capturar coincidencias exactas de términos médicos, códigos CIE-10 y dosis específicas. "
        "Ambas ramas se fusionan mediante el algoritmo de Fusión de Rangos Recíprocos (RRF) con constante de suavizado k igual a sesenta, logrando el equilibrio perfecto entre comprensión semántica y exactitud literal.",
        bold_lead="2. Recuperación Híbrida RRF:",
        pause_after=True
    )

    add_spoken_paragraph(
        doc,
        "En la tercera etapa, optimizamos la resiliencia del sistema. Incorporamos una caché semántica de dos niveles que responde en apenas cero punto cero cinco milisegundos "
        "ante consultas frecuentes, y un guardián de seguridad llamado PromptSecurityGuard que neutraliza al cien por ciento cualquier intento de inyección de prompts o jailbreak clínico. "
        "Además, mediante el adaptador universal compatible con APIs estándar, la plataforma puede conectarse tanto a modelos avanzados en la nube como a modelos médicos de código abierto ejecutándose de forma local en servidores propios bajo Docker.",
        bold_lead="3. Optimización y Resiliencia:"
    )

    add_spoken_paragraph(
        doc,
        "Y en la cuarta etapa, la inferencia multimodal entrega al estudiante un debriefing socrático mediante streaming token a token vía Server-Sent Events, "
        "mostrando aciertos, omisiones y la referencia exacta de la guía en menos de dos segundos.",
        bold_lead="4. Inferencia Multimodal e Interfaz:"
    )

    # -------------------------------------------------------------------------
    # DIAPOSITIVA 8 (CONTENIDO 4): MODELADO PSICOMÉTRICO (KST Y BKT)
    # -------------------------------------------------------------------------
    add_slide_transition_banner(
        doc,
        slide_num="8 (Diapositiva 4 en Canva)",
        title="4. Modelado Psicométrico: KST, BKT y Aprendizaje Adaptativo",
        duration="3 minutos",
        screen_action="Mostrar diapositiva con la explicación del motor adaptativo y las gráficas comparativas de curvas BKT (Ruta fija vs. Ruta KST adaptativa)."
    )

    add_cue_box(doc, "Explica esto de forma clara y sencilla, sin enredarte en fórmulas complejas. Es el corazón pedagógico del sistema.", label="CLARIDAD CONCEPTUAL")

    add_spoken_paragraph(
        doc,
        "Uno de los mayores aportes de Ateneo+ es que no evalúa al estudiante con una simple nota estática del uno al diez. "
        "Un diez en un examen tradicional puede ocultar que el estudiante no sabe dosificar un fármaco en una crisis, mientras que un seis no nos dice con precisión qué competencia específica falló.",
        bold_lead="Más Allá de la Nota Numérica:"
    )

    add_spoken_paragraph(
        doc,
        "Para resolver esto, integramos dos marcos matemáticos formales de modelado cognitivo: "
        "Primero, la Teoría de Espacios del Conocimiento (Knowledge Space Theory o KST), donde estructuramos la medicina en un grafo acíclico dirigido de siete competencias clínicas secuenciales: "
        "desde la anamnesis y la semiología, pasando por el diagnóstico presuntivo, la correlación de imágenes y laboratorios, hasta el diagnóstico definitivo y el plan terapéutico normado. "
        "El sistema respeta los prerrequisitos: un estudiante no puede recibir un caso de terapéutica avanzada si antes no ha demostrado dominio en el diagnóstico diferencial.",
        bold_lead="Grafo de Competencias KST:",
        pause_after=True
    )

    add_spoken_paragraph(
        doc,
        "Segundo, incorporamos el Rastreo Bayesiano del Conocimiento (Bayesian Knowledge Tracing o BKT). "
        "En cada interacción del estudiante, el motor calcula la probabilidad latente de que domine cada competencia. "
        "Y algo muy importante: calibramos parámetros matemáticos de 'desliz' y 'adivinación' (Slip y Guess). "
        "Esto significa que si un interno que usualmente responde bien comete un error involuntario de tipeo o un lapsus por fatiga de guardia, el sistema no lo castiga a cero; "
        "reconoce la probabilidad acumulada previa y amortigua el resultado hasta confirmar si se trata de un verdadero vacío cognitivo.",
        bold_lead="Rastreo Bayesiano Continuo (BKT):"
    )

    add_spoken_paragraph(
        doc,
        "Como pueden apreciar en la gráfica de la derecha, al comparar la ruta fija tradicional frente a nuestra ruta adaptativa KST, "
        "los estudiantes que utilizan Ateneo+ alcanzan el umbral de maestría en apenas cuatro sesiones de entrenamiento, mientras que la ruta fija requirió ocho sesiones. "
        "Esto demuestra empíricamente la efectividad de prescribir casos dentro de la Zona de Desarrollo Próximo del estudiante.",
        bold_lead="Convergencia Acelerada:"
    )

    # -------------------------------------------------------------------------
    # DIAPOSITIVA 9 (CONTENIDO 5): SIMULACIÓN MULTIMODAL SPLIT-SCREEN
    # -------------------------------------------------------------------------
    add_slide_transition_banner(
        doc,
        slide_num="9 (Diapositiva 5 en Canva)",
        title="5. Simulación Multimodal Split-Screen y Dictado por Voz",
        duration="2 minutos 30 segundos",
        screen_action="Mostrar diapositiva con la captura real de la interfaz de Ateneo+ en pantalla dividida y las viñetas explicativas."
    )

    add_cue_box(doc, "Señala la captura de pantalla de la interfaz con entusiasmo. Aquí se demuestra la calidad de producto terminado.", label="DEMOSTRACIÓN VISUAL")

    add_spoken_paragraph(
        doc,
        "En esta diapositiva pueden observar la interfaz real de Ateneo+ con la que interactuaron los médicos internos durante nuestro estudio piloto. "
        "Diseñamos una experiencia dividida en pantalla partida al cincuenta por ciento, exactamente como en las estaciones de trabajo hospitalarias modernas.",
        bold_lead="La Experiencia del Usuario:"
    )

    add_spoken_paragraph(
        doc,
        "En el panel izquierdo, el estudiante visualiza en tiempo real el expediente del paciente: motivo de consulta, antecedentes, signos vitales dinámicos "
        "y estudios paraclínicos multimodales integrados, tales como radiografías de tórax digitales en neumonía o tuberculosis cavitaria, "
        "trazados de electrocardiograma de doce derivaciones calibrados a veinticinco milímetros por segundo en hipertensión arterial, "
        "paneles laboratoriales con plaquetometría y transaminasas en preeclampsia severa, o coagulogramas de urgencia en encefalopatía hipóxico-isquémica. "
        "Además, cuenta con un visor DICOM multicorte nativo con presets de Unidades Hounsfield para tomografías axiales computarizadas. "
        "En el panel derecho, dispone de su espacio de trabajo interactivo para formular su razonamiento clínico estructurado "
        "en los cuatro ejes formativos normativos del Ministerio de Salud Pública de Ecuador: Diagnóstico y Criterios de Severidad, "
        "Plan Terapéutico y Farmacología Normada, Prevención y Control de Riesgos, y Criterios de Seguimiento y Referencia.",
        bold_lead="Pantalla Dividida 50/50 y Ejes Normativos MSP:",
        pause_after=True
    )

    add_spoken_paragraph(
        doc,
        "Para eliminar la fricción del teclado y reproducir la naturalidad de la práctica médica, integramos un módulo de dictado clínico por voz nativo en el navegador, "
        "calibrado específicamente para la terminología médica y fonética ecuatoriana. El estudiante puede hablar fluidamente y el sistema transcribe su juicio clínico al instante.",
        bold_lead="Dictado por Voz Nativo:"
    )

    add_spoken_paragraph(
        doc,
        "Además, la simulación opera por fases dinámicas en tres hitos progresivos: primero la sospecha diagnóstica inicial; luego el desbloqueo de estudios complementarios "
        "con justificación médica; y finalmente la conducta terapéutica y farmacológica con dosis por kilogramo de peso. "
        "Al concluir, el evaluador RAG genera el dictamen inmediato con desglose de aciertos, omisiones y la referencia oficial de la guía ministerial.",
        bold_lead="Simulación por Hitos:"
    )

    # -------------------------------------------------------------------------
    # DIAPOSITIVA 9B: ATENEOROOM Y CARRERA FORMATIVA MÉDICA
    # -------------------------------------------------------------------------
    add_slide_transition_banner(
        doc,
        slide_num="9B (Módulo de Colaboración y Mérito)",
        title="5B. Salas Colaborativas Hospitalarias (AteneoRoom) y Gamificación Médica",
        duration="3 minutos",
        screen_action="Mostrar diapositiva con el panel de AteneoRoom en WebSockets (las 4 fases sincrónicas) y el sendero de hitos clínicos de carrera médica."
    )

    add_cue_box(doc, "Enfatiza la deliberación colegiada hospitalaria y cómo la gamificación académica motiva el mérito clínico.", label="COLABORACIÓN Y MÉRITO")

    add_spoken_paragraph(
        doc,
        "La formación médica hospitalaria no se vive en solitario; se vive en equipo: en las entregas de guardia matutinas, "
        "en las juntas de servicio y en los ateneos bibliográficos donde múltiples profesionales debaten el mejor curso de acción para un paciente crítico.",
        bold_lead="La Dimensión Colegiada de la Medicina:"
    )

    add_spoken_paragraph(
        doc,
        "Para recrear esta dinámica, desarrollamos el módulo AteneoRoom: salas sincrónicas colaborativas hospitalarias operando sobre WebSockets bidireccionales nativos. "
        "Un docente modera la sala a través de cuatro fases pedagógicas estrictas: Espera o Lobby con código institucional de acceso; "
        "Resolución Activa; Discusión y Debate de cohorte; y Consenso y Cierre analítico. "
        "En el modo individual, el sistema oculta el panel de consenso de cohorte durante la resolución para evitar el sesgo de anclaje diagnóstico. "
        "Y en el modo grupal, los internos colaboran en tiempo real en un lienzo compartido con detección de presencia activa ('Redactando...') y bloqueo optimista de párrafos. "
        "Al finalizar, el motor de inteligencia colectiva calcula el promedio de sala, el porcentaje de quórum sobre el diagnóstico CIE-10 y las brechas normativas más frecuentes.",
        bold_lead="Salas AteneoRoom con WebSockets:",
        pause_after=True
    )

    add_spoken_paragraph(
        doc,
        "Y para sostener el compromiso formativo del estudiante sin caer en ludificaciones banales, implementamos el Subsistema de Carrera Formativa Médica. "
        "Aquí no hay monedas ni vidas de videojuego infantil; hay reconocimiento al mérito clínico anclado estrictamente en las Guías de Práctica Clínica. "
        "El estudiante progresa a lo largo de cinco rangos formales: desde Estudiante Clínico Inicial, Externo de Medicina, Interno Rotativo, "
        "Médico General Novel hasta Residente Clínico de Honor, acumulando Puntos de Experiencia Clínica (XP). "
        "El sistema audita de forma transaccional ocho hitos clínicos de alto rigor: desde la resolución oportuna de un Código Rojo materno, "
        "el apego normativo de excelencia con calificación superior a nueve, hasta la maestría secuencial en fases diagnósticas, "
        "desplegados en un sendero vertical continuo tipo Journey Pathway con iconos sobrios y trazabilidad ACID en Unit of Work.",
        bold_lead="Carrera Médica y Mérito Clínico:"
    )

    # -------------------------------------------------------------------------
    # DIAPOSITIVA 10 (CONTENIDO 6): RESULTADOS TÉCNICOS Y BENCHMARKS IR
    # -------------------------------------------------------------------------
    add_slide_transition_banner(
        doc,
        slide_num="10 (Diapositiva 6 en Canva)",
        title="6. Resultados I: Benchmarks de Recuperación y Supresión de Alucinación",
        duration="3 minutos",
        screen_action="Mostrar diapositiva con las métricas de oro (+369% Hit@1, +274% MRR@5, <5% alucinación) y la tabla comparativa de estrategias."
    )

    add_cue_box(doc, "Momento clave de rigor técnico. Lee las cifras con precisión y seguridad. Destaca el salto empírico de la GPU A100.", label="RIGOR EXPERIMENTAL")

    add_spoken_paragraph(
        doc,
        "Pasemos ahora al núcleo de la validación experimental y los resultados empíricos que respaldan esta investigación.",
        bold_lead="Evidencia Técnica y Experimental:"
    )

    add_spoken_paragraph(
        doc,
        "En la tabla que tienen en pantalla comparamos tres estrategias: en primer lugar, el modelo comercial sin anclaje normativo; en segundo lugar, un RAG genérico sin fine-tuning; "
        "y en tercer lugar, la arquitectura definitiva de Ateneo+ con fine-tuning supervisado en GPU A100.",
        bold_lead="Comparativa de Estrategias:"
    )

    add_spoken_paragraph(
        doc,
        "Los resultados son concluyentes: en la métrica Hit@1, que mide la probabilidad de que el fragmento normativo exacto aparezca en la primerísima posición de búsqueda, "
        "nuestro modelo fine-tuneado alcanzó un incremento del más trescientos sesenta y nueve punto veintitrés por ciento. "
        "Pasamos de un modesto cinco punto veintidós por ciento en el modelo base a un veinticuatro punto cincuenta por ciento, cuadruplicando la precisión en primera posición. "
        "En la métrica MRR@5, que evalúa la relevancia inmediata de los resultados, obtuvimos un salto del más doscientos setenta y cuatro punto cuarenta por ciento, "
        "subiendo de cero punto cero ocho ochenta y nueve a cero punto treinta y tres veintiocho.",
        bold_lead="Salto en Recuperación de Información (IR):",
        pause_after=True
    )

    add_spoken_paragraph(
        doc,
        "Para validar que este rendimiento no fuera producto del sobreajuste, sometimos el modelo a un benchmark ciego con doscientas ochenta y tres consultas clínicas "
        "completamente fuera de distribución (Out-of-Distribution). La prueba estadística no paramétrica de Wilcoxon arrojó un estadístico W de trescientos sesenta y cinco punto cero "
        "con un p-valor menor a cero punto cero cero uno, confirmando con alta significancia estadística que la ganancia es estructural y reproducible.",
        bold_lead="Validación Ciega de Wilcoxon:"
    )

    add_spoken_paragraph(
        doc,
        "Y en cuanto a la seguridad clínica, evaluamos el anclaje mediante el framework internacional RAGAS. "
        "Ateneo+ alcanzó un Faithfulness Score de entre ochenta y cien por ciento de afirmaciones ancladas directamente en las guías, "
        "reduciendo la tasa de alucinación crítica por debajo del cinco por ciento, erradicando por completo el cuarenta y cinco punto ocho por ciento de alucinación que presentan los LLMs comerciales.",
        bold_lead="Erradicación de la Alucinación:"
    )

    # -------------------------------------------------------------------------
    # DIAPOSITIVA 11 (CONTENIDO 7): VALIDACIÓN EDUCATIVA Y GANANCIA DE HAKE
    # -------------------------------------------------------------------------
    add_slide_transition_banner(
        doc,
        slide_num="11 (Diapositiva 7 en Canva)",
        title="7. Validación Educativa: Ganancia de Aprendizaje en Internos Rotativos",
        duration="3 minutos",
        screen_action="Mostrar diapositiva con las gráficas de barras Pre vs. Post-Test individual y la distribución de Ganancia Normalizada de Hake (g=0.74, N=25)."
    )

    add_cue_box(doc, "Presenta los resultados en humanos con orgullo técnico. Demuestra que la tecnología produce aprendizaje médico real.", label="IMPACTO CLÍNICO")

    add_spoken_paragraph(
        doc,
        "La mejor arquitectura informática carece de valor si no produce una mejora medible en el aprendizaje de los estudiantes. "
        "Por ello, ejecutamos un estudio piloto experimental cuantitativo con una cohorte de veinticinco médicos internos de pregrado, "
        "utilizando un diseño pareado Pre-Test versus Post-Test sobre casos normativos del Ministerio de Salud Pública.",
        bold_lead="El Estudio Piloto con Internos Rotativos:"
    )

    add_spoken_paragraph(
        doc,
        "Un componente metodológico cardinal de Ateneo+ es que cierra el ciclo didáctico formativo (closing the clinical loop) mediante tres fases estructuradas: "
        "Primero, una Evaluación Diagnóstica Inicial (Pre-Test) estratificada exactamente en las cuatro áreas troncales del Examen de Habilitación para el Ejercicio Profesional "
        "del CACES y del Ministerio de Salud Pública: Ginecología y Obstetricia con emergencias como Preeclampsia severa y Código Rojo; "
        "Pediatría y Neonatología con sepsis neonatal y asma grave; Medicina Interna y Crónicos con cetoacidosis diabética y síndrome coronario; "
        "e Infectología y Salud Pública con neumonía comunitaria y dengue grave, bajo un balance equitativo uno a uno con dos punto cincuenta puntos por área. "
        "Segundo, ante cada debilidad u omisión detectada, un motor heurístico prescriptivo pondera la severidad psicométrica y formula un Plan de Estudio Prescriptivo dosificado "
        "en la Zona de Desarrollo Próximo, combinando lectura de secciones exactas de la GPC ministerial, simulación de casos guiados y debriefing socrático reflexivo. "
        "Y tercero, la reevaluación de salida mediante un Post-Test isomórfico generado con inteligencia artificial, que preserva la encrucijada fisiopatológica y el estándar ministerial, "
        "pero varía las constantes del paciente para neutralizar por completo el sesgo de memorización o práctica repetida (testing effect).",
        bold_lead="El Ciclo Formativo Cerrado y Troncales CACES:",
        pause_after=True
    )

    add_spoken_paragraph(
        doc,
        "Los resultados pedagógicos fueron extraordinarios: la calificación promedio de razonamiento clínico ascendió de cuatro punto ochenta y siete sobre diez en el pre-test "
        "a ocho punto sesenta y cuatro sobre diez en el post-test. Esto representa una mejora formativa del setenta y siete punto cuatro por ciento. "
        "Al calcular la Ganancia Normalizada de Aprendizaje de Hake, obtuvimos un índice g igual a cero punto setenta y cuatro. "
        "En la literatura psicométrica internacional de Richard Hake, cualquier valor superior a cero punto setenta se cataloga como 'Ganancia Alta', "
        "un umbral que casi ningún método tradicional alcanza de forma homogénea.",
        bold_lead="Ganancia Alta de Hake (g = 0.74):"
    )

    add_spoken_paragraph(
        doc,
        "La prueba estadística t de Student pareada arrojó un valor de ciento cinco punto doscientos sesenta y seis con veinticuatro grados de libertad "
        "y un p-valor menor a cero punto cero cero cero uno, con un tamaño de efecto d de Cohen superior a dos punto cero. "
        "Como observan en la distribución de barras, el cien por ciento de los internos superó el umbral aprobatorio de siete sobre diez, "
        "logrando una notable reducción en la dispersión de conocimientos.",
        bold_lead="Significancia Estadística:"
    )

    # -------------------------------------------------------------------------
    # DIAPOSITIVA 12 (CONTENIDO 8): ANALÍTICA INSTITUCIONAL E ÍNDICE IBF
    # -------------------------------------------------------------------------
    add_slide_transition_banner(
        doc,
        slide_num="12 (Diapositiva 8 en Canva)",
        title="8. Analítica Institucional: Índice de Brecha Formativa (IBF) y Sostenibilidad",
        duration="2 minutos 30 segundos",
        screen_action="Mostrar diapositiva con el gráfico de barras del IBF por eje clínico y la comparación de impacto global (0.4151 vs. 0.0496)."
    )

    add_cue_box(doc, "Muestra el valor de gestión para decanos y directores de hospital. Destaca el costo sub-0.05 USD.", label="GESTIÓN Y SOSTENIBILIDAD")

    add_spoken_paragraph(
        doc,
        "Ateneo+ no solo acompaña al estudiante en su pantalla; también brinda a las facultades de medicina y a los comités de docencia hospitalaria "
        "un panel de analítica institucional en tiempo real a través del Índice de Brecha Formativa o IBF.",
        bold_lead="Vigilancia Curricular en Tiempo Real:"
    )

    add_spoken_paragraph(
        doc,
        "El IBF es un indicador continuo entre cero y uno que cuantifica qué tan alejada se encuentra una cohorte respecto al estándar normativo de ocho sobre diez. "
        "Funciona como un semáforo curricular de alerta temprana: permite identificar con precisión quirúrgica en qué eje clínico específico se concentran los vacíos. "
        "Por ejemplo, en nuestro piloto detectamos que las mayores debilidades se concentraban en los ejes de Tratamiento y Prevención, permitiendo a los docentes planificar talleres de refuerzo focalizados antes de que los internos enfrenten guardias hospitalarias reales.",
        bold_lead="Semáforo Curricular:",
        pause_after=True
    )

    add_spoken_paragraph(
        doc,
        "La gráfica de la derecha ilustra el impacto global del motor adaptativo: el IBF general de la cohorte descendió de cero punto cuarenta y uno cincuenta y uno, "
        "que corresponde a una brecha crítica, a tan solo cero punto cero cuatrocientos noventa y seis, catalogada como leve. "
        "Esto representa una reducción de la brecha formativa del ochenta y ocho punto seis por ciento.",
        bold_lead="Reducción del 88.6% de la Brecha:"
    )

    add_spoken_paragraph(
        doc,
        "En términos de viabilidad económica y soberanía, el costo computacional de una simulación completa en Ateneo+ es inferior a cero punto cero cinco dólares por caso, "
        "frente a los más de mil doscientos dólares por hora que representa la operación en centros de simulación físicos tradicionales. "
        "Además, la plataforma está completamente conteinerizada en Docker para ser instalada de forma local en los centros de datos de cada hospital, "
        "garantizando la custodia de datos y el cumplimiento estricto de la Ley Orgánica de Protección de Datos Personales del Ecuador.",
        bold_lead="Eficiencia Económica y Soberanía:"
    )

    # -------------------------------------------------------------------------
    # DIAPOSITIVA 13 (CONTENIDO 9): CONCLUSIONES Y HOJA DE RUTA
    # -------------------------------------------------------------------------
    add_slide_transition_banner(
        doc,
        slide_num="13 (Diapositiva 9 en Canva)",
        title="9. Conclusiones y Hoja de Ruta: Aporte a la Educación Médica y Escalabilidad",
        duration="2 minutos 30 segundos",
        screen_action="Mostrar diapositiva final de balance: 4 Conclusiones Principales y 4 Líneas de Trabajo Futuro."
    )

    add_cue_box(doc, "Conclusión firme y propositiva. Cierra con convicción y abre formalmente el espacio de preguntas.", label="CIERRE MAGISTRAL")

    add_spoken_paragraph(
        doc,
        "Para concluir nuestra exposición, deseamos sintetizar los cuatro aportes científicos y sanitarios más significativos de esta investigación:",
        bold_lead="Aportes Fundamentales del Proyecto:"
    )

    add_spoken_paragraph(
        doc,
        "Primero: Demostramos que el anclaje normativo mediante RAG híbrido y fine-tuning supervisado de embeddings BGE-M3 elimina el riesgo de alucinación clínica en la IA evaluativa. "
        "Segundo: El modelado psicométrico formal basado en KST y BKT permite personalizar la trayectoria pedagógica en la Zona de Desarrollo Próximo, acelerando la curva de aprendizaje al doble de velocidad. "
        "Tercero: Democratizamos el acceso a la simulación clínica de alta fidelidad, haciéndola accesible desde cualquier navegador web a costos operativos insignificantes. "
        "Y cuarto: Fortalecemos de manera decisiva la seguridad del paciente, cerrando brechas formativas críticas en un entorno virtual seguro antes de que el médico atienda urgencias reales.",
        bold_lead="Los Cuatro Pilares Demostrados:",
        pause_after=True
    )

    add_spoken_paragraph(
        doc,
        "En nuestra hoja de ruta de escalabilidad, estamos expandiendo el catálogo a cincuenta escenarios clínicos prioritarios de atención primaria y salud rural; "
        "estamos diseñando adaptadores nosológicos para incorporar consensos internacionales complementarios sin romper la norma nacional; "
        "estamos preparando la interoperabilidad con historias clínicas electrónicas bajo el estándar HL7 FHIR; "
        "y nos encontramos iniciando la validación multicéntrica en cinco facultades de medicina del Ecuador para consolidar este proyecto como un estándar nacional.",
        bold_lead="Hoja de Ruta Futura:"
    )

    # -------------------------------------------------------------------------
    # DIAPOSITIVA 14: CIERRE Y PREGUNTAS
    # -------------------------------------------------------------------------
    add_slide_transition_banner(
        doc,
        slide_num="14",
        title="Agradecimiento y Sesión de Preguntas y Respuestas (Q&A)",
        duration="1 minuto",
        screen_action="Mostrar diapositiva final de contacto con los datos de ambos investigadores."
    )

    add_spoken_paragraph(
        doc,
        "Agradecemos profundamente al comité organizador de CAISEB 2026 por brindarnos este espacio para divulgar ciencia aplicada hecha en Ecuador, "
        "y quedamos a entera disposición del honorable tribunal evaluador para atender sus preguntas y comentarios. Muchas gracias.",
        bold_lead="Cierre Protocolar:"
    )

    doc.add_page_break()

    # =========================================================================
    # VERSIÓN DE EMERGENCIA: PLAN B (15 MINUTOS)
    # =========================================================================
    add_section_header(doc, "PLAN B: VERSIÓN DE COMPRESIÓN TÁCTICA (15 MINUTOS)")
    
    add_cue_box(
        doc,
        "Utiliza esta sección únicamente si el moderador del congreso anuncia al inicio que por retrasos de agenda el tiempo se reduce a 15 minutos. "
        "Esta versión va directo al grano, preservando el 100% de las métricas clave sin perder impacto científico.",
        label="USO EXCLUSIVO ANTE RECORTE DE TIEMPO"
    )

    add_spoken_paragraph(
        doc,
        "Muy buenos días con todos. Presentamos Ateneo+: un simulador clínico multimodal desarrollado para resolver un desafío estructural en la formación médica: "
        "la necesidad de que los médicos internos entrenen su razonamiento diagnóstico y terapéutico bajo las Guías de Práctica Clínica del Ministerio de Salud Pública de Ecuador, "
        "sin comprometer la seguridad del paciente y sin depender de costosos maniquíes físicos inaccesibles para la mayoría de universidades.",
        bold_lead="Minuto 0 al 3 | El Problema y la Solución:"
    )

    add_spoken_paragraph(
        doc,
        "El uso de modelos de inteligencia artificial comerciales genéricos presenta un cuarenta y cinco punto ocho por ciento de alucinación crítica en dosificación médica y desconoce el Cuadro Nacional de Medicamentos Básicos. "
        "Nuestra solución consistió en diseñar una arquitectura RAG supervisada: procesamos cuarenta y dos guías oficiales del MSP generando siete mil cincuenta y dos fragmentos normativos. "
        "Realizamos fine-tuning supervisado del modelo de embeddings BGE-M3 en una GPU NVIDIA A100 y fusionamos búsqueda densa y léxica con Reciprocal Rank Fusion, "
        "logrando una caché semántica de cero punto cero cinco milisegundos y un debriefing socrático por streaming con cita física verificable de página.",
        bold_lead="Minuto 3 al 7 | Arquitectura Técnica y Fine-Tuning en GPU:"
    )

    add_spoken_paragraph(
        doc,
        "A nivel psicométrico y pedagógico, Ateneo+ modela el conocimiento sobre un grafo acíclico dirigido de siete competencias clínicas (KST), "
        "cierra el ciclo didáctico mediante un Pre-Test estratificado en las cuatro áreas troncales del CACES y formula planes prescriptivos heurísticos "
        "con reevaluación por Post-Test isomórfico asistido por IA. "
        "En la interfaz split-screen, el estudiante dictamina por voz o texto sobre los cuatro ejes formativos normativos del MSP, "
        "cuenta con salas colaborativas sincrónicas AteneoRoom con WebSockets para debate colegiado y progresa a través de cinco rangos "
        "de carrera médica con ocho hitos clínicos normativos con persistencia transaccional ACID.",
        bold_lead="Minuto 7 al 10 | Motor Psicométrico, Ciclo CACES, Salas y Carrera Médica:"
    )

    add_spoken_paragraph(
        doc,
        "En los resultados técnicos, el fine-tuning en GPU cuadruplicó la precisión de recuperación Top-1 con un incremento del más trescientos sesenta y nueve por ciento en Hit@1 "
        "y más doscientos setenta y cuatro por ciento en MRR@5, con significancia estadística de Wilcoxon con p menor a cero punto cero cero uno en consultas ciegas fuera de distribución, "
        "y cien por ciento de fidelidad normativa RAGAS.",
        bold_lead="Minuto 10 al 13 | Resultados Técnicos y Experimentales:"
    )

    add_spoken_paragraph(
        doc,
        "En el estudio piloto con veinticinco médicos internos, la calificación promedio se elevó de cuatro punto ochenta y siete a ocho punto sesenta y cuatro sobre diez (+setenta y siete por ciento), "
        "alcanzando una Ganancia Normalizada de Hake de g igual a cero punto setenta y cuatro, catalogada como Ganancia Alta, con t pareada de ciento cinco punto veintiséis y p menor a cero punto cero cero cero uno. "
        "El Índice de Brecha Formativa se redujo en un ochenta y ocho punto seis por ciento, con un costo menor a cinco centavos de dólar por sesión. "
        "Ateneo+ demuestra que es posible unir la inteligencia artificial y la salud pública con soberanía y rigor científico. Muchas gracias.",
        bold_lead="Minuto 13 al 15 | Impacto Educativo y Conclusión:"
    )

    doc.add_page_break()

    # =========================================================================
    # BANCO DE RESPUESTAS A PREGUNTAS DEL TRIBUNAL (Q&A)
    # =========================================================================
    add_section_header(doc, "BANCO DE RESPUESTAS VERBATIM PARA LA DEFENSA ANTE EL TRIBUNAL (Q&A)")
    
    add_cue_box(
        doc,
        "Durante la sesión de preguntas, escucha con calma al jurado, anota la palabra clave de su duda y lee directamente la respuesta correspondiente. "
        "Todas las respuestas están redactadas en primera persona, manteniendo tu rol como desarrollador e investigador de software.",
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

    # Guardar documento
    doc.save(str(DOCX_OUTPUT))
    print(f"Documento Word de Teleprompter generado con éxito: {DOCX_OUTPUT} ({DOCX_OUTPUT.stat().st_size} bytes)")

if __name__ == "__main__":
    build_teleprompter_document()
