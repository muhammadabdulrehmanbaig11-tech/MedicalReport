"""
MediLens AI - Main Streamlit Application Entry Point.
Phase 1: PDF Validation and Text Extraction.
"""

import streamlit as st
from src.ingestion.pdf_extractor import extract_text_from_pdf_bytes
from src.ingestion.exceptions import DocumentProcessingError
from src.config import MAX_PDF_SIZE_BYTES

def main():
    st.set_page_config(page_title="MediLens AI", page_icon="🧬")
    st.title("MediLens AI")
    st.info("Medical report analyser under development. (Phase 1)")

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

                    with st.expander("Extracted Text (Read-Only)"):
                        st.text_area("Extracted Text", value=result.extracted_text, height=300, disabled=True)

                    st.info("Note: No medical interpretation has been performed on this text.")

                except DocumentProcessingError as e:
                    st.error(f"Error processing document: {str(e)}")
                except Exception:
                    st.error("An unexpected error occurred during document processing.")

if __name__ == "__main__":
    main()
