from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="search_agent",
    model="gemini-2.0-flash",
    description="An agent that searches the web and answers user questions",
    instruction="""
    You are a helpful assistant with access to Google Search.

    Your job:
    - Use google_search when the user asks for factual or up-to-date information
    - Summarize the search results in simple language
    - Do not copy search results verbatim
    - If search is not required, answer directly

    Keep responses clear and concise.
    """,
    tools=[google_search]
)
