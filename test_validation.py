import copy
import json
import os
import sys

# Ensure UTF-8 stdout on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from src.models import CaseData
from src.template_models import TemplateSpecification
from src.affidavit_models import GeneratedAffidavit
from src.validator import validate_affidavit, validate_docx


def main():
    print("========================================")
    print("STEP 6: INDEPENDENT VALIDATION TEST")
    print("========================================\n")

    case_data_path = os.path.join("outputs", "extracted_case_data.json")
    template_path = os.path.join("outputs", "template_specification.json")
    affidavit_path = os.path.join("outputs", "generated_affidavit.json")
    docx_path = os.path.join("outputs", "generated_affidavit.docx")
    report_output_path = os.path.join("outputs", "validation_report.json")

    # 1. Load inputs
    print("📂 1. Loading pipeline artifacts...")
    with open(case_data_path, "r", encoding="utf-8") as f:
        case_data_dict = json.load(f)
    with open(template_path, "r", encoding="utf-8") as f:
        template_dict = json.load(f)
    with open(affidavit_path, "r", encoding="utf-8") as f:
        affidavit_dict = json.load(f)

    # 2. Validate all three through Pydantic
    print("🔍 2. Validating input models with Pydantic...")
    case_data = CaseData.model_validate(case_data_dict)
    template = TemplateSpecification.model_validate(template_dict)
    affidavit = GeneratedAffidavit.model_validate(affidavit_dict)
    print("   ✅ CaseData, TemplateSpecification, and GeneratedAffidavit validated.")

    # 3. Run validate_affidavit() on the valid document
    print("\n⚖️  3. Running deterministic affidavit validation...")
    affidavit_report = validate_affidavit(affidavit, case_data, template)
    print(f"   Result: {'PASSED' if affidavit_report.passed else 'FAILED'}")
    print(f"   Checks performed: {len(affidavit_report.checks)}")
    for check in affidavit_report.checks:
        status_icon = "✓" if check.passed else "✗"
        print(f"   {status_icon} [{check.check_name}] {check.message}")

    assert affidavit_report.passed is True, f"Validation failed on valid affidavit: {affidavit_report.issues}"

    # 4. Run validate_docx() on the rendered DOCX
    print(f"\n📄 4. Running independent DOCX validation on {docx_path}...")
    docx_report = validate_docx(docx_path, affidavit, case_data, template)
    print(f"   Result: {'PASSED' if docx_report.passed else 'FAILED'}")
    print(f"   Checks performed: {len(docx_report.checks)}")
    for check in docx_report.checks:
        status_icon = "✓" if check.passed else "✗"
        print(f"   {status_icon} [{check.check_name}] {check.message}")

    assert docx_report.passed is True, f"Validation failed on DOCX: {docx_report.issues}"

    # 5. Save consolidated report to outputs/validation_report.json
    all_checks = affidavit_report.checks + docx_report.checks
    all_issues = [c for c in all_checks if not c.passed]
    combined_report = {
        "passed": len(all_issues) == 0,
        "total_checks": len(all_checks),
        "checks": [c.model_dump() for c in all_checks],
        "issues": [i.model_dump() for i in all_issues],
        "summary": "All 20 validation checks passed successfully across GeneratedAffidavit and DOCX."
    }

    with open(report_output_path, "w", encoding="utf-8") as f:
        json.dump(combined_report, f, indent=2)
    print(f"\n💾 Saved validation report to: {report_output_path}")

    # ====================================================
    # 6. SYNTHETIC NEGATIVE TESTS (Catching Defects)
    # ====================================================
    print("\n" + "=" * 50)
    print("RUNNING SYNTHETIC NEGATIVE DEFECT TESTS")
    print("=" * 50)

    # Negative Test A: Verification range altered to "paragraphs 1 to 6"
    print("\n🧪 Negative Test A: Alter verification range to 'paragraphs 1 to 6'...")
    bad_affidavit_a = copy.deepcopy(affidavit)
    bad_affidavit_a.verification.verified_range_statement = "paragraphs 1 to 6 and the Prayer above"
    report_a = validate_affidavit(bad_affidavit_a, case_data, template)
    failed_check_a = next((i for i in report_a.issues if i.check_name == "verification_range"), None)
    assert failed_check_a is not None, "Validator failed to catch invalid verification range!"
    assert report_a.passed is False
    print(f"   ✅ Successfully caught defect: {failed_check_a.message}")

    # Negative Test B: Affidavit title altered to "RESPONDENT NO. 1"
    print("\n🧪 Negative Test B: Alter affidavit title to Respondent No. 1...")
    bad_affidavit_b = copy.deepcopy(affidavit)
    bad_affidavit_b.affidavit_title = "AFFIDAVIT IN REPLY ON BEHALF OF RESPONDENT NO. 1"
    report_b = validate_affidavit(bad_affidavit_b, case_data, template)
    failed_check_b = next((i for i in report_b.issues if i.check_name == "respondent_number_consistency"), None)
    assert failed_check_b is not None, "Validator failed to catch respondent number inconsistency!"
    assert report_b.passed is False
    print(f"   ✅ Successfully caught defect: {failed_check_b.message}")

    # Negative Test C: Body numbering altered with gap [1, 2, 3, 5, 6, 7, 8]
    print("\n🧪 Negative Test C: Alter body paragraph numbering to [1, 2, 3, 5, 6, 7, 8]...")
    bad_affidavit_c = copy.deepcopy(affidavit)
    for idx, num in enumerate([1, 2, 3, 5, 6, 7, 8]):
        bad_affidavit_c.body_paragraphs[idx].paragraph_number = num
    report_c = validate_affidavit(bad_affidavit_c, case_data, template)
    failed_check_c = next((i for i in report_c.issues if i.check_name == "continuous_numbering"), None)
    assert failed_check_c is not None, "Validator failed to catch discontinuous body numbering!"
    assert report_c.passed is False
    print(f"   ✅ Successfully caught defect: {failed_check_c.message}")

    # Negative Test D: Sample data leakage ("Arjun Mehta" inserted into body)
    print("\n🧪 Negative Test D: Introduce sample entity 'Arjun Mehta' into body text...")
    bad_affidavit_d = copy.deepcopy(affidavit)
    bad_affidavit_d.body_paragraphs[0].text += " (pertaining to Arjun Mehta)"
    report_d = validate_affidavit(bad_affidavit_d, case_data, template)
    failed_check_d = next((i for i in report_d.issues if i.check_name == "sample_data_leakage"), None)
    assert failed_check_d is not None, "Validator failed to catch leaked sample entity!"
    assert report_d.passed is False
    print(f"   ✅ Successfully caught defect: {failed_check_d.message}")

    # Negative Test E: Unsupported legal assertion ("constitutional right" inserted)
    print("\n🧪 Negative Test E: Introduce unsupplied assertion 'constitutional right'...")
    bad_affidavit_e = copy.deepcopy(affidavit)
    bad_affidavit_e.body_paragraphs[2].text += " No constitutional right was infringed."
    report_e = validate_affidavit(bad_affidavit_e, case_data, template)
    failed_check_e = next((i for i in report_e.issues if i.check_name == "unsupported_content_check"), None)
    assert failed_check_e is not None, "Validator failed to catch unsupplied constitutional right assertion!"
    assert report_e.passed is False
    print(f"   ✅ Successfully caught defect: {failed_check_e.message}")

    print("\n========================================")
    print("STEP 6 VALIDATION & NEGATIVE TESTS ALL PASSED!")
    print("========================================")


if __name__ == "__main__":
    main()
