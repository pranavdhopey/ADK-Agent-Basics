# Sequential Agent - Command Helper

## What Does This Agent Do?

This agent is a **command-line helper** that generates properly formatted shell commands for Linux, Kubernetes, Google Cloud, and Docker. Instead of generating commands in one shot, it uses a **3-step pipeline** to ensure accuracy and proper formatting.

Think of it as a specialized assistant that:
1. **Understands** what tool you need (Linux, kubectl, gcloud, or Docker)
2. **Generates** the correct command syntax
3. **Formats** the output beautifully with syntax highlighting

**Key difference from single-agent approaches**: By breaking the task into specialized steps, each agent can focus on doing one thing well, resulting in better quality output.

## Google ADK Features Used

This agent demonstrates **sequential workflow orchestration** with state management in the Google Agent Development Kit (ADK):

### 📋 SequentialAgent
The `SequentialAgent` runs sub-agents in a specific order, one after another, passing data between them.

```python
from google.adk.agents import SequentialAgent

root_agent = SequentialAgent(
    name="command_helper_agent",
    sub_agents=[intent, cmd, fmt],  # Run in order: 1→2→3
    description="Generates properly formatted command-line commands through a 3-step process..."
)
```

**How it works:**
- **Step 1**: Intent agent classifies the tool type
- **Step 2**: Command generator creates the command
- **Step 3**: Formatter wraps it in markdown with syntax highlighting

Each step runs sequentially, with later steps accessing earlier results through state.

### 🔗 State Management with output_key
Each sub-agent stores its output in shared state using `output_key`, allowing downstream agents to reference it.

```python
# Step 1: Intent classification
agent = Agent(
    name="intent_agent",
    output_key="tool_type",  # ← Stores result as "tool_type"
    instruction="Respond with ONLY the category name: linux, kubectl, gcloud, or docker"
)

# Step 2: Command generation (references tool_type)
agent = Agent(
    name="command_generator",
    output_key="raw_command",  # ← Stores result as "raw_command"
    instruction="Generate the appropriate {tool_type} command..."  # ← Reads tool_type
)

# Step 3: Formatting (references both tool_type and raw_command)
agent = Agent(
    name="formatter",
    instruction="Format the command(s) using the tool type ({tool_type})..."  # ← Reads tool_type
    # Also implicitly accesses raw_command from previous step
)
```

**State flow:**
```
State after Step 1: {tool_type: "kubectl"}
State after Step 2: {tool_type: "kubectl", raw_command: "kubectl get pods"}
State after Step 3: {tool_type: "kubectl", raw_command: "kubectl get pods", <final output>}
```

### 🎯 Template Variables
Agents use `{variable_name}` syntax to reference state variables in their instructions.

```python
instruction="Generate the appropriate {tool_type} command for the user's request."
                                        ↑
                                Replaced with actual value from state
```

When the instruction is executed:
- `{tool_type}` → Replaced with "kubectl" (or "linux", "gcloud", "docker")
- Agent sees: "Generate the appropriate kubectl command for the user's request."

## How It Works

Here's the complete flow when you ask for a command:

```
User: "Show me all running pods in the default namespace"
    ↓
[STEP 1: Intent Classification]
    ↓
Intent agent analyzes request
Recognizes keywords: "pods" → Kubernetes
Output: "kubectl"
State: {tool_type: "kubectl"}
    ↓
[STEP 2: Command Generation]
    ↓
Command generator reads {tool_type} from state
Knows to generate a kubectl command
Output: "kubectl get pods"
State: {tool_type: "kubectl", raw_command: "kubectl get pods"}
    ↓
[STEP 3: Formatting]
    ↓
Formatter reads {tool_type} from state
Knows to use bash syntax highlighting
Creates markdown code block
Output:
"List all pods in the default namespace:
```bash
kubectl get pods
```"
    ↓
Final formatted response returned to user
```

## Why Use Sequential Steps?

### Single Agent Approach (Less Effective):
```
User: "Show all pods"
    ↓
Agent: Generates command + formats + explains all at once
    ↓
"You can use kubectl to get pods, here's the command: kubectl get pods"
```
Problems:
- Mixed quality (some parts good, some parts bad)
- Hard to ensure consistent formatting
- No specialization

### Sequential Agent Approach (This Agent):
```
User: "Show all pods"
    ↓
Step 1: Classify → "kubectl" ✅ Specialist in classification
Step 2: Generate → "kubectl get pods" ✅ Specialist in commands
Step 3: Format → Markdown code block ✅ Specialist in formatting
```
Benefits:
- Each agent does ONE thing well
- Consistent output format
- Easier to improve individual steps
- Better quality through specialization

## Supported Tool Categories

The intent agent classifies requests into 4 categories:

### 1. Linux
General Linux/bash commands:
- File operations: `ls`, `cat`, `grep`, `find`, `chmod`
- Text processing: `sed`, `awk`, `cut`, `sort`
- System: `ps`, `netstat`, `df`, `du`

**Example request**: "Find all .txt files in the current directory"
**Output**:
```bash
find . -name "*.txt"
```

### 2. kubectl
Kubernetes commands:
- Resources: `kubectl get`, `kubectl describe`
- Deployment: `kubectl apply`, `kubectl create`
- Debugging: `kubectl logs`, `kubectl exec`

**Example request**: "Get all pods in production namespace"
**Output**:
```bash
kubectl get pods -n production
```

### 3. gcloud
Google Cloud Platform CLI:
- Compute: `gcloud compute instances list`
- Kubernetes: `gcloud container clusters get-credentials`
- Storage: `gcloud storage buckets list`

**Example request**: "List all GCE instances"
**Output**:
```bash
gcloud compute instances list
```

### 4. docker
Docker commands:
- Containers: `docker run`, `docker ps`, `docker exec`
- Images: `docker build`, `docker pull`, `docker images`
- Compose: `docker compose up`, `docker compose down`

**Example request**: "List all running containers"
**Output**:
```bash
docker ps
```

## When to Use This Agent

Perfect for:
- **Learning commands**: Get properly formatted commands for common tasks
- **DevOps documentation**: Generate command examples automatically
- **Understanding SequentialAgent**: See how to chain agents together
- **State management practice**: Learn how agents share data through state

Example requests:
- "How do I list all files with details?"
- "Show me the logs for a pod named nginx"
- "Create a Docker container from an image"
- "Delete a GCP VM instance"

Not needed for:
- Natural language questions (use a QA agent instead)
- Tasks that don't involve shell commands
- Complex scripts (this generates single commands or simple sequences)

## Key ADK Concepts in This Example

| Feature | What It Does | Used In This Agent |
|---------|-------------|-------------------|
| **SequentialAgent** | Runs sub-agents in order | ✅ Yes - Intent → Command → Format |
| **output_key** | Stores agent output in shared state | ✅ Yes - `tool_type`, `raw_command` |
| **Template Variables** | Reference state in instructions | ✅ Yes - `{tool_type}` |
| **State Management** | Share data between agents | ✅ Yes - Each step reads previous outputs |
| **Agent** | Individual LLM-powered components | ✅ Yes - 3 specialized agents |
| **Model** | The AI model powering each agent | ✅ Yes - `gemini-2.0-flash` |
| **Description** | Brief summary of each agent | ✅ Yes - All agents have descriptions |

## Sub-Agents Explained

### 1. Intent Agent (intent_agent)
**Purpose**: Classifies which tool the user needs

```python
agent = Agent(
    name="intent_agent",
    output_key="tool_type",
    instruction="Determine which command-line tool they need..."
)
```

**Input**: User's request (e.g., "Show all pods")
**Output**: Tool category → `"kubectl"` (stored in `tool_type`)
**Categories**: linux, kubectl, gcloud, docker

### 2. Command Generator (command_generator)
**Purpose**: Creates the actual command syntax

```python
agent = Agent(
    name="command_generator",
    output_key="raw_command",
    instruction="Generate the appropriate {tool_type} command..."
)
```

**Input**:
- User's request
- `{tool_type}` from state (e.g., "kubectl")

**Output**: Raw command → `"kubectl get pods"` (stored in `raw_command`)

### 3. Formatter (formatter)
**Purpose**: Wraps command in markdown with syntax highlighting

```python
agent = Agent(
    name="formatter",
    instruction="Format the command(s) using the tool type ({tool_type})..."
)
```

**Input**:
- `{tool_type}` from state (e.g., "kubectl")
- `raw_command` from previous step

**Output**: Formatted markdown:
```
List all pods in the default namespace:
```bash
kubectl get pods
```
```

## Sequential vs Parallel vs Loop

ADK provides three workflow agent types:

| Agent Type | Execution | Use Case | This Example |
|------------|-----------|----------|--------------|
| **SequentialAgent** | One after another | Multi-step pipelines | ✅ Used here |
| **ParallelAgent** | All at once | Independent tasks | ❌ Not used |
| **LoopAgent** | Repeat until condition | Iterative improvement | ❌ Not used |

**Why Sequential?**
Each step depends on the previous one:
- Command generator needs to know tool_type from intent
- Formatter needs to know tool_type for syntax highlighting
- Order matters! Can't format before generating

## Code Structure

```
sequential_agent/
├── agent.py                      # Main SequentialAgent setup
├── __init__.py                   # Package initialization
├── .env                          # Environment variables (API keys, etc.)
├── README.md                     # This file
└── sub_agents/
    ├── intent.py                 # Step 1: Classify tool type
    ├── command_gen.py            # Step 2: Generate command
    └── formatter.py              # Step 3: Format output
```

## Running the Agent

```python
from sequential_agent import root_agent

# Request a command
response = root_agent.run("Show me all Docker containers")

# The agent will:
# 1. Classify → "docker"
# 2. Generate → "docker ps"
# 3. Format → Markdown code block
```

**Example output:**
```
List all running Docker containers:
```bash
docker ps
```
```

## Workflow Diagram

```
┌─────────────────────────────────────────────┐
│       SequentialAgent (root_agent)          │
│                                             │
│  ┌──────────┐   ┌──────────┐   ┌─────────┐ │
│  │          │   │          │   │         │ │
│  │ Intent   │──▶│ Command  │──▶│ Format  │ │
│  │ Classify │   │ Generate │   │ Output  │ │
│  │          │   │          │   │         │ │
│  └──────────┘   └──────────┘   └─────────┘ │
│       │               │              │      │
│    output:         output:        output:   │
│   tool_type      raw_command    formatted   │
│                                             │
│  State flow:                                │
│  {}  →  {tool_type}  →  {tool_type,        │
│                          raw_command}       │
└─────────────────────────────────────────────┘
```

## Official Documentation

Learn more about the ADK features used in this agent:

| Feature | Documentation Link |
|---------|-------------------|
| **Workflow Agents Overview** | [Workflow Agents Documentation](https://google.github.io/adk-docs/agents/workflow-agents/) |
| **Sequential Agents** | [Sequential Agents Guide](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/) |
| **LLM Agents** | [LLM Agents Documentation](https://google.github.io/adk-docs/agents/llm-agents/) |
| **State Management** | [State Management Guide](https://google.github.io/adk-docs/sessions/state/) |
| **Agent Configuration** | [Agent Config Reference](https://google.github.io/adk-docs/agents/config/) |

## What You'll Learn

By studying this agent, you'll understand:
1. **SequentialAgent** - How to chain agents in a specific order
2. **output_key** - Storing results in shared state
3. **Template variables** - Referencing state with `{variable_name}`
4. **Pipeline design** - Breaking complex tasks into simple steps
5. **Specialization** - Each agent does one thing well
6. **State flow** - How data passes from agent to agent

## Advanced: Adding More Steps

Want to extend this agent? You can easily add more steps:

```python
from .sub_agents.validator import agent as validator

root_agent = SequentialAgent(
    name="command_helper_agent",
    sub_agents=[
        intent,      # Step 1: Classify
        cmd,         # Step 2: Generate
        validator,   # Step 3: Validate command ← NEW!
        fmt          # Step 4: Format
    ]
)
```

The validator could check if the command is safe before formatting!

---

**Beginner Tip**: Sequential workflows are like **assembly lines** - each agent is a specialist station that does one job perfectly. This pattern is powerful for multi-step tasks where order matters. Start simple (2-3 agents), then add more steps as needed. The key is: each agent should have a **clear, focused purpose** and store its result in state for the next agent!
