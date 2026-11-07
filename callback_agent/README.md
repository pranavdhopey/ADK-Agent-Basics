# 🛡️ Enterprise Callback Agent

A production-ready Google ADK agent demonstrating the **Callbacks System** based on the official [Google ADK Callbacks Specification](https://adk.dev/callbacks/).

---

## 🌟 What Does This Agent Do?

While instructions and prompts provide soft behavioral guidance to an LLM, **callbacks provide deterministic, code-level control**. 

This agent demonstrates how to intercept, inspect, validate, modify, and short-circuit execution across the 3 critical boundaries of the ADK runtime:

1. **Agent Lifecycle**: Gatekeeps access via session authentication (`before_agent_callback`) and appends compliance audit notices (`after_agent_callback`).
2. **Model Interaction**: Slashes latency and token costs via in-memory query caching (`before_model_callback`), redacts credit card PII (`after_model_callback`), and handles model outages gracefully (`on_model_error_callback`).
3. **Tool Execution**: Blocks destructive shell commands (`before_tool_callback`), scrubs internal secrets and slims heavy payloads (`after_tool_callback`), and catches backend database crashes (`on_tool_error_callback`).

---

## 📐 Architecture & Execution Flow

```mermaid
flowchart TD
    User([User Message]) --> B_Agent["1. before_agent_callback<br><i>Auth Check: authenticated == True?</i>"]
    
    B_Agent -- No: Short-circuit --> Blocked([⛔ Return 403 Access Denied])
    B_Agent -- Yes: Proceed --> B_Model["2. before_model_callback<br><i>Cache Check: Query in QUERY_CACHE?</i>"]
    
    B_Model -- Cache Hit: Skip LLM --> Cached([⚡ Return Cached Answer])
    B_Model -- Cache Miss --> LLM[Call Gemini 2.0 Flash]
    
    LLM -. Failure .-> Err_Model["on_model_error_callback<br><i>Return friendly outage notice</i>"]
    LLM -- Success --> A_Model["after_model_callback<br><i>Scrub Credit Card PII</i>"]
    
    A_Model --> ToolDecision{Tool call needed?}
    
    ToolDecision -- Yes --> B_Tool["3. before_tool_callback<br><i>Block 'rm -rf' or destructive ops</i>"]
    B_Tool -- Dangerous --> BlockTool([🛑 Skip Tool & Return Violation Dict])
    B_Tool -- Safe --> RunTool[Execute Tool Function]
    
    RunTool -. Exception .-> Err_Tool["on_tool_error_callback<br><i>Recover from DB timeout</i>"]
    RunTool -- Result --> A_Tool["after_tool_callback<br><i>Mask API secrets & store in state</i>"]
    A_Tool --> B_Model
    
    ToolDecision -- No / Final Answer --> A_Agent["after_agent_callback<br><i>Append ISO Audit Disclaimer</i>"]
    A_Agent --> FinalResponse([User Receives Response])
```

---

## 🛠️ Google ADK Features Used

### 1. Agent Lifecycle Callbacks (`BaseAgent`)
Available on all agents (`Agent`, `SequentialAgent`, `ParallelAgent`, `LoopAgent`):
- `before_agent_callback(callback_context)`: Intercepts the request before any agent work starts. Returning `types.Content` halts execution and sends that content directly to the user.
- `after_agent_callback(callback_context)`: Appends final data (disclaimers, surveys) to the conversation history after the agent completes.

### 2. Model Interaction Callbacks (`LlmAgent`)
Available on LLM-powered agents:
- `before_model_callback(callback_context, llm_request)`: Intercepts the request right before the LLM call. Returning `LlmResponse` skips the LLM entirely (ideal for caching or mock testing).
- `after_model_callback(callback_context, llm_response)`: Intercepts raw model output to redact sensitive data or enforce structured output.
- `on_model_error_callback(callback_context, llm_request, error)`: Catches model API exceptions (e.g. quota limits, timeouts).

### 3. Tool Execution Callbacks (`LlmAgent`)
- `before_tool_callback(tool, args, tool_context)`: Inspects tool arguments before execution. Returning a `dict` cancels tool execution and feeds the dictionary directly to the LLM.
- `after_tool_callback(tool, args, tool_context, tool_response)`: Modifies tool results, redacts secrets, or executes the store-and-slim pattern.
- `on_tool_error_callback(tool, args, tool_context, error)`: Recovers from tool runtime exceptions.

---

## ⚠️ The #1 Python Rule from `adk.dev/callbacks`

> [!CAUTION]
> **Exact Parameter Naming is Strictly Enforced!**
> In Python, ADK passes callback arguments by keyword (`**kwargs`). Your callback function arguments **must match** the documented names exactly:
> - For Agent & Model callbacks: `callback_context` (NOT `ctx` or `context`)
> - For Tool callbacks: `tool`, `args`, `tool_context` (NOT `ctx`)
> 
> Using aliases like `def my_callback(ctx):` will result in a runtime `TypeError`!

---

## 🎮 How to Run and Test

### 1. Configure Authentication
Create a `.env` file in this directory or in the workspace root:

```env
GOOGLE_GENAI_USE_ENTERPRISE=FALSE
GOOGLE_API_KEY=your_api_key_here
```

### 2. Run the Interactive Test Console
We built a custom runner that lets you toggle states, test cache hits, trigger command blocks, and see errors handled live:

```bash
cd callback_agent
python run_agent.py
```

### Try these interactive commands:
- Type **`login`** -> Sets session state `authenticated = True`.
- Type **`logout`** -> Sets session state `authenticated = False` (observe `before_agent_callback` block requests).
- Type **`hours`** -> Triggers an instant in-memory cache hit via `before_model_callback` without calling Gemini.
- Type **`danger`** -> Asks the agent to run `rm -rf /var/data` (observe `before_tool_callback` block the command).
- Type **`account`** -> Asks the agent to fetch `ACC-101` (observe `after_tool_callback` scrub the API secret).
- Type **`crash`** -> Asks the agent to fetch `corrupt_acc` (observe `on_tool_error_callback` recover from the database crash).

### 3. Run with ADK Web UI
```bash
adk web
```
Select `enterprise_callback_agent` from the dropdown to chat visually!

