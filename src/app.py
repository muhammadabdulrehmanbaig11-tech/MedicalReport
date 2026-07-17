"""
MediLens AI - Main Streamlit Application Entry Point.
Phase 3: Safe AI Explanation and Submission-Ready Streamlit Interface.
"""

import os
import streamlit as st
from src.ingestion.pdf_extractor import extract_text_from_pdf_bytes
from src.ingestion.exceptions import DocumentProcessingError
from src.config import MAX_PDF_SIZE_BYTES, GROQ_API_KEY_ENV_VAR
from src.analysis import parse_laboratory_results
from src.services import generate_plain_language_explanation

def main():
    st.set_page_config(page_title="MediLens AI", page_icon="💊")
    st.title("MediLens AI")
    st.info("Medical report analyser under development. (Phase 3)")

    st.warning(
        "**Medical Disclaimer:** This tool extracts text from laboratory reports. "
        "It performs NO medical interpretation, diagnosis, treatment recommendation, "
        "or medication advice. Always consult a qualified physician for medical advice."
    )

    max_mb = MAX_PDF_SIZE_BYTES // (1024 * 1024)
    uploaded_file = st.file_uploader(
        f"Upload a Blood Report PDF (Max {max_mb} MB)",
        type=["pdf"],
        accept_multiple_files=False
    )

    if uploaded_file is not None:
        if st.button("Extract Report Text"):
            with st.spinner("Extracting text..."):
                file_bytes = uploaded_file.read()
                filename = uploaded_file.name

                try:
                    result = extract_text_from_pdf_bytes(file_bytes, filename)
                    st.success("Extraction successful.")
                    st.write(f"**Filename:** {result.original_filename}")
                    st.write(f"**Page Count:** {result.page_count}")
                    st.write(f"**Character Count:** {result.extracted_character_count}")
                    
                    if result.warnings:
                        st.warning("**Warnings:**\n" + "\n".join(f"- {w}" for w in result.warnings))
                        
                    # Save results to session state so they persist when checkbox is toggled
                    st.session_state['extracted_text'] = result.extracted_text
                except DocumentProcessingError as e:
                    st.error(f"Error processing document: {str(e)}")
                except Exception:
                    st.error("An unexpected error occurred during document processing.")

        if 'extracted_text' in st.session_state:
            lab_results = parse_laboratory_results(st.session_state['extracted_text'])
            
            if lab_results:
                st.write(f"**Detected Laboratory Results:** {len(lab_results)}")
                st.info("Low, Normal and High labels are calculated only from the reference ranges printed in the uploaded report. They are not a diagnosis.")
                
                table_data = []
                for r in lab_results:
                    ref_str = r.reference_text if r.reference_text else ""
                    unit_str = r.unit if r.unit else ""
                    table_data.append({
                        "Test": r.test_name,
                        "Value": str(r.value),
                        "Unit": unit_str,
                        "Reference range": ref_str,
                        "Status": r.status.value
                    })
                    
                st.table(table_data)

                st.markdown("---")
                st.write("**AI Explanation**")
                st.info(
                    "The PDF itself and raw extracted text will NOT be sent. "
                    "Only de-identified structured result fields will be sent to Groq."
                )
                consent = st.checkbox("I understand that structured laboratory results will be sent to Groq for a general AI-generated explanation.")
                if consent:
                    api_key = os.environ.get(GROQ_API_KEY_ENV_VAR)
                    if not api_key:
                        st.warning("AI explanation is unavailable because the Groq API key is missing.")
                    elif st.button("Generate Plain-Language Explanation"):
                        with st.spinner("Generating explanation..."):
                            explanation = generate_plain_language_explanation(lab_results)
                            st.write("### Explanation")
                            st.write(explanation.summary_text)
                            st.caption(explanation.safety_disclaimer)
                            for w in explanation.warnings:
                                st.warning(w)

            else:
                st.info("No structured laboratory results could be detected reliably.")

            with st.expander("Extracted Text (Read-Only)"):
                st.text_area("Extracted Text", value=st.session_state['extracted_text'], height=300, disabled=True)

if __name__ == "__main__":
    main()
