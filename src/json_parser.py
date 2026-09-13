"""
Robust JSON Parser for LLM Responses.
Extracts and parses JSON objects from LLM outputs, gracefully handling:
- Leading/trailing whitespace
- Markdown code fences (```json ... ``` or ``` ... ```)
- Prefixed text (e.g. "User Safety: safe", "Here is the JSON:", etc.)
- Trailing non-JSON commentary
"""

import json
import re
from typing import Any, Dict, Optional


def clean_and_parse_llm_json(raw_text: str) -> Dict[str, Any]:
    """
    Attempts to parse JSON from an LLM response string using a multi-stage fallback approach:
    1. Direct json.loads on stripped content
    2. Markdown code fence extraction (```json ... ```)
    3. Balanced-brace JSON object search (extracts outermost {...})
    4. Regex pattern search for JSON structures

    Args:
        raw_text (str): Raw string returned by the LLM.

    Returns:
        Dict[str, Any]: Parsed JSON dictionary.

    Raises:
        ValueError: If no valid JSON object can be extracted.
    """
    if not raw_text or not isinstance(raw_text, str):
        raise ValueError("Cannot parse JSON from empty or non-string input.")

    text = raw_text.strip()

    # Attempt 1: Direct JSON parsing
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    # Attempt 2: Extract from Markdown code fence ```json ... ``` or ``` ... ```
    fence_pattern = r"```(?:json)?\s*(\{[\s\S]*?\})\s*```"
    fence_match = re.search(fence_pattern, text, re.IGNORECASE)
    if fence_match:
        try:
            parsed = json.loads(fence_match.group(1).strip())
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass

    # Attempt 3: Outermost balanced braces search
    # Handles cases where the model prepends text like "User Safety: safe\n\n{...}"
    first_brace = text.find("{")
    last_brace = text.rfind("}")

    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        candidate = text[first_brace : last_brace + 1].strip()
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass

    # Attempt 4: If JSON has trailing commas, try gentle regex cleanup
    if first_brace != -1 and last_brace != -1:
        candidate = text[first_brace : last_brace + 1].strip()
        # Remove trailing commas before closing braces/brackets
        cleaned_candidate = re.sub(r",\s*([\}\]])", r"\1", candidate)
        try:
            parsed = json.loads(cleaned_candidate)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass

    raise ValueError(
        f"Failed to extract a valid JSON object from LLM response.\n"
        f"Raw response (length {len(raw_text)}):\n{raw_text[:500]}"
    )
