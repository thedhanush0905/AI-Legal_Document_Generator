"""
End-to-End Pipeline Integration Test.
Runs the complete legal generation and evaluation pipeline without launching Streamlit interactively,
verifying that all steps and output files are created cleanly.
"""

import os
import sys

# Ensure UTF-8 stdout on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from src.pipeline import run_pipeline, PipelineResult


def test_end_to_end_pipeline():
    print("========================================")
    print("STEP 8: END-TO-END PIPELINE INTEGRATION TEST")
    print("========================================\n")

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("⚠️  WARNING: OPENROUTER_API_KEY not set. Skipping live LLM integration test.")
        return

    case_pdf = os.path.join("inputs", "case_information.pdf")
    format_pdf = os.path.join("inputs", "format_explained.pdf")
    sample_pdf = os.path.join("inputs", "sample_affidavit.pdf")

    assert os.path.exists(case_pdf), f"Missing input: {case_pdf}"
    assert os.path.exists(format_pdf), f"Missing input: {format_pdf}"
    assert os.path.exists(sample_pdf), f"Missing input: {sample_pdf}"

    print(f"🚀 Running full pipeline with {case_pdf}...")

    def progress_monitor(step, total, msg):
        print(f"   [{step}/{total}] {msg}")

    result: PipelineResult = run_pipeline(
        case_info_pdf_path=case_pdf,
        format_explained_pdf_path=format_pdf,
        sample_affidavit_pdf_path=sample_pdf,
        output_dir="outputs",
        progress_callback=progress_monitor,
    )

    print("\n🔍 Verifying pipeline outputs and integrity:")

    # 1. Output files exist
    expected_files = [
        result.docx_path,
        result.extracted_case_data_path,
        result.template_spec_path,
        result.generated_affidavit_path,
        result.validation_report_path,
        result.evaluation_report_path,
        result.evaluation_report_md_path,
    ]
    for file_path in expected_files:
        assert os.path.exists(file_path), f"Output file missing: {file_path}"
        assert os.path.getsize(file_path) > 0, f"Output file empty: {file_path}"
        print(f"   ✓ File exists and non-empty: {file_path}")

    # 2. Validation passed
    assert result.validation_report.passed is True, f"Validation failed: {result.validation_report.issues}"
    print(f"   ✓ Validation report passed: {len(result.validation_report.checks)} checks verified")

    # 3. Evaluation passed
    assert len(result.evaluation_report.dimensions) == 6, "Expected 6 evaluation dimensions"
    assert result.evaluation_report.overall_score == 100.0, f"Expected 100.0, got {result.evaluation_report.overall_score}"
    assert len(result.evaluation_report.issues) == 0, f"Expected 0 issues, got {len(result.evaluation_report.issues)}"
    print(f"   ✓ Evaluation report score: {result.evaluation_report.overall_score}/100.0 (100.0%) across 6 dimensions")

    # 4. Affidavit structure check
    assert len(result.affidavit.body_paragraphs) == 7, "Expected 7 body paragraphs"
    assert "paragraphs 1 to 7" in result.affidavit.verification.verified_range_statement
    assert "EXHIBIT-‘A’" in " ".join(p.text for p in result.affidavit.body_paragraphs) or "EXHIBIT-'A'" in " ".join(p.text for p in result.affidavit.body_paragraphs)
    print("   ✓ Affidavit structure and exhibit verified")

    print("\n========================================")
    print("STEP 8 INTEGRATION TEST PASSED SUCCESSFULLY!")
    print("========================================")


if __name__ == "__main__":
    test_end_to_end_pipeline()
