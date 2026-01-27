from typing import List
from pydantic import BaseModel, Field
from google.adk.agents import Agent


class ErrorExplanation(BaseModel):
    """Structured output for error explanations"""
    error_name: str = Field(description="The name or type of the error")
    cause: str = Field(description="What causes this error to occur")
    impact: str = Field(description="What happens when this error occurs")
    fix_steps: List[str] = Field(description="Step-by-step instructions to resolve the error")
    helpful_commands: List[str] = Field(description="Useful commands for debugging or fixing the issue")
    prevention: str = Field(description="How to prevent this error in the future")


error_agent = Agent(
    name="error_explainer_agent",
    model="gemini-2.0-flash",
    description="Explains infra and cloud errors with fixes",
    output_key="error_explanation",
    output_schema=ErrorExplanation,
    instruction="""
You are a DevOps error specialist who explains infrastructure and cloud errors.

YOUR TASK:
Analyze the error message or symptom and provide a structured explanation.

ERROR CATEGORIES YOU HANDLE:
- Kubernetes errors: CrashLoopBackOff, ImagePullBackOff, OOMKilled, Pending pods
- Container errors: Exit codes, resource limits, health check failures
- Cloud errors: Permission denied, quota exceeded, network issues
- Infrastructure errors: DNS, load balancer, certificate issues

RESPONSE GUIDELINES:
- Be specific about the cause - don't be vague
- Provide actionable fix steps in priority order
- Include relevant kubectl, gcloud, or docker commands
- Mention prevention strategies

Always provide helpful, actionable information.
"""
)
