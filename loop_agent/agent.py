from google.adk.agents import LoopAgent, SequentialAgent

from .sub_agents.generator import agent as generator
from .sub_agents.validator import agent as validator
from .sub_agents.fixer import agent as fixer


improve_loop = LoopAgent(
    name="yaml_improvement_loop",
    sub_agents=[
        validator,
        fixer
    ],
    max_iterations=3,
    description="Iteratively validates and improves Kubernetes YAML until it meets best practices or max iterations reached"
)

root_agent = SequentialAgent(
    name="k8s_yaml_helper",
    sub_agents=[
        generator,      # first draft
        improve_loop    # improve until valid
    ],
    description="Generates and iteratively improves Kubernetes YAML manifests following best practices"
)
