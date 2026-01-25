# Stateful Greeting Agent

## What Does This Agent Do?

This agent is a friendly greeter that **remembers your name** across multiple conversations. Unlike a basic chatbot that forgets everything after each message, this agent uses **state management** to store information (like your name) and recall it in future interactions.

Think of it as a receptionist with a good memory who:
- Asks for your name on the first visit
- Stores your name in memory
- Greets you by name on every future interaction
- Maintains this memory throughout the entire conversation session

**Key difference from stateless agents**: Regular agents forget everything between messages. This agent **remembers** using persistent state.

## Google ADK Features Used

This agent demonstrates several important **state management and session** features of the Google Agent Development Kit (ADK):

### 💾 State Management
The agent uses **conversation state** to store and retrieve information across multiple turns in a conversation.

```python
instruction="""
You are a friendly assistant.

Use conversation state to remember the user's name.

Rules:
- If the user's name is not in state, ask for it
- If the user provides their name, store it in state as `user_name`
- If `user_name` exists in state, greet the user using their name
"""
```

**How it works:**
- The agent can **read** from state: "What's the user's name?"
- The agent can **write** to state: "Store this name as `user_name`"
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
2. **Run Agent**: Agent reads/writes state during conversation
3. **Persist State**: State automatically saved after each turn
4. **Recall State**: Next message uses updated state

## How It Works

Here's a complete conversation flow showing state in action:

```
Turn 1:
You: "Hello!"
State: {}  (empty)
    ↓
Agent: "Hi there! I'd love to get to know you. What's your name?"
State: {}  (no update yet)

Turn 2:
You: "My name is Sarah"
State: {}
    ↓
Agent: "Nice to meet you, Sarah! How can I help you today?"
State: {user_name: "Sarah"}  ← Agent stored the name!

Turn 3:
You: "Hello again"
State: {user_name: "Sarah"}  ← State persists!
    ↓
Agent: "Welcome back, Sarah! Great to see you again!"
State: {user_name: "Sarah"}
```

### Without State (Regular Agent):
```
You: "My name is Sarah"
Agent: "Nice to meet you, Sarah!"

[Later in same conversation]
You: "What's my name?"
Agent: "I'm not sure, could you tell me?" ❌ Forgot!
```

### With State (This Agent):
```
You: "My name is Sarah"
Agent: "Nice to meet you, Sarah!"
State: {user_name: "Sarah"} stored

[Later in same conversation]
You: "What's my name?"
Agent: "Your name is Sarah!" ✅ Remembers!
```

## When to Use This Agent

Perfect for:
- **Multi-turn conversations**: Chatbots that need to remember context
- **Personalized experiences**: Greeting users by name, remembering preferences
- **Learning state management**: Understanding how to build stateful AI agents
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
| **State Management** | Stores data across conversation turns | ✅ Yes - `user_name` in state |
| **Session Service** | Manages session lifecycle and storage | ✅ Yes - `InMemorySessionService` |
| **Runner** | Executes agent with session support | ✅ Yes - `Runner` class |
| **Model** | The AI model powering the agent | ✅ Yes - `gemini-2.0-flash` |
| **Instruction** | Guides state read/write behavior | ✅ Yes - State usage instructions |

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

You: My name is Alex
Agent: Nice to meet you, Alex! How can I help you today?

You: What's my name?
Agent: Your name is Alex!

You: exit
```

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
```

## Session Service Types

ADK supports multiple session storage backends:

| Service Type | Storage | Use Case |
|--------------|---------|----------|
| **InMemorySessionService** | RAM (temporary) | Development, testing, demos |
| **Database Session Service** | Persistent DB | Production apps, multi-user systems |
| **Custom Session Service** | Your implementation | Specialized storage needs |

This example uses `InMemorySessionService` for simplicity. For production, you'd use a database-backed service to persist state across server restarts.

## Code Structure

```
stateful_greeting_agent/
├── agent.py          # Agent definition with state instructions
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
1. **State management** - How agents store and retrieve data across turns
2. **Session services** - Managing conversation sessions with unique IDs
3. **Runner usage** - Executing agents with full session support
4. **Async operations** - Using `asyncio` for session creation
5. **Event handling** - Processing streaming responses from agents

## State vs Context

**Important distinction:**

- **Context**: The conversation history (messages back and forth)
  - Automatically managed by ADK
  - Contains all previous messages

- **State**: Structured data you explicitly store
  - Manually managed by your agent
  - Contains specific values like `user_name`, `preferences`, etc.
  - More efficient than parsing conversation history

**Example:**
```python
# Context (automatic):
["User: My name is Jack", "Agent: Nice to meet you!", ...]

# State (explicit):
{user_name: "Jack", language: "en", theme: "dark"}
```

State is **faster to access** and **easier to query** than searching through context.

---

**Beginner Tip**: State management is essential for building **real conversational AI**! Start with simple key-value pairs (like `user_name`), then expand to more complex data (user preferences, cart items, form progress, etc.). The `InMemorySessionService` is perfect for learning, but switch to a database-backed service for production apps.
