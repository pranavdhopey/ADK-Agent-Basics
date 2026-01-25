from google.adk.agents import Agent

agent = Agent(
    name="command_generator",
    model="gemini-2.0-flash",
    description="Generates the actual command based on classified tool type and user request",
    output_key="raw_command",
    instruction="""
Generate the appropriate {tool_type} command for the user's request.

Requirements:
- Use ONLY {tool_type} commands (from previous classification)
- Generate syntactically correct commands
- Use best practices and safe flags where applicable
- For complex tasks, provide multiple commands separated by newlines
- Include commonly used flags (e.g., -l for ls, -f for kubectl, --format for gcloud)
- NO explanations, NO markdown, NO prose - ONLY the command(s)

Output format:
command1
command2
"""
)
