# Multi-Agent System - Router Pattern

## What Does This Agent Do?

This is a **multi-agent system** that intelligently routes user requests to specialized agents. Instead of one agent trying to handle everything, a **router agent** analyzes incoming messages and delegates them to the right specialist:

- **Greeting Agent** → Handles casual hellos and friendly conversation
- **Incident Analysis Agent** → Analyzes technical problems and provides structured reports

Think of it as a company reception desk:
1. You walk in and say something
2. The receptionist (router) listens and understands your intent
3. They direct you to the right department (specialist agent)
4. The specialist handles your request completely

**Key benefit**: Each agent is focused and specialized, resulting in better quality responses than a single "do-everything" agent.

## Google ADK Features Used

This agent demonstrates the **multi-agent routing pattern** with several important ADK features:

### 🔀 Sub-Agents and Routing
The router agent has `sub_agents` - specialized agents it can delegate to:

```python
root_agent = Agent(
    name="router_agent",
    sub_agents=[
        greeting_agent,
        incident_analysis_agent
    ],
    instruction="Route based on keywords..."
)
```

**How routing works:**
1. User sends a message to the router
2. Router's LLM analyzes the message content
3. Router calls `transfer_to_agent(agent_name='specialist_name')`
4. ADK intercepts this and hands control to the specialist
5. Specialist completes the task and responds

### 🚫 Transfer Control (Preventing Loops)
Sub-agents use transfer control to prevent infinite loops:

```python
agent = Agent(
    name="greeting_agent",
    disallow_transfer_to_parent=True,   # Can't transfer back to router
    disallow_transfer_to_peers=True,    # Can't transfer to incident_agent
    ...
)
```

**Why this matters:**
Without transfer control, you might get:
```
User: "Hello"
Router → Greeting Agent → Router → Greeting Agent → ... (infinite loop!)
```

With transfer control, agents become **terminal nodes** - they complete their task and stop.

### 📊 Structured Output (output_schema)
The incident analysis agent returns validated JSON using Pydantic:

```python
class IncidentReport(BaseModel):
    incident_summary: str = Field(description="...")
    severity: Literal["low", "medium", "high", "critical"]
    affected_components: List[str]
    probable_cause: str
    immediate_actions: List[str]

agent = Agent(
    output_schema=IncidentReport,
    ...
)
```

**Benefits:**
- Guaranteed structure (always same fields)
- Type validation (severity must be one of 4 values)
- Easy integration with APIs, databases, dashboards

### 💾 State Management (output_key)
Both agents store their outputs in session state:

```python
# Greeting agent
agent = Agent(
    output_key="greeting_response",
    ...
)

# Incident agent
agent = Agent(
    output_key="incident_report",
    ...
)
```

**State after interactions:**
```python
{
    "greeting_response": "Hey there! Nice to meet you!",
    "incident_report": {"severity": "high", "affected_components": [...], ...}
}
```

### 🗂️ Session Service
The `run_agent.py` script uses session management for persistent conversations:

```python
session_service = InMemorySessionService()

session = await session_service.create_session(
    app_name="Incident Copilot",
    user_id="user_1",
    session_id=SESSION_ID,
    state={}
)

runner = Runner(
    agent=root_agent,
    session_service=session_service,
)
```

This enables:
- Multi-turn conversations
- State persistence across messages
- User-specific sessions

## How It Works

### Routing Flow

```
User Message
    │
    ▼
┌─────────────────────────────────────────────────┐
│              Router Agent                        │
│                                                  │
│  Analyzes message for keywords:                  │
│  • Technical terms? → incident_analysis_agent    │
│  • Just greeting? → greeting_agent               │
│  • Unclear? → Ask for clarification              │
└─────────────────────────────────────────────────┘
    │
    ├─── "hello" ──────────────────┐
    │                              ▼
    │                    ┌──────────────────┐
    │                    │  Greeting Agent  │
    │                    │  (terminal)      │
    │                    └────────┬─────────┘
    │                             │
    │                    "Hey! What's your name?"
    │
    └─── "my server is down" ─────┐
                                  ▼
                        ┌──────────────────────┐
                        │ Incident Analysis    │
                        │ Agent (terminal)     │
                        └──────────┬───────────┘
                                   │
                          Structured JSON Report
```

### Example Conversations

**Greeting Flow:**
```
You: hello
Agent: Hey there! Great to see you! I'm your friendly assistant.
       What's your name?

You: I'm Alex
Agent: Nice to meet you, Alex! How can I brighten your day?
```

**Incident Flow:**
```
You: my GKE pods are crashing with OOMKilled errors

Agent: {
  "incident_summary": "GKE pods terminating due to memory exhaustion (OOMKilled)",
  "severity": "high",
  "affected_components": ["GKE pods", "Application containers", "Cluster resources"],
  "probable_cause": "Container memory limits too low or memory leak in application",
  "immediate_actions": [
    "Check pod resource limits with kubectl describe pod",
    "Review application memory usage patterns",
    "Increase memory limits in deployment spec",
    "Check for memory leaks in application code",
    "Monitor with kubectl top pods"
  ]
}
```

**Fallback Flow:**
```
You: asdfgh
Agent: I'd be happy to help! Are you reporting a technical issue,
       or just saying hello?
```

## Routing Rules

The router uses keyword-based routing:

### Route to `incident_analysis_agent` if message contains:

| Category | Keywords |
|----------|----------|
| Problems | issue, problem, error, failed, down, broken, crash, outage, timeout |
| Connectivity | connect, connecting, unable to, can't access, unreachable |
| Cloud/Infra | GKE, GCP, GCE, AWS, Azure, VM, server, cluster, container, pod |
| Networking | VPC, subnet, firewall, DNS, load balancer, ingress |
| Data | database, SQL, Redis, storage, backup, replication |
| DevOps | deployment, YAML, helm, terraform, CI/CD, pipeline |
| Environment | onprem, on-premise, production, staging |

### Route to `greeting_agent` if message is ONLY:
- hello, hi, hey, good morning, good afternoon, how are you, what's up

### Fallback (router asks for clarification):
- Message doesn't fit either category
- Intent is unclear

## Key ADK Concepts in This Example

| Feature | What It Does | Used In This Agent |
|---------|-------------|-------------------|
| **Sub-Agents** | Specialists the router can delegate to | ✅ Yes - greeting + incident agents |
| **Transfer Control** | Prevents infinite agent loops | ✅ Yes - `disallow_transfer_to_parent/peers` |
| **output_schema** | Enforces structured JSON output | ✅ Yes - `IncidentReport` model |
| **output_key** | Stores agent output in state | ✅ Yes - Both sub-agents |
| **Literal Type** | Validates enum-like values | ✅ Yes - Severity levels |
| **Session Service** | Manages conversation sessions | ✅ Yes - `InMemorySessionService` |
| **Runner** | Executes agent with session support | ✅ Yes - In `run_agent.py` |

## Sub-Agents Explained

### 1. Router Agent (root_agent)
**Purpose**: Analyzes messages and delegates to specialists

```python
root_agent = Agent(
    name="router_agent",
    sub_agents=[greeting_agent, incident_analysis_agent],
    instruction=ROUTER_INSTRUCTION
)
```

**Responsibilities:**
- Parse user intent from message content
- Match against routing rules
- Delegate to appropriate specialist
- Handle fallback (unclear messages)

### 2. Greeting Agent
**Purpose**: Handles casual greetings warmly

```python
agent = Agent(
    name="greeting_agent",
    output_key="greeting_response",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    ...
)
```

**Features:**
- State-aware (remembers user's name)
- Friendly, casual tone with light humor
- Terminal agent (doesn't transfer to others)

### 3. Incident Analysis Agent
**Purpose**: Analyzes technical problems and provides structured reports

```python
agent = Agent(
    name="incident_analysis_agent",
    output_schema=IncidentReport,
    output_key="incident_report",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    ...
)
```

**Features:**
- Returns validated JSON with Pydantic
- Severity classification (low/medium/high/critical)
- Actionable troubleshooting steps
- Terminal agent (doesn't transfer to others)

## Code Structure

```
multi_agent/
├── agent.py                              # Router agent definition
├── run_agent.py                          # Interactive runner script
├── __init__.py                           # Exports root_agent
├── .env                                  # Environment variables
├── README.md                             # This file
└── sub_agents/
    ├── __init__.py                       # Exports all sub-agents
    ├── greeting_agent/
    │   ├── agent.py                      # Greeting specialist
    │   ├── __init__.py                   # Exports agent
    │   └── README.md                     # Greeting agent docs
    └── incident_analysis_agent/
        ├── agent.py                      # Incident specialist + IncidentReport
        └── __init__.py                   # Exports agent + model
```

## Running the Agent

### Interactive Mode

```bash
cd multi_agent
python run_agent.py
```

**Example session:**
```
Session created: abc-123-def-456
Type 'exit' to quit

You: hello
Agent: Hey there! Welcome! I don't think we've met - what's your name?

You: I'm Sarah
Agent: Nice to meet you, Sarah! How can I help you today?

You: my database connection is timing out
Agent: {
  "incident_summary": "Database connection timeout issues",
  "severity": "high",
  ...
}

You: exit
Goodbye!
```

### Programmatic Usage

```python
from multi_agent import root_agent
from multi_agent.sub_agents import IncidentReport

# Use with your own runner/session setup
response = root_agent.run("my server is down")
```

## Error Handling

The `run_agent.py` includes robust error handling:

```python
try:
    # Process message
    for event in runner.run(...):
        if event.is_final_response():
            print(event.content.parts[0].text)
except KeyboardInterrupt:
    print("Interrupted. Goodbye!")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
```

**Handles:**
- Empty input validation
- Missing response content
- API errors
- Keyboard interrupts (Ctrl+C)
- Multiple exit commands (`exit`, `quit`, `q`)

## Best Practices Demonstrated

### 1. Externalized Instructions
Router instruction is stored in a constant for maintainability:
```python
ROUTER_INSTRUCTION = """..."""
root_agent = Agent(instruction=ROUTER_INSTRUCTION)
```

### 2. Explicit Routing Rules
Keywords and examples make routing predictable:
```python
# Good: Explicit keywords
"If message contains: issue, error, server, down → incident_analysis_agent"

# Bad: Vague
"Route technical stuff to incident agent"
```

### 3. Terminal Agents
Sub-agents don't transfer back, preventing loops:
```python
disallow_transfer_to_parent=True
disallow_transfer_to_peers=True
```

### 4. Validated Output
Using `Literal` ensures severity is always valid:
```python
severity: Literal["low", "medium", "high", "critical"]
```

## Extending This System

### Adding a New Specialist

1. Create the agent:
```python
# sub_agents/search_agent/agent.py
agent = Agent(
    name="search_agent",
    description="Searches the web for information",
    tools=[google_search],
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)
```

2. Register with router:
```python
# agent.py
from .sub_agents.search_agent.agent import agent as search_agent

root_agent = Agent(
    sub_agents=[greeting_agent, incident_analysis_agent, search_agent],
    ...
)
```

3. Update routing rules:
```python
ROUTER_INSTRUCTION = """
...
RULE 3 - SEARCH (use search_agent):
If user asks for current information, news, or facts:
- "what's the weather", "latest news", "search for"
→ delegate to: search_agent
"""
```

## Official Documentation

Learn more about the ADK features used in this agent:

| Feature | Documentation Link |
|---------|-------------------|
| **Multi-Agent Systems** | [Multi-Agents Documentation](https://google.github.io/adk-docs/agents/multi-agents/) |
| **Agent Team Tutorial** | [Building Agent Teams](https://google.github.io/adk-docs/tutorials/agent-team/) |
| **LLM Agents** | [LLM Agents Documentation](https://google.github.io/adk-docs/agents/llm-agents/) |
| **Sessions & State** | [Sessions Documentation](https://google.github.io/adk-docs/sessions/) |
| **Runtime & Runners** | [Runtime Documentation](https://google.github.io/adk-docs/runtime/) |
| **Custom Tools** | [Building Custom Tools](https://google.github.io/adk-docs/tools-custom/) |

## What You'll Learn

By studying this agent, you'll understand:
1. **Multi-agent routing** - How to build router + specialist patterns
2. **Transfer control** - Preventing infinite loops between agents
3. **Structured output** - Using Pydantic for validated JSON responses
4. **Session management** - Maintaining state across conversations
5. **Keyword-based routing** - Making routing predictable and reliable
6. **Error handling** - Building robust agent applications

---

**Beginner Tip**: The router pattern is one of the most powerful patterns in multi-agent systems! It lets you build modular, specialized agents that work together. Start with 2-3 specialists, then add more as needed. The key is: **clear routing rules** (explicit keywords) and **terminal agents** (no transfer loops). This pattern scales well - you can add many specialists without changing the architecture!
