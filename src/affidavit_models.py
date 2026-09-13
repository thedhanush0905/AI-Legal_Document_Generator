from typing import List, Optional
from pydantic import BaseModel, Field


class PartyEntry(BaseModel):
    """Represents a single party in the cause title."""
    party_type: str = Field(..., description="'Petitioner' or 'Respondent'")
    number: Optional[int] = Field(None, description="Respondent number, if applicable")
    name: str = Field(..., description="Name of the party")
    details: Optional[str] = Field(None, description="Optional extra details/address")
    status_tag: str = Field(..., description="Status tag, e.g. '...Petitioner' or '...Respondent No.1'")


class CauseTitle(BaseModel):
    """Represents the complete cause title section."""
    petitioner: PartyEntry = Field(..., description="Petitioner entry")
    versus_text: str = Field(default="VERSUS", description="VERSUS divider")
    respondents: List[PartyEntry] = Field(..., description="List of respondent entries")


class BodyParagraph(BaseModel):
    """Represents an individual numbered body paragraph in the affidavit."""
    paragraph_number: int = Field(..., description="Sequential paragraph number (1 to N)")
    move_type: str = Field(..., description="Rhetorical move type, e.g. IDENTITY_AND_PERUSAL, BLANKET_DENIAL, etc.")
    text: str = Field(..., description="Full text of the body paragraph")


class PrayerItem(BaseModel):
    """Represents a lettered prayer item."""
    letter: str = Field(..., description="Letter designation, e.g. '(a)'")
    text: str = Field(..., description="Text of the specific prayer relief")


class PrayerSection(BaseModel):
    """Represents the prayer section."""
    heading: str = Field(default="PRAYER", description="Prayer heading")
    intro_text: str = Field(
        default="I therefore respectfully pray that this Hon'ble Court may be pleased to:",
        description="Standard introductory prayer clause"
    )
    items: List[PrayerItem] = Field(..., description="List of lettered prayer items")


class JuratSection(BaseModel):
    """Represents the jurat / formal attestation block."""
    place_line: str = Field(..., description="Recites solemn affirmation place, e.g. 'Solemnly affirmed at Mumbai'")
    date_line: str = Field(..., description="Recites date, e.g. 'On this 5th day of September 2026'")
    before_me: str = Field(default="Before Me", description="'Before Me' attestation tag")
    deponent_tag: str = Field(default="DEPONENT", description="'DEPONENT' signature tag")


class VerificationSection(BaseModel):
    """Represents the verification section."""
    heading: str = Field(default="VERIFICATION", description="Verification heading")
    deponent_name: str = Field(..., description="Name of deponent")
    verified_range_statement: str = Field(..., description="Explicit text verifying paragraphs 1 to N and the Prayer")
    full_text: str = Field(..., description="Full verification text")
    verified_at_line: str = Field(..., description="Place and date line, e.g. 'Verified at Mumbai on this 5th day of September 2026.'")
    deponent_tag: str = Field(default="DEPONENT", description="'DEPONENT' tag")


class AdvocateSection(BaseModel):
    """Represents the advocate endorsement block."""
    firm_name: str = Field(..., description="Advocate / Firm name, e.g. 'Rajan & Associates'")
    acting_for: str = Field(..., description="Capacity tag, e.g. 'Advocates for the Respondent No. 2'")


class GeneratedAffidavit(BaseModel):
    """Complete structured representation of the generated Affidavit in Reply."""
    forum_heading: str = Field(..., description="Court and seat line")
    jurisdiction: str = Field(..., description="Jurisdiction line")
    case_number_line: str = Field(..., description="Case proceeding, number, and year line")
    cause_title: CauseTitle = Field(..., description="Structured cause title")
    affidavit_title: str = Field(..., description="Affidavit title with specific respondent number")
    deponent_clause: str = Field(..., description="Single sentence identifying deponent and solemn affirmation")
    body_paragraphs: List[BodyParagraph] = Field(..., description="Ordered list of exactly 7 body paragraphs")
    prayer: PrayerSection = Field(..., description="Structured prayer section")
    jurat: JuratSection = Field(..., description="Structured jurat section")
    verification: VerificationSection = Field(..., description="Structured verification section")
    advocate_block: AdvocateSection = Field(..., description="Structured advocate block")
