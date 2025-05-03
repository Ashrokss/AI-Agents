#agents.py 

import streamlit as st 
from agno.agent import Agent
from agno.models.azure import AzureOpenAI
from agno.tools.duckduckgo import DuckDuckGoTools
from utils.text_extraction import extract_text_from_pdf
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ----------------------------------Resume Analyzer agent--------------------------------------------------
def resume_analyzer(pdf_file_path: str, job_requirements: str):
    """
    Analyze a resume against custom job requirements.
    
    Args:
        pdf_file_path: Path to the PDF resume file
        job_requirements: Custom job requirements text provided by HR
    """
    # Step 1: Extract resume text
    extracted_text = extract_text_from_pdf(pdf_file_path)

    # Step 2: Initialize the agent
    agent = Agent(
        model=AzureOpenAI(
            azure_deployment="gpt-4o-mini",
            api_version="2024-02-15-preview",
        ),
        show_tool_calls=False,
        description="You are an expert technical recruiter who analyzes multiple resumes.",
        instructions=(
            "Analyze the resume against the provided job requirements.\n"
            "Be lenient with AI/ML candidates who show strong potential.\n"
            "Consider project experience as valid experience.\n"
            "Value hands-on experience with key technologies.\n"
            "Return a JSON response with selection decision as (Rejected or Selected) and feedback.\n"
            "The feedback must be detailed and proper."
            "Also return a structured response containing the Name and email id of the each candidate.\n"
            "Also include a resume_score from 0 to 100 representing how well the resume matches the job requirements.\n"
            "**Return a JSON response** in the following format:\n"
            "{\n"
            '  "name": "Candidate Name",\n'
            '  "email": "candidate@email.com",\n'
            '  "selection_decision": "Selected" or "Rejected",\n'
            '  "resume_score": 85,\n'
            '  "feedback": "Some feedback text"\n'
            "}\n"
        ),
        use_json_mode=True
    )

    # Step 3: Prompt to analyze
    prompt = f"""
    Resume:
    {extracted_text}

    Job Requirements:
    {job_requirements}
    """

    # Step 4: Run the agent and return the output
    response = agent.run(prompt)
    return response.content



# -----------------------------------------Test question Generator--------------------------------------- 

def test_question_generator(pdf_file_path: str, job_requirements: str):
    """
    Generate test questions based on resume and custom job requirements.
    
    Args:
        pdf_file_path: Path to the PDF resume file
        job_requirements: Custom job requirements text provided by HR
    """
    extracted_text = extract_text_from_pdf(pdf_file_path)

    # Initialize the agent
    agent = Agent(
        model=AzureOpenAI(
            azure_deployment="gpt-4o-mini",
            api_version="2024-02-15-preview",
        ),
        show_tool_calls=False,
        description="You are an expert technical interviewer who generates relevant test questions.",
        instructions=(
            "Analyze the candidate's resume and the target role requirements.\n"
            "Generate 5-10 technical interview questions specific to the candidate's background and the role.\n"
            "Focus on the required skills mentioned in the job requirements.\n"
            "Keep the questions practical and relevant.\n"
            "Return the questions only in a proper format.\n"
            "Do not repeat any questions"
        ),
        expected_output=(
            """
            1. Question 1 ....
            2. Question 2 ....

            Repeat for all questions
            """
        ),
        markdown=True
    )

    prompt = f"""
    Resume:
    {extracted_text}

    Job Requirements:
    {job_requirements}
    """
    response = agent.run(prompt)
    return response.content


def send_email_to_candidate(name: str, email: str, selected: str, questions=None):
    """Send an email to the candidate with results and questions if selected."""
    # Email configuration
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    EMAIL_SENDER = os.environ.get('sender_email')
    # Use App Password if 2FA enabled
    EMAIL_PASSWORD = os.environ.get('sender_passkey')

    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        st.error(
            "Email credentials not found in environment variables. Check your .env file.")
        return False

    subject = "Application Result"
    if selected.lower() == "selected":
        body = f"""
Dear {name},

Congratulations! 🎉

After reviewing your resume, we are pleased to inform you that you have been selected for the next steps in our hiring process.

You will receive test questions for your evaluation shortly. Please reply to this email to submit your answers.

All the best,

Best regards,  
Recruitment Team
"""
        # If questions are provided, send them in another email
        if questions:
            questions_subject = "Technical Assessment Questions"
            questions_body = f"""
Dear {name},

As part of our selection process, please answer the following technical questions:

{questions}

Please reply to this email with your answers.

Best regards,  
Recruitment Team
"""
    elif selected.lower() == "rejected":
        body = f"""
Dear {name},

Thank you for applying to our company.

After a thorough review of your resume, we regret to inform you that you were not selected for the role at this time.

We encourage you to apply again in the future and wish you the very best in your career.

Warm regards,  
Recruitment Team
"""

    try:
        # Compose the email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Send the email via SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)

        # Send questions in a separate email if selected
        if selected.lower() == "selected" and questions:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_SENDER
            msg['To'] = email
            msg['Subject'] = questions_subject
            msg.attach(MIMEText(questions_body, 'plain'))

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.send_message(msg)

        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False