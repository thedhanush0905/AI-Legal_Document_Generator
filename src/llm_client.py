import json
import os
from dotenv import load_dotenv
from openai import OpenAI

from src.models import CaseData

# Load environment variables from .env if present
load_dotenv()

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "openrouter/free"

EXTRACTION_SYSTEM_PROMPT = """You are a precise legal document data extractor.
Your task is to extract structured case information from the provided source document text.

CRITICAL INSTRUCTIONS:
1. Extract ONLY information that is explicitly present in the supplied source text.
2. Do NOT use outside legal knowledge or make assumptions.
3. Do NOT invent names, dates, numbers, organisations, legal provisions, exhibits, or facts.
4. Preserve names, dates, respondent numbers, case numbers, and all entities EXACTLY as written in the source.
5. Preserve all six reply points separately and in their exact original order (Point 1 to Point 6).
6. Return structured JSON that strictly conforms to the requested CaseData schema.
7. If any information is genuinely absent, use null/empty values according to the schema rather than guessing.
8. Do not rewrite or alter the factual substance.
"""


LLM_REQUEST_TIMEOUT = 60.0  # Hard timeout in seconds per request


def get_llm_client() -> tuple[OpenAI, str]:
    """
    Initializes and returns the OpenAI client configured for OpenRouter,
    along with the chosen model name. Configures an explicit hard timeout
    and disables internal client retries to prevent unbounded nested retries.

    Raises:
        ValueError: If OPENROUTER_API_KEY is missing or empty.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError(
            "Missing OPENROUTER_API_KEY environment variable. "
            "Please configure your OpenRouter API key in .env or your environment."
        )

    model = os.getenv("OPENROUTER_MODEL") or DEFAULT_MODEL

    client = OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=api_key,
        timeout=LLM_REQUEST_TIMEOUT,
        max_retries=0,  # Explicitly managed at caller level to avoid nested loops
    )
    return client, model


def extract_case_data(text: str) -> CaseData:
    """
    Extracts structured case information from raw document text using an LLM via OpenRouter.
    Bounded to MAX_RETRIES with an explicit timeout.

    Args:
        text (str): The raw text extracted from the case information document.

    Returns:
        CaseData: Validated Pydantic model instance containing the case information.

    Raises:
        ValueError: If API key is missing.
        RuntimeError: If the API call times out, fails, or the response cannot be parsed/validated.
    """
    client, model = get_llm_client()

    schema_json = json.dumps(CaseData.model_json_schema(), indent=2)

    user_prompt = f"""Extract the case information from the following source text and return a JSON object matching this JSON Schema:

{schema_json}

CRITICAL:
- Return ONLY the JSON object conforming to the schema above at the root level (do NOT wrap it under an outer key like "caseInformation" or "data").
- All fields defined in the schema must be populated strictly from the text.

--- SOURCE TEXT START ---
{text}
--- SOURCE TEXT END ---
"""

    import time
    from src.json_parser import clean_and_parse_llm_json

    max_retries = 3
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                temperature=0,  # Deterministic extraction
                response_format={"type": "json_object"},
                timeout=LLM_REQUEST_TIMEOUT,
                messages=[
                    {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
            )
            raw_content = ""
            if response.choices and response.choices[0].message and response.choices[0].message.content:
                raw_content = response.choices[0].message.content.strip()

            if not raw_content:
                raise ValueError("Received empty or whitespace response from LLM.")

            parsed_json = clean_and_parse_llm_json(raw_content)

            # If the LLM nested the response under an outer container key like "caseInformation" or "case_data"
            if isinstance(parsed_json, dict) and "court" not in parsed_json:
                for possible_key in ["caseInformation", "case_information", "caseData", "case_data", "data"]:
                    if possible_key in parsed_json and isinstance(parsed_json[possible_key], dict):
                        parsed_json = parsed_json[possible_key]
                        break

            validated_case_data = CaseData.model_validate(parsed_json)
            return validated_case_data

        except Exception as exc:
            last_error = exc
            if attempt < max_retries:
                time.sleep(2)

    raise RuntimeError(
        f"Case data extraction failed after {max_retries} attempts: {last_error}"
    ) from last_error
