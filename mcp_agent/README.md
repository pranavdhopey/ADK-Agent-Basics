# GitHub MCP Agent

## What Does This Agent Do?

This agent is a helpful assistant that can **interact with GitHub repositories** using the GitHub Model Context Protocol (MCP) server. When you ask questions or issue instructions related to repositories, files, commits, issues, or pull requests, it uses remote MCP tools to query the GitHub API and execute actions.

It demonstrates the **MCP Tools** integration capability of the Google Agent Development Kit (ADK).

## Google ADK Features Used

This agent demonstrates the **McpToolset** feature of the Google Agent Development Kit (ADK). Here's what that means:

### 🛠️ McpToolset
An `McpToolset` is a bridge that connects your ADK agent to an external Model Context Protocol (MCP) server. In this example, it connects to the GitHub MCP server using streamable HTTP transport (`StreamableHTTPConnectionParams`).

Without MCP tools, the agent cannot access external services like GitHub. **With the GitHub MCP server toolset**, this agent can:
- List, view, and search files inside GitHub repositories
- View commits, branches, and repository metadata
- List, create, and update GitHub issues and pull requests
- Query pull request reviews and repository actions

### How MCP Tools Work

```python
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

github_mcp_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://api.githubcopilot.com/mcp/",
        headers={
            "Authorization": f"Bearer {github_token}",
        } if github_token else None,
    )
)

agent = Agent(
    name="github_mcp_agent",
    model="gemini-2.5-flash",
    tools=[github_mcp_toolset]  # ← The agent now has GitHub capabilities!
)
```

The agent automatically discovers and calls tools provided by the GitHub MCP server over the network.

## When to Use This Agent

This agent is perfect for questions like:
- "Can you list the active issues in my repo?"
- "What files were changed in the latest commit?"
- "Create a new pull request to merge feature-branch into main"
- "Search for references to a specific function in my repository"

## How It Works

1. **You ask a question**: "What are the latest pull requests in my repository?"
2. **Agent decides**: "I should list the active pull requests. Let's call the `list_pull_requests` tool."
3. **Agent calls the tool**: Invokes the remote MCP tool over HTTP via `McpToolset`.
4. **Agent gets results**: Receives the list of PRs from the GitHub MCP server.
5. **Agent responds**: Summarizes the pull requests for the user.

## Key ADK Concepts in This Example

| Feature | What It Does | Used In This Agent |
|---------|-------------|-------------------|
| **Agent** | The core AI component that processes requests | ✅ Yes - `Agent` class |
| **McpToolset** | Connects to external MCP servers to load tools | ✅ Yes - `McpToolset` class |
| **Connection Params** | Configures transport details for the MCP server | ✅ Yes - `StreamableHTTPConnectionParams` |
| **Model** | The AI model powering the agent | ✅ Yes - `gemini-2.5-flash` |
| **Instruction** | Guides the agent on how to behave | ✅ Yes - Instructs how to use GitHub tools |

## Running the Agent

To run this agent, configure your environment variables first by updating `.env`:

```env
# Google GenAI Authentication
GOOGLE_API_KEY=your_gemini_api_key_here

# GitHub Token (Used as Bearer Authorization header for the HTTP MCP request)
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_personal_access_token_here

# MCP Connection Settings
GITHUB_MCP_URL=https://api.githubcopilot.com/mcp/
```

Then run the agent using the ADK CLI:

```bash
adk run mcp_agent
```

Or start the ADK Web UI:

```bash
adk web
```

## Code Structure

```
mcp_agent/
├── agent.py          # Main agent definition with McpToolset
├── __init__.py       # Package initialization
├── .env              # Environment variables (API keys, etc.)
└── README.md         # This file
```

## Official Documentation

Learn more about the ADK features used in this agent:

| Feature | Documentation Link |
|---------|-------------------|
| **MCP Tools Integration** | [ADK MCP Tools Guide](https://google.github.io/adk-docs/tools-custom/mcp-tools/) |
| **LLM Agents** | [LLM Agents Documentation](https://google.github.io/adk-docs/agents/llm-agents/) |
| **Official GitHub MCP Server** | [GitHub MCP Server Repository](https://github.com/github/github-mcp-server) |
