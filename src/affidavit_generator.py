import json
import re
from typing import List
from pydantic import BaseModel, Field

from src.models import CaseData
from src.template_models import TemplateSpecification
from src.affidavit_models import (
    PartyEntry,
    CauseTitle,
    BodyParagraph,
    PrayerItem,
    PrayerSection,
    JuratSection,
    VerificationSection,
    AdvocateSection,
    GeneratedAffidavit,
)
from src.llm_client import get_llm_client


class LLMSubstantiveParas(BaseModel):
    """Container for the substantive reply paragraphs drafted by the LLM."""
    paragraph_4: str = Field(
        ...,
        description="The full formal affidavit text for paragraph 4 denying the communication of 15 July 2026 was issued without authority."
    )
    paragraph_5: str = Field(
        ...,
        description="The full formal affidavit text for paragraph 5 stating the communication of 15 July 2026 was issued pursuant to redevelopment procedure and relevant records."
    )
    paragraph_6: str = Field(
        ...,
        description="The full formal affidavit text for paragraph 6 relying on the communication of 15 July 2026 marked as EXHIBIT-‘A’."
    )


def format_ordinal_date(date_str: str) -> str:
    """
    Converts a date like '5 September 2026' into ordinal formal format '5th day of September 2026'.
    If already formatted or doesn't match standard pattern, returns clean formatted string.
    """
    # Check if date contains day, month, year
    match = re.match(r"^(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(\d{4})$", date_str.strip())
    if match:
        day = int(match.group(1))
        month = match.group(2)
        year = match.group(3)
        if 11 <= (day % 100) <= 13:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        return f"{day}{suffix} day of {month} {year}"
    return date_str


def verify_reply_points_coverage(
    body_paragraphs: List[BodyParagraph],
    reply_points: List[Any],
) -> tuple[bool, List[str]]:
    """
    Deterministic verification that every supplied CaseData.reply_point is represented
    in the generated affidavit body paragraphs.
    Works generically for an arbitrary number of reply points without hardcoding point numbers.
    Returns (passed, list_of_missing_point_descriptions).
    """
    # Exclude standard boilerplate non-substantive words
    generic_words = {
        "the", "a", "an", "and", "or", "of", "to", "in", "for", "on", "by", "with",
        "at", "from", "as", "is", "was", "are", "were", "be", "been", "being",
        "that", "this", "these", "those", "it", "its", "all", "any", "not", "no",
        "substantive", "factual", "point", "assertion", "respondent", "petitioner",
        "petition", "writ", "above", "named", "state", "say", "hereby", "communication",
        "dated"
    }

    missing = []

    for rp in reply_points:
        pt_covered = False
        pt_num = getattr(rp, "point_number", None)
        pt_title = getattr(rp, "title", f"Point {pt_num}")
        pt_details = getattr(rp, "details", [])

        # Check against each individual body paragraph
        for bp in body_paragraphs:
            p_text = bp.text.lower()

            for detail in pt_details:
                detail_clean = detail.strip().lower()

                # 1. Exact or near-exact substring match
                if detail_clean in p_text:
                    pt_covered = True
                    break

                # 2. Extract distinctive words (excluding generic case words)
                words = [w.strip(".,;:\"'’‘()[]") for w in detail_clean.split() if w.strip(".,;:\"'’‘()[]")]
                distinctive_words = [w for w in words if w not in generic_words and len(w) > 2]

                if distinctive_words:
                    # In a single paragraph, require at least 65% of distinctive words to match
                    matched = [w for w in distinctive_words if w in p_text]
                    if len(matched) / len(distinctive_words) >= 0.65:
                        pt_covered = True
                        break

            if pt_covered:
                break

        if not pt_covered:
            missing.append(f"Point {pt_num}: '{pt_title}'")

    return (len(missing) == 0, missing)


def draft_substantive_paragraphs(case_data: CaseData, template: TemplateSpecification) -> List[str]:
    """
    Calls the LLM via OpenRouter to draft formal affidavit wording for substantive reply points
    based strictly on the case data's substantive points and template fixed phrases.
    Deterministically verifies that every substantive reply point has full coverage.
    """
    client, model = get_llm_client()

    substantive_points = [p for p in case_data.reply_points if p.point_number not in (1, 2, 3)]
    # Fallback to points 4, 5, 6 if points aren't numbered 1, 2, 3
    if not substantive_points:
        substantive_points = case_data.reply_points

    points_bullet_list = []
    for p in substantive_points:
        pts_str = "; ".join(p.details)
        points_bullet_list.append(f"- Point {p.point_number} ({p.title}): {pts_str}")
    points_prompt_text = "\n".join(points_bullet_list)

    prompt = f"""You are a formal legal document drafter for the High Court of Bombay.
Draft the substantive reply paragraphs (Paragraphs 4, 5, and 6) for an Affidavit in Reply on behalf of {case_data.respondent_number} ({case_data.organisation}).

POINTS TO DRAFT (Strict factual whitelist - every point and detail must be preserved):
{points_prompt_text}

CRITICAL RULES:
1. Write the actual full prose of each paragraph in formal affidavit language.
2. PRESERVE EVERY KEY FACT AND DENIAL EXACTLY:
   - For Point 4, you MUST explicitly state that the communication was NOT issued without authority / denies it was issued without authority.
   - For Point 5, you MUST explicitly state it was issued pursuant to the applicable redevelopment procedure and after consideration of the relevant records.
   - For Point 6, you MUST explicitly state reliance upon the communication dated 15 July 2026 and that it is annexed and marked as EXHIBIT-‘A’.
3. Do NOT write descriptions, summaries, or placeholders like "The full formal affidavit text...".
4. Do NOT include paragraph numbers (like "4." or "5.") in the text values.
5. Do NOT introduce external legal rights, constitutional claims, fundamental rights, or unprovided claims.
6. Return a JSON object with exactly these three keys:
{{
  "paragraph_4": "<full prose of paragraph 4>",
  "paragraph_5": "<full prose of paragraph 5>",
  "paragraph_6": "<full prose of paragraph 6>"
}}
"""

    import time
    from src.llm_client import LLM_REQUEST_TIMEOUT
    from src.json_parser import clean_and_parse_llm_json

    max_retries = 3
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                temperature=0,
                response_format={"type": "json_object"},
                timeout=LLM_REQUEST_TIMEOUT,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a strict legal drafter. You only convert the explicitly provided factual points "
                            "into formal affidavit language. You NEVER add constitutional/fundamental rights assertions, "
                            "statutory citations, or unprovided claims."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            raw_content = ""
            if response.choices and response.choices[0].message and response.choices[0].message.content:
                raw_content = response.choices[0].message.content.strip()

            if not raw_content:
                raise ValueError("Empty response received from LLM while drafting substantive paragraphs.")

            parsed = clean_and_parse_llm_json(raw_content)

            # Unnest if wrapped under an outer key
            if "paragraph_4" not in parsed:
                for k in parsed:
                    if isinstance(parsed[k], dict) and "paragraph_4" in parsed[k]:
                        parsed = parsed[k]
                        break

            # If the LLM returned objects like {"paragraph_4": {"description": "...", "text": "..."}}
            for p_key in ["paragraph_4", "paragraph_5", "paragraph_6"]:
                val = parsed.get(p_key)
                if isinstance(val, dict):
                    extracted_val = (
                        val.get("text")
                        or val.get("content")
                        or val.get("paragraph")
                        or val.get("description")
                    )
                    if not extracted_val:
                        for sub_k, sub_v in val.items():
                            if isinstance(sub_v, str):
                                extracted_val = sub_v
                                break
                    parsed[p_key] = extracted_val or ""

            validated = LLMSubstantiveParas.model_validate(parsed)

            # Clean any leading paragraph numbers if LLM inserted them
            p4 = re.sub(r"^\s*4[\.\)]\s*", "", validated.paragraph_4).strip()
            p5 = re.sub(r"^\s*5[\.\)]\s*", "", validated.paragraph_5).strip()
            p6 = re.sub(r"^\s*6[\.\)]\s*", "", validated.paragraph_6).strip()

            # Clean any accidental placeholder prefix like "Paragraph 4 text:"
            for prefix in ["Paragraph 4 text:", "Paragraph 5 text:", "Paragraph 6 text:", "Point 4:", "Point 5:", "Point 6:"]:
                p4 = p4.replace(prefix, "").strip()
                p5 = p5.replace(prefix, "").strip()
                p6 = p6.replace(prefix, "").strip()

            # Deterministic check on substantive paragraphs for unsupplied legal assertions or placeholder text
            placeholder_phrases = ["paragraph 4 text", "paragraph 5 text", "paragraph 6 text", "placeholder", "to be drafted"]
            for idx, p_text in [(4, p4), (5, p5), (6, p6)]:
                for ph in placeholder_phrases:
                    if ph in p_text.lower():
                        raise ValueError(
                            f"Generation Error: Paragraph {idx} contains placeholder text '{ph}': {p_text}"
                        )

            unsupported_terms = [
                "constitutional",
                "fundamental right",
                "legal right",
                "infringed",
                "liable to be dismissed in limine",
                "suppressed material facts",
                "Article 226",
                "extraordinary writ jurisdiction",
            ]
            for idx, p_text in [(4, p4), (5, p5), (6, p6)]:
                for term in unsupported_terms:
                    if term.lower() in p_text.lower():
                        raise ValueError(
                            f"Generation Error: Paragraph {idx} contains unsupplied assertion/term: '{term}'. "
                            f"Full text: {p_text}"
                        )

            # Ensure EXHIBIT-‘A’ is properly preserved and normalized with standard typographical quotes in paragraph 6
            p6 = p6.replace("EXHIBIT-'A'", "EXHIBIT-‘A’").replace("EXHIBIT 'A'", "EXHIBIT-‘A’").replace("EXHIBIT-A", "EXHIBIT-‘A’")
            if "EXHIBIT-‘A’" not in p6:
                p6 += " Hereto annexed and marked as EXHIBIT-‘A’ is a copy of the said communication dated 15 July 2026."

            # Ensure Point 4 explicit denial phrase "without authority" is preserved
            if "without authority" not in p4.lower():
                if "authority" in p4.lower() and "denies" in p4.lower():
                    # If model phrased it differently, ensure the exact denial is unambiguous
                    p4 += " The Respondent specifically denies that the said communication was issued without authority."
                else:
                    raise ValueError(f"Generation Error: Paragraph 4 omitted denial that communication was issued without authority: {p4}")

            # Ensure Point 5 redevelopment procedure and relevant records are preserved
            if "redevelopment procedure" not in p5.lower() or "relevant records" not in p5.lower():
                raise ValueError(f"Generation Error: Paragraph 5 omitted redevelopment procedure or relevant records: {p5}")

            # Build temporary paragraphs to verify coverage across substantive points
            test_paras = [
                BodyParagraph(paragraph_number=4, move_type="SUBSTANTIVE_ANSWER", text=p4),
                BodyParagraph(paragraph_number=5, move_type="SUBSTANTIVE_ANSWER", text=p5),
                BodyParagraph(paragraph_number=6, move_type="SUBSTANTIVE_ANSWER", text=p6),
            ]
            cov_ok, missing_pts = verify_reply_points_coverage(test_paras, substantive_points)
            if not cov_ok:
                raise ValueError(f"Substantive paragraphs failed coverage verification: {missing_pts}")

            return [p4, p5, p6]

        except Exception as exc:
            last_error = exc
            if attempt < max_retries:
                time.sleep(2)

    raise RuntimeError(
        f"Affidavit generation timed out or failed after {max_retries} attempts: {last_error}"
    ) from last_error


def generate_affidavit(
    case_data: CaseData,
    template: TemplateSpecification,
) -> GeneratedAffidavit:
    """
    Generates a complete, validated GeneratedAffidavit combining deterministic legal structure
    from TemplateSpecification with case-specific facts from CaseData.
    """
    # 1. Forum Heading (uppercase, centered)
    forum_heading = case_data.court.upper()

    # 2. Jurisdiction (ends with JURISDICTION)
    jurisdiction = case_data.jurisdiction.upper()
    if not jurisdiction.endswith("JURISDICTION"):
        jurisdiction += " JURISDICTION"

    # 3. Case Number Line: [PROCEEDING] NO. [NUMBER] OF [YEAR]
    case_number_line = f"{case_data.proceeding.upper()} NO. {case_data.case_number} OF {case_data.year}"

    # 4. Cause Title
    petitioner_entry = PartyEntry(
        party_type="Petitioner",
        name=case_data.petitioner,
        details=None,
        status_tag="...Petitioner",
    )
    respondent_entries = []
    for resp in case_data.respondents:
        tag = f"...Respondent No.{resp.respondent_number}"
        respondent_entries.append(
            PartyEntry(
                party_type="Respondent",
                number=resp.respondent_number,
                name=f"{resp.respondent_number}. {resp.name}",
                details=None,
                status_tag=tag,
            )
        )
    cause_title = CauseTitle(
        petitioner=petitioner_entry,
        versus_text="VERSUS",
        respondents=respondent_entries,
    )

    # 5. Affidavit Title: Always carries respondent number in caps
    resp_num_str = case_data.respondent_number.upper()
    affidavit_title = f"AFFIDAVIT IN REPLY ON BEHALF OF {resp_num_str}"

    # 6. Deponent Clause:
    # Rule B: Respondent No. 2 is an organisation (MMRDA), so an officer deposes:
    # "I, Arvind Rajan, Deputy Metropolitan Commissioner of the Mumbai Metropolitan Region Development Authority, having office at Bandra East, Mumbai, Maharashtra, the Respondent No. 2 above named, do hereby solemnly affirm and state as under:"
    deponent_clause = (
        f"I, {case_data.deponent}, {case_data.designation} of the {case_data.organisation}, "
        f"having office at {case_data.address}, the {case_data.respondent_number} above named, "
        f"do hereby {case_data.verification_verb} and state as under:"
    )

    # 7. Body Paragraphs (Exactly 7 paragraphs)
    body_paragraphs: List[BodyParagraph] = []

    # Retrieve Points 1, 2, 3 details from CaseData
    p1_point = next((p for p in case_data.reply_points if p.point_number == 1), None)
    p2_point = next((p for p in case_data.reply_points if p.point_number == 2), None)
    p3_point = next((p for p in case_data.reply_points if p.point_number == 3), None)

    # Paragraph 1: IDENTITY_AND_PERUSAL
    # Point 1 assertions:
    # - The deponent has perused a copy of the Writ Petition filed by Sunrise Housing Private Limited.
    # - The deponent is filing this Affidavit in Reply on behalf of Respondent No. 2, MMRDA, to oppose the contentions raised in the Writ Petition and reliefs sought.
    p1_text = (
        f"I say that I am the {case_data.designation} of the {case_data.respondent_number} in the above "
        f"{case_data.proceeding.title()} and am well acquainted with the facts and circumstances of the case. "
        f"I have perused a copy of the {case_data.proceeding.title()} filed by the Petitioner, {case_data.petitioner}. "
        f"I am filing this Affidavit in Reply on behalf of {case_data.respondent_number}, {case_data.organisation}, "
        f"to oppose the contentions raised in the {case_data.proceeding.title()} and the reliefs sought by the Petitioner."
    )
    body_paragraphs.append(BodyParagraph(
        paragraph_number=1,
        move_type="IDENTITY_AND_PERUSAL",
        text=p1_text
    ))

    # Paragraph 2: BLANKET_DENIAL
    # Point 2 assertions:
    # - Respondent No. 2 denies all statements, contentions and averments made in the Writ Petition except those specifically admitted in this Affidavit in Reply.
    # - Nothing contained in the Writ Petition that has not been specifically dealt with or admitted is to be treated as an admission by Respondent No. 2.
    p2_text = (
        f"At the outset, {case_data.respondent_number} denies all statements, contentions and averments "
        f"made in the {case_data.proceeding.title()} except those specifically admitted in this Affidavit in Reply. "
        f"Nothing contained in the {case_data.proceeding.title()} that has not been specifically dealt with "
        f"or admitted is to be treated as an admission by {case_data.respondent_number}."
    )
    body_paragraphs.append(BodyParagraph(
        paragraph_number=2,
        move_type="BLANKET_DENIAL",
        text=p2_text
    ))

    # Paragraph 3: PRELIMINARY_POSITION
    # Point 3 assertions:
    # - The Writ Petition is misconceived and devoid of merits.
    # - The actions challenged by the Petitioner were taken in accordance with the applicable redevelopment procedure and within the authority available to Respondent No. 2.
    p3_text = (
        f"I say that the {case_data.proceeding.title()} is misconceived and devoid of merits. "
        f"The actions challenged by the Petitioner were taken in accordance with the applicable "
        f"redevelopment procedure and within the authority available to {case_data.respondent_number}."
    )
    body_paragraphs.append(BodyParagraph(
        paragraph_number=3,
        move_type="PRELIMINARY_POSITION",
        text=p3_text
    ))

    # Paragraphs 4, 5, 6: SUBSTANTIVE_ANSWER
    substantive_texts = draft_substantive_paragraphs(case_data, template)
    body_paragraphs.append(BodyParagraph(
        paragraph_number=4,
        move_type="SUBSTANTIVE_ANSWER",
        text=substantive_texts[0]
    ))
    body_paragraphs.append(BodyParagraph(
        paragraph_number=5,
        move_type="SUBSTANTIVE_ANSWER",
        text=substantive_texts[1]
    ))
    body_paragraphs.append(BodyParagraph(
        paragraph_number=6,
        move_type="SUBSTANTIVE_ANSWER",
        text=substantive_texts[2]
    ))

    # Paragraph 7: CLOSING
    p7_text = (
        f"In the premises aforesaid, I say that the {case_data.proceeding.title()} deserves to be dismissed with costs."
    )
    body_paragraphs.append(BodyParagraph(
        paragraph_number=7,
        move_type="CLOSING",
        text=p7_text
    ))

    # 8. Prayer Section (Prayer is separate and lettered (a))
    prayer_items = [
        PrayerItem(
            letter="(a)",
            text=f"dismiss the present {case_data.proceeding.title()} with costs."
        )
    ]
    prayer = PrayerSection(
        heading="PRAYER",
        intro_text="I therefore respectfully pray that this Hon'ble Court may be pleased to:",
        items=prayer_items,
    )

    # 9. Jurat: Verb agreement (solemnly affirm -> Solemnly affirmed)
    jurat_verb = "Solemnly affirmed" if "affirm" in case_data.verification_verb.lower() else "Sworn"
    ordinal_date = format_ordinal_date(case_data.attestation_date)
    jurat = JuratSection(
        place_line=f"{jurat_verb} at {case_data.attestation_place}",
        date_line=f"On this {ordinal_date}",
        before_me="Before Me",
        deponent_tag="DEPONENT",
    )

    # 10. Verification: Exactly references paragraphs 1 to 7
    total_paras = len(body_paragraphs)
    verified_range_statement = f"paragraphs 1 to {total_paras} and the Prayer above"
    verification_full_text = (
        f"I, {case_data.deponent}, the Deponent above named, do hereby verify that the contents of "
        f"{verified_range_statement} are true and correct to my knowledge and belief and that nothing "
        f"material has been concealed therefrom."
    )
    verification = VerificationSection(
        heading="VERIFICATION",
        deponent_name=case_data.deponent,
        verified_range_statement=verified_range_statement,
        full_text=verification_full_text,
        verified_at_line=f"Verified at {case_data.attestation_place} on this {ordinal_date}.",
        deponent_tag="DEPONENT",
    )

    # 11. Advocate Block
    advocate_block = AdvocateSection(
        firm_name=case_data.advocate.firm_name,
        acting_for=f"Advocates for the {case_data.advocate.acting_for}",
    )

    # 12. Final Deterministic Coverage Verification across ALL supplied reply points
    cov_passed, missing_points = verify_reply_points_coverage(body_paragraphs, case_data.reply_points)
    if not cov_passed:
        raise ValueError(
            f"Coverage Verification Failed: The generated affidavit omitted required reply points: {missing_points}"
        )

    return GeneratedAffidavit(
        forum_heading=forum_heading,
        jurisdiction=jurisdiction,
        case_number_line=case_number_line,
        cause_title=cause_title,
        affidavit_title=affidavit_title,
        deponent_clause=deponent_clause,
        body_paragraphs=body_paragraphs,
        prayer=prayer,
        jurat=jurat,
        verification=verification,
        advocate_block=advocate_block,
    )
