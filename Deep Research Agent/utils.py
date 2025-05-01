# utils.py
# Contains utility functions for the app

import base64
import streamlit as st

def get_image_base64(image_path):
    """
    Load and encode an image to base64 format
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Base64 encoded image or None if error
    """
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception as e:
        st.warning(f"Could not load image: {e}")
        return None

