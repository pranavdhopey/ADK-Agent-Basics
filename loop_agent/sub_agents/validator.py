from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext


def exit_loop(tool_context: ToolContext):
    """Call this function ONLY when the YAML is perfect and meets all best practices."""
    print(f"[exit_loop] Triggered by {tool_context.agent_name} - YAML approved")
    tool_context.actions.escalate = True
    tool_context.actions.skip_summarization = True
    return {"status": "approved"}


agent = Agent(
    name="yaml_validator",
    model="gemini-2.0-flash",
    description="Validates Kubernetes YAML for best practices and completeness",
    tools=[exit_loop],
    output_key="validation_result",
    instruction="""
Validate the Kubernetes YAML manifest from {yaml_draft} or the previous iteration.

Check for:
- Missing or inadequate resource requests and limits
- Missing or poor labels (app, version, component)
- Missing readinessProbe and livenessProbe for Deployments
- Security issues (runAsNonRoot, readOnlyRootFilesystem)
- Bad practices (using :latest tag, no imagePullPolicy)

If the YAML is PERFECT and follows all best practices:
- Call the exit_loop tool to terminate the improvement loop
- Output: "APPROVED - YAML meets all best practices"

If problems exist:
- List specific issues clearly
- Output: "NEEDS IMPROVEMENT: [specific issues]"

Be thorough but concise.
"""
)
