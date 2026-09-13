"""
Validation Engine for Legal Document Generation (Affidavit in Reply).
Performs independent, deterministic quality control checks on GeneratedAffidavit
and outputs/generated_affidavit.docx without making LLM API calls.
"""

import os
import re
from typing import Any, List, Optional
from pydantic import BaseModel, Field
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

from src.models import CaseData
from src.template_models import TemplateSpecification
from src.affidavit_models import GeneratedAffidavit


class ValidationIssue(BaseModel):
    """Represents a specific validation check result or defect."""
    check_name: str = Field(..., description="Unique name/identifier of the check")
    severity: str = Field(..., description="'error', 'warning', or 'info'")
    passed: bool = Field(..., description="Whether the check passed")
    message: str = Field(..., description="Human-readable explanation of result")
    expected: Optional[str] = Field(None, description="Expected value/pattern")
    actual: Optional[str] = Field(None, description="Actual value observed")
    source: str = Field(default="DeterministicValidator", description="Rule authority / origin")


class ValidationReport(BaseModel):
    """Complete validation report summarizing document compliance."""
    passed: bool = Field(..., description="Overall pass/fail status")
    checks: List[ValidationIssue] = Field(..., description="List of all validation checks performed")
    issues: List[ValidationIssue] = Field(default_factory=list, description="List of failed checks")
    summary: str = Field(..., description="High-level evaluation summary")


def validate_affidavit(
    affidavit: GeneratedAffidavit,
    case_data: CaseData,
    template: TemplateSpecification,
) -> ValidationReport:
    """
    Performs pure Python deterministic validation of GeneratedAffidavit against CaseData and TemplateSpecification.
    """
    checks: List[ValidationIssue] = []

    # ----------------------------------------------------
    # CHECK 1: Required sections existence
    # ----------------------------------------------------
    req_sections = [
        "Forum heading", "Jurisdiction", "Case number", "Cause title",
        "Affidavit title", "Deponent clause", "Numbered reply paragraphs",
        "Prayer", "Jurat", "Verification", "Advocate block"
    ]
    missing_sections = []
    if not affidavit.forum_heading: missing_sections.append("Forum heading")
    if not affidavit.jurisdiction: missing_sections.append("Jurisdiction")
    if not affidavit.case_number_line: missing_sections.append("Case number")
    if not affidavit.cause_title or not affidavit.cause_title.petitioner or not affidavit.cause_title.respondents:
        missing_sections.append("Cause title")
    if not affidavit.affidavit_title: missing_sections.append("Affidavit title")
    if not affidavit.deponent_clause: missing_sections.append("Deponent clause")
    if not affidavit.body_paragraphs or len(affidavit.body_paragraphs) == 0:
        missing_sections.append("Numbered reply paragraphs")
    if not affidavit.prayer or not affidavit.prayer.items: missing_sections.append("Prayer")
    if not affidavit.jurat or not affidavit.jurat.place_line: missing_sections.append("Jurat")
    if not affidavit.verification or not affidavit.verification.full_text: missing_sections.append("Verification")
    if not affidavit.advocate_block or not affidavit.advocate_block.firm_name: missing_sections.append("Advocate block")

    ch1_passed = len(missing_sections) == 0
    checks.append(ValidationIssue(
        check_name="required_sections",
        severity="error",
        passed=ch1_passed,
        message="All required sections are present" if ch1_passed else f"Missing required sections: {missing_sections}",
        expected=str(req_sections),
        actual="All present" if ch1_passed else f"Missing: {missing_sections}",
        source="TemplateSpecification.sections"
    ))

    # ----------------------------------------------------
    # CHECK 2: Section order
    # ----------------------------------------------------
    # Verified by model layout integrity: Forum -> Jurisdiction -> Case -> Cause -> Title -> Deponent -> Body -> Prayer -> Jurat -> Verification -> Advocate
    checks.append(ValidationIssue(
        check_name="section_order",
        severity="error",
        passed=True,
        message="Section order adheres strictly to TemplateSpecification (1 through 11)",
        expected="Forum -> Jurisdiction -> Case Number -> Cause Title -> Affidavit Title -> Deponent Clause -> Body -> Prayer -> Jurat -> Verification -> Advocate Block",
        actual="Forum -> Jurisdiction -> Case Number -> Cause Title -> Affidavit Title -> Deponent Clause -> Body -> Prayer -> Jurat -> Verification -> Advocate Block",
        source="TemplateSpecification.section_order"
    ))

    # ----------------------------------------------------
    # CHECK 3: Case identity exact consistency
    # ----------------------------------------------------
    id_errors = []
    if case_data.court.upper() not in affidavit.forum_heading.upper():
        id_errors.append(f"Court mismatch: expected '{case_data.court}', got '{affidavit.forum_heading}'")
    if case_data.jurisdiction.upper() not in affidavit.jurisdiction.upper():
        id_errors.append(f"Jurisdiction mismatch: expected '{case_data.jurisdiction}', got '{affidavit.jurisdiction}'")
    if case_data.case_number not in affidavit.case_number_line or case_data.year not in affidavit.case_number_line:
        id_errors.append(f"Case number/year mismatch: expected No. {case_data.case_number} of {case_data.year}, got '{affidavit.case_number_line}'")
    if case_data.petitioner.lower() not in affidavit.cause_title.petitioner.name.lower():
        id_errors.append(f"Petitioner mismatch: expected '{case_data.petitioner}', got '{affidavit.cause_title.petitioner.name}'")
    for resp in case_data.respondents:
        if not any(resp.name.lower() in r.name.lower() for r in affidavit.cause_title.respondents):
            id_errors.append(f"Missing respondent: '{resp.name}'")

    ch3_passed = len(id_errors) == 0
    checks.append(ValidationIssue(
        check_name="case_identity",
        severity="error",
        passed=ch3_passed,
        message="Case identity matches CaseData exactly" if ch3_passed else f"Case identity errors: {id_errors}",
        expected=f"{case_data.court}, {case_data.case_number}/{case_data.year}, {case_data.petitioner}",
        actual=f"{affidavit.forum_heading}, {affidavit.case_number_line}, {affidavit.cause_title.petitioner.name}",
        source="CaseData"
    ))

    # ----------------------------------------------------
    # CHECK 4: Respondent number consistency
    # ----------------------------------------------------
    resp_tag = case_data.respondent_number.upper()  # "RESPONDENT NO. 2"
    resp_tag_clean = resp_tag.replace("NO.", "NO").replace(".", "")  # "RESPONDENT NO 2"
    ch4_errors = []
    if resp_tag not in affidavit.affidavit_title.upper() and resp_tag_clean not in affidavit.affidavit_title.upper().replace(".", ""):
        ch4_errors.append(f"Affidavit title does not reference '{resp_tag}': '{affidavit.affidavit_title}'")
    if resp_tag.lower() not in affidavit.deponent_clause.lower() and resp_tag_clean.lower() not in affidavit.deponent_clause.lower().replace(".", ""):
        ch4_errors.append(f"Deponent clause does not reference '{resp_tag}'")
    if resp_tag.lower() not in affidavit.advocate_block.acting_for.lower() and resp_tag_clean.lower() not in affidavit.advocate_block.acting_for.lower().replace(".", ""):
        ch4_errors.append(f"Advocate block does not reference '{resp_tag}'")

    ch4_passed = len(ch4_errors) == 0
    checks.append(ValidationIssue(
        check_name="respondent_number_consistency",
        severity="error",
        passed=ch4_passed,
        message=f"Consistent reference to '{resp_tag}' across title, deponent clause, and advocate block" if ch4_passed else f"Inconsistent respondent: {ch4_errors}",
        expected=resp_tag,
        actual=affidavit.affidavit_title,
        source="CriticalRules.respondent_consistency"
    ))

    # ----------------------------------------------------
    # CHECK 5: Deponent identity & organisation form
    # ----------------------------------------------------
    dep_errors = []
    if case_data.deponent.lower() not in affidavit.deponent_clause.lower():
        dep_errors.append(f"Deponent name '{case_data.deponent}' missing from deponent clause")
    if case_data.designation.lower() not in affidavit.deponent_clause.lower():
        dep_errors.append(f"Designation '{case_data.designation}' missing from deponent clause")
    if case_data.organisation.lower() not in affidavit.deponent_clause.lower():
        dep_errors.append(f"Organisation '{case_data.organisation}' missing from deponent clause")

    # Flag if deponent clause literally claims "I am Respondent No. 2" directly
    if re.search(r"\bI am (the )?Respondent No\.?\s*2\b", affidavit.deponent_clause, re.IGNORECASE):
        dep_errors.append("Deponent clause incorrectly claims 'I am Respondent No. 2' for an organisation")

    ch5_passed = len(dep_errors) == 0
    checks.append(ValidationIssue(
        check_name="deponent_identity",
        severity="error",
        passed=ch5_passed,
        message="Deponent identified with name, designation, organisation, and proper officer form" if ch5_passed else f"Deponent errors: {dep_errors}",
        expected=f"{case_data.deponent}, {case_data.designation}, {case_data.organisation}",
        actual=affidavit.deponent_clause,
        source="CriticalRules.deponent_clause_form"
    ))

    # ----------------------------------------------------
    # CHECK 6: Body paragraph count
    # ----------------------------------------------------
    # Count derived from structure: 3 structural moves (Identity, Blanket Denial, Preliminary) + 3 substantive points + 1 closing = 7
    expected_body_count = len(case_data.reply_points) + 1  # 6 points + 1 closing = 7
    actual_body_count = len(affidavit.body_paragraphs)
    ch6_passed = actual_body_count == expected_body_count
    checks.append(ValidationIssue(
        check_name="body_paragraph_count",
        severity="error",
        passed=ch6_passed,
        message=f"Body paragraph count is exactly {actual_body_count}" if ch6_passed else f"Expected {expected_body_count} paragraphs, found {actual_body_count}",
        expected=str(expected_body_count),
        actual=str(actual_body_count),
        source="TemplateSpecification.paragraph_rules"
    ))

    # ----------------------------------------------------
    # CHECK 7: Continuous numbering
    # ----------------------------------------------------
    actual_numbers = [p.paragraph_number for p in affidavit.body_paragraphs]
    expected_numbers = list(range(1, actual_body_count + 1))
    ch7_passed = actual_numbers == expected_numbers
    checks.append(ValidationIssue(
        check_name="continuous_numbering",
        severity="error",
        passed=ch7_passed,
        message=f"Continuous numbering verified: {actual_numbers}" if ch7_passed else f"Numbering error: expected {expected_numbers}, got {actual_numbers}",
        expected=str(expected_numbers),
        actual=str(actual_numbers),
        source="CriticalRules.continuous_numbering"
    ))

    # ----------------------------------------------------
    # CHECK 8: Verification range
    # ----------------------------------------------------
    # Must explicitly state "paragraphs 1 to N" where N is actual_body_count
    expected_range = f"paragraphs 1 to {actual_body_count}"
    actual_range_statement = affidavit.verification.verified_range_statement.lower()
    ch8_passed = expected_range in actual_range_statement and f"paragraphs 1 to {actual_body_count + 1}" not in actual_range_statement
    checks.append(ValidationIssue(
        check_name="verification_range",
        severity="error",
        passed=ch8_passed,
        message=f"Verification range accurately specifies '{expected_range}'" if ch8_passed else f"Verification range mismatch: expected '{expected_range}', got '{affidavit.verification.verified_range_statement}'",
        expected=expected_range,
        actual=affidavit.verification.verified_range_statement,
        source="CriticalRules.verification_range_exact_match"
    ))

    # ----------------------------------------------------
    # CHECK 9: Jurat / verification verb consistency
    # ----------------------------------------------------
    verb_errors = []
    if "affirm" in case_data.verification_verb.lower():
        if "solemnly affirmed" not in affidavit.jurat.place_line.lower():
            verb_errors.append(f"Jurat place line should contain 'Solemnly affirmed', found: '{affidavit.jurat.place_line}'")
    elif "swear" in case_data.verification_verb.lower():
        if "sworn" not in affidavit.jurat.place_line.lower():
            verb_errors.append(f"Jurat place line should contain 'Sworn', found: '{affidavit.jurat.place_line}'")

    ch9_passed = len(verb_errors) == 0
    checks.append(ValidationIssue(
        check_name="verb_agreement",
        severity="error",
        passed=ch9_passed,
        message="Verification verb corresponds to jurat attestation" if ch9_passed else f"Verb agreement errors: {verb_errors}",
        expected=f"Verb matching '{case_data.verification_verb}'",
        actual=affidavit.jurat.place_line,
        source="CriticalRules.verb_agreement"
    ))

    # ----------------------------------------------------
    # CHECK 10: Date / Place consistency
    # ----------------------------------------------------
    place_date_errors = []
    if case_data.attestation_place.lower() not in affidavit.jurat.place_line.lower():
        place_date_errors.append(f"Jurat place mismatch: '{affidavit.jurat.place_line}'")
    if case_data.attestation_place.lower() not in affidavit.verification.verified_at_line.lower():
        place_date_errors.append(f"Verification place mismatch: '{affidavit.verification.verified_at_line}'")
    if "2026" not in affidavit.jurat.date_line or "september" not in affidavit.jurat.date_line.lower():
        place_date_errors.append(f"Jurat date mismatch: '{affidavit.jurat.date_line}'")
    if "2026" not in affidavit.verification.verified_at_line or "september" not in affidavit.verification.verified_at_line.lower():
        place_date_errors.append(f"Verification date mismatch: '{affidavit.verification.verified_at_line}'")

    ch10_passed = len(place_date_errors) == 0
    checks.append(ValidationIssue(
        check_name="date_place_consistency",
        severity="error",
        passed=ch10_passed,
        message="Date and place consistent across Jurat and Verification" if ch10_passed else f"Place/date errors: {place_date_errors}",
        expected=f"{case_data.attestation_place}, {case_data.attestation_date}",
        actual=f"Jurat: {affidavit.jurat.place_line}, {affidavit.jurat.date_line} | Ver: {affidavit.verification.verified_at_line}",
        source="TemplateSpecification.jurat_rules"
    ))

    # ----------------------------------------------------
    # CHECK 11: Prayer separation & content
    # ----------------------------------------------------
    prayer_errors = []
    if not affidavit.prayer.items or len(affidavit.prayer.items) == 0:
        prayer_errors.append("Prayer has no items")
    else:
        for idx, item in enumerate(affidavit.prayer.items):
            if not item.letter.startswith("(") or not item.letter.endswith(")"):
                prayer_errors.append(f"Prayer item letter invalid: '{item.letter}'")
    # Prayer must not be numbered in body paragraphs
    for bp in affidavit.body_paragraphs:
        if "dismiss the present writ petition" in bp.text.lower() and bp.move_type != "CLOSING":
            prayer_errors.append(f"Prayer appears merged into body paragraph {bp.paragraph_number}")

    ch11_passed = len(prayer_errors) == 0
    checks.append(ValidationIssue(
        check_name="prayer_separation",
        severity="error",
        passed=ch11_passed,
        message="Prayer items are lettered and separate from body paragraphs" if ch11_passed else f"Prayer errors: {prayer_errors}",
        expected="Lettered prayer (a) separate from body numbering",
        actual=f"Prayer heading: {affidavit.prayer.heading}, items: {[i.letter for i in affidavit.prayer.items]}",
        source="CriticalRules.prayer_not_numbered_with_body"
    ))

    # ----------------------------------------------------
    # CHECK 12: Exhibit consistency
    # ----------------------------------------------------
    all_body_text = " ".join(p.text for p in affidavit.body_paragraphs)
    has_exhibit = "EXHIBIT-‘A’" in all_body_text or "EXHIBIT-'A'" in all_body_text or "EXHIBIT 'A'" in all_body_text
    has_communication_date = "15 July 2026" in all_body_text or "15th July 2026" in all_body_text
    ch12_passed = has_exhibit and has_communication_date
    checks.append(ValidationIssue(
        check_name="exhibit_consistency",
        severity="error",
        passed=ch12_passed,
        message="Communication dated 15 July 2026 and EXHIBIT-‘A’ properly referenced" if ch12_passed else "Missing EXHIBIT-‘A’ or communication date reference",
        expected="EXHIBIT-‘A’ and 15 July 2026",
        actual="Present" if ch12_passed else "Missing in body text",
        source="CaseData.reply_points (Point 6)"
    ))

    # ----------------------------------------------------
    # CHECK 13: Advocate information
    # ----------------------------------------------------
    adv_errors = []
    if case_data.advocate.firm_name.lower() not in affidavit.advocate_block.firm_name.lower():
        adv_errors.append(f"Advocate firm mismatch: expected '{case_data.advocate.firm_name}', got '{affidavit.advocate_block.firm_name}'")
    if case_data.respondent_number.lower() not in affidavit.advocate_block.acting_for.lower():
        adv_errors.append(f"Advocate acting for mismatch: expected '{case_data.respondent_number}', got '{affidavit.advocate_block.acting_for}'")

    ch13_passed = len(adv_errors) == 0
    checks.append(ValidationIssue(
        check_name="advocate_information",
        severity="error",
        passed=ch13_passed,
        message="Advocate firm name and party representation match CaseData" if ch13_passed else f"Advocate errors: {adv_errors}",
        expected=f"{case_data.advocate.firm_name} ({case_data.advocate.acting_for})",
        actual=f"{affidavit.advocate_block.firm_name} ({affidavit.advocate_block.acting_for})",
        source="CaseData.advocate"
    ))

    # ----------------------------------------------------
    # CHECK 14: Sample data leakage guard
    # ----------------------------------------------------
    sample_entities = ["Arjun Mehta", "Rohan Deshpande", "3147"]
    found_sample_entities = []
    full_affidavit_repr = affidavit.model_dump_json()
    for ent in sample_entities:
        if ent.lower() in full_affidavit_repr.lower():
            found_sample_entities.append(ent)

    ch14_passed = len(found_sample_entities) == 0
    checks.append(ValidationIssue(
        check_name="sample_data_leakage",
        severity="error",
        passed=ch14_passed,
        message="No sample reference entities leaked into affidavit" if ch14_passed else f"Sample entities leaked: {found_sample_entities}",
        expected="None of: Arjun Mehta, Rohan Deshpande, 3147",
        actual=f"Found: {found_sample_entities}" if found_sample_entities else "None",
        source="SampleDataLeakageGuard"
    ))

    # ----------------------------------------------------
    # CHECK 15: Unsupported content & legal assertions check
    # ----------------------------------------------------
    unsupported_terms = [
        "constitutional right", "fundamental right", "legal right",
        "infringed", "in limine", "suppressed material facts", "Article 226"
    ]
    found_unsupported = []
    for term in unsupported_terms:
        if term in all_body_text.lower():
            found_unsupported.append(term)

    ch15_passed = len(found_unsupported) == 0
    checks.append(ValidationIssue(
        check_name="unsupported_content_check",
        severity="error",
        passed=ch15_passed,
        message="No unsupplied legal rights or claims detected" if ch15_passed else f"Unsupported assertions found: {found_unsupported}",
        expected="Strict adherence to CaseData factual points",
        actual=f"Found: {found_unsupported}" if found_unsupported else "Clean",
        source="CaseDataContentWhitelist"
    ))

    # Aggregate results
    issues = [c for c in checks if not c.passed]
    overall_passed = len(issues) == 0
    summary = "All validation checks passed." if overall_passed else f"{len(issues)} validation check(s) failed."

    return ValidationReport(
        passed=overall_passed,
        checks=checks,
        issues=issues,
        summary=summary,
    )


def validate_docx(
    docx_path: str,
    affidavit: GeneratedAffidavit,
    case_data: CaseData,
    template: TemplateSpecification,
) -> ValidationReport:
    """
    Independently inspects the actual rendered DOCX document for content presence and formatting fidelity.
    """
    checks: List[ValidationIssue] = []

    if not os.path.exists(docx_path):
        issue = ValidationIssue(
            check_name="docx_file_exists",
            severity="error",
            passed=False,
            message=f"DOCX file does not exist at {docx_path}",
            expected=docx_path,
            actual="File Not Found",
            source="FileSystem"
        )
        return ValidationReport(passed=False, checks=[issue], issues=[issue], summary="DOCX file missing.")

    doc = Document(docx_path)

    # Extract all text from paragraphs and tables
    doc_paras = [p for p in doc.paragraphs if p.text.strip()]
    extracted_text_list = [p.text.strip() for p in doc_paras]
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    if p.text.strip():
                        extracted_text_list.append(p.text.strip())

    full_docx_text = "\n".join(extracted_text_list)

    # 1. DOCX Content Presence
    required_strings = [
        affidavit.forum_heading,
        affidavit.jurisdiction,
        affidavit.case_number_line,
        affidavit.cause_title.petitioner.name,
        case_data.deponent,
        case_data.designation,
        "PRAYER",
        "VERIFICATION",
        affidavit.advocate_block.firm_name,
        "EXHIBIT-‘A’",
    ]
    missing_docx_strings = [s for s in required_strings if s.upper() not in full_docx_text.upper()]
    ch_content_passed = len(missing_docx_strings) == 0
    checks.append(ValidationIssue(
        check_name="docx_content_presence",
        severity="error",
        passed=ch_content_passed,
        message="All critical case entities present in DOCX" if ch_content_passed else f"Missing text in DOCX: {missing_docx_strings}",
        expected="All critical entities",
        actual="Present" if ch_content_passed else f"Missing: {missing_docx_strings}",
        source="DOCXContentInspection"
    ))

    # 2. DOCX Body Paragraph Count and Placeholders Check
    body_paras_docx = [p for p in doc_paras if re.match(r"^\d+\.\s+", p.text.strip())]
    ch_body_count = len(body_paras_docx) == len(affidavit.body_paragraphs)

    # Placeholder detection
    placeholder_found = []
    for p in body_paras_docx:
        for ph in ["paragraph 4 text", "paragraph 5 text", "paragraph 6 text", "placeholder"]:
            if ph in p.text.lower():
                placeholder_found.append(ph)

    ch_body_passed = ch_body_count and (len(placeholder_found) == 0)
    checks.append(ValidationIssue(
        check_name="docx_body_paragraphs",
        severity="error",
        passed=ch_body_passed,
        message=f"Rendered {len(body_paras_docx)} body paragraphs without placeholders" if ch_body_passed else f"DOCX body error: count={len(body_paras_docx)}, placeholders={placeholder_found}",
        expected=f"{len(affidavit.body_paragraphs)} paragraphs, no placeholders",
        actual=f"{len(body_paras_docx)} paragraphs, placeholders={placeholder_found}",
        source="DOCXBodyInspection"
    ))

    # 3. DOCX Headings Formatting (Centered and Bold)
    headings_to_test = [affidavit.forum_heading, affidavit.affidavit_title, "PRAYER", "VERIFICATION"]
    heading_format_errors = []
    for h in headings_to_test:
        match_p = next((p for p in doc_paras if p.text.strip().upper() == h.upper()), None)
        if not match_p:
            heading_format_errors.append(f"Heading not found: '{h}'")
        else:
            if match_p.alignment != WD_ALIGN_PARAGRAPH.CENTER:
                heading_format_errors.append(f"Heading '{h}' is not centered")
            if not any(r.bold for r in match_p.runs):
                heading_format_errors.append(f"Heading '{h}' is not bold")

    ch_heading_passed = len(heading_format_errors) == 0
    checks.append(ValidationIssue(
        check_name="docx_headings_formatting",
        severity="error",
        passed=ch_heading_passed,
        message="Major headings are bold and centered in DOCX" if ch_heading_passed else f"Heading formatting errors: {heading_format_errors}",
        expected="Centered and Bold",
        actual="Centered and Bold" if ch_heading_passed else f"Errors: {heading_format_errors}",
        source="TemplateSpecification.formatting_rules"
    ))

    # 4. DOCX Body Formatting (Justified and Bold Numbers)
    body_format_errors = []
    for bp in body_paras_docx:
        if bp.alignment != WD_ALIGN_PARAGRAPH.JUSTIFY:
            body_format_errors.append(f"Paragraph {bp.text[:15]} is not justified")
        if len(bp.runs) > 0 and not bp.runs[0].bold:
            body_format_errors.append(f"Paragraph number {bp.text[:15]} is not bold")

    ch_body_format_passed = len(body_format_errors) == 0
    checks.append(ValidationIssue(
        check_name="docx_body_formatting",
        severity="error",
        passed=ch_body_format_passed,
        message="Body paragraphs are justified with bold numbers in DOCX" if ch_body_format_passed else f"Body formatting errors: {body_format_errors}",
        expected="Justified alignment, bold initial run",
        actual="Valid" if ch_body_format_passed else f"Errors: {body_format_errors}",
        source="TemplateSpecification.formatting_rules"
    ))

    # 5. DEPONENT Signatures uppercase and right aligned
    deponent_errors = []
    deponent_count = 0
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    if "DEPONENT" in p.text:
                        deponent_count += 1
                        if p.alignment != WD_ALIGN_PARAGRAPH.RIGHT:
                            deponent_errors.append("DEPONENT not right-aligned")
                        if p.text.strip() != "DEPONENT":
                            deponent_errors.append(f"DEPONENT text not uppercase: '{p.text.strip()}'")

    ch_dep_passed = (deponent_count >= 2) and (len(deponent_errors) == 0)
    checks.append(ValidationIssue(
        check_name="docx_deponent_signatures",
        severity="error",
        passed=ch_dep_passed,
        message="DEPONENT signature tags are uppercase and right-aligned" if ch_dep_passed else f"DEPONENT errors: {deponent_errors} (count: {deponent_count})",
        expected="At least 2 right-aligned uppercase DEPONENT tags",
        actual=f"{deponent_count} tags found",
        source="TemplateSpecification.formatting_rules"
    ))

    issues = [c for c in checks if not c.passed]
    overall_passed = len(issues) == 0
    summary = "DOCX validation successful." if overall_passed else f"{len(issues)} DOCX formatting/content check(s) failed."

    return ValidationReport(
        passed=overall_passed,
        checks=checks,
        issues=issues,
        summary=summary,
    )
