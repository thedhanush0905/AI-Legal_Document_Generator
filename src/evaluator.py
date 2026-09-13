"""
Evaluation and Scoring System for Legal Document Generation (Affidavit in Reply).
Evaluates the generated Affidavit in Reply across six standardized dimensions:
1. Entity Accuracy (20 pts)
2. Completeness (15 pts)
3. Structure (15 pts)
4. Consistency (15 pts)
5. Template Fidelity (20 pts)
6. Hallucination (15 pts)
Total = 100 points.

Works purely deterministically using CaseData, TemplateSpecification, GeneratedAffidavit,
and ValidationReport, with an optional semantic LLM evaluation layer.
"""

import json
import os
import re
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from src.models import CaseData
from src.template_models import TemplateSpecification
from src.affidavit_models import GeneratedAffidavit
from src.validator import ValidationReport, validate_affidavit


class EvaluationIssue(BaseModel):
    """Specific defect or omission penalizing a dimension score."""
    dimension: str = Field(..., description="Evaluation dimension name")
    severity: str = Field(..., description="'error', 'warning', or 'info'")
    description: str = Field(..., description="Detailed description of the issue")
    expected: Optional[str] = Field(None, description="Expected value or behavior")
    actual: Optional[str] = Field(None, description="Observed value or behavior")
    source: str = Field(..., description="Auditable source or reference location")


class EvaluationDimension(BaseModel):
    """Detailed score and breakdown for one evaluation dimension."""
    name: str = Field(..., description="Dimension title")
    score: float = Field(..., description="Earned score points")
    max_score: float = Field(..., description="Maximum possible points")
    percentage: float = Field(..., description="Percentage score (0-100%)")
    explanation: str = Field(..., description="Reasoning and breakdown for this score")
    issues: List[EvaluationIssue] = Field(default_factory=list, description="Issues found in this dimension")
    supporting_checks: List[str] = Field(default_factory=list, description="Validation check identifiers used")


class EvaluationReport(BaseModel):
    """Complete evaluation report with 100-point overall score and dimension breakdown."""
    overall_score: float = Field(..., description="Total earned points across all dimensions")
    max_score: float = Field(default=100.0, description="Maximum total points (100.0)")
    overall_percentage: float = Field(..., description="Overall percentage score")
    dimensions: List[EvaluationDimension] = Field(..., description="Scores for the six dimensions")
    issues: List[EvaluationIssue] = Field(default_factory=list, description="Consolidated list of all issues")
    methodology: Dict[str, float] = Field(..., description="Weighting configuration across dimensions")
    summary: str = Field(..., description="Executive evaluation summary")
    limitations: str = Field(..., description="Explicit statement regarding validation limitations")


DIMENSION_WEIGHTS = {
    "Entity Accuracy": 20.0,
    "Completeness": 15.0,
    "Structure": 15.0,
    "Consistency": 15.0,
    "Template Fidelity": 20.0,
    "Hallucination": 15.0,
}


def evaluate_affidavit(
    affidavit: GeneratedAffidavit,
    case_data: CaseData,
    template: TemplateSpecification,
    validation_report: Optional[ValidationReport] = None,
) -> EvaluationReport:
    """
    Computes a rigorous, auditable evaluation across all six dimensions.
    Scores are derived deterministically from the validation checks and entity comparisons.
    """
    if validation_report is None:
        validation_report = validate_affidavit(affidavit, case_data, template)

    val_checks_dict = {c.check_name: c for c in validation_report.checks}
    all_issues: List[EvaluationIssue] = []

    # ----------------------------------------------------
    # 1. ENTITY ACCURACY (20 Points)
    # Check 16 distinct entities against CaseData
    # ----------------------------------------------------
    entity_checks = [
        ("court", case_data.court.upper() in affidavit.forum_heading.upper(), case_data.court, affidavit.forum_heading, "CaseData.court"),
        ("jurisdiction", case_data.jurisdiction.upper() in affidavit.jurisdiction.upper(), case_data.jurisdiction, affidavit.jurisdiction, "CaseData.jurisdiction"),
        ("proceeding", case_data.proceeding.upper() in affidavit.case_number_line.upper(), case_data.proceeding, affidavit.case_number_line, "CaseData.proceeding"),
        ("case_number", case_data.case_number in affidavit.case_number_line, case_data.case_number, affidavit.case_number_line, "CaseData.case_number"),
        ("year", case_data.year in affidavit.case_number_line, case_data.year, affidavit.case_number_line, "CaseData.year"),
        ("petitioner", case_data.petitioner.lower() in affidavit.cause_title.petitioner.name.lower(), case_data.petitioner, affidavit.cause_title.petitioner.name, "CaseData.petitioner"),
        ("respondent_1", any("State of Maharashtra" in r.name for r in affidavit.cause_title.respondents), "State of Maharashtra", str([r.name for r in affidavit.cause_title.respondents]), "CaseData.respondents[0]"),
        ("respondent_2", any("Mumbai Metropolitan Region Development Authority" in r.name for r in affidavit.cause_title.respondents), "MMRDA", str([r.name for r in affidavit.cause_title.respondents]), "CaseData.respondents[1]"),
        ("respondent_number", case_data.respondent_number.upper().replace(".", "") in affidavit.affidavit_title.upper().replace(".", ""), case_data.respondent_number, affidavit.affidavit_title, "CaseData.respondent_number"),
        ("deponent", case_data.deponent.lower() in affidavit.deponent_clause.lower(), case_data.deponent, affidavit.deponent_clause, "CaseData.deponent"),
        ("designation", case_data.designation.lower() in affidavit.deponent_clause.lower(), case_data.designation, affidavit.deponent_clause, "CaseData.designation"),
        ("organisation", case_data.organisation.lower() in affidavit.deponent_clause.lower(), case_data.organisation, affidavit.deponent_clause, "CaseData.organisation"),
        ("address", case_data.address.lower() in affidavit.deponent_clause.lower(), case_data.address, affidavit.deponent_clause, "CaseData.address"),
        ("attestation_place", case_data.attestation_place.lower() in affidavit.jurat.place_line.lower(), case_data.attestation_place, affidavit.jurat.place_line, "CaseData.attestation_place"),
        ("attestation_date", "2026" in affidavit.jurat.date_line and "september" in affidavit.jurat.date_line.lower(), case_data.attestation_date, affidavit.jurat.date_line, "CaseData.attestation_date"),
        ("advocate", case_data.advocate.firm_name.lower() in affidavit.advocate_block.firm_name.lower(), case_data.advocate.firm_name, affidavit.advocate_block.firm_name, "CaseData.advocate.firm_name"),
    ]

    ent_issues: List[EvaluationIssue] = []
    passed_entities = 0
    for name, passed, exp, act, src in entity_checks:
        if passed:
            passed_entities += 1
        else:
            issue = EvaluationIssue(
                dimension="Entity Accuracy",
                severity="error",
                description=f"Entity '{name}' does not match CaseData.",
                expected=str(exp),
                actual=str(act),
                source=src,
            )
            ent_issues.append(issue)
            all_issues.append(issue)

    ent_score = round((passed_entities / len(entity_checks)) * DIMENSION_WEIGHTS["Entity Accuracy"], 2)
    dim_entity = EvaluationDimension(
        name="Entity Accuracy",
        score=ent_score,
        max_score=DIMENSION_WEIGHTS["Entity Accuracy"],
        percentage=round((ent_score / DIMENSION_WEIGHTS["Entity Accuracy"]) * 100, 2),
        explanation=f"Preserved {passed_entities} of {len(entity_checks)} key case entities correctly.",
        issues=ent_issues,
        supporting_checks=["case_identity", "deponent_identity", "advocate_information", "date_place_consistency"],
    )

    # ----------------------------------------------------
    # 2. COMPLETENESS (15 Points)
    # Checks coverage of all 6 reply points, prayer, exhibit, advocate
    # ----------------------------------------------------
    all_body_text = " ".join(p.text for p in affidavit.body_paragraphs)
    completeness_checks = [
        ("point_1_filing", "filing this affidavit" in all_body_text.lower() or "oppose the contentions" in all_body_text.lower(), "Point 1: Filing & Opposition", "CaseData.reply_points[0]"),
        ("point_2_denial", "denies all statements" in all_body_text.lower() or "deny each and every" in all_body_text.lower(), "Point 2: General Denial", "CaseData.reply_points[1]"),
        ("point_3_preliminary", "misconceived" in all_body_text.lower() and "redevelopment procedure" in all_body_text.lower(), "Point 3: Preliminary Position", "CaseData.reply_points[2]"),
        ("point_4_communication_denial", "communication dated 15 july 2026" in all_body_text.lower() and "without authority" in all_body_text.lower(), "Point 4: Denial of Lack of Authority", "CaseData.reply_points[3]"),
        ("point_5_communication_authority", "redevelopment procedure" in all_body_text.lower() and "relevant records" in all_body_text.lower(), "Point 5: Authority & Relevant Records", "CaseData.reply_points[4]"),
        ("point_6_document_relied", "exhibit-‘a’" in all_body_text.lower() or "exhibit-'a'" in all_body_text.lower() or "exhibit 'a'" in all_body_text.lower(), "Point 6: Document Relied Upon (EXHIBIT-‘A’)", "CaseData.reply_points[5]"),
        ("prayer_relief", "dismiss the present writ petition with costs" in affidavit.prayer.items[0].text.lower(), "Dismissal with costs", "CaseData.prayer"),
        ("advocate_coverage", "rajan & associates" in affidavit.advocate_block.firm_name.lower(), "Rajan & Associates block", "CaseData.advocate"),
    ]

    comp_issues: List[EvaluationIssue] = []
    passed_comp = 0
    for name, passed, exp, src in completeness_checks:
        if passed:
            passed_comp += 1
        else:
            issue = EvaluationIssue(
                dimension="Completeness",
                severity="error",
                description=f"Required content element '{name}' missing from generated affidavit.",
                expected=exp,
                actual="Missing in generated content",
                source=src,
            )
            comp_issues.append(issue)
            all_issues.append(issue)

    comp_score = round((passed_comp / len(completeness_checks)) * DIMENSION_WEIGHTS["Completeness"], 2)
    dim_completeness = EvaluationDimension(
        name="Completeness",
        score=comp_score,
        max_score=DIMENSION_WEIGHTS["Completeness"],
        percentage=round((comp_score / DIMENSION_WEIGHTS["Completeness"]) * 100, 2),
        explanation=f"Covered {passed_comp} of {len(completeness_checks)} mandatory case points and elements.",
        issues=comp_issues,
        supporting_checks=["exhibit_consistency", "prayer_separation", "advocate_information"],
    )

    # ----------------------------------------------------
    # 3. STRUCTURE (15 Points)
    # Required sections, order, 7 paragraphs, continuous numbering, prayer separation, verification range
    # ----------------------------------------------------
    struct_checks = [
        ("required_sections", val_checks_dict.get("required_sections", None)),
        ("section_order", val_checks_dict.get("section_order", None)),
        ("body_paragraph_count", val_checks_dict.get("body_paragraph_count", None)),
        ("continuous_numbering", val_checks_dict.get("continuous_numbering", None)),
        ("prayer_separation", val_checks_dict.get("prayer_separation", None)),
        ("verification_range", val_checks_dict.get("verification_range", None)),
    ]

    struct_issues: List[EvaluationIssue] = []
    passed_struct = 0
    for name, val_c in struct_checks:
        if val_c and val_c.passed:
            passed_struct += 1
        else:
            issue = EvaluationIssue(
                dimension="Structure",
                severity="error",
                description=val_c.message if val_c else f"Structural check '{name}' failed",
                expected=val_c.expected if val_c else "Valid structural layout",
                actual=val_c.actual if val_c else "Failed",
                source=val_c.source if val_c else f"TemplateSpecification.{name}",
            )
            struct_issues.append(issue)
            all_issues.append(issue)

    struct_score = round((passed_struct / len(struct_checks)) * DIMENSION_WEIGHTS["Structure"], 2)
    dim_structure = EvaluationDimension(
        name="Structure",
        score=struct_score,
        max_score=DIMENSION_WEIGHTS["Structure"],
        percentage=round((struct_score / DIMENSION_WEIGHTS["Structure"]) * 100, 2),
        explanation=f"Passed {passed_struct} of {len(struct_checks)} structural requirements.",
        issues=struct_issues,
        supporting_checks=[name for name, _ in struct_checks],
    )

    # ----------------------------------------------------
    # 4. CONSISTENCY (15 Points)
    # Internal consistency: respondent number, deponent identity, verb agreement, date/place, case identity
    # ----------------------------------------------------
    consistency_checks = [
        ("respondent_number_consistency", val_checks_dict.get("respondent_number_consistency", None)),
        ("deponent_identity", val_checks_dict.get("deponent_identity", None)),
        ("verb_agreement", val_checks_dict.get("verb_agreement", None)),
        ("date_place_consistency", val_checks_dict.get("date_place_consistency", None)),
        ("case_identity", val_checks_dict.get("case_identity", None)),
    ]

    consist_issues: List[EvaluationIssue] = []
    passed_consist = 0
    for name, val_c in consistency_checks:
        if val_c and val_c.passed:
            passed_consist += 1
        else:
            issue = EvaluationIssue(
                dimension="Consistency",
                severity="error",
                description=val_c.message if val_c else f"Consistency check '{name}' failed",
                expected=val_c.expected if val_c else "Consistent values",
                actual=val_c.actual if val_c else "Inconsistent",
                source=val_c.source if val_c else f"CriticalRules.{name}",
            )
            consist_issues.append(issue)
            all_issues.append(issue)

    consist_score = round((passed_consist / len(consistency_checks)) * DIMENSION_WEIGHTS["Consistency"], 2)
    dim_consistency = EvaluationDimension(
        name="Consistency",
        score=consist_score,
        max_score=DIMENSION_WEIGHTS["Consistency"],
        percentage=round((consist_score / DIMENSION_WEIGHTS["Consistency"]) * 100, 2),
        explanation=f"Passed {passed_consist} of {len(consistency_checks)} internal consistency checks.",
        issues=consist_issues,
        supporting_checks=[name for name, _ in consistency_checks],
    )

    # ----------------------------------------------------
    # 5. TEMPLATE FIDELITY (20 Points)
    # Compliance with TemplateSpecification rules, conventions, and formatting
    # ----------------------------------------------------
    fidelity_checks = [
        ("required_sections", val_checks_dict.get("required_sections", None)),
        ("section_order", val_checks_dict.get("section_order", None)),
        ("respondent_in_title", val_checks_dict.get("respondent_number_consistency", None)),
        ("deponent_clause_form", val_checks_dict.get("deponent_identity", None)),
        ("continuous_numbering", val_checks_dict.get("continuous_numbering", None)),
        ("prayer_separation", val_checks_dict.get("prayer_separation", None)),
        ("verification_range", val_checks_dict.get("verification_range", None)),
        ("verb_agreement", val_checks_dict.get("verb_agreement", None)),
    ]

    fid_issues: List[EvaluationIssue] = []
    passed_fid = 0
    for name, val_c in fidelity_checks:
        if val_c and val_c.passed:
            passed_fid += 1
        else:
            issue = EvaluationIssue(
                dimension="Template Fidelity",
                severity="error",
                description=val_c.message if val_c else f"Template fidelity check '{name}' failed",
                expected=val_c.expected if val_c else "Template rule adherence",
                actual=val_c.actual if val_c else "Non-compliant",
                source=val_c.source if val_c else f"TemplateSpecification.{name}",
            )
            fid_issues.append(issue)
            all_issues.append(issue)

    fid_score = round((passed_fid / len(fidelity_checks)) * DIMENSION_WEIGHTS["Template Fidelity"], 2)
    dim_fidelity = EvaluationDimension(
        name="Template Fidelity",
        score=fid_score,
        max_score=DIMENSION_WEIGHTS["Template Fidelity"],
        percentage=round((fid_score / DIMENSION_WEIGHTS["Template Fidelity"]) * 100, 2),
        explanation=f"Adheres to {passed_fid} of {len(fidelity_checks)} template rules and legal conventions.",
        issues=fid_issues,
        supporting_checks=[name for name, _ in fidelity_checks],
    )

    # ----------------------------------------------------
    # 6. HALLUCINATION (15 Points)
    # Rewards absence of unsupported facts, sample data leakage, unprovided legal rights
    # ----------------------------------------------------
    hallucination_checks = [
        ("sample_data_leakage", val_checks_dict.get("sample_data_leakage", None)),
        ("unsupported_content_check", val_checks_dict.get("unsupported_content_check", None)),
    ]

    halluc_issues: List[EvaluationIssue] = []
    passed_halluc = 0
    for name, val_c in hallucination_checks:
        if val_c and val_c.passed:
            passed_halluc += 1
        else:
            issue = EvaluationIssue(
                dimension="Hallucination",
                severity="error",
                description=val_c.message if val_c else f"Hallucination check '{name}' failed",
                expected="Zero sample facts or unsupported legal claims",
                actual=val_c.actual if val_c else "Detected unsupported content",
                source=val_c.source if val_c else "HallucinationGuard",
            )
            halluc_issues.append(issue)
            all_issues.append(issue)

    halluc_score = round((passed_halluc / len(hallucination_checks)) * DIMENSION_WEIGHTS["Hallucination"], 2)
    dim_hallucination = EvaluationDimension(
        name="Hallucination",
        score=halluc_score,
        max_score=DIMENSION_WEIGHTS["Hallucination"],
        percentage=round((halluc_score / DIMENSION_WEIGHTS["Hallucination"]) * 100, 2),
        explanation=f"Passed {passed_halluc} of {len(hallucination_checks)} deterministic hallucination & factual whitelist checks.",
        issues=halluc_issues,
        supporting_checks=["sample_data_leakage", "unsupported_content_check"],
    )

    dimensions = [
        dim_entity,
        dim_completeness,
        dim_structure,
        dim_consistency,
        dim_fidelity,
        dim_hallucination,
    ]

    overall_score = round(sum(d.score for d in dimensions), 2)
    overall_percentage = round((overall_score / 100.0) * 100.0, 2)

    limitations_text = (
        "Deterministic checks can identify known classes of errors (such as sample fact leakage, "
        "mismatched entity names, altered paragraph numbering, and known unsupported phrases), but cannot "
        "mathematically prove that a document contains zero subtle semantic distortions. "
        "The system evaluates document fidelity to the supplied source material and template; "
        "it does not provide legal advice or independently verify legal validity under Indian law."
    )

    summary_text = (
        f"Document achieved an overall score of {overall_score}/100.0 ({overall_percentage}%). "
        f"{len(all_issues)} issue(s) detected across 6 evaluation dimensions."
    )

    return EvaluationReport(
        overall_score=overall_score,
        max_score=100.0,
        overall_percentage=overall_percentage,
        dimensions=dimensions,
        issues=all_issues,
        methodology=DIMENSION_WEIGHTS,
        summary=summary_text,
        limitations=limitations_text,
    )


def evaluate_semantic_fidelity(affidavit: GeneratedAffidavit, case_data: CaseData) -> Dict[str, Any]:
    """
    OPTIONAL semantic evaluation layer using an LLM (OpenRouter).
    Compares the generated affidavit against CaseData to flag substantive distortions.
    Gracefully falls back if API key is not present or network call fails.
    """
    try:
        from src.llm_client import get_llm_client
        client, model = get_llm_client()
    except Exception as exc:
        return {
            "available": False,
            "reason": f"Semantic evaluator skipped: {exc}",
            "findings": []
        }

    case_data_summary = case_data.model_dump_json(indent=2)
    affidavit_summary = affidavit.model_dump_json(indent=2)

    prompt = f"""Compare this Generated Affidavit against the source CaseData.

STRICT INSTRUCTIONS:
- CaseData is the ONLY source of truth.
- Do NOT use outside legal knowledge.
- Do NOT penalize harmless legal formatting or standard introductory phrases.
- Flag ONLY substantive factual additions, omitted source facts, altered entities, or invented assertions.

CaseData:
{case_data_summary}

Generated Affidavit:
{affidavit_summary}

Return JSON:
{{
  "semantic_alignment_score": <number 0-100>,
  "findings": [<list of substantive factual discrepancies, if any>],
  "reasoning": "<brief explanation>"
}}
"""

    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a legal document auditor checking for factual divergence."},
                {"role": "user", "content": prompt}
            ]
        )
        content = response.choices[0].message.content
        result = json.loads(content)
        result["available"] = True
        return result
    except Exception as exc:
        return {
            "available": False,
            "reason": f"Semantic evaluation call failed: {exc}",
            "findings": []
        }
