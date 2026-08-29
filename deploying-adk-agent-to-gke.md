# Deploying Your ADK Agent to GKE: The Ultimate Control Path

*Part 3 of 3 in the "Deploying ADK Agents on GCP" series*

In [Part 1](deploying-adk-agent-cloud-run.md) and [Part 2](deploying-adk-agent-to-agent-engine.md), we prioritized speed and simplicity with serverless platforms. But what happens when "serverless" isn't an option? What if your platform engineering team demands strict network controls, you need dedicated GPUs for open-weight models, or you simply want your agent living right next to the rest of your microservices?

Welcome to Google Kubernetes Engine (GKE).

> **💡 TL;DR**
> The `adk deploy gke` command builds your container, pushes it to Artifact Registry, generates Kubernetes `Deployment` and `Service` manifests, and applies them to your cluster—all in one swing. Unlike Cloud Run or Agent Engine, GKE lets you run open-weight models on GPUs, tune native networking, and control autoscaling policies. You own the infrastructure.

---

## Step 1: Why Start With GKE?

GKE is the deployment option for when you actually need control. It’s the only path with tangible infrastructure behind it: real clusters, real nodes, and real YAML manifests. 

It involves more moving parts, but you control everything—from the base image to how traffic reaches your pods. If your agent needs to integrate into an existing service mesh or utilize a specialized GPU node pool, GKE is your destination.

---

## Step 2: The Architecture at a Glance

Under the hood, GKE uses the same Cloud Build → Artifact Registry pipeline as Cloud Run. The key difference is what happens after the image is created: you hand it over to a Kubernetes cluster that *you* provisioned and are responsible for.

```text
     ┌───────────────────────┐
     │   adk deploy gke      │
     └────────────┬────────────┘
                  │
     ┌────────────▼────────────┐
     │      Cloud Build        │
     │  (builds container image)│
     └────────────┬────────────┘
                  │
     ┌────────────▼────────────┐
     │   Artifact Registry     │
     └────────────┬────────────┘
                  │  generates + applies manifests
     ┌────────────▼─────────────────────────────┐
     │             GKE Cluster                  │
     │  ┌─────────────────────────────────────┐ │
     │  │ Deployment: adk-agent               │ │
     │  │  ┌───────────┐  ┌───────────┐       │ │
     │  │  │ Pod       │  │ Pod       │ ...   │ │
     │  │  │ (ADK API) │  │ (ADK API) │       │ │
     │  │  └───────────┘  └───────────┘       │ │
     │  └─────────────────────────────────────┘ │
     │  ┌─────────────────────────────────────┐ │
     │  │ Service: adk-agent                  │ │
     │  │ type: ClusterIP or LoadBalancer     │ │
     │  └─────────────────────────────────────┘ │
     │  Workload Identity → default KSA       │
     └───────────────────────┬──────────────────┘
                             │
                External IP / port-forward
                             │
     ┌───────────────────────▼──────────────────┐
     │  Gemini via Vertex AI                    │
     └──────────────────────────────────────────┘
```

---

## Step 3: Prerequisites

This is the longest prerequisite list in the series. Skipping these steps is a guaranteed recipe for a Friday evening debugging session:

* **✅ A Running GKE Cluster:** Autopilot is a great default for managing node provisioning.
  ```bash
  gcloud container clusters create-auto adk-cluster \
      --location=$GOOGLE_CLOUD_LOCATION \
      --project=$GOOGLE_CLOUD_PROJECT
  ```
  *(Give it 5–10 minutes, then connect `kubectl` using `get-credentials`)*
* **✅ APIs Enabled:**
  ```bash
  gcloud services enable container.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com aiplatform.googleapis.com
  ```
* **✅ IAM Roles:** Ensure your default Compute Engine service account has:
  * `roles/container.developer`
  * `roles/storage.objectViewer`
  * `roles/artifactregistry.createOnPushWriter`
  * `roles/logging.logWriter`
* **✅ Workload Identity Binding (CRITICAL):** Skip this, and your pods will start, but model calls will fail with `403 PERMISSION_DENIED`. 
  ```bash
  export GOOGLE_CLOUD_PROJECT_NUMBER=$(gcloud projects describe --format json $GOOGLE_CLOUD_PROJECT | jq -r ".projectNumber")

  gcloud projects add-iam-policy-binding projects/${GOOGLE_CLOUD_PROJECT} \
      --role=roles/aiplatform.user \
      --member=principal://iam.googleapis.com/projects/${GOOGLE_CLOUD_PROJECT_NUMBER}/locations/global/workloadIdentityPools/${GOOGLE_CLOUD_PROJECT}.svc.id.goog/subject/ns/default/sa/default \
      --condition=None
  ```

---

## Step 4: The Practical Deployment

We’ll deploy our trusty `capital_agent` to a GKE cluster. 

### 4.1. Setting the Environment Variables

> **⚠️ CRITICAL WARNING: Zonal vs. Regional Clusters**
> Be highly aware of your `$GOOGLE_CLOUD_LOCATION` in your `.env` file! The ADK CLI defaults to treating locations as **regional** (e.g., `us-central1`). If you manually provisioned a **zonal** GKE cluster (e.g., `us-central1-a`), the CLI will throw a 404 error during deployment:
> `Could not find [adk-cluster] in [us-central1]. Did you mean [adk-cluster] in [us-central1-a]?`
> Make sure your cluster's location type aligns with your environment variables.

Furthermore, per the latest ADK version and documentation (see [adk.dev](https://adk.dev/get-started/google-cloud/)), we should set the `GOOGLE_GENAI_USE_ENTERPRISE` variable to route traffic correctly:

```bash
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_GENAI_USE_ENTERPRISE=true
export SERVICE_NAME="capital-agent-service"
export APP_NAME="capital_agent_app"
```

### 4.2. Executing the Deploy Command

```bash
adk deploy gke \
  --project=$GOOGLE_CLOUD_PROJECT \
  --cluster_name=adk-cluster \
  --region=$GOOGLE_CLOUD_LOCATION \
  --service_name=$SERVICE_NAME \
  --app_name=$APP_NAME \
  --service_type=LoadBalancer \
  --with_ui \
  --log_level=info \
  ~/agents/capital_agent/
```

**What you'll see on screen:**
```text
[info] Building container image from ~/agents/capital_agent/...
[info] Build succeeded. Image pushed to Artifact Registry.
[info] Generating Kubernetes manifests (Deployment + Service)...
[info] Applying manifests to cluster 'adk-cluster' in us-central1...
deployment.apps/capital-agent-service created
service/capital-agent-service created
[info] Deployment complete.
```

---

## Step 5: Testing Your Deployment

### 5.1. Verifying the Resources
Check that your pods are running:
```bash
kubectl get pods -l app=capital-agent-service
```

Grab your public IP:
```bash
kubectl get service capital-agent-service
```
*(Note: It may take a few minutes for the `EXTERNAL-IP` to resolve from `<pending>`)*

### 5.2. Testing Headless (Internal Network)
If you omitted `--service_type=LoadBalancer`, you get a `ClusterIP` default. Reach it securely via port-forwarding:

```bash
kubectl port-forward svc/capital-agent-service 8080:80
```

Then cURL it directly:
```bash
curl -X POST http://localhost:8080/run_sse \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "capital_agent_app",
    "user_id": "user_123",
    "session_id": "session_abc",
    "new_message": {"role": "user", "parts": [{"text": "What is the capital of Canada?"}]},
    "streaming": false
  }'
```

---

## Step 6: Under the Hood

Curious about what `adk deploy gke` is actually doing?

1. **Containerization:** Builds a Docker image via Cloud Build.
2. **Image Push:** Tags and pushes the image to Artifact Registry.
3. **Manifest Generation:** Dynamically writes Kubernetes `Deployment` and `Service` YAML manifests.
4. **Cluster Deployment:** Applies those manifests via the Kubernetes API. The `Service` gives it network identity (ClusterIP by default, or LoadBalancer).
5. **Workload Identity Binding:** This is the *only* thing the CLI deliberately leaves to you, as modifying IAM bindings on K8s Service Accounts is a strict security decision.

---

## Advanced: Options & Limitations

### When GKE *Isn't* the Answer

* **Overkill for Utility Agents:** Standing up an entire GKE cluster just to host a basic chatbot is excessive. Stick to Cloud Run.
* **No Scale-to-Zero:** Even Autopilot keeps a baseline resource footprint. You pay for idle capacity.
* **Security Overhead:** You own the security posture—Workload Identity, network policies, and pod security standards are your responsibility to configure correctly.

### Essential Troubleshooting Tips
* **`403 PERMISSION_DENIED`:** Re-check your Workload Identity binding (`sa/default`).
* **`attempt to write a readonly database`:** You accidentally baked a local SQLite `sessions.db` into your image. Add it to your `.dockerignore`!

---

## Step 7: Cleanup

GKE clusters cost money, even when idle. Clean up thoroughly:

```bash
gcloud container clusters delete adk-cluster \
    --location=$GOOGLE_CLOUD_LOCATION \
    --project=$GOOGLE_CLOUD_PROJECT

gcloud artifacts repositories delete adk-repo \
    --location=$GOOGLE_CLOUD_LOCATION \
    --project=$GOOGLE_CLOUD_PROJECT
```

---

## Full Series Comparison

| Feature | Cloud Run | Agent Engine | GKE |
|---|---|---|---|
| **Setup Effort** | Lowest | Low | Highest |
| **Infra You Manage** | None | None | Cluster, nodes, IAM |
| **Session Persistence**| Manual | Built-in | Manual |
| **Scale to Zero** | Yes | Yes | No |
| **GPU / Open Models** | No | No | **Yes** |
| **Custom Networking** | Limited | None | **Full control** |
| **Console Dashboard** | No | Yes (Playground) | No |
| **Best For** | Utility APIs, Demos | Managed agents at scale | Enterprise infra, GPU workloads |

---

## Wrapping Up the Series

Three commands, three completely different operational models, one elegant CLI. 

If we boil this entire series down to a decision tree:
1. **Start with Cloud Run** unless you have a concrete reason not to.
2. **Move to Agent Engine** the moment session management and observability become chores eating into your development time.
3. **Reach for GKE** only when you need dedicated GPUs, custom networking, or if your agent must reside inside an existing Kubernetes ecosystem.

The beautiful part? All three targets read the exact same `root_agent` code. You get to make your deployment decision later, not earlier.

***

**Series: Deploying ADK Agents on GCP**
1. [Cloud Run — The one-command deploy](deploying-adk-agent-cloud-run.md)
2. [Agent Engine — The fully managed runtime](deploying-adk-agent-to-agent-engine.md)
3. **GKE — Full control for enterprise deployments (📍 You are here)**