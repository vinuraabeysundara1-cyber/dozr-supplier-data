from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime

# Read the markdown file
with open('DOZR_Google_Ads_Analysis_Summary.md', 'r') as f:
    content = f.read()

# Create PDF
pdf_filename = 'DOZR_Google_Ads_Analysis_Summary.pdf'
doc = SimpleDocTemplate(pdf_filename, pagesize=letter,
                       leftMargin=0.75*inch, rightMargin=0.75*inch,
                       topMargin=0.75*inch, bottomMargin=0.75*inch)

# Container for the 'Flowable' objects
elements = []

# Define styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    textColor=colors.HexColor('#0066cc'),
    spaceAfter=30,
    alignment=TA_CENTER
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=16,
    textColor=colors.HexColor('#0066cc'),
    spaceAfter=12,
    spaceBefore=12
)

# Parse markdown and create PDF content
lines = content.split('\n')
i = 0
while i < len(lines):
    line = lines[i].strip()

    # Skip empty lines
    if not line:
        i += 1
        continue

    # Title
    if line.startswith('# '):
        text = line[2:]
        elements.append(Paragraph(text, title_style))
        elements.append(Spacer(1, 0.2*inch))

    # Headings
    elif line.startswith('## '):
        text = line[3:]
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(text, heading_style))

    elif line.startswith('### '):
        text = line[4:]
        elements.append(Paragraph(f"<b>{text}</b>", styles['Heading3']))

    # Horizontal rules
    elif line.startswith('---'):
        elements.append(Spacer(1, 0.1*inch))

    # Tables - simple detection
    elif line.startswith('|') and '|' in line:
        table_lines = [line]
        i += 1
        # Collect all table rows
        while i < len(lines) and lines[i].strip().startswith('|'):
            table_lines.append(lines[i].strip())
            i += 1

        # Parse table
        table_data = []
        for tline in table_lines:
            if '---' not in tline:  # Skip separator line
                cells = [cell.strip() for cell in tline.split('|')[1:-1]]
                table_data.append(cells)

        if table_data:
            # Create table
            t = Table(table_data)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(t)
            elements.append(Spacer(1, 0.2*inch))
        continue

    # Bullet points
    elif line.startswith('- ') or line.startswith('* '):
        text = line[2:]
        elements.append(Paragraph(f"• {text}", styles['Normal']))

    # Numbered lists
    elif len(line) > 2 and line[0].isdigit() and line[1] == '.':
        text = line[line.index('.')+1:].strip()
        elements.append(Paragraph(f"{line[:line.index('.')+1]} {text}", styles['Normal']))

    # Regular paragraphs
    else:
        if line and not line.startswith('#'):
            # Handle bold text
            text = line.replace('**', '<b>').replace('**', '</b>')
            elements.append(Paragraph(text, styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))

    i += 1

# Add footer
elements.append(PageBreak())
elements.append(Paragraph(f"<i>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>",
                         styles['Normal']))

# Build PDF
try:
    doc.build(elements)
    print(f"✅ PDF created successfully: {pdf_filename}")
except Exception as e:
    print(f"❌ Error creating PDF: {e}")
    import traceback
    traceback.print_exc()
