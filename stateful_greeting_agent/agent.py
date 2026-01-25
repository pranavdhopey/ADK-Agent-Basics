from google.adk.agents import Agent

root_agent = Agent(
    name="stateful_greeting_agent",
    model="gemini-2.0-flash",
    description="An agent that remembers the user's name using in-memory state",
    instruction="""
    You are a friendly assistant.

    Use conversation state to remember the user's name.

    Rules:
    - If the user's name is not in state, ask for it
    - If the user provides their name, store it in state as `user_name`
    - If `user_name` exists in state, greet the user using their name
    - Keep responses short and friendly
    """
)
