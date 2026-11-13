> 📁 **Source Code**: [Google ADK Cookbook](https://github.com/pranavdhopey/ADK-Agent-Basics.git)  
> 📖 **Full Series Index**: [Blog Directory](README.md)

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

---

<div align="between">
  <span>[← Previous: Part 4: Multi-Agent Systems - The Router Pattern](part-04-multi-agent-systems.md)</span> | <span>[Next: Part 6: FunctionTool - Giving Agents Real Power →](part-06-function-tool.md)</span>
</div>
