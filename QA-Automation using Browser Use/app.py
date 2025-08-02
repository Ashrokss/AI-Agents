# Streamlit App: Multi-Agent QA with Browser Agent for Execution
import os
import json
import time
import ast
import sys
import atexit
import asyncio
import warnings
import pandas as pd
import streamlit as st

from style import CSS
from config import Config
from prompts import AgentPrompts
from browser_use import Controller
from openai import AsyncAzureOpenAI
from agents.mcp import MCPServerStdio
from langchain_openai import AzureChatOpenAI
from streamlit_option_menu import option_menu
from browser_use import Agent as BrowserAgent
from models import FRDModel, TestExecutionResults,CriticEvaluationResults
from agents import Agent, Runner, set_default_openai_client, OpenAIChatCompletionsModel, set_tracing_disabled



if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

warnings.filterwarnings("ignore", category=ResourceWarning)

def silence_stderr_on_exit():
    sys.stderr = open(os.devnull, 'w')


atexit.register(silence_stderr_on_exit)

AZURE_OPENAI_API_KEY = Config.AZURE_OPENAI_API_KEY
AZURE_OPENAI_ENDPOINT = Config.AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_CHAT_DEPLOYMENT = Config.AZURE_OPENAI_CHAT_DEPLOYMENT
AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL = Config.AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL
AZURE_OPENAI_API_VERSION = Config.AZURE_OPENAI_API_VERSION

st.set_page_config(
    page_title="Automation QA Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown(CSS, unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🤖 Automation QA Agent</h1>
    <p>AI-powered web application testing with Browser automation</p>
</div>
""", unsafe_allow_html=True)

# Option Menu
with st.sidebar:
    selected = option_menu(
        menu_title="",
        options=["Home","QA Automation", "FRD Generation","Feedback Analysis"],
        icons=["house","bug", "file-text","book"],
        menu_icon="gear",
        default_index=0,
        orientation="vertical",
    )
if selected == "Home":
    with st.container(border=True,height=210):
        body = """
            This is a Streamlit-based web application that leverages large language models and browser automation to:

            * Perform Quality Assurance Testing for a given Application.
            * Generate **Functional Requirement Documents (FRDs)** from GitHub repositories.
            * Automatically generate **test plans and test cases** from functional requirements.
            * Execute tests in a real browser using an intelligent **Browser Agent**.
            * Display test plans, test cases, and execution results in a clean UI.
        """
        st.markdown(body=body)


if selected == "QA Automation":
    st.title("🔍 QA Automation System")
    with st.container(height=280):
        body = """
            
            * Input URL of the application to be tested.
            * Upload a `.txt` file containing functional requirements.

            * The system reads the requirements and:
                * Generates a test plan and test cases in markdown table format.
                * Produces detailed, structured test cases.
                * Executes test cases using a browser agent powered by LangChain + Azure OpenAI + `browser_use`.
                * Displays results with pass/fail status, description
        """
        st.markdown(body=body)
    url = st.text_input("Enter web application URL:")
    uploaded_file = st.file_uploader(
        "Upload Functional Requirements (.txt)", type=["txt"])

    if st.button("Run QA Automation") and url and uploaded_file:
        start_time = time.time()
        os.makedirs("fs_files", exist_ok=True)

        with open("fs_files/FRD_requirements.txt", "w", encoding="utf-8") as f:
            f.write(uploaded_file.read().decode("utf-8"))

        client = AsyncAzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_version=AZURE_OPENAI_API_VERSION
        )
        set_default_openai_client(client)
        set_tracing_disabled(disabled=True)

        controller = Controller(output_model=TestExecutionResults)

        async def run_agents(url):
            with open("fs_files/FRD_requirements.txt", "r", encoding="utf-8") as f:
                frd_content = f.read()

            async with MCPServerStdio(
                name="Filesystem Server",
                params={"command": "npx", "args": [
                    "-y", "@modelcontextprotocol/server-filesystem", "fs_files"]},
                cache_tools_list=True
            ) as file_server:
                tools = await file_server.list_tools()
                file_tools = [tool.name for tool in tools]

                st.info("🤖 Agent 1: Creating test plans and test cases...")

                agent1 = Agent(
                    name="Test Plan Generator",
                    instructions=AgentPrompts.agent_1_instructions(
                        file_tools, frd_content, url),
                    mcp_servers=[file_server],
                    model=OpenAIChatCompletionsModel(
                        model=AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL,
                        openai_client=client
                    )
                )
                await Runner.run(
                    starting_agent=agent1,
                    input=f"Generate test plan and test cases for {url} and save in fs_files.",
                    max_turns=30
                )

                st.info("🧠 Browser Agent: Executing test cases...")
                llm = AzureChatOpenAI(
                    model=Config.AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL,
                    api_version=Config.AZURE_OPENAI_API_VERSION,
                    azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
                    api_key=Config.AZURE_OPENAI_API_KEY,
                )

                with open("fs_files/test_cases.md", "r", encoding="utf-8") as f:
                    test_cases_content = f.read()

                with open("fs_files/test_plan.md", "r", encoding="utf-8") as f:
                    test_plan_content = f.read()

                task_prompt, message_context = AgentPrompts.browser_test_execution_prompt(
                    url, test_plan_content, test_cases_content
                )

                browser_agent = BrowserAgent(
                    task=task_prompt,
                    llm=llm,
                    message_context=message_context,
                    controller=controller)
                result = await browser_agent.run(max_steps=100)

                with open("fs_files/test_execution_results.json", "w", encoding="utf-8") as out:
                    out.write(str(result.final_result()))

        st.info("🚀 Running agents...")
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures

            def run_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                return new_loop.run_until_complete(run_agents(url))

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_thread)
                future.result()

        except RuntimeError:
            asyncio.run(run_agents(url))

        st.success("✅ QA Automation Completed!")

        end_time = time.time()
        elapsed_time = end_time - start_time

        minutes, seconds = divmod(elapsed_time, 60)
        st.info(
            f"⏱️ Total Execution Time: {int(minutes)} minutes and {seconds:.2f} seconds")

        st.subheader("📝 Test Plan")
        if os.path.exists("fs_files/test_plan.md"):
            with open("fs_files/test_plan.md", "r", encoding="utf-8") as f:
                st.markdown(f.read())

        st.subheader("🎯 Test Cases ")
        if os.path.exists("fs_files/test_cases.md"):
            with open("fs_files/test_cases.md", "r", encoding="utf-8") as f:
                st.markdown(f.read())

        st.subheader("🎯 Test Execution Results")
        if os.path.exists("fs_files/test_execution_results.json"):
            with st.expander("Test Execution Result"):
                with open("fs_files/test_execution_results.json", "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        results = data.get("results", [])
                        print(results)

                        if isinstance(results, list):
                            df = pd.DataFrame(results)
                            st.dataframe(df)
                        else:
                            st.warning("Expected 'results' to be a list.")
                    except json.JSONDecodeError as e:
                        st.error(f"Failed to parse JSON: {e}")

elif selected == "FRD Generation":
    st.title("📄 FRD Generation System")
    with st.container(height=240):
        body = """
            * Input a GitHub repository URL.
            * The system analyzes the source code and automatically generates a full FRD including:
                * Purpose
                * Functional overview
                * Functional and non-functional requirements
                * Error handling
                * Sample use cases
        """
        st.markdown(body=body)

    github_url = st.text_input("Enter GitHub URL:")

    if st.button("Generate FRD") and github_url:
        start_time = time.time()

        os.makedirs("fs_files", exist_ok=True)

        llm = AzureChatOpenAI(
            model=Config.AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            api_key=Config.AZURE_OPENAI_API_KEY,
        )

        controller = Controller(output_model=FRDModel)

        async def generate_frd(github_url):
            task_prompt, message_context = AgentPrompts.frd_generation_prompt(
                github_url)

            agent = BrowserAgent(
                task=task_prompt,
                message_context=message_context,
                llm=llm,
                controller=controller
            )
            result = await agent.run(max_steps=100)
            return result.final_result()

        st.info("🚀 Generating FRD...")

        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures

            def run_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                return new_loop.run_until_complete(generate_frd(github_url))

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_thread)
                result = future.result()

        except RuntimeError:
            result = asyncio.run(generate_frd(github_url))

        # Process the result
        try:
            result = ast.literal_eval(result) if isinstance(
                result, str) else result

            # Save JSON output
            with open("fs_files/frd_output.json", "w",errors="ignore") as outfile:
                json.dump(result, outfile, indent=2)

            # Save formatted text file
            with open("fs_files/FRD_generated.txt", "w",errors="ignore") as f:
                f.write("APP NAME:\n")
                for name in result["app_name"]:
                    f.write(f"- {name}\n")

                f.write("\nPURPOSE:\n")
                for purpose in result["purpose"]:
                    f.write(f"- {purpose}\n")

                f.write("\nFUNCTIONAL OVERVIEW:\n")
                for item in result["functional_overview"]:
                    f.write(f"- {item['description']}\n")

                f.write("\nFUNCTIONAL REQUIREMENTS:\n")
                for fr in result["functional_requirements"]:
                    f.write(f"{fr['id']}: {fr['description']}\n")

                f.write("\nERROR HANDLING REQUIREMENTS:\n")
                for err in result["error_handling_requirements"]:
                    f.write(f"{err['id']}: {err['description']}\n")

                f.write("\nNON-FUNCTIONAL REQUIREMENTS:\n")
                for nfr in result["non_functional_requirements"]:
                    f.write(f"{nfr['id']}: {nfr['description']}\n")

                f.write("\nUSE CASES:\n")
                for uc in result["use_cases"]:
                    f.write(f"{uc['id']}: {uc['description']}\n")

            end_time = time.time()
            elapsed_time = end_time - start_time

            minutes, seconds = divmod(elapsed_time, 60)
            st.info(
                f"⏱️ Total Execution Time: {int(minutes)} minutes and {seconds:.2f} seconds")

            # Display the generated FRD
            st.subheader("📄 Generated Functional Requirements Document")

            if os.path.exists("fs_files/FRD_generated.txt"):
                with open("fs_files/FRD_generated.txt", "r", encoding="utf-8", errors="ignore") as f:
                    frd_content = f.read()
                    st.text_area("FRD Content", frd_content, height=600)
                app_name = result['app_name']
                # Download button for the FRD
                st.download_button(
                    label="📥 Download FRD",
                    data=frd_content,
                    file_name=f"FRD_generated_{app_name}.txt",
                    mime="text/plain"
                )

            # Show JSON data in expander
            with st.expander("📊 Structured FRD Data (JSON)"):
                st.json(result)

        except Exception as e:
            st.error(f"Error processing FRD result: {str(e)}")
            st.error("Raw result:")
            st.code(str(result))

elif selected == "Feedback Analysis":
    st.title("📄 Feedback Generation System")
    with st.container(height=240):
        body = """
            * Input the App URL.
            * The system analyzes the application against FRD provided and generates :
                * FR-ID
                * Requirement Summary 
                * Fullfillment  of the requirement
                * Critique
                * Suggestions (If needed)
        """
        st.markdown(body=body)

    url = st.text_input("Enter Application URL:")
    uploaded_file = st.file_uploader(
        "Upload Functional Requirements (.txt)", type=["txt"])

    if st.button("Run QA Automation") and url and uploaded_file:
        start_time = time.time()
        os.makedirs("fs_files", exist_ok=True)

        with open("fs_files/FRD_requirements.txt", "w", encoding="utf-8") as f:
            f.write(uploaded_file.read().decode("utf-8"))

        with open("fs_files/FRD_requirements.txt", "r", encoding="utf-8") as f:
                frd_content = f.read()

        llm = AzureChatOpenAI(
            model=Config.AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            api_key=Config.AZURE_OPENAI_API_KEY,
        )

        controller = Controller(output_model=CriticEvaluationResults)

        async def generate_feedback(url):
            task_prompt, message_context = AgentPrompts.critic_agent_prompt(
                url,frd_content)

            agent = BrowserAgent(
                task=task_prompt,
                message_context=message_context,
                llm=llm,
                controller=controller
            )
            result = await agent.run(max_steps=100)
            return result.final_result()

        st.info("🚀 Generating Feedback...")

        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures

            def run_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                return new_loop.run_until_complete(generate_feedback(url))

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_thread)
                result = future.result()

        except RuntimeError:
            result = asyncio.run(generate_feedback(url))

        # Process the result
        result = ast.literal_eval(result) if isinstance(
            result, str) else result

        with open("fs_files/critique_output.json", "w") as outfile:
            json.dump(result, outfile, indent=2)

        with open("fs_files/critic_results.txt", "w", encoding="utf-8") as f:
            f.write("Functional Requirement Evaluation\n\n")
            for item in result["results"]:
                f.write(f"FR ID: {item['FR_id']}\n")
                f.write(f"Requirement: {item['requirement_summary']}\n")
                f.write(f"Fulfillment: {item['fulfillment']}\n")
                f.write(f"Critique: {item['critique']}\n")
                f.write(f"Suggestions: {item['suggestions'] or 'None'}\n")
                f.write("\n")

        end_time = time.time()
        minutes, seconds = divmod(end_time - start_time, 60)
        st.info(f"⏱️ Total Execution Time: {int(minutes)} minutes and {seconds:.2f} seconds")

        st.subheader("📋 Critic Agent Feedback Summary")
        if os.path.exists("fs_files/critic_results.txt"):
            with open("critic_results.txt", "r", encoding="utf-8",errors="ignore") as f:
                feedback_text = f.read()
                st.text_area("Feedback Output", feedback_text, height=600)

            st.download_button(
                label="📥 Download Feedback Report",
                data=feedback_text,
                file_name="critic_results.txt",
                mime="text/plain"
            )

        # Optional: Show raw JSON output too
        with st.expander("📊 Structured Feedback (JSON)"):
            st.json(result)
  