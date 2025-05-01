# agents.py
# Contains agent definitions and initialization functions

import streamlit as st
from agno.agent import Agent
from agno.models.azure import AzureOpenAI
from agno.tools.duckduckgo import DuckDuckGoTools
from textwrap import dedent

@st.cache_resource
def initialize_single_agent():
    """
    Initialize the single research agent
    
    Returns:
        Agent: Configured research agent or None if error
    """
    try:
        agent = Agent(
            model=AzureOpenAI(
                azure_deployment="gpt-4o-mini",
                api_version="2024-02-15-preview",
            ),
            tools=[DuckDuckGoTools()],
            show_tool_calls=True,
            description="You are a deep researcher which gives detailed responses on the research topics provided.",
            instructions="""You are a research assistant that can perform deep web research on any topic.
            When given a research topic or question:
            1. Use the duckduckgo tool to gather comprehensive information
            2. The tool will search the web, analyze multiple sources, and provide a synthesis
            3. Review the research results and organize them into a well-structured report
            4. Include proper citations for all sources
            5. Highlight key findings and insights
            6. Ensure all URLs cited are working and accessible
            7. Provide clickable links for all sources
            8. The final Response must not be less than 1000 words.
            """,
            markdown=True
        )
        return agent
    except Exception as e:
        st.error(f"Error initializing agent: {str(e)}")
        return None

@st.cache_resource
def initialize_research_team():
    """
    Initialize the multi-agent research team
    
    Returns:
        Agent: Configured research team agent or None if error
    """
    try:
        # Research planner
        research_planner = Agent(
            name="Research Planner",
            role="Breaks research queries into structured subtopics and assigns relevant sources",
            instructions="""
            - Decompose research queries into well-structured subtopics covering all relevant angles
            - Ensure logical flow and coverage of historical, current, and future perspectives
            - Identify and recommend the most credible sources for each subtopic.
            - Prioritize primary research, expert opinions, and authoritative publications
            - Generate a detailed research roadmap specifying:
                1. Subtopics with clear focus areas.
                2. Recommended sources (websites, papers, reports).
                3. Suggested research methodologies (quantitative, qualitative, case studies).
            """,
            model=AzureOpenAI(
                azure_deployment="gpt-4o-mini",
                api_version="2024-02-15-preview",
            ),
            tools=[DuckDuckGoTools()],
            show_tool_calls=True,
            markdown=True
        )

        # Research Agent
        research_agent = Agent(
            name='Research Agent',
            tools=[DuckDuckGoTools()],
            model=AzureOpenAI(
                azure_deployment="gpt-4o-mini",
                api_version="2024-02-15-preview",
            ),
            description="An expert researcher conducting deep web searches and verifying sources",
            instructions="""
            - Go through the research plan
            - Perform relevant websearches based on the planned topics ad resources
            - Prioritize recent and authoritative sources.
            - Identify key stakeholders and perspectives
            - Ensure all URLs cited are working and accessible with 200 status codes
            - Provide all sources with proper formatted hyperlinks
            """,
            expected_output="""
            # Research Summary Report
            
            ## Topic: [Research Topic]
            
            ### Key Findings
            - **Finding 1:** [Detailed explanation with supporting data]
            - **Finding 2:** [Detailed explanation with supporting data]
            - **Finding 3:** [Detailed explanation with supporting data]
            
            ### Source-Based Insights
            #### Source 1: [Source Name / URL]
            - **Summary:** [Concise summary of key points]
            - **Relevant Data:** [Key statistics, dates, or figures]
            - **Notable Quotes:** [Direct citations from experts, if available]
            
            #### Source 2: [Source Name / URL]
            - **Summary:** [Concise summary of key points]
            - **Relevant Data:** [Key statistics, dates, or figures]
            - **Notable Quotes:** [Direct citations from experts, if available]
            
            (...repeat for all sources...)
            
            ### Overall Trends & Patterns
            - **Consensus among sources:** [Common viewpoints and recurring themes]
            - **Diverging Opinions:** [Conflicting perspectives and debates]
            - **Emerging Trends:** [New insights, innovations, or potential shifts]
            
            ### Citations & References
            - [[Source 1 Name]]([URL])
            - [[Source 2 Name]]([URL])
            - [...list all sources with links...]
            
            ---
            
            Research conducted by AI Investigative Journalist
            Compiled on: [current_date] at [current_time]
            """,
            show_tool_calls=True,
            add_datetime_to_instructions=True,
        )

        # Analysis Agent
        analysis_agent = Agent(
            name="Analysis Agent",
            tools=[DuckDuckGoTools()],
            model=AzureOpenAI(
                azure_deployment="gpt-4o-mini",
                api_version="2024-02-15-preview",
            ),
            description="A data analyst identifying trends, evaluating viewpoints, and synthesizing information",
            instructions=dedent("""
            - Analyze collected research for patterns, trends, and conflicting viewpoints.
            - Evaluate the credibility of sources and filter out misinformation.
            - Summarize findings with statistical and contextual backing.
            - Verify all URLs are accessible and valid.
            - Format all sources as clickable Markdown links.
            """),
            expected_output=dedent("""A critical analysis report in detail with all the identified patterns, trends, and insights supported by evidence. The report should evaluate source credibility and highlight any conflicting information found during research."""),
            show_tool_calls=True
        )

        # Writing Agent
        writing_agent = Agent(
            name='Writing Agent',
            model=AzureOpenAI(
                azure_deployment="gpt-4o-mini",
                api_version="2024-02-15-preview",
            ),
            tools=[DuckDuckGoTools()],
            description="A professional journalist specializing in NYT-style reporting and feature writing",
            instructions=dedent("""
            Report Structure 📝
            - Create an engaging academic title
            - Write a compelling abstract
            - Present methodology clearly
            - Discuss findings systematically
            - Draw evidence-based conclusions
            - Maintain journalistic integrity, objectivity, and balance.
            - Use clear, engaging language and provide necessary background.
            - Use proper citations for each source 
            - Format all references as proper Markdown links
            - Ensure all URLs cited are working and accessible
            """),
            markdown=True,
            show_tool_calls=True,
            add_datetime_to_instructions=True
        )

        # Research Team
        research_team = Agent(
            model=AzureOpenAI(
                azure_deployment="gpt-4o-mini",
                api_version="2024-02-15-preview",
            ),
            name="Research Team",
            description="A team coordinator conducting investigative reporting collaboratively",
            role="Executes a structured research workflow",
            team=[research_planner, research_agent, analysis_agent, writing_agent],
            tools=[DuckDuckGoTools()],
            instructions=dedent("""
            - Establish a workflow for executing a structured research operation.
            - Assign tasks to each agent sequentially.
            - Ensure that the output from one agent flows into the next.
            - Finally Produce a well-researched, structured final report based on the findings.
            - All Sections must contain citations 
            - Ensure all URLs cited are working and accessible
            - Format all references as proper clickable Markdown links (not full link just the header) 
            -  The final Response must not be less than 1000 words.
            """),
            expected_output=dedent("""
            ## Summary
            (Compelling headline)
            (Concise overview of key findings and significance)
            
            ## Background & Context
            (Historical context and importance)
            (Current landscape overview)
            
            ## Key Findings
            (Main discoveries and analysis with citations and links)
            (Expert insights and quotes with citations and links)
            (Statistical evidence with links)
            
            ## Impact Analysis
            (Broader implications)
            (Stakeholder perspectives)
            (Industry/societal effects)
            
            ## Future Directions
            (Emerging trends)
            (Expert predictions)
            (Potential challenges and opportunities)
            
            ## Expert Insights
            (Notable quotes and analysis from industry leaders)
            (Contrasting viewpoints)
            
            ## Sources & Methodology
            (List of primary sources with the links)
            (Research methodology overview)
            
            Compiled by ResearchGPT
            Published: [current_date]
            Last Updated: [current_time]
            """),
            markdown=True,
            show_tool_calls=True,
            add_datetime_to_instructions=True
        )
        
        return research_team
    except Exception as e:
        st.error(f"Error initializing research team: {str(e)}")
        return None

