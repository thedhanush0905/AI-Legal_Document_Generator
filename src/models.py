from typing import List, Optional
from pydantic import BaseModel, Field


class Respondent(BaseModel):
    """Details of a respondent in the case."""
    respondent_number: int = Field(
        ...,
        description="The serial number of the respondent, e.g. 1 or 2"
    )
    name: str = Field(
        ...,
        description="The full name/title of the respondent organisation or entity"
    )


class ReplyPoint(BaseModel):
    """A structured reply point to be incorporated in the affidavit."""
    point_number: int = Field(
        ...,
        description="Point number, from 1 to 6"
    )
    title: str = Field(
        ...,
        description="The title/heading of the point, e.g. 'Filing of Affidavit in Reply'"
    )
    details: List[str] = Field(
        ...,
        description="List of factual assertions or bullet points under this point"
    )


class AdvocateInfo(BaseModel):
    """Details of the advocate or advocate firm."""
    firm_name: str = Field(
        ...,
        description="Name of the advocate firm, e.g. 'Rajan & Associates'"
    )
    acting_for: str = Field(
        ...,
        description="Party for whom the advocate is acting, e.g. 'Respondent No. 2'"
    )


class CaseData(BaseModel):
    """Structured case information extracted from the source document."""
    court: str = Field(
        ...,
        description="The court name exactly as stated, e.g. 'IN THE HIGH COURT OF JUDICATURE AT BOMBAY'"
    )
    jurisdiction: str = Field(
        ...,
        description="The jurisdiction, e.g. 'ORDINARY ORIGINAL CIVIL JURISDICTION'"
    )
    proceeding: str = Field(
        ...,
        description="The proceeding type, e.g. 'WRIT PETITION'"
    )
    case_number: str = Field(
        ...,
        description="The case number, e.g. '1847'"
    )
    year: str = Field(
        ...,
        description="The case year, e.g. '2026'"
    )
    petitioner: str = Field(
        ...,
        description="The petitioner name, e.g. 'Sunrise Housing Private Limited'"
    )
    respondents: List[Respondent] = Field(
        ...,
        description="Structured list of all respondents"
    )
    respondent_number: str = Field(
        ...,
        description="The specific respondent on whose behalf this affidavit is filed, e.g. 'Respondent No. 2'"
    )
    deponent: str = Field(
        ...,
        description="Full name of the deponent, e.g. 'Arvind Rajan'"
    )
    designation: str = Field(
        ...,
        description="Deponent's designation, e.g. 'Deputy Metropolitan Commissioner'"
    )
    organisation: str = Field(
        ...,
        description="Deponent's organisation, e.g. 'Mumbai Metropolitan Region Development Authority'"
    )
    address: str = Field(
        ...,
        description="Deponent's address, e.g. 'Bandra East, Mumbai, Maharashtra'"
    )
    verification_verb: str = Field(
        ...,
        description="Verification verb, e.g. 'solemnly affirm'"
    )
    attestation_place: str = Field(
        ...,
        description="Place of attestation, e.g. 'Mumbai'"
    )
    attestation_date: str = Field(
        ...,
        description="Date of attestation, e.g. '5 September 2026'"
    )
    reply_points: List[ReplyPoint] = Field(
        ...,
        description="Structured list of all reply points preserving order and points 1 to 6"
    )
    prayer: str = Field(
        ...,
        description="The prayer/relief sought by respondent, e.g. dismissal with costs"
    )
    advocate: AdvocateInfo = Field(
        ...,
        description="Structured information regarding the advocate"
    )
