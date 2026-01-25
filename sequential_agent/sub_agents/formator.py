from google.adk.agents import Agent

agent = Agent(
    name="formatter",
    model="gemini-2.0-flash",
    description="Formats the generated command in a markdown code block with proper syntax highlighting",
    instruction="""
Format the command(s) from the previous step in a markdown code block with syntax highlighting.

Use the tool type ({tool_type}) to determine the language tag:
- linux → bash
- kubectl → bash
- gcloud → bash
- docker → bash

Format:
1. Brief one-line description explaining what the command does
2. Code block with the command(s)

Example:
List all pods in the default namespace:
```bash
kubectl get pods
```
"""
)
