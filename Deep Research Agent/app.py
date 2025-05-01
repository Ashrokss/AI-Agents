# app.py
# Main Streamlit application file

import streamlit as st
import os
import datetime
import time
from dotenv import load_dotenv

# Import from local modules
from style import CSS
from utils import get_image_base64
from agents import initialize_single_agent, initialize_research_team
from animation import show_research_pipeline

# Load environment variables
load_dotenv()

# Ensure Azure OpenAI environment variables are set
os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_OPENAI_ENDPOINT")

# Configure page settings
st.set_page_config(
    page_title="ResearchGPT | AI-Powered Research Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply CSS styling
st.markdown(CSS, unsafe_allow_html=True)

# Load the robot image once
robot_image_path = r"C:\Users\admin\Desktop\Deep Research\icons\ai research bot.png"
robot_image_base64 = get_image_base64(robot_image_path)

# Initialize session state for storing research history
if 'research_history' not in st.session_state:
    st.session_state.research_history = []

# Main content area
st.markdown('<h1 class="main-header">ResearchGPT</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-Powered Deep Research Assistant</p>', unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.markdown("### About")
    st.markdown("""
    ResearchGPT is an AI-powered research assistant that provides in-depth information on any topic using Azure OpenAI integration with web search capabilities.
    
    **Built with:**
    - Streamlit
    - Azure OpenAI
    - Agno Framework
    """)
    
    st.markdown("### Research Mode")
    research_mode = st.radio(
        "Select Research Mode:",
        ["Standard (Single Agent)", "Advanced (Multi-Agent Team)"],
        index=1
    )

# Create a two-column layout
col1, col2 = st.columns([2, 1])

with col1:
    # Main input area
    with st.container():
        st.markdown("### Research Topic")
        query = st.text_area("Enter your research question or topic:", 
                          height=100, 
                          placeholder="E.g., What are the latest developments in quantum computing?")
        
        col_btn1, col_space = st.columns([1, 3])
        with col_btn1:
            search_button = st.button("🔍 Research", use_container_width=True)

with col2:
    # Research history section
    st.markdown("### Recent Searches")
    if not st.session_state.research_history:
        st.info("Your research history will appear here")
    else:
        for i, item in enumerate(st.session_state.research_history[-5:]):
            with st.container():
                st.markdown(f"""
                <div class="history-item" onclick="document.getElementById('research-input').value='{item['query']}'">
                    <strong>{item['query'][:40]}{'...' if len(item['query']) > 40 else ''}</strong><br>
                    <small>{item['date']}</small>
                </div>
                """, unsafe_allow_html=True)

# Main research execution
if search_button and query:
    # Get appropriate agent based on selected mode
    if research_mode == "Standard (Single Agent)":
        agent = initialize_single_agent()
    else:  # Advanced (Multi-Agent Team)
        agent = initialize_research_team()
        show_research_pipeline()
    
    if agent:
        with st.container():
            st.markdown("### Research Results")
            with st.expander("Research details", expanded=True):
                st.info(f"Researching: '{query}'")
                
                try:
                    # Record start time
                    start_time = time.time()
                    
                    # Run the agent with the query
                    with st.spinner("Research Team Lead Finalizing research..."):
                        response = agent.run(query)
                        stream = True
                        if stream:
                            response_stream = agent.run(query, stream=True)
                            response_text = ""
                            report_placeholder = st.empty()

                            for chunk in response_stream:
                                response_text += chunk.content
                                report_placeholder.markdown(response_text + "▌")

                            report_placeholder.markdown(response_text)
                    
                    # Record end time and calculate duration
                    duration = round(time.time() - start_time, 2)
                    
                    # Save to history
                    st.session_state.research_history.append({
                        "query": query,
                        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "duration": duration,
                        "mode": research_mode
                    })
                    
                    # Show success message
                    st.success(f"Research completed in {duration} seconds using {research_mode} mode")
                    
                    # Display results
                    # with st.container():
                    #     st.markdown(response.content)
                    
                    # Generate file for download
                    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_name = f"research_{current_time}.md"
                    
                    # Add metadata to the markdown content
                    markdown_content = f"""# Research: {query}
                    
Date: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Mode: {research_mode}
Duration: {duration} seconds

---


                    """
                    
                    # Download option
                    st.download_button(
                        label="📥 Download Research",
                        data=markdown_content,
                        file_name=file_name,
                        mime="text/markdown"
                    )
                    
                except Exception as e:
                    st.error(f"Error during research: {str(e)}")
                    st.warning("An error occurred while performing the research. Please try again.")
    else:
        st.warning("Could not initialize the research agent. Please check your environment configuration.")
else:
    # Show placeholder or example when no search is performed
    if not search_button:
        with st.container():
            st.markdown("### How It Works")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### 🔍 Deep Research")
                st.markdown("Searches multiple sources on the web to gather comprehensive information")
            
            with col2:
                st.markdown("#### 🧠 AI Analysis")
                st.markdown("Analyzes and synthesizes information to create a coherent research report")
            
            with col3:
                st.markdown("#### 📊 Structured Results")
                st.markdown("Presents findings in a well-organized format with proper citations")
                
            st.markdown("---")
            
            # Example topics
            st.markdown("### Try researching these topics:")
            example_topics = [
                "The impact of artificial intelligence on healthcare",
                "Current developments in renewable energy technology",
                "Effects of climate change on biodiversity",
                "Latest advancements in quantum computing"
            ]

            # Display topics as normal text instead of buttons
            for topic in example_topics:
                st.markdown(f"• {topic}")

# Footer
st.markdown("---")

# Run the app
if __name__ == "__main__":
    pass  # Streamlit automatically runs the script