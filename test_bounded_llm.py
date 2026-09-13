"""
Unit test suite for bounded LLM execution and error handling.
Mocks the OpenAI/OpenRouter client to verify:
A. Successful response succeeds.
B. Timeout causes retry and eventually raises clean bounded error.
C. Invalid JSON causes retry and eventually raises clean bounded error.
D. Empty response causes retry and eventually raises clean bounded error.
E. Three consecutive failures execute exactly 3 bounded attempts with no infinite loop.
"""

import os
import sys
from unittest.mock import MagicMock, patch

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.models import CaseData, Respondent, ReplyPoint, AdvocateInfo
from src.template_models import TemplateSpecification
from src.affidavit_generator import draft_substantive_paragraphs
from src.llm_client import extract_case_data, LLM_REQUEST_TIMEOUT


def get_mock_case_data() -> CaseData:
    return CaseData(
        court="IN THE HIGH COURT OF JUDICATURE AT BOMBAY",
        jurisdiction="ORDINARY ORIGINAL CIVIL JURISDICTION",
        proceeding="WRIT PETITION",
        case_number="1847",
        year="2026",
        petitioner="Sunrise Housing Private Limited",
        respondents=[
            Respondent(respondent_number=1, name="State of Maharashtra"),
            Respondent(respondent_number=2, name="Mumbai Metropolitan Region Development Authority"),
        ],
        respondent_number="Respondent No. 2",
        deponent="Arvind Rajan",
        designation="Deputy Metropolitan Commissioner",
        organisation="Mumbai Metropolitan Region Development Authority",
        address="Bandra East, Mumbai, Maharashtra",
        verification_verb="solemnly affirm",
        reply_points=[
            ReplyPoint(point_number=1, title="Filing", details=["Point 1 text"]),
            ReplyPoint(point_number=2, title="Denial", details=["Point 2 text"]),
            ReplyPoint(point_number=3, title="Preliminary", details=["Point 3 text"]),
            ReplyPoint(point_number=4, title="Point 4", details=["Point 4 text"]),
            ReplyPoint(point_number=5, title="Point 5", details=["Point 5 text"]),
            ReplyPoint(point_number=6, title="Point 6", details=["Point 6 text"]),
        ],
        prayer="Writ Petition be dismissed with costs.",
        attestation_place="Mumbai",
        attestation_date="5 September 2026",
        advocate=AdvocateInfo(
            firm_name="Rajan & Associates",
            acting_for="Respondent No. 2",
        ),
    )


def test_llm_request_timeout_is_finite():
    """Verify the request timeout constant is configured to a finite bounded value (e.g. 60s)."""
    assert LLM_REQUEST_TIMEOUT == 60.0


def test_draft_substantive_paragraphs_success():
    """Test A: Successful response succeeds on attempt 1."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="""
        {
          "paragraph_4": "Respondent No. 2 denies that the communication dated 15 July 2026 was issued without authority.",
          "paragraph_5": "The communication dated 15 July 2026 was issued pursuant to redevelopment procedure and relevant records.",
          "paragraph_6": "Respondent No. 2 relies upon the communication dated 15 July 2026 marked as EXHIBIT-‘A’."
        }
        """))
    ]
    mock_client.chat.completions.create.return_value = mock_response

    case_data = get_mock_case_data()
    template = MagicMock(spec=TemplateSpecification)

    with patch("src.affidavit_generator.get_llm_client", return_value=(mock_client, "test-model")):
        paras = draft_substantive_paragraphs(case_data, template)

    assert len(paras) == 3
    assert "EXHIBIT-‘A’" in paras[2]
    assert mock_client.chat.completions.create.call_count == 1


def test_draft_substantive_paragraphs_timeout_retry_and_bounded_failure():
    """Test B: Timeout causes retry and eventually raises clean bounded error after 3 attempts."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = TimeoutError("Request timed out after 60s")

    case_data = get_mock_case_data()
    template = MagicMock(spec=TemplateSpecification)

    with patch("src.affidavit_generator.get_llm_client", return_value=(mock_client, "test-model")), \
         patch("time.sleep", return_value=None):
        try:
            draft_substantive_paragraphs(case_data, template)
            assert False, "Expected RuntimeError on timeout exhaustion"
        except RuntimeError as exc:
            assert "Affidavit generation timed out or failed after 3 attempts" in str(exc)

    assert mock_client.chat.completions.create.call_count == 3


def test_draft_substantive_paragraphs_invalid_json_retry_and_bounded_failure():
    """Test C: Invalid JSON causes retry and eventually raises bounded error after 3 attempts."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    # Malformed non-JSON string
    mock_response.choices = [MagicMock(message=MagicMock(content="User Safety: safe"))]
    mock_client.chat.completions.create.return_value = mock_response

    case_data = get_mock_case_data()
    template = MagicMock(spec=TemplateSpecification)

    with patch("src.affidavit_generator.get_llm_client", return_value=(mock_client, "test-model")), \
         patch("time.sleep", return_value=None):
        try:
            draft_substantive_paragraphs(case_data, template)
            assert False, "Expected RuntimeError on invalid JSON exhaustion"
        except RuntimeError as exc:
            assert "Affidavit generation timed out or failed after 3 attempts" in str(exc)

    assert mock_client.chat.completions.create.call_count == 3


def test_draft_substantive_paragraphs_empty_response_retry():
    """Test D: Empty response causes retry and eventually raises bounded error after 3 attempts."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="   "))]
    mock_client.chat.completions.create.return_value = mock_response

    case_data = get_mock_case_data()
    template = MagicMock(spec=TemplateSpecification)

    with patch("src.affidavit_generator.get_llm_client", return_value=(mock_client, "test-model")), \
         patch("time.sleep", return_value=None):
        try:
            draft_substantive_paragraphs(case_data, template)
            assert False, "Expected RuntimeError on empty response exhaustion"
        except RuntimeError as exc:
            assert "Affidavit generation timed out or failed after 3 attempts" in str(exc)

    assert mock_client.chat.completions.create.call_count == 3


def test_three_consecutive_failures_is_strictly_bounded():
    """Test E: Three consecutive failures execute exactly 3 bounded attempts with no infinite loop."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = RuntimeError("OpenRouter 503 Service Unavailable")

    case_data = get_mock_case_data()
    template = MagicMock(spec=TemplateSpecification)

    with patch("src.affidavit_generator.get_llm_client", return_value=(mock_client, "test-model")), \
         patch("time.sleep", return_value=None):
        try:
            draft_substantive_paragraphs(case_data, template)
        except RuntimeError as exc:
            assert "Affidavit generation timed out or failed after 3 attempts" in str(exc)

    assert mock_client.chat.completions.create.call_count == 3


def main():
    print("========================================")
    print("TEST: BOUNDED LLM EXECUTION & RETRIES")
    print("========================================\n")
    test_llm_request_timeout_is_finite()
    print("✓ test_llm_request_timeout_is_finite passed")
    test_draft_substantive_paragraphs_success()
    print("✓ test_draft_substantive_paragraphs_success passed")
    test_draft_substantive_paragraphs_timeout_retry_and_bounded_failure()
    print("✓ test_draft_substantive_paragraphs_timeout_retry_and_bounded_failure passed")
    test_draft_substantive_paragraphs_invalid_json_retry_and_bounded_failure()
    print("✓ test_draft_substantive_paragraphs_invalid_json_retry_and_bounded_failure passed")
    test_draft_substantive_paragraphs_empty_response_retry()
    print("✓ test_draft_substantive_paragraphs_empty_response_retry passed")
    test_three_consecutive_failures_is_strictly_bounded()
    print("✓ test_three_consecutive_failures_is_strictly_bounded passed")
    print("\n========================================")
    print("ALL BOUNDED LLM EXECUTION TESTS PASSED!")
    print("========================================")


if __name__ == "__main__":
    main()
