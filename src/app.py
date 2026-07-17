"""
MediLens AI - Main Streamlit Application Entry Point.
"""

import os
import streamlit as st

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ingestion.pdf_extractor import extract_text_from_pdf_bytes
from src.ingestion.exceptions import DocumentProcessingError
from src.config import MAX_PDF_SIZE_BYTES, GROQ_API_KEY_ENV_VAR
from src.analysis import parse_laboratory_results
from src.services import generate_plain_language_explanation
from src.export import generate_report_summary_pdf, ReportExportError

def main():
    st.set_page_config(
        page_title="MediLens AI",
        page_icon="🩺",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    # Clean Professional CSS
    st.markdown("""
        <style>
        /* Restrained, professional styling */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            font-family: 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            color: #333333;
        }
        h1, h2, h3 {
            color: #0F2A4A !important;
            font-weight: 600 !important;
        }
        .hero-card {
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .hero-title {
            font-size: 28px;
            font-weight: 700;
            color: #0F2A4A;
            margin-bottom: 8px;
        }
        .hero-subtitle {
            font-size: 16px;
            color: #475569;
            margin-bottom: 16px;
        }
        .trust-indicators {
            display: flex;
            gap: 16px;
            font-size: 13px;
            color: #64748B;
        }
        .trust-indicator {
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .disclaimer-card {
            background-color: #FFFBEB;
            border-left: 4px solid #F59E0B;
            padding: 16px;
            border-radius: 4px;
            color: #78350F;
            font-size: 14px;
            margin-bottom: 24px;
        }
        .compact-summary {
            background-color: #F0FDF4;
            border: 1px solid #BBF7D0;
            border-radius: 6px;
            padding: 12px 16px;
            margin-bottom: 16px;
            color: #166534;
            font-size: 14px;
        }
        .ai-explanation-card {
            background-color: #FFFFFF;
            border: 1px solid #CBD5E1;
            border-radius: 8px;
            padding: 20px;
            margin-top: 16px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            font-size: 15px;
            line-height: 1.6;
        }
        .footer {
            margin-top: 48px;
            padding-top: 16px;
            border-top: 1px solid #E2E8F0;
            text-align: center;
            font-size: 13px;
            color: #94A3B8;
        }
        </style>
    """, unsafe_allow_html=True)

    # Hero Card
    st.markdown("""
        <div class="hero-card">
            <div class="hero-title">MediLens AI</div>
            <div class="hero-subtitle">Understand your laboratory report more clearly</div>
            <div style="font-size: 15px; color: #334155; margin-bottom: 16px;">
                Securely extract laboratory values, compare them with the reference ranges printed in your report, and generate an optional plain-language AI explanation.
            </div>
            <div class="trust-indicators">
                <div class="trust-indicator">✓ In-memory processing</div>
                <div class="trust-indicator">✓ Deterministic classification</div>
                <div class="trust-indicator">✓ Optional AI explanation</div>
            </div>
            <div style="font-size: 12px; color: #94A3B8; margin-top: 16px;">
                Your PDF is processed in memory and is not permanently stored.
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Medical Disclaimer
    st.markdown("""
        <div class="disclaimer-card">
            <strong>Medical Disclaimer</strong><br/>
            MediLens AI compares detected laboratory values only with the reference ranges printed in the uploaded report. Optional AI explanations are provided for general educational purposes only. This application does not provide a diagnosis, treatment plan, medication advice, or a substitute for care from a qualified healthcare professional.
        </div>
    """, unsafe_allow_html=True)

    # 1. Upload Section
    st.markdown("### 1. Upload your laboratory report")
    st.markdown("<span style='color: #475569; font-size: 14px;'>Upload one text-based PDF laboratory report. Maximum file size: 10 MB.</span>", unsafe_allow_html=True)

    max_mb = MAX_PDF_SIZE_BYTES // (1024 * 1024)
    uploaded_file = st.file_uploader(
        label="Select PDF File",
        type=["pdf"],
        accept_multiple_files=False,
        label_visibility="collapsed"
    )

    if uploaded_file is not None:
        if st.button("Analyse Laboratory Report", type="primary"):
            with st.spinner("Processing document..."):
                file_bytes = uploaded_file.read()
                filename = uploaded_file.name

                try:
                    result = extract_text_from_pdf_bytes(file_bytes, filename)
                    
                    st.session_state['extracted_text'] = result.extracted_text
                    st.session_state['filename'] = result.original_filename
                    st.session_state['page_count'] = result.page_count
                    st.session_state['char_count'] = result.extracted_character_count
                    
                    if 'ai_explanation' in st.session_state:
                        del st.session_state['ai_explanation']
                        
                    if result.warnings:
                        st.warning("**Warnings:**\n" + "\n".join(f"- {w}" for w in result.warnings))

                except DocumentProcessingError as e:
                    st.error(f"Error processing document: {str(e)}")
                except Exception:
                    st.error("An unexpected error occurred during document processing.")

        if 'extracted_text' in st.session_state:
            lab_results = parse_laboratory_results(st.session_state['extracted_text'])
            
            # Extraction Success Card
            st.markdown(f"""
                <div class="compact-summary">
                    <strong>Extraction successful</strong> &nbsp;&bull;&nbsp; 
                    {st.session_state.get('filename', 'Unknown')} &nbsp;&bull;&nbsp; 
                    {st.session_state.get('page_count', 0)} pages &nbsp;&bull;&nbsp; 
                    {st.session_state.get('char_count', 0)} characters &nbsp;&bull;&nbsp; 
                    {len(lab_results) if lab_results else 0} results detected
                </div>
            """, unsafe_allow_html=True)
            
            if lab_results:
                # 2. Structured Results Section
                st.markdown("### 2. Detected Laboratory Results")
                
                table_data = []
                for r in lab_results:
                    ref_str = r.reference_text if r.reference_text else ""
                    unit_str = r.unit if r.unit else ""
                    
                    # Restrained visual status badges for Pandas dataframe rendering if possible,
                    # but we keep the underlying values exact as requested.
                    status_val = r.status.value
                    if status_val == "LOW":
                        status_display = "⬇ LOW"
                    elif status_val == "HIGH":
                        status_display = "⬆ HIGH"
                    elif status_val == "NORMAL":
                        status_display = "✓ NORMAL"
                    else:
                        status_display = "— UNDETERMINED"

                    table_data.append({
                        "Test": r.test_name,
                        "Value": str(r.value),
                        "Unit": unit_str,
                        "Reference Range": ref_str,
                        "Status": status_display
                    })
                    
                st.dataframe(table_data, use_container_width=True, hide_index=True)
                
                st.markdown("<div style='font-size: 13px; color: #64748B; margin-top: -10px; margin-bottom: 24px;'>These labels are calculated only from the reference ranges printed in the uploaded report. They are not a diagnosis.</div>", unsafe_allow_html=True)

                # 3. AI Explanation Section
                st.markdown("### 3. Optional Plain-Language Explanation")
                st.markdown("<div style='font-size: 14px; color: #475569; margin-bottom: 12px;'>Only the structured test name, value, unit, printed reference range and calculated status will be sent to Groq. The original PDF, raw extracted text and identity information will not be sent.</div>", unsafe_allow_html=True)
                
                consent = st.checkbox("I understand that structured laboratory results will be sent to Groq for a general AI-generated explanation.")
                
                if consent:
                    api_key = os.environ.get(GROQ_API_KEY_ENV_VAR)
                    if not api_key:
                        st.info("AI explanation is currently unavailable because the Groq API key is missing from the environment.", icon="ℹ️")
                    elif st.button("Generate AI Explanation"):
                        with st.spinner("Generating explanation..."):
                            explanation = generate_plain_language_explanation(lab_results)
                            if explanation.ai_used:
                                st.session_state['ai_explanation'] = explanation.summary_text
                                st.rerun()
                            else:
                                st.markdown(f"<div class='ai-explanation-card'>{explanation.summary_text}</div>", unsafe_allow_html=True)
                                st.caption(explanation.safety_disclaimer)
                                for w in explanation.warnings:
                                    st.warning(w)

                if 'ai_explanation' in st.session_state:
                    st.markdown(f"<div class='ai-explanation-card'>{st.session_state['ai_explanation']}</div>", unsafe_allow_html=True)
                    st.caption("This AI-generated explanation is for general educational purposes only. It is not a diagnosis, treatment plan or substitute for advice from a qualified healthcare professional.")

                st.markdown("<br/>", unsafe_allow_html=True)

                # 4. Download Section
                st.markdown("### 4. Download Your Summary")
                st.markdown("<span style='color: #475569; font-size: 14px; display: block; margin-bottom: 12px;'>Download a privacy-conscious PDF containing the structured results and, when generated, the optional AI explanation.</span>", unsafe_allow_html=True)
                try:
                    ai_text = st.session_state.get('ai_explanation')
                    pdf_bytes = generate_report_summary_pdf(lab_results, ai_explanation=ai_text)
                    st.download_button(
                        label="Download PDF Summary",
                        data=pdf_bytes,
                        file_name="medilens-medical-report-summary.pdf",
                        mime="application/pdf"
                    )
                except ReportExportError as e:
                    st.error(f"Could not generate PDF summary: {str(e)}")
                except Exception:
                    st.error("An unexpected error occurred while generating the PDF summary.")

            else:
                st.info("No structured laboratory results could be detected reliably.")
                st.markdown("<span style='font-size: 14px; color: #64748B;'>The report may use an unsupported layout, contain scanned images, or omit clear reference ranges.</span>", unsafe_allow_html=True)

            st.markdown("<br/>", unsafe_allow_html=True)
            with st.expander("View extracted raw text"):
                st.markdown("<span style='font-size: 13px; color: #64748B;'>Extracted text may contain spacing or formatting errors from the original PDF.</span>", unsafe_allow_html=True)
                st.text_area(label="Extracted text", value=st.session_state['extracted_text'], height=250, disabled=True, label_visibility="collapsed")

    # Footer
    st.markdown("""
        <div class="footer">
            MediLens AI · Privacy-first laboratory report analysis · Educational use only
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
