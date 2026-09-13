import json
import os
import sys

# Ensure UTF-8 stdout on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from src.document_reader import read_pdf
from src.template_builder import build_template_specification
from src.template_models import TemplateSpecification


def test_template():
    print("========================================")
    print("STEP 3: TEMPLATE UNDERSTANDING TEST")
    print("========================================\n")

    # 1. Read format_explained.pdf
    rulebook_path = os.path.join("inputs", "format_explained.pdf")
    print(f"📖 1. Reading rulebook: {rulebook_path}")
    rulebook_text = read_pdf(rulebook_path)
    print(f"   ✅ Successfully read rulebook ({len(rulebook_text)} chars)")

    # 2. Read sample_affidavit.pdf
    sample_path = os.path.join("inputs", "sample_affidavit.pdf")
    print(f"\n📑 2. Reading sample: {sample_path}")
    sample_text = read_pdf(sample_path)
    print(f"   ✅ Successfully read sample ({len(sample_text)} chars)")

    # 3. Build the template specification
    print("\n🏗️  3. Building TemplateSpecification from reference rules...")
    spec = build_template_specification()

    # 4. Validate with Pydantic
    print("🔍 4. Validating with Pydantic...")
    assert isinstance(spec, TemplateSpecification), "Specification must be instance of TemplateSpecification"
    print("   ✅ Pydantic model validation successful!")

    # 5. Verify the 10 required sections exist
    required_ten_sections = [
        "Forum heading",
        "Jurisdiction",
        "Case number",
        "Cause title",
        "Affidavit title",
        "Deponent clause",
        "Numbered reply paragraphs",
        "Prayer",
        "Jurat",
        "Verification",
    ]
    print("\n📋 5. Verifying ten required sections exist:")
    spec_section_names = [s.name for s in spec.sections]
    for section_name in required_ten_sections:
        assert section_name in spec_section_names, f"Missing required section: {section_name}"
        print(f"   ✓ {section_name}")

    # 6. Verify section order
    print("\n🔢 6. Verifying section order matches rulebook:")
    for idx, expected_name in enumerate(required_ten_sections):
        actual_name = spec.sections[idx].name
        assert actual_name == expected_name, (
            f"Section order mismatch at index {idx}: expected '{expected_name}', got '{actual_name}'"
        )
        print(f"   Order {idx+1}: {actual_name}")

    # 7. Verify critical rules are present
    print("\n⚖️  7. Verifying critical rules:")
    cr = spec.critical_rules
    assert "respondent number" in cr.respondent_in_title.lower()
    print("   ✓ Respondent number in affidavit title rule present")
    assert "organisation" in cr.deponent_clause_form.lower()
    print("   ✓ Organisation deponent designation rule present")
    assert "continuous" in cr.continuous_numbering.lower()
    print("   ✓ Continuous paragraph numbering rule present")
    assert "lettered" in cr.prayer_not_numbered_with_body.lower()
    print("   ✓ Prayer lettered and not numbered with body rule present")
    assert "exact" in cr.verification_range_exact_match.lower() or "match" in cr.verification_range_exact_match.lower()
    print("   ✓ Verification range exact match rule present")
    assert "verb" in cr.verb_agreement.lower()
    print("   ✓ Verb agreement rule present")
    assert "consistent" in cr.respondent_consistency.lower()
    print("   ✓ Respondent consistency rule present")

    # 8. Save to outputs/template_specification.json and outputs/template_specification.md
    os.makedirs("outputs", exist_ok=True)
    json_path = os.path.join("outputs", "template_specification.json")
    md_path = os.path.join("outputs", "template_specification.md")

    spec_json = spec.model_dump_json(indent=2)
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(spec_json)
    print(f"\n💾 Saved JSON specification to: {json_path}")

    # Generate readable markdown summary
    md_content = f"""# Template Specification: {spec.document_type}

Based on `inputs/format_explained.pdf` and verified against `inputs/sample_affidavit.pdf`.

## 1. Ten Required Sections (Strict Order)
| # | Section Name | Required | Formatting |
|---|--------------|----------|------------|
"""
    for s in spec.sections:
        req_str = "Yes" if s.required else "Optional"
        md_content += f"| {s.order} | **{s.name}** | {req_str} | {s.formatting} |\n"

    md_content += "\n## 2. Critical Validation Rules\n"
    md_content += f"- **Affidavit Title**: {cr.respondent_in_title}\n"
    md_content += f"- **Deponent Clause**: {cr.deponent_clause_form}\n"
    md_content += f"- **Continuous Numbering**: {cr.continuous_numbering}\n"
    md_content += f"- **Prayer Lettering**: {cr.prayer_not_numbered_with_body}\n"
    md_content += f"- **Verification Paragraph Range**: {cr.verification_range_exact_match}\n"
    md_content += f"- **Verb Agreement**: {cr.verb_agreement}\n"
    md_content += f"- **Respondent Consistency**: {cr.respondent_consistency}\n"

    md_content += "\n## 3. Rhetorical Reply Moves\n"
    for rm in spec.reply_move_structure:
        md_content += f"### {rm.move}\n- **Description**: {rm.description}\n- **Standard Opening**: `{rm.opening_words}`\n\n"

    md_content += "\n## 4. Exclusions\n"
    for exc in spec.exclusions:
        md_content += f"- {exc}\n"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"📝 Saved Markdown specification to: {md_path}")

    print("\n========================================")
    print("STEP 3 TEST PASSED SUCCESSFULLY!")
    print("========================================")


if __name__ == "__main__":
    test_template()
