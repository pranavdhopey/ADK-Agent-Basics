# Deploying Your ADK Agent to Agent Engine: The Fully Managed Path

*Part 2 of 3 in the "Deploying ADK Agents on GCP" series*

In [Part 1](deploying-adk-agent-cloud-run.md), we deployed our ADK agent to Cloud Run in a single command. It was fast, but it quietly handed us a homework assignment: managing session persistence, scaling policies, and observability wiring. What if you just want someone else to handle all of that?

Enter **Vertex AI Agent Engine**. Where Cloud Run treats your agent as "a container that happens to run ADK," Agent Engine treats it as a first-class agent. It provides built-in session state, telemetry, and a playground UI right in the Cloud Console. 

> **💡 TL;DR**
> The `adk deploy agent_engine` command wraps your agent in a `reasoning_engines.AdkApp`, ships it to Vertex AI Agent Engine's managed runtime, and gives you session persistence, telemetry, and a monitoring dashboard—without a single YAML file or Cloud Storage staging bucket. You trade container-level control for a built-in infrastructure team.

---

## Step 1: Why Start With Agent Engine?

If your organization is already living inside Vertex AI, this is the path of least resistance. 

Agent Engine is purpose-built for agentic workloads. By using it, you never have to configure databases for conversational memory or manually wire up tracing. You simply deploy your agent and get a production-ready, conversational endpoint out of the box.

---

## Step 2: The Architecture at a Glance

Notice there's no Docker build step here. Agent Engine builds and runs the container for you behind the scenes. You ship a pickled app bundle, not an image.

```text
     ┌────────────────────────┐
     │  adk deploy            │
     │  agent_engine          │
     └────────────┬────────────┘
                  │
     ┌────────────▼────────────┐
     │  Local packaging step   │
     │  *.pkl + requirements   │
     │  + dependencies.tar.gz  │
     │  (streamed directly)    │
     └────────────┬────────────┘
                  │  upload
     ┌────────────▼────────────┐
     │ Vertex AI Agent Engine  │
     │  ┌───────────────────┐  │
     │  │ reasoning_engines.│  │
     │  │ AdkApp            │  │
     │  │ ├─ Session Service│  │
     │  │ ├─ OpenTelemetry  │  │
     │  │ └─ Playground UI  │  │
     │  └───────────────────┘  │
     └────────────┬────────────┘
                  │
        REST API / Python SDK
        (session-aware, multi-turn)
                  │
     ┌────────────▼────────────┐
     │  Gemini via Vertex AI   │
     └─────────────────────────┘
```

---

## Step 3: Prerequisites

Before you run the deployment command, ensure you have the following ready:

* **✅ GCP Project:** You need a project with the Vertex AI API enabled.
* **✅ The `vertexai` SDK:** The CLI uses the Vertex AI SDK locally to wrap and pickle the app. Ensure it is installed in your active environment:
  ```bash
  pip install google-cloud-aiplatform
  ```
  *(Note: `google-adk` doesn't pull this in for you as a dependency, so install it explicitly!)*
* **✅ Directory Structure:** Your agent code (`agent.py` and `__init__.py`) structured normally.
* **✅ Region Selection:** Ensure you are deploying to a supported Agent Engine region (check the Agent Builder locations page).
* **⛔ No Staging Bucket Needed:** If you see older tutorials asking you to create a Cloud Storage bucket (`gsutil mb`), skip it! The `--staging_bucket` flag is deprecated in ADK 2.x, and the payload streams directly to Agent Engine.

---

## Step 4: The Practical Deployment

We'll reuse our geography-answering `capital_agent` from Part 1, but send it to a different destination.

### 4.1. Setting the Environment Variables

Set up your project and region:

```bash
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
```

### 4.2. Executing the Deploy Command

The deployment command requires no bucket and utilizes `--otel_to_cloud` for telemetry:

```bash
adk deploy agent_engine \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --display_name="Capital Agent" \
  --otel_to_cloud \
  capital_agent
```

**What you'll see on screen:**
Agent Engine takes over to build and spin up containers on its backend. Since you aren't doing the Docker build yourself, this process typically takes about **10 minutes**.

```text
Copying agent source code...
Initializing Vertex AI...
Building AdkApp bundle...
Creating AgentEngine...
✓ AgentEngine created successfully.

Resource name: projects/.../locations/us-central1/reasoningEngines/2902138951282196480
```

---

## Step 5: Interacting With Your Deployment

### 5.1. Finding it in the Console

Head to **Vertex AI → Agent Engine** in the GCP Console. Select your matching region, and you'll find "Capital Agent" ready and waiting. 

You get a rich dashboard with:
* **Playground:** Chat with your agent directly—no cURL commands required.
* **Runtime Metrics:** Track latency and request volumes.
* **Traces:** View per-request spans for model calls and tool executions.
* **Sessions:** Browse every conversation your agent has had.

### 5.2. Querying Programmatically (Python SDK)

Because session state is managed automatically, multi-turn conversations work right out of the box.

```python
import vertexai
from vertexai.preview import reasoning_engines

vertexai.init(project="your-gcp-project-id", location="us-central1")

# Use the ID returned from your deploy command
agent_engine = vertexai.agent_engines.get(
    "projects/123456/locations/us-central1/reasoningEngines/2902138951282196480"
)

# Start a session
session = agent_engine.create_session(user_id="user_123")

# Query the agent
for event in agent_engine.stream_query(
    user_id="user_123",
    session_id=session["id"],
    message="What is the capital of Japan?",
):
    print(event)
```

**Output:**
```json
{'content': {'parts': [{'text': 'The capital of Japan is Tokyo.'}], 'role': 'model'}, 'author': 'capital_agent'}
```

If you ask a follow-up ("and its population?"), the agent retains context automatically thanks to the `VertexAiSessionService`. 

---

## Step 6: Under the Hood

Here is exactly what the `adk deploy agent_engine` command is doing:

1. **Wraps your `root_agent`** in a `reasoning_engines.AdkApp`, granting you managed sessions and telemetry hooks.
2. **Pickles the app** locally rather than containerizing it. The `.pkl` file, `requirements.txt`, and a `dependencies.tar.gz` form the deployment payload.
3. **Streams the bundle directly** to Agent Engine. No intermediate storage bucket is needed.
4. **Calls the Agent Engine API** to create (or update) a `ReasoningEngine` resource. Google builds the serving container for you.
5. **Registers services automatically:** `VertexAiSessionService` enables persistent state, and `--otel_to_cloud` turns on OpenTelemetry exports.

---

## Advanced: Options & Limitations

### Crucial Update: Using `--agent_engine_id`
`adk deploy agent_engine` creates a brand-new resource *every time* you run it unless you explicitly pass the `--agent_engine_id` flag. To push updated code to the *same* deployed agent, pass the ID from your initial deploy:

```bash
adk deploy agent_engine \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --agent_engine_id=2902138951282196480 \
  capital_agent
```
*(Tip: Export your `AGENT_ENGINE_ID` as an environment variable right after your first deploy!)*

### When Agent Engine *Isn't* the Answer

* **No Custom Containers:** You lose raw container control. No custom base images, sidecar containers, or arbitrary `Dockerfile` tweaks. 
* **No GPU / Self-Hosted Models:** Just like Cloud Run, this is a managed, Gemini-first runtime.
* **Longer Deploy Times:** It takes ~10 minutes to deploy versus Cloud Run's 2-3 minutes.
* **Narrower Region Availability:** Check the supported regions list before committing.

---

## Step 7: Cleanup

Unlike Cloud Run, forgetting to delete an Agent Engine deployment won't incur significant idle costs, but tidy habits matter! Delete it programmatically:

```python
from vertexai import agent_engines
agent_engines.delete("projects/.../reasoningEngines/2902138951282196480")
```
*(Or delete it from the Console: **Service Configuration → Deployment details → Delete**).*

---

## Summary & Next Steps

Agent Engine is the perfect deployment target for teams who want to focus entirely on agent logic, rather than infrastructure. You trade raw flexibility for an out-of-the-box dashboard, playground, and seamless session handling.

**Next up in the series:** We'll explore **GKE**, the ultimate destination when you need GPUs, open models, custom networking, or if you're already operating within a Kubernetes ecosystem.

***

**Series: Deploying ADK Agents on GCP**
1. [Cloud Run — The one-command deploy](deploying-adk-agent-cloud-run.md)
2. **Agent Engine — The fully managed runtime (📍 You are here)**
3. GKE — Full control for enterprise deployments
