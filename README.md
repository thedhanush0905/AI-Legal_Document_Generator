# AI Affidavit in Reply Generator & Evaluator

An end-to-end AI-powered legal document generation and quality evaluation system. It ingests reference procedural rules, a structural sample affidavit, and case-specific facts to produce a formatted **Affidavit in Reply** following the supplied reference structure for the High Court of Bombay. The generated document is rendered as a stylized Microsoft Word (`.docx`) file and subjected to deterministic validation and a 100-point composite legal quality evaluation across six standardized dimensions.

---

## Architecture & Workflow

```text
               Reference Rules (PDF)        Sample Affidavit (PDF)       Case Information (PDF)
                        │                              │                            │
                        ▼                              ▼                            ▼
                 [Document Reader: PyMuPDF (fitz)] ─────────────────────────────────┘
                                                │
                                                ▼
                         [Structured CaseData Extraction: OpenRouter LLM]
                                                │
                                                ▼
                        [Deterministic Template Specification Builder]
                                                │
                                                ▼
                          [Legal Document Content Generator (LLM)]
                                                │
                                                ▼
                          [Deterministic DOCX Layout Renderer]
                                                │
                                                ▼
                      [Independent Deterministic Quality Validator]
                                 (20 Mandatory Quality Checks)
                                                │
                                                ▼
                         [Standardized 6-Dimension Evaluator]
                               (100-Point Audit Scoring)
                                                │
                        ┌───────────────────────┴───────────────────────┐
                        ▼                                               ▼
             outputs/generated_affidavit.docx             outputs/evaluation_report.json
             outputs/extracted_case_data.json             outputs/evaluation_report.md
```

---

## Key Features

1. **Structured Case Extraction**: Converts unstructured legal case summaries into validated Pydantic models (`CaseData`), strictly preserving case identities, parties, deponent designations, and sequential reply points.
2. **Template Understanding**: Formalizes procedural court rules from `format_explained.pdf` into a machine-enforceable `TemplateSpecification` (10 core affidavit parts + advocate/drafting block as an additional output section, section order, deponent capacity rules, rhetorical reply moves, and verification range matching).
3. **Factual Whitelist & Hallucination Guard**: Prohibits introduction of unsupplied constitutional/fundamental rights assertions, extraneous case law, statutory citations, or leaked sample facts (`Arjun Mehta`, `Rohan Deshpande`, `3147`).
4. **Formatted DOCX Generation**: Pure deterministic layout rendering conforming to Bombay High Court conventions (centered bold headers, borderless cause title alignment, justified body text with bold paragraph numbers, uppercase right-aligned `DEPONENT` signature lines, and left-aligned `Before Me`).
5. **Independent Quality Validation**: 20 automated deterministic quality checks covering required sections, sequence, continuous numbering, verification range exactness, verb agreement, and placeholder absence.
6. **Six-Dimension Audit & Scoring (100 pts)**:
   - **Entity Accuracy (20 pts)**: Preservation of all 16 key case entities.
   - **Completeness (15 pts)**: Full coverage of all 6 substantive case reply points (across 7 total body paragraphs: 6 substantive points + 1 closing paragraph), prayer, exhibit, and advocate blocks.
   - **Structure (15 pts)**: Strict 1–11 section sequence, continuous numbering across 7 body paragraphs, and prayer separation.
   - **Consistency (15 pts)**: Internal consistency across respondent numbers, deponent capacity, verbs, and dates.
   - **Template Fidelity (20 pts)**: Rulebook adherence.
   - **Hallucination (15 pts)**: Zero leaked sample entities or unsupplied legal claims.
7. **Interactive Streamlit Web UI**: Easy-to-use graphical interface with Demo Mode, progress indicators, preview tabs, metric cards, and one-click artifact downloads.

---

## Project Structure

```text
affidavit-ai-agent/
│
├── app.py                          # Streamlit interactive application
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variable template
├── .gitignore                      # Git ignore rules
├── README.md                       # Project documentation
│
├── src/
│   ├── __init__.py
│   ├── document_reader.py          # PyMuPDF PDF text extraction
│   ├── models.py                   # Pydantic schemas for CaseData
│   ├── llm_client.py               # OpenRouter / OpenAI SDK client
│   ├── template_models.py          # Pydantic schemas for TemplateSpecification
│   ├── template_builder.py         # Rulebook & sample template codification
│   ├── affidavit_models.py         # Pydantic schemas for GeneratedAffidavit
│   ├── affidavit_generator.py      # Legal generation engine & hallucination guards
│   ├── docx_generator.py           # Pure deterministic python-docx renderer
│   ├── validator.py                # 20-point independent deterministic validator
│   ├── evaluator.py                # 6-dimension evaluation & scoring system
│   └── pipeline.py                 # End-to-end pipeline orchestrator
│
├── inputs/
│   ├── format_explained.pdf        # Procedural rulebook
│   ├── sample_affidavit.pdf        # Reference sample affidavit
│   └── case_information.pdf        # Case-specific input facts
│
└── outputs/
    ├── extracted_case_data.json    # Structured case data
    ├── template_specification.json # Structured template specification
    ├── template_specification.md   # Human-readable template spec
    ├── generated_affidavit.json    # Structured generated affidavit
    ├── generated_affidavit.docx    # Formatted Word document
    ├── validation_report.json      # 20-point validation results
    ├── evaluation_report.json      # 100-point evaluation audit report (JSON)
    └── evaluation_report.md        # Comprehensive evaluation audit report (Markdown)
```

---

## Setup & Installation

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.12 / 3.14)
- Git

### 2. Create Virtual Environment & Install Dependencies
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Windows (Command Prompt):
.\.venv\Scripts\activate.bat
# Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env` and supply your OpenRouter API key:
```ini
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openrouter/auto
```
*(You may also configure any OpenRouter-supported model such as `openai/gpt-4o-mini` or `anthropic/claude-3.5-sonnet`.)*

---

## Running Locally

Launch the Streamlit web application:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### Demo Workflow
1. Select **Demo Mode** to automatically load the provided assignment documents (`inputs/case_information.pdf`, `inputs/format_explained.pdf`, and `inputs/sample_affidavit.pdf`).
2. Click **GENERATE AFFIDAVIT**.
3. Watch the progress bar step through extraction, template compilation, generation, DOCX styling, validation, and evaluation.
4. Inspect the generated affidavit preview, validation report, and 6-dimension quality score.
5. Download the `.docx` document and evaluation reports directly from the export section.

---

## Running Test Suite

The project includes an automated test suite verifying every component independently and collectively:

```bash
# 1. Test PDF Reader
python test_reader.py

# 2. Test Template Specification
python test_template.py

# 3. Test Affidavit Generation & Whitelist Guards
python test_generation.py

# 4. Test DOCX Document Creation & Typography
python test_docx.py

# 5. Test Independent Deterministic Validation & Negative Defect Tests
python test_validation.py

# 6. Test 6-Dimension Evaluator & Synthetic Negative Scoring Tests
python test_evaluation.py

# 7. Test End-to-End Pipeline Integration
python test_app_integration.py
```

---

## Evaluation Methodology & Dimension Weights

The evaluation system scores the generated document against a 100-point quality benchmark:

| Dimension | Points | Description |
|---|---|---|
| **Entity Accuracy** | 20.0 | Verifies exact preservation of 16 key case entities across 4 categories (Forum & Proceeding, Cause Title Parties, Deponent Capacity, and Attestation & Representation). |
| **Completeness** | 15.0 | Verifies full coverage of all 6 substantive case reply points (across 7 total body paragraphs: 6 substantive points + 1 closing paragraph), prayer for dismissal with costs, exhibit reference, and advocate representation. |
| **Structure** | 15.0 | Verifies presence and sequence of all 11 sections, 7 body paragraphs (6 substantive reply points + 1 closing paragraph), continuous numbering, prayer separation, and verification range. |
| **Consistency** | 15.0 | Verifies internal agreement across parties, designations, verbs (`solemnly affirm` $\rightarrow$ `Solemnly affirmed`), and dates. |
| **Template Fidelity** | 20.0 | Verifies compliance with procedural rules from `format_explained.pdf` (deponent officer form, uppercase centered headers, etc.). |
| **Hallucination** | 15.0 | Rewards zero leakage of sample entities (`Arjun Mehta`, `3147`) and zero unsupplied legal rights/constitutional assertions. |
| **Total** | **100.0** | **Comprehensive Legal Quality Metric** |

---

## Limitations & Disclaimer

- **Deterministic Checks**: Keyword checks, regex rules, and schema validations reliably catch known failure modes (sample entity leakage, altered paragraph numbering, missing sections, and unprovided legal boilerplate), but cannot mathematically prove that a document contains zero subtle semantic distortions.
- **Legal Advice Disclaimer**: This application is an educational prototype built for an internship assignment. It evaluates document fidelity against supplied reference materials and does not provide legal advice or independently guarantee judicial admissibility under Indian law.

---

## Deployment & Demo Video

- **Deployment**: https://ai-legaldocumentgenerator-jesxgb2aagm9sfzmnamtsk.streamlit.app
- **Demo Video**: https://www.loom.com/share/14b3e42fe6ce4a01975a71c51d379659

---

## AI Coding Assistant Disclosure

In compliance with the assignment disclosure guidelines, Google DeepMind's Antigravity coding assistant was utilized during the development of this project for rapid code scaffolding, test generation, and architectural structuring.
