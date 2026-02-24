from datetime import datetime

# Read the markdown file
with open('DOZR_Google_Ads_Analysis_Summary.md', 'r') as f:
    md_content = f.read()

# Simple markdown to HTML converter (basic)
def simple_md_to_html(md_text):
    html = md_text
    # Convert headers
    html = html.replace('### ', '<h3>').replace('\n\n', '</h3>\n\n')
    html = html.replace('## ', '<h2>').replace('\n\n', '</h2>\n\n')
    html = html.replace('# ', '<h1>').replace('\n\n', '</h1>\n\n')
    # Convert bold
    import re
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    # Convert tables (basic)
    lines = html.split('\n')
    html_lines = []
    in_table = False
    for i, line in enumerate(lines):
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                html_lines.append('<table>')
                in_table = True
            if i > 0 and '---' in line:
                continue
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if i == 0 or (i > 0 and '---' not in lines[i-1]):
                row_type = 'th' if (i == 0 or (i > 1 and '---' in lines[i-1])) else 'td'
                html_lines.append('<tr>')
                for cell in cells:
                    html_lines.append(f'<{row_type}>{cell}</{row_type}>')
                html_lines.append('</tr>')
        else:
            if in_table:
                html_lines.append('</table>')
                in_table = False
            html_lines.append(line)
    if in_table:
        html_lines.append('</table>')
    return '\n'.join(html_lines)

html_content = simple_md_to_html(md_content)

# Add CSS styling for better PDF formatting
html_with_style = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            color: #1a1a1a;
            border-bottom: 3px solid #0066cc;
            padding-bottom: 10px;
            margin-top: 30px;
        }}
        h2 {{
            color: #0066cc;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 8px;
            margin-top: 25px;
        }}
        h3 {{
            color: #333;
            margin-top: 20px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            font-size: 14px;
        }}
        th {{
            background-color: #0066cc;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }}
        td {{
            border: 1px solid #ddd;
            padding: 10px;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        strong {{
            color: #0066cc;
        }}
        hr {{
            border: none;
            border-top: 2px solid #e0e0e0;
            margin: 30px 0;
        }}
        ul, ol {{
            margin-left: 20px;
        }}
        li {{
            margin-bottom: 8px;
        }}
        .emoji {{
            font-size: 1.2em;
        }}
        blockquote {{
            border-left: 4px solid #0066cc;
            padding-left: 15px;
            margin-left: 0;
            color: #666;
            font-style: italic;
        }}
    </style>
</head>
<body>
{html_content}
<hr>
<p><em>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
</body>
</html>
"""

# Save HTML version
with open('DOZR_Google_Ads_Analysis_Summary.html', 'w') as f:
    f.write(html_with_style)

print("✅ HTML version saved: DOZR_Google_Ads_Analysis_Summary.html")
print("\n📄 To create PDF:")
print("   1. Open DOZR_Google_Ads_Analysis_Summary.html in your browser")
print("   2. Press Cmd+P (or File > Print)")
print("   3. Select 'Save as PDF' as destination")
print("   4. Save as DOZR_Google_Ads_Analysis_Summary.pdf")

# Try using system command for PDF generation
import subprocess
import sys

print("\n🔄 Attempting to generate PDF using system tools...")

try:
    # Try using wkhtmltopdf if available
    result = subprocess.run(
        ['which', 'wkhtmltopdf'],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("Found wkhtmltopdf, generating PDF...")
        subprocess.run([
            'wkhtmltopdf',
            '--page-size', 'Letter',
            '--margin-top', '0.75in',
            '--margin-right', '0.75in',
            '--margin-bottom', '0.75in',
            '--margin-left', '0.75in',
            'DOZR_Google_Ads_Analysis_Summary.html',
            'DOZR_Google_Ads_Analysis_Summary.pdf'
        ], check=True)
        print("✅ PDF generated successfully: DOZR_Google_Ads_Analysis_Summary.pdf")
    else:
        print("⚠️  wkhtmltopdf not found. Using HTML version.")
        print("   Install with: brew install wkhtmltopdf (for automatic PDF generation)")
except Exception as e:
    print(f"⚠️  Could not auto-generate PDF: {e}")
    print("   Using HTML version - open in browser to print as PDF")
