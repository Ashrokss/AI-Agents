# app/main.py
from typing import Iterator
import streamlit as st
from textwrap import dedent
import os
from agno.agent import Agent, RunResponse
from agno.models.azure import AzureOpenAI
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools

# --------- LOAD API KEY ---------
api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
if not api_key:
    st.error("AzureOpenAI API key not found. Please set the key environment variable.")
    st.stop()

# --------------- TITLE AND INFO SECTION -------------------
st.title("📈 Financial Analyst Team")
st.write("Your AI-powered market research squad with real-time data and news analysis")

# --------------- AGENT TEAM INITIALIZATION -------------------


def create_agent_team():
    # Web Research Agent
    web_agent = Agent(
        name="Web Agent",
        role="Financial news researcher",
        model=AzureOpenAI(
             id="gpt-4o-mini",
            api_key=api_key,
            azure_endpoint=azure_endpoint
        ),
        tools=[DuckDuckGoTools()],
        instructions=dedent("""\
            You are an experienced web researcher and news analyst! 🔍

            Follow these steps when searching for information:
            1. Start with the most recent and relevant sources
            2. Cross-reference information from multiple sources
            3. Prioritize reputable news outlets and official sources
            4. Always cite your sources with links
            5. Focus on market-moving news and significant developments

            Your style guide:
            - Present information in a clear, journalistic style
            - Use bullet points for key takeaways
            - Include relevant quotes when available
            - Specify the date and time for each piece of news
            - Highlight market sentiment and industry trends
            - End with a brief analysis of the overall narrative
            - Pay special attention to regulatory news, earnings reports, and strategic announcements\
        """),
        show_tool_calls=True,
        markdown=True,
        add_references=True,
        debug_mode=True,
    )

    # Financial Data Agent
    finance_agent = Agent(
        name="Finance Agent",
        role="Market data analyst",
        model=AzureOpenAI(
            id="gpt-4o-mini",
            api_key=api_key,
            azure_endpoint=azure_endpoint
        ),
        tools=[YFinanceTools(
            stock_price=True, analyst_recommendations=True, company_info=True)],
        instructions=dedent("""\
            You are a skilled financial analyst with expertise in market data! 📊

            Follow these steps when analyzing financial data:
            1. Start with the latest stock price, trading volume, and daily range
            2. Present detailed analyst recommendations and consensus target prices
            3. Include key metrics: P/E ratio, market cap, 52-week range
            4. Analyze trading patterns and volume trends
            5. Compare performance against relevant sector indices

            Your style guide:
            - Use tables for structured data presentation
            - Include clear headers for each data section
            - Add brief explanations for technical terms
            - Highlight notable changes with emojis (📈 📉)
            - Use bullet points for quick insights
            - Compare current values with historical averages
            - End with a data-driven financial outlook\
        """),
        show_tool_calls=True,
        markdown=True,
        add_references=True,
        debug_mode=True,
    )

    # Lead Editor Agent
    return Agent(
        team=[web_agent, finance_agent],
        model=AzureOpenAI(
            id="gpt-4o-mini",
            api_key=api_key,
            azure_endpoint=azure_endpoint
        ),
        instructions=dedent("""\
            You are the lead editor of a prestigious financial news desk! 📰

            Your role:
            1. Coordinate between the web researcher and financial analyst
            2. Combine their findings into a compelling narrative
            3. Ensure all information is properly sourced and verified
            4. Present a balanced view of both news and data
            5. Highlight key risks and opportunities

            Your style guide:
            - Start with an attention-grabbing headline
            - Begin with a powerful executive summary
            - Present financial data first, followed by news context
            - Use clear section breaks between different types of information
            - Include relevant charts or tables when available
            - Add 'Market Sentiment' section with current mood
            - Include a 'Key Takeaways' section at the end
            - End with 'Risk Factors' when appropriate
            - Sign off with 'Market Watch Team' and the current date\
        """),
        add_datetime_to_instructions=True,
        show_tool_calls=True,
        markdown=True,
        add_references=True,
        debug_mode=True,
    )


agent_team = create_agent_team()

# --------------- SIDEBAR CONTROLS -------------------
with st.sidebar:
    st.subheader("Example Queries")
    st.code("""
    AAPL news + financials
    NVDA AI impact analysis
    EV sector: TSLA vs RIVN
    Semiconductor market outlook
    MSFT recent performance
    """)

    st.markdown("---")
    st.subheader("Agent Team Capabilities")
    st.write("🔍 Web Agent: Real-time news analysis")
    st.write("📊 Finance Agent: Market data & metrics")
    st.write("📰 Lead Editor: Integrated reports")

stream = st.sidebar.checkbox("Stream")

# --------------- USER INPUT & DISPLAY -------------------
query = st.text_input(
    "Enter financial query (e.g., 'AAPL news and stock analysis')")

if query:
    with st.spinner("🔍 Assembling market intelligence..."):
        stream = True
        if stream:
            response_stream = agent_team.run(query, stream=True)
            response_text = ""
            report_placeholder = st.empty()

            for chunk in response_stream:
                response_text += chunk.content
                report_placeholder.markdown(response_text + "▌")

            report_placeholder.markdown(response_text)
        else:
            response = agent_team.run(query, stream=False)
            st.markdown(response.content)

# --------------- FOOTER & INFO -------------------
st.markdown("---")
st.caption("""
**Data Sources**: 
- Real-time market data from Yahoo Finance
- News analysis from web sources
- AI-powered insights from GPT-4o
""")
st.caption(
    "Note: Response times vary based on query complexity (typically 15-45 seconds)")
