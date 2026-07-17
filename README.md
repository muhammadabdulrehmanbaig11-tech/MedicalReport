# MediLens AI
Medical Report Analyser
Saylani final project
development status: completed demonstration project

## Problem Statement
Medical laboratory reports can be extremely difficult for non-technical users to read and understand due to complex jargon, non-standard formats, and obscure reference ranges. MediLens AI attempts to solve this problem by automatically extracting and structuring laboratory data into a clear, readable format. 

**IMPORTANT: This application does not diagnose conditions. It is an educational demonstration tool only.**

## Features
- secure PDF validation;
- in-memory text extraction;
- structured laboratory-result detection;
- deterministic LOW/NORMAL/HIGH classification;
- optional consent-based Groq explanation;
- downloadable PDF summary;
- synthetic sample report;
- automated tests;
- privacy-first processing.

## Workflow
```text
Upload PDF
→ Validate file
→ Extract text
→ Detect laboratory rows
→ Classify using printed reference ranges
→ Optional AI explanation
→ Download summary
```

## Technology
- Python
- Streamlit
- pdfplumber
- Pydantic
- Decimal
- Groq SDK
- fpdf2
- pytest

## Local Setup

Use Windows-friendly commands to set up the project:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m streamlit run src/app.py
```

The `GROQ_API_KEY` is optional. Extraction, classification, and PDF export work completely offline without it. For local AI testing, the key must be supplied securely as an environment variable (e.g. `$env:GROQ_API_KEY="your_key"`). Do not commit a real key to the repository.

## Streamlit Deployment

To deploy on Streamlit Community Cloud:
- repository branch: `main`;
- entrypoint: `src/app.py`;
- dependency file: root `requirements.txt`;
- recommended deployment Python version: `3.13`;
- add `GROQ_API_KEY` through Streamlit Community Cloud Advanced settings/Secrets;
- never commit `.streamlit/secrets.toml`.

## Safety
- **NOT A DIAGNOSIS**: This tool does not provide medical diagnoses.
- **NOT A TREATMENT PLAN**: This tool does not recommend treatments.
- **NOT MEDICATION ADVICE**: This tool does not provide medication advice.
- Classifications come only from ranges printed in the report.
- Laboratory ranges vary between different testing facilities.
- **Users should always consult qualified healthcare professionals for medical advice.**

## Privacy
- PDF processing is performed entirely in memory.
- Uploaded reports are not stored on disk or in a database.
- Raw PDF and raw report text are not sent to Groq.
- Only consented structured, de-identified result fields are sent to the AI model.
- Generated summaries explicitly exclude identity and raw report text.

## Limitations
- Scanned PDFs are unsupported.
- OCR is not implemented.
- Unusual table layouts may not parse correctly.
- Reference ranges must be printed clearly on the same line.
- No diagnosis or historical report storage is supported.
- AI explanations may contain errors.

## Testing
The application has a robust test suite with 73 automated tests that verify deterministic classification, secure extraction, fallback behaviors, and PDF export.

## Project Structure
```text
.
├── src/
│   ├── app.py                  # Main Streamlit interface
│   ├── config.py               # Application configuration
│   ├── analysis/               # Deterministic parsing and classification engine
│   ├── export/                 # PDF summary generation
│   ├── ingestion/              # Secure PDF validation and extraction
│   └── services/               # Safe AI Groq integration
├── tests/                      # Automated test suite
├── samples/                    # Synthetic demonstration reports and generators
├── data/                       # Empty placeholders
├── uploads/                    # Empty placeholders
├── requirements.txt            # Runtime dependencies
├── requirements-dev.txt        # Development dependencies
├── PROJECT_PLAN.md             # Initial project planning document
├── SUBMISSION.md               # Final Saylani submission details
└── README.md                   # Project documentation
```

## License and Attribution
This project was built as a student final project. There is no affiliation with any hospital, laboratory, doctor, Groq, Streamlit, or Saylani beyond stating that it is a student final project.
