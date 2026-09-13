import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from src.json_parser import clean_and_parse_llm_json


def test_parser_scenarios():
    print("Testing clean_and_parse_llm_json scenarios...")

    # Scenario 1: Clean JSON
    clean_json = '{"paragraph_4": "Prose 4", "paragraph_5": "Prose 5"}'
    res1 = clean_and_parse_llm_json(clean_json)
    assert res1["paragraph_4"] == "Prose 4"
    print("✓ Passed clean JSON")

    # Scenario 2: Markdown code fence ```json ... ```
    fenced_json = """```json
{
  "paragraph_4": "Fenced 4",
  "paragraph_5": "Fenced 5"
}
```"""
    res2 = clean_and_parse_llm_json(fenced_json)
    assert res2["paragraph_4"] == "Fenced 4"
    print("✓ Passed Markdown code fence")

    # Scenario 3: Prefixed text (e.g. "User Safety: safe")
    prefixed_json = """User Safety: safe

{
  "paragraph_4": "Prefixed 4",
  "paragraph_5": "Prefixed 5"
}"""
    res3 = clean_and_parse_llm_json(prefixed_json)
    assert res3["paragraph_4"] == "Prefixed 4"
    print("✓ Passed prefixed text ('User Safety: safe')")

    # Scenario 4: Commentary before and after
    commentary_json = """Here is the requested affidavit JSON:
{
  "court": "BOMBAY HIGH COURT",
  "year": "2026"
}
Hope this helps!"""
    res4 = clean_and_parse_llm_json(commentary_json)
    assert res4["court"] == "BOMBAY HIGH COURT"
    print("✓ Passed commentary before and after")

    # Scenario 5: Trailing comma cleanup
    trailing_comma_json = """{
  "court": "BOMBAY HIGH COURT",
  "year": "2026",
}"""
    res5 = clean_and_parse_llm_json(trailing_comma_json)
    assert res5["court"] == "BOMBAY HIGH COURT"
    print("✓ Passed trailing comma cleanup")

    print("\nAll json_parser unit tests passed successfully!")


if __name__ == "__main__":
    test_parser_scenarios()
