"""
Builds the deterministic TemplateSpecification according to inputs/format_explained.pdf
and inputs/sample_affidavit.pdf.
"""

from src.template_models import (
    TemplateSpecification,
    SectionRule,
    ReplyMove,
    EntityRequirement,
    CriticalRules,
)


def build_template_specification() -> TemplateSpecification:
    """
    Constructs the validated, deterministic TemplateSpecification strictly from the
    format_explained.pdf rulebook and sample_affidavit.pdf cross-check.
    """
    sections = [
        SectionRule(
            order=1,
            name="Forum heading",
            required=True,
            purpose="Identifies the court and seat where the proceeding is instituted",
            formatting="Bold, ALL CAPS, centred. First line.",
            important_rules=[
                "First line of document.",
                "Must be bold, uppercase, and centred.",
                "Format: IN THE HIGH COURT OF JUDICATURE AT [CITY]",
            ],
            expected_content="IN THE HIGH COURT OF JUDICATURE AT [CITY]",
        ),
        SectionRule(
            order=2,
            name="Jurisdiction",
            required=True,
            purpose="Identifies the specific side/bench/jurisdiction of the Court",
            formatting="Bold, ALL CAPS, centred.",
            important_rules=[
                "Always ends with the word JURISDICTION.",
                "E.g., Civil Appellate Jurisdiction; Ordinary Original Civil Jurisdiction.",
            ],
            expected_content="[TYPE] JURISDICTION",
        ),
        SectionRule(
            order=3,
            name="Case number",
            required=True,
            purpose="Identifies proceeding type, serial number, and year of the case",
            formatting="Bold, ALL CAPS, centred.",
            important_rules=[
                "'NO.' and 'OF' are fixed words.",
                "Format: [PROCEEDING] NO. [NUMBER] OF [YEAR]",
            ],
            expected_content="[PROCEEDING TYPE] NO. [NUMBER] OF [YEAR]",
        ),
        SectionRule(
            order=4,
            name="Cause title",
            required=True,
            purpose="Sets out party names, descriptions, addresses, and litigation tags",
            formatting="Party names left-aligned; status tags right-aligned; VERSUS centered on its own line.",
            important_rules=[
                "Status tags begin with three dots: '...Petitioner', '...Respondent No.1', '...Respondent No.2'.",
                "VERSUS appears centered on its own line.",
                "Respondents are numbered sequentially: 1., 2., 3.",
            ],
            expected_content="[Petitioner details] ...Petitioner\nVERSUS\n1. [Respondent 1 details] ...Respondent No.1\n2. [Respondent 2 details] ...Respondent No.2",
        ),
        SectionRule(
            order=5,
            name="Affidavit title",
            required=True,
            purpose="Formally declares the document type and on whose behalf it is filed",
            formatting="Bold, ALL CAPS, centred.",
            important_rules=[
                "Must be bold, uppercase, and centred.",
                "CRITICAL: Always carries the specific respondent number, e.g. AFFIDAVIT IN REPLY ON BEHALF OF RESPONDENT NO. [N].",
            ],
            expected_content="AFFIDAVIT IN REPLY ON BEHALF OF RESPONDENT NO. [N]",
        ),
        SectionRule(
            order=6,
            name="Deponent clause",
            required=True,
            purpose="Identifies the deponent, capacity, authority, and invocation of solemn affirmation",
            formatting="Normal text, one single sentence, unnumbered.",
            important_rules=[
                "One single sentence, not numbered.",
                "If respondent is an individual: 'I, [NAME], [age], residing at [ADDRESS], the Respondent No.[N] above named...'",
                "If respondent is an organisation/company/authority: an officer deposes for it: 'I, [NAME], [designation] of the Respondent No.[N] above named...'",
                "CRITICAL: Never write 'I am Respondent No. [N]' when the respondent is an organisation.",
                "Concludes with: 'do hereby solemnly affirm and state as under:' (or swearing verb).",
            ],
            expected_content="I, [DEPONENT NAME], [age / designation], [residing at / having office at] [ADDRESS], [the Respondent No.[N] above named / the [DESIGNATION] of the Respondent No.[N] above named], do hereby solemnly affirm and state as under:",
        ),
        SectionRule(
            order=7,
            name="Numbered reply paragraphs",
            required=True,
            purpose="Substantive factual assertions, denials, preliminary objections, and closing",
            formatting="Paragraph number bold followed by full stop (e.g. 1. 2. 3.). Paragraph body text normal and justified.",
            important_rules=[
                "One continuous numbering sequence.",
                "Prayer is not part of the body sequence.",
                "Follows rhetorical moves: Identity & Perusal -> Blanket Denial -> Preliminary Position -> Substantive Answers -> Closing.",
            ],
            expected_content="1. I say that I am... [Identity and perusal]\n2. At the outset, I deny... [Blanket denial]\n3. I say that... [Preliminary position]\n4. With reference to... [Substantive answer]\n[N]. In the premises aforesaid, I say that the [PROCEEDING] deserves to be dismissed with costs. [Closing]",
        ),
        SectionRule(
            order=8,
            name="Prayer",
            required=True,
            purpose="Formal prayer/reliefs sought from the Hon'ble Court",
            formatting="Heading PRAYER is bold, ALL CAPS, centred. Prayer letters (a), (b), (c) are bold. Body text justified.",
            important_rules=[
                "Heading PRAYER is bold, uppercase, centered.",
                "CRITICAL: Prayer paragraphs are lettered (a), (b), (c), NEVER numbered with the body paragraphs.",
                "Starts with standard introductory clause: 'I therefore respectfully pray that this Hon'ble Court may be pleased to:'",
            ],
            expected_content="PRAYER\nI therefore respectfully pray that this Hon'ble Court may be pleased to:\n(a) dismiss the present [PROCEEDING TYPE] with costs;\n(b) refuse any interim or ad-interim relief sought by the Petitioner; and\n(c) grant such other and further reliefs as this Hon'ble Court may deem fit and proper in the facts and circumstances of the case.",
        ),
        SectionRule(
            order=9,
            name="Jurat",
            required=True,
            purpose="Formal attestation clause reciting place, date of affirmation, and deponent signature line",
            formatting="Attestation lines left-aligned. 'DEPONENT' in ALL CAPS right-aligned. 'Before Me' left-aligned.",
            important_rules=[
                "Attestation text: 'Solemnly affirmed at [PLACE] / On this [Nth] day of [MONTH] [YEAR]'.",
                "Date format: ordinal day + month + year (e.g. 5th day of September 2026).",
                "'DEPONENT' in ALL CAPS and right-aligned.",
                "'Before Me' left-aligned.",
                "CRITICAL: Verb must match Part 6 (e.g. 'solemnly affirm' -> 'Solemnly affirmed'; 'swear' -> 'Sworn').",
            ],
            expected_content="Solemnly affirmed at [PLACE]\nOn this [Nth] day of [MONTH] [YEAR]\nBefore Me\n                                                        DEPONENT",
        ),
        SectionRule(
            order=10,
            name="Verification",
            required=True,
            purpose="Formal verification of truth of contents under personal knowledge and belief",
            formatting="Heading VERIFICATION bold, ALL CAPS, centred. Paragraph text normal and justified. 'DEPONENT' in ALL CAPS right-aligned.",
            important_rules=[
                "Heading VERIFICATION is bold, uppercase, and centred.",
                "CRITICAL: Paragraph range must exactly match actual body paragraph count (e.g. 'contents of paragraphs 1 to [N] and the Prayer above'). Never copy static range from sample.",
                "Place and date repeat the jurat: 'Verified at [PLACE] on this [Nth] day of [MONTH] [YEAR].'",
                "'DEPONENT' right-aligned in uppercase.",
            ],
            expected_content="VERIFICATION\nI, [DEPONENT NAME], the Deponent above named, do hereby verify that the contents of paragraphs 1 to [N] and the Prayer above are true and correct to my knowledge and belief and that nothing material has been concealed therefrom.\nVerified at [PLACE] on this [Nth] day of [MONTH] [YEAR].\n                                                        DEPONENT",
        ),
        SectionRule(
            order=11,
            name="Advocate block",
            required=False,
            purpose="Indicates the advocate firm or counsel representing the replying respondent",
            formatting="Left/normal alignment at the foot of the document.",
            important_rules=[
                "Appears at the foot of the document in the sample affidavit.",
                "Identifies advocate firm name and party represented, e.g. 'Advocates for the Respondent No.[N].'",
            ],
            expected_content="[ADVOCATE FIRM]\nAdvocates for the Respondent No.[N].",
        ),
    ]

    section_order = [s.name for s in sections]

    formatting_rules = {
        "forum_heading": "Bold, ALL CAPS, centred",
        "jurisdiction": "Bold, ALL CAPS, centred",
        "case_number": "Bold, ALL CAPS, centred",
        "affidavit_title": "Bold, ALL CAPS, centred",
        "prayer_heading": "Bold, ALL CAPS, centred",
        "verification_heading": "Bold, ALL CAPS, centred",
        "party_names": "Normal, left-aligned",
        "status_tags": "Right-aligned, prefixed with three dots (...Petitioner, ...Respondent No.1)",
        "versus": "Centred on its own line",
        "paragraph_numbers": "Bold, followed by full stop",
        "prayer_letters": "Bold, in parentheses (e.g. (a), (b), (c))",
        "paragraph_text": "Normal, justified",
        "deponent_signature_tag": "ALL CAPS, right-aligned (DEPONENT)",
        "before_me": "Normal, left-aligned",
        "date_format": "Ordinal day + month + year (e.g. 5th day of September 2026)",
    }

    paragraph_rules = [
        "Body paragraphs use continuous sequential numbering (1, 2, 3... N).",
        "Paragraph numbers are bold followed by a full stop.",
        "Prayer paragraphs are lettered and are NOT part of the body sequence.",
        "Paragraph text must be normal and justified.",
        "Must follow sequential rhetorical reply moves from identity through closing.",
    ]

    prayer_rules = [
        "Heading 'PRAYER' is bold, ALL CAPS, centred.",
        "Prayer items are lettered: (a), (b), (c), never numbered with body paragraphs.",
        "Prayer letters are bold.",
        "Starts with: 'I therefore respectfully pray that this Hon\\'ble Court may be pleased to:'",
        "Includes standard prayer to dismiss the petition with costs and refuse interim relief.",
    ]

    jurat_rules = [
        "Follows the prayer section.",
        "Recites: 'Solemnly affirmed at [PLACE]' on line 1.",
        "Recites: 'On this [Nth] day of [MONTH] [YEAR]' on line 2.",
        "'Before Me' is left-aligned.",
        "'DEPONENT' is in ALL CAPS and right-aligned.",
        "The affirmation/swearing verb must match the verification verb in the deponent clause.",
    ]

    verification_rules = [
        "Heading 'VERIFICATION' is bold, ALL CAPS, centred.",
        "CRITICAL: The paragraph range cited ('contents of paragraphs 1 to [N]') must exactly match the actual number of body paragraphs.",
        "Explicitly verifies both the body paragraphs and the Prayer above as true and correct to knowledge and belief.",
        "Recites: 'nothing material has been concealed therefrom'.",
        "Recites: 'Verified at [PLACE] on this [Nth] day of [MONTH] [YEAR].'",
        "'DEPONENT' is in ALL CAPS and right-aligned.",
    ]

    deponent_rules = [
        "Deponent clause is a single unnumbered sentence following the affidavit title.",
        "When the respondent is a natural person: the person deposes as 'the Respondent No.[N] above named'.",
        "When the respondent is a company, authority, or organisation: an officer deposes for it stating designation: 'the [DESIGNATION] of the Respondent No.[N] above named'.",
        "CRITICAL: Never write 'I am Respondent No.[N]' when the respondent is an organisation/authority.",
        "Verb agreement: 'solemnly affirm' -> 'Solemnly affirmed'; 'swear and affirm' -> 'Sworn'.",
    ]

    critical_rules = CriticalRules(
        respondent_in_title="The affidavit title must carry the specific respondent number (e.g. AFFIDAVIT IN REPLY ON BEHALF OF RESPONDENT NO. 2).",
        deponent_clause_form="If the respondent is an organisation, the deponent clause uses designation and relationship; never 'I am Respondent No. [N]'.",
        continuous_numbering="The numbered body paragraphs must use continuous numbering without interruption.",
        prayer_not_numbered_with_body="Prayer paragraphs are lettered ((a), (b), (c)) and are NOT part of the numbered body sequence.",
        verification_range_exact_match="The verification paragraph range ('paragraphs 1 to N') must exactly match the actual number of body paragraphs.",
        verb_agreement="The verification verb in the deponent clause must correspond to the jurat/affirmation wording (e.g. solemnly affirm -> Solemnly affirmed).",
        respondent_consistency="The respondent number must remain consistent throughout the document (title, deponent clause, body, prayer, jurat, verification, advocate block).",
    )

    fixed_phrases = {
        "deponent_clause": [
            "the Respondent No.__ above named",
            "the [designation] of the Respondent No.__ above named",
            "do hereby solemnly affirm and state as under:",
        ],
        "identity_and_perusal": [
            "am well acquainted with the facts and circumstances of the case",
            "I have perused the Petition and the documents annexed thereto",
            "am competent to affirm this Affidavit in Reply",
        ],
        "blanket_denial": [
            "At the outset, I deny each and every allegation, contention and submission made in the [PROCEEDING TYPE]",
            "save and except those specifically admitted herein",
            "misconceived, devoid of merits and is liable to be dismissed in limine",
        ],
        "preliminary_position": [
            "has suppressed material facts",
            "strictly in accordance with law and after following due procedure",
            "No legal, constitutional or fundamental right... has been infringed",
        ],
        "substantive_answer": [
            "With reference to the averments made in the Petition",
            "the same are false, incorrect and denied",
            "has failed to make out any case warranting interference",
            "the extraordinary writ jurisdiction of this Hon'ble Court",
        ],
        "closing": [
            "In the premises aforesaid",
            "deserves to be dismissed with costs",
        ],
        "prayer": [
            "I therefore respectfully pray that this Hon'ble Court may be pleased to:",
            "dismiss the present [PROCEEDING TYPE] with costs",
            "refuse any interim or ad-interim relief sought by the Petitioner",
            "grant such other and further reliefs as this Hon'ble Court may deem fit and proper in the facts and circumstances of the case",
        ],
        "verification": [
            "true and correct to my knowledge and belief",
            "nothing material has been concealed therefrom",
            "contents of paragraphs 1 to [N] and the Prayer above",
        ],
    }

    reply_move_structure = [
        ReplyMove(
            move="IDENTITY_AND_PERUSAL",
            description="Identifies who the deponent is, confirms perusal of the petition and annexed documents, and asserts competence to depose",
            opening_words="I say that I am [the Respondent No.__ / the [designation] of the Respondent No.__] in the above Writ Petition and am well acquainted with the facts and circumstances of the case...",
        ),
        ReplyMove(
            move="BLANKET_DENIAL",
            description="Denies all allegations, contentions, and submissions in the petition except those specifically admitted, asserting the petition is misconceived",
            opening_words="At the outset, I deny each and every allegation, contention and submission made in the Writ Petition, save and except those specifically admitted herein...",
        ),
        ReplyMove(
            move="PRELIMINARY_POSITION",
            description="Establishes preliminary defense: action taken strictly according to law and procedure; no legal or constitutional right infringed; material facts suppressed",
            opening_words="I say that... The action complained of has been taken strictly in accordance with law and after following due procedure...",
        ),
        ReplyMove(
            move="SUBSTANTIVE_ANSWER",
            description="Rebuts specific allegations or communications raised by petitioner, marks and annexes supporting exhibits (one paragraph per point answered)",
            opening_words="With reference to the averments made in the Petition, I say that the same are false, incorrect and denied...",
        ),
        ReplyMove(
            move="CLOSING",
            description="Formal conclusion asserting that the writ petition deserves to be dismissed with costs",
            opening_words="In the premises aforesaid, I say that the Writ Petition deserves to be dismissed with costs.",
        ),
        ReplyMove(
            move="PRAYER_TO_DISMISS",
            description="Formal prayer requesting dismissal with costs, refusal of interim relief, and other deemed reliefs",
            opening_words="I therefore respectfully pray that this Hon'ble Court may be pleased to:",
        ),
    ]

    extracted_entities = [
        EntityRequirement(
            category="FORUM/CITY",
            meaning="The court name and its geographical seat",
            relevance="Required for Section 1 Forum heading (e.g. High Court of Judicature at Bombay / Bombay)",
        ),
        EntityRequirement(
            category="JURISDICTION_TYPE",
            meaning="The specific bench or side of the court",
            relevance="Required for Section 2 Jurisdiction heading (e.g. Ordinary Original Civil Jurisdiction)",
        ),
        EntityRequirement(
            category="CASE_TYPE",
            meaning="The nature of the legal proceeding",
            relevance="Required for Section 3 Case number and throughout body/prayer (e.g. Writ Petition)",
        ),
        EntityRequirement(
            category="CASE_NUMBER",
            meaning="The unique serial number assigned to the proceeding",
            relevance="Required for Section 3 Case number heading (e.g. 1847)",
        ),
        EntityRequirement(
            category="YEAR",
            meaning="The filing/registration year of the case",
            relevance="Required for Section 3 Case number heading (e.g. 2026)",
        ),
        EntityRequirement(
            category="PETITIONER",
            meaning="Name, description, and details of the party who filed the petition",
            relevance="Required for Section 4 Cause title petitioner block",
        ),
        EntityRequirement(
            category="RESPONDENT",
            meaning="Name and details of parties called upon to answer the petition",
            relevance="Required for Section 4 Cause title respondents block",
        ),
        EntityRequirement(
            category="RESPONDENT_NUMBER",
            meaning="The specific respondent serial number on whose behalf the affidavit is filed",
            relevance="Required for Section 5 Affidavit title, Section 6 Deponent clause, and throughout for consistency",
        ),
        EntityRequirement(
            category="DEPONENT",
            meaning="Full name of the individual swearing the affidavit",
            relevance="Required for Section 6 Deponent clause, Section 9 Jurat, and Section 10 Verification",
        ),
        EntityRequirement(
            category="CAPACITY",
            meaning="Deponent's designation or authority if deposing on behalf of an entity",
            relevance="Required for Section 6 Deponent clause and Section 7 Para 1 to establish authority",
        ),
        EntityRequirement(
            category="ORGANISATION",
            meaning="Corporate body, statutory authority, or government entity party",
            relevance="Required to determine deponent phrasing rule (individual vs organisation officer)",
        ),
        EntityRequirement(
            category="ADDRESS",
            meaning="Deponent's residential address or official office address",
            relevance="Required for Section 6 Deponent clause identification",
        ),
        EntityRequirement(
            category="AGE",
            meaning="Age of deponent (when natural person deponent)",
            relevance="Required for individual deponent description in Section 4 and 6 if applicable",
        ),
        EntityRequirement(
            category="OCCUPATION",
            meaning="Occupation of individual deponent",
            relevance="Required for individual deponent description in Section 4 and 6 if applicable",
        ),
        EntityRequirement(
            category="VERIFICATION_VERB",
            meaning="Verbal formula used for solemn declaration (affirm vs swear)",
            relevance="Required for Section 6 Deponent clause and Section 9 Jurat verb agreement",
        ),
        EntityRequirement(
            category="PLACE_OF_ATTESTATION",
            meaning="City/location where the affidavit is sworn and executed",
            relevance="Required for Section 9 Jurat and Section 10 Verification",
        ),
        EntityRequirement(
            category="DATE",
            meaning="Date on which the affidavit is attested and verified",
            relevance="Required for Section 9 Jurat and Section 10 Verification (ordinal format: 5th day of September 2026)",
        ),
        EntityRequirement(
            category="PARAGRAPH_COUNT",
            meaning="Total number of body paragraphs (Part 7) in the generated document",
            relevance="Required for Section 10 Verification paragraph range statement ('paragraphs 1 to [N]')",
        ),
    ]

    exclusions = [
        "Exhibit references format (no specific internal format prescribed by rulebook, beyond marking EXHIBIT-'A')",
        "Advocate / drafting block (noted as not having a prescribed rule in rulebook, though present in sample)",
        "Para-wise reply (the rulebook covers short reply / preliminary objections format, not point-by-point exhaustive petition reproduction)",
        "Tribunal and board formats (e.g. 'BEFORE THE...')",
        "Statutory citations and case-law citations",
        "Monetary amounts and calculations",
    ]

    return TemplateSpecification(
        document_type="Affidavit in Reply",
        sections=sections,
        section_order=section_order,
        formatting_rules=formatting_rules,
        paragraph_rules=paragraph_rules,
        prayer_rules=prayer_rules,
        jurat_rules=jurat_rules,
        verification_rules=verification_rules,
        deponent_rules=deponent_rules,
        critical_rules=critical_rules,
        fixed_phrases=fixed_phrases,
        reply_move_structure=reply_move_structure,
        extracted_entities=extracted_entities,
        exclusions=exclusions,
    )
