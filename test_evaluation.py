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
from src.validator import ValidationReport
from src.evaluator import evaluate_affidavit, EvaluationReport, DIMENSION_WEIGHTS


def generate_markdown_report(report: EvaluationReport, output_path: str):
    """Renders a readable GitHub-flavored Markdown evaluation report."""
    md = f"""# Legal Document Evaluation Report: Affidavit in Reply

## Executive Summary
- **Overall Score**: **{report.overall_score} / {report.max_score}** ({report.overall_percentage}%)
- **Status**: **{'PASSED' if report.overall_score >= 80 else 'FAILED'}**
- **Total Issues Detected**: {len(report.issues)}

---

## 1. Six Evaluation Dimensions
| Dimension | Earned Score | Max Score | Percentage | Status |
|-----------|--------------|-----------|------------|--------|
"""
    for dim in report.dimensions:
        status_tag = "✅ PASS" if dim.score == dim.max_score else ("⚠️ PARTIAL" if dim.score > 0 else "❌ FAIL")
        md += f"| **{dim.name}** | {dim.score} | {dim.max_score} | {dim.percentage}% | {status_tag} |\n"

    md += """
---

## 2. Dimension Breakdown & Explanations
"""
    for dim in report.dimensions:
        md += f"### {dim.name} ({dim.score}/{dim.max_score} pts — {dim.percentage}%)\n"
        md += f"- **Explanation**: {dim.explanation}\n"
        md += f"- **Supporting Validation Checks**: `{', '.join(dim.supporting_checks)}`\n"
        if dim.issues:
            md += "- **Issues Recorded**:\n"
            for iss in dim.issues:
                md += f"  - [{iss.severity.upper()}] {iss.description} *(Source: `{iss.source}`)*\n"
        else:
            md += "- **Issues Recorded**: None. Full compliance.\n"
        md += "\n"

    md += """---

## 3. Scoring Methodology & Weighting
The 100-point composite scoring model is structured across six legal quality dimensions:

| Dimension | Max Points | Evaluation Scope |
|-----------|------------|------------------|
| **Entity Accuracy** | 20 | Court, Case No, Year, Parties, Deponent Name, Designation, Organisation, Address, Attestation, Advocate. |
| **Completeness** | 15 | Coverage of all 6 substantive reply points, Prayer relief, Attestation, Exhibit reference. |
| **Structure** | 15 | Section presence, strict 1-11 sequence, 7 body paragraphs, continuous numbering, verification range. |
| **Consistency** | 15 | Respondent No. 2 consistency, deponent officer form, verb agreement, place/date alignment. |
| **Template Fidelity** | 20 | Adherence to procedural rules, conventions, and document layout in `format_explained.pdf`. |
| **Hallucination** | 15 | Absence of sample entity leakage (`Arjun Mehta`, etc.) and unsupported legal/factual assertions. |
| **Total** | **100** | **Complete Legal Quality Metric** |

---

## 4. Issues Detail
"""
    if report.issues:
        for idx, iss in enumerate(report.issues, 1):
            md += f"{idx}. **[{iss.dimension}]** {iss.description}\n"
            md += f"   - *Expected*: `{iss.expected}`\n"
            md += f"   - *Actual*: `{iss.actual}`\n"
            md += f"   - *Source*: `{iss.source}`\n"
    else:
        md += "✅ No defects or discrepancies detected in the generated affidavit.\n"

    md += f"""
---

## 5. Limitations & Legal Disclaimer
> [!IMPORTANT]
> **Validation & Evaluation Limitations**:
> {report.limitations}
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md)


def main():
    print("========================================")
    print("STEP 7: EVALUATION & SCORING TEST")
    print("========================================\n")

    case_data_path = os.path.join("outputs", "extracted_case_data.json")
    template_path = os.path.join("outputs", "template_specification.json")
    affidavit_path = os.path.join("outputs", "generated_affidavit.json")
    val_report_path = os.path.join("outputs", "validation_report.json")
    eval_json_path = os.path.join("outputs", "evaluation_report.json")
    eval_md_path = os.path.join("outputs", "evaluation_report.md")

    # 1. Load inputs
    print("📂 1. Loading pipeline artifacts...")
    with open(case_data_path, "r", encoding="utf-8") as f:
        case_data_dict = json.load(f)
    with open(template_path, "r", encoding="utf-8") as f:
        template_dict = json.load(f)
    with open(affidavit_path, "r", encoding="utf-8") as f:
        affidavit_dict = json.load(f)
    with open(val_report_path, "r", encoding="utf-8") as f:
        val_report_dict = json.load(f)

    # 2. Validate models
    print("🔍 2. Validating input schemas with Pydantic...")
    case_data = CaseData.model_validate(case_data_dict)
    template = TemplateSpecification.model_validate(template_dict)
    affidavit = GeneratedAffidavit.model_validate(affidavit_dict)
    val_report = ValidationReport.model_validate(val_report_dict)
    print("   ✅ Models validated.")

    # 3. Run evaluation on valid document
    print("\n⚖️  3. Running 100-point evaluator on GeneratedAffidavit...")
    report = evaluate_affidavit(affidavit, case_data, template, val_report)

    # 4. Save JSON and Markdown reports
    with open(eval_json_path, "w", encoding="utf-8") as f:
        f.write(report.model_dump_json(indent=2))
    print(f"💾 Saved JSON report to: {eval_json_path}")

    generate_markdown_report(report, eval_md_path)
    print(f"📝 Saved Markdown report to: {eval_md_path}")

    # 5. Assertions on the valid document evaluation
    print("\n📋 4. Checking evaluation integrity:")
    assert len(report.dimensions) == 6, f"Expected 6 dimensions, got {len(report.dimensions)}"
    print(f"   ✓ 6 dimensions evaluated")

    weights_sum = sum(DIMENSION_WEIGHTS.values())
    assert weights_sum == 100.0, f"Weights sum to {weights_sum}, expected 100.0"
    print(f"   ✓ Weights sum to {weights_sum}")

    for dim in report.dimensions:
        assert 0.0 <= dim.score <= dim.max_score, f"Dimension {dim.name} score {dim.score} out of bounds"
        print(f"   ✓ {dim.name}: {dim.score} / {dim.max_score} pts ({dim.percentage}%)")

    assert report.overall_score == 100.0, f"Expected 100.0 for valid document, got {report.overall_score}"
    assert report.overall_percentage == 100.0
    assert len(report.issues) == 0, f"Expected 0 issues for valid document, got {len(report.issues)}"
    print(f"\n   ⭐ Overall Score: {report.overall_score} / {report.max_score} ({report.overall_percentage}%) - {len(report.issues)} Issues")

    # ====================================================
    # 6. SYNTHETIC NEGATIVE SCORING TESTS
    # ====================================================
    print("\n" + "=" * 50)
    print("RUNNING NEGATIVE SCORING TESTS")
    print("=" * 50)

    # Negative Test A: Wrong respondent number (Respondent No. 1)
    print("\n🧪 Negative Test A: Wrong respondent number (Title changed to Respondent No. 1)...")
    bad_affidavit_a = copy.deepcopy(affidavit)
    bad_affidavit_a.affidavit_title = "AFFIDAVIT IN REPLY ON BEHALF OF RESPONDENT NO. 1"
    report_a = evaluate_affidavit(bad_affidavit_a, case_data, template)
    print(f"   Score: {report_a.overall_score}/100 | Consistency: {report_a.dimensions[3].score}/15 | Issues: {len(report_a.issues)}")
    assert report_a.overall_score < 100.0, "Score should decrease for wrong respondent number"
    assert report_a.dimensions[3].score < 15.0 or report_a.dimensions[0].score < 20.0, "Consistency or Entity Accuracy score must decrease"
    print("   ✅ Test A Passed: Score decreased as expected.")

    # Negative Test B: Missing content (Remove Point 4 communication denial)
    print("\n🧪 Negative Test B: Missing content (Remove Point 4 substantive denial)...")
    bad_affidavit_b = copy.deepcopy(affidavit)
    bad_affidavit_b.body_paragraphs[3].text = "I say that the weather in Mumbai is pleasant."
    report_b = evaluate_affidavit(bad_affidavit_b, case_data, template)
    print(f"   Score: {report_b.overall_score}/100 | Completeness: {report_b.dimensions[1].score}/15 | Issues: {len(report_b.issues)}")
    assert report_b.dimensions[1].score < 15.0, "Completeness score must decrease when point 4 is omitted"
    assert report_b.overall_score < 100.0
    print("   ✅ Test B Passed: Completeness score decreased as expected.")

    # Negative Test C: Hallucination (Inject 'Arjun Mehta' and constitutional assertion)
    print("\n🧪 Negative Test C: Hallucination (Inject sample entity 'Arjun Mehta')...")
    bad_affidavit_c = copy.deepcopy(affidavit)
    bad_affidavit_c.body_paragraphs[0].text += " (pertaining to Arjun Mehta)"
    report_c = evaluate_affidavit(bad_affidavit_c, case_data, template)
    print(f"   Score: {report_c.overall_score}/100 | Hallucination: {report_c.dimensions[5].score}/15 | Issues: {len(report_c.issues)}")
    assert report_c.dimensions[5].score < 15.0, "Hallucination score must decrease when sample entity leaked"
    assert report_c.overall_score < 100.0
    print("   ✅ Test C Passed: Hallucination score decreased as expected.")

    print("\n========================================")
    print("STEP 7 EVALUATION TESTS ALL PASSED!")
    print("========================================")


if __name__ == "__main__":
    main()
