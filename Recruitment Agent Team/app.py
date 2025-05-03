# app.py
import streamlit as st
from streamlit_option_menu import option_menu
import json
import tempfile
import matplotlib.pyplot as plt
import os
import uuid
from dotenv import load_dotenv
import pandas as pd
from utils.resume_preview import display_pdf
from agents import resume_analyzer, test_question_generator, send_email_to_candidate

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(page_title="Resume Analyzer", layout="wide")

# Initialize session state variables
if 'job_skills' not in st.session_state:
    st.session_state.job_skills = []
if 'resumes' not in st.session_state:
    # Dictionary to store resume info: {id: {path, name, analyzed, result}}
    st.session_state.resumes = {}
if 'job_requirements' not in st.session_state:
    st.session_state.job_requirements = ""
if 'selected_resume_id' not in st.session_state:
    st.session_state.selected_resume_id = None
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Upload"
if 'show_all_analyzed' not in st.session_state:
    st.session_state.show_all_analyzed = False

# Common skills for different tech roles
COMMON_SKILLS = [
    "Python", "Java", "JavaScript", "C++", "C#", "React", "Angular", "Vue.js",
    "Node.js", "Express.js", "Django", "Flask", "FastAPI", "Spring Boot",
    "SQL", "MongoDB", "PostgreSQL", "MySQL", "Redis", "AWS", "Azure", "GCP",
    "Docker", "Kubernetes", "CI/CD", "Git", "TensorFlow", "PyTorch", "Scikit-learn",
    "NLP", "Computer Vision", "Data Analysis", "Machine Learning", "Deep Learning",
    "DevOps", "Agile", "Scrum", "REST API", "GraphQL", "Microservices",
    "System Design", "Cloud Architecture", "Mobile Development", "iOS", "Android"
]


def save_uploaded_file(uploaded_file):
    """Save uploaded file to temp directory and return file path"""
    # Generate a unique ID for this resume
    resume_id = str(uuid.uuid4())

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        file_path = tmp_file.name

    # Store resume info in session state
    st.session_state.resumes[resume_id] = {
        "path": file_path,
        "name": uploaded_file.name,
        "analyzed": False,
        "result": None
    }

    return resume_id


def delete_resume(resume_id):
    """Delete a resume from the list and remove the temp file"""
    if resume_id in st.session_state.resumes:
        # Delete the temporary file
        file_path = st.session_state.resumes[resume_id]["path"]
        if os.path.exists(file_path):
            try:
                os.unlink(file_path)
            except:
                pass

        # Remove from session state
        del st.session_state.resumes[resume_id]

        # Reset selected resume if it was the deleted one
        if st.session_state.selected_resume_id == resume_id:
            st.session_state.selected_resume_id = None


def analyze_resume(resume_id):
    """Analyze a single resume"""
    resume_info = st.session_state.resumes[resume_id]

    # Analyze the resume
    result = resume_analyzer(
        resume_info["path"], st.session_state.job_requirements)

    # Parse the result
    try:
        # Try to parse the result directly
        result_dict = json.loads(result)
    except:
        # If direct parsing fails, try to extract JSON from text
        import re
        json_match = re.search(r'({.*})', result, re.DOTALL)
        if json_match:
            result_dict = json.loads(json_match.group(1))
        else:
            return False

    # Update resume info in session state
    resume_info["analyzed"] = True
    resume_info["result"] = result_dict

    return True


def get_highest_scoring_resumes(limit=5):
    """Get the highest scoring resumes"""
    if not st.session_state.resumes:
        return []

    analyzed_resumes = {
        rid: info for rid, info in st.session_state.resumes.items()
        if info["analyzed"] and info["result"]
    }

    # Sort by score (descending)
    sorted_resumes = sorted(
        analyzed_resumes.items(),
        key=lambda x: x[1]["result"].get("resume_score", 0),
        reverse=True
    )

    return sorted_resumes[:limit]


def get_match_status(score, selection_decision):
    """Get match status based on score and selection decision"""
    if selection_decision.lower() == "selected":
        return "Strong Match", "green"
    else:
        # For rejected candidates, show more detailed remarks
        if score >= 70:
            return "Moderate Match", "orange"  # Even high scoring can be rejected for specific reasons
        elif score >= 50:
            return "Moderate Match", "orange"
        else:
            return "Poor Match", "red"



# Streamlit UI

def main():
    st.title("👨🏻‍💻 Automated Recruitment Agent Team")

    with st.sidebar:
        # Navigation using option menu - reduced to just 2 options
        selected = option_menu(
            menu_title="Navigation",  # Menu title
            options=["Home", "Resume Analysis"],  # Menu options - reduced to 2
            icons=["house-door-fill", "clipboard-check"],  # Optional icons
            menu_icon="cast",  # Menu icon
            default_index=0,  # Default selected index
        )

        # Set the selected tab in session state
        if selected == "Home":
            st.session_state.active_tab = "Upload"
        elif selected == "Resume Analysis":
            st.session_state.active_tab = "Results"

    # Conditional rendering based on active tab
    if st.session_state.active_tab == "Upload":
        render_job_configuration()
    elif st.session_state.active_tab == "Results":
        render_resume_results()


def render_job_configuration():
    # Job Role Configuration Section
    st.header("Job Role Configuration")

    # Define job title and description
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        job_title = st.text_input(
            "Job Title", placeholder="e.g., Senior Python Developer")

    with col2:
        experience_level = st.selectbox(
            "Experience Level",
            ["Entry Level", "Junior (1-3 years)", "Mid-level (3-5 years)",
             "Senior (5+ years)", "Lead/Architect"]
        )

    job_description = st.text_area(
        "Job Description",
        placeholder="Enter detailed job description including responsibilities and requirements...",
        height=150
    )

    # Skills Selection with multi-select and ability to add custom skills
    st.subheader("Required Skills")

    # Good to have skill input
    custom_skill = st.text_input("Add Good to have Skill")
    if custom_skill and st.button("Add Skill"):
        if custom_skill not in COMMON_SKILLS and custom_skill not in st.session_state.job_skills:
            st.session_state.job_skills.append(custom_skill)

    # Display and edit custom skills
    if st.session_state.job_skills:
        st.write("Custom Skills:")
        cols = st.columns(4)
        skills_to_remove = []

        for i, skill in enumerate(st.session_state.job_skills):
            col_idx = i % 4
            with cols[col_idx]:
                if st.button(f"❌ {skill}"):
                    skills_to_remove.append(skill)

        # Remove selected skills
        for skill in skills_to_remove:
            st.session_state.job_skills.remove(skill)

    # Select from common skills
    selected_common_skills = st.multiselect(
        "Select Required Skills",
        COMMON_SKILLS
    )

    # Combine all selected skills
    all_skills = selected_common_skills + st.session_state.job_skills

    # Generate final job requirements
    if job_title and job_description:
        full_job_requirements = f"""
## {job_title} ({experience_level})

{job_description}

### Required Skills:
{', '.join(all_skills) if all_skills else 'No specific skills selected'}
"""

        with st.expander("Preview Job Requirements", expanded=True):
            st.markdown(full_job_requirements)

            # Save job requirements button
            if st.button("Save Job Requirements"):
                st.session_state.job_requirements = full_job_requirements
                st.success("✅ Job requirements saved successfully!")

    # Resume Upload Section
    st.markdown("---")
    st.header("Resume Upload")

    uploaded_files = st.file_uploader("Upload Resumes (PDF)",
                                      type="pdf",
                                      accept_multiple_files=True,
                                      key="resume_uploader")

    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Check if this file is already uploaded (by name)
            file_exists = any(
                info["name"] == uploaded_file.name for info in st.session_state.resumes.values())

            if not file_exists:
                # Save the file and add to session state
                save_uploaded_file(uploaded_file)

        st.success(f"✅ {len(uploaded_files)} resume(s) uploaded successfully!")

    # Display uploaded resumes
    if st.session_state.resumes:
        st.markdown("### Uploaded Resumes")

        # Use a container with columns for each resume
        for resume_id, info in list(st.session_state.resumes.items()):
            with st.container(border=True):
                cols = st.columns([3, 1, 1])
                cols[0].write(f"**{info['name']}**")

                # Fix for Delete button - use unique keys and call the delete function
                delete_key = f"delete_{resume_id}"
                if cols[2].button("Delete", key=delete_key):
                    delete_resume(resume_id)
                    st.rerun()
                    
        # Analyze All button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            unanalyzed_count = sum(
                1 for info in st.session_state.resumes.values() if not info["analyzed"])
            if unanalyzed_count > 0:
                if st.button(f"🧠 Analyze All Remaining ({unanalyzed_count})", key="analyze_all_home", use_container_width=True):
                    progress_bar = st.progress(0)
                    to_analyze = [
                        rid for rid, info in st.session_state.resumes.items() if not info["analyzed"]]
                    total = len(to_analyze)

                    for i, resume_id in enumerate(to_analyze):
                        with st.spinner(f"Analyzing {st.session_state.resumes[resume_id]['name']}..."):
                            analyze_resume(resume_id)
                        progress_bar.progress((i + 1) / total)

                    st.success(f"✅ Successfully analyzed {total} resumes!")
                    st.session_state.show_all_analyzed = True
                    st.session_state.active_tab = "Results"
                    st.rerun()


def render_resume_details(resume_id):
    """Render full details of a selected resume"""
    if resume_id not in st.session_state.resumes:
        st.error("Resume not found!")
        return
        
    resume_info = st.session_state.resumes[resume_id]
    
    # --- Selected Resume Preview ---
    st.markdown("---")
    st.subheader(f"📑 Preview: {resume_info['name']}")
    display_pdf(resume_info["path"])

    # Analyze if not yet analyzed
    if not resume_info["analyzed"]:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔍 Analyze This Resume", key="analyze_single", use_container_width=True):
                with st.spinner("Analyzing resume..."):
                    if analyze_resume(resume_id):
                        st.success("✅ Resume analyzed successfully!")
                        st.rerun()
                    else:
                        st.error(
                            "❌ Failed to analyze resume. Please try again.")
    else:
        # --- Analysis Results ---
        result_dict = resume_info["result"]
        st.markdown("---")
        with st.container(border=True):
            st.markdown("## 🧾 Analysis Results")

            score = result_dict.get("resume_score", 0)
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**Resume Score:** {score}/100")
                st.progress(score / 100)
            with col2:
                selection_decision = result_dict.get("selection_decision", "Rejected")
                match_text, color = get_match_status(score, selection_decision)
                st.markdown(
                    f"<h3 style='color: {color};'>{match_text}</h3>", unsafe_allow_html=True)

        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("👤 Candidate Info")
                st.write(f"**Name:** {result_dict.get('name', 'N/A')}")
                st.write(f"**Email:** {result_dict.get('email', 'N/A')}")
            with col2:
                st.subheader("📝 Selection Decision")
                ai_decision = result_dict.get("selection_decision", "N/A")
                hr_decision_index = 0 if ai_decision.lower() == "selected" else 1

                hr_decision = st.selectbox(
                    "HR Decision (Override)",
                    ["Selected", "Rejected"],
                    index=hr_decision_index,
                    key=f"hr_decision_{resume_id}"
                )

                color = "green" if hr_decision.lower() == "selected" else "red"
                st.markdown(
                    f"<h4 style='color: {color};'>{hr_decision}</h4>", unsafe_allow_html=True)
                if hr_decision.lower() != ai_decision.lower():
                    st.info("⚠️ Original AI decision was overridden")

            st.markdown("#### 🗣️ Feedback")
            hr_feedback = st.text_area("Edit feedback if needed:",
                                       value=result_dict.get(
                                           "feedback", "No feedback provided"),
                                       height=150,
                                       key=f"hr_feedback_{resume_id}")

            # Apply Feedback Changes (Centered)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("💾 Apply Feedback Changes", key=f"apply_feedback_{resume_id}", use_container_width=True):
                    resume_info["result"]["selection_decision"] = hr_decision
                    resume_info["result"]["feedback"] = hr_feedback
                    st.success("✅ Feedback updated successfully!")

            # --- If selected, handle question generation and email ---
            if hr_decision.lower() == "selected":
                if "questions_text" not in resume_info or not resume_info["questions_text"]:
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if st.button("⚙️ Generate Questions", key=f"gen_questions_{resume_id}", use_container_width=True):
                            with st.spinner("Generating technical questions..."):
                                questions = test_question_generator(
                                    resume_info["path"], st.session_state.job_requirements)
                                resume_info["questions_text"] = questions
                                st.rerun()

                if resume_info.get("questions_text"):
                    with st.container(border=True):
                        st.markdown("### 📘 Technical Assessment Questions")
                        st.markdown(resume_info["questions_text"])

                        edited = st.text_area("Edit questions if needed:",
                                              value=resume_info["questions_text"],
                                              height=300,
                                              key=f"edited_questions_{resume_id}")
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            if st.button("💾 Apply Question Edits", key=f"apply_questions_{resume_id}", use_container_width=True):
                                resume_info["questions_text"] = edited
                                st.success(
                                    "✅ Questions updated successfully!")

                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("📧 Send Selection Email", key=f"send_selection_email_{resume_id}", use_container_width=True):
                        with st.spinner("Sending email..."):
                            sent = send_email_to_candidate(
                                result_dict.get("name", "Candidate"),
                                result_dict.get("email", ""),
                                hr_decision,
                                # hr_feedback,
                                resume_info.get("questions_text")
                            )
                            if sent:
                                resume_info["email_sent"] = True
                                st.success("✅ Email sent successfully!")
                            else:
                                st.warning(
                                    "⚠️ Failed to send email. Check your credentials.")
            else:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("📧 Send Rejection Email", key=f"send_rejection_email_{resume_id}", use_container_width=True):
                        with st.spinner("Sending email..."):
                            sent = send_email_to_candidate(
                                result_dict.get("name", "Candidate"),
                                result_dict.get("email", ""),
                                hr_decision,
                                # hr_feedback
                            )
                            if sent:
                                resume_info["email_sent"] = True
                                st.info("❌ Rejection email sent.")
                            else:
                                st.warning(
                                    "⚠️ Failed to send rejection email.")


def render_resume_results():
    st.header("Resume Analysis")
    st.text("")

    # Check if any resumes are analyzed
    analyzed_resumes = {
        rid: info for rid, info in st.session_state.resumes.items() if info["analyzed"]}

    if not analyzed_resumes:
        unanalyzed_count = len(st.session_state.resumes)
        if unanalyzed_count > 0:
            st.warning(f"⚠️ You have {unanalyzed_count} resumes that need to be analyzed!")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(f"🧠 Analyze All Resumes ({unanalyzed_count})", key="analyze_all_results", use_container_width=True):
                    progress_bar = st.progress(0)
                    to_analyze = [
                        rid for rid, info in st.session_state.resumes.items() if not info["analyzed"]]
                    total = len(to_analyze)

                    for i, resume_id in enumerate(to_analyze):
                        with st.spinner(f"Analyzing {st.session_state.resumes[resume_id]['name']}..."):
                            analyze_resume(resume_id)
                        progress_bar.progress((i + 1) / total)

                    st.success(f"✅ Successfully analyzed {total} resumes!")
                    st.session_state.show_all_analyzed = True
                    st.rerun()
        else:
            st.warning("⚠️ No resumes have been uploaded yet! Go to Home tab to upload resumes.")
        return

    # Summary stats (KPIs)
    total_resumes = len(st.session_state.resumes)
    analyzed_count = len(analyzed_resumes)
    selected_count = sum(1 for info in analyzed_resumes.values(
    ) if info["result"].get("selection_decision", "").lower() == "selected")

    # Display metrics with full st.metric parameters
    cols = st.columns(3)
    cols[0].metric(
        label="Total Resumes", 
        value=total_resumes, 
        delta=None, 
        delta_color="normal", 
        help="Total number of resumes uploaded", 
        label_visibility="visible", 
        border=True
    )
    cols[1].metric(
        label="Analyzed", 
        value=analyzed_count, 
        delta=None, 
        delta_color="normal", 
        help="Number of resumes that have been analyzed", 
        label_visibility="visible", 
        border=True
    )
    cols[2].metric(
        label="Selected Candidates", 
        value=selected_count, 
        delta=None, 
        delta_color="normal", 
        help="Number of candidates selected for next steps", 
        label_visibility="visible", 
        border=True
    )
    st.text("")

    # --- Resume Comparison Table ---
    st.subheader("Resume Comparison Table")
    st.text("")

    # Prepare data for table
    table_data = []
    for rid, info in analyzed_resumes.items():
        result = info["result"]
        score = result.get("resume_score", 0)
        selection_decision = result.get("selection_decision", "Rejected")
        match_text, match_color = get_match_status(score, selection_decision)
        
        table_data.append({
            "ID": rid,
            "Name": result.get("name", "N/A"),
            "Email": result.get("email", "N/A"),
            "Score": f"{score}/100",
            "Match": match_text,
            "Match_Color": match_color,
            "Decision": selection_decision,
        })

    # Create DataFrame
    df = pd.DataFrame(table_data)
    
    # Display table with View Details button for each row
    for _, row in df.iterrows():
        rid = row["ID"]
        info = analyzed_resumes[rid]
        result = info["result"]
        score = result.get("resume_score", 0)
        selection_decision = result.get("selection_decision", "Rejected")
        match_text, match_color = get_match_status(score, selection_decision)
        
        with st.container(border=True):
            cols = st.columns([2, 2, 1, 1, 2])
            
            cols[0].write(f"**{result.get('name', 'N/A')}**")
            cols[1].write(result.get('email', 'N/A'))
            
            cols[2].markdown(f"<span style='color: {match_color};'>{match_text}</span>", unsafe_allow_html=True)
            
            cols[3].write(f"Score: {score}/100")
            
            if cols[4].button("View Full Details", key=f"view_{rid}"):
                st.session_state.selected_resume_id = rid
                st.rerun()
    
    # Display selected resume details if available
    if st.session_state.selected_resume_id:
        with st.container(border=True):
            st.subheader("Detailed Resume Analysis")
            
            # Add a back button
            if st.button("← Back to Table View"):
                st.session_state.selected_resume_id = None
                st.rerun()
                
            render_resume_details(st.session_state.selected_resume_id)

    # Optional: export CSV
    st.markdown("---")
    export_df = df[["Name", "Email", "Score", "Match", "Decision"]]
    csv = export_df.to_csv(index=False).encode('utf-8')
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.download_button(
            label="📄 Download Results as CSV",
            data=csv,
            file_name="resume_results.csv",
            mime="text/csv",
            use_container_width=True
        )


if __name__ == "__main__":
    main()