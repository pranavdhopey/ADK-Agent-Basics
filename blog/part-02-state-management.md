> 📁 **Source Code**: [Google ADK Cookbook](https://github.com/pranavdhopey/ADK-Agent-Basics.git)  
> 📖 **Full Series Index**: [Blog Directory](README.md)

---

# Part 2: State Management - Teaching Your Agent to Remember

📁 **Code**: [GitHub Repository](https://github.com/pranavdhopey/ADK-Agent-Basics.git)

> **TL;DR**: Learn how agents can remember context across conversations using tools with `ToolContext`, `Runner`, and `InMemorySessionService`. Build a Stateful Greeting Agent that stores user names in session state.

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

**Important:** To actually write to session state, we need **tools with ToolContext**. Instructions alone won't modify `session.state`!

First, let's define the tools:

```python
from google.adk.tools import ToolContext

def save_user_name(name: str, tool_context: ToolContext):
    """Saves the user's name to session state."""
    tool_context.state["user_name"] = name
    return f"✅ Saved '{name}' to state successfully!"

def get_user_name(tool_context: ToolContext) -> str:
    """Retrieves the user's name from session state."""
    user_name = tool_context.state.get("user_name", "")
    if user_name:
        return f"Found user_name in state: {user_name}"
    else:
        return "No user_name found in state yet."
```

Now, let's create the agent with these tools:

```python
from google.adk.agents import Agent

root_agent = Agent(
    name="stateful_greeting_agent",
    model="gemini-2.0-flash",
    description="A greeting agent that remembers your name",
    tools=[save_user_name, get_user_name],  # Tools for state management!
    instruction="""
    You are a friendly assistant that uses STATE MANAGEMENT.

    You have two tools to manage state:
    1. get_user_name() - Check if user's name is in state
    2. save_user_name(name) - Save user's name to state

    Rules:
    - ALWAYS call get_user_name() first to check
    - If empty, ask for their name
    - When user provides name, call save_user_name(name) immediately
    - Use the stored name to greet them personally
    """
)
```

The tools use `tool_context.state` to directly read and write to the session state dictionary. This is the key to making state management actually work!

### The Runner Code

Here's where the magic happens:

```python
import uuid
import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agent import root_agent

APP_NAME = "Greeting Bot"
USER_ID = "user_001"
SESSION_ID = str(uuid.uuid4())

async def main():
    # 1. Create a session service (in-memory for now)
    session_service = InMemorySessionService()

    # 2. Create a unique session for this user
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state={}  # Start with empty state
    )

    print(f"Session created: {session.id}")

    # 3. Create the runner
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
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
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=message,
        ):
            if event.is_final_response():
                # Check if content exists (tool calls may not have text)
                if event.content and event.content.parts and event.content.parts[0].text:
                    print(f"Agent: {event.content.parts[0].text}")
        
        # Print state after each turn to verify it's being updated
        current_state = await session_service.get_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID
        )
        print(f"📊 Current State: {current_state.state}")

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
    user_id=USER_ID,
    session_id=SESSION_ID,
    new_message=message,
):
    if event.is_final_response():
        # Important: Check for content before accessing
        if event.content and event.content.parts and event.content.parts[0].text:
            print(f"Agent: {event.content.parts[0].text}")
```
When you run the agent, you provide the user and session IDs. The runner automatically loads the state, lets the agent use it (and call tools!), and saves any changes.

**Important note**: We check if `event.content` exists because when the agent calls tools, the event might not have text content. This prevents errors.

**5. Checking State After Each Turn**
```python
current_state = await session_service.get_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID
)
print(f"📊 Current State: {current_state.state}")
```
This prints the state dictionary after each turn, so you can verify that the tools are actually writing to state. Very helpful for debugging!

### Now Let's See It Work!

```
Session created: abc-123-def-456

You: Hello!
Agent: Hey there! I don't think we've met yet. What's your name?
📊 Current State: {}

You: I'm Alex
Agent: Nice to meet you, Alex! I'll remember that. How can I help you today?
📊 Current State: {'user_name': 'Alex'}

You: What's my name?
Agent: Your name is Alex! See, I've got a good memory!
📊 Current State: {'user_name': 'Alex'}

You: Hi again
Agent: Hey Alex! Good to see you again!
📊 Current State: {'user_name': 'Alex'}
```

It remembers! The magic is that after "I'm Alex," the agent **called the `save_user_name("Alex")` tool**, which wrote `{user_name: "Alex"}` to the session state dictionary. Every subsequent message has access to that state.

### State vs Context - Important Distinction!

I was confused about this at first, so let me clarify:

**Context** = The conversation history (automatic)
```
["User: Hello", "Agent: Hey there!", "User: I'm Alex", ...]
```
The AI sees all previous messages. But parsing this to find the user's name is inefficient.

**State** = Structured data you explicitly store via tools (manual)
```python
{user_name: "Alex", theme: "dark", language: "en"}
```
Fast to access, easy to query, explicitly controlled, **programmatically accessible**.

**Why use State?**
- Faster: Direct lookup vs searching conversation
- Structured: Clean data vs messy text
- Controlled: You decide what to remember
- Persistent: Survives beyond context window limits
- **Programmatic**: Can use `session.state["user_name"]` in your code!

### What I Learned

1. **Tools are required for state management** - Instructions alone don't write to `session.state`. You need tools with `ToolContext`!

2. **tool_context.state is the key** - Use `tool_context.state` (not `tool_context.session.state`) for proper state access.

3. **State is powerful** - Once I understood state, I started seeing use cases everywhere: shopping carts, user preferences, form progress, game scores...

4. **Session = User context** - Each session is like a separate notebook for that user. Perfect for multi-user applications.

5. **InMemorySessionService is for development** - It's fast and easy, but everything disappears when you restart. Use database-backed sessions for real apps.

6. **The Runner is the orchestrator** - It handles the complexity of loading state, running the agent (and tools!), and saving updates.

---

## Recap: Part 1 + Part 2 Concepts

| Part | Feature | What It Does |
|------|---------|--------------|
| 1 | `instruction` | Defines agent personality |
| 1 | `tools` | External capabilities (search, etc.) |
| 1 | `output_schema` | Structured JSON output |
| 2 | Tools (for state) | Custom tools with ToolContext to read/write state |
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

---

<div align="between">
  <span>[← Previous: Part 1: The Basics - Your First AI Agents](part-01-the-basics.md)</span> | <span>[Next: Part 3: Workflow Agents - Building Agent Teams →](part-03-workflow-agents.md)</span>
</div>
