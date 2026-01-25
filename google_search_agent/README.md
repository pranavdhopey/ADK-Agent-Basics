# Google Search Agent

## What Does This Agent Do?

This agent is a helpful assistant that can **search the web** to answer your questions. When you ask something that requires up-to-date or factual information, it automatically searches Google and then summarizes the results in clear, simple language.

Think of it as having a research assistant that:
- Listens to your question
- Searches Google if needed
- Reads the search results
- Gives you a concise answer

## Google ADK Features Used

This agent demonstrates the **Tools** feature of the Google Agent Development Kit (ADK). Here's what that means:

### 🛠️ Tools
"Tools" are special abilities you can give to your agent. In this case, the agent has access to the `google_search` tool, which allows it to search the web in real-time.

Without tools, an AI agent can only answer based on what it already knows. **With the `google_search` tool**, this agent can:
- Look up current events
- Find factual information
- Get the latest data
- Research topics beyond its training data

### How Tools Work

```python
from google.adk.tools import google_search

agent = Agent(
    name="search_agent",
    model="gemini-2.0-flash",
    tools=[google_search]  # ← The agent now has search capability!
)
```

When you give an agent a tool, it learns when and how to use it. The agent's **instruction** guides it on when to search:

```python
instruction="""
You are a helpful assistant with access to Google Search.

Your job:
- Use google_search when the user asks for factual or up-to-date information
- Summarize the search results in simple language
- If search is not required, answer directly
"""
```

## When to Use This Agent

This agent is perfect for questions like:
- "What's the current weather in Tokyo?"
- "Who won the latest Formula 1 race?"
- "What are the top rated restaurants in Paris?"
- "Latest news about renewable energy"

This agent is NOT needed for:
- General knowledge questions (e.g., "What is Python?")
- Math calculations
- Code generation
- Creative writing

## How It Works

1. **You ask a question**: "What's the latest version of Python?"
2. **Agent decides**: "This requires up-to-date info, I should search"
3. **Agent calls the tool**: Uses `google_search` to find current information
4. **Agent gets results**: Receives search results from Google
5. **Agent responds**: Summarizes the findings in simple language

## Key ADK Concepts in This Example

| Feature | What It Does | Used In This Agent |
|---------|-------------|-------------------|
| **Agent** | The core AI component that processes requests | ✅ Yes - `Agent` class |
| **Tools** | External capabilities the agent can use | ✅ Yes - `google_search` |
| **Model** | The AI model powering the agent | ✅ Yes - `gemini-2.0-flash` |
| **Instruction** | Guides the agent on how to behave | ✅ Yes - Tells when to search |
| **Description** | Brief summary of agent's purpose | ✅ Yes - "An agent that searches the web..." |

## Running the Agent

To use this agent, you would typically:

```python
from google_search_agent import root_agent

# The agent is ready to answer questions with web search capability
response = root_agent.run("What's the latest news on AI?")
print(response)
```

## Code Structure

```
google_search_agent/
├── agent.py          # Main agent definition with google_search tool
├── __init__.py       # Package initialization
├── .env              # Environment variables (API keys, etc.)
└── README.md         # This file
```

## Learn More

- **ADK Tools Documentation**: Learn about other built-in tools like code execution, file operations, and more
- **Custom Tools**: You can create your own tools to give agents custom capabilities
- **Tool Selection**: Agents automatically decide when to use tools based on your instruction

---

**Beginner Tip**: The "tools" feature is one of the most powerful aspects of ADK. It transforms your agent from a simple chatbot into an assistant that can take actions and access real-time information!
