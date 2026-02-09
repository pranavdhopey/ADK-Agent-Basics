from google.adk.agents import Agent
from google.adk.tools import ToolContext


def save_user_name(name: str, tool_context: ToolContext):
    """
    Saves the user's name into the session state. 
    Call this as soon as the user identifies themselves.
    
    Args:
        name: The user's name to save
        tool_context: Context containing session information
    """
    tool_context.state["user_name"] = name  # Direct state access for proper persistence
    return f"✅ Saved '{name}' to state successfully!"


def get_user_name(tool_context: ToolContext) -> str:
    """
    Retrieves the user's name from the session state.
    Call this to check if we already know the user's name.
    
    Args:
        tool_context: Context containing session information
    
    Returns:
        The user's name if stored, or empty string if not found
    """
    user_name = tool_context.state.get("user_name", "")  # Direct state access
    if user_name:
        return f"Found user_name in state: {user_name}"
    else:
        return "No user_name found in state yet."


root_agent = Agent(
    name="stateful_greeting_agent",
    model="gemini-2.0-flash",
    description="An agent that remembers the user's name using in-memory state",
    tools=[save_user_name, get_user_name],
    instruction="""
    You are a friendly assistant that uses STATE MANAGEMENT to remember user information.

    IMPORTANT: You have two tools to manage state:
    1. get_user_name() - Check if user's name is already in state
    2. save_user_name(name) - Save the user's name to state

    Rules:
    - ALWAYS call get_user_name() first to check if you already know the user's name
    - If get_user_name() returns empty, ask the user for their name
    - When the user provides their name, IMMEDIATELY call save_user_name(name) to store it
    - After saving, greet the user by name
    - If get_user_name() returns a name, use it to greet them personally
    - Keep responses short and friendly
    
    Remember: Use the TOOLS to manage state, not just conversation history!
    """
)
