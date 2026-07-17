# MediLens AI — Phased Implementation Plan

## Phase 1: Project foundation
* **Objective:** Establish the initial repository, environment configuration, and minimal application scaffold.
* **Expected files:** `README.md`, `PROJECT_PLAN.md`, `requirements.txt`, basic folder structure.
* **Acceptance criteria:** Project structure exists, dependencies are documented, and safe placeholders are in place. No cloud databases or complex orchestration tools are used.
* **Medical-safety boundary:** No data is processed in this phase.

## Phase 2: PDF validation and secure extraction
* **Objective:** Implement reliable, local text extraction from uploaded medical PDF reports.
* **Expected files:** `src/ingestion/extractor.py`, tests for extraction logic.
* **Acceptance criteria:** `pdfplumber` successfully reads text from standard laboratory formats without relying on external services. The system rejects overly large or malformed PDFs.
* **Medical-safety boundary:** Data extraction must be strictly accurate; no interpretation or alteration of the raw text is allowed.

## Phase 3: Structured laboratory-result models
* **Objective:** Define robust data models for holding extracted laboratory results, metadata, and patient information.
* **Expected files:** `src/analysis/models.py`.
* **Acceptance criteria:** Pydantic models are created to strictly validate the data types of extracted markers (name, value, unit, reference range).
* **Medical-safety boundary:** Validation ensures that only well-formed numeric values and recognized text are accepted for analysis.

## Phase 4: Deterministic high, low and normal classification
* **Objective:** Implement a deterministic algorithm to classify test markers against their reference ranges.
* **Expected files:** `src/analysis/classifier.py`, corresponding test files.
* **Acceptance criteria:** Each numerical test result is accurately flagged as high, low, or normal based strictly on its associated reference bounds.
* **Medical-safety boundary:** The classification logic must be 100% deterministic mathematical comparison, completely decoupled from LLM inference.

## Phase 5: Streamlit upload and results interface
* **Objective:** Create the user-facing Streamlit application for report uploading and structured data presentation.
* **Expected files:** `src/app.py`, `src/ui/components.py`.
* **Acceptance criteria:** Users can upload a PDF and view a rendered table of their extracted and flagged markers.
* **Medical-safety boundary:** Information presented on the screen must clearly distinguish between the exact raw values and any derived flags.

## Phase 6: Groq-generated plain-language explanation
* **Objective:** Integrate Groq API to provide safe, educational summaries of the identified markers.
* **Expected files:** `src/services/llm_service.py`.
* **Acceptance criteria:** The system securely sends extracted marker data to Groq and retrieves a concise, plain-language explanation.
* **Medical-safety boundary:** The LLM prompt must strictly forbid providing diagnoses, treatment advice, or medication recommendations.

## Phase 7: SQLite report history
* **Objective:** Implement local persistence so users can maintain a history of their lab reports.
* **Expected files:** `src/storage/db.py`, schema definitions.
* **Acceptance criteria:** SQLite database is initialized and can store and retrieve historical marker data.
* **Medical-safety boundary:** All health data must be stored locally without exposure to third-party cloud databases like Supabase.

## Phase 8: Charts and report comparison
* **Objective:** Visualize longitudinal trends in marker values.
* **Expected files:** `src/analysis/charts.py`, updates to Streamlit UI.
* **Acceptance criteria:** Plotly charts successfully render historical data for selected markers, enabling visual comparison across dates.
* **Medical-safety boundary:** Charts must accurately reflect the deterministic values stored in the local database without visual distortion.

## Phase 9: PDF export
* **Objective:** Allow users to download a consolidated summary of their analysis.
* **Expected files:** `src/export/pdf_exporter.py`.
* **Acceptance criteria:** The application uses FPDF2 to generate a well-formatted PDF containing the test table and educational summary.
* **Medical-safety boundary:** Exported documents must include a prominent medical disclaimer.

## Phase 10: Tests, privacy review and deployment
* **Objective:** Ensure application reliability and prepare for deployment.
* **Expected files:** Comprehensive test suite in `tests/`, deployment configuration.
* **Acceptance criteria:** All core logic is covered by unit tests. The application deploys successfully to Streamlit Community Cloud.
* **Medical-safety boundary:** Final verification that no diagnostic capabilities have been introduced and the privacy model is intact.
