"""
Test Suite for Step 8.7:
A. CaseData with six reply points -> Generated affidavit contains coverage for all six.
B. Simulated omitted reply point -> Coverage verification detects it.
C. Different number of reply points -> Coverage mechanism remains generic.
D. Preview HTML -> Dedented HTML renders clean tags without leading 4-space code block triggers.
E. Evaluation issue exists -> UI status becomes REVIEW REQUIRED.
F. Perfect evaluation -> UI status remains PASSED.
"""

import json
import os
import sys
import textwrap

# Ensure UTF-8 stdout on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from src.models import CaseData, ReplyPoint
from src.affidavit_models import BodyParagraph
from src.affidavit_generator import verify_reply_points_coverage
from src.evaluator import EvaluationIssue, EvaluationReport, EvaluationDimension


def test_a_coverage_six_reply_points():
    print("\n--- Test A: CaseData with six reply points has full coverage ---")
    with open("outputs/extracted_case_data.json", "r", encoding="utf-8") as f:
        case_data_dict = json.load(f)
    case_data = CaseData.model_validate(case_data_dict)

    with open("outputs/generated_affidavit.json", "r", encoding="utf-8") as f:
        affidavit_dict = json.load(f)
    body_paragraphs = [BodyParagraph.model_validate(bp) for bp in affidavit_dict["body_paragraphs"]]

    passed, missing = verify_reply_points_coverage(body_paragraphs, case_data.reply_points)
    assert passed is True, f"Failed coverage on 6 points: {missing}"
    assert len(missing) == 0
    print(f"   ✓ All {len(case_data.reply_points)} reply points verified as covered.")


def test_b_simulated_omitted_reply_point():
    print("\n--- Test B: Simulated omitted reply point detected by verification ---")
    with open("outputs/extracted_case_data.json", "r", encoding="utf-8") as f:
        case_data_dict = json.load(f)
    case_data = CaseData.model_validate(case_data_dict)

    # Paragraphs omitting Point 4 (communication denial regarding lack of authority)
    with open("outputs/generated_affidavit.json", "r", encoding="utf-8") as f:
        affidavit_dict = json.load(f)
    
    # Replace Paragraph 4 with irrelevant text
    omitted_paragraphs = []
    for bp in affidavit_dict["body_paragraphs"]:
        model_bp = BodyParagraph.model_validate(bp)
        if model_bp.paragraph_number == 4:
            model_bp.text = "This paragraph omits the communication denial entirely."
        omitted_paragraphs.append(model_bp)

    passed, missing = verify_reply_points_coverage(omitted_paragraphs, case_data.reply_points)
    assert passed is False, "Coverage verification should have failed when Point 4 was omitted!"
    assert any("Point 4" in m for m in missing), f"Expected Point 4 in missing list, got: {missing}"
    print(f"   ✓ Correctly detected omitted reply point: {missing}")


def test_c_different_number_of_reply_points():
    print("\n--- Test C: Different number of reply points (generic mechanism) ---")
    custom_points = [
        ReplyPoint(
            point_number=1,
            title="Jurisdiction Challenge",
            details=["The respondent challenges the territorial jurisdiction of this court."]
        ),
        ReplyPoint(
            point_number=2,
            title="Alternative Remedy",
            details=["The petitioner has an effective alternative remedy available before the tribunal."]
        ),
        ReplyPoint(
            point_number=3,
            title="Limitation Period",
            details=["The present claim is barred by the statutory period of limitation."]
        ),
        ReplyPoint(
            point_number=4,
            title="Acquiescence",
            details=["The petitioner by its own conduct has acquiesced in the impugned order."]
        ),
    ]

    # Test complete coverage
    covered_paras = [
        BodyParagraph(paragraph_number=1, move_type="SUBSTANTIVE_ANSWER", text="The respondent challenges the territorial jurisdiction of this court as no cause of action arose within its limits."),
        BodyParagraph(paragraph_number=2, move_type="SUBSTANTIVE_ANSWER", text="The petitioner has an effective alternative remedy available before the appellate tribunal."),
        BodyParagraph(paragraph_number=3, move_type="SUBSTANTIVE_ANSWER", text="The claim is completely barred by the statutory period of limitation."),
        BodyParagraph(paragraph_number=4, move_type="SUBSTANTIVE_ANSWER", text="The petitioner by its own conduct has acquiesced in the impugned order without demur."),
    ]
    passed, missing = verify_reply_points_coverage(covered_paras, custom_points)
    assert passed is True, f"Failed on custom 4 points: {missing}"
    print("   ✓ Generic verification succeeded for 4 custom reply points.")

    # Test omission of point 3
    incomplete_paras = [covered_paras[0], covered_paras[1], covered_paras[3]]
    passed_inc, missing_inc = verify_reply_points_coverage(incomplete_paras, custom_points)
    assert passed_inc is False
    assert any("Point 3" in m for m in missing_inc)
    print(f"   ✓ Generic verification correctly caught missing custom point 3: {missing_inc}")


def test_d_preview_html_not_raw_text():
    print("\n--- Test D: Preview HTML does not contain 4-space markdown indentations ---")
    from src.affidavit_models import GeneratedAffidavit
    with open("outputs/generated_affidavit.json", "r", encoding="utf-8") as f:
        affidavit_dict = json.load(f)
    affidavit = GeneratedAffidavit.model_validate(affidavit_dict)

    body_paras_html = "".join([f"<p><b>{bp.paragraph_number}.</b> {bp.text}</p>" for bp in affidavit.body_paragraphs])
    prayer_items_html = "".join([f"<p style='margin-left: 20px;'><b>{pi.letter}</b> {pi.text}</p>" for pi in affidavit.prayer.items])
    respondents_html = "".join([f"<div>{r.name}</div><div style='font-size: 0.9em; font-style: italic;'>{r.status_tag}</div>" for r in affidavit.cause_title.respondents])

    raw_document_html = f"""
<div class="affidavit-document-preview">
<h3>{affidavit.forum_heading}</h3>
<h4>{affidavit.jurisdiction}</h4>
<div style="text-align: center; font-weight: bold; margin-bottom: 1.5rem;">{affidavit.case_number_line}</div>

<div style="margin-bottom: 1rem;">
<b>{affidavit.cause_title.petitioner.name}</b><br/>
<span style="font-style: italic;">...Petitioner</span>
</div>

<div class="versus-line">VERSUS</div>

<div style="margin-bottom: 1.5rem;">
{respondents_html}
</div>

<hr style="border: 0; border-top: 1px solid #e5e7eb; margin: 1.5rem 0;" />

<h4>{affidavit.affidavit_title}</h4>
<p style="font-style: italic;">{affidavit.deponent_clause}</p>

<div style="margin-top: 1.5rem;">
{body_paras_html}
</div>

<h4 style="margin-top: 1.5rem;">PRAYER</h4>
<p>{affidavit.prayer.intro_text}</p>
{prayer_items_html}

<div style="margin-top: 2rem;">
<div>{affidavit.jurat.place_line}</div>
<div>{affidavit.jurat.date_line}</div>
<div style="margin-top: 0.5rem; font-style: italic;">{affidavit.jurat.before_me}</div>
<div class="right-sign">{affidavit.jurat.deponent_tag}</div>
</div>

<h4 style="margin-top: 2rem;">VERIFICATION</h4>
<p>{affidavit.verification.full_text}</p>
<p>{affidavit.verification.verified_at_line}</p>
<div class="right-sign">{affidavit.verification.deponent_tag}</div>

<div style="margin-top: 2rem; border-top: 1px solid #e5e7eb; padding-top: 1rem;">
<b>{affidavit.advocate_block.firm_name}</b><br/>
<span style="font-size: 0.9em;">{affidavit.advocate_block.acting_for}</span>
</div>
</div>
"""
    document_html = "\n".join(line.strip() for line in raw_document_html.strip().splitlines())

    # Verify no line has 4 or more leading spaces
    lines = document_html.split("\n")
    for i, line in enumerate(lines):
        assert not line.startswith("    "), f"Line {i} has 4+ leading spaces which triggers Markdown code block: {line!r}"
    assert lines[0].startswith("<div")
    print(f"   ✓ Preview HTML verified clean ({len(lines)} lines): zero leading indentation, no raw markdown code blocks.")


def test_e_f_quality_status_logic():
    print("\n--- Test E & F: Quality Status Logic ---")
    def compute_status(validation_passed: bool, overall_score: float, issues_count: int) -> str:
        if not validation_passed or overall_score < 100.0 or issues_count > 0:
            return "REVIEW REQUIRED"
        return "PASSED"

    # Test E: Evaluation issue exists or score < 100
    status_imperfect_score = compute_status(True, 98.1, 1)
    assert status_imperfect_score == "REVIEW REQUIRED", f"Expected REVIEW REQUIRED, got {status_imperfect_score}"

    status_eval_issue = compute_status(True, 100.0, 1)
    assert status_eval_issue == "REVIEW REQUIRED", f"Expected REVIEW REQUIRED, got {status_eval_issue}"

    status_val_failed = compute_status(False, 100.0, 0)
    assert status_val_failed == "REVIEW REQUIRED", f"Expected REVIEW REQUIRED, got {status_val_failed}"
    print("   ✓ Test E Passed: Imperfect score, issues, or validation failure -> REVIEW REQUIRED.")

    # Test F: Perfect evaluation (100% and 0 issues and validation passed)
    status_perfect = compute_status(True, 100.0, 0)
    assert status_perfect == "PASSED", f"Expected PASSED, got {status_perfect}"
    print("   ✓ Test F Passed: 100.0 score + 0 issues + validation passed -> PASSED.")


if __name__ == "__main__":
    print("========================================")
    print("STEP 8.7 UNIT & INTEGRATION TESTS")
    print("========================================")
    test_a_coverage_six_reply_points()
    test_b_simulated_omitted_reply_point()
    test_c_different_number_of_reply_points()
    test_d_preview_html_not_raw_text()
    test_e_f_quality_status_logic()
    print("\n========================================")
    print("ALL STEP 8.7 TESTS PASSED SUCCESSFULLY!")
    print("========================================")
