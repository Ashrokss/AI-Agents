# Gemini Tutor

Gemini Tutor is an advanced educational AI assistant powered by Google's Gemini models. It provides multimodal, interactive learning experiences tailored to different education levels, with support for real-time search grounding and professional UI styling.

# Demo:
<video controls src="Gemini Multimodal Tutor - Google Chrome 2025-08-15 10-33-01.mp4" title="Gemini-Tutor Demo"></video>


## Project Structure
```
gemini-tutor/
├── __init__.py
├── .env
├── agents.py
├── app.py
├── prompts.py
├── README.md
├── requirements.txt
├── style.py
└── utils.py

```


## Features
- Select between Gemini 2.0 Flash and Gemini 2.5 Flash-Lite models
- Choose education level (Elementary, High School, College, Graduate, PhD)
- Interactive chat interface with multimodal support
- Real-time search grounding and citations
- Professional UI with custom CSS

## Setup Instructions

### 1. Clone the Repository
```
git clone <your-repo-url>
cd gemini-tutor
```

### 2. Install Python Dependencies
Create a virtual environment (recommended):
```
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Mac/Linux
```
Install required packages:
```
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the project root and add your Gemini API key:
```
GOOGLE_GEMINI_API_KEY=your_google_gemini_api_key_here
```

### 4. Run the Streamlit App
```
streamlit run app.py
```

## File Details
- **agents.py**: Defines `TutorAppAgent`, which manages model selection, prompt construction, and learning experience generation.
- **app.py**: Main entry point for the Streamlit web app. Handles UI, session state, and agent interaction.
- **prompts.py**: Contains prompt templates for agent instructions and grounding.
- **style.py**: Custom CSS for a modern, professional look.
- **utils.py**: Helper functions for displaying citations, tool calls, and other metadata.
- **requirements.txt**: List of required Python packages.

## Customization
- To add more models, update `MODEL_OPTIONS` in `app.py` and ensure support in `agents.py`.
- To change UI styles, edit `style.py` and update the CSS classes as needed.

## Troubleshooting
- Ensure your API key is valid and set in `.env`.
- If you encounter missing packages, run `pip install -r requirements.txt` again.
- For Streamlit errors, check the terminal output and logs.
