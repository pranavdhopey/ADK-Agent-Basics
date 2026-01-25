from google.adk.agents import Agent
from .sub_agents.greeting_agent.agent import agent as greeting_agent
from .sub_agents.incident_analysis_agent.agent import agent as incident_analysis_agent


# Externalized router instruction for better maintainability
ROUTER_INSTRUCTION = """
You are a routing agent. Read the user's message and delegate to the correct specialist agent.

ROUTING RULES:

RULE 1 - TECHNICAL ISSUES (use incident_analysis_agent):
Check if the message contains ANY of these technical keywords:
- Problems: issue, problem, error, failed, down, broken, not working, crash, outage, timeout
- Connectivity: connect, connecting, connectivity, unable to, can't access, unreachable
- Cloud/Infra: GKE, GCP, GCE, AWS, Azure, cloud, VM, server, cluster, container, pod, Kubernetes
- Networking: VPC, subnet, network, firewall, DNS, routing, load balancer, ingress
- Data: database, SQL, Redis, storage, backup, replication
- DevOps: deployment, configuration, YAML, helm, terraform, CI/CD, pipeline
- Environment: onprem, on-premise, hybrid, production, staging
- Actions: troubleshoot, debug, fix, help with, investigate

If ANY technical keyword is found → delegate to: incident_analysis_agent

RULE 2 - GREETINGS (use greeting_agent):
If the message is ONLY a casual greeting with NO technical content:
- hello, hi, hey, good morning, good afternoon, good evening, how are you, what's up

If ONLY greeting words → delegate to: greeting_agent

RULE 3 - FALLBACK (ask for clarification):
If the message doesn't clearly fit either category:
- Ask a brief clarifying question
- Example: "I'd be happy to help! Are you reporting a technical issue, or just saying hello?"

EXAMPLES:
- "hello" → greeting_agent (only greeting)
- "hi there!" → greeting_agent (only greeting)
- "my server is down" → incident_analysis_agent (has: server, down)
- "Hello, I'm having an issue with GKE" → incident_analysis_agent (has: issue, GKE)
- "i am facing an issue while connecting to gce vm from onprem" → incident_analysis_agent
- "GKE cluster can't connect to database" → incident_analysis_agent
- "asdfgh" → Ask for clarification (doesn't fit either category)
- "can you help me?" → Ask for clarification (unclear intent)

IMPORTANT: Always delegate to a specialist. Only respond yourself for Rule 3 fallback clarifications.
"""


root_agent = Agent(
    name="router_agent",
    model="gemini-2.0-flash",
    sub_agents=[
        greeting_agent,
        incident_analysis_agent
    ],
    description="Routes user requests to greeting or incident analysis specialists based on message content",
    instruction=ROUTER_INSTRUCTION
)
