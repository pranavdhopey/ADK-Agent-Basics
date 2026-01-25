from typing import List
from pydantic import BaseModel, Field
from google.adk.agents import Agent


class IncidentReport(BaseModel):
    incident_summary: str = Field(description="Summary of the incident")
    severity: str = Field(description="low, medium, high, or critical")
    affected_components: List[str]
    probable_cause: str
    immediate_actions: List[str]


root_agent = Agent(
    name="incident_analysis_agent",
    model="gemini-2.0-flash",
    description="Analyzes incidents and produces a structured report",
    output_schema=IncidentReport,
    instruction="""
    You are an Incident Analysis Assistant.
    Your task is to analyze an incident described by the user and produce a structured incident report.

    GUIDELINES:
    - Carefully analyze the incident description
    - Summarize the incident clearly and concisely
    - Determine the severity level:
      * low
      * medium
      * high
      * critical
    - Identify all affected components or systems
    - Suggest the most likely root cause
    - Recommend clear and actionable immediate steps to mitigate the issue

    IMPORTANT: Your response MUST be valid JSON matching this structure:
    { 
       "incident_summary": "Short, clear summary of the incident",
       "severity": "low | medium | high | critical",
       "affected_components": ["component1", "component2"],
       "probable_cause": "Most likely cause of the incident",
       "immediate_actions": [
          "Action 1",
          "Action 2",
          "Action 3"
       ]
    }

    DO NOT include any explanations, markdown, or additional text outside the JSON response.
    """
)
