from google.adk.agents import Agent

agent = Agent(
    name="yaml_generator",
    model="gemini-2.0-flash",
    description="Generates initial Kubernetes YAML manifests based on user requirements",
    output_key="yaml_draft",
    instruction="""
Generate Kubernetes YAML manifests based on the user's request.

Include best practices:
- Set resource requests and limits
- Add appropriate labels
- Include readinessProbe and livenessProbe for deployments
- Use proper apiVersion and kind

Output ONLY valid YAML, no explanations or markdown.
"""
)
