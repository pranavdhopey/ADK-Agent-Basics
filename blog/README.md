# 📚 Google ADK Blog Series: From Zero to Production

Welcome to the complete, step-by-step tutorial series for the **Google Agent Development Kit (ADK)**. 

All articles are split into bite-sized, standalone parts designed for reading on Medium, Dev.to, or GitHub, with working code in the repository.

---

## 🚀 Series 1: The Core ADK Cookbook (Parts 1 – 8)

*From "Hello World" to Multi-Agent Workflows and Model Context Protocol (MCP).*

| Part | Title | Core Concepts Covered | Companion Code | Est. Read |
| :---: | :--- | :--- | :--- | :---: |
| **01** | [**The Basics: Your First AI Agents**](part-01-the-basics.md) | Agent class, instructions, tools, output schemas | [`greeting_agent/`](../greeting_agent/) | 8 min |
| **02** | [**State Management: Teaching Agents to Remember**](part-02-state-management.md) | Session services, in-memory state, runners | [`stateful_greeting_agent/`](../stateful_greeting_agent/) | 7 min |
| **03** | [**Workflow Agents: Building Agent Teams**](part-03-workflow-agents.md) | Sequential, Parallel, and Loop agent patterns | [`sequential_agent/`](../sequential_agent/) | 10 min |
| **04** | [**Multi-Agent Systems: The Router Pattern**](part-04-multi-agent-systems.md) | Supervisor routing, specialists, control transfers | [`multi-agent/`](../multi-agent/) | 10 min |
| **05** | [**AgentTool: Turning Agents into Tools**](part-05-agent-tool.md) | Nesting agents as callable sub-tools | [`devops_copilot_agent_tool/`](../devops_copilot_agent_tool/) | 9 min |
| **06** | [**FunctionTool: Giving Agents Real Power**](part-06-function-tool.md) | Executing real Python code and bash commands | [`devops_function_tool_agent/`](../devops_function_tool_agent/) | 9 min |
| **07** | [**Multi-Provider Support: Using LiteLLM**](part-07-litellm-multi-provider.md) | Running Claude, OpenAI, and local models with ADK | [`litellm_agent/`](../litellm_agent/) | 5 min |
| **08** | [**MCP Tools: Model Context Protocol**](part-08-mcp-tools.md) | Standardized external remote tools via SSE / HTTP | [`mcp_agent/`](../mcp_agent/) | 6 min |
| 📑 | [**Core Series Quick Reference Card**](quick-reference.md) | Code snippets and cheat sheet for core ADK patterns | — | 3 min |

---

## 🛡️ Series 2: Mastering ADK Callbacks (Parts 1 – 4)

*The Deterministic Control Plane for Guardrails, Caching, Safety, and Observability ([Official Specification](https://adk.dev/callbacks/)).*

| Part | Title | Interceptor Hooks Covered | Companion Code | Est. Read |
| :---: | :--- | :--- | :--- | :---: |
| **01** | [**Agent Lifecycle: The Security Gatekeepers**](callbacks-part-1-agent-lifecycle.md) | `before_agent_callback`<br>`after_agent_callback` | [`callback_agent/`](../callback_agent/) | 6 min |
| **02** | [**Model Interaction: Peeking Inside the Brain**](callbacks-part-2-model-interaction.md) | `before_model_callback`<br>`after_model_callback`<br>`on_model_error_callback` | [`callback_agent/`](../callback_agent/) | 7 min |
| **03** | [**Tool Execution: The Safety Valve**](callbacks-part-3-tool-execution.md) | `before_tool_callback`<br>`after_tool_callback`<br>`on_tool_error_callback` | [`callback_agent/`](../callback_agent/) | 7 min |
| **04** | [**Enterprise Pipeline: Chaining & Gotchas**](callbacks-part-4-enterprise-pipeline.md) | List chaining, exact naming gotcha, defensive state copy gotcha, `BasePlugin` | [`callback_agent/`](../callback_agent/) | 8 min |
| 📑 | [**Callbacks Quick Reference Card**](callbacks-quick-reference.md) | Full signatures, return types, and lifecycle cheat sheet | — | 3 min |

---

## 💡 Publishing Tips for Authors

When posting these articles to **Medium, Dev.to, or Hashnode**:
1. Copy the markdown content from the individual `part-*.md` or `callbacks-part-*.md` file.
2. Embed the relevant architecture diagrams (Mermaid or exported PNGs).
3. Update the navigation links at the bottom with your published live URLs (e.g. `Next: Part 2 (https://medium.com/@yourname/...)`).
4. Link back to the GitHub repository: `https://github.com/pranavdhopey/ADK-Agent-Basics.git`.

