# My Journey Learning Google ADK: Building AI Agents from Scratch

*A beginner's guide to Google Agent Development Kit - learning by building*

📁 **All Code Examples**: [GitHub Repository](https://github.com/pranavdhopey/ADK-Agent-Basics.git)

---

Hey there, fellow learner!

I'm going to be honest with you - when I first heard about "AI Agents," I thought it was some super complicated stuff that only PhD researchers could understand. But here I am, a few weeks later, building my own AI agents and actually understanding how they work. And if I can do it, trust me, you can too!

This blog series documents my journey learning Google's Agent Development Kit (ADK). I'm not an expert - I'm learning alongside you. Think of this as notes from a fellow student who just happens to be a few chapters ahead. I'll share the mistakes I made, the "aha!" moments I had, and most importantly, the actual code that works.

This is a **6-part series** that will take you from building your first "hello world" agent to creating sophisticated multi-agent systems that can actually execute real infrastructure commands. Each part builds on the previous one, so by the end you'll have a solid understanding of ADK's core concepts - agents, tools, state management, workflows, and more. Whether you're completely new to AI agents or looking to learn Google's ADK specifically, this series has got you covered.

Let's dive in!

---

## Table of Contents

- [Part 1: The Basics](#part-1-the-basics---your-first-ai-agents) - Your first AI agents, tools, and the core Agent class
- [Part 2: State Management](#part-2-state-management---teaching-your-agent-to-remember) - Teaching agents to remember with sessions and runners
- [Part 3: Workflow Agents](#part-3-workflow-agents---building-agent-teams) - Sequential, Parallel, and Loop agent patterns
- [Part 4: Multi-Agent Systems](#part-4-multi-agent-systems---the-router-pattern) - Router pattern with specialist agents
- [Part 5: AgentTool](#part-5-agenttool---turning-agents-into-tools) - Wrapping agents as callable tools
- [Part 6: FunctionTool](#part-6-functiontool---giving-agents-real-power) - Executing real code with Python functions
- [Quick Reference Card](#quick-reference-card) - Cheat sheet for all ADK patterns

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

# Part 2: State Management - Teaching Your Agent to Remember

📁 **Code**: [GitHub Repository](https://github.com/pranavdhopey/ADK-Agent-Basics.git)

> **TL;DR**: Learn how agents can remember context across conversations using `Runner`, `InMemorySessionService`, and `output_key`. Build an Incident Analyzer that stores results in session state.

*Welcome back to the series! If you're joining fresh, I recommend starting with [Part 1](#part-1-the-basics---your-first-ai-agents) where we built our first three agents.*

---

## Reflections on Part 1

Wow, what a journey Part 1 was! We went from "what even is an AI agent?" to building three working agents:
- A **Greeting Agent** that has actual personality
- A **Search Agent** that can browse the internet
- An **Incident Analysis Agent** that returns structured JSON

I was genuinely surprised how quickly things clicked once I understood the basic pattern. The `instruction` → `tools` → `output_schema` trio is powerful!

But here's the thing that started bugging me while testing the greeting agent...

## What We're Building in Part 2

Have you noticed that our greeting agent has the memory of a goldfish? It asks your name, you tell it, and two messages later it's forgotten. Frustrating, right?

In this part, we're going to fix that by learning:
- **State Management** - How to make agents remember things
- **Session Services** - Managing conversations across messages
- **Runners** - The glue that connects agents with sessions

By the end of Part 2, our greeting agent will remember your name for the entire conversation. It's a small feature, but it's what separates a toy demo from a real application.

Let's dive in!

---

## The Problem with Stateless Agents

Remember our friendly greeting agent from Part 1? Let's have a conversation with it:

```
You: Hi there!
Agent: Hey! Great to meet you! What's your name?

You: I'm Alex!
Agent: Nice to meet you, Alex! How can I help?

You: What's my name?
Agent: I'm not sure, could you tell me?
```

Wait, what?! It just asked my name and immediately forgot it! That's like talking to someone with amnesia. Not a great user experience.

This is because our agent is **stateless** - every message is a fresh start. It doesn't remember anything from previous messages.

Let's fix that.

## Enter: The Stateful Greeting Agent

### The Scenario

We want an agent that:
- Asks for your name if it doesn't know it
- Stores your name when you tell it
- Uses your name in future greetings
- Remembers throughout the entire session

### The New Concepts

To build this, we need three new ADK concepts:

1. **State** - A dictionary that persists across messages
2. **Session Service** - Manages the lifecycle of conversations
3. **Runner** - Executes the agent with session support

Let me show you how they work together.

### The Agent Code

```python
from google.adk.agents import Agent

root_agent = Agent(
    name="stateful_greeting_agent",
    model="gemini-2.0-flash",
    description="A greeting agent that remembers your name",
    instruction="""
    You are a friendly assistant that remembers users.

    Use conversation state to manage user information:

    1. If you don't know the user's name (not in state), ask for it
    2. When the user tells you their name, store it in state as 'user_name'
    3. If 'user_name' exists in state, greet them by name

    Be warm, casual, and use their name naturally in conversation.
    """
)
```

The agent itself looks similar, but notice the instruction mentions "state." The AI understands it can read and write to a persistent storage.

### The Runner Code

Here's where the magic happens:

```python
import uuid
import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agent import root_agent

async def main():
    # 1. Create a session service (in-memory for now)
    session_service = InMemorySessionService()

    # 2. Create a unique session for this user
    session = await session_service.create_session(
        app_name="Greeting Bot",
        user_id="user_001",
        session_id=str(uuid.uuid4()),
        state={}  # Start with empty state
    )

    print(f"Session created: {session.id}")

    # 3. Create the runner
    runner = Runner(
        agent=root_agent,
        app_name="Greeting Bot",
        session_service=session_service,
    )

    # 4. Interactive loop
    while True:
        user_input = input("\nYou: ")
        if user_input == "exit":
            break

        message = types.Content(
            role="user",
            parts=[types.Part(text=user_input)]
        )

        for event in runner.run(
            user_id="user_001",
            session_id=session.id,
            new_message=message,
        ):
            if event.is_final_response():
                print(f"Agent: {event.content.parts[0].text}")

asyncio.run(main())
```

### Let's Break This Down

**1. Session Service**
```python
session_service = InMemorySessionService()
```
This is where state gets stored. `InMemorySessionService` keeps everything in RAM (great for development, gone when you restart). For production, you'd use a database-backed service.

**2. Creating a Session**
```python
session = await session_service.create_session(
    app_name="Greeting Bot",
    user_id="user_001",
    session_id=str(uuid.uuid4()),
    state={}  # Empty state to start
)
```
Each user gets their own session with their own state. This is how the agent remembers things per-user.

**3. The Runner**
```python
runner = Runner(
    agent=root_agent,
    app_name="Greeting Bot",
    session_service=session_service,
)
```
The Runner connects everything together - your agent, the session service, and handles execution.

**4. Running with Session Context**
```python
for event in runner.run(
    user_id="user_001",
    session_id=session.id,
    new_message=message,
):
```
When you run the agent, you provide the user and session IDs. The runner automatically loads the state, lets the agent use it, and saves any changes.

### Now Let's See It Work!

```
Session created: abc-123-def-456

You: Hello!
Agent: Hey there! I don't think we've met yet. What's your name?

You: I'm Alex
Agent: Nice to meet you, Alex! I'll remember that. How can I help you today?

You: What's my name?
Agent: Your name is Alex! See, I've got a good memory!

You: Hi again
Agent: Hey Alex! Good to see you again!
```

It remembers! The magic is that after "I'm Alex," the agent stored `{user_name: "Alex"}` in the session state. Every subsequent message has access to that state.

### State vs Context - Important Distinction!

I was confused about this at first, so let me clarify:

**Context** = The conversation history (automatic)
```
["User: Hello", "Agent: Hey there!", "User: I'm Alex", ...]
```
The AI sees all previous messages. But parsing this to find the user's name is inefficient.

**State** = Structured data you explicitly store (manual)
```python
{user_name: "Alex", theme: "dark", language: "en"}
```
Fast to access, easy to query, explicitly controlled.

**Why use State?**
- Faster: Direct lookup vs searching conversation
- Structured: Clean data vs messy text
- Controlled: You decide what to remember
- Persistent: Survives beyond context window limits

### What I Learned

1. **State is powerful** - Once I understood state, I started seeing use cases everywhere: shopping carts, user preferences, form progress, game scores...

2. **Session = User context** - Each session is like a separate notebook for that user. Perfect for multi-user applications.

3. **InMemorySessionService is for development** - It's fast and easy, but everything disappears when you restart. Use database-backed sessions for real apps.

4. **The Runner is the orchestrator** - It handles the complexity of loading state, running the agent, and saving updates.

---

## Recap: Part 1 + Part 2 Concepts

| Part | Feature | What It Does |
|------|---------|--------------|
| 1 | `instruction` | Defines agent personality |
| 1 | `tools` | External capabilities (search, etc.) |
| 1 | `output_schema` | Structured JSON output |
| 2 | State | Persistent memory across messages |
| 2 | Session Service | Manages user sessions |
| 2 | Runner | Executes agent with session support |

We've now covered the fundamentals of single agents. But what if one agent isn't enough?

---

## What's Next?

In **Part 3**, we enter the world of **Workflow Agents**. Instead of one agent doing everything, we'll build teams of specialized agents that work together:

- **SequentialAgent** - Agents that run one after another (like a pipeline)
- **ParallelAgent** - Agents that run simultaneously (faster!)
- **LoopAgent** - Agents that repeat until a condition is met

We'll build:
1. A **Command Helper** - Classifies, generates, and formats shell commands (sequential)
2. A **Multi-Cloud Advisor** - Consults GCP, AWS, and K8s experts at the same time (parallel)
3. A **YAML Generator** - Iteratively improves until perfect (loop)

This is where things get really interesting!

---

*Continue to Part 3: Workflow Agents - Building Agent Teams →*

---

# Part 3: Workflow Agents - Building Agent Teams

📁 **Code**: [GitHub Repository](https://github.com/pranavdhopey/ADK-Agent-Basics.git)

> **TL;DR**: Learn three workflow patterns - `SequentialAgent` (agents run one after another), `ParallelAgent` (agents run simultaneously), and `LoopAgent` (agents repeat until done). Build a YAML generator with validation loop.

*Welcome back! This is Part 3 of my ADK learning series. Catch up with [Part 1 (Basics)](#part-1-the-basics---your-first-ai-agents) and [Part 2 (State Management)](#part-2-state-management---teaching-your-agent-to-remember) if you haven't already.*

---

## Reflections on Parts 1 & 2

Okay, I have to admit - after Part 2, I felt like I'd leveled up. We went from simple one-shot agents to agents that actually remember things across conversations. The `InMemorySessionService` + `Runner` combo felt like unlocking a secret power.

But here's what started bothering me while building more complex agents: **one agent trying to do everything results in mediocre work**. My incident analysis agent was okay at analyzing incidents, but when I tried to make it also format output beautifully AND validate the YAML AND suggest improvements... it got messy.

That's when I discovered **workflow agents**, and honestly? This is where ADK goes from "cool" to "whoa."

## What We're Building in Part 3

In this part, we're learning how to build **teams of agents** that work together. Think of it like building a company:
- Instead of one person doing everything, you have specialists
- Each specialist does ONE thing really well
- They coordinate to deliver amazing results

We'll explore three types of workflows:
- **SequentialAgent** - Agents that run one after another (like a pipeline)
- **ParallelAgent** - Agents that run simultaneously (3x faster!)
- **LoopAgent** - Agents that repeat until they get it right

By the end of Part 3, you'll have built:
1. A **Command Helper** that classifies, generates, and formats shell commands
2. A **Multi-Cloud Advisor** that consults GCP, AWS, and K8s experts in parallel
3. A **YAML Generator** that iteratively improves until the output is perfect

This is where things get really interesting. Let's go!

---

## Why Multiple Agents?

Here's something I realized while building agents: sometimes one agent trying to do everything results in mediocre work. But if you have specialists, each doing one thing really well...

Think about it like a restaurant:
- One person doing cooking, serving, and dishes = okay food, slow service
- Chef cooks, waiter serves, busboy cleans = great food, fast service

The same principle applies to AI agents. Let's build some teams!

## The Three Workflow Agent Types

ADK gives us three ways to orchestrate multiple agents:

| Agent Type | Execution Style | Use When |
|------------|-----------------|----------|
| **SequentialAgent** | One after another | Steps depend on each other |
| **ParallelAgent** | All at once | Steps are independent |
| **LoopAgent** | Repeat until done | Need iterative improvement |

Let me show you each with real examples.

---

## Sequential Agent: The Command Helper

### The Scenario

You want an agent that generates shell commands (Linux, Docker, kubectl, gcloud). But doing this in one shot often produces inconsistent results. So we break it into a pipeline:

1. **Intent Agent** - Figure out what tool the user needs
2. **Command Generator** - Create the actual command
3. **Formatter** - Wrap it in a nice markdown code block

### The Code

First, let's create our specialist agents:

```python
# sub_agents/intent.py
from google.adk.agents import Agent

agent = Agent(
    name="intent_agent",
    model="gemini-2.0-flash",
    output_key="tool_type",  # Store result in state!
    description="Classifies which command-line tool the user needs",
    instruction="""
    Determine which tool the user needs. Respond with ONLY one word:
    - linux (for general shell commands like ls, grep, find)
    - kubectl (for Kubernetes commands)
    - gcloud (for Google Cloud commands)
    - docker (for Docker commands)

    Just the category name, nothing else.
    """
)
```

```python
# sub_agents/command_gen.py
from google.adk.agents import Agent

agent = Agent(
    name="command_generator",
    model="gemini-2.0-flash",
    output_key="raw_command",  # Store result in state!
    description="Generates the actual command",
    instruction="""
    Generate the appropriate {tool_type} command for the user's request.

    Output ONLY the command, no explanation.
    """
)
```

```python
# sub_agents/formatter.py
from google.adk.agents import Agent

agent = Agent(
    name="formatter",
    model="gemini-2.0-flash",
    description="Formats the command beautifully",
    instruction="""
    Format the command in a markdown code block.

    Use {tool_type} to determine the language tag (all use 'bash').

    Format:
    1. Brief one-line description
    2. Code block with the command

    Example:
    List all pods in the default namespace:
    ```bash
    kubectl get pods
    ```
    """
)
```

Now, the magic - connecting them sequentially:

```python
# agent.py
from google.adk.agents import SequentialAgent
from sub_agents.intent import agent as intent
from sub_agents.command_gen import agent as cmd
from sub_agents.formatter import agent as fmt

root_agent = SequentialAgent(
    name="command_helper_agent",
    sub_agents=[intent, cmd, fmt],  # Run in this order!
    description="Generates properly formatted commands through a 3-step pipeline"
)
```

### The Key Concept: output_key and State Variables

Notice `output_key="tool_type"` in the intent agent? This stores its output in state. Then the command generator uses `{tool_type}` in its instruction to access that value!

**State flow:**
```
Step 1 (Intent): {} → {tool_type: "kubectl"}
Step 2 (Command): {tool_type: "kubectl"} → {tool_type: "kubectl", raw_command: "kubectl get pods"}
Step 3 (Format): Uses both, produces final output
```

### Example Conversation

```
You: Show me all running pods
    ↓
Intent: "kubectl"
    ↓
Command: "kubectl get pods"
    ↓
Formatter:
"List all pods in the default namespace:
```bash
kubectl get pods
```"
```

Each agent does ONE thing perfectly!

---

## Parallel Agent: The Multi-Cloud Advisor

### The Scenario

You need architecture advice for a project, but you want perspectives from different cloud platforms. Asking one agent three times is slow. What if you could ask all three simultaneously?

### The Code

Three specialist agents (each focusing on their cloud):

```python
# sub_agents/gcp_arch.py
agent = Agent(
    name="gcp_arch_agent",
    model="gemini-2.0-flash",
    output_key="gcp_solution",  # Stores its answer
    description="GCP cloud architecture expert",
    instruction="""
    You are a GCP architecture expert.

    Provide recommendations using GCP services:
    - Compute: GCE, GKE, Cloud Run, Cloud Functions
    - Storage: Cloud SQL, Cloud Storage, Firestore
    - Networking: VPC, Load Balancer, Cloud CDN

    Be specific with service recommendations.
    """
)
```

```python
# sub_agents/aws_arch.py
agent = Agent(
    name="aws_arch_agent",
    model="gemini-2.0-flash",
    output_key="aws_solution",  # Stores its answer
    # ... similar for AWS
)
```

```python
# sub_agents/k8s_arch.py
agent = Agent(
    name="k8s_arch_agent",
    model="gemini-2.0-flash",
    output_key="k8s_solution",  # Stores its answer
    # ... similar for Kubernetes
)
```

And the formatter that combines everything:

```python
# sub_agents/formatter.py
agent = Agent(
    name="formatter_agent",
    model="gemini-2.0-flash",
    description="Combines all cloud recommendations",
    instruction="""
    Combine the architecture recommendations into a unified report.

    Access the solutions from state:
    - GCP: {gcp_solution}
    - AWS: {aws_solution}
    - Kubernetes: {k8s_solution}

    Create a well-structured comparison document.
    """
)
```

Now the hybrid workflow - parallel THEN sequential:

```python
# agent.py
from google.adk.agents import SequentialAgent, ParallelAgent

# Step 1: All three architects run in PARALLEL
parallel_architects = ParallelAgent(
    name="parallel_architects",
    sub_agents=[gcp, aws, k8s],  # All run simultaneously!
)

# Step 2: Formatter runs AFTER parallel step completes
root_agent = SequentialAgent(
    name="multi_cloud_advisor",
    sub_agents=[parallel_architects, formatter],
    description="Multi-cloud architecture recommendations"
)
```

### The Performance Win

```
Sequential approach:
GCP (5s) → AWS (5s) → K8s (5s) → Format (2s) = 17 seconds

Parallel approach:
[GCP + AWS + K8s in parallel] (5s) → Format (2s) = 7 seconds
```

**3x faster!** Because the three experts don't need each other's output - they can all think at the same time.

### When to Use Parallel

Use ParallelAgent when:
- Tasks are **independent** (don't need each other's results)
- You want **speed** (parallel is faster)
- Each task produces **separate output** (stored with output_key)

Don't use when:
- Step 2 needs Step 1's result (that's sequential)
- Tasks modify the same state (could conflict)

---

## Loop Agent: The Kubernetes YAML Generator

### The Scenario

Here's a real problem I faced: I wanted an AI to generate Kubernetes YAML, but the first draft was never production-ready. It would miss resource limits, forget probes, use `:latest` tags...

What if the agent could **check its own work and improve**? That's exactly what LoopAgent does.

### The Architecture

```
Generator → [Validator → Fixer → Validator → Fixer → ...] → Final YAML
              ↑_________________________↓
                    Loop until perfect
```

### The Code

First, the generator (runs once):

```python
# sub_agents/generator.py
agent = Agent(
    name="yaml_generator",
    model="gemini-2.0-flash",
    output_key="yaml_draft",
    instruction="Generate Kubernetes YAML for the user's request."
)
```

The validator (checks quality):

```python
# sub_agents/validator.py
from google.adk.tools.tool_context import ToolContext

# Custom tool to exit the loop when YAML is perfect
def exit_loop(tool_context: ToolContext):
    """Call this when YAML meets all best practices."""
    tool_context.actions.escalate = True  # This exits the loop!
    return {"status": "approved"}

agent = Agent(
    name="yaml_validator",
    model="gemini-2.0-flash",
    tools=[exit_loop],
    output_key="validation_result",
    instruction="""
    Validate the YAML from {yaml_draft}.

    Check for:
    - Resource requests and limits
    - Readiness and liveness probes
    - Proper labels (app, version)
    - No :latest tags
    - Security context

    If ALL checks pass: call exit_loop()
    If ANY issues found: describe what needs fixing
    """
)
```

The fixer (corrects issues):

```python
# sub_agents/fixer.py
agent = Agent(
    name="yaml_fixer",
    model="gemini-2.0-flash",
    output_key="yaml_draft",  # Updates the draft!
    instruction="""
    Fix the YAML based on {validation_result}.
    Output the corrected YAML.
    """
)
```

And the loop agent that ties it together:

```python
# agent.py
from google.adk.agents import SequentialAgent, LoopAgent

# The improvement loop (validator → fixer, repeat)
improve_loop = LoopAgent(
    name="yaml_improvement_loop",
    sub_agents=[validator, fixer],
    max_iterations=3,  # Safety limit
)

# Full pipeline: generate once, then loop to improve
root_agent = SequentialAgent(
    name="k8s_yaml_helper",
    sub_agents=[generator, improve_loop],
)
```

### The Magic: exit_loop

The validator has a special tool called `exit_loop()`. When the YAML passes all checks, it calls this tool, which sets `tool_context.actions.escalate = True`. This tells the LoopAgent to stop immediately.

Without this, the loop would always run all 3 iterations even if the YAML was perfect on the first try!

### Example Execution

```
User: "Create a deployment for nginx with 3 replicas"
    ↓
Generator: Creates initial YAML (missing some best practices)
    ↓
[Loop Iteration 1]
Validator: "Missing resource limits and readiness probe"
Fixer: Adds resource limits and readiness probe
    ↓
[Loop Iteration 2]
Validator: "Missing security context"
Fixer: Adds security context
    ↓
[Loop Iteration 3]
Validator: "All checks pass!" → calls exit_loop()
    ↓
Final YAML returned (production-ready!)
```

### What I Learned About LoopAgent

1. **Always set max_iterations** - Infinite loops are bad!
2. **The exit condition is a tool** - The AI decides when to exit by calling the tool
3. **State accumulates** - Each iteration can read/write state
4. **Quality improves** - Perfect for validation/correction patterns

---

## Recap: Workflow Agent Types

| Agent | Pattern | Example | Key Insight |
|-------|---------|---------|-------------|
| Sequential | A → B → C | Command Helper | Order matters, pass data via state |
| Parallel | A + B + C | Multi-Cloud Advisor | Independent tasks, 3x faster |
| Loop | [A → B] repeat | YAML Generator | Iterate until quality is met |

You can even **combine** them like we did with the Multi-Cloud Advisor (Parallel inside Sequential)!

---

## What's Next?

In **Part 4**, we tackle the ultimate challenge: **Multi-Agent Systems with Routing**.

Instead of hardcoded workflows, we'll build a system where:
- A **router agent** reads user messages
- It decides which specialist to call
- The specialist handles the request

This is how you build assistants that can handle many different types of requests - like a real company with departments!

We'll build a complete system with:
- A router agent that analyzes intent
- A greeting specialist for casual hellos
- An incident analyst for technical issues

And we'll solve the tricky problem of **infinite loops** when agents try to transfer back and forth!

---

*Continue to Part 4: Multi-Agent Systems - The Router Pattern →*

---

# Part 4: Multi-Agent Systems - The Router Pattern

📁 **Code**: [GitHub Repository](https://github.com/pranavdhopey/ADK-Agent-Basics.git)

> **TL;DR**: Learn the router pattern where a main agent analyzes intent and delegates to specialists using `sub_agents`. Build a DevOps Copilot with kubectl and gcloud specialist agents that handle domain-specific requests.

*Welcome back! This is Part 4 of my ADK learning series. If you're new here, start with [Part 1 (Basics)](#part-1-the-basics---your-first-ai-agents), then [Part 2 (State Management)](#part-2-state-management---teaching-your-agent-to-remember), and [Part 3 (Workflow Agents)](#part-3-workflow-agents---building-agent-teams).*

---

## Reflections on Parts 1-3

What. A. Journey.

Looking back at where we started - literally just trying to make an AI say "hello" with personality - and where we are now... it's kind of amazing. We've gone from:
- Simple agents (Part 1) → Agents with memory (Part 2) → Teams of agents (Part 3)

The workflow agents in Part 3 were a game-changer for me. The idea that I could have a "generator" agent, a "validator" agent, and a "fixer" agent working in a loop until the output is perfect? That's not just cool - that's production-ready quality assurance!

But there was still one thing bugging me: **all our workflows were predetermined**. The Sequential/Parallel/Loop agents always follow the same path. What if I want an agent that can handle *any* type of request and figure out the right path dynamically?

## What We're Building in Part 4

This is the capstone of the series. We're building a **multi-agent system with dynamic routing**:
- A **Router Agent** that reads user messages and decides what to do
- **Specialist Agents** that handle specific types of requests
- **Transfer Control** to prevent infinite loops (this one took me HOURS to debug!)

Think of it like a company's reception desk:
1. Someone walks in (user message)
2. The receptionist (router) figures out what they need
3. They direct them to the right department (specialist agent)
4. The specialist handles everything from there

By the end of Part 4, you'll have:
- A complete support bot that greets users OR analyzes technical incidents
- Deep understanding of transfer control (and why infinite loops happen)
- Production-ready patterns for building scalable agent systems

This is the most complex thing we've built - but if you've followed along, you're ready. Let's finish strong!

---

## The Challenge

So far, we've built agents that do one thing, or workflows with predetermined steps. But what about a system that can handle *any* type of request?

Imagine building a support bot that should:
- Greet users warmly when they say "hello"
- Analyze technical incidents when they report problems

You could build one massive agent with a huge instruction... but that gets messy fast. Instead, let's use the **router pattern**.

## The Router Pattern

The idea is simple:
1. A **router agent** receives all user messages
2. It analyzes the intent
3. It delegates to the appropriate **specialist agent**
4. The specialist handles the request

```
User Message → Router → [Greeting Agent OR Incident Agent]
```

### The Code - Specialist Agents

First, our specialists. Notice how each one is focused and includes important features:

```python
# sub_agents/greeting_agent/agent.py
from google.adk.agents import Agent

agent = Agent(
    name="greeting_agent",
    model="gemini-2.0-flash",
    description="Handles casual greetings like hello, hi, hey - responds warmly and asks for user's name",
    output_key="greeting_response",           # Store output in state
    disallow_transfer_to_parent=True,         # Can't go back to router
    disallow_transfer_to_peers=True,          # Can't go to incident agent
    instruction="""
You are a friendly, casual, and slightly funny assistant specialized in greetings.

STATE MANAGEMENT:
- Check if 'user_name' exists in session state
- If user_name is NOT in state, ask for their name
- When user tells you their name, store it in state as 'user_name'
- If user_name IS in state, greet them by name

BEHAVIOR:
- Greet the user warmly and keep it short and natural
- Light jokes are okay but stay professional
- Avoid sarcasm or offensive humor

IMPORTANT: Do NOT transfer to any other agent. Complete your greeting and respond directly.
"""
)
```

The incident analysis agent uses **structured output** with proper validation:

```python
# sub_agents/incident_analysis_agent/agent.py
from typing import List, Literal
from pydantic import BaseModel, Field
from google.adk.agents import Agent

class IncidentReport(BaseModel):
    """Structured incident analysis report."""
    incident_summary: str = Field(
        description="Brief summary of what went wrong and the impact"
    )
    severity: Literal["low", "medium", "high", "critical"] = Field(
        description="Severity level based on impact and urgency"
    )
    affected_components: List[str] = Field(
        description="List of affected systems, services, or components"
    )
    probable_cause: str = Field(
        description="Most likely root cause based on the symptoms described"
    )
    immediate_actions: List[str] = Field(
        description="List of 3-5 recommended troubleshooting steps in priority order"
    )

agent = Agent(
    name="incident_analysis_agent",
    model="gemini-2.0-flash",
    description="Analyzes technical incidents involving cloud, infrastructure, networking, database, and deployment issues",
    output_key="incident_report",             # Store output in state
    output_schema=IncidentReport,             # Enforces structured JSON
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    instruction="""
You are an Incident Analysis Assistant specializing in cloud and infrastructure issues.

ANALYSIS GUIDELINES:
1. incident_summary: Concise description of the problem and its business impact
2. severity: Determine based on:
   - critical: Complete outage, data loss risk, security breach
   - high: Major functionality broken, many users affected
   - medium: Partial degradation, workaround available
   - low: Minor issue, minimal impact
3. affected_components: Identify ALL systems involved (be thorough)
4. probable_cause: Provide the most likely root cause based on symptoms
5. immediate_actions: List 3-5 specific, actionable troubleshooting steps in priority order

Be specific, technical, and actionable. Avoid generic advice.

IMPORTANT: Do NOT transfer to any other agent. Analyze the incident and respond with the structured report.
"""
)
```

**Key improvements I made:**

| Feature | Why It Matters |
|---------|---------------|
| `output_key` | Stores output in session state for later use |
| `Literal["low", "medium", "high", "critical"]` | Validates severity - can only be one of these values! |
| `Field(description=...)` | Helps the AI understand what goes in each field |
| Explicit "Do NOT transfer" | Reinforces terminal behavior |

### The Router - Externalized Instructions

Here's a pro tip I learned: **externalize long instructions into constants**. It makes the code cleaner and easier to maintain:

```python
# agent.py
from google.adk.agents import Agent
from .sub_agents.greeting_agent.agent import agent as greeting_agent
from .sub_agents.incident_analysis_agent.agent import agent as incident_analysis_agent

# Externalized for better maintainability
ROUTER_INSTRUCTION = """
You are a routing agent. Read the user's message and delegate to the correct specialist agent.

ROUTING RULES:

RULE 1 - TECHNICAL ISSUES (use incident_analysis_agent):
Check if the message contains ANY of these technical keywords:
- Problems: issue, problem, error, failed, down, broken, not working, crash, outage, timeout
- Connectivity: connect, connecting, connectivity, unable to, can't access, unreachable
- Cloud/Infra: GKE, GCP, GCE, AWS, Azure, cloud, VM, server, cluster, container, pod, Kubernetes
- Networking: VPC, subnet, network, firewall, DNS, routing, load balancer, ingress
- Data: database, SQL, Redis, storage, backup, replication
- DevOps: deployment, configuration, YAML, helm, terraform, CI/CD, pipeline
- Environment: onprem, on-premise, hybrid, production, staging
- Actions: troubleshoot, debug, fix, help with, investigate

If ANY technical keyword is found → delegate to: incident_analysis_agent

RULE 2 - GREETINGS (use greeting_agent):
If the message is ONLY a casual greeting with NO technical content:
- hello, hi, hey, good morning, good afternoon, good evening, how are you, what's up

If ONLY greeting words → delegate to: greeting_agent

RULE 3 - FALLBACK (ask for clarification):
If the message doesn't clearly fit either category:
- Ask a brief clarifying question
- Example: "I'd be happy to help! Are you reporting a technical issue, or just saying hello?"

EXAMPLES:
- "hello" → greeting_agent (only greeting)
- "hi there!" → greeting_agent (only greeting)
- "my server is down" → incident_analysis_agent (has: server, down)
- "Hello, I'm having an issue with GKE" → incident_analysis_agent (has: issue, GKE)
- "asdfgh" → Ask for clarification (doesn't fit either category)
- "can you help me?" → Ask for clarification (unclear intent)

IMPORTANT: Always delegate to a specialist. Only respond yourself for Rule 3 fallback clarifications.
"""

root_agent = Agent(
    name="router_agent",
    model="gemini-2.0-flash",
    sub_agents=[greeting_agent, incident_analysis_agent],
    description="Routes user requests to greeting or incident analysis specialists based on message content",
    instruction=ROUTER_INSTRUCTION
)
```

**What I added:**
- **Rule 3 - Fallback**: Handles unclear messages instead of guessing wrong
- **Comprehensive keywords**: Organized by category for easy maintenance
- **More examples**: Including edge cases like "asdfgh"
- **Externalized instruction**: Easier to update and test

### The Transfer Control Problem (And What I Learned)

Here's a bug that took me HOURS to figure out. My agents kept getting stuck in an infinite loop:

```
User: "Hello"
Router → Greeting Agent
Greeting Agent → Router (trying to go back)
Router → Greeting Agent
... forever ...
```

The solution? Those two parameters:

```python
disallow_transfer_to_parent=True,  # Can't transfer back to router
disallow_transfer_to_peers=True,   # Can't transfer to other specialists
```

**Important discovery**: These are "soft constraints" - they modify the system prompt to discourage transfers, but don't technically block them at runtime. That's why I ALSO add explicit instructions like "Do NOT transfer to any other agent" in each specialist.

This makes each specialist a **terminal agent** - it handles the request and stops. No bouncing around!

### Why Terminal Agents Matter

Without transfer control:
```
User: "Hello"
Router: "This is a greeting, transferring to greeting_agent"
Greeting Agent: "Hi! ... hmm, should I transfer back?"
Router: "This is a greeting, transferring to greeting_agent"
... infinite loop ...
```

With transfer control:
```
User: "Hello"
Router: "This is a greeting, transferring to greeting_agent"
Greeting Agent: "Hi there! Great to meet you! What's your name?"
... done! ...
```

### Making Routing Reliable

My first router instruction was vague:

```python
# Bad - too vague
instruction="Route greetings to greeting agent and technical issues to incident agent"
```

It worked... sometimes. But edge cases failed constantly.

The fix? **Explicit keywords, categories, and examples:**

```python
# Good - explicit rules organized by category
instruction="""
RULE 1 - TECHNICAL ISSUES:
- Problems: issue, problem, error, failed, down, broken...
- Cloud/Infra: GKE, GCP, AWS, server, cluster...
- Networking: VPC, firewall, DNS, load balancer...
→ incident_analysis_agent

RULE 2 - GREETINGS:
- ONLY: hello, hi, hey, good morning...
→ greeting_agent

RULE 3 - FALLBACK:
- Unclear? Ask for clarification!

EXAMPLES:
- "hello" → greeting_agent
- "my server is down" → incident_analysis_agent
- "hi, I'm having an issue" → incident_analysis_agent (has "issue")
- "asdfgh" → Ask for clarification
"""
```

Notice the "hi, I'm having an issue" example - it teaches the router that greetings with problems go to incident analysis, not greeting!

### Adding Error Handling

One more improvement - proper error handling in the runner:

```python
# run_agent.py
while True:
    try:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "q"]:
            print("Goodbye!")
            break

        if not user_input.strip():
            print("Please enter a message.")
            continue

        # ... run agent ...

        for event in runner.run(...):
            if event.is_final_response():
                if event.content and event.content.parts:
                    print(f"Agent: {event.content.parts[0].text}")
                else:
                    print("Agent: [No response content]")

    except KeyboardInterrupt:
        print("\nInterrupted. Goodbye!")
        break
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        print("Please try again or type 'exit' to quit.")
```

This handles: empty input, keyboard interrupts, API errors, and missing responses

---

## Putting It All Together

Here's the final architecture of a complete multi-agent system:

```
                         User Message
                              │
                              ▼
                    ┌─────────────────┐
                    │  Router Agent   │
                    │  (analyzes      │
                    │   intent)       │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                              ▼
        ┌──────────┐                ┌──────────────┐
        │ Greeting │                │   Incident   │
        │  Agent   │                │   Analysis   │
        │          │                │    Agent     │
        └──────────┘                └──────────────┘
        (terminal)                    (terminal)
```

Each specialist is:
- **Focused** on one task
- **Terminal** (doesn't transfer to others)
- **Specialized** with its own tools/schema if needed

The router is:
- **Smart** about intent detection
- **Explicit** with routing rules
- **Always delegates** (never answers directly)

---

## The Complete Journey

Let's recap everything we've learned across all four parts:

### Part 1: The Basics
| Concept | What It Does |
|---------|--------------|
| `Agent` | The core AI component |
| `instruction` | Defines personality and behavior |
| `tools` | External capabilities (search, etc.) |
| `output_schema` | Forces structured JSON output |

### Part 2: State Management
| Concept | What It Does |
|---------|--------------|
| State | Persistent memory across messages |
| Session Service | Manages user sessions |
| Runner | Executes agent with session support |
| `output_key` | Stores agent output in state |

### Part 3: Workflow Agents
| Concept | What It Does |
|---------|--------------|
| `SequentialAgent` | Runs agents in order (A → B → C) |
| `ParallelAgent` | Runs agents simultaneously (A + B + C) |
| `LoopAgent` | Runs until condition met (repeat A → B) |
| Template Variables | Reference state with `{variable_name}` |
| Custom Tools | Control loop exit with `escalate` |

### Part 4: Multi-Agent Systems
| Concept | What It Does |
|---------|--------------|
| Router Pattern | Central agent delegates to specialists |
| `sub_agents` | Register specialists with router |
| Transfer Control | Soft constraints to prevent infinite loops |
| `Literal` Type | Validates enum-like values (e.g., severity) |
| Fallback Handling | Ask for clarification when intent is unclear |
| Externalized Instructions | Move long instructions to constants |
| Error Handling | Gracefully handle API errors and edge cases |

---

## What Makes a Good Agent System?

After building all these agents, here's my advice:

### 1. Start Simple
Don't build a multi-agent router for a simple task. Start with one agent, add complexity only when needed.

### 2. Make Specialists Actually Specialized
Each agent should do ONE thing well. If an agent's instruction is 50 lines, it's doing too much.

### 3. Use output_key Everywhere
It's the glue that holds multi-agent systems together. Always name your outputs.

### 4. Test Edge Cases
"Hi, my server is broken" - is that a greeting or an incident? Make sure your router handles these!

### 5. Terminal Agents are Your Friend
For router patterns, always use `disallow_transfer_to_parent=True`. Trust me, infinite loops are not fun to debug.

---

## Your Next Steps

You now have all the tools to build sophisticated AI agent systems! Here are some project ideas:

### Beginner Projects
- **Personal Assistant** - Greets you, searches web, sets reminders
- **Code Helper** - Generates, explains, and reviews code
- **Quiz Bot** - Asks questions, tracks scores (stateful!)

### Intermediate Projects
- **Support Bot** - Routes to billing, technical, or sales agents
- **Document Generator** - Parallel research + sequential writing
- **CI/CD Helper** - Validates configs, suggests fixes (loop)

### Advanced Projects
- **Full DevOps Assistant** - Multi-cloud, K8s, monitoring, incidents
- **Research Agent** - Parallel web searches + structured synthesis
- **Game Master** - Stateful RPG with multiple story branches

---

## What's Next?

We've mastered routing with `sub_agents` - but there's one more powerful pattern to explore. In **Part 5**, we'll learn about **AgentTool** - a different way to combine agents where the main agent stays in control.

We'll build a **DevOps Copilot** that:
- Calls specialist agents as tools (not transfers!)
- Gets results back and presents them
- Can combine multiple tool results if needed

The key difference: with `sub_agents`, control transfers completely. With `AgentTool`, the main agent stays in charge. Both patterns have their place!

---

*Continue to Part 5: AgentTool - Agents as Tools →*

---

# Part 5: AgentTool - Turning Agents Into Tools

📁 **Code**: [GitHub Repository](https://github.com/pranavdhopey/ADK-Agent-Basics.git)

> **TL;DR**: Learn `AgentTool` to wrap agents as callable tools (unlike `sub_agents` where control transfers). The main agent stays in control, calls specialists, and gets results back. Great for orchestration.

*Bonus part! If you're following along, you've already mastered [Part 1 (Basics)](#part-1-the-basics---your-first-ai-agents), [Part 2 (State)](#part-2-state-management---teaching-your-agent-to-remember), [Part 3 (Workflows)](#part-3-workflow-agents---building-agent-teams), and [Part 4 (Multi-Agent Routing)](#part-4-multi-agent-systems---the-router-pattern).*

---

## Reflections on Part 4

The router pattern was powerful - we built a system where a router agent analyzes intent and delegates to specialists. But there was something that bothered me: once the router transfers to a specialist, **the specialist takes over completely**. The router is out of the picture.

What if I want the main agent to:
- Call a specialist for a specific task
- Get the result back
- Do something else with it (combine results, post-process, etc.)

This is where **AgentTool** comes in, and honestly? It's one of my favorite ADK features now.

## What We're Building in Part 5

We're building a **DevOps Copilot** - an assistant that helps with:
- Generating kubectl commands
- Generating gcloud commands
- Explaining errors (CrashLoopBackOff, OOMKilled, etc.)
- Creating Kubernetes YAML manifests

But here's the twist: instead of transferring control to specialists (like Part 4), our copilot **calls** specialists as tools and gets results back. Think of it like:
- **Part 4 (sub_agents)**: "Here, you handle this. I'm done."
- **Part 5 (AgentTool)**: "Give me the answer, I'll present it to the user."

By the end of Part 5, you'll understand:
- The difference between `AgentTool` and `sub_agents`
- When to use each pattern
- How to build composite agents that orchestrate specialists

Let's build!

---

## AgentTool vs Sub-Agents - The Mental Model

Before we dive into code, let me explain the difference with an analogy:

**Sub-Agents (Part 4) = Transferring a Call**
```
Customer calls → Receptionist → "Let me transfer you to Billing"
→ Billing handles everything from here
→ Customer talks directly with Billing
```

**AgentTool (Part 5) = Putting Someone on Hold**
```
Customer calls → Receptionist → "Let me check with Billing"
→ Receptionist calls Billing, gets answer
→ Receptionist comes back: "Billing says your balance is $50"
```

The key difference? **Who stays in control.**

| Feature | AgentTool | Sub-Agents |
|---------|-----------|------------|
| **Control flow** | Main agent stays in control | Control transfers to specialist |
| **Result handling** | Main agent gets result back | Specialist responds directly |
| **Chaining** | Can call multiple tools in sequence | One specialist handles request |
| **Post-processing** | Main agent can modify/combine results | Specialist has final say |
| **Use case** | Composite tasks, combining results | Routing to specialists |

---

## The DevOps Copilot Architecture

Here's what we're building:

```
User Request
    │
    ▼
┌─────────────────────────────────────────────────────┐
│           DevOps Copilot (root_agent)               │
│                                                      │
│  Analyzes request and calls appropriate tool:       │
│                                                      │
│  ┌─────────────┐  ┌─────────────┐                   │
│  │ kubectl_tool│  │ gcloud_tool │                   │
│  │ (AgentTool) │  │ (AgentTool) │                   │
│  └──────┬──────┘  └──────┬──────┘                   │
│         │                │                          │
│  ┌──────▼──────┐  ┌──────▼──────┐                   │
│  │kubectl_agent│  │gcloud_agent │                   │
│  └─────────────┘  └─────────────┘                   │
│                                                      │
│  ┌─────────────┐  ┌─────────────┐                   │
│  │ error_tool  │  │  yaml_tool  │                   │
│  │ (AgentTool) │  │ (AgentTool) │                   │
│  └──────┬──────┘  └──────┬──────┘                   │
│         │                │                          │
│  ┌──────▼──────┐  ┌──────▼──────┐                   │
│  │ error_agent │  │ yaml_agent  │                   │
│  └─────────────┘  └─────────────┘                   │
│                                                      │
│  Main agent receives results and responds           │
└─────────────────────────────────────────────────────┘
    │
    ▼
Response to User
```

The main agent stays in control throughout. It decides which tool to call, gets the result, and presents it to the user.

---

## Building the Specialist Agents

First, let's create our specialist agents. Each one is focused on ONE task:

### 1. Kubectl Agent

```python
# tools/kubectl_agent.py
from google.adk.agents import Agent

kubectl_agent = Agent(
    name="kubectl_agent",
    model="gemini-2.0-flash",
    description="Generates kubectl commands only",
    output_key="kubectl_command",
    instruction="""
You are a kubectl CLI expert specializing in Kubernetes command generation.

YOUR TASK:
- Generate the exact kubectl command for the user's request
- Return ONLY the command - no explanations, no markdown, no code blocks

COMMAND GUIDELINES:
- Use proper flags and options
- Include namespace flags (-n) when relevant
- Use appropriate output formats (-o yaml, -o json, -o wide) when helpful

EXAMPLES OF GOOD OUTPUT:
- kubectl get pods -n production
- kubectl describe deployment nginx -n default
- kubectl logs -f deployment/my-app --tail=100

Return only the command, nothing else.
"""
)
```

### 2. GCloud Agent

```python
# tools/gcloud_agent.py
from google.adk.agents import Agent

gcloud_agent = Agent(
    name="gcloud_agent",
    model="gemini-2.0-flash",
    description="Generates gcloud CLI commands only",
    output_key="gcloud_command",
    instruction="""
You are a Google Cloud gcloud CLI expert.

YOUR TASK:
- Generate the exact gcloud command for the user's request
- Return ONLY the command - no explanations, no markdown, no code blocks

COMMAND AREAS:
- Compute Engine: gcloud compute instances, disks, networks
- Kubernetes Engine: gcloud container clusters, node-pools
- IAM: gcloud iam service-accounts, roles, policies
- Storage: gcloud storage buckets, objects

Return only the command, nothing else.
"""
)
```

### 3. Error Explainer Agent (with Structured Output!)

This one is special - it returns structured output for consistent error explanations:

```python
# tools/error_agent.py
from typing import List
from pydantic import BaseModel, Field
from google.adk.agents import Agent


class ErrorExplanation(BaseModel):
    """Structured output for error explanations"""
    error_name: str = Field(description="The name or type of the error")
    cause: str = Field(description="What causes this error to occur")
    impact: str = Field(description="What happens when this error occurs")
    fix_steps: List[str] = Field(description="Step-by-step instructions to resolve")
    helpful_commands: List[str] = Field(description="Useful commands for debugging")
    prevention: str = Field(description="How to prevent this error in the future")


error_agent = Agent(
    name="error_explainer_agent",
    model="gemini-2.0-flash",
    description="Explains infra and cloud errors with fixes",
    output_key="error_explanation",
    output_schema=ErrorExplanation,
    instruction="""
You are a DevOps error specialist who explains infrastructure and cloud errors.

ERROR CATEGORIES YOU HANDLE:
- Kubernetes: CrashLoopBackOff, ImagePullBackOff, OOMKilled, Pending pods
- Container: Exit codes, resource limits, health check failures
- Cloud: Permission denied, quota exceeded, network issues

Provide specific, actionable information.
"""
)
```

### 4. YAML Generator Agent

```python
# tools/yaml_agent.py
from google.adk.agents import Agent

yaml_agent = Agent(
    name="k8s_yaml_generator",
    model="gemini-2.0-flash",
    description="Generates Kubernetes YAML manifests",
    output_key="k8s_yaml",
    instruction="""
You are a Kubernetes YAML manifest expert.

YOUR TASK:
- Generate valid Kubernetes YAML manifests
- Return ONLY the YAML - no explanations, no markdown code blocks

YAML GUIDELINES:
- Always include apiVersion, kind, metadata
- Use proper indentation (2 spaces)
- Include common labels (app, version)
- Add resource requests/limits for containers
- Include health checks where appropriate

Return only valid YAML that can be directly applied with kubectl apply -f.
"""
)
```

---

## The Magic: Converting Agents to Tools

Here's where `AgentTool` comes in. We convert each specialist agent into a tool:

```python
# agent.py
from google.adk.agents import Agent
from google.adk.tools import AgentTool

from .tools.kubectl_agent import kubectl_agent
from .tools.gcloud_agent import gcloud_agent
from .tools.error_agent import error_agent
from .tools.yaml_agent import yaml_agent


# Convert agents → tools
kubectl_tool = AgentTool(agent=kubectl_agent)
gcloud_tool = AgentTool(agent=gcloud_agent)
error_tool = AgentTool(agent=error_agent)
yaml_tool = AgentTool(agent=yaml_agent)
```

**That's it!** One line each. `AgentTool(agent=my_agent)` converts any agent into a tool that another agent can call.

---

## The Main Copilot Agent

Now we create the main agent that uses these tools:

```python
COPILOT_INSTRUCTION = """
You are a DevOps/Cloud Copilot - a helpful assistant for DevOps engineers.

IMPORTANT: Always use the appropriate tool instead of answering manually.

TOOL ROUTING:
- kubectl tasks (pods, deployments, services, namespaces, logs) → use kubectl_agent
- gcloud tasks (GCE, GKE, IAM, storage, networking) → use gcloud_agent
- errors/issues (CrashLoopBackOff, OOMKilled, permission errors) → use error_explainer_agent
- yaml/manifest creation (deployments, services, configmaps) → use k8s_yaml_generator

WORKFLOW:
1. Analyze the user's request
2. Determine which tool is most appropriate
3. Call the tool and wait for the result
4. Present the result to the user with brief context if helpful

Do NOT generate kubectl commands, gcloud commands, or YAML yourself.
Always delegate to the specialist tools.
"""

root_agent = Agent(
    name="devops_copilot",
    model="gemini-2.0-flash",
    description="DevOps assistant that delegates to specialist tools",

    tools=[
        kubectl_tool,
        gcloud_tool,
        error_tool,
        yaml_tool
    ],

    instruction=COPILOT_INSTRUCTION
)
```

Notice: we use `tools=[...]` not `sub_agents=[...]`. This is the key difference!

---

## Example Conversations

Let's see how this works in practice:

### Kubectl Task

```
You: How do I get all pods in the production namespace?
    ↓
Copilot thinks: "This is a kubectl task"
    ↓
Copilot calls: kubectl_tool("get all pods in production namespace")
    ↓
kubectl_agent returns: "kubectl get pods -n production"
    ↓
Copilot to user: Here's the command to list pods in production:
                 kubectl get pods -n production
```

The copilot stayed in control. It called the specialist, got the command, and presented it.

### Error Explanation

```
You: What does "CrashLoopBackOff" mean in Kubernetes?
    ↓
Copilot thinks: "This is an error explanation task"
    ↓
Copilot calls: error_tool("CrashLoopBackOff")
    ↓
error_agent returns: {
    error_name: "CrashLoopBackOff",
    cause: "Container keeps crashing and Kubernetes keeps restarting it",
    impact: "Pod never becomes ready, service unavailable",
    fix_steps: ["Check logs with kubectl logs", "Verify image exists", ...],
    helpful_commands: ["kubectl logs pod/name", "kubectl describe pod/name"],
    prevention: "Add proper health checks, resource limits"
}
    ↓
Copilot to user: CrashLoopBackOff means your pod keeps crashing...
                 Cause: ...
                 Fix: ...
```

The structured output from error_agent makes it easy for the copilot to present organized information!

### YAML Generation

```
You: Create a deployment for nginx with 3 replicas
    ↓
Copilot thinks: "This is a YAML generation task"
    ↓
Copilot calls: yaml_tool("nginx deployment with 3 replicas")
    ↓
yaml_agent returns: Complete YAML manifest
    ↓
Copilot to user: Here's the Kubernetes deployment:
                 apiVersion: apps/v1
                 kind: Deployment
                 ...
```

---

## When to Use AgentTool vs Sub-Agents

This was confusing for me at first, so here's my decision framework:

### Use AgentTool When:
- ✅ You want to **combine results** from multiple specialists
- ✅ The main agent needs to **post-process** results
- ✅ You're building a **"command center"** agent
- ✅ You want **consistent presentation** of results
- ✅ The main agent might call **multiple tools** for one request

### Use Sub-Agents When:
- ✅ Each specialist **handles the request completely**
- ✅ No post-processing needed
- ✅ Building a **router/dispatcher** pattern
- ✅ Specialists have **very different response styles**
- ✅ You want specialists to **interact directly** with users

### Real-World Examples

**AgentTool pattern:**
- DevOps Copilot (this example)
- Research Assistant (searches multiple sources, combines results)
- Code Review Bot (runs linter, security check, style check - combines findings)

**Sub-Agents pattern:**
- Support Bot (routes to billing, technical, sales - each handles completely)
- Multi-language Bot (routes to English, Spanish, French handlers)
- Game Bot (routes to different game modes)

---

## Key Concepts Recap

| Feature | What It Does |
|---------|--------------|
| `AgentTool` | Converts an Agent into a Tool |
| `tools=[...]` | Registers tools with the main agent |
| Main agent | Stays in control, calls tools, presents results |
| `output_key` | Stores tool output in state |
| `output_schema` | Structured output for consistent data |

---

## The Complete Pattern

```python
from google.adk.agents import Agent
from google.adk.tools import AgentTool

# 1. Create specialist agents
specialist_1 = Agent(
    name="specialist_1",
    output_key="result_1",
    instruction="Do one thing well..."
)

specialist_2 = Agent(
    name="specialist_2",
    output_key="result_2",
    instruction="Do another thing well..."
)

# 2. Convert to tools
tool_1 = AgentTool(agent=specialist_1)
tool_2 = AgentTool(agent=specialist_2)

# 3. Create main agent with tools
main_agent = Agent(
    name="main_agent",
    tools=[tool_1, tool_2],
    instruction="Use the right tool for each task..."
)
```

That's the pattern! Specialist agents → AgentTool → Main agent uses tools.

---

## What I Learned

1. **AgentTool is for orchestration** - When you want one agent to coordinate others without losing control.

2. **The description matters** - The main agent uses each tool's description to decide when to call it. Good descriptions = better routing.

3. **Specialists should be focused** - Each specialist does ONE thing. The main agent handles the complexity of combining them.

4. **Structured output + AgentTool = powerful** - The error_agent with `output_schema` shows how tools can return rich, structured data that the main agent can present beautifully.

5. **It's like building a team** - The main agent is the manager. Specialists are the experts. AgentTool is how they communicate.

---

## What's Next?

We've learned how to use `AgentTool` to wrap agents and call them as tools. But what if you want your agent to execute **real code** - run shell commands, make API calls, or interact with databases?

In **Part 6**, we'll explore **FunctionTool** - the ability to wrap Python functions as tools that the LLM can call. We'll build a **DevOps Runtime Assistant** that actually executes `kubectl` and `gcloud` commands on real infrastructure.

The key difference:
- **AgentTool**: Wraps an Agent (uses LLM to generate response)
- **FunctionTool**: Wraps a Python function (executes real code)

---

*Continue to Part 6: FunctionTool - Real Code Execution →*

---

# Part 6: FunctionTool - Giving Agents Real Power

📁 **Code**: [GitHub Repository](https://github.com/pranavdhopey/ADK-Agent-Basics.git)

> **TL;DR**: Learn `FunctionTool` to wrap Python functions as tools that execute real code (kubectl, gcloud, HTTP requests). Unlike AgentTool (LLM reasoning), FunctionTool runs actual commands and returns real results.

*Final part! You've mastered [Part 1 (Basics)](#part-1-the-basics---your-first-ai-agents), [Part 2 (State)](#part-2-state-management---teaching-your-agent-to-remember), [Part 3 (Workflows)](#part-3-workflow-agents---building-agent-teams), [Part 4 (Multi-Agent Routing)](#part-4-multi-agent-systems---the-router-pattern), and [Part 5 (AgentTool)](#part-5-agenttool---turning-agents-into-tools).*

---

## Reflections on Part 5

The AgentTool pattern was elegant - we could wrap specialist agents and call them as tools. But there's something important to notice: those tools still used **LLM reasoning** to generate responses. The kubectl_agent *generated* a command string, it didn't *execute* it.

What if I want my agent to actually:
- Run a shell command and get the output?
- Make an HTTP request and check if a service is healthy?
- Query a database and return results?
- Interact with real infrastructure?

This is where **FunctionTool** comes in - and it's a game-changer.

## What We're Building in Part 6

We're building a **DevOps Runtime Assistant** - an agent that can actually **execute** commands on your infrastructure:

- Check pod status (runs `kubectl get pods`)
- Get GCP VM details (runs `gcloud compute instances describe`)
- Scale deployments (runs `kubectl scale`)
- Check service health (makes real HTTP requests)

The difference from Part 5:
- **Part 5 (AgentTool)**: "Here's the kubectl command you should run"
- **Part 6 (FunctionTool)**: "I ran kubectl, here are your pods"

By the end of Part 6, you'll understand:
- How to wrap Python functions as tools
- Why docstrings are critical for FunctionTool
- How to handle errors gracefully
- Safety considerations for infrastructure tools

Let's build!

---

## FunctionTool vs AgentTool - The Core Difference

Let me make this crystal clear:

| Feature | FunctionTool | AgentTool |
|---------|--------------|-----------|
| **Wraps** | Python function | Another Agent |
| **Execution** | Runs real code | Uses LLM reasoning |
| **Speed** | Fast (no LLM call) | Slower (LLM call) |
| **Deterministic** | Yes (same input → same output) | No (LLM may vary) |
| **Use case** | API calls, CLI commands, calculations | Complex reasoning, text generation |

**FunctionTool is for doing things. AgentTool is for thinking about things.**

---

## The DevOps Runtime Architecture

Here's what we're building:

```
User: "Check pods in production namespace"
    │
    ▼
┌─────────────────────────────────────────────────────┐
│         DevOps Runtime Agent                        │
│                                                     │
│  LLM analyzes request and decides:                  │
│  "I should call check_pod_status"                   │
│                                                     │
│  ┌─────────────────┐  ┌─────────────────┐          │
│  │ check_pod_status│  │ get_gcp_instance│          │
│  │ (FunctionTool)  │  │ (FunctionTool)  │          │
│  └────────┬────────┘  └─────────────────┘          │
│           │                                         │
│  ┌────────▼────────┐                               │
│  │ Python Function │                               │
│  │ subprocess.run  │                               │
│  │ kubectl get...  │                               │
│  └────────┬────────┘                               │
│           │                                         │
│  Returns: {"output": "NAME  READY...", ...}        │
│                                                     │
│  ┌─────────────────┐  ┌─────────────────┐          │
│  │scale_deployment │  │check_svc_health │          │
│  │ (FunctionTool)  │  │ (FunctionTool)  │          │
│  └─────────────────┘  └─────────────────┘          │
│                                                     │
│  LLM receives result and responds to user          │
└─────────────────────────────────────────────────────┘
    │
    ▼
"Here are your pods in production:
 - nginx-abc123: Running
 - api-def456: Running"
```

The LLM decides which function to call, the function executes real code, and the LLM presents the results.

---

## Building the Python Functions

The key to FunctionTool is writing good Python functions. Here's what matters:

### 1. Docstrings Are Critical

The docstring becomes the tool description that the LLM sees. A good docstring helps the LLM know **when** to use the tool and **how**.

```python
def check_pod_status(namespace: str = "default") -> dict:
    """Check the status of pods in a Kubernetes namespace.

    Use this tool when the user wants to see what pods are running,
    check pod health, or troubleshoot pod issues.

    Args:
        namespace: The Kubernetes namespace to check. Defaults to "default".

    Returns:
        dict with "output" containing pod information in JSON format,
        and "error" if any errors occurred.
    """
```

Notice:
- **First line**: What the function does
- **"Use this tool when"**: Helps LLM decide when to call it
- **Args**: Clear parameter descriptions with defaults
- **Returns**: What the LLM will receive back

### 2. Type Hints Matter

Type hints tell the LLM what types of arguments to provide:

```python
def get_gcp_instance(instance_name: str, zone: str, project: str) -> dict:
```

The LLM sees: "I need to provide three strings: instance_name, zone, and project."

### 3. Error Handling is Essential

Your function runs in the real world. Things fail. Handle it gracefully:

```python
def check_pod_status(namespace: str = "default") -> dict:
    """Check the status of pods in a Kubernetes namespace."""
    try:
        result = subprocess.run(
            ["kubectl", "get", "pods", "-n", namespace, "-o", "json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.stderr else None
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out after 30 seconds"}
    except FileNotFoundError:
        return {"success": False, "error": "kubectl not found. Is it installed?"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}
```

The LLM can then explain the error to the user intelligently.

---

## The Four Tools

Let me show you all four functions we're building:

### 1. Check Pod Status

```python
def check_pod_status(namespace: str = "default") -> dict:
    """Check the status of pods in a Kubernetes namespace.

    Use this tool when the user wants to see what pods are running,
    check pod health, or troubleshoot pod issues.
    """
    try:
        result = subprocess.run(
            ["kubectl", "get", "pods", "-n", namespace, "-o", "json"],
            capture_output=True, text=True, timeout=30
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.stderr else None
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out"}
    except FileNotFoundError:
        return {"success": False, "error": "kubectl not found"}
```

### 2. Get GCP Instance

```python
def get_gcp_instance(instance_name: str, zone: str, project: str) -> dict:
    """Get details of a GCP Compute Engine VM instance.

    Use this tool when the user wants to see VM details like status,
    machine type, IP addresses, or other instance configuration.
    """
    try:
        result = subprocess.run(
            ["gcloud", "compute", "instances", "describe", instance_name,
             "--zone", zone, "--project", project, "--format", "json"],
            capture_output=True, text=True, timeout=30
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.stderr else None
        }
    except FileNotFoundError:
        return {"success": False, "error": "gcloud not found"}
```

### 3. Scale Deployment (with Safety!)

```python
def scale_deployment(deployment: str, replicas: int, namespace: str = "default") -> dict:
    """Scale a Kubernetes deployment to the specified number of replicas.

    IMPORTANT: This modifies infrastructure. Always confirm with user first.

    Use this tool when the user wants to scale up or scale down a deployment.
    """
    # Safety check!
    if replicas < 0 or replicas > 100:
        return {
            "success": False,
            "message": f"Replicas must be between 0 and 100. Got: {replicas}"
        }

    try:
        result = subprocess.run(
            ["kubectl", "scale", "deployment", deployment,
             f"--replicas={replicas}", "-n", namespace],
            capture_output=True, text=True, timeout=30
        )
        return {
            "success": result.returncode == 0,
            "message": result.stdout if result.returncode == 0 else result.stderr
        }
    except FileNotFoundError:
        return {"success": False, "message": "kubectl not found"}
```

Notice the **safety limit**: 0-100 replicas. Never let an AI scale to infinity!

### 4. Check Service Health

```python
def check_service_health(url: str, timeout: int = 5) -> dict:
    """Check if an HTTP service endpoint is healthy and responding.

    Use this tool when the user wants to verify if a service is up,
    check response times, or troubleshoot connectivity issues.
    """
    if not url.startswith(("http://", "https://")):
        return {"healthy": False, "error": "URL must start with http:// or https://"}

    try:
        response = requests.get(url, timeout=timeout)
        return {
            "healthy": response.status_code == 200,
            "status_code": response.status_code,
            "response_time_ms": round(response.elapsed.total_seconds() * 1000, 2)
        }
    except requests.Timeout:
        return {"healthy": False, "error": f"Timed out after {timeout} seconds"}
    except requests.ConnectionError:
        return {"healthy": False, "error": "Connection failed"}
```

---

## Wrapping Functions with FunctionTool

Now for the magic. We wrap our functions with `FunctionTool`:

```python
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from .tools import (
    check_pod_status,
    get_gcp_instance,
    scale_deployment,
    check_service_health
)

# Explicitly wrap as FunctionTool
root_agent = Agent(
    name="devops_runtime_assistant",
    model="gemini-2.0-flash",
    description="DevOps assistant that executes real infrastructure commands",

    tools=[
        FunctionTool(func=check_pod_status),
        FunctionTool(func=get_gcp_instance),
        FunctionTool(func=scale_deployment),
        FunctionTool(func=check_service_health)
    ],

    instruction="""
You are a DevOps Runtime Assistant with access to real infrastructure.

AVAILABLE TOOLS:
1. check_pod_status - Get pod status in a Kubernetes namespace
2. get_gcp_instance - Get details of a GCP Compute Engine VM
3. scale_deployment - Scale a Kubernetes deployment (MODIFIES INFRASTRUCTURE)
4. check_service_health - Check if an HTTP endpoint is responding

GUIDELINES:
- Always use the appropriate tool instead of guessing answers
- For scaling operations, ALWAYS confirm with the user before executing
- If a tool returns an error, explain what went wrong and suggest fixes

SAFETY:
- Never scale to more than 100 replicas
- Always show what you're about to do before doing it
"""
)
```

That's it! `FunctionTool(func=my_function)` wraps any Python function as a tool.

---

## Example Conversations

### Checking Pods

```
You: What pods are running in the production namespace?
    ↓
Agent thinks: "I should use check_pod_status"
    ↓
Agent calls: check_pod_status("production")
    ↓
Python executes: kubectl get pods -n production -o json
    ↓
Returns: {"success": true, "output": "NAME  READY  STATUS..."}
    ↓
Agent: Here are the pods in production:
       - nginx-7b8d9c5f6-abc12: Running (1/1 ready)
       - api-server-xyz789: Running (1/1 ready)
       - redis-master-0: Running (1/1 ready)
```

The agent ran a **real command** and got **real output**!

### Scaling with Confirmation

```
You: Scale nginx to 5 replicas
    ↓
Agent: I'll scale the nginx deployment to 5 replicas in the default namespace.
       This will create 4 new pods. Should I proceed?
    ↓
You: Yes, go ahead
    ↓
Agent calls: scale_deployment("nginx", 5, "default")
    ↓
Python executes: kubectl scale deployment nginx --replicas=5 -n default
    ↓
Returns: {"success": true, "message": "deployment.apps/nginx scaled"}
    ↓
Agent: Done! Successfully scaled nginx to 5 replicas.
```

Notice: The agent asked for confirmation before modifying infrastructure. This is crucial!

### Health Check

```
You: Is https://api.example.com/health responding?
    ↓
Agent calls: check_service_health("https://api.example.com/health")
    ↓
Python executes: requests.get("https://api.example.com/health")
    ↓
Returns: {"healthy": true, "status_code": 200, "response_time_ms": 127.5}
    ↓
Agent: The endpoint is healthy!
       - Status: 200 OK
       - Response time: 127.5ms
```

---

## When to Use FunctionTool vs AgentTool

Here's my decision framework:

### Use FunctionTool When:
- ✅ You need to **execute real code** (commands, API calls, queries)
- ✅ You want **deterministic results** (same input = same output)
- ✅ **Speed matters** (no LLM call overhead)
- ✅ The output is **structured data** (JSON, numbers, status codes)
- ✅ You're building **infrastructure tools** (kubectl, gcloud, terraform)

### Use AgentTool When:
- ✅ You need **LLM reasoning** to generate a response
- ✅ The task requires **creativity or interpretation**
- ✅ Output is **natural language** (explanations, summaries)
- ✅ You want to **chain multiple agents** for complex tasks

### Combining Both

You can use both in the same agent! Imagine:
- `FunctionTool` to run `kubectl get pods` and get raw data
- `AgentTool` to analyze the data and explain what's wrong

---

## Safety Considerations

FunctionTool gives your agent real power. With great power comes great responsibility:

### 1. Input Validation
```python
if replicas < 0 or replicas > 100:
    return {"error": "Invalid replica count"}
```

### 2. Confirmation for Destructive Actions
```
instruction="For scaling operations, ALWAYS confirm with the user before executing"
```

### 3. Timeouts
```python
subprocess.run(..., timeout=30)
```

### 4. Least Privilege
Configure `kubectl` and `gcloud` with minimal required permissions.

### 5. Audit Logging
Consider logging all tool invocations for security review.

---

## What I Learned

1. **Docstrings are documentation for the LLM** - Write them as if explaining to a colleague when to use this function.

2. **Type hints guide the LLM** - They help the LLM provide correct argument types.

3. **Error handling is user-facing** - The LLM will explain errors to users, so make error messages helpful.

4. **Safety limits are essential** - Never trust user input (even through an LLM) for destructive operations.

5. **FunctionTool completes the picture** - AgentTool thinks, FunctionTool does. Together, they're powerful.

---

## Final Thoughts

We've come full circle! From simple "hello world" agents in Part 1 to sophisticated systems that can:
- Remember user context (Part 2)
- Run complex workflows (Part 3)
- Route requests dynamically (Part 4)
- Orchestrate specialists as tools (Part 5)
- Execute real infrastructure commands (Part 6)

The patterns build on each other. Once you understand the fundamentals, you can combine them in countless ways.

Now go build your own AI agent systems! Whether it's a DevOps assistant, a research bot, or something entirely new - you have all the tools you need.

Happy coding! 🚀

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
```

---

## Resources

- Google ADK Documentation
- Pydantic for Structured Output
- Python AsyncIO for Runners

---

*Thanks for reading! Connect with me if you build something cool with ADK!*
