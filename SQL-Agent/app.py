import streamlit as st
from agno.agent import Agent
from agno.tools.sql import SQLTools
from agno.models.azure import AzureOpenAI
from style import CSS
from config import Config

# Load configuration
mysql_pass = Config.MY_SQL_PASS
db_name = Config.MY_SQL_DATABASE_NAME
api_key = Config.AZURE_OPENAI_API_KEY
azure_endpoint = Config.AZURE_OPENAI_ENDPOINT

# MySQL connection string
db_url = f"mysql://root:{mysql_pass}@localhost:3306/{db_name}"

# Initialize agent
@st.cache_resource
def get_agent():
    return Agent(
        model=AzureOpenAI(
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            id='gpt-4o-mini'  # Update if needed
        ),
        tools=[SQLTools(db_url=db_url)],
        instructions="""You are a sql agent designed to anwer about queries related to your table Do not answer about things that are not in your database."""
    )

agent_team = get_agent()

# Streamlit UI
# Custom CSS for better styling
st.markdown(CSS,unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🛢️ SQL Agent</h1>
    <p>AI-powered web application that helps users ineracting with Database Tables</p>
</div>
""", unsafe_allow_html=True)
# st.title("🛢️SQL Query Agent")
query = st.text_input("Ask a question about your database/tables:")

if query:
    with st.spinner("🔍 Thinking..."):
        # stream = True
        
        # if stream:
        #     response_stream = agent_team.run(query, stream=True)
        #     response_text = ""
        #     report_placeholder = st.empty()

        #     # for chunk in response_stream:
        #     #     response_text += chunk.content
        #     #     report_placeholder.markdown(response_text + "▌")

        #     for chunk in response_stream:
        #         content = getattr(chunk, "content", "")
        #         if content:
        #             response_text += content
        #             report_placeholder.markdown(response_text + "▌")
        #     report_placeholder.markdown(response_text)
            
        
        response = agent_team.run(query, stream=False)
        with st.expander("Tools Execution"):
            st.json(response.tools)
        with st.expander("Tools Called"):
            st.json(response.formatted_tool_calls)
             
        st.markdown(response.content)
    

        
