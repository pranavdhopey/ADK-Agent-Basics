# Incident Analysis Agent

## What Does This Agent Do?

This agent is a technical incident analyzer that takes descriptions of system problems, outages, or errors and produces a **structured incident report**. Instead of getting free-form text, you get a standardized JSON report with all the key details organized and ready to use.

Think of it as your on-call incident responder who:
- Listens to your problem description
- Analyzes the severity and impact
- Identifies which systems are affected
- Suggests the most likely root cause
- Recommends immediate actions to fix the issue

**Key difference from regular chatbots**: This agent returns **structured data** (JSON), not just conversational text. This makes it perfect for integrating into incident management systems, dashboards, or automated workflows.

## Google ADK Features Used

This agent demonstrates **structured output**, one of the most powerful features in Google ADK:

### 📊 Output Schema (Structured Output)
Instead of getting unpredictable free-form text, you can force your agent to return **structured, validated data** using Pydantic models.

```python
from pydantic import BaseModel, Field

class IncidentReport(BaseModel):
    incident_summary: str = Field(description="Summary of the incident")
    severity: str = Field(description="low, medium, high, or critical")
    affected_components: List[str]
    probable_cause: str
    immediate_actions: List[str]

agent = Agent(
    name="incident_analysis_agent",
    output_schema=IncidentReport,  # ← Agent MUST return this structure
    # ...
)
```

**What this means:**
- The agent's response will **always** match the `IncidentReport` structure
- You'll always get the same fields: `incident_summary`, `severity`, `affected_components`, etc.
- The data is **validated** - severity must be a string, affected_components must be a list, etc.
- No parsing needed - you get a clean Python object or JSON

### 🔍 Pydantic BaseModel
Pydantic is a data validation library. By inheriting from `BaseModel`, you define:
- **Field names**: `incident_summary`, `severity`, etc.
- **Field types**: `str`, `List[str]`, etc.
- **Field descriptions**: Helps the AI understand what each field should contain

```python
class IncidentReport(BaseModel):
    incident_summary: str = Field(description="Summary of the incident")
    severity: str = Field(description="low, medium, high, or critical")
    affected_components: List[str]  # Must be a list of strings
    probable_cause: str
    immediate_actions: List[str]  # Must be a list of strings
```

### 📝 Instruction with JSON Guidelines
The instruction guides the agent on **how** to fill the structured output:

```python
instruction="""
You are an Incident Analysis Assistant.

GUIDELINES:
- Determine the severity level: low, medium, high, or critical
- Identify all affected components or systems
- Suggest the most likely root cause
- Recommend clear and actionable immediate steps

IMPORTANT: Your response MUST be valid JSON matching this structure:
{
   "incident_summary": "...",
   "severity": "low | medium | high | critical",
   "affected_components": ["component1", "component2"],
   "probable_cause": "...",
   "immediate_actions": ["Action 1", "Action 2"]
}
"""
```

## How It Works

Here's the flow when you report an incident:

```
You: "Our GKE cluster can't connect to the Cloud SQL database.
      Getting connection timeout errors."
    ↓
Agent receives incident description
    ↓
Agent analyzes the problem
    ↓
Agent returns STRUCTURED JSON:
{
  "incident_summary": "GKE cluster unable to connect to Cloud SQL database with timeout errors",
  "severity": "high",
  "affected_components": ["GKE cluster", "Cloud SQL", "Network connectivity"],
  "probable_cause": "Firewall rules blocking traffic between GKE and Cloud SQL, or VPC peering misconfiguration",
  "immediate_actions": [
    "Check Cloud SQL authorized networks configuration",
    "Verify VPC firewall rules allow traffic from GKE node IPs",
    "Check Cloud SQL proxy configuration if used",
    "Review VPC peering status between GKE and Cloud SQL networks"
  ]
}
```

### Without Structured Output (Regular Agent):
```
Agent: "It looks like your GKE cluster is having trouble connecting to your
        database. This could be a firewall issue. Maybe check your network
        settings? Also the timeout might mean..."
```
You'd need to parse this text, extract severity, find action items, etc. **Not fun!**

### With Structured Output (This Agent):
```json
{
  "incident_summary": "...",
  "severity": "high",
  "affected_components": [...],
  "immediate_actions": [...]
}
```
Clean, predictable, ready to use! ✅

## When to Use This Agent

Perfect for:
- **Incident management systems**: Automatically create tickets with structured data
- **On-call dashboards**: Display severity, affected components, etc.
- **Automated workflows**: Trigger actions based on severity level
- **API integrations**: Feed structured incident data to other systems
- **Learning structured output**: Understanding how to get predictable responses from AI

Example use cases:
- "My server is returning 500 errors"
- "Database connection pool exhausted"
- "Kubernetes pod keeps crashing"
- "Users reporting slow page load times"

Not needed for:
- Casual questions or conversations
- Tasks that don't need structured data
- Simple greetings

## Key ADK Concepts in This Example

| Feature | What It Does | Used In This Agent |
|---------|-------------|-------------------|
| **Agent** | The core AI component | ✅ Yes - `Agent` class |
| **Output Schema** | Enforces structured output format | ✅ Yes - `IncidentReport` |
| **Pydantic BaseModel** | Defines data structure and validation | ✅ Yes - Field definitions |
| **Model** | The AI model powering analysis | ✅ Yes - `gemini-2.0-flash` |
| **Instruction** | Guides analysis and response format | ✅ Yes - Incident analysis guidelines |
| **Description** | Brief summary of agent purpose | ✅ Yes - "Analyzes incidents..." |

## Running the Agent

To use this agent in your code:

```python
from incident_analysis_agent import root_agent

# Report an incident
incident = "Our Redis cache is down and users can't log in"
response = root_agent.run(incident)

# Response is a structured IncidentReport object
print(f"Severity: {response.severity}")
print(f"Affected: {response.affected_components}")
print(f"Actions: {response.immediate_actions}")

# Or convert to JSON for APIs
import json
json_report = json.dumps(response.dict())
```

## Example Output

**Input:**
```
"GKE pods are in CrashLoopBackOff state. Application logs show 'cannot connect to database' errors."
```

**Structured Output:**
```json
{
  "incident_summary": "GKE pods in CrashLoopBackOff due to database connection failures",
  "severity": "critical",
  "affected_components": [
    "GKE pods",
    "Database connection",
    "Application service"
  ],
  "probable_cause": "Database credentials incorrect, database service unavailable, or network connectivity issue between GKE and database",
  "immediate_actions": [
    "Verify database service is running and accessible",
    "Check Kubernetes secrets for database credentials",
    "Verify network policies and firewall rules",
    "Review recent configuration changes",
    "Check database connection limits and active connections"
  ]
}
```

## Difference from Multi-Agent Incident Analysis Agent

If you've seen the incident analysis agent in `multi_agent/sub_agents/` folder, here's how they differ:

| Feature | This Agent (Standalone) | Multi-Agent Version |
|---------|------------------------|---------------------|
| **Purpose** | Works independently | Part of a router system |
| **Transfer Control** | None | Has `disallow_transfer_to_parent/peers` |
| **Use Case** | Direct incident analysis | Handles incidents routed by parent |
| **Complexity** | Intermediate (structured output) | Advanced (multi-agent + structured) |

Both use the same `output_schema` for structured reporting, but the multi-agent version integrates into a larger routing system.

## Code Structure

```
incident_analysis_agent/
├── agent.py          # Main agent with IncidentReport schema
├── __init__.py       # Package initialization
├── .env              # Environment variables (API keys, etc.)
└── README.md         # This file
```

## Official Documentation

Learn more about the ADK features used in this agent:

| Feature | Documentation Link |
|---------|-------------------|
| **LLM Agents** | [LLM Agents Documentation](https://google.github.io/adk-docs/agents/llm-agents/) |
| **Agent Configuration** | [Agent Config Reference](https://google.github.io/adk-docs/agents/config/) |
| **Getting Started** | [ADK Quickstart Guide](https://google.github.io/adk-docs/get-started/quickstart/) |
| **Models (Gemini)** | [Google Gemini Models](https://google.github.io/adk-docs/agents/models/google-gemini/) |

> **Note**: The `output_schema` feature for structured output is documented in the [LLM Agents](https://google.github.io/adk-docs/agents/llm-agents/) page under "Data & Schema Parameters".

## What You'll Learn

By studying this agent, you'll understand:
1. **Structured output with Pydantic** - How to get predictable JSON responses
2. **Output schema definition** - Creating data models for agent responses
3. **Field validation** - Using type hints and Field descriptions
4. **Real-world integration** - Building agents for production systems

---

**Beginner Tip**: Structured output is a **game-changer** for real applications! Instead of parsing messy text, you get clean, validated data every time. This makes it easy to integrate AI agents into dashboards, APIs, databases, and automated workflows. Start with simple schemas and gradually add more fields as needed.
