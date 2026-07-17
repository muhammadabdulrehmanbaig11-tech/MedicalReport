# MediLens AI — Final Submission

**GitHub Repository URL:** [https://github.com/muhammadabdulrehmanbaig11-tech/MedicalReport.git]  
**Deployed Streamlit URL:** [DEPLOYMENT_URL_PLACEHOLDER]  
**Demonstration Video URL:** [VIDEO_URL_PLACEHOLDER]  

**Student Name:** [STUDENT_NAME_PLACEHOLDER]  
**Batch:** [BATCH_PLACEHOLDER]  
**Roll Number:** [ROLL_NUMBER_PLACEHOLDER]  

---

## 1. Project Title
MediLens AI - Medical Report Analyser

## 2. Student-Project Purpose
This project is submitted as the final capstone project for the Saylani Web/Mobile/AI development program. It demonstrates end-to-end Python programming, Streamlit UI development, PDF manipulation, regular expressions, and LLM API integrations within strict security boundaries.

## 3. Problem Being Solved
Medical laboratory reports are notoriously difficult for non-technical users to read. The data is often unstructured, dense, and full of medical jargon. Patients frequently struggle to identify which of their blood tests are outside normal ranges before their official follow-up doctor appointments.

## 4. Objectives
- Automatically ingest and extract text from digital PDF laboratory reports.
- Deterministically structure the extracted data into readable tables.
- Highlight LOW, NORMAL, and HIGH values mathematically without relying on AI hallucination.
- Optionally provide safe, de-identified plain-language explanations using the Groq API.
- Generate a clear, shareable PDF summary.

## 5. System Workflow
1. **Upload:** User uploads a PDF.
2. **Validate:** System validates file size and format constraints.
3. **Extract:** Text is extracted securely in-memory.
4. **Detect:** Deterministic regex engines detect laboratory rows and reference ranges.
5. **Classify:** Decimal math classifies the results.
6. **Explain (Optional):** De-identified results are sent to Groq for a strictly prompted explanation.
7. **Download:** User exports a generated PDF summary.

## 6. Core Features
- Secure PDF validation.
- In-memory text extraction.
- Structured laboratory-result detection.
- Deterministic LOW/NORMAL/HIGH classification.
- Optional consent-based Groq explanation.
- Downloadable PDF summary.
- Synthetic sample report generation.

## 7. Technology Stack
- **Python 3.13:** Core programming language.
- **Streamlit:** Web interface framework.
- **pdfplumber:** Robust PDF extraction.
- **Pydantic:** Data validation and typing models.
- **Groq SDK:** High-speed LLM inference (Llama-3.3-70b-versatile).
- **fpdf2:** Programmatic PDF generation.
- **pytest:** Automated unit testing.

## 8. Project Architecture
The application is structured into highly cohesive, loosely coupled Python modules:
- `src/ingestion`: Handles secure file reading and PDF extraction.
- `src/analysis`: Deterministic regex parsing and Decimal-based classification models.
- `src/services`: Gated, safe prompt construction and Groq API calls.
- `src/export`: In-memory PDF synthesis.
- `src/app.py`: Streamlit presentation layer.

## 9. Testing Strategy and Final Results
The project uses `pytest` to enforce functionality and prevent regressions. It includes tests for:
- PDF spoofing, corruption, and encryption rejection.
- Edge cases in reference range overlaps.
- Decimal precision.
- Missing API keys and Rate Limit errors.
- Export behavior and formatting.
**Final Results:** 73 passing tests. 100% core pipeline success rate.

## 10. Security Controls
- No database or external storage persistence.
- Zero local file writing of uploaded documents.
- API keys are injected via secure environment variables.
- Exception traces are caught and masked with safe, user-friendly messages.

## 11. Privacy Controls
- All processing is strictly in-memory.
- The raw text of the PDF report is never sent to the LLM.
- Only the specific mathematical result fields (Test Name, Value, Unit, Range) are sent to Groq.
- The exported summary strips all patient metadata, PII, and filenames.

## 12. Medical-Safety Controls
- Explanations are gated behind an explicit consent checkbox.
- Mathematical classification (`LOW`/`NORMAL`/`HIGH`) is computed using local, deterministic code based entirely on the printed ranges on the document. It does NOT use AI to determine if a value is high or low.
- Strong medical disclaimers are prominently embedded in the UI and the generated PDF.
- The system prompt physically restricts the LLM from diagnosing conditions or recommending treatments.

## 13. Limitations
- Unstructured scanned images require OCR, which is not implemented.
- Unusual, dense, or badly formatted PDF tables may fail regex extraction.
- The AI explanation is purely educational and relies on external API uptime.

## 14. Future Improvements
- Integrate OCR libraries (like Tesseract) for scanned documents.
- Support historic trend visualization (Charts/Graphs).
- Add support for multiple languages.

## 15. Local-Run Instructions
To run this application locally on Windows:
```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m streamlit run src/app.py
```

## 16. Streamlit Deployment Fields
- **Repository:** https://github.com/muhammadabdulrehmanbaig11-tech/MedicalReport.git
- **Branch:** `main`
- **Entrypoint:** `src/app.py`
- **Python Version:** `3.13`
