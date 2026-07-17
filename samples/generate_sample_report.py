import os
from fpdf import FPDF

def generate_sample_report():
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Synthetic Laboratory Report", ln=True, align="C")
    
    pdf.set_font("Helvetica", "I", 12)
    pdf.cell(0, 10, "Demonstration Data Only", ln=True, align="C")
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 10, "This is synthetic demonstration data and not a real medical report.", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Courier", "", 10)
    lines = [
        "Hemoglobin 11.2 g/dL 12.0 - 16.0",
        "Glucose | 96 | mg/dL | 70 - 99",
        "Platelets 250 10^3/uL 150 - 450",
        "TSH 4.8 mIU/L < 4.0",
        "Ferritin 18 ng/mL > 15"
    ]
    
    for line in lines:
        pdf.cell(0, 6, line, ln=True)
        
    out_path = os.path.join(os.path.dirname(__file__), "sample_lab_report.pdf")
    pdf.output(out_path)
    print(f"Generated: {out_path}")

if __name__ == "__main__":
    generate_sample_report()
