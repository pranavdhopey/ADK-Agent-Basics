# Sequential-Parallel Agent - Multi-Cloud Architecture Advisor

## What Does This Agent Do?

This agent is a **multi-cloud architecture advisor** that provides recommendations from three different cloud perspectives simultaneously: Google Cloud (GCP), Amazon Web Services (AWS), and Kubernetes. Instead of consulting each expert one-by-one (slow!), it runs all three in **parallel**, then combines their advice into a single formatted report.

Think of it as having a panel of cloud experts who:
1. **Work simultaneously** - GCP, AWS, and Kubernetes architects analyze your requirements at the same time
2. **Give independent advice** - Each expert provides their cloud-specific recommendations
3. **Present unified report** - A formatter combines all advice into one clean document

**Key difference from sequential-only workflows**: Parallel execution is **much faster** when tasks are independent and don't need to wait for each other.

## Google ADK Features Used

This agent demonstrates **hybrid workflow orchestration** - combining parallel and sequential execution patterns:

### ⚡ ParallelAgent
The `ParallelAgent` runs multiple sub-agents **simultaneously**, all at the same time, rather than one after another.

```python
from google.adk.agents import ParallelAgent

parallel_architects = ParallelAgent(
    name="parallel_architects",
    sub_agents=[gcp, aws, k8s],  # Run ALL THREE at once!
    description="Runs GCP, AWS, and Kubernetes architects in parallel..."
)
```

**How it works:**
- All three agents (gcp, aws, k8s) start at the same time
- They work independently and simultaneously
- Each stores its result in state with its own `output_key`
- Execution completes when ALL agents finish

**Performance benefit:**
```
Sequential (one after another):
GCP (5s) → AWS (5s) → K8s (5s) = 15 seconds total ❌

Parallel (all at once):
GCP (5s) ⎤
AWS (5s) ⎥ All running at same time = 5 seconds total ✅
K8s (5s) ⎦
```

### 📋 SequentialAgent
The `SequentialAgent` orchestrates the overall workflow: first run the parallel architects, then format the results.

```python
from google.adk.agents import SequentialAgent

root_agent = SequentialAgent(
    name="multi_cloud_architecture_advisor",
    sub_agents=[
        parallel_architects,  # Step 1: Get all cloud advice (parallel)
        formatter             # Step 2: Format the combined advice
    ],
    description="Provides multi-cloud architecture recommendations..."
)
```

**Flow:**
1. **Parallel step**: Run GCP + AWS + K8s architects simultaneously
2. **Sequential step**: After all finish, run formatter to combine results

### 🔗 State Management with output_key
Each cloud architect stores its recommendations in shared state using `output_key`.

```python
# GCP architect
agent = Agent(
    name="gcp_arch_agent",
    output_key="gcp_solution",  # ← Stores GCP recommendations
    instruction="Provide GCP-specific recommendations..."
)

# AWS architect
agent = Agent(
    name="aws_arch_agent",
    output_key="aws_solution",  # ← Stores AWS recommendations
    instruction="Provide AWS-specific recommendations..."
)

# K8s architect
agent = Agent(
    name="k8s_arch_agent",
    output_key="k8s_solution",  # ← Stores Kubernetes recommendations
    instruction="Provide Kubernetes-native recommendations..."
)
```

**State after parallel execution:**
```python
{
  gcp_solution: "Use GKE, Cloud SQL, Cloud Load Balancer...",
  aws_solution: "Use EKS, RDS, ALB...",
  k8s_solution: "Use Deployments, Services, Ingress..."
}
```

### 📝 Template Variables in Formatter
The formatter accesses all three solutions from state:

```python
agent = Agent(
    name="formatter_agent",
    instruction="""
    Combine the architecture recommendations from all three cloud perspectives.

    Access the results from state:
    - GCP recommendations: {gcp_solution}
    - AWS recommendations: {aws_solution}
    - Kubernetes recommendations: {k8s_solution}
    """
)
```

The `{variable_name}` syntax pulls data from state automatically.

## How It Works

Here's the complete flow when you ask for architecture advice:

```
User: "I need to deploy a scalable web application with a PostgreSQL database"
    ↓
[STEP 1: Parallel Architects - ALL RUN SIMULTANEOUSLY]
    ↓
┌─────────────────┬─────────────────┬─────────────────┐
│   GCP Expert    │   AWS Expert    │   K8s Expert    │
│                 │                 │                 │
│ Analyzing...    │ Analyzing...    │ Analyzing...    │
│                 │                 │                 │
│ Recommends:     │ Recommends:     │ Recommends:     │
│ • GKE           │ • EKS           │ • Deployment    │
│ • Cloud SQL     │ • RDS           │ • Service       │
│ • Cloud Load    │ • ALB           │ • Ingress       │
│   Balancer      │ • Auto Scaling  │ • HPA           │
│                 │                 │                 │
│ Done! (5s)      │ Done! (5s)      │ Done! (5s)      │
└─────────────────┴─────────────────┴─────────────────┘
    ↓ (All complete in ~5 seconds, not 15!)
    ↓
State: {
  gcp_solution: "GKE for compute, Cloud SQL PostgreSQL...",
  aws_solution: "EKS for Kubernetes, RDS PostgreSQL...",
  k8s_solution: "Deployment with 3 replicas, Service type LoadBalancer..."
}
    ↓
[STEP 2: Formatter - Runs after parallel step completes]
    ↓
Formatter reads all three solutions from state
Combines into unified report:

## Multi-Cloud Architecture Recommendations

### GCP Solution
- GKE for Kubernetes orchestration
- Cloud SQL PostgreSQL for database
- Cloud Load Balancer for traffic distribution
...

### AWS Solution
- EKS for Kubernetes orchestration
- RDS PostgreSQL for managed database
- Application Load Balancer for routing
...

### Kubernetes Solution
- Deployment with 3 replicas for HA
- Service type LoadBalancer
- ConfigMap for app configuration
...

### Summary
All three approaches leverage Kubernetes for container orchestration,
with cloud-specific managed services for database and load balancing.
    ↓
Final formatted report returned to user
```

## Why Use Parallel + Sequential?

### Pure Sequential (Slower):
```
User asks question
    ↓
GCP agent (5s)
    ↓
AWS agent (5s)
    ↓
K8s agent (5s)
    ↓
Formatter (2s)
    ↓
Total: 17 seconds ❌
```

### Parallel + Sequential (This Agent - Faster):
```
User asks question
    ↓
[GCP + AWS + K8s run in parallel] (5s)
    ↓
Formatter (2s)
    ↓
Total: 7 seconds ✅
```

**3x faster!** Because the three architects don't depend on each other - they can all think at the same time.

## Cloud Architects Explained

### 1. GCP Architect (gcp_arch_agent)
**Specialization**: Google Cloud Platform services

**Focus areas:**
- **Compute**: GCE, GKE, Cloud Run, Cloud Functions
- **Storage**: Cloud Storage, Cloud SQL, Firestore, BigQuery
- **Networking**: VPC, Cloud Load Balancer, Cloud CDN, Cloud Armor
- **Monitoring**: Cloud Logging, Cloud Monitoring, Cloud Trace

**Example output:**
```
Recommended Services:
1. GKE for container orchestration
2. Cloud SQL PostgreSQL for managed database
3. Cloud Load Balancer for traffic distribution
4. Cloud Storage for static assets

Architecture Pattern:
Multi-zone GKE cluster with Cloud SQL private IP connection

Best Practices:
- Use Workload Identity for secure service authentication
- Enable VPC-native networking for better performance
- Implement Cloud Armor for DDoS protection
```

### 2. AWS Architect (aws_arch_agent)
**Specialization**: Amazon Web Services

**Focus areas:**
- **Compute**: EC2, ECS, EKS, Lambda, Fargate
- **Storage**: S3, RDS, DynamoDB, Aurora, ElastiCache
- **Networking**: VPC, ALB/NLB, CloudFront, WAF, Route53
- **Monitoring**: CloudWatch, X-Ray, CloudTrail

**Example output:**
```
Recommended Services:
1. EKS for Kubernetes orchestration
2. RDS PostgreSQL for managed database
3. Application Load Balancer for Layer 7 routing
4. S3 for object storage

Architecture Pattern:
Multi-AZ EKS cluster with RDS Multi-AZ deployment

Best Practices:
- Use IAM Roles for Service Accounts (IRSA)
- Enable VPC Flow Logs for network visibility
- Implement AWS WAF for application security
```

### 3. Kubernetes Architect (k8s_arch_agent)
**Specialization**: Cloud-native Kubernetes patterns

**Focus areas:**
- **Workloads**: Deployments, StatefulSets, DaemonSets, Jobs, CronJobs
- **Networking**: Services, Ingress, NetworkPolicies
- **Configuration**: ConfigMaps, Secrets
- **Storage**: PVCs, StorageClasses
- **Package Management**: Helm charts, Operators

**Example output:**
```
Recommended Resources:
1. Deployment with 3 replicas for high availability
2. Service type LoadBalancer for external access
3. ConfigMap for application configuration
4. PersistentVolumeClaim for database storage

Architecture Pattern:
Rolling update deployment strategy with readiness probes

Best Practices:
- Set resource requests and limits
- Implement horizontal pod autoscaling (HPA)
- Use NetworkPolicies for pod-to-pod security
```

### 4. Formatter (formatter_agent)
**Purpose**: Combines all three recommendations into a clean report

**Input**: Reads `{gcp_solution}`, `{aws_solution}`, `{k8s_solution}` from state

**Output**: Structured markdown report with all three perspectives plus a comparison summary

## When to Use This Agent

Perfect for:
- **Multi-cloud strategy planning**: Compare different cloud approaches
- **Cloud migration decisions**: See options before committing
- **Learning cloud architectures**: Understand how GCP, AWS, and K8s differ
- **Understanding ParallelAgent**: See parallel execution in action
- **Performance optimization**: When independent tasks can run simultaneously

Example requests:
- "Design a microservices architecture for an e-commerce platform"
- "How should I deploy a machine learning model API?"
- "Architecture for a real-time analytics dashboard"
- "Best practices for a multi-tenant SaaS application"

Not needed for:
- Single-cloud-only advice (use just one architect)
- Questions that don't involve architecture
- Tasks where parallel execution doesn't help

## Key ADK Concepts in This Example

| Feature | What It Does | Used In This Agent |
|---------|-------------|-------------------|
| **ParallelAgent** | Runs sub-agents simultaneously | ✅ Yes - 3 cloud architects |
| **SequentialAgent** | Runs sub-agents in order | ✅ Yes - Parallel then format |
| **Hybrid Workflows** | Combines parallel + sequential | ✅ Yes - This entire agent |
| **output_key** | Stores agent output in shared state | ✅ Yes - Each architect has one |
| **Template Variables** | Reference state in instructions | ✅ Yes - Formatter uses all 3 |
| **State Management** | Share data between agents | ✅ Yes - Solutions stored in state |
| **Independent Execution** | Agents don't depend on each other | ✅ Yes - Architects run independently |

## Parallel vs Sequential - When to Use Which?

| Scenario | Use ParallelAgent | Use SequentialAgent |
|----------|-------------------|---------------------|
| Tasks are **independent** | ✅ Yes - Run in parallel | ❌ No - Waste time waiting |
| Tasks **depend on each other** | ❌ No - Need previous results | ✅ Yes - Run in order |
| Need to **save time** | ✅ Yes - Faster execution | ❌ No - Takes longer |
| Tasks **modify same data** | ⚠️ Careful - May conflict | ✅ Yes - Safe sequential updates |

**This agent uses BOTH:**
- **Parallel**: For independent cloud architects (don't need each other's results)
- **Sequential**: To ensure formatting happens AFTER all architects finish

## Code Structure

```
sequential_parallel_agent/
├── agent.py                      # Main workflow orchestration
├── __init__.py                   # Package initialization
├── .env                          # Environment variables (API keys, etc.)
├── README.md                     # This file
└── sub_agents/
    ├── gcp_arch.py               # GCP cloud architect
    ├── aws_arch.py               # AWS cloud architect
    ├── k8s_arch.py               # Kubernetes architect
    └── formatter.py              # Combines all recommendations
```

## Running the Agent

```python
from sequential_parallel_agent import root_agent

# Ask for architecture advice
response = root_agent.run(
    "I need to deploy a real-time messaging application with WebSocket support"
)

# The agent will:
# 1. Run GCP, AWS, and K8s architects in parallel (fast!)
# 2. Wait for all three to complete
# 3. Format the combined recommendations
# 4. Return unified multi-cloud report
```

**Example output:**
```markdown
## Multi-Cloud Architecture Recommendations

### GCP Solution
- GKE for Kubernetes orchestration
- Cloud Pub/Sub for messaging infrastructure
- Cloud Load Balancer with WebSocket support
...

### AWS Solution
- EKS for Kubernetes orchestration
- Amazon MQ or SQS for messaging
- Application Load Balancer with WebSocket support
...

### Kubernetes Solution
- Deployment with WebSocket-enabled pods
- Service type LoadBalancer
- Horizontal Pod Autoscaler based on connection count
...

### Summary
All approaches use Kubernetes for orchestration with cloud-specific
managed messaging services and load balancers configured for WebSocket support.
```

## Workflow Diagram

```
┌──────────────────────────────────────────────────────┐
│        SequentialAgent (root_agent)                  │
│                                                      │
│  Step 1: Parallel Execution                         │
│  ┌────────────────────────────────────────┐         │
│  │     ParallelAgent (parallel_architects) │         │
│  │                                         │         │
│  │   ┌─────────┐  ┌─────────┐  ┌────────┐│         │
│  │   │   GCP   │  │   AWS   │  │  K8s   ││         │
│  │   │ Architect│  │Architect│  │Architect││         │
│  │   └────┬────┘  └────┬────┘  └───┬────┘│         │
│  │        │            │            │     │         │
│  │   gcp_solution  aws_solution  k8s_solution       │
│  │        │            │            │     │         │
│  │        └────────────┴────────────┘     │         │
│  └─────────────────┬────────────────────┬─┘         │
│                    │                                 │
│  Step 2: Sequential Execution (after parallel)      │
│                    ▼                                 │
│            ┌──────────────┐                          │
│            │  Formatter   │                          │
│            │  (combines   │                          │
│            │   all three) │                          │
│            └──────┬───────┘                          │
│                   │                                  │
│              Final Report                            │
└──────────────────────────────────────────────────────┘
```

## Official Documentation

Learn more about the ADK features used in this agent:

| Feature | Documentation Link |
|---------|-------------------|
| **Workflow Agents Overview** | [Workflow Agents Documentation](https://google.github.io/adk-docs/agents/workflow-agents/) |
| **Parallel Agents** | [Parallel Agents Guide](https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/) |
| **Sequential Agents** | [Sequential Agents Guide](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/) |
| **LLM Agents** | [LLM Agents Documentation](https://google.github.io/adk-docs/agents/llm-agents/) |
| **State Management** | [State Management Guide](https://google.github.io/adk-docs/sessions/state/) |

## What You'll Learn

By studying this agent, you'll understand:
1. **ParallelAgent** - How to run multiple agents simultaneously
2. **Hybrid workflows** - Combining parallel and sequential execution
3. **Performance optimization** - When parallel execution saves time
4. **Independent tasks** - Identifying which agents can run in parallel
5. **State aggregation** - Collecting results from multiple parallel agents
6. **Multi-expert patterns** - Consulting multiple specialists at once

## Advanced: Nested Workflow Agents

This agent demonstrates **workflow composition** - using one workflow agent (ParallelAgent) inside another (SequentialAgent):

```python
# ParallelAgent is a sub-agent of SequentialAgent!
root_agent = SequentialAgent(
    sub_agents=[
        parallel_architects,  # ← This is itself a workflow agent
        formatter
    ]
)
```

You can nest workflow agents to create complex execution patterns:
- Sequential → Parallel → Sequential
- Parallel → Sequential (each parallel branch has sequential steps)
- Loop → Parallel (each loop iteration runs parallel tasks)

---

**Beginner Tip**: Use **ParallelAgent when tasks are independent** and don't need each other's results. This dramatically speeds up execution! The pattern is: identify independent tasks → run them in parallel → combine results sequentially. This agent shows a perfect use case: three cloud experts can think independently, then we merge their advice. Start by identifying which parts of your workflow can run simultaneously!
