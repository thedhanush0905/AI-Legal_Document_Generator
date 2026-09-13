import json
import os
import sys

# Ensure UTF-8 stdout on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from src.models import CaseData
from src.template_models import TemplateSpecification
from src.affidavit_models import GeneratedAffidavit
from src.affidavit_generator import generate_affidavit


def main():
    print("========================================")
    print("STEP 4: AFFIDAVIT GENERATION TEST")
    print("========================================\n")

    case_data_file = os.path.join("outputs", "extracted_case_data.json")
    template_file = os.path.join("outputs", "template_specification.json")
    output_affidavit_file = os.path.join("outputs", "generated_affidavit.json")

    # 1. Load outputs/extracted_case_data.json
    print(f"📂 1. Loading CaseData from {case_data_file}...")
    with open(case_data_file, "r", encoding="utf-8") as f:
        case_data_dict = json.load(f)

    # 2. Load outputs/template_specification.json
    print(f"📂 2. Loading TemplateSpecification from {template_file}...")
    with open(template_file, "r", encoding="utf-8") as f:
        template_dict = json.load(f)

    # 3. Validate both using Pydantic
    print("🔍 3. Validating inputs with Pydantic...")
    case_data = CaseData.model_validate(case_data_dict)
    template = TemplateSpecification.model_validate(template_dict)
    print("   ✅ Input models validated successfully.")

    # 4. Generate affidavit
    print("\n⚖️  4. Calling generate_affidavit()...")
    affidavit = generate_affidavit(case_data, template)

    # 5. Validate GeneratedAffidavit using Pydantic
    print("🔍 5. Validating GeneratedAffidavit model...")
    assert isinstance(affidavit, GeneratedAffidavit)
    print("   ✅ GeneratedAffidavit validated successfully.")

    # Convert to JSON string for inspections
    affidavit_json = affidavit.model_dump_json(indent=2)

    # 12. Hallucination guard (sample entities whitelist check + unsupported legal assertions check)
    print("\n🛡️  6. Executing Hallucination Guard & Content Whitelist Checks...")
    prohibited_sample_entities = ["Arjun Mehta", "Rohan Deshpande", "3147"]
    for entity in prohibited_sample_entities:
        assert entity not in affidavit_json, f"HALLUCINATION DETECTED: Found sample entity '{entity}' in generated affidavit!"
    print("   ✅ No sample entities leaked into generated affidavit.")

    # Check for unsupplied legal assertions in body paragraphs
    unsupported_assertions = [
        "constitutional",
        "fundamental right",
        "legal right",
        "infringed",
        "liable to be dismissed in limine",
        "liable to be dismissed",
        "suppressed material facts",
        "Article 226",
    ]
    all_body_text = " ".join(p.text for p in affidavit.body_paragraphs)
    for phrase in unsupported_assertions:
        assert phrase.lower() not in all_body_text.lower(), (
            f"UNSUPPORTED LEGAL ASSERTION DETECTED: '{phrase}' found in body paragraphs! Full text: {all_body_text}"
        )
    print("   ✅ No unsupported legal assertions (constitutional/fundamental rights, limine, etc.) found.")

    # 7. Verification checks
    print("\n📋 7. Running rigorous structural assertions:")

    # Court
    assert "BOMBAY" in affidavit.forum_heading, f"Unexpected court: {affidavit.forum_heading}"
    print(f"   ✓ Court: {affidavit.forum_heading}")

    # Jurisdiction
    assert "ORDINARY ORIGINAL CIVIL JURISDICTION" in affidavit.jurisdiction, f"Unexpected jurisdiction: {affidavit.jurisdiction}"
    print(f"   ✓ Jurisdiction: {affidavit.jurisdiction}")

    # Case number line
    assert "WRIT PETITION NO. 1847 OF 2026" == affidavit.case_number_line, f"Unexpected case line: {affidavit.case_number_line}"
    print(f"   ✓ Case Number: {affidavit.case_number_line}")

    # Petitioner
    assert affidavit.cause_title.petitioner.name == "Sunrise Housing Private Limited"
    print(f"   ✓ Petitioner: {affidavit.cause_title.petitioner.name}")

    # Respondents
    resp1 = affidavit.cause_title.respondents[0]
    resp2 = affidavit.cause_title.respondents[1]
    assert "State of Maharashtra" in resp1.name
    assert "Mumbai Metropolitan Region Development Authority" in resp2.name
    print(f"   ✓ Respondent 1: {resp1.name}")
    print(f"   ✓ Respondent 2: {resp2.name}")

    # Respondent Number in Title
    assert "RESPONDENT NO. 2" in affidavit.affidavit_title
    print(f"   ✓ Affidavit Title: {affidavit.affidavit_title}")

    # Deponent details
    assert "Arvind Rajan" in affidavit.deponent_clause
    assert "Deputy Metropolitan Commissioner" in affidavit.deponent_clause
    assert "Mumbai Metropolitan Region Development Authority" in affidavit.deponent_clause
    assert "I am Respondent No. 2" not in affidavit.deponent_clause
    print("   ✓ Deponent clause correctly designates Arvind Rajan as Deputy Metropolitan Commissioner of MMRDA")

    # Body paragraphs count
    assert len(affidavit.body_paragraphs) == 7, f"Expected exactly 7 paragraphs, got {len(affidavit.body_paragraphs)}"
    print(f"   ✓ Paragraph count: exactly {len(affidavit.body_paragraphs)} paragraphs")

    # Paragraph numbers sequence
    numbers = [p.paragraph_number for p in affidavit.body_paragraphs]
    assert numbers == [1, 2, 3, 4, 5, 6, 7], f"Numbering sequence incorrect: {numbers}"
    print(f"   ✓ Numbering sequence: {numbers}")

    # Prayer check
    assert affidavit.prayer.heading == "PRAYER"
    assert len(affidavit.prayer.items) == 1
    assert affidavit.prayer.items[0].letter == "(a)"
    assert "dismiss the present Writ Petition with costs" in affidavit.prayer.items[0].text
    print("   ✓ Prayer is lettered (a) and separate from body paragraphs")

    # Verification range
    assert "paragraphs 1 to 7" in affidavit.verification.verified_range_statement, (
        f"Verification range incorrect: {affidavit.verification.verified_range_statement}"
    )
    print(f"   ✓ Verification Range: '{affidavit.verification.verified_range_statement}'")

    # Jurat & Attestation
    assert "Mumbai" in affidavit.jurat.place_line
    assert "September 2026" in affidavit.jurat.date_line
    assert "Solemnly affirmed" in affidavit.jurat.place_line
    print(f"   ✓ Jurat: {affidavit.jurat.place_line}, {affidavit.jurat.date_line}")

    # Advocate
    assert affidavit.advocate_block.firm_name == "Rajan & Associates"
    assert "Respondent No. 2" in affidavit.advocate_block.acting_for
    print(f"   ✓ Advocate: {affidavit.advocate_block.firm_name} ({affidavit.advocate_block.acting_for})")

    # Exhibit A
    all_body_text = " ".join(p.text for p in affidavit.body_paragraphs)
    assert "EXHIBIT-‘A’" in all_body_text or "EXHIBIT-'A'" in all_body_text or "EXHIBIT 'A'" in all_body_text
    print("   ✓ EXHIBIT-‘A’ is referenced in substantive paragraph")

    # 6. Save outputs/generated_affidavit.json
    with open(output_affidavit_file, "w", encoding="utf-8") as f:
        f.write(affidavit_json)
    print(f"\n💾 Saved structured affidavit to: {output_affidavit_file}")

    print("\n========================================")
    print("STEP 4 TEST PASSED SUCCESSFULLY!")
    print("========================================")


if __name__ == "__main__":
    main()
