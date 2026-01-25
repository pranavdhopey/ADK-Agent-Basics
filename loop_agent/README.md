# Loop Agent - Kubernetes YAML Generator

## What Does This Agent Do?

This agent generates **perfect Kubernetes YAML manifests** by iteratively improving them until they meet all best practices. Instead of generating YAML once and hoping it's good, this agent uses a **validate-and-fix loop** to ensure production-quality output.

Think of it as having a team of Kubernetes experts:
1. **Generator**: Creates the first draft of your YAML
2. **Validator**: Checks for issues and best practice violations
3. **Fixer**: Corrects the problems
4. **Loop continues** until the YAML is perfect or max iterations reached

**Key difference from single-pass agents**: Regular agents generate output once. This agent **iteratively improves** until quality standards are met.

## Google ADK Features Used

This agent demonstrates advanced **workflow orchestration** features of the Google Agent Development Kit (ADK):

### 🔄 LoopAgent
The `LoopAgent` runs a sequence of sub-agents repeatedly until a condition is met or max iterations is reached.

```python
from google.adk.agents import LoopAgent

improve_loop = LoopAgent(
    name="yaml_improvement_loop",
    sub_agents=[
        validator,  # Check for issues
        fixer       # Fix issues
    ],
    max_iterations=3,
    description="Iteratively validates and improves Kubernetes YAML..."
)
```

**How it works:**
- **Iteration 1**: Validator checks YAML → Fixer corrects issues
- **Iteration 2**: Validator checks again → Fixer corrects new issues
- **Iteration 3**: Validator checks → If still not perfect, stops at max_iterations
- **Early exit**: If Validator approves, loop terminates immediately

### 🎯 SequentialAgent
The `SequentialAgent` runs sub-agents in order, one after another.

```python
from google.adk.agents import SequentialAgent

root_agent = SequentialAgent(
    name="k8s_yaml_helper",
    sub_agents=[
        generator,      # Step 1: Generate first draft
        improve_loop    # Step 2: Improve until valid
    ],
    description="Generates and iteratively improves Kubernetes YAML manifests..."
)
```

**Flow:**
1. Generator creates initial YAML → Outputs to `yaml_draft`
2. Improve loop takes `yaml_draft` → Validates and fixes repeatedly

### 🛠️ Custom Tools (Exit Loop)
The validator uses a **custom tool** to signal when the YAML is perfect and the loop should terminate early.

```python
from google.adk.tools.tool_context import ToolContext

def exit_loop(tool_context: ToolContext):
    """Call this function ONLY when the YAML is perfect and meets all best practices."""
    print(f"[exit_loop] Triggered by {tool_context.agent_name} - YAML approved")
    tool_context.actions.escalate = True  # ← Terminates the loop
    tool_context.actions.skip_summarization = True
    return {"status": "approved"}

agent = Agent(
    name="yaml_validator",
    tools=[exit_loop],  # ← Custom tool for loop control
    # ...
)
```

**What this does:**
- `tool_context.actions.escalate = True`: Tells the LoopAgent to stop immediately
- Without this tool, the loop would always run max_iterations even if YAML is perfect

### 🔗 State Management with output_key
Each agent stores its output in shared state using `output_key`, allowing downstream agents to reference it.

```python
# Generator creates initial YAML
agent = Agent(
    name="yaml_generator",
    output_key="yaml_draft",  # ← Stores output here
    # ...
)

# Validator reads from yaml_draft
agent = Agent(
    name="yaml_validator",
    output_key="validation_result",  # ← Stores validation output
    instruction="Validate the Kubernetes YAML manifest from {yaml_draft}..."  # ← Reads yaml_draft
)

# Fixer reads validation_result and updates yaml_draft
agent = Agent(
    name="yaml_fixer",
    output_key="yaml_draft",  # ← Updates the yaml_draft
    instruction="Fix the Kubernetes YAML based on the validation feedback from {validation_result}..."
)
```

## How It Works

Here's the complete flow when you request a Kubernetes deployment:

```
User: "Create a Kubernetes deployment for an nginx web server"
    ↓
[STEP 1: Generator]
    ↓
Generator creates initial YAML draft
State: {yaml_draft: "apiVersion: apps/v1\nkind: Deployment..."}
    ↓
[STEP 2: Improvement Loop - Iteration 1]
    ↓
Validator checks yaml_draft
Issues found:
  - Missing resource limits
  - No readiness probe
  - Using :latest tag
State: {validation_result: "NEEDS IMPROVEMENT: Missing resource limits..."}
    ↓
Fixer corrects issues
State: {yaml_draft: "...with resource limits, probes, specific tag..."}
    ↓
[STEP 2: Improvement Loop - Iteration 2]
    ↓
Validator checks updated yaml_draft
Issues found:
  - Missing security context
State: {validation_result: "NEEDS IMPROVEMENT: Missing security context"}
    ↓
Fixer adds security context
State: {yaml_draft: "...with security context..."}
    ↓
[STEP 2: Improvement Loop - Iteration 3]
    ↓
Validator checks yaml_draft
No issues found! ✅
Validator calls exit_loop() tool
State: {validation_result: "APPROVED - YAML meets all best practices"}
    ↓
Loop terminates early (before max_iterations)
    ↓
Final YAML returned to user
```

## Best Practices Enforced

The validator checks for Kubernetes best practices:

✅ **Resource Management**
- CPU and memory requests and limits
- Prevents resource exhaustion

✅ **Health Checks**
- readinessProbe (when pod is ready for traffic)
- livenessProbe (when to restart pod)

✅ **Labels**
- app, version, component labels
- Essential for service discovery and monitoring

✅ **Security**
- runAsNonRoot (don't run as root user)
- readOnlyRootFilesystem (prevent file modifications)

✅ **Image Best Practices**
- Avoid `:latest` tag (use specific versions)
- Set imagePullPolicy explicitly

## When to Use This Agent

Perfect for:
- **Generating production-ready Kubernetes manifests**: Ensure best practices automatically
- **Learning LoopAgent**: Understanding iterative improvement workflows
- **Quality assurance**: Validate and fix until perfect
- **DevOps automation**: Generate consistent, validated YAML

Example requests:
- "Create a Kubernetes deployment for a Python Flask app"
- "Generate a StatefulSet for PostgreSQL"
- "Create a complete manifest for a microservice with database"

Not needed for:
- Simple one-off YAML generation without validation
- Non-Kubernetes YAML
- Tasks that don't benefit from iterative improvement

## Key ADK Concepts in This Example

| Feature | What It Does | Used In This Agent |
|---------|-------------|-------------------|
| **LoopAgent** | Runs sub-agents repeatedly until condition met | ✅ Yes - Validate-fix loop |
| **SequentialAgent** | Runs sub-agents in order | ✅ Yes - Generate then improve |
| **Custom Tools** | Agent-specific capabilities | ✅ Yes - `exit_loop` function |
| **ToolContext** | Provides loop control actions | ✅ Yes - `escalate` to exit loop |
| **output_key** | Stores agent output in shared state | ✅ Yes - `yaml_draft`, `validation_result` |
| **State Variables** | Reference other agents' outputs | ✅ Yes - `{yaml_draft}`, `{validation_result}` |
| **max_iterations** | Limits loop iterations | ✅ Yes - Set to 3 |

## Sub-Agents Explained

### 1. Generator (yaml_generator)
**Purpose**: Creates the initial Kubernetes YAML draft

```python
agent = Agent(
    name="yaml_generator",
    output_key="yaml_draft",
    instruction="Generate Kubernetes YAML manifests based on the user's request..."
)
```

**Input**: User's request (e.g., "Create a deployment for nginx")
**Output**: First draft YAML stored in `yaml_draft`

### 2. Validator (yaml_validator)
**Purpose**: Checks YAML for best practice violations

```python
agent = Agent(
    name="yaml_validator",
    tools=[exit_loop],  # Can terminate loop if perfect
    output_key="validation_result",
    instruction="Validate the Kubernetes YAML manifest from {yaml_draft}..."
)
```

**Input**: Reads `{yaml_draft}` from state
**Output**: Either "APPROVED" or "NEEDS IMPROVEMENT: [issues]"
**Special**: Calls `exit_loop()` tool when YAML is perfect

### 3. Fixer (yaml_fixer)
**Purpose**: Corrects issues found by validator

```python
agent = Agent(
    name="yaml_fixer",
    output_key="yaml_draft",  # Updates the draft
    instruction="Fix the Kubernetes YAML based on the validation feedback from {validation_result}..."
)
```

**Input**: Reads `{validation_result}` from state
**Output**: Corrected YAML, updates `yaml_draft` in state

## Loop Termination

The loop can end in two ways:

### 1. Early Exit (Perfect YAML)
```python
# Validator finds no issues
validator calls exit_loop()
    ↓
tool_context.actions.escalate = True
    ↓
LoopAgent terminates immediately
```

### 2. Max Iterations Reached
```python
# After 3 iterations
improve_loop = LoopAgent(
    max_iterations=3,
    # ...
)
# If still not perfect after 3 iterations, stops anyway
```

## Code Structure

```
loop_agent/
├── agent.py                  # Main LoopAgent and SequentialAgent setup
├── __init__.py               # Package initialization
├── .env                      # Environment variables (API keys, etc.)
├── README.md                 # This file
└── sub_agents/
    ├── generator.py          # Creates initial YAML draft
    ├── validator.py          # Validates YAML, has exit_loop tool
    └── fixer.py              # Fixes issues found by validator
```

## Running the Agent

```python
from loop_agent import root_agent

# Request Kubernetes YAML
response = root_agent.run("Create a deployment for a Redis cache with 3 replicas")

# The agent will:
# 1. Generate initial YAML
# 2. Validate it
# 3. Fix any issues
# 4. Repeat validation and fixing until perfect or max 3 iterations
# 5. Return production-ready YAML
```

## Workflow Diagram

```
┌─────────────────────────────────────────────┐
│         SequentialAgent (root)              │
│                                             │
│  ┌────────────┐      ┌─────────────────┐   │
│  │            │      │   LoopAgent     │   │
│  │ Generator  │──────▶│   (improve)     │   │
│  │            │      │                 │   │
│  └────────────┘      │  ┌───────────┐  │   │
│                      │  │ Validator │  │   │
│                      │  └─────┬─────┘  │   │
│                      │        │        │   │
│                      │        ▼        │   │
│                      │  ┌───────────┐  │   │
│                      │  │   Fixer   │  │   │
│                      │  └─────┬─────┘  │   │
│                      │        │        │   │
│                      │        │ Loop   │   │
│                      │        │ (max 3)│   │
│                      │        ▼        │   │
│                      │   exit_loop()?  │   │
│                      │   Yes: Exit     │   │
│                      │   No: Continue  │   │
│                      └─────────────────┘   │
└─────────────────────────────────────────────┘
```

## Official Documentation

Learn more about the ADK features used in this agent:

| Feature | Documentation Link |
|---------|-------------------|
| **Workflow Agents Overview** | [Workflow Agents Documentation](https://google.github.io/adk-docs/agents/workflow-agents/) |
| **Loop Agents** | [Loop Agents Guide](https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/) |
| **Sequential Agents** | [Sequential Agents Guide](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/) |
| **Custom Tools** | [Building Custom Tools](https://google.github.io/adk-docs/tools-custom/) |
| **Function Tools** | [Function Tools Guide](https://google.github.io/adk-docs/tools-custom/function-tools/) |
| **State Management** | [State Management Guide](https://google.github.io/adk-docs/sessions/state/) |

## What You'll Learn

By studying this agent, you'll understand:
1. **LoopAgent** - How to create iterative improvement workflows
2. **SequentialAgent** - Chaining agents in a specific order
3. **Custom tools** - Building tools with ToolContext for loop control
4. **Workflow composition** - Combining multiple agent types
5. **State management** - Using output_key and state variables
6. **Quality assurance** - Automated validation and correction

## Advanced: Why Use LoopAgent vs Regular Agent?

### Regular Agent (Single Pass):
```
User: "Create K8s deployment"
    ↓
Agent generates YAML
    ↓
Returns YAML (might have issues) ❌
```

### LoopAgent (Iterative):
```
User: "Create K8s deployment"
    ↓
Agent generates YAML
    ↓
Validate → Fix → Validate → Fix...
    ↓
Returns perfect YAML ✅
```

**Benefits:**
- **Higher quality**: Multiple validation passes catch more issues
- **Self-correcting**: Automatically fixes problems
- **Consistency**: Always meets best practices
- **Reliability**: Production-ready output

---

**Beginner Tip**: The LoopAgent is perfect for **quality-critical tasks** where you need to iterate until success. Common patterns: code generation with validation, document drafting with review loops, data processing with error correction. The key is having a **validator** that can check quality and a **fixer** that can improve the output!
