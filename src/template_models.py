from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SectionRule(BaseModel):
    """Specification of an individual section in the Affidavit in Reply."""
    order: int = Field(..., description="1-based sequence order of the section")
    name: str = Field(..., description="Standardized name of the section")
    required: bool = Field(default=True, description="Whether this section is mandatory")
    purpose: str = Field(..., description="Purpose or legal function of this section")
    formatting: str = Field(..., description="Visual alignment, casing, and style rules")
    important_rules: List[str] = Field(default_factory=list, description="Specific rules governing this section")
    expected_content: str = Field(..., description="Template structure or pattern for this section")


class ReplyMove(BaseModel):
    """Specification of a rhetorical move in the body paragraphs."""
    move: str = Field(..., description="Standard move identifier, e.g. IDENTITY_AND_PERUSAL")
    description: str = Field(..., description="What the move achieves")
    opening_words: Optional[str] = Field(None, description="Standard opening phrases prescribed by the rulebook")


class EntityRequirement(BaseModel):
    """Specification of an entity required for generation."""
    category: str = Field(..., description="Entity category name, e.g. FORUM/CITY")
    meaning: str = Field(..., description="Description of the entity")
    relevance: str = Field(..., description="Why this entity is relevant to document generation")


class CriticalRules(BaseModel):
    """Inviolable rules governing affidavit construction and validation."""
    respondent_in_title: str = Field(
        ...,
        description="The affidavit title must carry the specific respondent number"
    )
    deponent_clause_form: str = Field(
        ...,
        description="Deponent clause format depends on individual vs organisation capacity"
    )
    continuous_numbering: str = Field(
        ...,
        description="Body paragraphs must use one continuous sequence (e.g. 1, 2, 3...)"
    )
    prayer_not_numbered_with_body: str = Field(
        ...,
        description="Prayer items are lettered and must NOT be numbered with body paragraphs"
    )
    verification_range_exact_match: str = Field(
        ...,
        description="Verification range 'paragraphs 1 to N' must exactly match actual body paragraph count"
    )
    verb_agreement: str = Field(
        ...,
        description="Verification verb in deponent clause must correspond to jurat wording"
    )
    respondent_consistency: str = Field(
        ...,
        description="Respondent number must remain consistent throughout the entire document"
    )


class TemplateSpecification(BaseModel):
    """Complete, reusable specification for an Affidavit in Reply."""
    document_type: str = Field(..., description="Document type name")
    sections: List[SectionRule] = Field(..., description="The ordered list of required sections")
    section_order: List[str] = Field(..., description="List of section names in strict order of appearance")
    formatting_rules: Dict[str, str] = Field(..., description="Global formatting rules for document elements")
    paragraph_rules: List[str] = Field(..., description="Rules governing body paragraph structure and numbering")
    prayer_rules: List[str] = Field(..., description="Rules governing prayer structure and lettering")
    jurat_rules: List[str] = Field(..., description="Rules governing jurat wording and alignment")
    verification_rules: List[str] = Field(..., description="Rules governing verification range and wording")
    deponent_rules: List[str] = Field(..., description="Rules governing individual vs organisation deponents")
    critical_rules: CriticalRules = Field(..., description="Mandatory rules that must never break")
    fixed_phrases: Dict[str, List[str]] = Field(..., description="Set phrases categorized by section/move")
    reply_move_structure: List[ReplyMove] = Field(..., description="Sequence of rhetorical moves for body paragraphs")
    extracted_entities: List[EntityRequirement] = Field(..., description="Entities needed to populate the template")
    exclusions: List[str] = Field(..., description="Material explicitly excluded from this format")
