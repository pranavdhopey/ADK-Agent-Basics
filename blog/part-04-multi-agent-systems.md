> 📁 **Source Code**: [Google ADK Cookbook](https://github.com/pranavdhopey/ADK-Agent-Basics.git)  
> 📖 **Full Series Index**: [Blog Directory](README.md)

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

### What I Learned

1. **`sub_agents` is a handoff, not a call** - When the router transfers to a specialist, the specialist takes over completely. The router doesn't get the result back. This is great for simple delegation but limiting for orchestration.

2. **Routing instructions must be crystal clear** - Vague routing like "handle technical stuff" leads to misrouted requests. Be explicit: "If the user mentions pods, kubectl, or Kubernetes, transfer to kubectl_agent."

3. **`disallow_transfer_to_parent` prevents infinite loops** - Without it, specialists try to transfer back to the router, which transfers back to them, and so on. Always make specialists terminal.

4. **`output_key` stores agent responses** - Even in routed systems, use `output_key` so each specialist's response is stored in session state for later reference.

5. **Description matters for routing** - The router uses each specialist's `description` to decide who should handle the request. Write descriptions like you're explaining the agent's job to a new hire.

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

---

<div align="between">
  <span>[← Previous: Part 3: Workflow Agents - Building Agent Teams](part-03-workflow-agents.md)</span> | <span>[Next: Part 5: AgentTool - Turning Agents Into Tools →](part-05-agent-tool.md)</span>
</div>
