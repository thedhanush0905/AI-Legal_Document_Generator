from src.document_reader import read_pdf

pdf_path = "inputs/case_information.pdf"

text = read_pdf(pdf_path)

print("✅ PDF read successfully!")
print(f"Extracted characters: {len(text)}")
print("\n" + text[:3000])