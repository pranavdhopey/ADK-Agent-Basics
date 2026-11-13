> 📁 **Source Code**: [Google ADK Cookbook](https://github.com/pranavdhopey/ADK-Agent-Basics.git)  
> 📖 **Full Series Index**: [Blog Directory](README.md)

---

# Part 1: The Basics - Your First AI Agents

📁 **Code**: [GitHub Repository](https://github.com/pranavdhopey/ADK-Agent-Basics.git)

> **TL;DR**: Learn what AI agents are, set up Google ADK, and build 3 agents - a Greeting Agent (basic), Search Agent (with tools), and Multi-tool Agent. You'll understand the `Agent` class, `instruction`, `tools`, and `model` parameters.

---

## What Even Is an AI Agent?

Before we write any code, let's clear up what we're building.

An **AI Agent** is basically an AI that can do things, not just chat. Think about it:
- A regular chatbot: You ask "What's the weather?", it says "I don't know, I'm just an AI"
- An AI Agent: You ask "What's the weather?", it actually *searches* the web and tells you

The difference? **Tools and actions**. An agent can use tools, make decisions, and take actions. It's like upgrading from a parrot (repeats information) to an assistant (actually helps you do stuff).

## Setting Up Google ADK

First things first. You'll need to install the ADK:

```bash
pip install google-adk
```

And set up your API key (I use a `.env` file):

```
GOOGLE_API_KEY=your_api_key_here
```

Now let's build our first agent!

---

## Agent 1: The Greeting Agent - Hello, World! (But Make It AI)

Every programming journey starts with "Hello World," right? Ours is no different. But instead of `print("Hello World")`, we're building an AI that actually greets people like a friendly human would.

### The Scenario

Imagine you're building a chatbot for your company's website. The first thing it needs to do is greet visitors warmly. Not a boring "Hello, how can I help you?" - but something with personality!

### The Code

Here's my first agent - I call it the Greeting Agent:

```python
from google.adk.agents import Agent

root_agent = Agent(
    name="greeting_agent",
    model="gemini-2.0-flash",
    description="A casual and funny agent that greets the user",
    instruction="""
    You are a friendly, casual, and slightly funny assistant.

    Your job:
    - Greet the user in a relaxed and cheerful way
    - Lightly joke, but stay professional
    - Ask for the user's name if you don't know it
    - Keep messages short and natural

    Avoid sarcasm or offensive humor.
    """
)
```

That's it. Seriously. Let me break down what each piece does:

| Parameter | What It Does | My Example |
|-----------|--------------|------------|
| `name` | Unique identifier for your agent | `"greeting_agent"` |
| `model` | Which AI model to use | `"gemini-2.0-flash"` (fast and cheap!) |
| `description` | Brief summary (for you and other agents) | `"A casual and funny agent..."` |
| `instruction` | The personality and behavior guide | The whole instruction block |

### What I Learned

The **instruction** is where the magic happens. It's like writing a job description for your AI. The more specific you are, the better your agent behaves.

My first version just said "be friendly." The result? Generic, boring responses. When I added specific guidance like "lightly joke" and "ask for their name," suddenly the agent had personality!

**Pro tip I discovered:** Use bullet points in your instructions. The AI follows structured instructions way better than long paragraphs.

### Try It Out

When you run this agent and say "Hello!", you might get something like:

```
You: Hello!
Agent: Hey there! Great to see a friendly face around here. I'm your
       neighborhood AI assistant - part helpful, part caffeinated.
       What's your name? I promise I'll try to remember it!
```

See how it's not just "Hello, how can I help you?" It has personality! That's the power of good instructions.

---

## Agent 2: The Google Search Agent - Teaching Your AI to Use the Internet

Okay, so our greeting agent is nice, but it's kind of... limited. It can only answer based on what it already knows. What if someone asks "What's the latest news on AI?"

This is where **Tools** come in. And trust me, this was my first "WHOA" moment with ADK.

### The Scenario

You want an assistant that can actually search the internet to answer questions. Not just guess based on training data - actually look stuff up in real-time.

### The Code

```python
from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="search_agent",
    model="gemini-2.0-flash",
    description="An agent that searches the web to answer questions",
    tools=[google_search],  # THIS IS THE MAGIC LINE
    instruction="""
    You are a helpful assistant with access to Google Search.

    Your job:
    - Use google_search when the user asks for factual or up-to-date information
    - Summarize the search results in simple language
    - If search is not required, answer directly

    Always cite your sources when using search.
    """
)
```

### The "Tools" Concept - My Aha Moment

See that `tools=[google_search]` line? That one line transforms your agent from a "knows stuff from training" AI to a "can look stuff up" AI.

Here's how I think about it:

**Without tools:**
```
User: What's the weather in Tokyo right now?
Agent: I'm sorry, I don't have access to real-time weather data.
```

**With tools:**
```
User: What's the weather in Tokyo right now?
Agent: *uses google_search tool*
Agent: It's currently 15°C and sunny in Tokyo! Perfect weather
       for cherry blossom viewing.
```

The agent **decides** when to use the tool. You don't have to tell it "search for this." It reads the question, thinks "hmm, this needs current info," and uses the search tool automatically.

### What Tools Are Available?

ADK comes with some built-in tools:
- `google_search` - Search the web
- Code execution tools
- File operation tools
- And you can build your own!

### What I Learned

The instruction matters even more when you have tools. You need to tell the agent:
1. **When** to use the tool (for up-to-date information)
2. **How** to use results (summarize in simple language)
3. **What else** to do (cite sources)

Without clear instructions, my agent was searching for EVERYTHING, even simple questions like "What is 2+2?" Waste of time and API calls!

---

## Agent 3: The Incident Analysis Agent - Getting Structured Output

This one changed how I think about AI agents. Up until now, our agents return free-form text. But what if you need structured data? Like a JSON report that you can actually use in your code?

### The Scenario

You're building an on-call incident management system. When someone reports a problem like "The database is down!", you need:
- A summary
- Severity level (critical, high, medium, low)
- Affected components
- Recommended actions

And you need this in a consistent format every time, not random text.

### The Code

```python
from google.adk.agents import Agent
from pydantic import BaseModel, Field
from typing import List

# Define the structure you want
class IncidentReport(BaseModel):
    incident_summary: str = Field(description="Brief summary of the incident")
    severity: str = Field(description="low, medium, high, or critical")
    affected_components: List[str] = Field(description="Systems affected")
    probable_cause: str = Field(description="Most likely root cause")
    immediate_actions: List[str] = Field(description="Recommended steps")

# Create the agent with output_schema
root_agent = Agent(
    name="incident_analysis_agent",
    model="gemini-2.0-flash",
    description="Analyzes technical incidents and provides structured reports",
    output_schema=IncidentReport,  # THE MAGIC!
    instruction="""
    You are an Incident Analysis Assistant.

    Analyze the user's incident description and provide:
    1. A concise summary
    2. Severity level: critical, high, medium, or low
    3. List of affected components/systems
    4. Most probable root cause
    5. Immediate actions to take

    Be specific and actionable in your recommendations.
    """
)
```

### The "output_schema" Concept - Game Changer!

Before I discovered `output_schema`, I was doing this:

```python
# Bad approach - parsing text manually
response = agent.run("Database is down!")
# Response: "Well, this seems like a critical issue affecting the database..."
# Now I have to somehow extract severity, components, etc. from text 😫
```

With `output_schema`:

```python
# Good approach - structured output
response = agent.run("Database is down!")
# Response is automatically a structured object!
print(response.severity)  # "critical"
print(response.affected_components)  # ["Database", "Backend API", "User Authentication"]
print(response.immediate_actions)  # ["Check database logs", "Verify connections", ...]
```

**No parsing! No regex! No hoping the AI formats things correctly!**

### Example Output

Input:
```
"GKE pods are in CrashLoopBackOff state. Application logs show
'cannot connect to database' errors."
```

Output (structured JSON):
```json
{
  "incident_summary": "GKE pods failing to start due to database connectivity issues",
  "severity": "critical",
  "affected_components": [
    "GKE pods",
    "Database connection",
    "Application service"
  ],
  "probable_cause": "Database service unavailable or network connectivity issue between GKE and database",
  "immediate_actions": [
    "Verify database service is running",
    "Check Kubernetes secrets for database credentials",
    "Verify network policies and firewall rules",
    "Review recent configuration changes"
  ]
}
```

### What I Learned

**Pydantic is your friend!** The `BaseModel` class lets you define exactly what structure you want:
- Field names (`incident_summary`, `severity`, etc.)
- Field types (`str`, `List[str]`, etc.)
- Field descriptions (helps the AI understand what each field should contain)

The descriptions in `Field(description="...")` are actually important! They guide the AI on what content goes where.

---

## Recap: What We've Built So Far

Let's step back and see what we learned:

| Agent | ADK Feature | What It Does |
|-------|-------------|--------------|
| Greeting Agent | `instruction` | Defines personality and behavior |
| Google Search Agent | `tools` | Gives agent external capabilities |
| Incident Analysis Agent | `output_schema` | Forces structured JSON output |

These three concepts - **instructions**, **tools**, and **structured output** - are the foundation of everything else we'll build.

### The Pattern I Noticed

Every agent follows the same basic pattern:

```python
from google.adk.agents import Agent

agent = Agent(
    name="unique_name",           # Identify your agent
    model="gemini-2.0-flash",     # Pick your brain
    description="What it does",    # Brief summary
    instruction="How to behave",   # Personality and rules
    tools=[...],                   # Optional: External capabilities
    output_schema=MyModel,         # Optional: Structured output
)
```

Once you understand this pattern, building new agents becomes almost like filling out a form!

---

## What's Next?

In **Part 2**, we'll level up with **State Management**. Our greeting agent right now forgets your name immediately after you tell it. Rude, right? We'll fix that by teaching our agents to remember things across conversations.

We'll build a **Stateful Greeting Agent** that:
- Asks your name once
- Remembers it forever (well, for the session)
- Greets you by name every time

This involves some new concepts:
- Session services
- State variables
- Runners

It's where things start to feel like building a real application!

---

## Quick Reference

Here's a cheat sheet of what we covered:

```python
# Basic Agent (Greeting)
Agent(
    name="greeting_agent",
    model="gemini-2.0-flash",
    instruction="Be friendly and casual"
)

# Agent with Tools (Search)
Agent(
    name="search_agent",
    tools=[google_search],
    instruction="Search when needed"
)

# Agent with Structured Output (Incident Analysis)
Agent(
    name="incident_agent",
    output_schema=IncidentReport,
    instruction="Analyze and categorize"
)
```

---

## Try It Yourself!

Before moving to Part 2, try building:
1. A **joke agent** - Uses the greeting pattern but tells dad jokes
2. A **news agent** - Uses google_search to fetch and summarize news
3. A **bug report agent** - Uses output_schema to structure bug reports

The best way to learn is by building. Trust me, I wrote probably 10 broken agents before these examples worked!

---

*Continue to Part 2: State Management - Teaching Your Agent to Remember →*

---

---

<div align="between">
  <span>[← Series Home](README.md)</span> | <span>[Next: Part 2: State Management - Teaching Your Agent to Remember →](part-02-state-management.md)</span>
</div>
