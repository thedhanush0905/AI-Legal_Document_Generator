import textwrap

s = textwrap.dedent("""
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
""").strip()

for i, l in enumerate(s.splitlines()):
    print(f"{i}: {repr(l)}")
