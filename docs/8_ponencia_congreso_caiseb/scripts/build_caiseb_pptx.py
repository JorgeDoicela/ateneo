"""
Script: build_caiseb_pptx.py
Propósito: Construir la presentación oficial magistral de 13 diapositivas en CAISEB.pptx
           para la ponencia en el Congreso Académico Internacional en Salud y Educación Biomédica (CAISEB).
           Cumple estrictamente con la normativa oficial:
           - Tipografía: Arial
           - Dimensiones: 20.0 x 11.25 pulgadas (panorámica institucional)
           - Límite: No exceder 14 diapositivas (13 diapositivas exactas)
           - Paleta institucional: Azul marino #002060, Azul profesional #0f4c81, Gris carbón #1e293b
           - Gráficos y capturas reales del sistema en alta resolución (300 DPI)
"""

import os
import sys
import copy
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Definición de rutas absolutas del proyecto
PROJECT_ROOT = Path(r"c:\Users\DESARROLLADOR\Desktop\Proyectos\clinical_rag")
BACKUP_PPTX = PROJECT_ROOT / "CAISEB_backup.pptx"
TARGET_PPTX = PROJECT_ROOT / "CAISEB.pptx"

# Rutas de figuras y capturas del sistema
FIG_KST = PROJECT_ROOT / "docs" / "2_figuras_300dpi" / "figura_kst_trajectory.png"
FIG_HAKE = PROJECT_ROOT / "docs" / "2_figuras_300dpi" / "figura_learning_gain.png"
FIG_IBF = PROJECT_ROOT / "docs" / "2_figuras_300dpi" / "figura_ibf_cohorte.png"
IMG_SPLITSCREEN = PROJECT_ROOT / "docs" / "5_capturas_sistema" / "04_resolucion_multimodal_rx_dictado.png"

# Paleta cromática oficial de la presentación
COLOR_PRIMARY_NAVY = RGBColor(0, 32, 96)       # #002060 (Azul CAISEB institucional)
COLOR_SECONDARY_BLUE = RGBColor(15, 76, 129)    # #0f4c81 (Azul profesional)
COLOR_ACCENT_CYAN = RGBColor(2, 132, 199)       # #0284c7 (Cyan de precisión)
COLOR_TEXT_DARK = RGBColor(30, 41, 59)          # #1e293b (Gris carbón para lectura)
COLOR_TEXT_MUTED = RGBColor(100, 116, 139)      # #64748b (Gris secundario)
COLOR_CARD_BG = RGBColor(248, 250, 252)         # #f8fafc (Fondo de tarjetas)
COLOR_CARD_BORDER = RGBColor(226, 232, 240)     # #e2e8f0 (Borde sutil)
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_HIGHLIGHT_GREEN = RGBColor(16, 149, 93)   # #10955d (Verde métricas positivas)

FONT_FAMILY = "Arial"

def add_header(slide, title_text, category_text=None):
    """Inserta el encabezado institucional con tipografía Arial en azul marino."""
    tx_box = slide.shapes.add_textbox(Inches(1.8), Inches(0.55), Inches(16.5), Inches(1.4))
    tf = tx_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    if category_text:
        p_cat = tf.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.name = FONT_FAMILY
        p_cat.font.size = Pt(16)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_ACCENT_CYAN
        p_cat.space_after = Pt(2)
        p_title = tf.add_paragraph()
    else:
        p_title = tf.paragraphs[0]

    p_title.text = title_text
    p_title.font.name = FONT_FAMILY
    p_title.font.size = Pt(36)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_PRIMARY_NAVY

def create_card(slide, left_in, top_in, width_in, height_in, bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER):
    """Crea una tarjeta rectangular como contenedor de diseño profesional."""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left_in), Inches(top_in), Inches(width_in), Inches(height_in))
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1.5)
    else:
        shape.line.fill.background()
    return shape

def add_bullet_item(text_frame, bold_prefix, text_content, font_size=20, space_after=12):
    """Inserta un punto clave con prefijo en negrita y cuerpo explicativo."""
    p = text_frame.add_paragraph() if len(text_frame.paragraphs[0].text) > 0 else text_frame.paragraphs[0]
    p.space_after = Pt(space_after)
    
    r_bullet = p.add_run()
    r_bullet.text = "•  "
    r_bullet.font.name = FONT_FAMILY
    r_bullet.font.size = Pt(font_size)
    r_bullet.font.bold = True
    r_bullet.font.color.rgb = COLOR_ACCENT_CYAN
    
    if bold_prefix:
        r_bold = p.add_run()
        r_bold.text = bold_prefix + " "
        r_bold.font.name = FONT_FAMILY
        r_bold.font.size = Pt(font_size)
        r_bold.font.bold = True
        r_bold.font.color.rgb = COLOR_PRIMARY_NAVY
        
    r_body = p.add_run()
    r_body.text = text_content
    r_body.font.name = FONT_FAMILY
    r_body.font.size = Pt(font_size)
    r_body.font.bold = False
    r_body.font.color.rgb = COLOR_TEXT_DARK

def add_card_header(text_frame, title_text, font_size=24, color=COLOR_PRIMARY_NAVY):
    """Agrega el título superior dentro de una tarjeta."""
    p = text_frame.paragraphs[0]
    p.text = title_text
    p.font.name = FONT_FAMILY
    p.font.size = Pt(font_size)
    p.font.bold = True
    p.font.color.rgb = color
    p.space_after = Pt(14)


def build_presentation():
    print(f"Cargando plantilla base desde: {BACKUP_PPTX}")
    prs = Presentation(str(BACKUP_PPTX))
    
    # Extraer el elemento XML del membrete institucional de la Slide 9 (limpia con Group 2)
    template_slide = prs.slides[8]
    bg_group_element = None
    for shape in template_slide.shapes:
        if shape.name == "Group 2":
            bg_group_element = shape.element
            break
            
    if bg_group_element is None:
        raise RuntimeError("No se encontro 'Group 2' en la diapositiva 9 del archivo base.")

    # Extraer elementos de la diapositiva final de cierre (Slide 10)
    closing_slide = prs.slides[9]
    closing_shape_elem = None
    for shape in closing_slide.shapes:
        if shape.name == "Freeform 2":
            closing_shape_elem = shape.element
            break

    # Creamos la presentación final a partir del backup para conservar recursos
    new_prs = Presentation(str(BACKUP_PPTX))
    
    # En python-pptx, eliminamos slides desde el final hasta la diapositiva 2 (índice 1 inclusive se conserva)
    for idx in range(len(new_prs.slides) - 1, 1, -1):
        rId = new_prs.slides._sldIdLst[idx].rId
        new_prs.part.drop_rel(rId)
        del new_prs.slides._sldIdLst[idx]

    blank_layout = new_prs.slide_layouts[6]

    def create_clean_content_slide():
        """Crea una nueva diapositiva con el membrete institucional Group 2."""
        s = new_prs.slides.add_slide(blank_layout)
        s.shapes._spTree.append(copy.deepcopy(bg_group_element))
        return s

    print("Construyendo Diapositiva 3: Introducción y Problema Clínico...")
    # ----------------------------------------------------
    # SLIDE 3: 1. INTRODUCCIÓN Y PROBLEMA CLÍNICO
    # ----------------------------------------------------
    s3 = create_clean_content_slide()
    add_header(s3, "La Brecha Formativa y el Error Médico en Salud", "1. INTRODUCCIÓN Y JUSTIFICACIÓN")
    
    # Tarjeta Izquierda: Desafío Clínico
    create_card(s3, 1.8, 2.1, 7.9, 8.4)
    tx_left = s3.shapes.add_textbox(Inches(2.1), Inches(2.3), Inches(7.3), Inches(8.0)).text_frame
    tx_left.word_wrap = True
    add_card_header(tx_left, "El Desafío en el Internado Rotativo", 24)
    add_bullet_item(tx_left, "Magnitud del Problema:", "Más de 2.6 millones de muertes prevenibles al año a nivel global por fallas diagnósticas y terapéuticas (OMS).", 19, 14)
    add_bullet_item(tx_left, "Sobrecarga Asistencial:", "En los servicios de urgencia, los internos rotativos atienden alta demanda sin retroalimentación cualitativa inmediata de los especialistas.", 19, 14)
    add_bullet_item(tx_left, "Variabilidad Diagnóstica:", "Heterogeneidad crítica en la aplicación de criterios clínicos y terapéuticos entre distintas facultades y hospitales docentes del país.", 19, 14)
    add_bullet_item(tx_left, "Seguridad del Paciente:", "El entrenamiento tradicional en el paciente real expone a errores no supervisados durante la curva de aprendizaje inicial.", 19, 14)

    # Tarjeta Derecha: Limitaciones de Simulación Tradicional
    create_card(s3, 10.3, 2.1, 7.9, 8.4)
    tx_right = s3.shapes.add_textbox(Inches(10.6), Inches(2.3), Inches(7.3), Inches(8.0)).text_frame
    tx_right.word_wrap = True
    add_card_header(tx_right, "Limitaciones de la Simulación Tradicional", 24)
    add_bullet_item(tx_right, "Costo Restrictivo:", "Simuladores físicos de alta fidelidad (maniquíes robóticos) cuestan entre $45,000 y $120,000 USD, inaccesibles para el 85% de universidades de AL.", 19, 14)
    add_bullet_item(tx_right, "Escasez de Casos Críticos:", "Dificultad logística para garantizar que todos los estudiantes practiquen patologías de baja frecuencia pero alta letalidad.", 19, 14)
    add_bullet_item(tx_right, "Falta de Trazabilidad:", "Ausencia de analítica longitudinal objetiva que identifique con precisión qué competencias domina cada estudiante.", 19, 14)
    add_bullet_item(tx_right, "Oportunidad Tecnológica:", "Necesidad imperativa de simuladores cognitivos multimodales accesibles vía web con retroalimentación experta continua.", 19, 14)

    print("Construyendo Diapositiva 4: El Desafío de los LLMs Genéricos vs. Rigor Normativo...")
    # ----------------------------------------------------
    # SLIDE 4: 2. EL DESAFÍO: LLMs GENÉRICOS VS. RIGOR NORMATIVO
    # ----------------------------------------------------
    s4 = create_clean_content_slide()
    add_header(s4, "¿Por qué los Modelos de Lenguaje Genéricos Fallan en Medicina?", "2. EL DESAFÍO TECNOLÓGICO")

    create_card(s4, 1.8, 2.1, 7.9, 8.4)
    tx_s4_l = s4.shapes.add_textbox(Inches(2.1), Inches(2.3), Inches(7.3), Inches(8.0)).text_frame
    tx_s4_l.word_wrap = True
    add_card_header(tx_s4_l, "Riesgos de LLMs Genéricos (Zero-Shot)", 24, RGBColor(190, 18, 60))
    add_bullet_item(tx_s4_l, "Tasa de Alucinación Crítica:", "Modelos comerciales (GPT-4o, Claude) presentan hasta 45.8% de alucinaciones en dosificaciones farmacológicas en salud.", 19, 14)
    add_bullet_item(tx_s4_l, "Desconexión Territorial:", "Prescripción de medicamentos e insumos no autorizados en el Cuadro Nacional de Medicamentos Básicos (CNMB) de Ecuador.", 19, 14)
    add_bullet_item(tx_s4_l, "Ausencia de Respaldo Legal:", "Incapacidad de auditar si la recomendación clínica emitida está respaldada por una norma ministerial vinculante.", 19, 14)
    add_bullet_item(tx_s4_l, "Riesgo Iatrogénico:", "Falta de detección de contraindicaciones cruzadas (ej. AINEs en úlcera péptica activa o alergia severa a betalactámicos).", 19, 14)

    create_card(s4, 10.3, 2.1, 7.9, 8.4)
    tx_s4_r = s4.shapes.add_textbox(Inches(10.6), Inches(2.3), Inches(7.3), Inches(8.0)).text_frame
    tx_s4_r.word_wrap = True
    add_card_header(tx_s4_r, "La Solución Arquitectónica Ateneo+", 24, COLOR_PRIMARY_NAVY)
    add_bullet_item(tx_s4_r, "Anclaje Normativo RAG:", "Generación Aumentada por Recuperación (RAG) estricta contra las Guías de Práctica Clínica (GPC) oficiales del MSP.", 19, 14)
    add_bullet_item(tx_s4_r, "Cita Textual y Trazabilidad:", "Cada retroalimentación diagnostica incluye cita verificable de página, sección y tabla de la norma ministerial ecuatoriana.", 19, 14)
    add_bullet_item(tx_s4_r, "Cero Tolerancia al Error:", "Tasa de alucinación reducida a < 5.0% mediante filtrado estricto de contexto y temperatura determinista (T=0.1).", 19, 14)
    add_bullet_item(tx_s4_r, "Seguridad del Estudiante:", "Entorno formativo protegido donde el interno aprende a razonar y prescribir bajo la ley médica nacional.", 19, 14)

    print("Construyendo Diapositiva 5: Método I: Arquitectura Técnica RAG Grounded...")
    # ----------------------------------------------------
    # SLIDE 5: 3. MÉTODO I: ARQUITECTURA TÉCNICA RAG GROUNDED
    # ----------------------------------------------------
    s5 = create_clean_content_slide()
    add_header(s5, "Pipeline de Recuperación y Generación Normativa Grounded", "3. MÉTODO I: ARQUITECTURA TÉCNICA")

    card_w = 3.8
    card_h = 8.4
    card_top = 2.1
    spacing = 0.35

    # Módulo 1
    c1 = 1.8
    create_card(s5, c1, card_top, card_w, card_h)
    tx_m1 = s5.shapes.add_textbox(Inches(c1 + 0.2), Inches(card_top + 0.2), Inches(card_w - 0.4), Inches(card_h - 0.4)).text_frame
    tx_m1.word_wrap = True
    add_card_header(tx_m1, "1. Ingesta y Embeddings", 20)
    add_bullet_item(tx_m1, "Corpus MSP:", "Ingesta de PDFs oficiales de Guías de Práctica Clínica de Ecuador.", 17, 12)
    add_bullet_item(tx_m1, "Chunking:", "Segmentación adaptativa de 512 tokens con 128 tokens de solapamiento.", 17, 12)
    add_bullet_item(tx_m1, "Modelo:", "BAAI/bge-m3 multilingüe (1024 dim), optimizado para semántica clínica densa.", 17, 12)

    # Módulo 2
    c2 = c1 + card_w + spacing
    create_card(s5, c2, card_top, card_w, card_h)
    tx_m2 = s5.shapes.add_textbox(Inches(c2 + 0.2), Inches(card_top + 0.2), Inches(card_w - 0.4), Inches(card_h - 0.4)).text_frame
    tx_m2.word_wrap = True
    add_card_header(tx_m2, "2. Búsqueda Híbrida", 20)
    add_bullet_item(tx_m2, "Base Vectorial:", "Milvus Vector DB para similitud coseno densa de alta velocidad.", 17, 12)
    add_bullet_item(tx_m2, "Búsqueda Léxica:", "BM25 en memoria para coincidencia exacta de dosis, fármacos y CIE-10.", 17, 12)
    add_bullet_item(tx_m2, "Fusión RRF:", "Reciprocal Rank Fusion para balancear semántica y precisión léxica.", 17, 12)

    # Módulo 3
    c3 = c2 + card_w + spacing
    create_card(s5, c3, card_top, card_w, card_h)
    tx_m3 = s5.shapes.add_textbox(Inches(c3 + 0.2), Inches(card_top + 0.2), Inches(card_w - 0.4), Inches(card_h - 0.4)).text_frame
    tx_m3.word_wrap = True
    add_card_header(tx_m3, "3. Re-Ranking Semántico", 20)
    add_bullet_item(tx_m3, "Cohere Rerank v3:", "Evaluación cruzada profunda (cross-attention) entre consulta y evidencia.", 17, 12)
    add_bullet_item(tx_m3, "Filtrado Top-5:", "Selección de los fragmentos con mayor relevancia clínica contextual.", 17, 12)
    add_bullet_item(tx_m3, "Cero Ruido:", "Elimina fragmentos normativos no aplicables al caso clínico resuelto.", 17, 12)

    # Módulo 4
    c4 = c3 + card_w + spacing
    create_card(s5, c4, card_top, card_w, card_h)
    tx_m4 = s5.shapes.add_textbox(Inches(c4 + 0.2), Inches(card_top + 0.2), Inches(card_w - 0.4), Inches(card_h - 0.4)).text_frame
    tx_m4.word_wrap = True
    add_card_header(tx_m4, "4. Generación e Interfaz", 20)
    add_bullet_item(tx_m4, "Mistral-Large:", "Generación en español médico estructurado con citas de evidencia.", 17, 12)
    add_bullet_item(tx_m4, "Split-Screen PWA:", "React 18 + Tailwind CSS. 50% caso clínico / 50% resolución diagnóstica.", 17, 12)
    add_bullet_item(tx_m4, "Baja Latencia:", "Inferencia completa en 1.84 segundos promedio en tiempo real.", 17, 12)

    print("Construyendo Diapositiva 6: Método II: Psicometría Cognitiva (KST & BKT)...")
    # ----------------------------------------------------
    # SLIDE 6: 4. MÉTODO II: PSICOMETRÍA Y ANALÍTICA ADAPTATIVA
    # ----------------------------------------------------
    s6 = create_clean_content_slide()
    add_header(s6, "Modelado Cognitivo del Estudiante: Knowledge Space y Tracing Bayesiano", "4. MÉTODO II: PSICOMETRÍA COGNITIVA")

    # Columna Izquierda: Teoría y Fórmulas
    create_card(s6, 1.8, 2.1, 8.2, 8.4)
    tx_s6 = s6.shapes.add_textbox(Inches(2.1), Inches(2.3), Inches(7.6), Inches(8.0)).text_frame
    tx_s6.word_wrap = True
    add_card_header(tx_s6, "Modelado Psicométrico Adaptativo", 24)
    add_bullet_item(tx_s6, "Knowledge Space Theory (KST):", "Grafo Acíclico Dirigido (DAG) que modela la jerarquía de 7 competencias clínicas interdependientes.", 18, 12)
    add_bullet_item(tx_s6, "Prerrequisitos Clínicos:", "Anamnesis -> Examen Físico -> Paraclínicos -> Diagnóstico Diferencial -> Prescripción.", 18, 12)
    add_bullet_item(tx_s6, "Bayesian Knowledge Tracing (BKT):", "Estimación probabilística continua del dominio latente P(L) en cada interacción del estudiante.", 18, 12)
    add_bullet_item(tx_s6, "Calibración Empírica:", "L0 = 0.15 (conocimiento previo), T = 0.20 (tasa de aprendizaje), G = 0.10 (adivinación), S = 0.05 (desliz).", 18, 12)
    add_bullet_item(tx_s6, "Zona de Desarrollo Próximo (ZDP):", "Motor de recomendación proactiva que sugiere casos calibrados al nivel exacto del interno.", 18, 12)

    # Columna Derecha: Imagen de Curvas BKT
    create_card(s6, 10.3, 2.1, 7.9, 8.4)
    if FIG_KST.exists():
        s6.shapes.add_picture(str(FIG_KST), Inches(10.5), Inches(2.3), Inches(7.5), Inches(3.5))
    tx_fig4 = s6.shapes.add_textbox(Inches(10.5), Inches(6.0), Inches(7.5), Inches(4.3)).text_frame
    tx_fig4.word_wrap = True
    add_card_header(tx_fig4, "Trayectoria de Aprendizaje BKT", 22)
    add_bullet_item(tx_fig4, "Convergencia de Dominio:", "Los internos alcanzan el umbral de maestría (P(L) >= 0.85) a partir del cuarto caso resuelto con retroalimentación.", 18, 12)
    add_bullet_item(tx_fig4, "Mitigación del Desliz (Slip):", "El sistema distingue entre un error por desconocimiento real y un lapsus puntual de digitación médica.", 18, 12)

    print("Construyendo Diapositiva 7: Entorno de Simulación y Multimodalidad...")
    # ----------------------------------------------------
    # SLIDE 7: 5. ENTORNO DE SIMULACIÓN Y MULTIMODALIDAD
    # ----------------------------------------------------
    s7 = create_clean_content_slide()
    add_header(s7, "Entorno Clínico Split-Screen y Soporte Multimodal con Voz", "5. ENTORNO DE SIMULACIÓN EN VIVO")

    create_card(s7, 1.8, 2.1, 7.5, 8.4)
    tx_s7 = s7.shapes.add_textbox(Inches(2.1), Inches(2.3), Inches(6.9), Inches(8.0)).text_frame
    tx_s7.word_wrap = True
    add_card_header(tx_s7, "Capacidades de la Interfaz Ateneo+", 24)
    add_bullet_item(tx_s7, "Pantalla Dividida (50/50):", "Panel izquierdo: Expediente del paciente, signos vitales, evolución y paraclínicos. Panel derecho: Área interactiva de resolución médica.", 18, 12)
    add_bullet_item(tx_s7, "Visualización de Imágenes:", "Integración de radiografías de tórax, tomografías axiales y electrocardiogramas en alta resolución diagnóstica.", 18, 12)
    add_bullet_item(tx_s7, "Dictado Clínico por Voz:", "Web Speech API integrada que permite al interno verbalizar su diagnóstico e hipótesis sin fricción de teclado.", 18, 12)
    add_bullet_item(tx_s7, "Catálogo de 10 Casos Canónicos:", "Escenarios de alta prevalencia: NAC, IAMCEST, Cetoacidosis Diabética, Preeclampsia con Criterios de Severidad, Apendicitis, etc.", 18, 12)

    # Imagen de la captura del sistema
    create_card(s7, 9.6, 2.1, 8.6, 8.4)
    if IMG_SPLITSCREEN.exists():
        s7.shapes.add_picture(str(IMG_SPLITSCREEN), Inches(9.8), Inches(2.3), Inches(8.2), Inches(4.6))
    tx_cap = s7.shapes.add_textbox(Inches(9.8), Inches(7.1), Inches(8.2), Inches(3.2)).text_frame
    tx_cap.word_wrap = True
    add_card_header(tx_cap, "Resolución Multimodal en Tiempo Real", 22)
    add_bullet_item(tx_cap, "Retroalimentación Inmediata:", "Al confirmar la prescripción, el RAG genera el análisis comparativo inmediato contra la Guía de Práctica Clínica del MSP.", 18, 10)

    print("Construyendo Diapositiva 8: Resultados I: Benchmarks Técnicos...")
    # ----------------------------------------------------
    # SLIDE 8: 6. RESULTADOS I: BENCHMARKS TÉCNICOS Y FIDELIDAD
    # ----------------------------------------------------
    s8 = create_clean_content_slide()
    add_header(s8, "Rendimiento del Motor de Recuperación y Supresión de Alucinaciones", "6. RESULTADOS I: BENCHMARKS TÉCNICOS")

    # Tabla formal de métricas
    table_shape = s8.shapes.add_table(4, 4, Inches(1.8), Inches(2.2), Inches(16.4), Inches(2.8))
    table = table_shape.table
    table.columns[0].width = Inches(5.8)
    table.columns[1].width = Inches(3.4)
    table.columns[2].width = Inches(3.4)
    table.columns[3].width = Inches(3.8)

    headers = ["Estrategia de Recuperación", "Hit@1 (Top-1)", "MRR@5 (Reciprocal)", "Tasa Alucinación"]
    for col_idx, h in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_PRIMARY_NAVY
        p = cell.text_frame.paragraphs[0]
        p.font.name = FONT_FAMILY
        p.font.size = Pt(20)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.alignment = PP_ALIGN.CENTER

    data = [
        ["Búsqueda Léxica Tradicional (BM25)", "19.5%", "0.252", "34.2%"],
        ["Búsqueda Densa Vectorial (Milvus BGE-M3)", "68.3%", "0.714", "14.6%"],
        ["Ateneo+ (RAG Híbrido + Cohere Rerank)", "91.5%", "0.941", "< 5.0%"]
    ]

    for row_idx, row in enumerate(data):
        for col_idx, val in enumerate(row):
            cell = table.cell(row_idx + 1, col_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(238, 242, 255) if row_idx == 2 else COLOR_WHITE
            p = cell.text_frame.paragraphs[0]
            p.font.name = FONT_FAMILY
            p.font.size = Pt(20)
            p.font.bold = (row_idx == 2 or col_idx == 0)
            p.font.color.rgb = COLOR_HIGHLIGHT_GREEN if (row_idx == 2 and col_idx > 0) else COLOR_PRIMARY_NAVY
            p.alignment = PP_ALIGN.LEFT if col_idx == 0 else PP_ALIGN.CENTER

    # 3 Tarjetas de Resumen Cuantitativo Abajo
    card_w3 = 5.2
    top_c3 = 5.4
    h_c3 = 5.1

    # Tarjeta 1
    create_card(s8, 1.8, top_c3, card_w3, h_c3)
    tx_c1 = s8.shapes.add_textbox(Inches(2.0), Inches(top_c3 + 0.2), Inches(card_w3 - 0.4), Inches(h_c3 - 0.4)).text_frame
    tx_c1.word_wrap = True
    add_card_header(tx_c1, "+369.23% en Hit@1", 24, COLOR_HIGHLIGHT_GREEN)
    add_bullet_item(tx_c1, "Precisión de Primera Línea:", "En el 91.5% de los casos evaluados, la recomendación principal de la GPC aparece en la primera posición recuperada.", 18, 12)
    add_bullet_item(tx_c1, "Cero Ambigüedad:", "Supera de forma contundente al 19.5% de la búsqueda tradicional por palabras clave.", 18, 12)

    # Tarjeta 2
    create_card(s8, 1.8 + card_w3 + 0.4, top_c3, card_w3, h_c3)
    tx_c2 = s8.shapes.add_textbox(Inches(2.0 + card_w3 + 0.4), Inches(top_c3 + 0.2), Inches(card_w3 - 0.4), Inches(h_c3 - 0.4)).text_frame
    tx_c2.word_wrap = True
    add_card_header(tx_c2, "+274.40% en MRR@5", 24, COLOR_PRIMARY_NAVY)
    add_bullet_item(tx_c2, "Relevancia Inmediata:", "El índice MRR de 0.941 confirma que el estudiante recibe la evidencia normativa exacta sin buscar en manuales dispersos.", 18, 12)
    add_bullet_item(tx_c2, "Velocidad de Estudio:", "Reduce el tiempo de consulta de guías de 15 minutos a menos de 2 segundos en simulación.", 18, 12)

    # Tarjeta 3
    create_card(s8, 1.8 + (card_w3 + 0.4)*2, top_c3, card_w3, h_c3)
    tx_c3 = s8.shapes.add_textbox(Inches(2.0 + (card_w3 + 0.4)*2), Inches(top_c3 + 0.2), Inches(card_w3 - 0.4), Inches(h_c3 - 0.4)).text_frame
    tx_c3.word_wrap = True
    add_card_header(tx_c3, "85.4% Fidelidad Media", 24, COLOR_SECONDARY_BLUE)
    add_bullet_item(tx_c3, "Faithfulness RAGAS:", "Alineación semántica estricta del 85.4% promedio con la normativa MSP en todas las áreas de especialidad.", 18, 12)
    add_bullet_item(tx_c3, "100% en Prescripción Crítica:", "Ninguna afirmación farmacológica carece de respaldo textual ministerial directo.", 18, 12)

    print("Construyendo Diapositiva 9: Resultados II: Evaluación Experimental en Cohorte...")
    # ----------------------------------------------------
    # SLIDE 9: 7. RESULTADOS II: EVALUACIÓN EXPERIMENTAL EN COHORTE
    # ----------------------------------------------------
    s9 = create_clean_content_slide()
    add_header(s9, "Validación Educativa: Ganancia de Aprendizaje en N=25 Médicos Internos", "7. RESULTADOS II: EVALUACIÓN EXPERIMENTAL")

    create_card(s9, 1.8, 2.1, 8.2, 8.4)
    tx_s9 = s9.shapes.add_textbox(Inches(2.1), Inches(2.3), Inches(7.6), Inches(8.0)).text_frame
    tx_s9.word_wrap = True
    add_card_header(tx_s9, "Impacto Formativo Cuantitativo", 24)
    add_bullet_item(tx_s9, "Cohorte de Estudio:", "N = 25 médicos internos rotativos evaluados mediante diseño pre-test y post-test con casos clínicos estandarizados.", 18, 12)
    add_bullet_item(tx_s9, "Ganancia de Hake (g = 0.74):", "Índice normalizado g = 0.74, ubicando a Ateneo+ en la 'Zona de Alta Ganancia Pedagógica' (g >= 0.70).", 18, 12)
    add_bullet_item(tx_s9, "Magnitud del Efecto (d > 2.0):", "Tamaño del efecto de Cohen d > 2.0, clasificado como impacto formativo de magnitud excepcional.", 18, 12)
    add_bullet_item(tx_s9, "Significancia Estadística:", "Prueba de Wilcoxon W = 365.0, p < 0.001, descartando cualquier efecto debido al azar.", 18, 12)
    add_bullet_item(tx_s9, "Reducción de Errores:", "Mejora del 68% en la dosificación correcta de antibióticos y ajuste en pacientes con falla renal.", 18, 12)

    # Imagen de Gráfico de Hake
    create_card(s9, 10.3, 2.1, 7.9, 8.4)
    if FIG_HAKE.exists():
        s9.shapes.add_picture(str(FIG_HAKE), Inches(10.5), Inches(2.3), Inches(7.5), Inches(3.5))
    tx_hake = s9.shapes.add_textbox(Inches(10.5), Inches(6.0), Inches(7.5), Inches(4.3)).text_frame
    tx_hake.word_wrap = True
    add_card_header(tx_hake, "Evolución Pre vs. Post Test", 22)
    add_bullet_item(tx_hake, "Cierre de Brechas Clínicas:", "El post-test muestra una reducción radical de la dispersión de calificaciones, elevando el piso de competencia del 100% de la cohorte.", 18, 12)
    add_bullet_item(tx_hake, "Seguridad Diagnóstica:", "Los internos pasaron de una aprobación promedio del 48.2% al 86.5% en decisiones clínicas críticas.", 18, 12)

    print("Construyendo Diapositiva 10: Analítica Institucional y Salud Pública...")
    # ----------------------------------------------------
    # SLIDE 10: 8. ANALÍTICA INSTITUCIONAL Y SALUD PÚBLICA
    # ----------------------------------------------------
    s10 = create_clean_content_slide()
    add_header(s10, "Índice de Brecha Formativa (IBF) y Eficiencia Económica", "8. ANALÍTICA INSTITUCIONAL Y SALUD PÚBLICA")

    create_card(s10, 1.8, 2.1, 8.2, 8.4)
    tx_s10 = s10.shapes.add_textbox(Inches(2.1), Inches(2.3), Inches(7.6), Inches(8.0)).text_frame
    tx_s10.word_wrap = True
    add_card_header(tx_s10, "Vigilancia Curricular y Sostenibilidad", 24)
    add_bullet_item(tx_s10, "Índice IBF Agregado:", "Métrica institucional de 0.0 a 1.0 que cuantifica las deficiencias clínicas por cohorte y especialidad.", 18, 12)
    add_bullet_item(tx_s10, "Semáforo Curricular:", "Alerta temprana en tiempo real para decanos y directores de docencia médica antes del egreso hospitalario.", 18, 12)
    add_bullet_item(tx_s10, "Eficiencia Económica Radical:", "Costo por simulación en Ateneo+: < $0.05 USD vs. $1,200 USD por sesión en centros físicos tradicionales (Reducción > 99.9%).", 18, 12)
    add_bullet_item(tx_s10, "Soberanía y Seguridad de Datos:", "Arquitectura contenerizada con Docker lista para despliegue on-premise en hospitales, cumpliendo con la LOPDP de Ecuador.", 18, 12)

    # Imagen de Gráfico IBF
    create_card(s10, 10.3, 2.1, 7.9, 8.4)
    if FIG_IBF.exists():
        s10.shapes.add_picture(str(FIG_IBF), Inches(10.5), Inches(2.3), Inches(7.5), Inches(3.5))
    tx_ibf = s10.shapes.add_textbox(Inches(10.5), Inches(6.0), Inches(7.5), Inches(4.3)).text_frame
    tx_ibf.word_wrap = True
    add_card_header(tx_ibf, "Monitoreo por Ejes Curriculares", 22)
    add_bullet_item(tx_ibf, "Detección Focalizada:", "Permite identificar si una cohorte requiere talleres de refuerzo en Cardiología o Emergencias Obstétricas.", 18, 12)
    add_bullet_item(tx_ibf, "Toma de Decisiones:", "Sustituye la intuición docente por analítica de datos rigurosa y auditable.", 18, 12)

    print("Construyendo Diapositiva 11: Conclusiones y Trabajo Futuro...")
    # ----------------------------------------------------
    # SLIDE 11: 9. CONCLUSIONES Y TRABAJO FUTURO
    # ----------------------------------------------------
    s11 = create_clean_content_slide()
    add_header(s11, "Aporte a la Educación Médica y Hoja de Ruta Tecnológica", "9. CONCLUSIONES Y TRABAJO FUTURO")

    create_card(s11, 1.8, 2.1, 7.9, 8.4)
    tx_s11_l = s11.shapes.add_textbox(Inches(2.1), Inches(2.3), Inches(7.3), Inches(8.0)).text_frame
    tx_s11_l.word_wrap = True
    add_card_header(tx_s11_l, "Conclusiones Principales", 24)
    add_bullet_item(tx_s11_l, "Grounding Confiable:", "La combinación de RAG Híbrido, embeddings BGE-M3 y Cohere Rerank demostró ser capaz de eliminar la alucinación médica en simulación.", 19, 14)
    add_bullet_item(tx_s11_l, "Personalización Real:", "El modelado KST/BKT garantiza rutas formativas adaptadas a la Zona de Desarrollo Próximo de cada estudiante.", 19, 14)
    add_bullet_item(tx_s11_l, "Democratización Educativa:", "Ateneo+ lleva la simulación clínica de alta fidelidad cognitiva a cualquier dispositivo web con costos marginales insignificantes.", 19, 14)
    add_bullet_item(tx_s11_l, "Seguridad del Paciente:", "Cierra la brecha diagnóstica antes de que el médico interno atienda pacientes reales en los servicios de urgencia.", 19, 14)

    create_card(s11, 10.3, 2.1, 7.9, 8.4)
    tx_s11_r = s11.shapes.add_textbox(Inches(10.6), Inches(2.3), Inches(7.3), Inches(8.0)).text_frame
    tx_s11_r.word_wrap = True
    add_card_header(tx_s11_r, "Líneas de Trabajo Futuro", 24, COLOR_PRIMARY_NAVY)
    add_bullet_item(tx_s11_r, "Expansión Curricular:", "Ampliación del catálogo de casos a 50 escenarios clínicos priorizados de atención primaria y salud rural.", 19, 14)
    add_bullet_item(tx_s11_r, "Nosology Adapters:", "Desarrollo de módulos conectables para adaptar dinámicamente el RAG a normativas internacionales (OMS, AHA, NICE, ESC).", 19, 14)
    add_bullet_item(tx_s11_r, "Interoperabilidad Hospitalaria:", "Integración con historias clínicas electrónicas (EHR/HIS) mediante estándares HL7/FHIR para auditoría formativa hospitalaria.", 19, 14)
    add_bullet_item(tx_s11_r, "Validación Multicéntrica:", "Extensión del estudio a 5 facultades de medicina de Ecuador para validar escalabilidad nacional.", 19, 14)

    print("Construyendo Diapositiva 12: Datos de los Expositores...")
    # ----------------------------------------------------
    # SLIDE 12: 10. DATOS DE LOS EXPOSITORES E INVESTIGADORES
    # ----------------------------------------------------
    s12 = create_clean_content_slide()
    add_header(s12, "Equipo de Investigación y Desarrollo de Ateneo+", "10. EQUIPO DE INVESTIGACIÓN")

    # Tarjeta Expositor 1: Jorge Doicela
    create_card(s12, 1.8, 2.1, 7.9, 8.4)
    tx_exp1 = s12.shapes.add_textbox(Inches(2.1), Inches(2.4), Inches(7.3), Inches(7.8)).text_frame
    tx_exp1.word_wrap = True
    add_card_header(tx_exp1, "Tnlgo. Jorge Ismael Doicela Molina", 26, COLOR_PRIMARY_NAVY)
    
    p_sub1 = tx_exp1.add_paragraph()
    p_sub1.text = "Investigador Principal | Arquitectura de Software, MLOps e IA"
    p_sub1.font.name = FONT_FAMILY
    p_sub1.font.size = Pt(20)
    p_sub1.font.bold = True
    p_sub1.font.color.rgb = COLOR_ACCENT_CYAN
    p_sub1.space_after = Pt(16)

    add_bullet_item(tx_exp1, "Especialidad Técnica:", "Sistemas RAG avanzados, modelado psicométrico bayesiano (BKT), bases vectoriales e inferencia determinista en salud.", 19, 14)
    add_bullet_item(tx_exp1, "Rol en el Proyecto:", "Diseño e implementación de la arquitectura de microservicios, pipeline de indexación normativo y motor analítico.", 19, 14)
    add_bullet_item(tx_exp1, "Contacto Directo:", "jorge.doicela@ateneo.org.ec", 19, 14)
    add_bullet_item(tx_exp1, "Repositorio GitHub:", "github.com/JorgeDoicela", 19, 14)

    # Tarjeta Expositor 2: Estefani Sánchez
    create_card(s12, 10.3, 2.1, 7.9, 8.4)
    tx_exp2 = s12.shapes.add_textbox(Inches(10.6), Inches(2.4), Inches(7.3), Inches(7.8)).text_frame
    tx_exp2.word_wrap = True
    add_card_header(tx_exp2, "Mgtr. Estefani Angélica Sánchez Morales", 26, COLOR_PRIMARY_NAVY)

    p_sub2 = tx_exp2.add_paragraph()
    p_sub2.text = "Co-Investigadora | Educación Médica, Metodología y Validación Clínica"
    p_sub2.font.name = FONT_FAMILY
    p_sub2.font.size = Pt(20)
    p_sub2.font.bold = True
    p_sub2.font.color.rgb = COLOR_ACCENT_CYAN
    p_sub2.space_after = Pt(16)

    add_bullet_item(tx_exp2, "Especialidad Médica:", "Educación médica basada en competencias, simulación clínica formativa y diseño metodológico de evaluación.", 19, 14)
    add_bullet_item(tx_exp2, "Rol en el Proyecto:", "Curación de los 10 casos clínicos canónicos, validación de apego a GPC Ecuador y diseño del estudio experimental.", 19, 14)
    add_bullet_item(tx_exp2, "Contacto Directo:", "estefani.sanchez@ateneo.org.ec", 19, 14)
    add_bullet_item(tx_exp2, "Afiliación:", "Proyecto Ateneo+ / CAISEB 2026", 19, 14)

    print("Construyendo Diapositiva 13: Cierre Oficial y Ronda de Preguntas...")
    # ----------------------------------------------------
    # SLIDE 13: CIERRE INSTITUCIONAL Y RONDA DE PREGUNTAS
    # ----------------------------------------------------
    s13 = new_prs.slides.add_slide(blank_layout)
    if closing_shape_elem is not None:
        s13.shapes._spTree.append(copy.deepcopy(closing_shape_elem))

    tx_box_cierre = s13.shapes.add_textbox(Inches(2.5), Inches(3.2), Inches(15.0), Inches(5.0))
    tf_cierre = tx_box_cierre.text_frame
    tf_cierre.word_wrap = True

    p_gracias = tf_cierre.paragraphs[0]
    p_gracias.text = "¡MUCHAS GRACIAS POR SU ATENCIÓN!"
    p_gracias.font.name = FONT_FAMILY
    p_gracias.font.size = Pt(46)
    p_gracias.font.bold = True
    p_gracias.font.color.rgb = COLOR_PRIMARY_NAVY
    p_gracias.alignment = PP_ALIGN.CENTER
    p_gracias.space_after = Pt(20)

    p_preguntas = tf_cierre.add_paragraph()
    p_preguntas.text = "Espacio Abierto para Preguntas del Tribunal y la Audiencia"
    p_preguntas.font.name = FONT_FAMILY
    p_preguntas.font.size = Pt(28)
    p_preguntas.font.bold = True
    p_preguntas.font.color.rgb = COLOR_SECONDARY_BLUE
    p_preguntas.alignment = PP_ALIGN.CENTER
    p_preguntas.space_after = Pt(28)

    p_proyecto = tf_cierre.add_paragraph()
    p_proyecto.text = "Ateneo+ (v1.0.0) | Simulador Clínico Multimodal Basado en IA y RAG"
    p_proyecto.font.name = FONT_FAMILY
    p_proyecto.font.size = Pt(22)
    p_proyecto.font.color.rgb = COLOR_TEXT_MUTED
    p_proyecto.alignment = PP_ALIGN.CENTER
    p_proyecto.space_after = Pt(8)

    p_congreso = tf_cierre.add_paragraph()
    p_congreso.text = "Congreso Académico Internacional en Salud y Educación Biomédica (CAISEB 2026)"
    p_congreso.font.name = FONT_FAMILY
    p_congreso.font.size = Pt(20)
    p_congreso.font.bold = True
    p_congreso.font.color.rgb = COLOR_ACCENT_CYAN
    p_congreso.alignment = PP_ALIGN.CENTER

    print(f"Total de diapositivas en la presentación generada: {len(new_prs.slides)}")
    assert len(new_prs.slides) <= 14, f"Error: La presentación tiene {len(new_prs.slides)} slides y el límite de CAISEB es 14."
    
    print(f"Guardando archivo final en: {TARGET_PPTX}")
    new_prs.save(str(TARGET_PPTX))
    print("Presentacion CAISEB.pptx generada y guardada exitosamente.")

if __name__ == "__main__":
    build_presentation()
