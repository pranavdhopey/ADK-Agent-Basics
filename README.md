# AI Agents - Google ADK Examples

A collection of AI agent examples built with [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/).

## Prerequisites

- Python 3.13+
- A [Google API Key](https://aistudio.google.com/apikey) **or** a [Google Cloud project with Vertex AI enabled](https://console.cloud.google.com/vertex-ai)

## Setup

1. Clone the repository:

```bash
git clone <repo-url>
cd AI-Agents
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install google-adk requests pyyaml
```

4. Configure authentication by creating a `.env` file in the agent directory you want to run.

**Option A: Google API Key**

```
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_api_key_here
```

**Option B: Vertex AI**

```
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your_gcp_project_id
GOOGLE_CLOUD_LOCATION=us-central1
```

Make sure you are authenticated with Google Cloud:

```bash
gcloud auth application-default login
```

## Running Agents

### Using ADK Web UI

Start the ADK dev server pointing to the parent directory of your agent:

```bash
adk web
```

This opens a browser UI where you can select and chat with any agent interactively.

### Using ADK CLI

Run an agent directly from the terminal:

```bash
adk run <agent_directory>
```

For example:

```bash
adk run greeting_agent
adk run multi_agent
adk run sequential_agent
```

### Using Python Runner

Some agents include a `run_agent.py` script for interactive sessions:

```bash
cd multi_agent
python run_agent.py
```

## Project Structure

| Agent | Description |
|-------|-------------|
| `greeting_agent` | Basic agent with instructions |
| `google_search_agent` | Agent with Google Search tool |
| `incident_analysis_agent` | Structured output with Pydantic models |
| `multi_agent` | Router pattern with sub-agents |
| `sequential_agent` | Pipeline orchestration |
| `sequential_parallel_agent` | Parallel + sequential workflow |
| `loop_agent` | Iterative improvement with LoopAgent |
| `stateful_greeting_agent` | Session state management |
| `devops_copilot_agent_tool` | AgentTool pattern |
| `devops_function_tool_agent` | FunctionTool with Python functions |

## Resources

- [ADK Documentation](https://google.github.io/adk-docs/)
- [blog.md](blog.md) - Step-by-step tutorial covering all agent patterns
