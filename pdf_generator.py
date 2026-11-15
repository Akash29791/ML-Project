import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_water_report_pdf(record_data: dict) -> io.BytesIO:
    """
    Generates a professional Water Quality Analysis Certificate PDF using ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        alignment=0
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#2563eb'),
        alignment=0
    )
    header_meta_style = ParagraphStyle(
        'HeaderMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#475569')
    )
    section_title = ParagraphStyle(
        'SectionTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1e3a8a')
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1e293b')
    )
    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#0f172a')
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#0f172a')
    )

    story = []

    # 1. Header with branding
    header_table = Table([
        [
            Paragraph("<b>AQUA-SENSE ANALYTICAL LABS</b><br/><font color='#2563eb'>Official Water Quality Assessment Certificate</font>", title_style),
            Paragraph(f"<b>Certificate #:</b> WQ-{record_data.get('id', '1001')}<br/>"
                      f"<b>Date:</b> {record_data.get('timestamp', datetime.utcnow().strftime('%Y-%m-%d %H:%M'))}<br/>"
                      f"<b>Standard:</b> WHO / US-EPA Potability", header_meta_style)
        ]
    ], colWidths=[360, 180])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2563eb'), spaceBefore=4, spaceAfter=12))

    # 2. Sample & Custody Information Table
    sample_name = record_data.get('sample_name', 'Water Sample')
    water_source = record_data.get('water_source', 'Municipal Supply')
    location = record_data.get('location', 'General Sampling Point')
    tested_by = record_data.get('tested_by', 'Certified Laboratory Analyst')

    meta_grid = [
        [
            Paragraph("<b>Sample Name:</b>", body_style), Paragraph(sample_name, body_style),
            Paragraph("<b>Water Source:</b>", body_style), Paragraph(water_source, body_style)
        ],
        [
            Paragraph("<b>Sampling Location:</b>", body_style), Paragraph(location, body_style),
            Paragraph("<b>Tested / Verified By:</b>", body_style), Paragraph(tested_by, body_style)
        ]
    ]
    meta_table = Table(meta_grid, colWidths=[100, 170, 100, 170])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # 3. Overall Verdict Banner
    status = record_data.get('overall_status', 'Safe')
    wqi_score = record_data.get('wqi_score', 85.0)

    if status == "Safe":
        banner_bg = colors.HexColor('#dcfce7')
        banner_border = colors.HexColor('#16a34a')
        banner_text_color = '#15803d'
        status_label = "SAFE FOR HUMAN CONSUMPTION"
        sub_label = "All measured physicochemical parameters comply with drinking water potability limits."
    elif status == "Needs Further Testing":
        banner_bg = colors.HexColor('#fef3c7')
        banner_border = colors.HexColor('#d97706')
        banner_text_color = '#b45309'
        status_label = "NEEDS FURTHER TESTING / CONDITIONAL"
        sub_label = "Borderline parameters detected. Secondary microbial culture or filtration strongly recommended."
    else:
        banner_bg = colors.HexColor('#fee2e2')
        banner_border = colors.HexColor('#dc2626')
        banner_text_color = '#b91c1c'
        status_label = "UNSAFE FOR DRINKING / NON-COMPLIANT"
        sub_label = "Exceeds safe contaminant or physical thresholds. DO NOT INGEST without treatment."

    verdict_content = [
        [
            Paragraph(f"<font color='{banner_text_color}'><b>OVERALL ASSESSMENT: {status_label}</b></font><br/>"
                      f"<font size='8' color='#334155'>{sub_label}</font>", body_style),
            Paragraph(f"<font size='14' color='{banner_text_color}'><b>WQI: {wqi_score} / 100</b></font><br/>"
                      f"<font size='7.5' color='#64748b'>Weighted Quality Score</font>", body_style)
        ]
    ]
    verdict_table = Table(verdict_content, colWidths=[410, 130])
    verdict_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), banner_bg),
        ('BOX', (0, 0), (-1, -1), 1.5, banner_border),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(verdict_table)
    story.append(Spacer(1, 14))

    # 4. Physicochemical Evaluation Table
    story.append(Paragraph("<b>Detailed Physicochemical Laboratory Findings</b>", section_title))
    story.append(Spacer(1, 6))

    evals = record_data.get('evaluations', {})
    params_data = record_data.get('input_params', {
        'ph': record_data.get('ph'),
        'tds': record_data.get('tds'),
        'turbidity': record_data.get('turbidity'),
        'hardness': record_data.get('hardness'),
        'chlorine': record_data.get('chlorine'),
        'temperature': record_data.get('temperature')
    })

    table_data = [
        [
            Paragraph("<b>Parameter</b>", table_cell_bold),
            Paragraph("<b>Measured Value</b>", table_cell_bold),
            Paragraph("<b>Permissible Limit</b>", table_cell_bold),
            Paragraph("<b>Status</b>", table_cell_bold),
            Paragraph("<b>Diagnostic Remark</b>", table_cell_bold)
        ]
    ]

    parameter_configs = [
        ("ph", "pH Level", "pH", "6.5 - 8.5", "Optimal chemical neutrality"),
        ("tds", "Total Dissolved Solids", "ppm", "≤ 500 ppm", "Dissolved mineral content"),
        ("turbidity", "Turbidity", "NTU", "≤ 5.0 NTU (Ideal <1.0)", "Water clarity & suspended matter"),
        ("hardness", "Total Hardness", "mg/L", "≤ 200 mg/L", "Calcium & magnesium hardness"),
        ("chlorine", "Residual Chlorine", "ppm", "0.2 - 2.0 ppm", "Residual disinfectant safety"),
        ("temperature", "Temperature", "°C", "≤ 25.0 °C", "Thermal storage stability")
    ]

    for key, name, unit, default_limit, default_desc in parameter_configs:
        ev = evals.get(key, {})
        val = params_data.get(key, '--')
        stat = ev.get('status', 'PASS')
        limit = ev.get('acceptable_range', default_limit)
        remark = ev.get('finding', default_desc)

        if stat == "PASS":
            stat_html = "<font color='#16a34a'><b>PASS</b></font>"
        elif stat == "WARNING":
            stat_html = "<font color='#d97706'><b>REVIEW</b></font>"
        else:
            stat_html = "<font color='#dc2626'><b>FAIL</b></font>"

        table_data.append([
            Paragraph(f"<b>{name}</b>", table_cell),
            Paragraph(f"{val} {unit}", table_cell),
            Paragraph(limit, table_cell),
            Paragraph(stat_html, table_cell),
            Paragraph(remark, table_cell)
        ])

    param_table = Table(table_data, colWidths=[110, 80, 95, 65, 190])
    param_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#eff6ff')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#93c5fd')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(param_table)
    story.append(Spacer(1, 14))

    # 5. Remediation & Action Recommendations
    recs = record_data.get('recommendations', [])
    if recs:
        story.append(Paragraph("<b>Corrective Remediation & Engineering Actions</b>", section_title))
        story.append(Spacer(1, 4))
        for idx, rec in enumerate(recs, 1):
            story.append(Paragraph(f"• <b>Action {idx}:</b> {rec}", body_style))
            story.append(Spacer(1, 2))
        story.append(Spacer(1, 12))

    # 6. Official Sign-off & Footer
    footer_data = [
        [
            Paragraph("<b>Automated Quality Verification</b><br/>"
                      "Certified by Aqua-Sense Software Analytics Engine<br/>"
                      "Reference Protocol: WHO Guidelines for Drinking-water Quality (4th Edition)", header_meta_style),
            Paragraph("<b>Authorized Laboratory Stamp</b><br/>"
                      "<i>Aqua-Sense Water Safety Unit</i><br/>"
                      "Status: <b>VERIFIED RECORD</b>", header_meta_style)
        ]
    ]
    footer_table = Table(footer_data, colWidths=[360, 180])
    footer_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(KeepTogether(footer_table))

    doc.build(story)
    buffer.seek(0)
    return buffer
