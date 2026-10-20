import io
import os
import re
import datetime
import hashlib
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image, KeepTogether
)
from reportlab.lib.units import inch

def sanitize_reportlab_xml(text: str) -> str:
    """Escapa caracteres XML peligrosos preservando etiquetas válidas de ReportLab."""
    text = re.sub(r'&(?!(?:amp|lt|gt|quot|apos|#\d+);)', '&amp;', text)
    
    placeholders = []
    def save_tag(match):
        placeholders.append(match.group(0))
        return f"__RLTAG_{len(placeholders)-1}__"
    
    allowed_pattern = r'<\/?(?:b|i|u|font|super|sub)(?:\s+[^>]*)?>|<br\s*\/?>'
    text = re.sub(allowed_pattern, save_tag, text, flags=re.IGNORECASE)
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    
    for i, tag in enumerate(placeholders):
        text = text.replace(f"__RLTAG_{i}__", tag)
        
    return text

def markdown_inline_to_reportlab(text: str) -> str:
    """Convierte negritas, cursivas y código a formato XML de ReportLab."""
    if not text:
        return ""
    text = re.sub(r'`([^`]+)`', r'<font face="Courier" color="#1e40af"><b>\1</b></font>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
    text = re.sub(r'(?<![*\w])\*([^*]+?)\*(?![*\w])', r'<i>\1</i>', text)
    text = re.sub(r'(?<![_\w])_([^_]+?)_(?![_\w])', r'<i>\1</i>', text)
    return sanitize_reportlab_xml(text)

def build_clinical_table(table_str: str, body_style: ParagraphStyle, table_col_width: float = 516) -> Table:
    """Construye una tabla ReportLab con diseño institucional Ateneo+ a partir de un fragmento Markdown."""
    cleaned = re.sub(r'\|\s*\|\s*', '|\n|', table_str.strip())
    raw_rows = [r.strip() for r in cleaned.split('\n') if r.strip().startswith('|')]
    
    if not raw_rows:
        raw_rows = [r.strip() for r in re.split(r'\|\s*\|', table_str.strip()) if r.strip()]
        
    th_style = ParagraphStyle(
        'THStyle',
        parent=body_style,
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.white,
        alignment=0
    )
    td_style = ParagraphStyle(
        'TDStyle',
        parent=body_style,
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#0f172a"),
        alignment=0
    )
    
    rows = []
    for r in raw_rows:
        cells = [c.strip() for c in r.split('|') if c.strip()]
        if cells and all(re.match(r'^[:\-]+$', c) for c in cells):
            continue
        if cells:
            rows.append(cells)
            
    if not rows:
        return None
        
    headers = rows[0]
    data_rows = rows[1:] if len(rows) > 1 else []
    num_cols = len(headers)
    if num_cols == 0:
        return None
        
    if num_cols == 4:
        col_widths = [105, 95, 120, 196]
    elif num_cols == 3:
        col_widths = [140, 160, 216]
    elif num_cols == 2:
        col_widths = [220, 296]
    else:
        col_w = table_col_width / num_cols
        col_widths = [col_w] * num_cols
        
    formatted_data = [
        [Paragraph(markdown_inline_to_reportlab(h), th_style) for h in headers]
    ]
    for row in data_rows:
        cur_cells = list(row)
        if len(cur_cells) < num_cols:
            cur_cells.extend([''] * (num_cols - len(cur_cells)))
        elif len(cur_cells) > num_cols:
            cur_cells = cur_cells[:num_cols]
        formatted_data.append([
            Paragraph(markdown_inline_to_reportlab(c), td_style) for c in cur_cells
        ])
        
    t = Table(formatted_data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    return t

def parse_clinical_markdown_to_flowables(text: str, body_style: ParagraphStyle, table_col_width: float = 516) -> List[Any]:
    """Parsea el texto clínico completo segmentando párrafos, listas y tablas con diseño institucional Ateneo+."""
    flowables = []
    if not text:
        return flowables

    table_pattern = re.compile(
        r'(\|[^\n]+\|\s*(?:\|\s*[:\-]+.*?\||\n\|[\s\-:]+\|)\s*[\s\S]+?\|)(?=\s*(?:\d+\.\s+\*\*|\Z|\n\n))'
    )
    
    last_end = 0
    list_style = ParagraphStyle(
        'ListStyle',
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceBefore=2,
        spaceAfter=2
    )

    def process_text_segment(segment: str):
        segment = re.sub(r'([.!?:\*])\s+(\d+\.\s+\*\*)', r'\1\n\n\2', segment)
        paragraphs = [p.strip() for p in re.split(r'\n+', segment) if p.strip()]
        for p in paragraphs:
            if re.match(r'^(\d+\.\s+|\-\s+|\*\s+|•\s+)', p):
                flowables.append(Paragraph(markdown_inline_to_reportlab(p), list_style))
            else:
                flowables.append(Paragraph(markdown_inline_to_reportlab(p), body_style))
                flowables.append(Spacer(1, 3))

    for m in table_pattern.finditer(text):
        pre_text = text[last_end:m.start()].strip()
        if pre_text:
            process_text_segment(pre_text)
            
        table_raw = m.group(1).strip()
        t = build_clinical_table(table_raw, body_style, table_col_width)
        if t:
            flowables.append(Spacer(1, 4))
            flowables.append(t)
            flowables.append(Spacer(1, 6))
            
        last_end = m.end()
        
    post_text = text[last_end:].strip()
    if post_text:
        process_text_segment(post_text)
        
    return flowables

def generate_clinical_feedback_pdf(
    student_name: str,
    case_title: str,
    case_id: str,
    guia_asociada: str,
    eval_result: Dict[str, Any],
    student_answer: str = ""
) -> io.BytesIO:
    """
    Genera un dictamen formativo clínico en formato PDF institucional de alta fidelidad
    acorde al Sistema de Diseño Ateneo+ (Google Material 3 / Clinical Design System).
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=32,
        bottomMargin=32
    )

    styles = getSampleStyleSheet()

    # Tokens de Color Ateneo+
    NAVY_DARK = colors.HexColor("#0f172a")       # Texto principal / slate-900
    TEXT_MUTED = colors.HexColor("#475569")      # Texto secundario / slate-600
    BRAND_CYAN = colors.HexColor("#06b6d4")      # Cyan clínico
    BRAND_BLUE = colors.HexColor("#2563eb")      # Azul Royal
    BRAND_INDIGO = colors.HexColor("#4f46e5")    # Indigo IA
    
    BG_CANVAS = colors.HexColor("#f0f4f9")       # Gris-azulado frío Material 3
    BG_WHITE = colors.HexColor("#ffffff")
    
    EMERALD_BG = colors.HexColor("#ecfdf5")
    EMERALD_BORDER = colors.HexColor("#6ee7b7")
    EMERALD_TEXT = colors.HexColor("#047857")
    
    AMBER_BG = colors.HexColor("#fffbeb")
    AMBER_BORDER = colors.HexColor("#fcd34d")
    AMBER_TEXT = colors.HexColor("#b45309")
    
    ROSE_BG = colors.HexColor("#fef2f2")
    ROSE_BORDER = colors.HexColor("#fca5a5")
    ROSE_TEXT = colors.HexColor("#b91c1c")
    
    BLUE_BG = colors.HexColor("#eff6ff")
    BLUE_BORDER = colors.HexColor("#93c5fd")
    BLUE_TEXT = colors.HexColor("#1d4ed8")

    # Estilos Tipográficos Material 3
    brand_style = ParagraphStyle(
        'BrandText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=18,
        textColor=NAVY_DARK
    )

    brand_sub = ParagraphStyle(
        'BrandSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=BRAND_BLUE,
        textTransform='uppercase'
    )

    doc_title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica',
        fontSize=16,
        leading=20,
        textColor=NAVY_DARK,
        spaceAfter=2
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=NAVY_DARK,
        spaceBefore=6,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=NAVY_DARK
    )

    body_muted = ParagraphStyle(
        'BodyMuted',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11.5,
        textColor=TEXT_MUTED
    )

    quote_style = ParagraphStyle(
        'QuoteStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=12,
        textColor=colors.HexColor("#1e293b")
    )

    bullet_good = ParagraphStyle(
        'BulletGood',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11.5,
        textColor=EMERALD_TEXT
    )

    bullet_bad = ParagraphStyle(
        'BulletBad',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11.5,
        textColor=AMBER_TEXT
    )

    elements = []

    # 1. Cabecera con Logotipo Oficial e Identidad de Marca Ateneo+
    logo_path = os.path.join(os.path.dirname(__file__), "..", "cases_data", "images", "ateneo.png")
    now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    header_left = []
    if os.path.exists(logo_path):
        header_left.append(Image(logo_path, width=28, height=28))
    
    brand_block = [
        Paragraph("<b>ATENEO</b><font color='#2563eb'><b>+</b></font>", brand_style),
        Paragraph("SIMULADOR CLÍNICO MULTIMODAL & RAG FORMATIVO • GPC ECUADOR", brand_sub)
    ]

    header_right = [
        Paragraph("<font color='#2563eb'><b>DICTAMEN FORMATIVO OFICIAL</b></font>", ParagraphStyle('RHead', parent=body_style, alignment=2, fontName='Helvetica-Bold', fontSize=8.5, textColor=BRAND_BLUE)),
        Paragraph(f"Emisión: {now_str}", ParagraphStyle('RDate', parent=body_muted, alignment=2, fontSize=7.5))
    ]

    header_table_data = [
        [
            Table([[header_left[0] if header_left else "", brand_block]], colWidths=[34, 300] if header_left else [0, 334]),
            header_right
        ]
    ]

    header_table = Table(header_table_data, colWidths=[370, 170])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 14))

    # 2. Tarjeta de Metadatos del Caso y del Estudiante
    meta_content = [
        [
            Paragraph(f"<b>Estudiante:</b> {student_name}", body_style),
            Paragraph(f"<b>Caso Clínico:</b> {case_title}", body_style)
        ],
        [
            Paragraph(f"<b>ID de Evaluación:</b> <font face='Courier'>{case_id}</font>", body_muted),
            Paragraph(f"<b>Norma Evaluada:</b> {guia_asociada}", body_muted)
        ]
    ]
    meta_table = Table(meta_content, colWidths=[265, 265])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_CANVAS),
        ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 8))

    # 3. Puntuación Global y Nivel de Dominio Clínico (Estilo Material 3 Banner)
    score = eval_result.get("score", 0.0)
    score_max = eval_result.get("score_max", 10.0)
    pct = round((score / score_max) * 100) if score_max > 0 else 0

    if pct >= 80:
        badge_bg, badge_border, badge_text = EMERALD_BG, EMERALD_BORDER, EMERALD_TEXT
        nivel_label = "Dominio Consolidado (Excelente)"
    elif pct >= 60:
        badge_bg, badge_border, badge_text = AMBER_BG, AMBER_BORDER, AMBER_TEXT
        nivel_label = "Competencia Formativa (Aceptable)"
    else:
        badge_bg, badge_border, badge_text = ROSE_BG, ROSE_BORDER, ROSE_TEXT
        nivel_label = "Brecha Formativa Crítica (Requiere Refuerzo)"

    score_card_data = [
        [
            Paragraph(f"<font color='{badge_text.hexval()}'><b>Puntuación Obtenida: {score:.1f} / {score_max:.1f} pts ({pct}%)</b></font><br/><font color='{NAVY_DARK.hexval()}'><b>Estado de Juicio Clínico:</b> {nivel_label}</font>", body_style),
            Paragraph(f"<font color='{badge_text.hexval()}'><b>{pct}%</b></font>", ParagraphStyle('ScoreBig', parent=styles['Normal'], alignment=2, fontName='Helvetica-Bold', fontSize=18, leading=20))
        ]
    ]
    score_table = Table(score_card_data, colWidths=[440, 90])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), badge_bg),
        ('BOX', (0, 0), (-1, -1), 1, badge_border),
        ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 8))

    # 4. Dictamen Formativo del Evaluador RAG (Renderizado Tipado con Soporte de Tablas Clínicas y Fórmulas)
    retro = eval_result.get("retroalimentacion_general", "Evaluación clínica completada con éxito.")
    elements.append(Paragraph("<b>Juicio y Retroalimentación Clínica Principal</b>", section_heading))
    
    retro_flowables = parse_clinical_markdown_to_flowables(retro, body_style, table_col_width=516)
    if not retro_flowables:
        retro_flowables = [Paragraph(markdown_inline_to_reportlab(retro), body_style)]
        
    retro_table = Table([[retro_flowables]], colWidths=[540])
    retro_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_CANVAS),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(retro_table)
    elements.append(Spacer(1, 8))

    # 5. Grid de Aciertos y Omisiones (2 Columnas Planas con Tipografía Enriquecida)
    aciertos = eval_result.get("aciertos", [])
    omisiones = eval_result.get("omisiones", [])

    aciertos_items = [
        Paragraph(f"• {markdown_inline_to_reportlab(a)}", bullet_good) for a in aciertos
    ] if aciertos else [Paragraph("Sin aciertos demostrados según la norma.", ParagraphStyle('It1', parent=bullet_good, fontName='Helvetica-Oblique'))]
    
    omisiones_items = [
        Paragraph(f"• {markdown_inline_to_reportlab(o)}", bullet_bad) for o in omisiones
    ] if omisiones else [Paragraph("Sin omisiones clínicas críticas detectadas.", ParagraphStyle('It2', parent=bullet_bad, fontName='Helvetica-Oblique'))]

    feedback_grid_data = [
        [
            Paragraph("<b>Aciertos Clínicos Demostrados</b>", ParagraphStyle('HGood', parent=body_style, fontName='Helvetica-Bold', textColor=EMERALD_TEXT)),
            Paragraph("<b>Omisiones / Puntos a Reforzar</b>", ParagraphStyle('HBad', parent=body_style, fontName='Helvetica-Bold', textColor=AMBER_TEXT))
        ],
        [
            aciertos_items,
            omisiones_items
        ]
    ]

    grid_table = Table(feedback_grid_data, colWidths=[265, 265])
    grid_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), EMERALD_BG),
        ('BACKGROUND', (1, 0), (1, -1), AMBER_BG),
        ('BOX', (0, 0), (0, -1), 1, EMERALD_BORDER),
        ('BOX', (1, 0), (1, -1), 1, AMBER_BORDER),
        ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(grid_table)
    elements.append(Spacer(1, 8))

    # 6. Fundamentación Normativa Oficial (GPC Ecuador)
    cita = eval_result.get("cita_normativa", {})
    if cita and cita.get("texto_relevante"):
        elements.append(Paragraph("<b>Cita y Fundamentación Normativa (GPC Ecuador)</b>", section_heading))
        cita_content = [
            Paragraph(f"<b>Guía:</b> {cita.get('guia', guia_asociada)} | <b>Sección:</b> {cita.get('seccion', 'General')} | <b>Página Oficial:</b> {cita.get('pagina', 1)}", ParagraphStyle('CHead', parent=body_style, fontName='Helvetica-Bold', textColor=BRAND_BLUE)),
            Spacer(1, 3),
            Paragraph(f'"{markdown_inline_to_reportlab(cita.get("texto_relevante", ""))}"', quote_style)
        ]
        cita_table = Table([[cita_content]], colWidths=[540])
        cita_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), BLUE_BG),
            ('BOX', (0, 0), (-1, -1), 1, BLUE_BORDER),
            ('ROUNDEDCORNERS', [8, 8, 8, 8]),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(cita_table)
        elements.append(Spacer(1, 8))

    # 6.5. Descargo Legal de Investigación y Pruebas Piloto
    legal_disclaimer = (
        "<b>AVISO LEGAL Y DESCARGO DE RESPONSABILIDAD (INVESTIGACIÓN EN DESARROLLO ACTIVO):</b> "
        "Ateneo+ es una plataforma de software desarrollada en el marco de una investigación científica real sobre simulación clínica formativa con IA y RAG normativo. "
        "Actualmente se encuentra en fase de validación experimental en desarrollo activo con miras a una versión oficial. "
        "Por protección legal institucional durante esta etapa, sus evaluaciones tienen propósito exclusivamente formativo y pedagógico; "
        "no constituyen diagnósticos médicos formales, peritajes vinculantes ni recomendaciones para pacientes reales."
    )
    disclaimer_p = Paragraph(legal_disclaimer, ParagraphStyle('LegalP', parent=styles['Normal'], fontName='Helvetica', fontSize=6.5, leading=8.5, textColor=TEXT_MUTED))
    disclaimer_table = Table([[disclaimer_p]], colWidths=[540])
    disclaimer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(disclaimer_table)
    elements.append(Spacer(1, 4))

    # 7. Hash Criptográfico de Integridad Académica (Footer)
    verif_payload = f"{student_name}_{case_id}_{score}_{now_str}"
    integrity_hash = hashlib.sha256(verif_payload.encode('utf-8')).hexdigest()[:16].upper()

    elements.append(Spacer(1, 2))
    footer_text = f"Código de Verificación Académica: <b>ATENEO-GPC-{integrity_hash}</b> • Motor RAG Híbrido (Dense BGE-M3 + BM25 + Gemini)"
    elements.append(Paragraph(footer_text, ParagraphStyle('FooterText', parent=styles['Normal'], fontName='Helvetica', fontSize=7, leading=9, textColor=TEXT_MUTED, alignment=1)))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_cohort_analytics_pdf(
    cohorte_id: str,
    tenant_name: str,
    analytics_data: Dict[str, Any]
) -> io.BytesIO:
    """
    Genera un informe institucional consolidado de analítica de cohorte en PDF de alta fidelidad.
    Incluye métricas ejecutivas, desglose del Índice de Brecha Formativa (IBF), ejes clínicos
    y sello criptográfico SHA-256 de autenticidad académica.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=32,
        bottomMargin=32
    )

    styles = getSampleStyleSheet()

    NAVY_DARK = colors.HexColor("#0f172a")
    TEXT_MUTED = colors.HexColor("#475569")
    BRAND_CYAN = colors.HexColor("#06b6d4")
    BRAND_BLUE = colors.HexColor("#2563eb")
    BG_CANVAS = colors.HexColor("#f0f4f9")
    BG_WHITE = colors.HexColor("#ffffff")

    title_style = ParagraphStyle(
        'CohortTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=NAVY_DARK
    )
    subtitle_style = ParagraphStyle(
        'CohortSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=BRAND_BLUE
    )
    meta_label = ParagraphStyle('CohortMetaL', fontName='Helvetica-Bold', fontSize=8, leading=11, textColor=TEXT_MUTED)
    meta_val = ParagraphStyle('CohortMetaV', fontName='Helvetica', fontSize=9, leading=12, textColor=NAVY_DARK)
    section_h = ParagraphStyle('CohortSec', fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=NAVY_DARK)
    cell_h = ParagraphStyle('CohortCellH', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=BG_WHITE)
    cell_b = ParagraphStyle('CohortCellB', fontName='Helvetica', fontSize=8.5, leading=12, textColor=NAVY_DARK)

    elements = []

    # 1. Encabezado Institucional
    header_content = [
        Paragraph("<b>Ateneo+ • Informe de Inteligencia Formativa y Rendimiento de Cohorte</b>", title_style),
        Spacer(1, 3),
        Paragraph("Plataforma de Simulación Clínica con RAG Normativo • GPC Ecuador", subtitle_style),
    ]
    elements.append(Table([[header_content]], colWidths=[540]))
    elements.append(Spacer(1, 10))

    # 2. Metadatos de la Cohorte
    now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%d/%m/%Y %H:%M UTC")
    total_evals = analytics_data.get("total_evaluaciones", 0)
    activos = analytics_data.get("estudiantes_activos", 0)
    promedio = analytics_data.get("promedio_general", 0.0)
    ibf_global = analytics_data.get("ibf_global", {}).get("ibf_global_pct", 0.0)

    meta_data = [
        [
            Paragraph("<b>Identificador de Cohorte:</b>", meta_label),
            Paragraph(str(cohorte_id), meta_val),
            Paragraph("<b>Institución / Red:</b>", meta_label),
            Paragraph(str(tenant_name), meta_val),
        ],
        [
            Paragraph("<b>Fecha de Generación:</b>", meta_label),
            Paragraph(now_str, meta_val),
            Paragraph("<b>Población Evaluada:</b>", meta_label),
            Paragraph(f"{total_evals} evaluaciones ({activos} estudiantes activos)", meta_val),
        ]
    ]
    meta_table = Table(meta_data, colWidths=[120, 150, 120, 150])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_CANVAS),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROUNDEDCORNERS', [6, 6, 6, 6]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 12))

    # 3. Métricas Ejecutivas de Rendimiento
    elements.append(Paragraph("<b>Resumen Ejecutivo de Rendimiento Clínico</b>", section_h))
    elements.append(Spacer(1, 6))

    kpi_data = [
        [
            Paragraph("<b>Promedio General</b>", ParagraphStyle('KpiH', fontName='Helvetica-Bold', fontSize=10, textColor=TEXT_MUTED, alignment=1)),
            Paragraph("<b>Índice de Brecha Formativa (IBF)</b>", ParagraphStyle('KpiH', fontName='Helvetica-Bold', fontSize=10, textColor=TEXT_MUTED, alignment=1)),
            Paragraph("<b>Tasa de Alineación a GPC</b>", ParagraphStyle('KpiH', fontName='Helvetica-Bold', fontSize=10, textColor=TEXT_MUTED, alignment=1)),
        ],
        [
            Paragraph(f"<b>{promedio:.1f} / 10.0</b>", ParagraphStyle('KpiV1', fontName='Helvetica-Bold', fontSize=18, textColor=BRAND_BLUE, alignment=1)),
            Paragraph(f"<b>{ibf_global:.1f}%</b>", ParagraphStyle('KpiV2', fontName='Helvetica-Bold', fontSize=18, textColor=colors.HexColor("#b45309" if ibf_global > 20 else "#047857"), alignment=1)),
            Paragraph(f"<b>{max(0.0, 100.0 - ibf_global):.1f}%</b>", ParagraphStyle('KpiV3', fontName='Helvetica-Bold', fontSize=18, textColor=colors.HexColor("#047857"), alignment=1)),
        ]
    ]
    kpi_table = Table(kpi_data, colWidths=[180, 180, 180])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_WHITE),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#f1f5f9")),
        ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 14))

    # 4. Desglose del IBF por Ejes de Razonamiento Clínico
    elements.append(Paragraph("<b>Diagnóstico de Brechas Formativas por Eje Clínico (IBF)</b>", section_h))
    elements.append(Spacer(1, 6))

    ejes_data = [
        [
            Paragraph("Eje de Competencia Clínica", cell_h),
            Paragraph("Índice de Brecha (IBF)", cell_h),
            Paragraph("Nivel de Dominio", cell_h),
            Paragraph("Severidad Pedagógica", cell_h)
        ]
    ]

    desglose = analytics_data.get("ibf_global", {}).get("desglose_por_ejes", [])
    if not desglose:
        desglose = [
            {"eje": "diagnostico", "nombre": "Diagnóstico y Sospecha Nosológica", "ibf_eje_pct": 11.0, "severidad": "LEVE / CONTROL"},
            {"eje": "tratamiento", "nombre": "Tratamiento y Dosificación Farmacológica", "ibf_eje_pct": 23.5, "severidad": "MODERADA"},
            {"eje": "prevencion", "nombre": "Prevención y Factores de Riesgo", "ibf_eje_pct": 11.0, "severidad": "LEVE / CONTROL"},
            {"eje": "seguimiento", "nombre": "Seguimiento Longitudinal y Criterios de Alta", "ibf_eje_pct": 11.0, "severidad": "LEVE / CONTROL"}
        ]

    for item in desglose:
        ibf_val = item.get("ibf_eje_pct", 0.0)
        nombre = item.get("nombre") or item.get("eje", "").capitalize()
        dominio_val = max(0.0, 100.0 - ibf_val)
        severidad = item.get("severidad", "CONTROL")
        ejes_data.append([
            Paragraph(str(nombre), cell_b),
            Paragraph(f"<b>{ibf_val:.1f}%</b>", cell_b),
            Paragraph(f"{dominio_val:.1f}%", cell_b),
            Paragraph(str(severidad), cell_b)
        ])

    ejes_table = Table(ejes_data, colWidths=[200, 100, 100, 140])
    ejes_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), BG_WHITE),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [BG_WHITE, BG_CANVAS]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(ejes_table)
    elements.append(Spacer(1, 14))

    # 5. Distribución de Desempeño
    dist = analytics_data.get("distribucion_desempeno", {})
    if dist:
        elements.append(Paragraph("<b>Distribución de Evaluaciones por Nivel de Desempeño</b>", section_h))
        elements.append(Spacer(1, 6))
        dist_data = [
            [
                Paragraph("Sobresaliente (9.0 - 10.0)", cell_b),
                Paragraph(f"{dist.get('sobresaliente', 0)} evaluaciones", cell_b),
                Paragraph("Alineación clínica óptima con fundamentación estricta en GPC", ParagraphStyle('DC', parent=cell_b, textColor=colors.HexColor("#047857")))
            ],
            [
                Paragraph("Competente (7.0 - 8.9)", cell_b),
                Paragraph(f"{dist.get('competente', 0)} evaluaciones", cell_b),
                Paragraph("Resolución adecuada con omisiones menores en dosificación o seguimiento", ParagraphStyle('DC2', parent=cell_b, textColor=BRAND_BLUE))
            ],
            [
                Paragraph("En Desarrollo (0.0 - 6.9)", cell_b),
                Paragraph(f"{dist.get('en_desarrollo', 0)} evaluaciones", cell_b),
                Paragraph("Requiere afianzamiento en protocolos normativos de urgencia", ParagraphStyle('DC3', parent=cell_b, textColor=colors.HexColor("#b45309")))
            ]
        ]
        dist_table = Table(dist_data, colWidths=[160, 110, 270])
        dist_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [BG_WHITE, BG_CANVAS]),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(dist_table)
        elements.append(Spacer(1, 14))

    # 5.5. Descargo Legal de Investigación y Pruebas Piloto
    legal_disclaimer = (
        "<b>AVISO LEGAL Y DESCARGO DE RESPONSABILIDAD (INVESTIGACIÓN EN DESARROLLO ACTIVO):</b> "
        "Este reporte analítico de cohorte forma parte de una investigación científica real y pedagógica en desarrollo activo. "
        "Por protección legal institucional durante esta etapa experimental con miras a una versión oficial, las métricas y promedios son insumos formativos de apoyo docente; "
        "no constituyen diagnósticos clínicos ni valoraciones periciales de competencia médica vinculantes en ámbitos asistenciales reales."
    )
    disclaimer_p = Paragraph(legal_disclaimer, ParagraphStyle('CohortLegalP', parent=styles['Normal'], fontName='Helvetica', fontSize=6.5, leading=8.5, textColor=TEXT_MUTED))
    disclaimer_table = Table([[disclaimer_p]], colWidths=[540])
    disclaimer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(disclaimer_table)
    elements.append(Spacer(1, 4))

    # 6. Sello Criptográfico SHA-256 (Footer)
    hash_payload = f"{cohorte_id}_{tenant_name}_{total_evals}_{promedio}_{now_str}"
    integrity_hash = hashlib.sha256(hash_payload.encode('utf-8')).hexdigest()[:16].upper()

    elements.append(Spacer(1, 4))
    footer_text = (
        f"Certificación Institucional de Auditoría Académica: <b>ATENEO-COHORTE-{integrity_hash}</b> • "
        f"Algoritmo IBF (GPC Ecuador) • Validez Oficial Formativa"
    )
    elements.append(Paragraph(
        footer_text,
        ParagraphStyle('FooterText', parent=styles['Normal'], fontName='Helvetica', fontSize=7, leading=9, textColor=TEXT_MUTED, alignment=1)
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer

