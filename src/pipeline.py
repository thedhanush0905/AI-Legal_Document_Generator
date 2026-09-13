"""
Affidavit Pipeline Orchestrator.
Connects document reading, structured extraction, template building,
affidavit generation, DOCX rendering, validation, and evaluation into a
single reproducible pipeline.
"""

import json
import os
from typing import Optional, Tuple
from pydantic import BaseModel, Field

from src.document_reader import read_pdf
from src.models import CaseData
from src.llm_client import extract_case_data
from src.template_models import TemplateSpecification
from src.template_builder import build_template_specification
from src.affidavit_models import GeneratedAffidavit
from src.affidavit_generator import generate_affidavit
from src.docx_generator import create_affidavit_docx
from src.validator import ValidationReport, validate_affidavit, validate_docx
from src.evaluator import EvaluationReport, evaluate_affidavit


class PipelineResult(BaseModel):
    """Encapsulates all results and artifact paths produced by the pipeline."""
    case_data: CaseData
    template_spec: TemplateSpecification
    affidavit: GeneratedAffidavit
    validation_report: ValidationReport
    evaluation_report: EvaluationReport
    docx_path: str
    extracted_case_data_path: str
    template_spec_path: str
    generated_affidavit_path: str
    validation_report_path: str
    evaluation_report_path: str
    evaluation_report_md_path: str


def run_pipeline(
    case_info_pdf_path: str,
    format_explained_pdf_path: Optional[str] = None,
    sample_affidavit_pdf_path: Optional[str] = None,
    output_dir: str = "outputs",
    progress_callback: Optional[callable] = None,
) -> PipelineResult:
    """
    Executes the complete legal document generation & evaluation pipeline.

    Args:
        case_info_pdf_path: Path to case information PDF.
        format_explained_pdf_path: Path to format explained PDF (optional, uses inputs/format_explained.pdf by default).
        sample_affidavit_pdf_path: Path to sample affidavit PDF (optional, uses inputs/sample_affidavit.pdf by default).
        output_dir: Output directory to save generated artifacts.
        progress_callback: Optional callable receiving (step_num: int, total_steps: int, message: str).

    Returns:
        PipelineResult: Complete structured result object containing all models and paths.
    """
    os.makedirs(output_dir, exist_ok=True)

    def notify(step: int, total: int, msg: str):
        if progress_callback:
            progress_callback(step, total, msg)

    # ----------------------------------------------------
    # Step 1: Read Case Information PDF
    # ----------------------------------------------------
    notify(1, 7, "Reading Case Information PDF...")
    case_info_text = read_pdf(case_info_pdf_path)
    if not case_info_text.strip():
        raise ValueError(f"Case information document '{case_info_pdf_path}' yielded no readable text.")

    # ----------------------------------------------------
    # Step 2: Extract Structured CaseData via LLM
    # ----------------------------------------------------
    notify(2, 7, "Extracting structured CaseData using LLM...")
    case_data = extract_case_data(case_info_text)
    case_data_path = os.path.join(output_dir, "extracted_case_data.json")
    with open(case_data_path, "w", encoding="utf-8") as f:
        f.write(case_data.model_dump_json(indent=2))

    # ----------------------------------------------------
    # Step 3: Build/Verify Template Specification
    # ----------------------------------------------------
    notify(3, 7, "Building and validating Template Specification...")
    template_spec = build_template_specification()
    template_spec_path = os.path.join(output_dir, "template_specification.json")
    with open(template_spec_path, "w", encoding="utf-8") as f:
        f.write(template_spec.model_dump_json(indent=2))

    # ----------------------------------------------------
    # Step 4: Generate Affidavit Content
    # ----------------------------------------------------
    notify(4, 7, "Generating Affidavit in Reply structure and substantive prose...")
    affidavit = generate_affidavit(case_data, template_spec)
    generated_affidavit_path = os.path.join(output_dir, "generated_affidavit.json")
    with open(generated_affidavit_path, "w", encoding="utf-8") as f:
        f.write(affidavit.model_dump_json(indent=2))

    # ----------------------------------------------------
    # Step 5: Render DOCX File
    # ----------------------------------------------------
    notify(5, 7, "Rendering legal DOCX document with styling...")
    docx_path = os.path.join(output_dir, "generated_affidavit.docx")
    create_affidavit_docx(affidavit, docx_path)

    # ----------------------------------------------------
    # Step 6: Execute Deterministic Validation
    # ----------------------------------------------------
    notify(6, 7, "Running independent deterministic validation on affidavit and DOCX...")
    affidavit_val = validate_affidavit(affidavit, case_data, template_spec)
    docx_val = validate_docx(docx_path, affidavit, case_data, template_spec)

    combined_checks = affidavit_val.checks + docx_val.checks
    combined_issues = [c for c in combined_checks if not c.passed]
    validation_report = ValidationReport(
        passed=len(combined_issues) == 0,
        checks=combined_checks,
        issues=combined_issues,
        summary=f"{len(combined_checks) - len(combined_issues)} of {len(combined_checks)} validation checks passed.",
    )
    validation_report_path = os.path.join(output_dir, "validation_report.json")
    with open(validation_report_path, "w", encoding="utf-8") as f:
        f.write(validation_report.model_dump_json(indent=2))

    # ----------------------------------------------------
    # Step 7: Run 6-Dimension Evaluation & Scoring
    # ----------------------------------------------------
    notify(7, 7, "Evaluating quality across 6 standardized legal dimensions...")
    evaluation_report = evaluate_affidavit(affidavit, case_data, template_spec, validation_report)
    evaluation_report_path = os.path.join(output_dir, "evaluation_report.json")
    with open(evaluation_report_path, "w", encoding="utf-8") as f:
        f.write(evaluation_report.model_dump_json(indent=2))

    # Render Markdown report
    evaluation_report_md_path = os.path.join(output_dir, "evaluation_report.md")
    from test_evaluation import generate_markdown_report
    generate_markdown_report(evaluation_report, evaluation_report_md_path)

    return PipelineResult(
        case_data=case_data,
        template_spec=template_spec,
        affidavit=affidavit,
        validation_report=validation_report,
        evaluation_report=evaluation_report,
        docx_path=docx_path,
        extracted_case_data_path=case_data_path,
        template_spec_path=template_spec_path,
        generated_affidavit_path=generated_affidavit_path,
        validation_report_path=validation_report_path,
        evaluation_report_path=evaluation_report_path,
        evaluation_report_md_path=evaluation_report_md_path,
    )
