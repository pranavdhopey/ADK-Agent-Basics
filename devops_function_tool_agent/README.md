# DevOps Function Tool Agent - Real Infrastructure Access

## What Does This Agent Do?

This is a **DevOps Runtime Assistant** that can execute **real infrastructure commands** on your systems. Unlike agents that just generate commands (like the DevOps Copilot), this agent actually **runs** the commands and returns real results.

It demonstrates **FunctionTool** - the ability to wrap Python functions as tools that an LLM can call.

**What it can do:**
- Check pod status in Kubernetes clusters (runs `kubectl get pods`)
- Get GCP VM instance details (runs `gcloud compute instances describe`)
- Scale Kubernetes deployments (runs `kubectl scale`)
- Check HTTP endpoint health (makes real HTTP requests)

**Key difference from AgentTool:**
- `AgentTool` wraps another Agent (uses LLM to generate response)
- `FunctionTool` wraps a Python function (executes real code)

## Google ADK Features Used

### FunctionTool - Python Functions as Tools

The core feature demonstrated is converting Python functions into tools:

```python
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

def check_pod_status(namespace: str = "default") -> dict:
    """Check pod status in a Kubernetes namespace.

    Use this tool when the user wants to see what pods are running,
    check pod health, or troubleshoot pod issues.

    Args:
        namespace: The Kubernetes namespace to check. Defaults to "default".

    Returns:
        dict with "output" containing pod information in JSON format.
    """
    result = subprocess.run(
        ["kubectl", "get", "pods", "-n", namespace, "-o", "json"],
        capture_output=True, text=True, timeout=30
    )
    return {"success": result.returncode == 0, "output": result.stdout, "error": result.stderr}

# Explicitly wrap as FunctionTool
pod_tool = FunctionTool(func=check_pod_status)

# Use in Agent
agent = Agent(
    tools=[
        FunctionTool(func=check_pod_status),
        FunctionTool(func=get_gcp_instance),
        # ... more tools
    ],
    ...
)
```

**Key points:**
- **Docstrings** become tool descriptions (helps LLM know when to use it)
- **Type hints** define parameter types (helps LLM provide correct arguments)
- **Return values** are passed back to the LLM

### How It Works

```
User: "Check pods in the production namespace"
    │
    ▼
┌─────────────────────────────────────────────┐
│         DevOps Runtime Agent                │
│                                             │
│  LLM analyzes request and decides:          │
│  "I should call check_pod_status"           │
│                                             │
│  LLM calls: check_pod_status("production")  │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│         Python Function Executes            │
│                                             │
│  subprocess.run(["kubectl", "get", "pods",  │
│                  "-n", "production", ...])  │
│                                             │
│  Returns: {"output": "NAME  READY...", ...} │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│         LLM Receives Result                 │
│                                             │
│  "Here are your pods in production:         │
│   - nginx-abc123: Running                   │
│   - api-def456: Running"                    │
└─────────────────────────────────────────────┘
```

## Available Tools

### 1. check_pod_status
**Purpose**: Get Kubernetes pod status in a namespace

```python
def check_pod_status(namespace: str = "default") -> dict:
    """Check pod status in a Kubernetes namespace."""
    ...
```

**Example usage:**
```
User: "What pods are running in the staging namespace?"
Agent: [Calls check_pod_status("staging")]
Agent: "Here are the pods in staging: ..."
```

### 2. get_gcp_instance
**Purpose**: Get details of a GCP Compute Engine VM

```python
def get_gcp_instance(instance_name: str, zone: str, project: str) -> dict:
    """Get details of a GCP VM instance."""
    ...
```

**Example usage:**
```
User: "Get info about the web-server-1 VM in us-central1-a, project my-project"
Agent: [Calls get_gcp_instance("web-server-1", "us-central1-a", "my-project")]
Agent: "The VM is a n1-standard-2, status: RUNNING, IP: 10.0.0.5"
```

### 3. scale_deployment
**Purpose**: Scale a Kubernetes deployment

```python
def scale_deployment(deployment: str, replicas: int, namespace: str = "default") -> dict:
    """Scale a Kubernetes deployment to specified replicas."""
    ...
```

**Example usage:**
```
User: "Scale the nginx deployment to 5 replicas"
Agent: "I'll scale nginx to 5 replicas. Please confirm."
User: "Yes"
Agent: [Calls scale_deployment("nginx", 5)]
Agent: "Successfully scaled nginx to 5 replicas."
```

### 4. check_service_health
**Purpose**: Check if an HTTP endpoint is healthy

```python
def check_service_health(url: str, timeout: int = 5) -> dict:
    """Check if a service endpoint is healthy."""
    ...
```

**Example usage:**
```
User: "Is https://api.example.com/health responding?"
Agent: [Calls check_service_health("https://api.example.com/health")]
Agent: "The endpoint is healthy. Status: 200, Response time: 45ms"
```

## Key ADK Concepts in This Example

| Feature | What It Does | Used In This Agent |
|---------|-------------|-------------------|
| **FunctionTool** | Wraps Python functions as LLM tools | ✅ Yes - All 4 functions explicitly wrapped |
| **Agent** | Core AI component | ✅ Yes - 1 agent |
| **tools** | External capabilities | ✅ Yes - 4 FunctionTools |
| **instruction** | Behavior guidance | ✅ Yes |
| **description** | Brief summary for tool selection | ✅ Yes |
| **Type hints** | Define parameter types | ✅ Yes - All functions |
| **Docstrings** | Tool descriptions for LLM | ✅ Yes - Comprehensive docstrings |
| **Error handling** | Graceful failure handling | ✅ Yes - try/except blocks |

## Code Structure

```
devops_function_tool_agent/
├── agent.py              # Main agent with FunctionTools
├── tools.py              # Python functions (kubectl, gcloud, http)
├── __init__.py           # Package exports
├── requirements.txt      # Dependencies (google-adk, requests)
├── .env                  # Environment variables
└── README.md             # This file
```

## FunctionTool vs AgentTool - When to Use Which

| Feature | FunctionTool | AgentTool |
|---------|--------------|-----------|
| **Wraps** | Python function | Another Agent |
| **Execution** | Runs real code | Uses LLM reasoning |
| **Speed** | Fast (no LLM call) | Slower (LLM call) |
| **Use case** | API calls, CLI commands, calculations | Complex reasoning, text generation |
| **Deterministic** | Yes (same input → same output) | No (LLM may vary) |

**Use FunctionTool when:**
- You need to run actual commands (kubectl, gcloud, etc.)
- You're calling APIs or databases
- You need deterministic results
- Speed matters

**Use AgentTool when:**
- You need LLM reasoning or creativity
- The task requires understanding context
- Output is text/explanation, not structured data

## Running the Agent

### Prerequisites
- `kubectl` configured with cluster access
- `gcloud` CLI authenticated
- Python dependencies installed

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run with ADK
```bash
adk run devops_function_tool_agent
```

### Example session
```
You: Check pods in the default namespace
Agent: [Executes kubectl get pods -n default]
Agent: Here are your pods:
       - nginx-7b8d9c5f6-abc12: Running (1/1 ready)
       - redis-5d4c3b2a1-def34: Running (1/1 ready)

You: Scale nginx to 3 replicas
Agent: I'll scale the nginx deployment to 3 replicas. This will create 2 new pods.
       Should I proceed?

You: Yes
Agent: [Executes kubectl scale deployment nginx --replicas=3]
Agent: Successfully scaled nginx to 3 replicas.

You: Check if https://myapp.com/health is up
Agent: [Makes HTTP request to https://myapp.com/health]
Agent: The endpoint is healthy!
       - Status: 200 OK
       - Response time: 127ms
```

## Security Considerations

This agent executes **real commands** on your infrastructure. Be aware:

1. **Authentication**: Ensure `kubectl` and `gcloud` are configured with appropriate (limited) permissions
2. **Confirmation**: The instruction tells the agent to confirm before scaling - this is important!
3. **Audit trail**: Consider logging all tool invocations
4. **Rate limiting**: The agent could make many requests rapidly
5. **Input validation**: URLs and names should be validated

## Official Documentation

Learn more about the ADK features used in this agent:

| Feature | Documentation Link |
|---------|-------------------|
| **Tools Overview** | [ADK Tools Documentation](https://google.github.io/adk-docs/tools/) |
| **Function Tools** | [Function Tools Guide](https://google.github.io/adk-docs/tools/function-tools/) |
| **Custom Function Tools** | [Building Custom Function Tools](https://google.github.io/adk-docs/tools-custom/function-tools/) |
| **Built-in Tools** | [Built-in Tools](https://google.github.io/adk-docs/tools/built-in-tools/) |
| **Tool Authentication** | [Tool Authentication](https://google.github.io/adk-docs/tools/authentication/) |
| **LLM Agents** | [LLM Agents Documentation](https://google.github.io/adk-docs/agents/llm-agents/) |

## What You'll Learn

By studying this agent, you'll understand:
1. **FunctionTool** - How to explicitly wrap Python functions as LLM tools
2. **Real infrastructure access** - How agents can execute actual commands
3. **Docstrings as descriptions** - Why good docstrings matter for tool selection
4. **Type hints** - How type annotations help the LLM provide correct arguments
5. **Error handling** - Graceful failure with try/except and meaningful error messages
6. **Safety considerations** - Why confirmation prompts and limits (0-100 replicas) are important
7. **FunctionTool vs AgentTool** - When to use each pattern

---

**Beginner Tip**: FunctionTool is incredibly powerful - it lets your AI agent actually DO things, not just talk about them. Use `FunctionTool(func=your_function)` to explicitly wrap functions, and write comprehensive docstrings since they become the tool description the LLM sees. But with great power comes great responsibility! Always add confirmation steps for actions that modify infrastructure, include error handling, and use the principle of least privilege for credentials.
