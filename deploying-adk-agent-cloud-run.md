# Deploying Your ADK Agent to Cloud Run: A Practical Guide

*Part 1 of 3 in the "Deploying ADK Agents on GCP" series*

Deploying AI agents shouldn't be harder than writing them. If you've built an agent using the Agent Development Kit (ADK) and are wondering where to host it, you're not alone. The eternal question usually boils down to: *"Cloud Run, Agent Engine, or GKE?"*

In this series, we're taking the practical approach—deploying the exact same agent to all three platforms and unpacking the experience. 

> **💡 TL;DR**
> The `adk deploy cloud_run` command takes your agent folder, builds a container via Cloud Build, pushes it to Artifact Registry, and deploys it to Cloud Run—all in one go. No Dockerfile required. If your agent is relatively stateless, doesn't need a GPU, and you want the absolute fastest path from `agent.py` to a public HTTPS endpoint, this is your starting line.

---

## Step 1: Why Start With Cloud Run?

Cloud Run is the obvious place to begin because it aligns perfectly with the philosophy of modern serverless deployments. 

Here's the pitch: **Cloud Run gives you a serverless container platform that scales to zero, can scale to thousands of instances, and never asks you to manage clusters, nodes, or YAML files.** 

For an agent that processes a few hundred requests an hour—and shouldn't cost you a dime when nobody is asking it questions—this is exactly the architecture you want.

---

## Step 2: The Architecture at a Glance

Behind the scenes of that single command, four managed GCP services are orchestrating your deployment:

```text
                    ┌─────────────────────────────┐
                    │     adk deploy cloud_run    │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │         Cloud Build          │
                    │   (builds container image)   │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │      Artifact Registry       │
                    │     (stores the image)       │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │          Cloud Run           │
                    │  ┌───────────────────────┐   │
                    │  │    ADK API Server     │   │
                    │  │  (+ optional Dev UI)  │   │
                    │  │    scale: 0 → N       │   │
                    │  └───────────────────────┘   │
                    └──────────────┬───────────────┘
                                   │
                        HTTPS endpoint (public 
                        or IAM-authenticated)
                                   │
                    ┌──────────────▼───────────────┐
                    │    Gemini via Vertex AI /    │
                    │       Google AI Studio       │
                    └──────────────────────────────┘
```

---

## Step 3: Prerequisites

Before we deploy, let's get our house in order. Ensure you have the following checked off:

* **✅ GCP Project:** You need a project with billing enabled. Ensure you are logged in (`gcloud auth login`) and have the project set (`gcloud config set project <PROJECT_ID>`).
* **✅ Directory Structure:** Your agent folder must follow the standard ADK structure:
  ```text
  capital_agent/
  ├── __init__.py       # contains: from . import agent
  └── agent.py          # defines root_agent
  ```
* **✅ Dependencies:** A `requirements.txt` file in the agent directory (or one level up).
* **✅ IAM Permissions:** The default Compute Engine service account needs the `roles/cloudbuild.builds.builder` role. 
  ```bash
  gcloud projects add-iam-policy-binding [PROJECT_ID] \
      --member="serviceAccount:[PROJECT_NUMBER]-compute@developer.gserviceaccount.com" \
      --role="roles/cloudbuild.builds.builder"
  ```
* **✅ Credentials:** If using an API key instead of Application Default Credentials, store it safely in Secret Manager and grant `roles/secretmanager.secretAccessor` to your service account.

---

## Step 4: The Practical Deployment

Let's walk through a real-world example using the `capital_agent` from the ADK docs. It's a lightweight `LlmAgent` backed by `gemini-flash-latest` that answers geography questions—a perfect stand-in for any single-purpose utility agent.

### 4.1. The Agent Code (`agent.py`)

```python
from google.adk.agents import LlmAgent

def get_capital_city(country: str) -> str:
    """Retrieves the capital city for a given country."""
    capitals = {"france": "Paris", "japan": "Tokyo", "canada": "Ottawa"}
    return capitals.get(country.lower(), f"Sorry, I don't know the capital of {country}.")

capital_agent = LlmAgent(
    model="gemini-flash-latest",
    name="capital_agent",
    description="Answers questions about the capital city of a country.",
    instruction="You are an agent that provides the capital city of a country when asked.",
    tools=[get_capital_city],
)

root_agent = capital_agent
```

### 4.2. Setting the Environment Variables

**Do not skip this step!** Properly setting your variables ensures the deployment process doesn't hang or ask unnecessary questions.

```bash
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
export AGENT_PATH="./capital_agent"
export SERVICE_NAME="capital-agent-service"
export APP_NAME="capital_agent_app"
```

### 4.3. Executing the Deploy Command

With everything configured, the deployment is a single, elegant command:

```bash
adk deploy cloud_run \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --service_name=$SERVICE_NAME \
  --app_name=$APP_NAME \
  --with_ui \
  $AGENT_PATH
```

**What you'll see on screen:**
The CLI will build the image, push it to Artifact Registry, and prompt you with one crucial question:

> `Allow unauthenticated invocations to [capital-agent-service] (y/N)?`

* **Press `y`** for a quick public demo. 
* **Press `N`** (or Enter) if you are handling sensitive data and want to restrict access via IAM identity tokens.

Once complete, you'll receive your live Service URL:
`Service URL: https://capital-agent-service-abc123xyz-uc.a.run.app`

---

## Step 5: Testing Your Deployment

### Option A: Testing With the UI
If you deployed with the `--with_ui` flag, simply open your Service URL in a browser. Select your agent from the dropdown, ask *"What's the capital of Japan?"*, and watch your agent process the tool call and respond in real-time.

### Option B: Testing Headless (via cURL)
For API integrations, you'll want to communicate directly with the endpoint. 

**1. Setup auth and endpoints:**
```bash
export APP_URL="https://capital-agent-service-abc123xyz-uc.a.run.app"
export TOKEN=$(gcloud auth print-identity-token)
```

**2. Verify the App Name:**
Always confirm the registered app name to avoid 404 errors.
```bash
curl -X GET -H "Authorization: Bearer $TOKEN" $APP_URL/list-apps
```

**3. Create a Session:**
Sessions must be explicitly created before querying.
```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  $APP_URL/apps/capital_agent_app/users/user_123/sessions/session_abc \
  -H "Content-Type: application/json" \
  -d '{}'
```

**4. Send the Query:**
```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  $APP_URL/run_sse \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "capital_agent_app",
    "user_id": "user_123",
    "session_id": "session_abc",
    "new_message": {
      "role": "user",
      "parts": [{"text": "What is the capital of Canada?"}]
    },
    "streaming": false
  }'
```

**Response:**
```json
{"content": {"role": "model", "parts": [{"text": "The capital of Canada is Ottawa."}]}, "author": "capital_agent"}
```

---

## Step 6: Under the Hood

Curious about what `adk deploy cloud_run` is actually doing?

1. **Packages your agent:** It copies your source directory and adds a lightweight ADK API server entry point.
2. **Generates a Dockerfile:** A standard Python slim image running `uvicorn` is generated on the fly.
3. **Delegates to Cloud Build:** Your source is uploaded and built remotely—no local Docker daemon required.
4. **Pushes to Artifact Registry:** Images are automatically tagged and versioned.
5. **Calls `gcloud run deploy`:** It handles the final deployment seamlessly. You can even pass raw `gcloud` flags by appending them after a `--` separator (e.g., `-- --min-instances=2`).

---

## Advanced: When Cloud Run *Isn't* the Answer

Cloud Run is fantastic, but it's not a silver bullet. Be aware of these limitations:

* **No Native Session Persistence:** A container restart can lose conversational state unless you manually configure a database like Cloud SQL or use an Agent Engine session service.
* **No GPU Support:** If you want to self-host open models (instead of calling Gemini APIs), you'll need GKE.
* **Cold Starts:** Scale-to-zero is great for billing, but the first request pays a latency penalty. Setting `--min-instances=1` solves this but incurs continuous costs.

---

## Summary & Next Steps

If you want the fastest, lowest-friction way to get an HTTPS endpoint for your ADK agent, `adk deploy cloud_run` delivers. It's the ideal default for utility agents, APIs, and rapid prototyping.

**Next up in the series:** We'll explore **Agent Engine**, where we trade a bit of Cloud Run's simplicity for a fully managed runtime featuring built-in session persistence, tracing, and monitoring—all with zero infrastructure management. 

***

**Series: Deploying ADK Agents on GCP**
1. **Cloud Run — The one-command deploy (📍 You are here)**
2. Agent Engine — The fully managed runtime
3. GKE — Full control for enterprise deployments
