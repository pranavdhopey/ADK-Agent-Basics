> 📁 **Source Code**: [Google ADK Cookbook](https://github.com/pranavdhopey/ADK-Agent-Basics.git)  
> 📖 **Full Series Index**: [Blog Directory](README.md)

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

---

<div align="between">
  <span>[← Previous: Part 5: AgentTool - Turning Agents Into Tools](part-05-agent-tool.md)</span> | <span>[Next: Part 7: Multi-Provider Support - Using LiteLLM with Google ADK →](part-07-litellm-multi-provider.md)</span>
</div>
