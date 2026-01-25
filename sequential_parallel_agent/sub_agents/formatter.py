from google.adk.agents import Agent

agent = Agent(
    name="formatter_agent",
    model="gemini-2.0-flash",
    description="Formats multi-cloud architecture recommendations into a clean, structured report",
    instruction="""
Combine the architecture recommendations from all three cloud perspectives into a well-formatted report.

Access the results from state:
- GCP recommendations: {gcp_solution}
- AWS recommendations: {aws_solution}
- Kubernetes recommendations: {k8s_solution}

Format as:

## Multi-Cloud Architecture Recommendations

### GCP Solution
{gcp_solution}

### AWS Solution
{aws_solution}

### Kubernetes Solution
{k8s_solution}

### Summary
Provide a brief 1-2 sentence summary comparing the approaches or highlighting key differences.

Keep formatting clean and readable. If any solution is missing or empty, note it briefly.
"""
)
