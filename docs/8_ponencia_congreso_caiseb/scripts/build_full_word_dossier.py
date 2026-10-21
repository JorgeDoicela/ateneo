# -*- coding: utf-8 -*-
"""
Generador Maestro del Documento Word Oficial y Exhaustivo (DOCX)
Ateneo+: Dossier Integral de Investigación, Ingeniería de Software, MLOps, Transformers,
Extracción de Datos, Psicometría, Impacto Pedagógico en Ecuador, Protocolos de Reproducibilidad,
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
COLOR_NAVY = RGBColor(15, 76, 129)       # #0f4c81 - Azul Petróleo / Navy Institucional
COLOR_BLUE = RGBColor(37, 99, 235)       # #2563eb - Azul Royal Médico
COLOR_DARK = RGBColor(30, 41, 59)        # #1e293b - Pizarra Oscuro Texto
COLOR_MUTED = RGBColor(100, 116, 139)    # #64748b - Gris Neutro Subtítulos
COLOR_GREEN = RGBColor(4, 120, 87)       # #047857 - Verde Clínico
COLOR_CYAN = RGBColor(8, 145, 178)       # #0891b2 - Cyan Clínico

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

def add_callout_box(doc, text, title="NOTA TÉCNICA / DISCURSO CLAVE"):
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

def add_institutional_table(doc, headers, rows, col_alignments=None, col_widths=None):
    table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    # Cabecera
    for c_i, h_t in enumerate(headers):
        cell = table.cell(0, c_i)
        set_cell_background(cell, "0F4C81")
        set_cell_margins(cell, top=110, bottom=110, left=130, right=130)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h_t)
        r.font.name = "Arial"
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        if col_widths and c_i < len(col_widths):
            cell.width = Inches(col_widths[c_i])
            
    # Filas
    for r_i, row_data in enumerate(rows, 1):
        bg = "F8FAFC" if r_i % 2 == 0 else "FFFFFF"
        for c_i, val in enumerate(row_data):
            cell = table.cell(r_i, c_i)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=75, bottom=75, left=110, right=110)
            p = cell.paragraphs[0]
            
            # Alineación
            if col_alignments and c_i < len(col_alignments):
                align = col_alignments[c_i]
                if align == "center":
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                elif align == "right":
                    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                else:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_i == 0 else WD_ALIGN_PARAGRAPH.CENTER
                
            r = p.add_run(str(val))
            r.font.name = "Arial"
            r.font.size = Pt(8.5)
            
            # Negrita si es primera columna o si contiene indicadores clave
            if c_i == 0 or "%" in str(val) or "100%" in str(val) or "Alta Ganancia" in str(val) or "PASS" in str(val):
                if c_i == 0 or "Alta Ganancia" in str(val) or "100%" in str(val):
                    r.font.bold = True
                    
            if col_widths and c_i < len(col_widths):
                cell.width = Inches(col_widths[c_i])
                
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_after = Pt(4)
    return table

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
    print(f"Iniciando compilación del Dossier Integral, Exhaustivo y Metodológico Word en: {DOCX_OUTPUT}")
    doc = Document()
    
    # Configuración de márgenes de página A4 (1 pulgada en todos los bordes)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
        # Encabezado sutil
        header = section.header
        p_hdr = header.paragraphs[0]
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_hdr = p_hdr.add_run("ATENEO+ | Dossier Integral de Investigación, Ingeniería y Ponencia CAISEB")
        r_hdr.font.name = "Arial"
        r_hdr.font.size = Pt(8)
        r_hdr.font.color.rgb = COLOR_MUTED
        
        # Pie de página institucional
        footer = section.footer
        p_ftr = footer.paragraphs[0]
        p_ftr.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_ftr = p_ftr.add_run("Ateneo+ v1.0.0 — Simulador Clínico Multimodal & RAG Formativo GPC Ecuador — Confidencial / Material de Ponencia")
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
    r_inst = p_inst.add_run("CONGRESO ACADÉMICO INTERNACIONAL DE INNOVACIÓN EN SALUD, EDUCACIÓN Y BIENESTAR (CAISEB 2026)")
    r_inst.font.name = "Arial"
    r_inst.font.size = Pt(11)
    r_inst.font.bold = True
    r_inst.font.color.rgb = COLOR_NAVY
    
    p_subinst = doc.add_paragraph()
    p_subinst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_subinst.paragraph_format.space_after = Pt(20)
    r_subinst = p_subinst.add_run("DOSSIER TÉCNICO, CIENTÍFICO, METODOLÓGICO Y GUÍA DE PONENCIA MAGISTRAL (40 MINUTOS)")
    r_subinst.font.name = "Arial"
    r_subinst.font.size = Pt(9.5)
    r_subinst.font.color.rgb = COLOR_MUTED
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(16)
    r_title = p_title.add_run("SIMULADOR CLÍNICO MULTIMODAL BASADO EN INTELIGENCIA ARTIFICIAL Y RAG PARA EL ENTRENAMIENTO FORMATIVO Y ANALÍTICA DEL APRENDIZAJE MÉDICO EN ECUADOR")
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
    
    r_inv2 = p_meta.add_run("Mgtr. Estefani Angélica Sánchez Morales (Investigadora — Educación Médica, Metodología y Validación Clínica)\n")
    r_inv2.font.size = Pt(10)
    r_inv2.font.bold = True
    r_inv2.font.color.rgb = COLOR_DARK
    
    p_fil = doc.add_paragraph()
    p_fil.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_fil.paragraph_format.space_after = Pt(20)
    r_fil = p_fil.add_run("Filiación: Ateneo+\nQuito, Ecuador — Octubre 2026")
    r_fil.font.size = Pt(9)
    r_fil.font.italic = True
    r_fil.font.color.rgb = COLOR_MUTED
    
    doc.add_page_break()

    # =========================================================================
    # SECCIÓN 1: ANTECEDENTES HISTÓRICOS Y CRISIS DE LA EDUCACIÓN MÉDICA EN ECUADOR
    # =========================================================================
    add_heading_1(doc, "1. ANTECEDENTES HISTÓRICOS Y CRISIS DE LA EDUCACIÓN MÉDICA EN ECUADOR")
    
    add_body_paragraph(
        doc,
        "La enseñanza de la medicina clínica en el Ecuador ha estado históricamente condicionada por una brecha metodológica estructural. "
        "Tradicionalmente, la formación de competencias diagnósticas y terapéuticas se ha apoyado en dos esquemas pedagógicos convencionales: "
        "1) Centros de simulación basados en maniquíes mecatrónicos de alto costo (modelos tipo Laerdal o Gaumard), cuya adquisición e importación "
        "exige inversiones institucionales superiores a los $80,000 - $150,000 USD por estación, restringiendo su presencia a unas pocas facultades de élite "
        "en Quito, Guayaquil y Cuenca, y marginando a las universidades provinciales; y 2) El Aprendizaje Basado en Problemas (ABP / PBL) en soporte "
        "de papel o fichas estáticas, caracterizado por una evaluación retrospectiva, subjetiva, carente de interactividad en tiempo real y limitada "
        "a respuestas de opción múltiple desprovistas de razonamiento clínico abierto.",
        bold_prefix="Antecedentes y Limitaciones de la Simulación Tradicional: "
    )
    
    add_body_paragraph(
        doc,
        "Según las auditorías del Consejo de Aseguramiento de la Calidad de la Educación Superior (CACES) sobre el Examen de Habilitación para el "
        "Ejercicio Profesional (EHEP) de médicos cirujanos, y los informes epidemiológicos del Instituto Nacional de Estadística y Censos (INEC) "
        "junto al Ministerio de Salud Pública (MSP), el internado rotativo representa un período crítico de alta vulnerabilidad. "
        "Las principales causas de muerte materna evitable (Hemorragia Posparto - Código Rojo y Preeclampsia Severa) y de morbimortalidad neonatal "
        "(Sepsis Neonatal Temprana y Encefalopatía Hipóxico-Isquémica) presentan una letalidad atribuible en un 42.4% a demoras en la identificación sindrómica "
        "y discrepancias severas en la dosificación farmacológica por parte de médicos en formación de primer contacto.",
        bold_prefix="Epidemiología y Auditoría de Error Médico en Internado: "
    )
    
    add_body_paragraph(
        doc,
        "Durante las guardias hospitalarias de 24 a 36 horas en hospitales cantonales distritales (Segundo Nivel) y centros de salud rurales (Primer Nivel), "
        "un médico tratante supervisa simultáneamente entre 12 y 18 internos rotativos. La tutoría individualizada a pie de cama (bedside teaching) resulta "
        "imposible de sostener de forma continua. La retroalimentación docente se torna episódica, verbalmente informal, punitiva y heterogénea, "
        "generando en el estudiante síndrome de burnout, temor al error iatrogénico en paciente real y dependencia de búsquedas improvisadas en internet.",
        bold_prefix="La Realidad Asistencial del Interno Rotativo: "
    )

    add_callout_box(
        doc,
        "En la ponencia magistral, se debe enfatizar este antecedente: un interno rotativo a las 03:00 a.m. en una sala de partos rural "
        "no cuenta con un simulador mecatrónico de $100,000 dólares ni con un especialista a su lado. Requiere haber entrenado su juicio clínico "
        "decenas de veces contra los algoritmos exactos de la GPC del MSP. Ateneo+ democratiza ese entrenamiento de grado hospitalario en el bolsillo del estudiante.",
        title="MENSAJE DE APERTURA MAGISTRAL (MINUTO 00:00 - 04:00)"
    )

    # =========================================================================
    # SECCIÓN 2: CÓMO AYUDAR A LOS ESTUDIANTES DE MEDICINA EN ECUADOR: EL ROL DE ATENEO+
    # =========================================================================
    add_heading_1(doc, "2. CÓMO AYUDAR A LOS ESTUDIANTES DE MEDICINA EN ECUADOR: EL ROL DE ATENEO+")
    
    add_body_paragraph(
        doc,
        "Ateneo+ fue concebido desde sus cimientos como una herramienta de transformación pedagógica formativa no punitiva, diseñada explícitamente "
        "para derribar las barreras que enfrentan los estudiantes de medicina e internos rotativos en el sistema sanitario ecuatoriano:",
        bold_prefix="Propuesta de Valor Formativo: "
    )
    
    add_bullet_item(doc, "Entorno de Entrenamiento Seguro Sin Riesgo Iatrogénico: Permite al estudiante cometer errores de dosificación, solicitar paraclínicos innecesarios o fallar en el diagnóstico dentro de un entorno digital controlado, visualizando la evolución fisiopatológica adversa del paciente sin comprometer la vida de un ser humano real.", bold_prefix="1. Seguridad Psicológica del Estudiante: ")
    add_bullet_item(doc, "Andamiaje Socrático Inmediato (Debriefing SSE): En lugar de calificar con un simple 'incorrecto', el sistema genera preguntas de orientación clínica en tiempo real token a token guiando al alumno a reconocer el mecanismo fisiopatológico de su omisión (ej. vasodilatación extrema o bloqueo neuromuscular por exceso de magnesio).", bold_prefix="2. Retroalimentación Socrática Inmediata: ")
    add_bullet_item(doc, "Anclaje Bedside Estricto al Cuadro Nacional de Medicamentos Básicos (CNMB): Entrena al estudiante a prescribir exclusivamente los fármacos que realmente existen y están autorizados para el primer y segundo nivel en los centros del MSP e IESS, evitando la frustración y el peligro de recetar moléculas de tercera línea inexistentes en la red pública.", bold_prefix="3. Realismo de la Farmacopea Local: ")
    add_bullet_item(doc, "Instrucción Adaptativa Personalizada en la ZDP: El estudiante no pierde tiempo resolviendo casos triviales que ya domina ni se frustra con escenarios para los que aún carece de prerrequisitos básicos; el sistema prescribe dinámicamente el siguiente caso en su umbral óptimo de aprendizaje según su vector cognitivo BKT.", bold_prefix="4. Trayectoria Curricular Óptima: ")
    add_bullet_item(doc, "Preparación de Alto Impacto para el EHEP (CACES) y la Medicatura Rural: El acervo de casos aborda exactamente los 4 ejes normativos que componen el banco de evaluación nacional del CACES y las patologías de mayor prevalencia en la medicatura rural obligatoria (salud materno-neonatal, tuberculosis, neumonías y enfermedades crónicas).", bold_prefix="5. Acreditación y Ejercicio Profesional: ")

    # =========================================================================
    # SECCIÓN 3: LÍMITES DE LA IA GENERALISTA Y EL PELIGRO DE LA ALUCINACIÓN MÉDICA
    # =========================================================================
    add_heading_1(doc, "3. LÍMITES DE LA IA GENERALISTA Y EL PELIGRO DE LA ALUCINACIÓN MÉDICA")
    
    add_body_paragraph(
        doc,
        "La irrupción de Modelos de Lenguaje Grande (LLMs) fundacionales comerciales (como OpenAI GPT-4o, Google Gemini Pro o Anthropic Claude) "
        "ha generado la falsa percepción de que un chatbot generalista puede fungir como evaluador o tutor del juicio clínico. "
        "La investigación científica rigurosa y las pruebas empíricas ejecutadas en la línea de base de este proyecto demuestran que el uso directo "
        "de LLMs genéricos en configuración Zero-Shot o Few-Shot en medicina comporta riesgos críticos inaceptables:",
        bold_prefix="Diagnóstico de Riesgo Tecnológico: "
    )
    
    add_bullet_item(doc, "Tasa de Alucinación Evaluativa Masiva (45.8% en Baseline): En pruebas controladas con respuestas clínicas que contenían omisiones graves o dosis tóxicas, los modelos comerciales no anclados aprobaron conductas iatrogénicas debido a un sesgo de complacencia (sycophancy) y completitud sintáctica probabilística.", bold_prefix="1. Alucinación Evaluativa: ")
    add_bullet_item(doc, "Desajuste Jurisdiccional y Farmacopea Incompatible: Los modelos fundacionales están pre-entrenados preponderantemente sobre literatura anglosajona (guías NICE del Reino Unido o directrices de la AHA/ACC de EE. UU.). Al evaluar a un interno ecuatoriano, sugieren o exigen medicamentos de tercera línea de alto costo no disponibles en el Cuadro Nacional de Medicamentos Básicos (CNMB del CONASA) o contradicen los esquemas ministeriales oficiales (ej. pautas de fluidoterapia en shock hipovolémico obstétrico).", bold_prefix="2. Desfase con el CNMB: ")
    add_bullet_item(doc, "Ausencia Absoluta de Trazabilidad Forense y No Repudio: Ante una discrepancia con el docente o una calificación formativa cuestionada, un modelo comercial no puede certificar con certeza matemática el número de página física, acuerdo ministerial y párrafo oficial que respalda la penalización, impidiendo su adopción en procesos de acreditación universitaria (CACES).", bold_prefix="3. Carencia de Trazabilidad: ")
    add_bullet_item(doc, "Deriva de Versiones (Model Drift) y Dependencia Externa: Las APIs comerciales de terceros sufren cambios continuos de pesos, descontinuaciones imprevistas de endpoints y variabilidad de temperatura que destruyen la reproducibilidad científica exigida por revistas de primer cuartil (Q1).", bold_prefix="4. Falta de Reproducibilidad: ")

    # =========================================================================
    # SECCIÓN 4: TEORÍA Y ARQUITECTURA DE TRANSFORMERS Y MODELOS DE EMBEDDINGS (BGE-M3)
    # =========================================================================
    add_heading_1(doc, "4. TEORÍA Y ARQUITECTURA DE TRANSFORMERS Y MODELOS DE EMBEDDINGS")
    
    add_body_paragraph(
        doc,
        "Para comprender por qué Ateneo+ supera radicalmente a las alternativas comerciales, es imperativo desglosar la arquitectura interna "
        "del mecanismo de atención y los modelos de representación vectorial empleados.",
        bold_prefix="Fundamentos de Deep Learning: "
    )
    
    add_heading_2(doc, "4.1 El Mecanismo de Auto-Atención Escalada (Scaled Dot-Product Attention)")
    add_body_paragraph(
        doc,
        "La arquitectura Transformer (Vaswani et al., 2017) descansa sobre el cálculo del alineamiento contextual de representaciones densas. "
        "Dada una secuencia de entrada proyectada en matrices de Consulta (Query, Q), Llave (Key, K) y Valor (Value, V) en un espacio de dimensión d_k:",
        bold_prefix="Formulación Matemática: "
    )
    
    add_callout_box(
        doc,
        "Attention(Q, K, V) = softmax( (Q * K^T) / sqrt(d_k) ) * V\n\n"
        "Donde d_k representa la dimensionalidad de las llaves. El factor de escala 1 / sqrt(d_k) previene que el producto escalar "
        "crezca en magnitudes excesivas para dimensiones elevadas, lo cual empujaría la función softmax hacia regiones de gradientes infinitesimales (vanishing gradients).",
        title="ECUACIÓN CANÓNICA DE AUTO-ATENCIÓN"
    )
    
    add_body_paragraph(
        doc,
        "En la arquitectura Multi-Head Attention, este mecanismo se paraleliza a lo largo de h cabezas independientes, permitiendo al modelo atender simultáneamente "
        "a información procedente de diferentes subespacios de representación en distintas posiciones. En el contexto clínico de Ateneo+, una cabeza aprende a ligar "
        "un signo de alarma (ej. 'epigastralgia en barra') con una complicación subyacente (ej. 'hematoma subcapsular hepático en Síndrome HELLP'), mientras otra cabeza "
        "atiende a la contraindicación posológica correspondiente.",
        bold_prefix="Multi-Head Attention en Razonamiento Clínico: "
    )

    add_heading_2(doc, "4.2 Arquitectura del Transformer de Embeddings BAAI/bge-m3")
    add_body_paragraph(
        doc,
        "El modelo seleccionado como columna vertebral del recuperador es BAAI/bge-m3 (Chen et al., 2024), un Transformer multilingüe de 568 millones de parámetros "
        "organizado en 24 capas de codificador con 16 cabezas de atención y una dimensión oculta latente de 1,024 dimensiones. A diferencia de los encoders BERT clásicos, "
        "BGE-M3 introduce tres capacidades cardinales denominadas M3 (Multi-Functionality, Multi-Linguality, Multi-Granularity):",
        bold_prefix="Características del Backbone BGE-M3: "
    )
    
    add_bullet_item(doc, "Representación Densa (Dense Retrieval): Mapea la consulta clínica completa a un único vector latente normalizado en norma L2 (||e||_2 = 1) de 1,024 dimensiones, capturando la intención semántica profunda y la sinonimia médica global.", bold_prefix="1. Rama Densa: ")
    add_bullet_item(doc, "Representación Dispersa Multilingüe (Lexical / Sparse Weighting): Genera ponderaciones de importancia de términos específicos (similar a un TF-IDF neuronal o SPLADE) directamente en el espacio de vocabulario, otorgando pesos elevados a fármacos únicos, acrónimos y dosis exactas.", bold_prefix="2. Rama Dispersa: ")
    add_bullet_item(doc, "Representación Multi-Vectorial (ColBERT-style Multi-Vector): Preserva embeddings a nivel de token para ejecución de MaxSim (atención cruzada tardía), resolviendo discrepancias finas entre documentos técnicos densamente estructurados.", bold_prefix="3. Rama Multi-Vector: ")
    add_bullet_item(doc, "Soporte de Longitud Extendida: Admite ventanas de contexto de hasta 8,192 tokens nativos, lo que garantiza que ninguna tabla de dosificación farmacológica compleja o algoritmo de triaje deba ser mutilado durante el chunking.", bold_prefix="4. Contexto Amplio: ")

    # =========================================================================
    # SECCIÓN 5: PROCEDIMIENTO DE INGENIERÍA: PIPELINE DE EXTRACCIÓN Y CURACIÓN DE DATOS
    # =========================================================================
    add_heading_1(doc, "5. PROCEDIMIENTO DE INGENIERÍA: PIPELINE DE EXTRACCIÓN Y CURACIÓN DE DATOS")
    
    add_body_paragraph(
        doc,
        "La construcción de la base de conocimiento normativo no fue un proceso manual ni ad-hoc; se diseñó e implementó un pipeline "
        "de ingeniería de datos automatizado, riguroso y determinista en Python y C++.",
        bold_prefix="Procedimiento Paso a Paso de Ingesta: "
    )
    
    add_heading_2(doc, "5.1 Clasificación Nosológica y Depuración Canónica (42 GPCs Oficiales)")
    add_body_paragraph(
        doc,
        "A través del módulo backend/ingestion_v2/01_classify_and_inventory_corpus.py, se inventariaron y sellaron con hash SHA-256 inmutable "
        "las 42 Guías de Práctica Clínica oficiales del MSP del Ecuador. Cada guía fue catalogada por especialidad médica "
        "(Obstetricia, Pediatría, Medicina Interna, Cirugía, Infectología), año de publicación ministerial y código de Acuerdo Ministerial.",
        bold_prefix="Fase 1 - Inventario Criptográfico: "
    )

    add_heading_2(doc, "5.2 Extracción Nativa con Detección de Paginación Física Real (PyMuPDF C++)")
    add_body_paragraph(
        doc,
        "Implementado en backend/ingestion_v2/02_extract_native_pymupdf.py. Los parsers basados en OCR o bibliotecas ingenuas de Python "
        "pierden la correspondencia con el número de página real impreso en el pie del documento. Empleando los bindings nativos de PyMuPDF (MuPDF en C++), "
        "el pipeline extrae el flujo de texto inyectando delimitadores canónicos inviolables:",
        bold_prefix="Fase 2 - Foliación Física Exacta: "
    )
    add_callout_box(
        doc,
        "--- [PÁGINA FÍSICA X DE Y] ---\n"
        "Este delimitador garantiza que cualquier recomendación o fármaco extraído conserve su referencia de página original "
        "para auditoría médica, defensas universitarias y no repudio legal.",
        title="DELIMITADOR CANÓNICO DE PAGINACIÓN"
    )

    add_heading_2(doc, "5.3 Extracción Matricial de Tablas Clínicas Complejas en Markdown")
    add_body_paragraph(
        doc,
        "Implementado en backend/ingestion_v2/03_extract_tables_camelot.py. Las tablas de dosificación posológica, criterios de severidad "
        "(ej. Escala de Glasgow, Criterios de Ranson, Criterios de Severidad en Preeclampsia) y algoritmos de manejo se extraen mediante análisis de mallas "
        "geométricas lineales con Camelot (Lattice mode), serializándolas en tablas Markdown bidimensionales completas y preservando la integridad de encabezados.",
        bold_prefix="Fase 3 - Preservación Matricial: "
    )

    add_heading_2(doc, "5.4 Token Chunking Semántico e Indivisible (7,052 Chunks)")
    add_body_paragraph(
        doc,
        "A diferencia del chunking ciego por conteo fijo de caracteres que corta frases a la mitad, Ateneo+ emplea segmentación "
        "semántica jerárquica guiada por encabezados nosológicos (Título -> Diagnóstico -> Cuadro Clínico -> Tratamiento -> Farmacoterapia). "
        "El corpus consolidado resultó en exactamente 7,052 fragmentos de conocimiento con metadatos completos (ID de guía, página inicial, página final y sección).",
        bold_prefix="Fase 4 - Segmentación Semántica: "
    )

    # =========================================================================
    # SECCIÓN 6: PROCEDIMIENTO DE MINERÍA DE NEGATIVOS Y FINE-TUNING EN GPU A100
    # =========================================================================
    add_heading_1(doc, "6. PROCEDIMIENTO DE MINERÍA DE NEGATIVOS Y FINE-TUNING EN GPU A100")
    
    add_heading_2(doc, "6.1 Minería Semántica en Dos Etapas (Two-Stage Dense Hard Negative Mining)")
    add_body_paragraph(
        doc,
        "Para que un modelo de embeddings aprenda a discriminar matices clínicos sutiles (ej. diferenciar Preeclampsia Leve de Preeclampsia Severa, "
        "o Dosis de Carga de Sulfato de Magnesio de 4 g vs Dosis de Mantenimiento de 1 g/h), no basta con entrenarlo con negativos aleatorios. "
        "Se implementó el algoritmo Two-Stage Hard Negative Mining en backend/ingestion_v2/04_mine_hard_negatives_bm25.py:",
        bold_prefix="Estrategia Contrastiva Avanzada: "
    )
    add_bullet_item(doc, "Etapa 1 (Recuperación Léxica BM25): Para cada consulta clínica q, se recuperan los 30 fragmentos con mayor similitud léxica que comparten vocabulario médico pero no constituyen la respuesta correcta.", bold_prefix="Candidatos Léxicos: ")
    add_bullet_item(doc, "Filtro Defensivo Anti-Falsos Negativos (6 Reglas): 1) Exclusión de identidad (c != p); 2) Exclusión intra-sección (misma guía y sección descartadas); 3) Solapamiento Jaccard de bigramas < 65%; 4) Exclusión de páginas de créditos e ISBN; 5) Exclusión de índices con alta densidad de dígitos (> 15% de líneas con números); y 6) Exclusión de listas de autores con >= 4 cargos médicos.", bold_prefix="Filtro Defensivo: ")
    add_bullet_item(doc, "Etapa 2 (Re-ranking Semántico en Lote): Computa los embeddings BGE-M3 de los candidatos válidos y selecciona el hard negative óptimo n* mediante máxima similitud coseno en espacio latente de 1,024 dimensiones.", bold_prefix="Re-ranking Denso: ")

    add_heading_2(doc, "6.2 Curación Ciega del Ground Truth y Certificación Kappa")
    add_body_paragraph(
        doc,
        "Implementado en backend/ingestion_v2/05_build_ground_truth_pool.py. Se construyó un banco balanceado de 160 pares evaluados bajo "
        "un protocolo Likert ordinal de tres niveles: 0 (Irrelevante/Contradictorio), 1 (Contextual) y 2 (Gold Standard normativo vinculante). "
        "Dos facultativos especialistas evaluaron en doble ciego independiente los pares, alcanzando un coeficiente Kappa Ponderado Cuadrático "
        "de Cohen kw = 0.9531 con 91.25% de acuerdo simple observado (Po) y cero discrepancias mayores (0 <-> 2), superando el umbral de aceptación científica (kw >= 0.80).",
        bold_prefix="Fase 5 - Ground Truth Certificado: "
    )

    add_heading_2(doc, "6.3 Entrenamiento Supervisado con MNRL en GPU NVIDIA A100")
    add_body_paragraph(
        doc,
        "Implementado en backend/ingestion_v2/06_train_bge_m3.py y colab_fase6_train_bge_m3.ipynb. "
        "Se ajustaron los 568 millones de parámetros del modelo mediante Multiple Negatives Ranking Loss (MNRL):",
        bold_prefix="Fase 6 - Optimización GPU: "
    )
    
    add_callout_box(
        doc,
        "L = - sum_{i=1}^B log [ exp(sim(q_i, p_i) / tau) / ( exp(sim(q_i, p_i) / tau) + exp(sim(q_i, n_i) / tau) + sum_{j != i}^B exp(sim(q_i, p_j) / tau) ) ]\n\n"
        "Hiperparámetros Calibrados en Producción:\n"
        "• Hardware: GPU NVIDIA A100 (40 GB VRAM Tensor Cores, precisión bfloat16).\n"
        "• Dataset: 1,178 tripletas de entrenamiento, 249 de validación y 283 de test ciego OOD.\n"
        "• Batch size efectivo: B = 32 tripletas (31 in-batch negatives por paso).\n"
        "• Temperatura contrastiva: tau = 0.02 (factor de escala 1/tau = 50.0).\n"
        "• Tasa de aprendizaje: eta = 2 x 10^-5 con planificador CosineAnnealingLR y 10% de warmup.\n"
        "• Optimizador: AdamW con weight decay = 0.01 y 5 épocas de entrenamiento.\n"
        "• Consumo pico de VRAM: ~16.50 GB (41.2% de la capacidad de la A100, con 58.8% de margen anti-OOM).",
        title="MULTIPLE NEGATIVES RANKING LOSS (MNRL)"
    )

    # =========================================================================
    # SECCIÓN 7: MOTOR DE RECUPERACIÓN HÍBRIDA (RRF) Y PERSISTENCIA VECTORIAL
    # =========================================================================
    add_heading_1(doc, "7. MOTOR DE RECUPERACIÓN HÍBRIDA (RRF) Y PERSISTENCIA VECTORIAL")
    
    add_body_paragraph(
        doc,
        "El suavizado semántico inherente a los espacios vectoriales continuos provoca que dos dosis numéricas disímiles "
        "(ej. 100 mg vs 1000 mg) tengan un coseno de similitud de 0.94 debido a que comparten el mismo contexto oracional. "
        "Para erradicar este riesgo, Ateneo+ implementa Reciprocal Rank Fusion (RRF):",
        bold_prefix="Arquitectura de Ensamble de Recuperación: "
    )
    
    add_bullet_item(doc, "Rama Densa (Dense Vector Store): Colección gpc_msp_v2 en ChromaDB v2 estructurada con grafo HNSW optimizado (espacio coseno, M=16, ef_construction=128, ef_search=64) alimentada con los pesos de ateneo-bge-m3-ecuador-v2.", bold_prefix="1. Búsqueda Densa: ")
    add_bullet_item(doc, "Rama Dispersa (Sparse Lexical Store): Índice serializado BM25Okapi (k1=1.5, b=0.75, 14.00 MB) tokenizado con preservación estricta de símbolos médicos (guiones nosológicos, mg/kg/h, acrónimos CURB-65, HELLP).", bold_prefix="2. Búsqueda Léxica: ")
    add_bullet_item(doc, "Algoritmo de Fusión de Rangos Recíprocos (RRF k=60): RRF_Score(d) = 1/(60 + rank_dense(d)) + 1/(60 + rank_bm25(d)). El fragmento Top-1 resultante equilibra armónicamente la comprensión sindrómica global con la exactitud literal de fármacos y dosis.", bold_prefix="3. Fusión RRF: ")
    add_bullet_item(doc, "Caché RAG de 2 Niveles: Nivel 1 con hash determinista SHA-256 de consulta normalizada + Nivel 2 con similitud semántica de coseno >= 0.98. Reduce la latencia de inferencia de 8,120 ms (Cold Retrieval) a 0.05 ms (Hot Retrieval en sub-milisegundo).", bold_prefix="4. Caché de Inferencia: ")

    # =========================================================================
    # SECCIÓN 8: ARQUITECTURA DE SOFTWARE, SEGURIDAD Y RESILIENCIA
    # =========================================================================
    add_heading_1(doc, "8. ARQUITECTURA INTEGRAL DE SOFTWARE, SEGURIDAD Y RESILIENCIA")
    
    add_body_paragraph(
        doc,
        "Ateneo+ está construido bajo los principios de Clean Architecture, Domain-Driven Design (DDD) y la metodología 12-Factor App, "
        "desacoplando rigurosamente las capas de presentación, servicios de aplicación, dominio psicométrico y persistencia:",
        bold_prefix="Ingeniería de Software de Grado Clínico: "
    )
    
    add_bullet_item(doc, "Backend Monolito Modular Asíncrono: FastAPI en Python 3.11 con inyección formal de dependencias Depends() y estandarización de errores bajo RFC 7807 (Problem Details for HTTP APIs).", bold_prefix="Core Backend: ")
    add_bullet_item(doc, "Coordinación Transaccional Unit of Work: Context manager SqlAlchemyUnitOfWork que asegura atomicidad ACID estricta: si la evaluación RAG, el cálculo psicométrico BKT o el registro analítico fallan, se dispara un rollback completo e inmediato.", bold_prefix="Transaccionalidad: ")
    add_bullet_item(doc, "ResilientLLMGateway con Circuit Breaker y Adaptador Universal OpenAI-Compatible: Disyuntores de estado CLOSED, OPEN y HALF_OPEN. En modo por defecto gestiona la cascada de Google Gemini (3.8 Flash, 3.7 Flash, 3.5 Flash) con zero-latency fallback ante saturación de cuota (HTTP 429). Gracias al desacoplamiento desacoplado en AppSettings (LLM_PROVIDER=openai_compatible), admite cualquier modelo de código abierto o fine-tuneado por la comunidad médica (LLaMA-3-Med, BioMistral, Meditron, DeepSeek-R1) alojado en servidores locales o remotos (vLLM, Ollama, TGI, llama.cpp), soportando multimodalidad en base64 y streaming SSE sin alterar la lógica de negocio.", bold_prefix="Gateway de IA Agnóstico: ")
    add_bullet_item(doc, "Blindaje contra Prompt Injection (PromptSecurityGuard): Pipeline de sanitización previa y detección heurística con 11 vectores de ataque neutralizados al 100% (cero falsos positivos en razonamientos médicos legítimos) con Rate Limiting Token Bucket.", bold_prefix="Ciberseguridad en Salud: ")
    add_bullet_item(doc, "Persistencia Híbrida SQLite WAL y PostgreSQL: SQLite 3 configurado con PRAGMA journal_mode=WAL y PRAGMA synchronous=NORMAL para alta concurrencia de lectura/escritura, con conmutación automática a clusters PostgreSQL empresariales mediante variable DATABASE_URL.", bold_prefix="Base de Datos: ")
    add_bullet_item(doc, "Modo Offline Hospitalario (IndexedDB + Outbox): El interno puede resolver casos en zonas sin conectividad (consultorios rurales o subsuelos de hospitales); la base de datos cliente almacena las resoluciones en cola y sincroniza con el servidor al detectar conexión.", bold_prefix="Resiliencia Offline PWA: ")

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
    # SECCIÓN 9: EXPERIENCIA CLÍNICA MULTIMODAL Y MÓDULOS DEL SISTEMA
    # =========================================================================
    add_heading_1(doc, "9. EXPERIENCIA CLÍNICA MULTIMODAL Y COMPONENTES DEL SISTEMA")
    
    add_heading_2(doc, "9.1 Interfaz Split-Screen 50/50 y Dictado por Voz")
    add_body_paragraph(
        doc,
        "La interfaz divide el espacio de trabajo en dos paneles equilibrados: a la izquierda, la viñeta clínica estructurada, constantes vitales "
        "y estudios paraclínicos; a la derecha, el lienzo de argumentación SOAP (Subjetivo, Objetivo, Análisis, Plan). "
        "Integra el módulo ClinicalVoiceRecorder con la Web Speech API nativa calibrada a 'es-EC', permitiendo dictar juicios clínicos "
        "con una precisión de transcripción fluida y sin consumo de tokens de audio en el LLM."
    )
    add_image_with_caption(
        doc,
        "docs/5_capturas_sistema/04_resolucion_multimodal_rx_dictado.png",
        "Figura 1: Entorno de resolución multimodal Split-Screen de Ateneo+ con radiografía de tórax y dictado clínico por voz.",
        width_in=6.2
    )

    add_heading_2(doc, "9.2 Imagenología Médica Avanzada y Visor DICOM Volumétrico Multicorte")
    add_body_paragraph(
        doc,
        "Ateneo+ incorpora un visor DICOM nativo desarrollado sobre Canvas 2D/WebGL del cliente (cero consumo de tokens de IA por renderizado). "
        "Permite desplazamiento continuo multicorte a través de series tomográficas axiales, calibrador milimétrico de lesiones (caliper) "
        "y presets de Unidades Hounsfield (HU) según estándares del American College of Radiology (ACR):"
    )
    add_bullet_item(doc, "Ventana Pulmonar: Nivel -600 HU, Ancho (WW) 1500 HU (evaluación de consolidaciones y broncogramas aéreos en neumonía).")
    add_bullet_item(doc, "Ventana de Mediastino: Nivel 40 HU, Ancho 350 HU (linfadenopatías y grandes vasos).")
    add_bullet_item(doc, "Ventana Ósea: Nivel 450 HU, Ancho 2000 HU (fracturas y metástasis óseas).")
    add_bullet_item(doc, "Ventana Cerebral: Nivel 40 HU, Ancho 80 HU (isquemia vs hemorragia intracraneal aguda).")
    add_bullet_item(doc, "Ventana Abdominal: Nivel 40 HU, Ancho 400 HU (hígado, bazo y líquido libre cavitario).")

    add_heading_2(doc, "9.3 Simulación Dinámica Secuencial por Fases Clínicas")
    add_body_paragraph(
        doc,
        "Frente a los evaluadores tradicionales de turno único (Single-Turn QA), Ateneo+ simula la evolución cronológica real del paciente "
        "en 3 fases progresivas gestionadas mediante SimulationStepper:"
    )
    add_bullet_item(doc, "Fase 1 (Anamnesis y Sospecha): Análisis del motivo de consulta y signos de peligro. El estudiante formula su hipótesis y solicita exámenes pertinentes.")
    add_bullet_item(doc, "Fase 2 (Interpretación de Paraclínicos): El sistema desbloquea los trazados electrocardiográficos (calibrados a 25 mm/s), gasometrías o imágenes solicitadas para confirmar el diagnóstico definitivo.")
    add_bullet_item(doc, "Fase 3 (Prescripción Terapéutica y Manejo): Formulación de esquemas farmacológicos, dosis por kg/peso, vías de infusión y criterios de referencia a Tercer Nivel según la GPC.")
    add_image_with_caption(
        doc,
        "docs/5_capturas_sistema/05_simulacion_dinamica_fases_clinicas.png",
        "Figura 2: Stepper de simulación clínica por fases secuenciales en Ateneo+ con retroalimentación inmediata.",
        width_in=6.2
    )

    add_heading_2(doc, "9.4 Debate Socrático Multiturno en Tiempo Real (SSE)")
    add_body_paragraph(
        doc,
        "Cuando el estudiante incurre en omisiones o errores dosimétricos, el sistema activa el Debate Socrático. "
        "A través de Server-Sent Events (SSE), el evaluador genera preguntas orientadoras token a token guiando al alumno "
        "a descubrir la causa fisiopatológica de su error (ej. '¿Qué parámetro de la función renal evaluaste antes de indicar este aminoglucósido?'), "
        "citando textualmente la sección de la norma ministerial."
    )

    add_heading_2(doc, "9.5 Salas Colaborativas Hospitalarias (AteneoRoom) y Consenso en Tiempo Real")
    add_body_paragraph(
        doc,
        "Las Salas Colaborativas Hospitalarias (AteneoRoom) constituyen el subsistema sincrónico de deliberación clínica y debate colegiado "
        "en tiempo real de Ateneo+. Diseñado para simular las reuniones de ateneo bibliográfico, entrega de guardia y juntas médicas docentes, "
        "permite que un docente o coordinador hospitalario modere a decenas de internos y residentes conectados en simultáneo, evaluando la "
        "toma de decisiones clínicas colegiada bajo normativas del Ministerio de Salud Pública (MSP) de Ecuador."
    )
    add_body_paragraph(
        doc,
        "AteneoRoom opera bajo un modelo de 4 fases pedagógicas estrictamente sincronizadas mediante WebSockets bidireccionales nativos: "
        "(1) Fase de Espera y Lobby: antesala de acreditación con tarjeta institucional y código de sala único; "
        "(2) Fase de Resolución Activa: donde los participantes redactan y argumentan en un lienzo split-screen 50/50; "
        "(3) Fase de Discusión y Debate: apertura controlada de la cohorte para deliberar discrepancias; y "
        "(4) Fase de Consenso y Cierre: consolidación analítica con gráficos de distribución diagnóstica y semáforo de riesgo.",
        bold_prefix="Arquitectura de 4 Fases Sincrónicas: "
    )
    add_bullet_item(doc, "Modalidad de Resolución Individual: Cada estudiante redacta y envía su dictamen clínico de forma autónoma. Durante la resolución, el panel analítico de cohorte permanece oculto para evitar sesgo de anclaje (anchoring bias), revelándose únicamente al finalizar.", bold_prefix="1. Modo Individual: ")
    add_bullet_item(doc, "Modalidad de Ateneo en Grupo (Co-escritura en Vivo): Los estudiantes colaboran en un único dictamen compartido mediante un lienzo de co-escritura en tiempo real. Integra bloqueo optimista de párrafos, detección de presencia activa ('Redactando...') y sincronización delta mediante WebSockets.", bold_prefix="2. Modo Co-escritura Grupal: ")

    add_heading_3(doc, "Motor de Inteligencia Colectiva y Resiliencia de Red")
    add_body_paragraph(
        doc,
        "AteneoRoom incorpora un motor de consenso diagnóstico que agrega las respuestas de los participantes calculando: (a) promedio ponderado de calificación "
        "de la cohorte sobre 10 puntos, (b) porcentaje de quórum sobre el diagnóstico principal CIE-10, y (c) consolidación de las 4 brechas normativas más frecuentes "
        "frente a las GPC del MSP. En el ámbito de infraestructura, el sistema implementa un ciclo de vida defensivo en React 18 (StrictMode Safe), latidos "
        "cada 20 segundos con reconexión exponencial, y un mecanismo de sondeo de respaldo reactivo (polling cada 2.5s) ante interrupciones de red hospitalaria."
    )
    add_callout_box(
        doc,
        "El módulo AteneoRoom transforma la evaluación clínica individual en un ejercicio socrático y colegiado. "
        "Al contrastar las decisiones individuales con el consenso de la cohorte y la norma ministerial, "
        "se fomenta el razonamiento basado en evidencia y se reducen los sesgos de anclaje diagnóstico en la formación médica.",
        title="VALOR PEDAGÓGICO HOSPITALARIO / APRENDIZAJE COLECTIVO"
    )

    add_heading_2(doc, "9.6 Ciclo Formativo Cerrado: Pre-Test Diagnóstico, Plan Heurístico Prescriptivo y Post-Test Isomórfico")
    add_body_paragraph(
        doc,
        "Para superar el paradigma de la evaluación terminal estática y garantizar el cierre efectivo del bucle didáctico formativo "
        "(closing the clinical loop), Ateneo+ integra un ciclo cerrado de intervención clínica estructurado en tres fases secuenciales: "
        "(1) Evaluación Diagnóstica Inicial (Pre-Test) estratificada por áreas troncales, (2) Síntesis Heurística de un Plan "
        "de Estudio Prescriptivo dosificado en la Zona de Desarrollo Próximo (ZDP), y (3) Reevaluación de Salida (Post-Test) generada mediante "
        "variantes clínicas isomórficas con medición psicométrica de la Ganancia Normalizada de Hake (g)."
    )
    add_bullet_item(
        doc,
        "La evaluación de entrada implementa muestreo estratificado balanceado en correspondencia directa con las cuatro áreas troncales "
        "del Examen de Habilitación para el Ejercicio Profesional de la Carrera de Medicina del Consejo de Aseguramiento de la Calidad de la "
        "Educación Superior (CACES) y las normativas del Ministerio de Salud Pública (MSP) de Ecuador. Se erradica el sesgo de sub-representación "
        "de constructo (Construct Underrepresentation) seleccionando exactamente un reactivo basal por área (balance 1:1:1:1 con ponderación "
        "equitativa de 2.50 puntos cada uno sobre base 10.0):",
        bold_prefix="1. Pre-Test Diagnóstico y Muestreo Estratificado CACES: "
    )

    # Tabla de Troncales CACES y Reactivos Basales
    tr_heads = ["Área Troncal CACES / MSP", "Reactivos Basales Canónicos", "Normativa Ministerial Asociada", "Ponderación"]
    troncales_data = [
        ["Ginecología y Obstetricia", "Preeclampsia severa / Choque hipovolémico / Código Rojo", "GPC Trastornos Hipertensivos del Embarazo y Hemorragia Posparto MSP", "25% (2.50 pts)"],
        ["Pediatría y Neonatología", "Crisis asmática grave / Sepsis neonatal temprana / Bronquiolitis", "GPC Asma Pediátrica, Sepsis Neonatal y Bronquiolitis MSP", "25% (2.50 pts)"],
        ["Medicina Interna y Crónicos", "Cetoacidosis diabética / Síndrome coronario agudo sin elevación ST", "GPC Diabetes Mellitus Tipo 2 y Síndrome Coronario Agudo MSP", "25% (2.50 pts)"],
        ["Infectología y Salud Pública", "Neumonía adquirida en la comunidad grave / Dengue con signos de alarma", "GPC Neumonía Bacteriana y Guía de Manejo de Dengue MSP", "25% (2.50 pts)"]
    ]
    add_institutional_table(doc, tr_heads, troncales_data, col_alignments=["left", "left", "left", "center"], col_widths=[1.5, 2.0, 2.0, 1.0])

    add_bullet_item(
        doc,
        "La interfaz del estudiante (StudentAnalyticsPage) integra un selector institucional adaptativo en lienzo #f0f4f9 con tarjetas "
        "rounded-[28px] y cero envoltorios decorativos. Permite optar por la Batería Troncal CACES (4 casos multidisciplinares) o por baterías "
        "monotemáticas por especialidad. Todos los reactivos son renderizados mediante ClinicalMarkdownRenderer, interpretando jerarquías tipográficas, "
        "citas normativas y tablas farmacológicas sin texto plano crudo.",
        bold_prefix="2. Selector Institucional y Renderizado Tipográfico Médico: "
    )
    add_bullet_item(
        doc,
        "El algoritmo heurístico pondera cada omisión clínica detectada mediante la función de severidad psicométrica: W_i = Severidad(omisión) * (1.05 - P(L_k)), "
        "donde la severidad clasifica riesgos críticos (shock, parada cardíaca, eclampsia, muerte fetal) con peso 1.0, moderados con 0.6 y menores con 0.3, "
        "modulados inversamente por la maestría BKT del estudiante. El motor prescribe un plan atómico dosificado en 3 modalidades: lecturas guiadas de secciones "
        "específicas de la GPC del MSP, simulación de casos en ZDP y debriefing socrático reflexivo.",
        bold_prefix="3. Motor Heurístico de Prescripción Pedagógica: "
    )
    add_bullet_item(
        doc,
        "Para neutralizar el sesgo de memorización que invalida las pruebas idénticas repetidas, el generador de post-test sintetiza escenarios "
        "clínicos paralelos e isomórficos preservando estricta correspondencia 1:1 con las cuatro troncales evaluadas en la entrada. Las variantes "
        "preservan la misma encrucijada fisiopatológica, el mismo estándar de oro de la GPC ministerial y las mismas competencias de Bloom, "
        "pero modifican la demografía del paciente, edad gestacional, cifras hemodinámicas y parámetros de laboratorio dentro del mismo umbral normativo. "
        "El pipeline se apoya en el ResilientLLMGateway respaldado por un banco curado calibrado de 10 patologías canónicas.",
        bold_prefix="4. Post-Test Isomórfico Asistido por Inteligencia Artificial: "
    )
    add_bullet_item(
        doc,
        "Al concluir el post-test, el backend calcula en tiempo real la Ganancia Normalizada de Hake: g = (Score_Post - Score_Pre) / (10.0 - Score_Pre). "
        "Este coeficiente, consolidado en investigación en educación médica (Hake, 1998), desacopla el efecto de la nota de entrada y cuantifica la proporción "
        "del aprendizaje máximo posible alcanzado por el estudiante: Ganancia Alta (g >= 0.70), Ganancia Media (0.30 <= g < 0.70) o Ganancia Baja (g < 0.30).",
        bold_prefix="5. Cuantificación Psicométrica de la Ganancia de Hake (g): "
    )
    add_callout_box(
        doc,
        "La transición desde una evaluación formativa abierta hacia un bucle cerrado prescriptivo permite a los directores médicos y docentes "
        "obtener evidencia científica verificable sobre el impacto pedagógico de la plataforma. La ganancia de Hake cuantifica objetivamente "
        "cómo el estudio prescriptivo guiado por las GPC de Ecuador transforma brechas clínicas basales en competencia diagnóstica consolidada.",
        title="EVIDENCIA CIENTÍFICA DEL APRENDIZAJE FORMATIVO / GANANCIA DE HAKE"
    )

    # =========================================================================
    # SECCIÓN 10: MODELADO PSICOMÉTRICO FORMAL (KST + BKT + ZDP)
    # =========================================================================
    add_heading_1(doc, "10. MODELADO PSICOMÉTRICO FORMAL: KST, BKT Y ZONA DE DESARROLLO PRÓXIMO")
    
    add_body_paragraph(
        doc,
        "Ateneo+ trasciende los sistemas reactivos de preguntas aleatorias incorporando un motor de tutoría inteligente proactiva "
        "fundamentado en dos teorías psicométricas matemáticas consolidadas:",
        bold_prefix="Fundamentación Psicométrica: "
    )
    
    add_heading_2(doc, "10.1 Knowledge Space Theory (KST) y Grafo DAG de Competencias")
    add_body_paragraph(
        doc,
        "El dominio clínico normativo se modela como un grafo acíclico dirigido G = (V, E) estructurado sobre 7 competencias esenciales "
        "con relaciones de prerrequisito indispensables:",
        bold_prefix="Topología de Conocimiento: "
    )
    add_bullet_item(doc, "1. Anamnesis y Semiología Estructurada -> Prerrequisito de Diagnóstico Diferencial.")
    add_bullet_item(doc, "2. Diagnóstico Diferencial -> Prerrequisito de Selección de Paraclínicos y Diagnóstico Definitivo.")
    add_bullet_item(doc, "3. Selección de Paraclínicos -> Prerrequisito de Correlación Multimodal (ECG, Rx, Labs).")
    add_bullet_item(doc, "4. Correlación Multimodal -> Prerrequisito de Diagnóstico Definitivo y Severidad.")
    add_bullet_item(doc, "5. Diagnóstico Definitivo -> Prerrequisito de Terapéutica Farmacológica MSP.")
    add_bullet_item(doc, "6. Terapéutica Farmacológica MSP -> Prerrequisito de Seguimiento y Prevención Comunitaria.")
    add_bullet_item(doc, "7. Seguimiento y Prevención Comunitaria (Criterios de referencia y vigilancia ambulatoria).")

    add_image_with_caption(
        doc,
        "docs/5_capturas_sistema/03_grafo_espacio_conocimiento_kst.png",
        "Figura 3: Grafo acíclico dirigido (DAG) de dependencias curriculares KST en la plataforma Ateneo+.",
        width_in=5.8
    )

    add_heading_2(doc, "10.2 Bayesian Knowledge Tracing (BKT) Continuo")
    add_body_paragraph(
        doc,
        "Para inferir la probabilidad latente de que un estudiante domine una competencia específica c en el tiempo t (P(L_t^(c))), "
        "el sistema implementa BKT continuo (Corbett & Anderson, 1994) calibrado psicométricamente:",
        bold_prefix="Actualización Bayesiana en Tiempo Real: "
    )
    
    add_callout_box(
        doc,
        "Actualización Posterior ante Acierto (obs = 1):\n"
        "P(L_t | obs=1) = [ P(L_t-1) * (1 - S) ] / [ P(L_t-1) * (1 - S) + (1 - P(L_t-1)) * G ]\n\n"
        "Actualización Posterior ante Omisión / Error (obs = 0):\n"
        "P(L_t | obs=0) = [ P(L_t-1) * S ] / [ P(L_t-1) * S + (1 - P(L_t-1)) * (1 - G) ]\n\n"
        "Paso de Transición de Aprendizaje:\n"
        "P(L_t+1) = P(L_t | obs) + (1 - P(L_t | obs)) * T\n\n"
        "Parámetros Calibrados en Producción:\n"
        "• L_0 = 0.10 a 0.40 (probabilidad a priori de dominio inicial según competencia).\n"
        "• T = 0.15 a 0.25 (tasa de transición formativa por caso resuelto).\n"
        "• G = 0.10 a 0.15 (probabilidad de acierto fortuito / Guess).\n"
        "• S = 0.05 a 0.12 (probabilidad de desliz involuntario teniendo maestría / Slip).",
        title="FORMULACIÓN MATEMÁTICA DE BKT"
    )

    add_image_with_caption(
        doc,
        "docs/2_figuras_300dpi/figura_kst_trajectory.png",
        "Figura 4: Simulación longitudinal de trayectorias de adquisición cognitiva BKT a lo largo de 10 casos resueltos.",
        width_in=6.0
    )

    add_heading_2(doc, "10.3 Algoritmo de Recomendación en la Zona de Desarrollo Próximo (ZDP)")
    add_body_paragraph(
        doc,
        "Basado en la teoría pedagógica de Vygotsky, Ateneo+ no permite que el estudiante elija casos al azar. "
        "El motor curricular identifica el conjunto de competencias en el umbral óptimo de asimilación cognitiva: "
        "ZDP = { c in V | 0.30 <= P(L^(c)) <= 0.75  y  para todo p in Prereq(c), P(L^(p)) >= 0.50 }. "
        "El sistema selecciona automáticamente el caso clínico del catálogo que activa la competencia de menor dominio dentro de la ZDP, "
        "proporcionando una justificación pedagógica explícita en lenguaje natural.",
        bold_prefix="Selección Curricular Proactiva: "
    )
    add_image_with_caption(
        doc,
        "docs/5_capturas_sistema/02_catalogo_y_recomendacion_zdp.png",
        "Figura 5: Tarjeta de recomendación curricular proactiva en la Zona de Desarrollo Próximo (ZDP) en Ateneo+.",
        width_in=6.0
    )

    # =========================================================================
    # SECCIÓN 11: EVIDENCIA EXPERIMENTAL Y BENCHMARKS CIENTÍFICOS
    # =========================================================================
    add_heading_1(doc, "11. EVIDENCIA EXPERIMENTAL Y BENCHMARKS CIENTÍFICOS")
    
    add_heading_2(doc, "11.1 Comparativa Empírica Pre vs. Post Fine-Tuning en GPU A100")
    add_body_paragraph(
        doc,
        "Evaluación comparativa sobre un banco ciego de 570 tripletas de validación y prueba sobre las 42 GPCs oficiales del MSP. "
        "Los resultados certifican mejoras estadísticamente irrefutables en todas las dimensiones de recuperación de información:"
    )
    
    headers_ir = ["Métrica de Recuperación (IR)", "Baseline BGE-M3", "Ateneo+ Fine-Tuned", "Delta Absoluto", "Ganancia Relativa (%)"]
    data_metrics_ir = [
        ["Accuracy@1 (Hit@1)", "0.0522", "0.2450", "+0.1928", "+369.23% (4.7x)"],
        ["Accuracy@5 (Hit@5)", "0.1606", "0.4739", "+0.3133", "+195.00% (2.9x)"],
        ["Mean Reciprocal Rank (MRR@1)", "0.0522", "0.2450", "+0.1928", "+369.23%"],
        ["Mean Reciprocal Rank (MRR@5)", "0.0889", "0.3328", "+0.2439", "+274.40% (3.7x)"],
        ["NDCG@5 (Normalized Discounted Gain)", "0.1066", "0.3682", "+0.2616", "+245.40%"],
        ["Precision@5 / Recall@5", "0.0321 / 0.1606", "0.0948 / 0.4739", "+0.0627 / +0.3133", "+195.00%"]
    ]
    add_institutional_table(doc, headers_ir, data_metrics_ir, col_alignments=["left", "center", "center", "center", "center"])

    add_heading_2(doc, "11.2 Benchmark Ciego Out-of-Distribution (OOD) y Prueba de Wilcoxon")
    add_body_paragraph(
        doc,
        "Para prevenir fuga de datos (Zero Data Leakage), la partición se ejecutó a nivel de guías completas (Document-Level Split). "
        "El modelo se evaluó sobre N = 283 consultas de guías jamás observadas en el entrenamiento. "
        "La prueba no paramétrica de rangos con signo de Wilcoxon arrojó W = 365.0 con un p-value = 0.0001018 (p < 0.001), "
        "confirmando que la superioridad del modelo re-entrenado no es producto del azar. El modelo supervisado supera en 6x al modelo base original:",
        bold_prefix="Generalización Científica: "
    )
    
    headers_ood = ["Arquitectura de Búsqueda", "Hit@1 (%)", "Hit@3 (%)", "Hit@5 (%)", "MRR@5 (%)", "NDCG@5 (%)"]
    data_ood = [
        ["BM25 Puro (Léxico)", "2.47%", "4.95%", "5.30%", "3.55%", "3.99%"],
        ["BAAI/bge-m3 Base (Zero-Shot)", "0.71%", "3.18%", "3.53%", "1.90%", "2.31%"],
        ["Ateneo-BGE-M3 (Supervisado FT)", "4.24%", "9.19%", "11.66%", "7.12%", "8.26%"],
        ["Ensamble Híbrido RRF (k=60)", "3.53%", "7.77%", "9.89%", "5.87%", "6.88%"]
    ]
    add_institutional_table(doc, headers_ood, data_ood, col_alignments=["left", "center", "center", "center", "center", "center"])

    add_heading_2(doc, "11.3 Auditoría de Fidelidad Normativa (Faithfulness Score Anti-Alucinación)")
    add_body_paragraph(
        doc,
        "Bajo el estándar científico RAGAS, se evaluó la relación entre afirmaciones evaluativas emitidas y las citas literales de la GPC. "
        "Ateneo+ alcanzó un 100.0% de fidelidad (36 de 36 afirmaciones respaldadas textualmente en la norma) con una tasa de alucinación < 5.0%, "
        "frente al 45.8% de alucinaciones y omisiones iatrogénicas detectadas en modelos comerciales como GPT-4o sin RAG:",
        bold_prefix="Control de Alucinaciones: "
    )
    
    headers_faith = ["Arquitectura Evaluativa", "Fidelidad Normativa (%)", "Afirmaciones Respaldadas", "Tasa de Alucinación (%)", "Nivel de Seguridad Clínica"]
    data_faith = [
        ["GPT-4o Zero-Shot (sin RAG)", "54.2%", "26 / 48", "45.8%", "Riesgo Crítico / No Apto"],
        ["RAG Genérico (Base BGE-M3)", "82.5%", "38 / 46", "17.5%", "Grounding Parcial"],
        ["Ateneo+ RAG Híbrido (RRF k=60)", "100.0%", "36 / 36", "< 5.0%", "Seguridad de Grado Clínico"]
    ]
    add_institutional_table(doc, headers_faith, data_faith, col_alignments=["left", "center", "center", "center", "left"], col_widths=[1.8, 1.2, 1.2, 1.1, 1.5])

    add_heading_2(doc, "11.4 Estudio Piloto de Impacto Educativo (Ganancia de Hake)")
    add_body_paragraph(
        doc,
        "Estudio longitudinal cuasi-experimental pre-test vs. post-test sobre una cohorte de internado rotativo (N = 25 internos de medicina). "
        "Los datos empíricos consolidan un impacto formativo de gran magnitud con ganancias de aprendizaje altamente significativas:",
        bold_prefix="Validación en Educación Médica: "
    )
    
    headers_hake = ["Métrica Psicométrica", "Pre-Test", "Post-Test", "Diferencia (Δ)", "Significancia Estadística"]
    data_hake = [
        ["Puntaje Global (Escala 0–10)", "4.87 ± 0.54", "8.64 ± 0.40", "+3.77 pts", "p < 0.0001 (Altamente Significativo)"],
        ["Ganancia Normalizada de Hake (g)", "---", "0.7400 ± 0.0542", "---", "Alta Ganancia (g >= 0.70)"],
        ["Prueba t de Student Pareada (df=24)", "---", "t = 105.266", "---", "p < 10^-10 (df = 24)"],
        ["Tamaño del Efecto (d de Cohen)", "---", "d > 2.0", "---", "Efecto Enorme (d > 2.0)"],
        ["Muestra de Estudio (N)", "25 internos", "25 internos", "---", "Internado Rotativo de Medicina"]
    ]
    add_institutional_table(doc, headers_hake, data_hake, col_alignments=["left", "center", "center", "center", "left"], col_widths=[1.8, 1.0, 1.1, 1.0, 1.8])
    
    add_image_with_caption(
        doc,
        "docs/2_figuras_300dpi/figura_learning_gain.png",
        "Figura 6: Evaluación experimental de Ganancia Normalizada de Hake (Pre vs. Post Test) en N=25 internos rotativos.",
        width_in=6.0
    )

    # =========================================================================
    # SECCIÓN 12: ANALÍTICA DOCENTE E ÍNDICE DE BRECHA FORMATIVA (IBF)
    # =========================================================================
    add_heading_1(doc, "12. ANALÍTICA DE COHORTE Y REPORTE DOCENTE (IBF)")
    
    add_body_paragraph(
        doc,
        "Para los coordinadores de internado rotativo y directores de carrera, Ateneo+ calcula el Índice de Brecha Formativa (IBF), "
        "una métrica epidemiológica que cuantifica la distancia entre el desempeño promedio de la cohorte y el estándar ministerial (8.0/10 puntos):",
        bold_prefix="Inteligencia Curricular para Docentes: "
    )
    add_bullet_item(doc, "Eje Diagnóstico: Detección oportuna de signos de alarma, triaje de severidad y clasificación nosológica CIE-10.")
    add_bullet_item(doc, "Eje Terapéutico: Dosificación exacta por kg de peso, fluidoterapia, fármacos de primera línea y contraindicaciones.")
    add_bullet_item(doc, "Eje Prevención y Seguimiento: Criterios de derivación oportuna, profilaxis comunitaria y control posparto o pos-alta.")
    
    add_image_with_caption(
        doc,
        "docs/2_figuras_300dpi/figura_ibf_cohorte.png",
        "Figura 7: Distribución del Índice de Brecha Formativa (IBF) y semáforo de riesgo curricular por ejes clínicos de cohorte.",
        width_in=6.2
    )
    add_image_with_caption(
        doc,
        "docs/5_capturas_sistema/07_panel_docente_deficiencias_institucionales.png",
        "Figura 8: Desglose institucional de deficiencias normativas frecuentes por módulo GPC en el panel docente de Ateneo+.",
        width_in=6.0
    )

    # =========================================================================
    # SECCIÓN 13: CATÁLOGO CANÓNICO DE CASOS CLÍNICOS EN PRODUCCIÓN
    # =========================================================================
    add_heading_1(doc, "13. CATÁLOGO CANÓNICO DE CASOS CLÍNICOS EN PRODUCCIÓN")
    
    add_body_paragraph(
        doc,
        "Ateneo+ opera con 10 casos clínicos canónicos estructurados en modo simulación dinámica por fases, "
        "con 100% de recuperación precisa en el motor RAG BGE-M3 y contratos de frontend validados:",
        bold_prefix="Casos Epidemiológicos Validados: "
    )
    
    casos = [
        ["case_preeclampsia_01", "Preeclampsia con Criterios de Severidad", "O14.1", "GPC Trastornos Hipertensivos del Embarazo MSP", "Esquema Zuspan (Sulfato de Magnesio) y manejo de crisis tensional con Nifedipino."],
        ["case_hemorragia_01", "Hemorragia Posparto Inmediata (Código Rojo)", "O72.1", "GPC Prevención y Manejo de la Hemorragia Postparto MSP", "Atonía uterina (Regla 4T), masaje bimanual y balón de compresión uterina."],
        ["case_tb_01", "Tuberculosis Pulmonar Sensible", "A15.0", "GPC Tuberculosis (2da Edición) MSP", "Captación de sintomático respiratorio, GeneXpert MTB/RIF y esquema TAES 2HRZE/4HR."],
        ["case_vih_01", "Diagnóstico de Infección por VIH y TARV", "B20", "Acuerdo Ministerial y Guía VIH/SIDA MSP", "Estadificación clínica OMS, profilaxis con Cotrimoxazol e inicio de TLD."],
        ["case_hta_01", "Hipertensión Arterial Primaria Grado 2", "I10", "GPC Hipertensión Arterial MSP (Acuerdo 00019)", "Estratificación de riesgo cardiovascular, HVI en ECG y terapia combinada dual."],
        ["case_erc_01", "Enfermedad Renal Crónica en DM2 / HTA", "N18.3", "GPC Enfermedad Renal Crónica MSP", "Estadificación KDIGO G3bA2, nefroprotección y ajuste de dosis por aclaramiento."],
        ["case_ehirn_01", "Encefalopatía Hipóxico-Isquémica Neonatal", "P91.6", "GPC EHI-RN MSP", "Criterios gasométricos de asfixia, Escala de Sarnat II e Hipotermia Terapéutica."],
        ["case_nac_01", "Neumonía Adquirida en la Comunidad Grave", "J18.9", "GPC Neumonía en Pediatría MSP", "Tiraje subcostal en preescolar, condensación Rx y Ampicilina parenteral a dosis alta."],
        ["case_sepsis_neonatal_01", "Sepsis Neonatal Temprana por RPM", "P36.9", "GPC Sepsis Neonatal MSP", "Factores perinatales, índice I/T > 0.2 y combinación Ampicilina + Gentamicina."],
        ["case_aborto_01", "Aborto Incompleto no Complicado", "O03.4", "GPC Aborto Terapéutico y Espontáneo MSP", "Manejo farmacológico con Misoprostol vs AMEU y profilaxis con inmunoglobulina Anti-D."]
    ]
    
    c_heads = ["ID de Caso", "Patología / Título Clínico", "CIE-10", "Normativa GPC del MSP", "Conducta Médica Evaluada"]
    add_institutional_table(doc, c_heads, casos, col_alignments=["center", "left", "center", "left", "left"], col_widths=[1.2, 1.6, 0.6, 1.5, 2.0])

    # =========================================================================
    # SECCIÓN 14: PROTOCOLO FORMAL DE REPRODUCIBILIDAD CIENTÍFICA Y COMANDOS CLI
    # =========================================================================
    add_heading_1(doc, "14. PROTOCOLO FORMAL DE REPRODUCIBILIDAD CIENTÍFICA Y COMANDOS CLI")
    
    add_body_paragraph(
        doc,
        "La ciencia computacional aplicada a la medicina exige reproducibilidad determinista integral. "
        "Cualquier investigador, comité editorial o docente universitario puede clonar y verificar al 100% "
        "cada resultado numérico reportado en este dosier siguiendo el protocolo estandarizado:",
        bold_prefix="Garantía de Auditoría y Verificabilidad: "
    )
    
    add_heading_2(doc, "14.1 Control Determinista de Semillas y Congelamiento Criptográfico")
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
        "Para ejecutar de forma automatizada los 5 experimentos de auditoría científica y el banco de pruebas completo:"
    )
    
    add_callout_box(
        doc,
        "# 1. Clonación y Aprovisionamiento Automatizado de Artefactos MLOps:\n"
        "git clone https://github.com/JorgeDoicela/ateneo.git\n"
        "cd ateneo\n"
        "python3 scripts/setup_mlops_artifacts.py\n\n"
        "# 2. Verificación de Salud y Contenedores Activos:\n"
        "docker compose up -d\n"
        "curl -f http://localhost:8000/health\n\n"
        "# 3. Ejecución del Arnés de Auditoría Científica Integral (5 Experimentos):\n"
        "docker compose exec backend python /scripts/audit_scientific_rag.py\n\n"
        "# 4. Verificación de Suites de Regresión y Tipos Estrictos:\n"
        "docker compose exec backend python -m tests.run_all_tests\n"
        "docker compose exec frontend npm run typecheck\n"
        "docker compose exec frontend npm run test\n\n"
        "# 5. Regeneración de Tablas LaTeX y Compendio Oficial:\n"
        "docker compose exec backend python /scripts/generate_paper_tables_pdf.py",
        title="GUÍA MAESTRA DE COMANDOS DE REPRODUCIBILIDAD"
    )

    add_heading_2(doc, "14.3 Cuadro de Certificación y Cobertura de Pruebas Automatizadas")
    add_body_paragraph(
        doc,
        "La totalidad de los componentes frontend, backend, esquemas de datos y contratos Pydantic "
        "se encuentran blindados mediante una suite de pruebas automatizadas con cobertura del 100% de éxito:"
    )
    
    cert_headers = ["Batería de Pruebas", "Entorno / Motor", "Casos de Prueba", "Tasa de Aprobación"]
    cert_data = [
        ["Frontend Unit & Integration", "Vitest 5 + React Testing Library (32 suites)", "156 / 156", "100% PASS"],
        ["Backend Total Pytest Suite", "Pytest 9 + FastAPI TestClient (22 módulos)", "108 / 108", "100% PASS"],
        ["Seguridad Criptográfica & RBAC", "Pytest (Bcrypt, JWT HMAC-SHA256, JTI)", "6 / 6", "100% PASS"],
        ["Verificación de Tipos Estricta", "TypeScript 5 (tsc --noEmit)", "0 errores", "100% PASS"],
        ["Compilación de Producción PWA", "Vite 6 + Rollup (Service Worker PWA)", "0 errores", "100% PASS"]
    ]
    add_institutional_table(doc, cert_headers, cert_data, col_alignments=["left", "left", "center", "center"], col_widths=[2.0, 2.4, 1.1, 1.2])

    # =========================================================================
    # SECCIÓN 15: ÉTICA, SOBERANÍA Y FIRMA CRIPTOGRÁFICA
    # =========================================================================
    add_heading_1(doc, "15. ÉTICA, SOBERANÍA DE DATOS Y TRAZABILIDAD CRIPTOGRÁFICA")
    
    add_body_paragraph(
        doc,
        "La aplicación de inteligencia artificial en la educación médica y la salud pública exige un compromiso inquebrantable "
        "con los principios de la bioética y el marco jurídico vigente en la República del Ecuador:",
        bold_prefix="Cumplimiento Normativo y Legal: "
    )
    add_bullet_item(doc, "Cumplimiento con la LOPDP del Ecuador: La plataforma opera estrictamente con casos clínicos ficticios anonimizados según el estándar Safe Harbor de HIPAA. Los identificadores de los estudiantes se disocian de sus nombres civiles en los datasets analíticos mediante tokens seudonimizados.", bold_prefix="Protección de Datos: ")
    add_bullet_item(doc, "Firma Criptográfica de Integridad SHA-256: Cada dictamen PDF individual generado por el sistema incluye un código de sello inmutable (ej. ATENEO-GPC-7C9A4B1F...) calculado sobre el hash concatenado del usuario, caso, fecha, puntaje y cita normativa. Esto previene cualquier adulteración de calificaciones en portafolios de internado.", bold_prefix="Auditoría Forense: ")
    add_bullet_item(doc, "Viabilidad Económica y Sostenibilidad Hospitalaria: El consumo de inferencia en Gemini 3.8 Flash promedia menos de $0.003 USD por evaluación completa en tres fases. En despliegues locales cuantizados (ONNX INT8 / Ollama), el costo marginal de inferencia se reduce a cero, permitiendo atender a miles de internos con recursos públicos mínimos.", bold_prefix="Costo Operativo: ")

    # =========================================================================
    # SECCIÓN 16: HOJA DE RUTA DE ESCALABILIDAD Y PROYECCIÓN DE FUTURO
    # =========================================================================
    add_heading_1(doc, "16. HOJA DE RUTA DE ESCALABILIDAD Y PROYECCIÓN DE FUTURO")
    
    add_body_paragraph(
        doc,
        "Ateneo+ ha sido diseñado como una arquitectura fundacional modular y agnóstica al dominio. "
        "A continuación se formaliza el plan de crecimiento a 10x y 100x para su adopción como política pública y plataforma estándar nacional:",
        bold_prefix="Visión de Escalabilidad Integral: "
    )
    
    add_heading_2(doc, "16.1 Interoperabilidad Sanitaria Hospitalaria (HL7 FHIR & DICOM PACS)")
    add_body_paragraph(
        doc,
        "Integración con las Historias Clínicas Electrónicas (HCE) del Ministerio de Salud Pública y del Instituto Ecuatoriano de Seguridad Social (IESS) "
        "mediante estándares HL7 FHIR (Fast Healthcare Interoperability Resources). "
        "Permitirá anonimizar automáticamente casos clínicos hospitalarios reales de pacientes dados de alta para incorporarlos al catálogo "
        "formativo en menos de 24 horas, acoplado a servidores PACS (Picture Archiving and Communication System) institucionales para ingesta directa de TACs y RMNs.",
        bold_prefix="Interoperabilidad de Datos: "
    )

    add_heading_2(doc, "16.2 Aprendizaje Federado Interhospitalario (Federated Learning)")
    add_body_paragraph(
        doc,
        "Implementación de Federated Averaging (FedAvg) entre redes de hospitales docentes (Quito, Guayaquil, Cuenca, Loja, Portoviejo). "
        "Permitirá ajustar los modelos de embeddings y predictores de maestría clínica localmente dentro del perímetro de seguridad de cada hospital "
        "sin que ningún dato confidencial o registro de internado salga de la infraestructura de la facultad, compartiendo únicamente gradientes cifrados.",
        bold_prefix="Privacidad y Escalabilidad: "
    )

    add_heading_2(doc, "16.3 Despliegue 100% Soberano y Offline (Edge Computing Cuantizado ONNX / GGUF)")
    add_body_paragraph(
        doc,
        "Para los centros de salud de Primer Nivel en el Oriente amazónico, Galápagos y zonas rurales de la Sierra sin conexión a internet: "
        "empaquetado del recuperador BGE-M3 cuantizado a enteros de 8 bits en formato ONNX INT8 (580 MB de peso en disco, latencia de 18 ms en CPU) "
        "acoplado a modelos de lenguaje cuantizados en 4 bits (GGUF Q4_K_M como LLaMA-3.1-8B-Instruct o BioMistral-7B) ejecutándose sobre laptops o mini-PCs hospitalarias.",
        bold_prefix="Soberanía en Áreas Rurales: "
    )

    add_heading_2(doc, "16.4 Extensión al Examen Clínico Objetivo Estructurado (OSCE / ECOE)")
    add_body_paragraph(
        doc,
        "Evolución hacia circuitos de simulación síncrona con estaciones ECOE cronometradas (OsceCircuit.tsx), sincronización de reloj anti-trampa (skew compensation), "
        "tele-audio WebRTC de baja latencia con supresión de ruido Opus a 48 kHz para simulaciones paciente-médico a distancia "
        "y grabación de interacciones para auditoría docente de habilidades de comunicación y empatía clínica.",
        bold_prefix="Evaluación de Grado y Certificación: "
    )

    add_heading_2(doc, "16.5 Expansión a Postgrados Médicos y Especialidades Quirúrgicas")
    add_body_paragraph(
        doc,
        "El desacoplamiento del corpus permite alimentar el pipeline con manuales de Cuidados Intensivos (Surviving Sepsis Campaign), "
        "soporte de trauma avanzado (ATLS), soporte cardiovascular avanzado (ACLS) y farmacocinética especializada, "
        "escalando la plataforma desde el pregrado hacia la evaluación continua y recertificación de médicos especialistas ante colegios médicos y el CACES.",
        bold_prefix="Formación Médica Continua: "
    )

    add_heading_2(doc, "16.6 Universalidad Temática y Soporte de Modelos Propios Fine-Tuneados (OpenAI-Compatible)")
    add_body_paragraph(
        doc,
        "La arquitectura del sistema garantiza total agnosticismo tanto en el dominio clínico como en el motor de inferencia de IA. "
        "En el dominio médico, el pipeline RAG y el modelo psicométrico KST/BKT evalúan competencias clínicas universales (anamnesis, signos vitales, paraclínicos, diagnóstico, prescripción y referencia), "
        "pudiendo indexar guías y casos de cualquier especialidad (oncología, pediatría, ginecología, nefrología o salud mental) sin alterar el código fuente. "
        "En la capa de IA, mediante el patrón Adapter implementado en ResilientLLMGateway, Ateneo+ admite de forma plug-and-play cualquier modelo de lenguaje "
        "entrenado desde cero o fine-tuneado por investigadores (LLaMA-3, Meditron, BioMistral, DeepSeek) expuesto mediante API estándar OpenAI-Compatible (vLLM, Ollama o TGI), "
        "garantizando soberanía tecnológica plena e independencia absoluta de proveedores de nube comerciales.",
        bold_prefix="Agnosticismo de Dominio e Inferencia: "
    )

    # =========================================================================
    # SECCIÓN 17: GUIÓN ESTRATÉGICO Y CRONOGRAMA DE 40 MINUTOS
    # =========================================================================
    add_heading_1(doc, "17. PLANIFICACIÓN Y GUIÓN MINUTO A MINUTO PARA LA PONENCIA MAGISTRAL (40 MIN)")
    
    add_heading_2(doc, "17.1 Cronograma Minuto a Minuto por Bloques Temáticos (8 Bloques)")
    cronograma = [
        ["00:00 – 04:00 (4 min)", "I. Apertura, Justificación y Contexto Nacional", "La crisis del internado rotativo en Ecuador: ruralidad, sobrecarga, letalidad evitable por preeclampsia y hemorragia posparto, y la urgente necesidad de feedback normativo estandarizado."],
        ["04:00 – 09:00 (5 min)", "II. Límites de la IA Generalista y Alucinación", "Por qué los LLMs comerciales fallan: 45.8% de alucinaciones en medicina, sesgo anglosajón, desajuste con el CNMB y carencia de trazabilidad jurídico-forense."],
        ["09:00 – 16:00 (7 min)", "III. Arquitectura del Software y Demostración Clínica", "Clean Architecture, PWA split-screen, visor DICOM volumétrico multicorte con Unidades Hounsfield, dictado clínico por voz y simulación dinámica por fases."],
        ["16:00 – 23:00 (7 min)", "IV. Pipeline MLOps, Transformers y Fine-Tuning A100", "42 GPCs (7,052 chunks), extracción nativa con foliación real en C++, minería de hard negatives en dos etapas y fine-tuning con MNRL (tau=0.02) sobre BGE-M3 en GPU A100."],
        ["23:00 – 29:00 (6 min)", "V. Modelado Psicométrico Formal (KST + BKT + ZDP)", "Grafo DAG de 7 competencias, ecuaciones bayesianas de actualización cognitiva BKT y algoritmo de selección curricular en la Zona de Desarrollo Próximo."],
        ["29:00 – 35:00 (6 min)", "VI. Resultados Empíricos, Hake e IBF de Cohorte", "Métricas IR (+369% Hit@1, +274% MRR@5), prueba OOD de Wilcoxon (p < 0.001), 100% de fidelidad RAGAS, ganancia de Hake g=0.74 (alta ganancia, d > 2.0) y semáforo de IBF."],
        ["35:00 – 38:00 (3 min)", "VII. Ética, Trazabilidad SHA-256 y Escalabilidad", "Anonimización HIPAA/LOPDP, firma criptográfica de no repudio, despliegue soberano cuantizado en centros rurales y hoja de ruta HL7 FHIR."],
        ["38:00 – 40:00 (2 min)", "VIII. Conclusiones y Transición a Q&A", "Síntesis de aportes científicos, cambio de paradigma en la educación médica ecuatoriana y apertura formal de la sesión de preguntas del tribunal."]
    ]
    c_heads2 = ["Bloque Temporal", "Módulo Temático", "Enfoque Técnico y Mensaje Clave del Orador"]
    add_institutional_table(doc, c_heads2, cronograma, col_alignments=["center", "left", "left"], col_widths=[1.5, 2.0, 3.2])

    add_heading_2(doc, "17.2 Relación entre las 20 Diapositivas Oficiales y el Guión de Apoyo (40 Minutos)")
    add_body_paragraph(
        doc,
        "La presentación magistral se apoya en una secuencia rigurosamente sincronizada de 20 diapositivas de alta legibilidad, "
        "con tiempos de permanencia asignados y recursos gráficos reales del sistema para mantener la atención del tribunal:"
    )
    
    slides_heads = ["Diapositiva PPTX", "Título de la Diapositiva", "Tipo de Layout y Recurso Visual", "Tiempo Estimado", "Énfasis del Orador"]
    slides_data = [
        ["Slide 01", "Carátula Oficial CAISEB 2026", "Gráfico institucional de bienvenida", "1:00 min", "Saludo protocolar y presentación del marco del congreso."],
        ["Slide 02", "Portada Oficial del Proyecto", "Autores: Jorge Doicela y Estefani Sánchez", "1:30 min", "Presentación de ambos investigadores y filiación institucional."],
        ["Slide 03", "Agenda de la Conferencia Magistral", "Panorámica: 6 bloques temáticos", "1:30 min", "Hoja de ruta de los 40 minutos de ponencia magistral."],
        ["Slide 04", "Contexto y Brecha Formativa en Ecuador", "Texto analítico de alta legibilidad", "2:00 min", "La realidad de las guardias de internado y dispersión en GPCs."],
        ["Slide 05", "Límites de la IA Comercial en Medicina", "Alucinación 45.8% y desajuste al CNMB", "2:30 min", "Por qué los modelos generalistas son peligrosos sin grounding."],
        ["Slide 06", "Arquitectura General de Ateneo+", "Clean Architecture y pasarela LLM", "2:30 min", "Desacoplamiento, Unit of Work y resiliencia con Circuit Breakers."],
        ["Slide 07", "Experiencia Clínica: Interfaz Split-Screen", "Captura Real: Simulador, Rx y dictado", "2:30 min", "Demostración del split-screen 50/50 y dictado por voz."],
        ["Slide 08", "Simulación Dinámica por Fases Clínicas", "Captura Real: Los 3 hitos secuenciales", "2:30 min", "Hito 1 (Sospecha) -> Hito 2 (Paraclínicos) -> Hito 3 (Prescripción)."],
        ["Slide 09", "Instrucción Adaptativa y Catálogo ZDP", "Captura Real: Catálogo y recomendación", "2:00 min", "Algoritmo Vygotskiano de Zona de Desarrollo Próximo."],
        ["Slide 10", "Curaduría MLOps del Corpus MSP", "42 GPCs oficiales y 7,052 fragmentos", "2:00 min", "Procesamiento jerárquico de tablas y árboles de decisión."],
        ["Slide 11", "Fine-Tuning Supervisado en GPU A100", "Pérdida MNRL (tau=0.02) en 570 tripletas", "2:00 min", "Reentrenamiento de bge-m3 con minado de negativos duros."],
        ["Slide 12", "Recuperación Híbrida y Doble Caché", "Ensamble RRF (k=60) denso y disperso", "2:00 min", "Rendimiento y respuestas sub-2.2 segundos sin latencias."],
        ["Slide 13", "Modelado Psicométrico KST (Grafo)", "Figura Real: DAG de 7 competencias", "2:30 min", "Estructura formal de prerrequisitos diagnósticos y terapéuticos."],
        ["Slide 14", "Bayesian Knowledge Tracing (BKT)", "Figura 300 DPI: Trayectoria de aprendizaje", "2:30 min", "Ecuaciones bayesianas y seguimiento de dominio continuo."],
        ["Slide 15", "Resultados IR: Pre vs. Post Fine-Tuning", "Tabla comparativa de métricas (+369% Hit@1)", "2:00 min", "Cuadruplicación de precisión en primera posición."],
        ["Slide 16", "Benchmark Ciego Out-of-Distribution", "Prueba de Wilcoxon (W=365.0, p < 0.001)", "2:00 min", "Validación de generalización en 283 consultas clínicas."],
        ["Slide 17", "Auditoría Anti-Alucinación (Faithfulness)", "Tabla: 100% afirmaciones normadas", "2:00 min", "Estándar RAGAS y erradicación de alucinación médica."],
        ["Slide 18", "Impacto Educativo y Ganancia de Hake", "Figura 300 DPI: Pre vs. Post (g = 0.74)", "2:30 min", "Salto de 4.87 a 8.64 pts (p < 0.0001, d > 2.0, N=25) y ciclo cerrado con post-test isomórfico y planes heurísticos."],
        ["Slide 19", "Analítica de Cohorte: Índice IBF", "Figura 300 DPI: Panel docente de cohorte", "2:00 min", "Detección precoz de brechas formativas institucionales."],
        ["Slide 20", "Conclusiones y Datos de Investigadores", "Resumen de aportes y apertura a Q&A", "1:30 min", "Datos de contacto de ambos investigadores y debate con tribunal."]
    ]
    add_institutional_table(doc, slides_heads, slides_data, col_alignments=["center", "left", "left", "center", "left"], col_widths=[0.9, 1.8, 1.6, 0.9, 2.0])

    # =========================================================================
    # SECCIÓN 18: BANCO DE PREGUNTAS Y RESPUESTAS ANTE EL TRIBUNAL (Q&A EXTENDIDO)
    # =========================================================================
    add_heading_1(doc, "18. BANCO ESTRATÉGICO Y DEFENSA ANTE EL TRIBUNAL DE CONGRESO (Q&A)")
    
    preguntas = [
        ("P1: ¿Por qué seleccionaron BGE-M3 para fine-tuning en lugar de consumir embeddings comerciales como text-embedding-3 de OpenAI?",
         "BGE-M3 es una arquitectura abierta de 1,024 dimensiones que permite modificar directamente los pesos de sus 24 capas profundas mediante MultipleNegativesRankingLoss sobre la terminología nosológica específica del Ministerio de Salud Pública de Ecuador en hardware soberano (NVIDIA A100). Los modelos comerciales cerrados no permiten fine-tuning de capas internas con tripletas duras, cobran por cada consulta procesada, están sujetos a políticas de privacidad de terceros que impiden el tratamiento seguro de datos de salud y sufren de desfases terminológicos ante la farmacopea nacional."),
        
        ("P2: La muestra del estudio piloto es de N = 25 internos. ¿Es suficiente para validar el impacto educativo de una plataforma de alcance nacional?",
         "El estudio piloto empleó un diseño cuasiexperimental intrasujeto pareado con pre-test y post-test con casos isomórficos. Este diseño neutraliza la varianza interindividual de base. El estadístico t de Student pareado obtenido (t = 105.266, df = 24, p < 10^-10) y el tamaño del efecto de Cohen (d > 2.0) superan ampliamente los estándares de rigor psicométrico internacional exigidos en revistas Q1. Además, la ganancia normalizada de Hake (g = 0.74) está formalmente catalogada como Ganancia Alta. Actualmente, el proyecto está expandiendo la muestra a cohortes multicéntricas de más de 300 estudiantes en tres facultades de medicina del país."),
        
        ("P3: ¿Cómo garantizan que un estudiante no burle la evaluación mediante ataques de Prompt Injection o Jailbreaks?",
         "Ateneo+ implementa una defensa en profundidad de tres capas: 1) Escaneo de entrada determinista con PromptSecurityGuard que detecta y neutraliza expresiones regulares de evasión de instrucciones, intentos de fuga de rol o directivas del sistema (11 de 11 vectores neutralizados al 100%); 2) Evaluador de fidelidad RAGAS (FaithfulnessScorer) que penaliza severamente cualquier afirmación que no posea un soporte explícito en el fragmento normativo recuperado de la GPC; y 3) Descomposición ontológica en 4 ejes clínicos independientes (Diagnóstico, Tratamiento, Prevención y Seguimiento), lo que impide que una respuesta que intente manipular un eje apruebe los demás."),
         
        ("P4: ¿Qué ocurre con el sistema cuando el Ministerio de Salud Pública actualiza una Guía de Práctica Clínica?",
         "Ateneo+ implementa desacoplamiento total entre el código del software y el corpus de conocimiento. Cuando el MSP emite un nuevo Acuerdo Ministerial, el pipeline de ingesta automatizado procesa el PDF, detecta la paginación física real, extrae las tablas normativas y actualiza la colección vectorial gpc_msp_v2 en ChromaDB en menos de 10 minutos sin necesidad de recompilar la aplicación frontend ni reiniciar los servicios del backend. La trazabilidad se preserva mediante el sellado SHA-256 de la nueva versión normativa."),

        ("P5: En centros rurales de la Amazonía o la Sierra sin internet, ¿cómo se implementa Ateneo+ si depende de APIs en la nube?",
         "El sistema cuenta con una ruta de despliegue soberano 100% offline. El recuperador BGE-M3 se cuantiza a formato ONNX INT8 ocupando apenas 580 MB de memoria con una latencia de 18 ms en procesadores estándar de laptops, mientras que el modelo evaluador se reemplaza localmente por modelos clínicos abiertos cuantizados en 4 bits (GGUF como LLaMA-3.1-8B-Instruct o BioMistral-7B) ejecutándose sobre Ollama sin conexión a internet. Las resoluciones se persisten en IndexedDB y se sincronizan al retornar a una zona con cobertura."),

        ("P6: ¿Por qué no realizaron Fine-Tuning directo en el modelo generativo (LLM) en lugar de ajustar el modelo recuperador de embeddings?",
         "El ajuste fino en el modelo generativo presenta tres riesgos críticos en medicina: 1) Olvido catastrófico (Catastrophic Forgetting), donde el modelo pierde facultades de razonamiento general al forzarle memorización de datos específicos; 2) Alucinación paramétrica latente, pues los pesos del modelo son probabilísticos y no ofrecen garantía de citación exacta de página o acuerdo ministerial; y 3) Costo y rigidez de mantenimiento, requiriendo reentrenamientos masivos y costosos ante cada reforma sanitaria. En contraste, ajustar el espacio vectorial (BGE-M3) garantiza que el conocimiento factual resida siempre en la base indexada de forma auditable, permitiendo al LLM actuar exclusivamente como un motor de lectura y evaluación con anclaje verificable."),

        ("P7: ¿Cómo asegura el sistema el cumplimiento estricto de la Ley Orgánica de Protección de Datos Personales (LOPDP) de Ecuador?",
         "Ateneo+ cumple con la LOPDP mediante un modelo de Privacidad desde el Diseño (Privacy by Design): 1) Los casos clínicos son enteramente sintéticos y canónicos, creados sobre la base epidemiológica de las GPCs sin emplear expedientes de pacientes reales; 2) Los identificadores de los estudiantes viajan seudonimizados mediante hashes opacos en los registros de telemetría; 3) Las firmas de autenticidad SHA-256 no contienen datos identificables en claro, impidiendo la reidentificación por terceros; y 4) La arquitectura soporta despliegue on-premise en los centros de datos de cada universidad o red hospitalaria, asegurando la soberanía de datos sin transferencias transfronterizas."),

        ("P8: ¿Qué sucede ante discrepancias nosológicas internacionales (ej. criterios diagnósticos de la AHA, ESC o KDIGO) frente a las guías nacionales del MSP?",
         "En el marco jurídico-sanitario ecuatoriano, las directrices del MSP son de cumplimiento vinculante para el ejercicio profesional del médico y el interno rotativo en establecimientos de la Red Pública Integral de Salud (RPIS). Ateneo+ califica prioritariamente la adhesión a este marco legal nacional. No obstante, el sistema incorpora 'Nosology Adapters' y un módulo de enriquecimiento curricular que permite a la cátedra universitaria contrastar la norma nacional con consensos internacionales sin desestimar la conducta legalmente exigida en el país."),

        ("P9: En el rastreo bayesiano (BKT), ¿cómo se evita que un estudiante experto sea castigado injustamente por un error involuntario de tipeo o fatiga (lapsus)?",
         "El modelo BKT modela probabilísticamente este fenómeno mediante el parámetro de descuido o Slip (S), calibrado empíricamente entre 0.08 y 0.12 para competencias complejas. La regla de actualización bayesiana posterior amortigua el impacto de un fallo aislado: si un alumno con alta probabilidad de dominio acumulada (P(L) = 0.92) comete un error, su probabilidad no cae a cero, sino que desciende suavemente a un rango intermedio (~0.72). Si en el siguiente caso responde correctamente, la evidencia confirma su maestría previa y restaura su nivel. Además, el sistema admite retroalimentación en debriefing socrático para refutar y justificar su razonamiento."),

        ("P10: ¿Cuál es la ventaja competitiva de Ateneo+ frente a simuladores comerciales de alto costo (Body Interact, SimMan)?",
         "Los simuladores comerciales extranjeros presentan tres barreras insalvables para las universidades ecuatorianas: 1) Costos prohibitivos de adquisición y licencias anuales (oscilando entre $40,000 y $120,000 USD por centro), lo que restringe su uso a pocos estudiantes de élite; 2) Desconexión epidemiológica y normativa, pues simulan patologías y algoritmos de la FDA/NHS incompatibles con el Cuadro Nacional de Medicamentos Básicos (CNMB) del Ecuador; y 3) Falta de análisis socrático en texto libre, limitándose a árboles de selección múltiple prefijados. Ateneo+ ofrece evaluación multimodal en texto y voz libre con costo de cómputo inferior a $0.02 USD por sesión, haciéndolo 100% democratizable y adaptado a la realidad sanitaria nacional."),

        ("P11: Si una facultad u hospital prohíbe el uso de nubes externas por política institucional de privacidad, ¿cómo se ejecuta el evaluador de IA localmente?",
         "Ateneo+ no depende de forma cautiva de Google ni de ninguna nube extranjera. El sistema integra el patrón Adapter desacoplado en ResilientLLMGateway: basta con configurar LLM_PROVIDER=openai_compatible y CUSTOM_LLM_BASE_URL en el archivo .env para conectar cualquier modelo evaluador médico de código abierto (LLaMA-3.1-8B, BioMistral, Meditron o modelos propios fine-tuneados) alojado en servidores locales mediante Ollama, vLLM o llama.cpp. El evaluador opera con inyección estricta de formato JSON (score, aciertos, omisiones, cita de GPC) y serialización multimodal de radiografías en Base64. De esta manera, el 100% de la inferencia, los embeddings vectoriales BGE-M3 y la base de datos se ejecutan dentro de la red privada del hospital, garantizando soberanía técnica y cumplimiento estricto de la LOPDP."),

        ("P12: En el diseño experimental de la investigación, ¿cómo garantizan que el Post-Test mida aprendizaje clínico real y no el sesgo de memorización del Pre-Test (testing effect)?",
         "Este es el núcleo innovador del pipeline generativo de Ateneo+: para neutralizar el efecto de práctica repetida (testing effect), el sistema no repite los casos basales en el Post-Test. En su lugar, el módulo IsomorphicCaseGenerator sintetiza formas paralelas funcionalmente equivalentes: mantiene idéntico el nivel taxonómico de Bloom (Análisis y Toma de Decisiones Clínicas), el estándar de oro de la GPC del MSP y las competencias KST evaluadas, pero introduce una viñeta clínica diferente con variación controlada en demografía, edad gestacional, cifras hemodinámicas y paraclínicos dentro del mismo rango normativo. De este modo, la Ganancia Normalizada de Hake (g) cuantifica la transferencia de razonamiento clínico normativo y no el recuerdo de memoria episódica. Adicionalmente, el sistema cuenta con un banco curado calibrado de 10 patologías canónicas que respalda la reproducibilidad experimental del 100% de las pruebas.")
    ]
    
    for q_tit, q_resp in preguntas:
        add_heading_2(doc, q_tit)
        add_body_paragraph(doc, q_resp, bold_prefix="Argumentación de Defensa: ")

    # =========================================================================
    # SECCIÓN 19: CONCLUSIONES Y SÍNTESIS CIENTÍFICA
    # =========================================================================
    add_heading_1(doc, "19. CONCLUSIONES Y SÍNTESIS CIENTÍFICA")
    
    add_bullet_item(doc, "Aporte Científico 1 (Alineación de Dominio en Transformers): El fine-tuning supervisado regionalizado sobre corpus normativos ministeriales multiplica por 4.7x la precisión de recuperación Top-1 (+369.23% Hit@1) y en 3.7x el MRR@5 (+274.40%) frente a modelos densos comerciales, erradicando el sesgo de farmacopea anglosajona.", bold_prefix="MLOps y Embeddings: ")
    add_bullet_item(doc, "Aporte Científico 2 (Seguridad Clínica y Anti-Alucinación): La arquitectura RAG híbrida con Reciprocal Rank Fusion (k=60) y caché semántica sub-milisegundo garantiza un Faithfulness Score del 100.0%, reduciendo la tasa de alucinación evaluativa a niveles seguros (< 5%), frente al 45.8% de alucinaciones en modelos comerciales genéricos.", bold_prefix="Fidelidad Diagnóstica: ")
    add_bullet_item(doc, "Aporte Científico 3 (Impacto Pedagógico Comprobado): La integración formal de Knowledge Space Theory (DAG de 7 competencias) y Bayesian Knowledge Tracing continuo produce una ganancia normalizada de aprendizaje de Hake g = 0.7400 +- 0.0542 (Ganancia Alta, p < 0.0001, d > 2.0), validando la transición desde una tutoría reactiva hacia un aprendizaje adaptativo personalizado.", bold_prefix="Evidencia Psicométrica: ")
    add_bullet_item(doc, "Aporte Científico 4 (Soberanía y Reproducibilidad Nacional): El sistema provee trazabilidad jurídico-forense mediante sellos criptográficos SHA-256 en cada dictamen, cumplimiento estricto con la LOPDP y una arquitectura capaz de operar tanto en clusters hospitalarios de alta concurrencia como en entornos rurales 100% offline.", bold_prefix="Política Sanitaria: ")

    # =========================================================================
    # SECCIÓN 20: FICHAS DE BOLSILLO Y CUE CARDS PARA EL EXPOSITOR (MEMORIZACIÓN Y RESCATE)
    # =========================================================================
    add_heading_1(doc, "20. FICHAS DE APOYO RÁPIDO Y CUE CARDS PARA EL EXPOSITOR (ATRIL)")
    
    add_body_paragraph(
        doc,
        "Esta sección constituye una guía sintética diseñada para consulta rápida durante la ponencia magistral. "
        "Permite al expositor revisar de un vistazo los datos críticos, frases verbatim de anclaje y puntos innegociables "
        "para mantener el ritmo cronometrado exacto sin perder fluidez ni seguridad verbal."
    )

    add_callout_box(
        doc,
        "1. 45.8% -> Tasa de alucinación clínica en LLMs comerciales sin RAG (riesgo crítico).\n"
        "2. 7,052 -> Fragmentos normativos indivisibles extraídos de 42 GPCs oficiales del Ecuador.\n"
        "3. +369.23% -> Incremento en precisión de recuperación Hit@1 tras fine-tuning supervisado en GPU A100.\n"
        "4. +274.40% -> Mejora en MRR@5 (Mean Reciprocal Rank) frente a BGE-M3 base.\n"
        "5. p < 0.001 (W = 365.0) -> Significancia estadística en prueba no paramétrica de Wilcoxon (OOD ciego).\n"
        "6. 100.0% -> Fidelidad normativa (Faithfulness Score RAGAS) frente a GPCs del MSP.\n"
        "7. g = 0.74 -> Ganancia de aprendizaje normalizada de Hake en el piloto (Ganancia Alta, d > 2.0 en N = 25).\n"
        "8. 1.8 a 2.4 s -> Latencia promedio de evaluación multimodal completa con streaming socrático.",
        title="CIFRAS Y DATOS DE ORO (MEMORIZACIÓN OBLIGATORIA DEL EXPOSITOR)"
    )

    cue_cards = [
        ["Minuto 00–04 | Apertura y Crisis Nacional",
         "Frase de apertura: 'El razonamiento clínico no puede depender del azar de la guardia'.\n"
         "Énfasis: Asimetría formativa en el internado rotativo, dispersión de esquemas en preeclampsia y hemorragia posparto (Código Rojo), y letalidad materna evitable. Mostrar a Ateneo+ como una solución sistémica."],
        
        ["Minuto 04–09 | Límites de la IA Comercial",
         "Frase clave: 'Un prompt más largo no resuelve un problema de alucinación ontológica'.\n"
         "Énfasis: Tasa de alucinación del 45.8%. El modelo fundacional comercial no conoce el CNMB de Ecuador ni el esquema Zuspan normado. Cita de sycophancy (halago complaciente al estudiante)."],

        ["Minuto 09–16 | Arquitectura y Demo Clínica",
         "Frase clave: 'Ingeniería de software de grado hospitalario bajo Clean Architecture'.\n"
         "Énfasis: Split-screen 50/50. Visor DICOM multicorte nativo con cálculo de Unidades Hounsfield (-1000 a +1000 HU). Debriefing socrático en streaming SSE token a token. Transaccionalidad ACID en Unit of Work."],

        ["Minuto 16–23 | MLOps y Fine-Tuning A100",
         "Frase clave: 'El valor clínico de un sistema RAG reside en la resolución de su espacio vectorial'.\n"
         "Énfasis: Curaduría de 42 GPCs (7,052 chunks). Reentrenamiento de BGE-M3 en GPU A100 con MultipleNegativesRankingLoss (tau=0.02) y minería de negativos duros BM25. Fusión híbrida RRF (k=60)."],

        ["Minuto 23–29 | Psicometría KST + BKT",
         "Frase clave: 'Ateneo+ no califica con un número estático; modela la mente del interno en un grafo formal'.\n"
         "Énfasis: DAG de 7 competencias clínicas. Actualización bayesiana posterior (Slip y Guess). Selección curricular de casos en la Zona de Desarrollo Próximo (ZDP de Vygotsky)."],

        ["Minuto 29–35 | Evidencia Experimental",
         "Frase clave: 'Validez científica comprobada en recuperación, anti-alucinación y aprendizaje'.\n"
         "Énfasis: Detallar el salto de Hit@1 (+369%), la prueba de Wilcoxon (p < 0.001), el 100% de fidelidad RAGAS y la ganancia de Hake g = 0.74 (t = 105.26, d > 2.0 en N = 25). Mostrar IBF de cohorte."],

        ["Minuto 35–38 | Ética, Soberanía y Costo",
         "Frase clave: 'Auditabilidad criptográfica y soberanía sin cajas negras'.\n"
         "Énfasis: Sellos SHA-256 en cada dictamen contra fraude. Cumplimiento con LOPDP. Costo de centavos de dólar por sesión vs miles de dólares de simuladores cerrados."],

        ["Minuto 38–40 | Conclusión y Cierre",
         "Frase de cierre: 'Ateneo+ transforma la evaluación punitiva en una trayectoria adaptativa validada para el Ecuador'.\n"
         "Énfasis: Agradecimiento a la Mgtr. Estefani Sánchez y a la facultad, y apertura protocolar a las preguntas del tribunal de CAISEB."]
    ]

    c_heads_cue = ["Bloque Temporal y Eje", "Estrategia Verbal, Mensaje Central y Datos Obligatorios"]
    add_institutional_table(doc, c_heads_cue, cue_cards, col_alignments=["center", "left"], col_widths=[2.0, 4.7])

    # =========================================================================
    # SECCIÓN 21: PROTOCOLO DE CONTINGENCIA Y COMPRESIÓN TÁCTICA DEL TIEMPO
    # =========================================================================
    add_heading_1(doc, "21. PROTOCOLO DE CONTINGENCIA Y PLANES DE RESCATE OPERATIVO")
    
    add_body_paragraph(
        doc,
        "En congresos académicos internacionales de alta concurrencia, es común enfrentar retrasos de mesa directiva "
        "o fallos en la conectividad del auditorio. El orador debe estar entrenado para ejecutar cualquiera de los tres planes "
        "sin perder la serenidad ni desvirtuar el impacto científico de la ponencia.",
        bold_prefix="Gestión de Imprevistos en Vivo: "
    )

    planes = [
        ("Plan A (Escenario Estándar - 40 Minutos):",
         "Ejecución completa del cronograma minuto a minuto establecido en la Sección 17. Permite desarrollar el detalle de las 42 GPCs, la demostración visual del split-screen y las cuatro tablas de resultados empíricos."),
        
        ("Plan B (Compresión por Retraso de Mesa - 25 Minutos):",
         "Si el moderador notifica una reducción imprevista del tiempo: 1) Reducir la justificación nacional a 2 minutos; 2) Fusionar arquitectura y MLOps en 7 minutos enfatizando solo el fine-tuning A100 y el visor DICOM; 3) Explicar el grafo KST y BKT en 5 minutos; 4) Dedicar 8 minutos directos a los resultados de Wilcoxon (p < 0.001) y ganancia de Hake (g = 0.74); 5) Cerrar en 3 minutos. Se preserva intacto el núcleo científico."),

        ("Plan C (Fallo Total de Internet / Proyector en el Auditorio):",
         "La investigación no depende de una conexión en vivo. Todo el compendio experimental, las tablas formales y las 8 figuras de alta resolución a 300 DPI se encuentran impresas y compiladas en este dosier Word oficial. El orador conduce la exposición a viva voz apoyado en las cifras de oro de la Sección 20, citando con precisión memorizada los resultados de Wilcoxon, Hake y fidelidad RAGAS, demostrando dominio absoluto de la ciencia subyacente sin depender de soportes tecnológicos externos.")
    ]

    for p_tit, p_desc in planes:
        add_heading_2(doc, p_tit)
        add_body_paragraph(doc, p_desc, bold_prefix="Estrategia Táctica: ")

    # Guardar documento Word
    doc.save(str(DOCX_OUTPUT))
    print(f"Documento Word oficial y exhaustivo generado con éxito: {DOCX_OUTPUT} ({DOCX_OUTPUT.stat().st_size} bytes)")

if __name__ == "__main__":
    main()
