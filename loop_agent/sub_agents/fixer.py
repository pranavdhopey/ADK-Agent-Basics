from google.adk.agents import Agent

agent = Agent(
    name="yaml_fixer",
    model="gemini-2.0-flash",
    description="Fixes Kubernetes YAML based on validator feedback",
    output_key="yaml_draft",
    instruction="""
Fix the Kubernetes YAML based on the validation feedback from {validation_result}.

Address ALL issues mentioned by the validator:
- Add missing resource requests and limits
- Add or improve labels
- Add readinessProbe and livenessProbe
- Fix security concerns
- Apply best practices

Output ONLY the corrected YAML manifest, no explanations or markdown.
The fixed YAML will be validated again in the next iteration.
"""
)
