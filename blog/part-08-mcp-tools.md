> 📁 **Source Code**: [Google ADK Cookbook](https://github.com/pranavdhopey/ADK-Agent-Basics.git)  
> 📖 **Full Series Index**: [Blog Directory](README.md)

---

# Part 8: Model Context Protocol (MCP) Tools - Connecting to External Services

📁 **Code**: [GitHub Repository](https://github.com/pranavdhopey/ADK-Agent-Basics.git)

> **TL;DR**: Learn how to connect your ADK agents to external Model Context Protocol (MCP) servers using `McpToolset` and `StreamableHTTPConnectionParams`. We'll build an agent that connects to the remote GitHub MCP server to interact with repositories, issues, and pull requests.

---

## What is Model Context Protocol (MCP)?

Up until now, we've given our agents capabilities by either:
1. Using built-in tools (like `google_search`).
2. Writing custom Python functions and wrapping them as `FunctionTool`.

But what if a service already provides an open, standard interface containing dozens of tools?
This is what **Model Context Protocol (MCP)** is for. MCP is an open standard that allows developers to build secure, protocol-based servers that expose data and tools. By using MCP, your agents can connect to external services without needing you to write custom integration wrapper code for each tool.

Google ADK supports MCP out of the box through `McpToolset`. It supports standard transport types, including Stdio (local process) and HTTP/SSE (remote servers).

## Connecting to a Remote MCP Server

Let's say we want our agent to have full access to GitHub. Instead of writing custom python functions for searching issues, listing files, creating PRs, and getting commits, we can connect our agent directly to the official **GitHub MCP Server** using streamable HTTP transport (`StreamableHTTPConnectionParams`).

Here is the agent configuration code:

```python
import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

# Load environment variables
load_dotenv()

github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN") or os.getenv("GITHUB_TOKEN")
mcp_url = os.getenv("GITHUB_MCP_URL", "https://api.githubcopilot.com/mcp/")

# Define the remote HTTP MCP server connection
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
```

## How It Works Under the Hood

When you add `github_mcp_toolset` to your agent's tools:

1. **Lazy Connection**: The toolset doesn't connect to the server immediately.
2. **Tool Discovery**: When the runner starts the agent session, the ADK MCP client connects to `https://api.githubcopilot.com/mcp/` and calls `list_tools` to dynamically discover the tools available on the server.
3. **Dynamic Registration**: The tools are translated and registered as native ADK tools on the agent.
4. **Proxy Calls**: When the agent calls a tool, the request is marshalled and sent to the remote MCP server over HTTP. The server executes it (calling the GitHub API) and returns the output to the agent.

## Setup Requirements

1. **Configure API Keys & Token**:
   Add your keys to your `.env` file:
   ```env
   # Google GenAI Authentication
   GOOGLE_API_KEY=your_gemini_api_key_here

   # GitHub Personal Access Token (PAT)
   GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token_here

   # Remote MCP Endpoint
   GITHUB_MCP_URL=https://api.githubcopilot.com/mcp/
   ```

2. **Run the Agent**:
   ```bash
   adk run mcp_agent
   ```

---

## What I Learned about MCP Integration

1. **Zero Integration Code**: Instead of writing 20 Python functions for 20 GitHub actions, we just point the agent to the MCP endpoint, and ADK registers all tools automatically.
2. **Standardized Protocols**: The agent calls `list_pull_requests` or `get_commits` just like standard Python functions.
3. **Remote Execution**: Using the remote HTTP/SSE transport means you don't need a local Docker container or node process running on your machine.

---

*End of Series*

---

## Quick Reference Card

```python
# Basic Agent
Agent(name, model, instruction, description)

# Agent with Tools
Agent(..., tools=[google_search])

# Agent with Structured Output

---

<div align="between">
  <span>[← Previous: Part 7: Multi-Provider Support - Using LiteLLM with Google ADK](part-07-litellm-multi-provider.md)</span> | <span>[Next: Callbacks Deep Dive Part 1 →](callbacks-part-1-agent-lifecycle.md)</span>
</div>
