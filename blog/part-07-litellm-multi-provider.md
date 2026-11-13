> 📁 **Source Code**: [Google ADK Cookbook](https://github.com/pranavdhopey/ADK-Agent-Basics.git)  
> 📖 **Full Series Index**: [Blog Directory](README.md)

---

# Part 7: Multi-Provider Support - Using LiteLLM with Google ADK

📁 **Code**: [GitHub Repository](https://github.com/pranavdhopey/ADK-Agent-Basics.git)

> **TL;DR**: Learn how to use non-Gemini models (like Anthropic Claude or OpenAI GPT) in your Google ADK agents using the LiteLLM integration. We'll build an agent that uses Claude Haiku under the hood.

---

## Why Use Other Model Providers?

While Google's Gemini models are fantastic, fast, and cost-effective, real-world applications sometimes require testing or utilizing models from other providers (like Anthropic's Claude or OpenAI's GPT-4) for comparison, specialized capabilities, or vendor neutrality.

Google ADK supports this natively through its **LiteLLM integration**. LiteLLM acts as a unified translation layer, letting you invoke hundreds of different LLMs using the exact same ADK agent patterns.

## The LiteLlm Class

To use another provider, you import `LiteLlm` from `google.adk.models.lite_llm` and pass it to the agent's `model` parameter.

Here is the code for our LiteLLM agent:

```python
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

root_agent = Agent(
    name="litellm_devops_agent",
    model=LiteLlm(model="anthropic/claude-haiku-4-5-20251001"),
    description="A DevOps assistant powered by Anthropic Claude (via LiteLLM) that helps troubleshoot systems and write automation scripts",
    instruction="""
    You are a DevOps Assistant powered by Anthropic Claude (via LiteLLM).

    Your job:
    - Help engineers troubleshoot system errors, logs, and stack traces
    - Recommend cloud infrastructure best practices for GCP, AWS, and Kubernetes
    - Generate clean, commented automation scripts (Bash, Python, Terraform, etc.)
    - Explain complex DevOps workflows in simple, clear language

    Always keep responses structured, professional, and technically accurate.
    """
)
```

## How It Works Under the Hood

To understand how Google ADK integrates with other model providers, it's helpful to look at the component stack:

```
User Request
     │
     ▼
┌─────────────────────────┐
│     Google ADK Agent    │  <-- Maintains session state, templates, and orchestration
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│     LiteLlm Adapter     │  <-- ADK's internal wrapper class
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│     LiteLLM Library     │  <-- Underlying Python library handling model translation
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│      Anthropic API      │  <-- Processed by Claude Haiku using ANTHROPIC_API_KEY
└─────────────────────────┘
```

Here's the plumbing behind every `.run()` call:

```
  ┌────────────────┐       ┌───────────┐       ┌─────────────────┐
  │   ADK Runner   │ ────> │  LiteLlm  │ ────> │ Provider Router │
  │  (your agent)  │       │  wrapper  │       │ (LiteLLM core)  │
  └────────────────┘       └───────────┘       └────────┬────────┘
                                                        │ reads "anthropic/..." prefix
                                                        │ picks up ANTHROPIC_API_KEY
                                                        ▼
                                               ┌─────────────────┐
                                               │  Anthropic API  │
                                               │  (Claude Haiku) │
                                               └─────────────────┘
```

1. **The Agent stays generic**: It calls `model.generate()` the exact same way regardless of what's inside — it doesn't know or care that it's talking to Claude instead of Gemini.
2. **LiteLLM reads the prefix**: The `anthropic/` in `anthropic/claude-haiku-4-5-20251001` tells LiteLLM which provider adapter to use and which environment variable to read.
3. **LiteLLM routes and authenticates**: It resolves the request to Anthropic's API endpoint and reads `ANTHROPIC_API_KEY` from your environment.
4. **The response comes back normalized**: Whatever shape Claude Haiku returns, LiteLLM reshapes it into the format ADK's runner already knows how to parse. This normalization step is crucial because it ensures that features like tool calls, routing, and structured schemas continue working without any model-specific logic in your agent code!


## Setup Requirements

To run this agent:

1. **Install LiteLLM**:
   ```bash
   pip install litellm
   ```
2. **Configure API Keys**:
   Add your provider's API key to your `.env` file:
   ```env
   ANTHROPIC_API_KEY=your-actual-anthropic-key
   ```

---

## What I Learned about LiteLLM Integration

1. **Seamless Swap**: All of your existing ADK patterns (like `SequentialAgent`, `ParallelAgent`, and tools) still work perfectly. ADK abstracts the model calls entirely.
2. **API Keys naming**: LiteLLM standardizes on standard provider key names like `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` rather than ADK specific ones.
3. **Model Strings**: Ensure you use the exact LiteLLM model prefixes (e.g., `anthropic/...` or `openai/...`) so LiteLLM knows where to route the request.

---

## Final Thoughts

We've come full circle! From simple "hello world" agents in Part 1 to sophisticated systems that can:
- Remember user context (Part 2)
- Run complex workflows (Part 3)
- Route requests dynamically (Part 4)
- Orchestrate specialists as tools (Part 5)
- Execute real infrastructure commands (Part 6)
- Run non-Gemini models via LiteLLM (Part 7)
- Connect to remote servers via Model Context Protocol (Part 8)

The patterns build on each other. Once you understand the fundamentals, you can combine them in countless ways.

Now go build your own AI agent systems! Whether it's a DevOps assistant, a research bot, or something entirely new - you have all the tools you need.

Happy coding! 🚀

---

---

<div align="between">
  <span>[← Previous: Part 6: FunctionTool - Giving Agents Real Power](part-06-function-tool.md)</span> | <span>[Next: Part 8: Model Context Protocol (MCP) Tools - Connecting to External Services →](part-08-mcp-tools.md)</span>
</div>
