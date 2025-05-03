# text_extraction.py
import PyPDF2
import os
import traceback
import streamlit as st

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        str: Extracted text
    """
    text = ""
    
    try:
        # Check if file exists
        if not os.path.exists(pdf_path):
            return f"Error: File not found at {pdf_path}"
        
        # Open the PDF file
        with open(pdf_path, 'rb') as file:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Get the number of pages
            num_pages = len(pdf_reader.pages)
            
            # Extract text from each page
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n\n"
                
        # If no text was extracted, return a message
        if not text.strip():
            return "No text could be extracted from the PDF. The PDF may be scanned or contain images."
            
        return text
        
    except Exception as e:
        error_msg = f"Error extracting text from PDF: {str(e)}\n{traceback.format_exc()}"
        st.error(error_msg)
        return f"Error processing PDF: {str(e)}"