# DevOps Copilot Agent - Using Agents as Tools

## What Does This Agent Do?

This is a **DevOps Copilot** - a comprehensive assistant that helps with various DevOps tasks by delegating to specialized agents. Unlike multi-agent routing (where control transfers between agents), this copilot uses **AgentTool** to call specialist agents as tools and get results back.

Think of it as a senior DevOps engineer with a team of specialists on speed dial:
- Need a kubectl command? → Calls the **Kubectl Agent**
- Need a gcloud command? → Calls the **GCloud Agent**
- Got an error message? → Calls the **Error Explainer Agent**
- Need Kubernetes YAML? → Calls the **YAML Generator Agent**

**Key difference from sub_agents**: With `AgentTool`, the main agent stays in control. It calls the specialist, gets the result, and can continue processing. With `sub_agents`, control transfers completely to the specialist.

## Google ADK Features Used

This agent demonstrates **AgentTool** - one of the most powerful features in ADK for building composite agents:

### 🔧 AgentTool - Agents as Tools

The `AgentTool` class converts an Agent into a Tool that another agent can use:

```python
from google.adk.agents import Agent
from google.adk.tools import AgentTool

# Create a specialist agent
kubectl_agent = Agent(
    name="kubectl_agent",
    model="gemini-2.0-flash",
    description="Generates kubectl commands",
    instruction="Generate ONLY the kubectl command..."
)

# Convert it to a tool
kubectl_tool = AgentTool(agent=kubectl_agent)

# Use it in the main agent
root_agent = Agent(
    name="devops_copilot",
    tools=[kubectl_tool],  # Agent is now a tool!
    instruction="Use kubectl_agent for kubectl tasks..."
)
```

**How it works:**
1. User asks: "How do I list all pods?"
2. Main agent thinks: "This is a kubectl task"
3. Main agent calls `kubectl_tool` (which runs `kubectl_agent`)
4. `kubectl_agent` returns: `kubectl get pods`
5. Main agent receives the result and responds to user

### AgentTool vs Sub-Agents - When to Use Which?

| Feature | AgentTool | Sub-Agents |
|---------|-----------|------------|
| **Control flow** | Main agent stays in control | Control transfers to specialist |
| **Result handling** | Main agent gets result back | Specialist responds directly |
| **Chaining** | Can call multiple tools in sequence | One specialist handles request |
| **Post-processing** | Main agent can modify/combine results | Specialist has final say |
| **Use case** | Composite tasks, combining results | Routing to specialists |

**Use AgentTool when:**
- You want to combine results from multiple specialists
- The main agent needs to post-process results
- You're building a "command center" agent

**Use Sub-Agents when:**
- Each specialist handles the request completely
- No post-processing needed
- Building a router/dispatcher pattern

## How It Works

### Architecture

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

### Example Conversations

**Kubectl Task:**
```
You: How do I get all pods in the production namespace?
    ↓
Copilot: [Calls kubectl_tool]
    ↓
kubectl_agent returns: "kubectl get pods -n production"
    ↓
Copilot: Here's the command to list pods in production:
         kubectl get pods -n production
```

**GCloud Task:**
```
You: How do I list all GCE instances?
    ↓
Copilot: [Calls gcloud_tool]
    ↓
gcloud_agent returns: "gcloud compute instances list"
    ↓
Copilot: To list all GCE instances, run:
         gcloud compute instances list
```

**Error Explanation:**
```
You: What does "CrashLoopBackOff" mean in Kubernetes?
    ↓
Copilot: [Calls error_tool]
    ↓
error_agent returns: Explanation with cause, fix steps, commands
    ↓
Copilot: CrashLoopBackOff means your pod keeps crashing...
         Cause: ...
         Fix: ...
```

**YAML Generation:**
```
You: Create a deployment for nginx with 3 replicas
    ↓
Copilot: [Calls yaml_tool]
    ↓
yaml_agent returns: Complete YAML manifest
    ↓
Copilot: Here's the Kubernetes deployment:
         apiVersion: apps/v1
         kind: Deployment
         ...
```

## Specialist Agents

### 1. Kubectl Agent
**Purpose**: Generates kubectl CLI commands

```python
kubectl_agent = Agent(
    name="kubectl_agent",
    description="Generates kubectl commands only",
    output_key="kubectl_command",
    instruction="Generate ONLY the kubectl command..."
)
```

**Example outputs:**
- `kubectl get pods -n production`
- `kubectl describe deployment nginx`
- `kubectl logs -f pod/my-app`

### 2. GCloud Agent
**Purpose**: Generates gcloud CLI commands

```python
gcloud_agent = Agent(
    name="gcloud_agent",
    description="Generates gcloud CLI commands only",
    output_key="gcloud_command",
    instruction="Generate ONLY the gcloud command..."
)
```

**Example outputs:**
- `gcloud compute instances list`
- `gcloud container clusters get-credentials my-cluster`
- `gcloud iam service-accounts list`

### 3. Error Explainer Agent
**Purpose**: Explains infrastructure and cloud errors with actionable fixes

```python
class ErrorExplanation(BaseModel):
    error_name: str
    cause: str
    impact: str
    fix_steps: List[str]
    helpful_commands: List[str]
    prevention: str

error_agent = Agent(
    name="error_explainer_agent",
    description="Explains infra and cloud errors with fixes",
    output_key="error_explanation",
    output_schema=ErrorExplanation,
    instruction="Explain the error: cause, fix steps, commands..."
)
```

**Example inputs:**
- "What is CrashLoopBackOff?"
- "Error: permission denied when accessing GCS bucket"
- "ImagePullBackOff in my pod"

### 4. YAML Generator Agent
**Purpose**: Generates Kubernetes YAML manifests

```python
yaml_agent = Agent(
    name="k8s_yaml_generator",
    description="Generates Kubernetes YAML manifests",
    output_key="k8s_yaml",
    instruction="Generate Kubernetes YAML only..."
)
```

**Example outputs:**
- Deployments
- Services
- ConfigMaps
- Ingress resources

## When to Use This Agent

Perfect for:
- **DevOps daily tasks**: Quick command generation
- **Learning kubectl/gcloud**: Get commands with explanations
- **Troubleshooting**: Error explanations with fix steps
- **K8s manifest creation**: Generate YAML quickly
- **Understanding AgentTool**: See how agents can be tools

Example requests:
- "How do I scale a deployment to 5 replicas?"
- "Generate a ClusterIP service for my nginx deployment"
- "What does 'insufficient cpu' error mean?"
- "Create a ConfigMap from a file"

## Key ADK Concepts in This Example

| Feature | What It Does | Used In This Agent |
|---------|-------------|-------------------|
| **AgentTool** | Converts Agent to Tool | ✅ Yes - All 4 specialists |
| **Agent** | Core AI component | ✅ Yes - 5 agents total |
| **tools** | External capabilities | ✅ Yes - 4 AgentTools |
| **description** | Brief summary (important for tool selection!) | ✅ Yes - All agents |
| **instruction** | Behavior guidance | ✅ Yes - All agents |
| **output_key** | State management for results | ✅ Yes - All specialists |
| **output_schema** | Structured output with Pydantic | ✅ Yes - Error agent |

## Code Structure

```
devops_copilot_agent_tool/
├── agent.py                  # Main DevOps Copilot with AgentTools
├── __init__.py               # Package initialization
├── .env                      # Environment variables
├── README.md                 # This file
└── tools/
    ├── __init__.py           # Tools package exports
    ├── kubectl_agent.py      # Kubectl command generator (output_key: kubectl_command)
    ├── gcloud_agent.py       # GCloud command generator (output_key: gcloud_command)
    ├── error_agent.py        # Error explainer with structured output (output_key: error_explanation)
    └── yaml_agent.py         # K8s YAML generator (output_key: k8s_yaml)
```

## Running the Agent

```python
from devops_copilot_agent_tool import root_agent

# Ask for kubectl help
response = root_agent.run("How do I delete all pods in a namespace?")

# Ask for error explanation
response = root_agent.run("What does OOMKilled mean?")

# Generate YAML
response = root_agent.run("Create a deployment for redis with persistent storage")
```

## Official Documentation

Learn more about the ADK features used in this agent:

| Feature | Documentation Link |
|---------|-------------------|
| **Tools Overview** | [ADK Tools Documentation](https://google.github.io/adk-docs/tools/) |
| **Custom Tools** | [Building Custom Tools](https://google.github.io/adk-docs/tools-custom/) |
| **Function Tools** | [Function Tools Guide](https://google.github.io/adk-docs/tools-custom/function-tools/) |
| **LLM Agents** | [LLM Agents Documentation](https://google.github.io/adk-docs/agents/llm-agents/) |
| **Agent Configuration** | [Agent Config Reference](https://google.github.io/adk-docs/agents/config/) |

## What You'll Learn

By studying this agent, you'll understand:
1. **AgentTool** - How to convert agents into tools for other agents
2. **Composite agents** - Building agents that orchestrate other agents
3. **Tool selection** - How the main agent decides which tool to call
4. **Description importance** - Why good descriptions help tool selection
5. **Agent patterns** - When to use AgentTool vs Sub-Agents
6. **output_key** - Storing tool results in session state for later use
7. **output_schema** - Structured output using Pydantic models

## Comparison: AgentTool vs Sub-Agents vs Sequential

| Pattern | This Agent (AgentTool) | Multi-Agent (Sub-Agents) | Sequential Agent |
|---------|------------------------|--------------------------|------------------|
| **Flow** | Main calls tools | Router transfers control | Fixed pipeline |
| **Flexibility** | High (any tool anytime) | Medium (routing rules) | Low (fixed order) |
| **Post-processing** | ✅ Yes | ❌ No | ✅ Yes (each step) |
| **Best for** | Composite tasks | Routing/dispatch | Pipelines |

---

**Beginner Tip**: `AgentTool` is perfect when you want your main agent to stay "in charge" while delegating specific tasks. Think of it as a manager who assigns tasks to team members but reviews the results before presenting them. The key is writing good `description` fields - they help the main agent decide which tool to use!
