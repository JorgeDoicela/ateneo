import re
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

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
    """Convierte negritas, cursivas y código a formato ReportLab."""
    # 1. Código inline
    text = re.sub(r'`([^`]+)`', r'<font face="Courier" color="#1e40af"><b>\1</b></font>', text)
    # 2. Negrita
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
    # 3. Cursiva
    text = re.sub(r'(?<![*\w])\*([^*]+?)\*(?![*\w])', r'<i>\1</i>', text)
    text = re.sub(r'(?<![_\w])_([^_]+?)_(?![_\w])', r'<i>\1</i>', text)
    
    return sanitize_reportlab_xml(text)

def build_clinical_table(table_str: str, body_style: ParagraphStyle, table_col_width: float = 520) -> Table:
    """Construye una tabla ReportLab con diseño institucional Ateneo+ a partir de un fragmento Markdown."""
    # Separar filas por | | o saltos de línea
    # Si hay saltos de línea o dobles pipes
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
        # Ignorar fila separadora :---
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
        
    # Ancho de columnas adaptativo
    if num_cols == 4:
        col_widths = [105, 95, 120, 200]
    elif num_cols == 3:
        col_widths = [140, 160, 220]
    elif num_cols == 2:
        col_widths = [220, 300]
    else:
        col_w = table_col_width / num_cols
        col_widths = [col_w] * num_cols
        
    formatted_data = [
        [Paragraph(markdown_inline_to_reportlab(h), th_style) for h in headers]
    ]
    for row in data_rows:
        # Asegurar coincidencia de columnas
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
        # Cabecera Ateneo+ Azul Real / Navy
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

def parse_clinical_markdown_to_flowables(text: str, body_style: ParagraphStyle, table_col_width: float = 520) -> list:
    """Parsea el texto clínico completo segmentando párrafos, listas y tablas con diseño Ateneo+."""
    flowables = []
    
    # Patrón robusto para capturar tablas Markdown completas (tanto multilínea como en línea)
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
        # Separar listas numeradas pegadas en línea
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

test_input = """El estudiante declara no tener conocimiento sobre el caso clínico planteado, omitiendo la conducta diagnóstica y terapéutica inicial de una emergencia obstétrica crítica. En una paciente con gestación de 32 semanas que presenta **presión arterial sistólica (TAS) ≥ 160 mmHg** y/o **presión arterial diastólica (TAD) ≥ 110 mmHg**, asociada a síntomas de irritación cortical (cefalea intensa, fosfenos, hiperreflexia) y dolor en epigastrio en barra, el diagnóstico mandatario es **preeclampsia con criterios de severidad**. El manejo inmediato protocolizado por la normativa comprende: 1. **Estabilización hemodinámica y neuroprotección inmediata:** - Iniciar **sulfato de magnesio** vía intravenosa utilizando el esquema Zuspan para prevenir la aparición de convulsiones eclampsias: - Dosis de ataque: **4 g IV diluidos en solución salina al 0.9% administrados en 20 minutos**. - Dosis de mantenimiento: **1 g/hora IV en infusión continua**. 2. **Terapia antihipertensiva de emergencia:** - El objetivo es reducir la presión arterial de forma segura para evitar hemorragia intracraneal y desprendimiento prematuro de placenta normoinserta. | Fármaco | Dosis Inicial | Vía de Administración | Intervalo / Consideraciones | | :--- | :--- | :--- | :--- | | **Nifedipino** | 10 mg a 20 mg | Oral (no sublingual) | Repetir cada 20 a 30 minutos según respuesta tensional (máx. 60 mg) | | **Hidralazina** | 5 mg | Intravenosa lenta | Repetir dosis de 5-10 mg cada 20-30 minutos (dosis máxima 20 mg) | 3. **Monitoreo de seguridad clínica:** - Vigilar frecuencia respiratoria (> 16 rpm), presencia de reflejo rotuliano y gasto urinario (> 30 mL/h con sonda vesical a permanencia). - Disponer de **gluconato de calcio al 10%** (1 g IV en 10 minutos) como antídoto en caso de signos de intoxicación por magnesio."""

styles = getSampleStyleSheet()
body_style = ParagraphStyle(
    'BodyTextCustom',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=8.5,
    leading=12.5,
    textColor=colors.HexColor("#0f172a")
)

flowables = parse_clinical_markdown_to_flowables(test_input, body_style)
print(f"Total flowables generados: {len(flowables)}")
for idx, f in enumerate(flowables):
    print(f"  [{idx}] Tipo: {type(f).__name__}")
    if isinstance(f, Table):
        print(f"       -> Filas: {len(f._cellvalues)}, Columnas: {len(f._cellvalues[0])}")
        for r_idx, r in enumerate(f._cellvalues):
            print(f"          Fila {r_idx}: {[c.text for c in r]}")
    elif isinstance(f, Paragraph):
        print(f"       -> Texto (primeros 60 cars): {f.text[:60]}")
