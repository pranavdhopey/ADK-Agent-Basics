from google.adk.agents import Agent

agent = Agent(
    name="intent_agent",
    model="gemini-2.0-flash",
    description="Classifies user's command request into the appropriate tool category",
    output_key="tool_type",
    instruction="""
Analyze the user's request and determine which command-line tool they need.

Categories:
- linux: General Linux/bash commands (ls, grep, find, chmod, cat, sed, awk, ps, netstat, etc.)
- kubectl: Kubernetes commands (kubectl get, apply, describe, logs, exec, etc.)
- gcloud: Google Cloud CLI commands (gcloud compute, gcloud container, gcloud storage, etc.)
- docker: Docker commands (docker run, build, ps, exec, compose, etc.)

Respond with ONLY the category name: linux, kubectl, gcloud, or docker
"""
)
