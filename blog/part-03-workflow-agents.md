> 📁 **Source Code**: [Google ADK Cookbook](https://github.com/pranavdhopey/ADK-Agent-Basics.git)  
> 📖 **Full Series Index**: [Blog Directory](README.md)

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

### When to Use Sequential

Use SequentialAgent when:
- Steps **depend on each other** (Step 2 needs Step 1's output)
- You need a **pipeline** with clear data flow
- The order of execution **matters**

Don't use when:
- Steps are independent (that's parallel)
- You need dynamic routing based on input (that's a router agent)

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

### When to Use Loop

Use LoopAgent when:
- Output needs **iterative improvement** (generate → validate → fix)
- Quality can be **checked programmatically** (validation rules)
- You want **self-correcting** behavior without human intervention

Don't use when:
- A single pass is good enough (that's sequential)
- There's no clear **exit condition** (you'll hit max_iterations every time)
- Tasks are independent and don't build on each other (that's parallel)

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

## Recap: Workflow Agent Types

| Agent | Pattern | Example | Key Insight |
|-------|---------|---------|-------------|
| Sequential | A → B → C | Command Helper | Order matters, pass data via state |
| Parallel | A + B + C | Multi-Cloud Advisor | Independent tasks, 3x faster |
| Loop | [A → B] repeat | YAML Generator | Iterate until quality is met |

You can even **combine** them like we did with the Multi-Cloud Advisor (Parallel inside Sequential)!

---

### What I Learned

1. **One agent can't do everything well** - Splitting tasks across specialists dramatically improves output quality. A dedicated validator will always catch more issues than an all-in-one agent.

2. **State is the glue** - `output_key` is what connects agents in workflows. Without it, agents can't pass data to each other.

3. **Order matters in Sequential, not in Parallel** - If tasks depend on each other, use Sequential. If they're independent, Parallel gives you a speed boost.

4. **Loops need an escape hatch** - Always set `max_iterations` and provide an explicit `exit_loop` tool. Without these, your agent will loop forever.

5. **You can nest workflows** - Parallel inside Sequential (or any combo) opens up powerful patterns. Think of them as building blocks you can stack.

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

---

<div align="between">
  <span>[← Previous: Part 2: State Management - Teaching Your Agent to Remember](part-02-state-management.md)</span> | <span>[Next: Part 4: Multi-Agent Systems - The Router Pattern →](part-04-multi-agent-systems.md)</span>
</div>
