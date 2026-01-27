from google.adk.agents import Agent
from google.adk.tools import AgentTool

from .tools.kubectl_agent import kubectl_agent
from .tools.gcloud_agent import gcloud_agent
from .tools.error_agent import error_agent
from .tools.yaml_agent import yaml_agent


# Convert agents → tools
kubectl_tool = AgentTool(agent=kubectl_agent)
gcloud_tool = AgentTool(agent=gcloud_agent)
error_tool = AgentTool(agent=error_agent)
yaml_tool = AgentTool(agent=yaml_agent)


COPILOT_INSTRUCTION = """
You are a DevOps/Cloud Copilot - a helpful assistant for DevOps engineers and cloud practitioners.

IMPORTANT: Always use the appropriate tool instead of answering manually.

TOOL ROUTING:
- kubectl tasks (pods, deployments, services, namespaces, logs) → use kubectl_agent
- gcloud tasks (GCE, GKE, IAM, storage, networking) → use gcloud_agent
- errors/issues (CrashLoopBackOff, OOMKilled, permission errors) → use error_explainer_agent
- yaml/manifest creation (deployments, services, configmaps) → use k8s_yaml_generator

WORKFLOW:
1. Analyze the user's request
2. Determine which tool is most appropriate
3. Call the tool and wait for the result
4. Present the result to the user with brief context if helpful

Do NOT generate kubectl commands, gcloud commands, or YAML yourself.
Always delegate to the specialist tools.
"""

root_agent = Agent(
    name="devops_copilot",
    model="gemini-2.0-flash",
    description="DevOps assistant that delegates to specialist tools for kubectl, gcloud, error explanation, and YAML generation",

    tools=[
        kubectl_tool,
        gcloud_tool,
        error_tool,
        yaml_tool
    ],

    instruction=COPILOT_INSTRUCTION
)
