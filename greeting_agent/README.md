# Greeting Agent

## What Does This Agent Do?

This is a friendly, casual AI assistant that specializes in greeting users. It responds to your "hello" or "hi" with warmth, humor, and a personal touch.

Think of it as your cheerful virtual assistant who:
- Greets you in a relaxed and friendly manner
- Adds light jokes to make conversations fun (but keeps it professional)
- Asks for your name if it doesn't know it
- Uses your name in future greetings once you share it
- Keeps responses short and natural

## Google ADK Features Used

This agent demonstrates the fundamental building blocks of the Google Agent Development Kit (ADK):

### 🤖 Agent
The core component of ADK - the **Agent** class. This is the foundation of any AI assistant you build with ADK.

```python
from google.adk.agents import Agent

root_agent = Agent(
    name="greeting_agent",
    model="gemini-2.0-flash",
    description="A casual and funny agent that greets the user",
    instruction="..."
)
```

An Agent needs:
- **name**: Unique identifier for the agent
- **model**: Which AI model to use (here: `gemini-2.0-flash`)
- **description**: Brief summary of what the agent does
- **instruction**: Detailed guide on how the agent should behave

### 📝 Instruction
The **instruction** is like a job description for your AI agent. It defines personality, behavior, and rules:

```python
instruction="""
You are a friendly, casual, and slightly funny assistant.

Your job:
- Greet the user in a relaxed and cheerful way
- Lightly joke, but stay professional
- Ask for the user's name if you don't know it
- Keep messages short and natural

Avoid sarcasm or offensive humor.
"""
```

The instruction shapes:
- **Tone**: Friendly and casual
- **Behavior**: Asks for names, uses light humor
- **Boundaries**: No sarcasm, no offensive content
- **Style**: Short and natural responses

### 🧠 Model
This agent uses **gemini-2.0-flash**, which is:
- Fast and efficient
- Good for conversational tasks
- Cost-effective for simple interactions like greetings

## How It Works

Here's what happens when you interact with this agent:

```
You: "Hello!"
    ↓
Agent receives message
    ↓
Agent follows instruction (be friendly, casual, funny)
    ↓
Agent: "Hey there! 👋 Great to see you! I'm your friendly greeting bot.
       What's your name?"
    ↓
You: "I'm Sarah"
    ↓
Agent remembers context from conversation
    ↓
Agent: "Nice to meet you, Sarah! How can I brighten your day?"
```

## When to Use This Agent

Perfect for:
- Building a welcoming chatbot for your app
- Learning the basics of ADK agent creation
- Understanding how instructions shape agent behavior
- Testing conversational AI with simple use cases

Not needed for:
- Complex multi-step tasks
- Technical problem-solving
- Data analysis or processing

## Key ADK Concepts in This Example

| Feature | What It Does | Used In This Agent |
|---------|-------------|-------------------|
| **Agent** | The core AI component | ✅ Yes - `Agent` class |
| **Model** | The AI model powering responses | ✅ Yes - `gemini-2.0-flash` |
| **Instruction** | Defines behavior and personality | ✅ Yes - Friendly greeting style |
| **Description** | Brief summary of agent purpose | ✅ Yes - "A casual and funny agent..." |
| **Name** | Unique identifier | ✅ Yes - `greeting_agent` |

## Running the Agent

To use this agent in your code:

```python
from greeting_agent import root_agent

# Start a conversation
response = root_agent.run("Hello!")
print(response)
```

The agent will greet you based on its instruction and maintain a friendly, casual tone throughout the conversation.

## Difference from Multi-Agent Greeting Agent

If you've seen the greeting agent in the `multi_agent/sub_agents/` folder, here's how they differ:

| Feature | This Agent (Standalone) | Multi-Agent Version |
|---------|------------------------|---------------------|
| **Purpose** | Works independently | Part of a router system |
| **Transfer Control** | None | Has `disallow_transfer_to_parent/peers` |
| **Use Case** | Simple greeting bot | Specialized greeter in larger system |
| **Complexity** | Beginner-friendly | Intermediate (multi-agent concepts) |

This standalone version is **simpler** and great for learning ADK basics. The multi-agent version demonstrates advanced routing and agent coordination.

## Code Structure

```
greeting_agent/
├── agent.py          # Main agent definition
├── __init__.py       # Package initialization
├── .env              # Environment variables (API keys, etc.)
└── README.md         # This file
```

## Official Documentation

Learn more about the ADK features used in this agent:

| Feature | Documentation Link |
|---------|-------------------|
| **Getting Started** | [ADK Quickstart Guide](https://google.github.io/adk-docs/get-started/quickstart/) |
| **LLM Agents** | [LLM Agents Documentation](https://google.github.io/adk-docs/agents/llm-agents/) |
| **Agent Configuration** | [Agent Config Reference](https://google.github.io/adk-docs/agents/config/) |
| **Models (Gemini)** | [Google Gemini Models](https://google.github.io/adk-docs/agents/models/google-gemini/) |

## What You'll Learn

By studying this agent, you'll understand:
1. **How to create a basic ADK agent** - The Agent class and required parameters
2. **How instructions work** - Shaping AI behavior with natural language
3. **Model selection** - Choosing the right AI model for your task
4. **Personality design** - Making your agent friendly, professional, or formal

---

**Beginner Tip**: This is one of the simplest agents you can build with ADK. It's a perfect starting point! The key takeaway: **Instructions are powerful** - they let you define your agent's personality and behavior using plain English.
