<div align="center">
  <h1>🤖 Google ADK Agent Cookbook</h1>
  <p><strong>A curated collection of production-ready AI agents built with the Google Agent Development Kit (ADK)</strong></p>

  [![Python Version](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://python.org)
  [![Google ADK](https://img.shields.io/badge/Google-ADK-orange.svg)](https://google.github.io/adk-docs/)
  [![Vertex AI](https://img.shields.io/badge/Google_Cloud-Vertex_AI-4285F4.svg)](https://cloud.google.com/vertex-ai)
  [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
</div>

---

## 🌟 Why this repository?

Building AI agents can be daunting. This repository serves as a **practical, pattern-based cookbook** for the [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/). Whether you are building a simple chatbot, a complex multi-agent orchestration, or integrating external tools via MCP (Model Context Protocol), you will find working, copy-pasteable examples here.

---

## 🚀 The Agent Gallery

Explore different architectures and paradigms of agentic development. Each folder is a standalone, runnable example:

| Agent | Complexity | Core Concept / Description |
|-------|:---:|-------------|
| 💬 **`greeting_agent`** | 🟢 Low | The "Hello World". Basic instruction-following and simple prompts. |
| 🔍 **`google_search_agent`** | 🟢 Low | Equipping your agent with external world knowledge via Search Tools. |
| 🚨 **`incident_analysis_agent`** | 🟡 Med | Enforcing structured, JSON/Pydantic outputs for programmatic downstream usage. |
| 🔀 **`multi_agent`** | 🟡 Med | The Router Pattern: A supervisor agent delegating tasks to specialized sub-agents. |
| 🔄 **`sequential_agent`** | 🟡 Med | Pipeline Orchestration: Chaining agents where the output of one is the input to the next. |
| 🛤️ **`sequential_parallel_agent`** | 🔴 High | Combining parallel processing with sequential aggregation for complex workflows. |
| 🔁 **`loop_agent`** | 🔴 High | Iterative self-improvement using the ADK `LoopAgent` paradigm. |
| 🧠 **`stateful_greeting_agent`** | 🟡 Med | Session state management for maintaining context across long conversations. |
| 🛠️ **`devops_copilot_agent_tool`** | 🔴 High | Implementing the `AgentTool` pattern for complex DevOps workflows. |
| ⚙️ **`devops_function_tool_agent`** | 🟡 Med | Binding custom Python functions directly into the agent's reasoning loop. |
| 🔌 **`mcp_agent`** | 🔴 High | Integrating with the **Model Context Protocol (MCP)** for standardized tool usage. |
| 🪶 **`litellm_agent`** | 🟡 Med | Using LiteLLM to wrap and call non-Google models seamlessly within the ADK. |

> *Note: Looking for a specific pattern? Feel free to open an issue and request it!*

---

## 🛠️ Quick Start Guide

Get up and running in less than 2 minutes.

### 1. Prerequisites
- Python 3.13+
- A [Google API Key](https://aistudio.google.com/apikey) **or** a [Google Cloud project with Vertex AI enabled](https://console.cloud.google.com/vertex-ai)

### 2. Setup

Clone the repository and jump in:
```bash
git clone <repo-url>
cd AI-Agents
```

Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

Install the ADK and dependencies:
```bash
pip install google-adk requests pyyaml
```

### 3. Authentication
Create a `.env` file inside the specific agent directory you wish to run.

**Option A: Quick Prototyping (Google API Key)**
```env
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_api_key_here
```

**Option B: Enterprise (Vertex AI)**
```env
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your_gcp_project_id
GOOGLE_CLOUD_LOCATION=us-central1
```
*(If using Vertex AI, ensure you are authenticated via CLI: `gcloud auth application-default login`)*

---

## 🎮 Running the Agents

The ADK provides a beautiful, built-in developer UI for interacting with your agents.

**1. The Visual Way (Recommended)**
Start the ADK web server from the root directory:
```bash
adk web
```
*This opens a local browser UI. Select your agent from the dropdown and start chatting!*

**2. The Terminal Way**
Run any agent directly from the CLI:
```bash
adk run greeting_agent
```

**3. The Pythonic Way**
Some agents include a custom `run_agent.py` script for interactive terminal sessions:
```bash
cd multi_agent
python run_agent.py
```

---

## ☁️ Deployment Guides

Ready to take your agent from local to production? Check out our step-by-step deployment tutorials:
- 📖 [Deploying to Cloud Run: The One-Command Deploy](deploying-adk-agent-cloud-run.md)
- 📖 [Deploying to Agent Engine: The Fully Managed Path](deploying-adk-agent-to-agent-engine.md)

---

## 📚 Further Reading & Resources
- [Official ADK Documentation](https://google.github.io/adk-docs/)
- [blog.md](blog.md) - Deep dive tutorial covering agent patterns

---

<div align="center">
  <b>If you found this repository helpful, please consider leaving a ⭐!</b><br>
  It helps other AI enthusiasts find these examples.
</div>
