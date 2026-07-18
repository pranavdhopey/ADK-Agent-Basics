import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

# Load environment variables (e.g. GITHUB_PERSONAL_ACCESS_TOKEN)
load_dotenv()

github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN") or os.getenv("GITHUB_TOKEN")
mcp_url = os.getenv("GITHUB_MCP_URL", "https://api.githubcopilot.com/mcp/")

github_mcp_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=mcp_url,
        headers={
            "Authorization": f"Bearer {github_token}",
        } if github_token else None,
    )
)

root_agent = Agent(
    model='gemini-2.5-flash',
    name='github_mcp_agent',
    description='An agent that uses the GitHub MCP server to interact with GitHub repositories, issues, and PRs.',
    instruction="""
    You are a helpful assistant with access to the GitHub MCP server tools.

    Your job:
    - Use the provided GitHub tools to interact with repositories, issues, pull requests, commits, and repository files when requested by the user.
    - If the GITHUB_PERSONAL_ACCESS_TOKEN is missing or invalid, politely ask the user to configure it.
    - Summarize the results clearly and concisely.
    """,
    tools=[github_mcp_toolset]
)


