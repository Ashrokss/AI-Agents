from agno.agent import Agent
from agno.models.azure import AzureOpenAI
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools

import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("AZURE_OPENAI_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

agent = Agent(
    name="Finance Agent",
    model=AzureOpenAI(
        id="gpt-4o-mini",
        api_key=api_key,
        azure_endpoint=azure_endpoint
    ),
    tools=[DuckDuckGoTools(), YFinanceTools(
        stock_price=True, analyst_recommendations=True, stock_fundamentals=True)],
    markdown=True,
    show_tool_calls=True,
    description="You are an investment analyst that researches stock prices, analyst recommendations, and stock fundamentals.",
    instructions=[
        "Format your response using markdown and use tables to display data where possible.Also provide relevant links to verify the data."],
    add_context=True,
    add_references=True,
    )

agent.print_response("Compare nvidia and apple stocks ", markdown=True,stream=True)
