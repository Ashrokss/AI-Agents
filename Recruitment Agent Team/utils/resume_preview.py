# resume_preview.py
import base64
import streamlit as st

def display_pdf(file_path):
    """Display the PDF file in the Streamlit app"""
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    
    # Embed PDF viewer
    pdf_display = f"""
        <iframe
            src="data:application/pdf;base64,{base64_pdf}"
            width="100%"
            height="500px"
            style="border: 1px solid #ddd; border-radius: 5px;"
            type="application/pdf">
        </iframe>
    """
    st.markdown(pdf_display, unsafe_allow_html=True)

def display_pdf_thumbnail(file_path, height="200px"):
    """Display a smaller thumbnail of the PDF file"""
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    
    # Embed PDF viewer as thumbnail
    pdf_display = f"""
        <iframe
            src="data:application/pdf;base64,{base64_pdf}"
            width="100%"
            height="{height}"
            style="border: 1px solid #ddd; border-radius: 5px;"
            type="application/pdf">
        </iframe>
    """
    st.markdown(pdf_display, unsafe_allow_html=True)