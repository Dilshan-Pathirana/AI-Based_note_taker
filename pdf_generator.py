import os
import markdown2
from weasyprint import HTML

def generate_pdf_from_markdown(md_text: str, output_path: str):
    # Convert Markdown to HTML with extras for better formatting
    html_text = markdown2.markdown(md_text, extras=["fenced-code-blocks", "strike", "tables"])

    # Add minimal CSS for styling headers, bold, bullets, etc.
    css = """
    @page { size: A4; margin: 1in; }
    body { font-family: Arial, sans-serif; font-size: 12pt; line-height: 1.5; }
    h1, h2, h3, h4 { color: #003366; margin-bottom: 0.3em; }
    h2 { border-bottom: 1px solid #ccc; padding-bottom: 0.1em; }
    strong { font-weight: bold; }
    ul { margin-left: 1.2em; }
    li { margin-bottom: 0.3em; }
    pre { background: #f4f4f4; padding: 0.5em; }
    code { font-family: Consolas, monospace; background: #f0f0f0; padding: 0.1em 0.3em; }
    """

    html = f"""
    <html>
      <head>
        <meta charset="utf-8" />
        <style>{css}</style>
      </head>
      <body>{html_text}</body>
    </html>
    """

    HTML(string=html).write_pdf(output_path)
