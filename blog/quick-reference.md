> 📖 **Series Index**: [Blog Directory](README.md)

---

Agent(..., output_schema=MyPydanticModel)

# Agent that Stores Output
Agent(..., output_key="my_output")

# Sequential Workflow
SequentialAgent(name, sub_agents=[a, b, c])

# Parallel Workflow
ParallelAgent(name, sub_agents=[a, b, c])

# Loop Workflow
LoopAgent(name, sub_agents=[a, b], max_iterations=5)

# Router Pattern (sub_agents - control transfers)
Agent(
    name="router",
    sub_agents=[specialist_a, specialist_b],
    instruction="Route based on keywords..."
)

# Terminal Agent (no transfers back)
Agent(
    ...,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)

# AgentTool Pattern (main agent stays in control)
from google.adk.tools import AgentTool

specialist = Agent(name="specialist", output_key="result", ...)
specialist_tool = AgentTool(agent=specialist)

main_agent = Agent(
    name="main",
    tools=[specialist_tool],
    instruction="Use specialist for specific tasks..."
)

# FunctionTool Pattern (execute real code)
from google.adk.tools import FunctionTool

def my_function(param: str) -> dict:
    """Description for LLM. Use when user wants X."""
    # Real code execution here
    return {"result": "data"}

agent = Agent(
    name="runtime_agent",
    tools=[FunctionTool(func=my_function)],
    instruction="Use my_function to do X..."
)

# State Variable Reference
instruction="Use the value from {previous_output_key}"

# Custom Exit Tool for Loops
def exit_loop(tool_context: ToolContext):
    tool_context.actions.escalate = True
    return {"status": "done"}

# LiteLLM Integration (Multi-Provider Models)
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents import Agent
Agent(model=LiteLlm(model="anthropic/claude-haiku-4-5-20251001"), name="litellm_devops_agent", ...)

# MCP Tools Integration (Remote HTTP)
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams
github_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://api.githubcopilot.com/mcp/",
        headers={"Authorization": f"Bearer {github_token}"}
    )
)
Agent(tools=[github_toolset], ...)
```

---

## Resources

- Google ADK Documentation
- Pydantic for Structured Output
- Python AsyncIO for Runners

---

*Thanks for reading! Connect with me if you build something cool with ADK!*