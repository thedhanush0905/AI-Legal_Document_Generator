import re
import textwrap

raw_html = """
        <div class="affidavit-document-preview">
            <h3>HEADING</h3>
            <h4>JURISDICTION</h4>
            <div style="text-align: center; font-weight: bold; margin-bottom: 1.5rem;">CASE LINE</div>
            
            <div style="margin-bottom: 1rem;">
                <b>Petitioner</b><br/>
                <span style="font-style: italic;">...Petitioner</span>
            </div>
            
            <div class="versus-line">VERSUS</div>
        </div>
"""

# Strip leading whitespace from every single line
clean_html = "\n".join(line.strip() for line in raw_html.strip().splitlines())

for i, l in enumerate(clean_html.splitlines()):
    print(f"{i}: {repr(l)}")
