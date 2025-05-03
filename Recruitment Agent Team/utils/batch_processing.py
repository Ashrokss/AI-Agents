# batch_processing.py
import streamlit as st
import threading
import json
import pandas as pd
from agents import resume_analyzer

def process_resumes_in_background(resume_ids, job_requirements, callback=None):
    """
    Process multiple resumes in the background
    
    Args:
        resume_ids: List of resume IDs to process
        job_requirements: Job requirements text
        callback: Function to call when processing is complete
    """
    def process_worker():
        for resume_id in resume_ids:
            # Check if resume exists and is not already analyzed
            if resume_id in st.session_state.resumes and not st.session_state.resumes[resume_id]["analyzed"]:
                resume_info = st.session_state.resumes[resume_id]
                
                try:
                    # Analyze the resume
                    result = resume_analyzer(resume_info["path"], job_requirements)
                    
                    # Parse the result
                    try:
                        result_dict = json.loads(result)
                        resume_info["result"] = result_dict
                        resume_info["analyzed"] = True
                    except:
                        # If parsing fails, try to extract JSON from text
                        import re
                        json_match = re.search(r'({.*})', result, re.DOTALL)
                        if json_match:
                            resume_info["result"] = json.loads(json_match.group(1))
                            resume_info["analyzed"] = True
                except Exception as e:
                    print(f"Error processing resume {resume_id}: {e}")

        # Call the callback when done
        if callback:
            callback()
    
    # Start processing in a separate thread
    thread = threading.Thread(target=process_worker)
    thread.daemon = True
    thread.start()
    
    return thread

def generate_comparison_table(resumes_dict):
    """
    Generate a comparison table of all analyzed resumes
    
    Args:
        resumes_dict: Dictionary of resume information
        
    Returns:
        pandas.DataFrame: Comparison table
    """
    data = []
    
    for resume_id, info in resumes_dict.items():
        if info["analyzed"] and info["result"]:
            result = info["result"]
            
            row = {
                "Resume ID": resume_id,
                "Name": result.get("name", "Unknown"),
                "Email": result.get("email", "N/A"),
                "Score": result.get("resume_score", 0),
                "Decision": result.get("selection_decision", "N/A"),
                "Feedback": result.get("feedback", "")[:50] + "..." if result.get("feedback", "") else ""
            }
            
            data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Sort by score (descending)
    if not df.empty and "Score" in df.columns:
        df = df.sort_values("Score", ascending=False)
    
    return df

def export_results_to_json(resumes_dict, job_requirements):
    """
    Export resume analysis results to JSON
    
    Args:
        resumes_dict: Dictionary of resume information
        job_requirements: Job requirements text
        
    Returns:
        str: JSON string
    """
    export_data = {
        "job_requirements": job_requirements,
        "candidates": []
    }
    
    for resume_id, info in resumes_dict.items():
        if info["analyzed"] and info["result"]:
            result = info["result"]
            
            candidate_data = {
                "name": result.get("name", "Unknown"),
                "email": result.get("email", "N/A"),
                "resume_name": info.get("name", "unknown.pdf"),
                "score": result.get("resume_score", 0),
                "decision": result.get("selection_decision", "N/A"),
                "feedback": result.get("feedback", ""),
                "email_sent": info.get("email_sent", False)
            }
            
            if "questions_text" in info and info["questions_text"]:
                candidate_data["questions"] = info["questions_text"]
            
            export_data["candidates"].append(candidate_data)
    
    return json.dumps(export_data, indent=2)

def export_results_to_csv(resumes_dict):
    """
    Export resume analysis results to CSV
    
    Args:
        resumes_dict: Dictionary of resume information
        
    Returns:
        pandas.DataFrame: CSV data
    """
    data = []
    
    for resume_id, info in resumes_dict.items():
        if info["analyzed"] and info["result"]:
            result = info["result"]
            
            row = {
                "Name": result.get("name", "Unknown"),
                "Email": result.get("email", "N/A"),
                "Resume Filename": info.get("name", "unknown.pdf"),
                "Score": result.get("resume_score", 0),
                "Decision": result.get("selection_decision", "N/A"),
                "Feedback": result.get("feedback", ""),
                "Email Sent": "Yes" if info.get("email_sent", False) else "No"
            }
            
            data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Sort by score (descending)
    if not df.empty and "Score" in df.columns:
        df = df.sort_values("Score", ascending=False)
    
    return df