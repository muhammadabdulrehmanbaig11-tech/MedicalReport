# MediLens AI — Medical Report Analyser

## Project Purpose
MediLens AI is a secure, locally-focused application designed to help users understand their medical laboratory reports. It allows users to safely upload their PDF test results and receive clear, deterministic classifications of their markers along with easy-to-understand, non-diagnostic explanations.

## Main Planned Features
* **Secure PDF Upload:** Local ingestion and processing of laboratory test reports.
* **Text Extraction:** Extraction of test parameters and values from PDF documents.
* **Deterministic Classification:** Hard-coded validation of high, low, and normal values based on established reference ranges.
* **Plain-Language Explanations:** Integration with an LLM for understandable summaries of complex medical terminology.
* **Local Storage & History:** Secure local retention of past reports to enable chronological comparison without relying on external cloud databases.
* **Visual Insights:** Interactive charts displaying marker trends over time.
* **PDF Summaries:** Downloadable generated reports highlighting key findings and trends.

## Planned Technology Stack
* **Frontend:** Streamlit
* **Language:** Python
* **PDF Processing:** `pdfplumber`
* **Validation & Data Structures:** Pydantic
* **LLM Integration:** Groq (exclusively for plain-language explanations and optional extraction fallback)
* **Local Storage:** SQLite
* **Visualisation:** Plotly
* **Export Generation:** FPDF2
* **Testing:** pytest
* **Deployment Target:** Streamlit Community Cloud

## Project Structure
```text
Medical Report Analyser Saylani/
├── .gitignore
├── README.md
├── PROJECT_PLAN.md
├── requirements.txt
├── src/
│   ├── app.py
│   ├── config.py
│   ├── ingestion/
│   ├── analysis/
│   ├── services/
│   ├── storage/
│   └── export/
├── tests/
├── data/
└── uploads/
```

## Medical-Safety Disclaimer
**MediLens AI is NOT a diagnostic tool.** It does not provide medical advice, diagnosis, treatment recommendations, or medication recommendations. The application strictly classifies numerical laboratory data against standard reference ranges and provides generalized educational explanations. Always consult a qualified healthcare professional or physician for medical interpretation, diagnosis, and treatment.

## Privacy Approach
MediLens AI prioritises user privacy by retaining data exclusively in local storage (SQLite). The system is designed to minimize the use of external APIs, ensuring that any necessary data sent for processing (such as LLM summarization) is handled strictly and without retaining PII (Personally Identifiable Information).

## Development Status
**Initial scaffold.** This project is currently in the foundational setup phase and is absolutely not production-ready.
