# LiteLLM Agent - Multi-Provider Model Support

## What Does This Agent Do?

This is a **DevOps Assistant** that demonstrates **multi-provider model support** within the Google Agent Development Kit (ADK). While the other agents in this repository use Google's Gemini models, this agent uses **Anthropic Claude Haiku** under the hood via the **LiteLLM** integration.

This agent is configured to:
- Help engineers troubleshoot system errors, stack traces, and application logs
- Recommending cloud infrastructure best practices for GCP, AWS, and Kubernetes
- Generate clean, commented automation scripts (Bash, Python, Terraform)
- Explain complex cloud concepts and DevOps workflows in simple language

It serves as a template for building provider-agnostic agents that can switch models without rewriting the core business logic or agent instructions.

---

## Google ADK Features Used

This agent demonstrates model-provider flexibility in ADK:

### 🤖 Multi-Provider Models via `LiteLlm`

By default, ADK integrates directly with Google's GenAI SDK to call Gemini models. However, by wrapping a model with the `LiteLlm` class from `google.adk.models.lite_llm`, you can swap the backend to any model supported by LiteLLM:

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

The `Agent` constructor accepts:
- **name**: Unique identifier for the agent
- **model**: An instance of `LiteLlm` initialized with your target provider-model string (e.g. `anthropic/...` or `openai/...`)
- **description**: A short description of what the agent does
- **instruction**: Rules, constraints, and personality details for the agent

---

## How It Works

### The Component Stack Flow

Here is the sequential flow of data from the user request down to the model provider:

```
User Request (e.g., "Troubleshoot this crash log...")
          │
          ▼
┌──────────────────────────────────────────────┐
│            Google ADK Agent                  │
│                                              │
│  Maintains session state, invokes templates, │
│  and manages execution.                      │
└─────────────────┬────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────┐
│             LiteLlm Adapter                  │
│                                              │
│  Translates ADK payload format to LiteLLM's  │
│  unified model input interface.              │
└─────────────────┬────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────┐
│             LiteLLM Library                  │
│                                              │
│  Translates inputs and routes the request    │
│  to Anthropic (using ANTHROPIC_API_KEY).     │
└─────────────────┬────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────┐
│            Anthropic API                     │
│                                              │
│  Claude processes request and returns final   │
│  response text back to ADK.                  │
└──────────────────────────────────────────────┘
```

### What's Actually Happening When You Call `.run()`

It's worth understanding the plumbing here, because it explains how ADK stays provider-agnostic:

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

1. **`Agent` stays generic**: It calls `model.generate()` the exact same way regardless of what's inside — it doesn't know or care that it's talking to Claude instead of Gemini.
2. **`LiteLlm` reads the prefix**: The `anthropic/` prefix in `anthropic/claude-haiku-4-5-20251001` tells LiteLLM which provider adapter to use and which environment variable to read.
3. **LiteLLM routes and authenticates**: It resolves the request to Anthropic's API endpoint and reads `ANTHROPIC_API_KEY` from your environment.
4. **The response comes back normalized**: Whatever shape Claude Haiku returns, LiteLLM reshapes it into the unified schema ADK's runner already knows how to parse. 

That normalization step is the entire point of the integration — it's what lets `transfer_to_agent`, tool calls, and structured output all keep working without provider-specific branching in your code.

---

## When to Use This Agent

Perfect for:
- Testing how different LLMs (e.g. Claude vs. Gemini) perform on your specific prompts
- Creating vendor-agnostic systems that can swap providers dynamically
- Leveraging provider-specific model benefits or pricing tiers

Not needed for:
- Standard implementations where Gemini models (`gemini-2.0-flash`) already perform perfectly
- Applications where introducing external dependencies (`litellm`) is restricted

---

## Key ADK Concepts in This Example

| Feature | What It Does | Used In This Agent |
|:---|:---|:---|
| **Agent** | The core AI component | ✅ Yes - `Agent` class |
| **Model (LiteLLM)** | Non-Gemini model provider wrapper | ✅ Yes - `LiteLlm` wrapping Claude |
| **Instruction** | Defines DevOps troubleshooting personality | ✅ Yes - Automation & troubleshooting tone |
| **Description** | Brief summary | ✅ Yes - "A DevOps assistant powered by..." |
| **Name** | Unique identifier | ✅ Yes - `litellm_devops_agent` |

---

## Running the Agent

### 1. Install Dependencies
Ensure you have `lite_llm` support installed alongside Google ADK:

```bash
pip install google-adk litellm
```

### 2. Configure Authentication
Create a `.env` file in this directory and specify your Anthropic API Key:

```env
# Since the agent uses Claude (anthropic/claude-haiku-4-5-20251001)
# we must configure the Anthropic API key.
# For other providers, use standard LiteLLM environment keys (e.g., OPENAI_API_KEY)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 3. Execution
Use the ADK CLI to run the agent interactively:

```bash
adk run litellm_agent
```

---

## Difference from Other Agents

| Feature | This Agent (LiteLLM) | Standard Agents (e.g., Greeting Agent) |
|:---|:---|:---|
| **Model Provider** | Multi-Provider (Anthropic Claude) | Google Gemini |
| **Model Class** | `LiteLlm` model adapter | Built-in Gemini model support |
| **Setup Complexity** | Requires `litellm` package & provider API keys | Out-of-the-box support with Gemini API keys |
| **Vendor Portability** | High (can easily swap to OpenAI, Cohere, etc.) | High compatibility within Google Vertex/AI Studio |

---

## Code Structure

```
litellm_agent/
├── agent.py          # DevOps agent using LiteLlm Claude model
├── __init__.py       # Package initialization
├── .env              # Environment config containing ANTHROPIC_API_KEY
└── README.md         # This file
```

---

## Official Documentation

| Feature / Tool | Documentation Link |
|:---|:---|
| **Google ADK Models** | [ADK Models Guide](https://google.github.io/adk-docs/agents/models/) |
| **LiteLLM Models** | [LiteLLM Model Providers](https://docs.litellm.ai/docs/providers) |
| **Anthropic Models** | [Anthropic Claude Models Documentation](https://docs.anthropic.com/en/docs/about-claude/models) |

---

## What You'll Learn

By studying this agent, you'll understand:
1. **How to initialize multi-provider models** using ADK's `LiteLlm` class
2. **How to configure third-party environment variables** (e.g. `ANTHROPIC_API_KEY`) for LiteLLM routing
3. **How to swap model layers** seamlessly while preserving the instructions and core agent structures

---

**Pro Tip**: LiteLLM supports over 100+ model providers. If you want to use OpenAI's GPT models instead, simply swap the string to `openai/gpt-4o` and set the `OPENAI_API_KEY` in your `.env` file. The agent will run exactly the same way without requiring any changes to `agent.py`!
