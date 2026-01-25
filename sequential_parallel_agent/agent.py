from google.adk.agents import ParallelAgent, SequentialAgent

from .sub_agents.gcp_arch import agent as gcp
from .sub_agents.aws_arch import agent as aws
from .sub_agents.k8s_arch import agent as k8s
from .sub_agents.formatter import agent as formatter


# Step 1 → run all architects in parallel
parallel_architects = ParallelAgent(
    name="parallel_architects",
    sub_agents=[gcp, aws, k8s],
    description="Runs GCP, AWS, and Kubernetes architects in parallel to provide multi-cloud solutions"
)

# Step 2 → merge results
root_agent = SequentialAgent(
    name="multi_cloud_architecture_advisor",
    sub_agents=[parallel_architects, formatter],
    description="Provides multi-cloud architecture recommendations by consulting GCP, AWS, and Kubernetes experts in parallel, then formatting the combined advice"
)
