from google.adk.agents import LlmAgent

def get_capital_city(country: str) -> str:
    """Retrieves the capital city for a given country."""
    capitals = {"france": "Paris", "japan": "Tokyo", "canada": "Ottawa"}
    return capitals.get(country.lower(), f"Sorry, I don't know the capital of {country}.")

capital_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="capital_agent",
    description="Answers questions about the capital city of a country.",
    instruction="You are an agent that provides the capital city of a country when asked.",
    tools=[get_capital_city],
)

root_agent = capital_agent