# Stateful Greeting Agent

## What Does This Agent Do?

This agent is a friendly greeter that **remembers your name** across multiple conversations. Unlike a basic chatbot that forgets everything after each message, this agent uses **state management with tools** to store information (like your name) and recall it in future interactions.

Think of it as a receptionist with a good memory who:
- Asks for your name on the first visit
- Stores your name in memory using dedicated tools
- Greets you by name on every future interaction
- Maintains this memory throughout the entire conversation session

**Key difference from stateless agents**: Regular agents forget everything between messages. This agent **remembers** using persistent state that you can access programmatically.

## Google ADK Features Used

This agent demonstrates several important **state management and session** features of the Google Agent Development Kit (ADK):

### 🛠️ Tools with ToolContext

The agent uses **custom tools** to read and write session state. This is the critical component that enables true state management:

```python
from google.adk.tools import ToolContext

def save_user_name(name: str, tool_context: ToolContext):
    """Saves the user's name into the session state."""
    tool_context.state["user_name"] = name
    return f"✅ Saved '{name}' to state successfully!"

def get_user_name(tool_context: ToolContext) -> str:
    """Retrieves the user's name from the session state."""
    user_name = tool_context.state.get("user_name", "")
    if user_name:
        return f"Found user_name in state: {user_name}"
    else:
        return "No user_name found in state yet."
```

**How it works:**
- The agent calls **tools** to read from and write to state
- `tool_context.state` provides direct access to the session state dictionary
- State changes are automatically persisted by ADK's event system
- The state is accessible programmatically in your code

**⚠️ Important**: You must use `tool_context.state` directly, not `tool_context.session.state`, to ensure proper ADK event tracking and state persistence.

**Why this matters**: Simply instructing an agent to "remember" or "store in state" doesn't actually write to `session.state`. You need tools that explicitly modify the state dictionary.

### 💾 State Management

The agent stores data in **session.state**, which persists across message turns within the same session:

```python
root_agent = Agent(
    name="stateful_greeting_agent",
    tools=[save_user_name, get_user_name],
    instruction="""
    You have two tools to manage state:
    1. get_user_name() - Check if user's name is already in state
    2. save_user_name(name) - Save the user's name to state
    
    Rules:
    - ALWAYS call get_user_name() first to check if you already know the user's name
    - When the user provides their name, call save_user_name(name) to store it
    - Use the stored name to greet them personally
    """
)
```

**How state works:**
- The agent **calls tools** to interact with state
- Tools **write to** `tool_context.state["key"]` to save data
- Tools **read from** `tool_context.state.get("key")` to retrieve data
- State persists across messages within the same session

### 🗂️ Session Service

Sessions allow you to maintain state across an entire conversation. The `InMemorySessionService` stores session data in memory.

```python
from google.adk.sessions import InMemorySessionService

session_service = InMemorySessionService()

# Create a session with initial state
session = await session_service.create_session(
    app_name="Greeting Bot",
    user_id="user_001",
    session_id=SESSION_ID,
    state={}  # Start with empty state
)
```

**What this provides:**
- Each user gets a unique session
- State is tied to the session
- Multiple users can interact simultaneously with isolated states

### 🏃 Runner

The `Runner` class executes your agent with full session support, handling state automatically.

```python
from google.adk.runners import Runner

runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)

# Run the agent with session context
for event in runner.run(
    user_id=USER_ID,
    session_id=SESSION_ID,
    new_message=message,
):
    if event.is_final_response():
        print("Agent:", event.content.parts[0].text)
```

**Benefits:**
- Automatically manages state across message turns
- Handles session lifecycle
- Provides streaming event support
- Works with any session service (in-memory, database, etc.)

### 📋 Session Lifecycle

1. **Create Session**: Initialize a new conversation with empty state
2. **Run Agent**: Agent calls tools to read/write state during conversation
3. **Persist State**: Tools update state via `tool_context.state`
4. **Recall State**: Next message has access to updated state

## How It Works

Here's a complete conversation flow showing state in action:

```
Turn 1:
You: "Hello!"
    ↓
Agent calls: get_user_name()
Tool returns: "No user_name found in state yet."
State: {}  (empty)
    ↓
Agent: "Hi there! I'd love to get to know you. What's your name?"

Turn 2:
You: "My name is Sarah"
    ↓
Agent calls: save_user_name("Sarah")
Tool executes: tool_context.state["user_name"] = "Sarah"
Tool returns: "✅ Saved 'Sarah' to state successfully!"
State: {user_name: "Sarah"}  ← Agent stored the name!
    ↓
Agent: "Nice to meet you, Sarah! How can I help you today?"

Turn 3:
You: "What's my name?"
    ↓
Agent calls: get_user_name()
Tool executes: tool_context.state.get("user_name")
Tool returns: "Found user_name in state: Sarah"
State: {user_name: "Sarah"}  ← State persists!
    ↓
Agent: "Your name is Sarah!"
```

### Without Tools (Using Only Conversation History):

```
You: "My name is Sarah"
Agent: "Nice to meet you, Sarah!"
State: {}  ← Still empty! Agent found name in conversation history

[Later in same conversation]
You: "What's my name?"
Agent: "Your name is Sarah!"  ← Found by searching context
State: {}  ← Still empty! Not in state dictionary
```

**Problem**: Can't use `session.state["user_name"]` in your code for integrations, APIs, or databases.

### With Tools (True State Management):

```
You: "My name is Sarah"
Agent calls: save_user_name("Sarah")
State: {user_name: "Sarah"}  ← Actually stored!

[Later in same conversation]
You: "What's my name?"
Agent calls: get_user_name()
State: {user_name: "Sarah"}  ← Available programmatically!
```

**Benefit**: You can use `session.state["user_name"]` in your code!

## When to Use This Agent

Perfect for:
- **Multi-turn conversations**: Chatbots that need to remember context
- **Personalized experiences**: Greeting users by name, remembering preferences
- **Learning state management**: Understanding how to build stateful AI agents with tools
- **Session-based applications**: Customer support, onboarding flows, interactive tutorials

Example use cases:
- Customer support bot that remembers issue details
- Onboarding assistant that tracks user progress
- Personal assistant that learns user preferences
- Interactive game that maintains player state

Not needed for:
- Single-turn Q&A (no context needed)
- Stateless API endpoints
- Simple greetings without personalization

## Key ADK Concepts in This Example

| Feature | What It Does | Used In This Agent |
|---------|-------------|-------------------|
| **Agent** | The core AI component | ✅ Yes - `Agent` class |
| **Tools** | Functions the agent can call | ✅ Yes - `save_user_name`, `get_user_name` |
| **ToolContext** | Provides access to session state | ✅ Yes - `tool_context.state` |
| **State Management** | Stores data across conversation turns | ✅ Yes - `user_name` in state |
| **Session Service** | Manages session lifecycle and storage | ✅ Yes - `InMemorySessionService` |
| **Runner** | Executes agent with session support | ✅ Yes - `Runner` class |
| **Model** | The AI model powering the agent | ✅ Yes - `gemini-2.0-flash` |
| **Instruction** | Guides state read/write behavior | ✅ Yes - Tool usage instructions |

## Running the Agent

### Using the Included Script

This agent includes a `run_agent.py` script that sets up everything:

```bash
python run_agent.py
```

**Interactive session:**
```
Created session: abc-123-def-456

You: Hello!
Agent: Hi there! I'd love to get to know you. What's your name?
📊 Current State: {}

You: My name is Alex
Agent: Nice to meet you, Alex!
📊 Current State: {'user_name': 'Alex'}

You: What's my name?
Agent: Your name is Alex!
📊 Current State: {'user_name': 'Alex'}

You: exit
```

### Using ADK Web UI

Start the ADK dev server pointing to the parent directory:

```bash
adk web
```

This opens a browser UI where you can select and chat with the agent interactively. The **State tab** on the left will show session state updating in real-time!

### Code Breakdown (run_agent.py)

```python
# 1. Create session service (in-memory storage)
session_service = InMemorySessionService()

# 2. Create a new session
session = await session_service.create_session(
    app_name="Greeting Bot",
    user_id="user_001",
    session_id=SESSION_ID,
    state={}  # Empty state to start
)

# 3. Create runner with agent and session service
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)

# 4. Run agent with session context
for event in runner.run(
    user_id=USER_ID,
    session_id=SESSION_ID,
    new_message=message,
):
    if event.is_final_response():
        print("Agent:", event.content.parts[0].text)

# 5. Check state after each turn
current_state = await session_service.get_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID
)
print(f"📊 Current State: {current_state.state}")
```

## Session Service Types

ADK supports multiple session storage backends:

| Service Type | Storage | Use Case |
|--------------|---------|----------|
| **InMemorySessionService** | RAM (temporary) | Development, testing, demos |
| **DatabaseSessionService** | Persistent DB | Production apps, multi-user systems |
| **Custom Session Service** | Your implementation | Specialized storage needs |

This example uses `InMemorySessionService` for simplicity. For production, you'd use a database-backed service to persist state across server restarts.

## Code Structure

```
stateful_greeting_agent/
├── agent.py          # Agent definition with state management tools
├── run_agent.py      # Runner script with session management
├── __init__.py       # Package initialization
├── .env              # Environment variables (API keys, etc.)
└── README.md         # This file
```

## Official Documentation

Learn more about the ADK features used in this agent:

| Feature | Documentation Link |
|---------|-------------------|
| **Sessions Overview** | [Sessions Documentation](https://google.github.io/adk-docs/sessions/) |
| **State Management** | [State Management Guide](https://google.github.io/adk-docs/sessions/state/) |
| **Session Management** | [Session Guide](https://google.github.io/adk-docs/sessions/session/) |
| **Memory** | [Memory Documentation](https://google.github.io/adk-docs/sessions/memory/) |
| **Runtime & Runners** | [Runtime Documentation](https://google.github.io/adk-docs/runtime/) |
| **Event Loop** | [Event Loop Guide](https://google.github.io/adk-docs/runtime/event-loop/) |

## What You'll Learn

By studying this agent, you'll understand:
1. **Tools with ToolContext** - How to create functions that read/write state
2. **True state management** - The difference between context-based and tool-based state
3. **State access patterns** - Why `tool_context.state` matters
4. **Session services** - Managing conversation sessions with unique IDs
5. **Runner usage** - Executing agents with full session support
6. **Async operations** - Using `asyncio` for session creation
7. **Event handling** - Processing streaming responses from agents

## State vs Context

**Important distinction:**

- **Context**: The conversation history (messages back and forth)
  - Automatically managed by ADK
  - Contains all previous messages
  
- **State**: Structured data you explicitly store using tools
  - Manually managed via `tool_context.state`
  - Contains specific values like `user_name`, `preferences`, etc.
  - More efficient than parsing conversation history
  - Programmatically accessible in your code

**Example:**
```python
# Context (automatic):
["User: My name is Jack", "Agent: Nice to meet you!", ...]

# State (explicit via tools):
{user_name: "Jack", language: "en", theme: "dark"}
```

State is **faster to access** and **easier to query** than searching through context. Plus, you can use it in your application code for integrations!

---

**Beginner Tip**: State management with tools is essential for building **real conversational AI**! The key takeaway: **Instructions alone don't write to state** - you need tools that explicitly call `tool_context.state["key"] = value`. Start with simple key-value pairs (like `user_name`), then expand to more complex data (user preferences, cart items, form progress, etc.). The `InMemorySessionService` is perfect for learning, but switch to a database-backed service for production apps.
