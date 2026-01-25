from google.adk.agents import SequentialAgent
from .sub_agents.intent import agent as intent
from .sub_agents.command_gen import agent as cmd
from .sub_agents.formatter import agent as fmt

root_agent = SequentialAgent(
    name="command_helper_agent",
    sub_agents=[intent, cmd, fmt],
    description="Generates properly formatted command-line commands through a 3-step process: classify tool, generate command, format output"
)
