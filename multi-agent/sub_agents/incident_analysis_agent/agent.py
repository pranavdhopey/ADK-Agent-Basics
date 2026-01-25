from typing import List, Literal
from pydantic import BaseModel, Field
from google.adk.agents import Agent


class IncidentReport(BaseModel):
    """Structured incident analysis report."""
    incident_summary: str = Field(
        description="Brief summary of what went wrong and the impact"
    )
    severity: Literal["low", "medium", "high", "critical"] = Field(
        description="Severity level based on impact and urgency"
    )
    affected_components: List[str] = Field(
        description="List of affected systems, services, or components"
    )
    probable_cause: str = Field(
        description="Most likely root cause based on the symptoms described"
    )
    immediate_actions: List[str] = Field(
        description="List of 3-5 recommended troubleshooting steps in priority order"
    )


agent = Agent(
    name="incident_analysis_agent",
    model="gemini-2.0-flash",
    description="Analyzes technical incidents involving cloud, infrastructure, networking, database, and deployment issues",
    output_key="incident_report",
    output_schema=IncidentReport,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    instruction="""
You are an Incident Analysis Assistant specializing in cloud and infrastructure issues.

ANALYSIS GUIDELINES:
1. incident_summary: Concise description of the problem and its business impact
2. severity: Determine based on:
   - critical: Complete outage, data loss risk, security breach
   - high: Major functionality broken, many users affected
   - medium: Partial degradation, workaround available
   - low: Minor issue, minimal impact
3. affected_components: Identify ALL systems involved (be thorough)
4. probable_cause: Provide the most likely root cause based on symptoms
5. immediate_actions: List 3-5 specific, actionable troubleshooting steps in priority order

Be specific, technical, and actionable. Avoid generic advice.

IMPORTANT: Do NOT transfer to any other agent. Analyze the incident and respond with the structured report.
"""
)
