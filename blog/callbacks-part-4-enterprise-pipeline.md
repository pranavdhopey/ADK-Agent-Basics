> 📁 **Source Code**: [`callback_agent/`](../callback_agent/)  
> 📖 **Callbacks Master Series**: [Blog Directory](README.md)  
> 🌐 **Official Spec**: [adk.dev/callbacks](https://adk.dev/callbacks/)

---

# Part 4: The Enterprise Pipeline - Chaining, Precedence & Full Blueprint

📁 **Code**: [callback_agent/agent.py](../callback_agent/agent.py)  
> **TL;DR**: Combine Agent, Model, and Tool callbacks into a single cohesive production pipeline. Learn list chaining, execution precedence, the #1 Parameter Name trap, the #2 State-Copy trap, and when to upgrade to `BasePlugin`.

*Welcome to the grand finale of the Callbacks series! If you haven't read [Part 1](callbacks-part-1-agent-lifecycle.md), [Part 2](callbacks-part-2-model-interaction.md), and [Part 3](callbacks-part-3-tool-execution.md), start there first!*

---

## Reflections on Parts 1–3

Across the first three parts, we conquered all three callback levels:
- **Part 1**: Locked the front door with `before_agent_callback`
- **Part 2**: Slashed API costs and redacted PII with `before_model_callback` & `after_model_callback`
- **Part 3**: Defended our servers and caught crashes with `before_tool_callback` & `on_tool_error_callback`

Now, the final challenge: **How do we tie everything together into a production-grade enterprise pipeline?**

---

## What We're Building in Part 4

In production, you rarely have just one callback function. You have:
- An audit logger
- A rate limiter
- A security guardrail
- A response cache

How do you chain multiple callbacks without writing spaghetti code? What happens if two callbacks try to modify the same response? And how do you avoid the two most dangerous Python gotchas in Google ADK?

In this final part, we cover:
1. **Callback Chaining**: Supplying lists of callbacks (`[cb1, cb2]`) and how resolution precedence works
2. **The Decision Matrix**: When to use Instructions vs State vs Tools vs Callbacks
3. **The #1 Gotcha**: The strict keyword naming requirement
4. **The #2 Gotcha**: The session defensive copy trap
5. **Async Support**: Calling Redis and remote APIs inside callbacks
6. **Going Global**: When to package callbacks into reusable `BasePlugin` classes

---

## 1. Callback Chaining with Lists

Did you know that every callback argument in ADK accepts either a **single callable** or a **list of callables**?

```python
root_agent = Agent(
    name="audited_agent",
    model="gemini-2.0-flash",
    # Chaining multiple callbacks in list order:
    before_tool_callback=[
        log_tool_invocation_metrics,
        validate_user_permissions,
        block_destructive_commands,
    ]
)
```

### How ADK Resolves Callback Chains
ADK executes callbacks in the exact order they appear in the list until **one callback returns a non-None value**:
1. `log_tool_invocation_metrics` runs -> returns `None` (passes through).
2. `validate_user_permissions` runs -> returns `None` (passes through).
3. `block_destructive_commands` runs -> returns `{"status": "blocked"}`!
4. **Execution stops immediately**: Remaining callbacks in the list and the actual tool function are skipped!

---

## 2. When to Use What: The Decision Matrix

One of the biggest questions developers ask is: *"Should I solve this with an instruction, a tool, state, or a callback?"*

Use this cheat sheet to choose the right tool for the job:

| Capability / Requirement | Instructions | State | Tools | Callbacks |
| :--- | :---: | :---: | :---: | :---: |
| Agent tone, personality & role | ✅ **Best** | ❌ No | ❌ No | ❌ No |
| Retaining user details across turns | ❌ No | ✅ **Best** | ❌ No | ⚠️ Can read/set |
| Fetching external data / taking actions | ❌ No | ❌ No | ✅ **Best** | ❌ No |
| **Deterministic Access Control (Auth)** | ❌ Fragile | ❌ No | ❌ No | ✅ **Best** (`before_agent`) |
| **Response Caching (Zero Token Cost)** | ❌ Impossible | ❌ No | ❌ No | ✅ **Best** (`before_model`) |
| **PII & Secret Redaction** | ❌ Unreliable | ❌ No | ❌ No | ✅ **Best** (`after_model` / `after_tool`) |
| **Blocking Destructive Commands** | ❌ Unreliable | ❌ No | ❌ No | ✅ **Best** (`before_tool`) |
| **Graceful API / Tool Crash Recovery** | ❌ Impossible | ❌ No | ❌ No | ✅ **Best** (`on_*_error`) |

---

## 3. The #1 Gotcha: Exact Parameter Naming

According to [adk.dev/callbacks](https://adk.dev/callbacks/), ADK invokes Python callbacks using **keyword arguments (`**kwargs`)**.

If you name your parameters using personal aliases like `ctx`, your code will fail with an immediate runtime crash:

```python
# ❌ THIS WILL CRASH AT RUNTIME!
def my_callback(ctx):  # TypeError: got an unexpected keyword argument 'callback_context'
    return None

# ✅ THIS WORKS PERFECTLY!
def my_callback(callback_context):
    return None
```

### The Golden Naming Rules:
- **Agent Callbacks**: Must use `callback_context`
- **Model Callbacks**: Must use `callback_context`, `llm_request`, `llm_response`, `error`
- **Tool Callbacks**: Must use `tool`, `args`, `tool_context`, `tool_response`, `error`

---

## 4. The #2 Gotcha: Modifying Session State (`get_session` Returns a Defensive Copy!)

If you try to inspect or toggle session state from an external runner or test harness like this:

```python
# ❌ THIS DOES NOT PERSIST!
session = await session_service.get_session(app_name, user_id, session_id)
session.state["authenticated"] = True  # Modifies a disconnected copy!
```

In Google ADK, `session_service.get_session()` intentionally returns a **copy** of the session to prevent multi-threaded race conditions. Direct mutations to `session.state` on that copy are discarded!

### How State Persistence Works in ADK:
1. **Inside Callbacks & Tools**: Always mutate `callback_context.state["key"] = val` or `tool_context.state["key"] = val`. ADK automatically tracks deltas (`state_delta`) and commits them to the store at the end of the turn!
2. **Outside the Agent (Runners/Tests)**: Either update the internal store directly (`session_service.sessions[app][user][id].state[...] = val`) or append an event containing `actions=EventActions(state_delta={"authenticated": True})`.

---

## 5. Async Support

All callbacks in ADK support both standard synchronous (`def`) and asynchronous (`async def`) functions:

```python
async def async_auth_guard(callback_context: CallbackContext) -> Optional[types.Content]:
    # Seamlessly call remote Redis, Firestore, or Auth0!
    user_token = callback_context.state.get("token")
    is_valid = await verify_jwt_with_auth0(user_token)
    if not is_valid:
        return types.Content(parts=[types.Part.from_text(text="Invalid token.")])
    return None
```

ADK automatically detects if a callback returns an `Awaitable` and awaits it seamlessly.

---

## 6. Going Global: Callbacks vs. Plugins (`BasePlugin`)

As documented in the official Google ADK Architecture Guide:
- **Callbacks** are defined inline and scoped directly to **individual agents** (e.g. `auth_guard_agent` or `safe_tool_agent`).
- **Plugins (`BasePlugin`)** package these exact same lifecycle callbacks into reusable, application-wide modules that automatically hook into **every agent and runner** across your system.

```python
from google.adk.plugins.base_plugin import BasePlugin

class GlobalAuditPlugin(BasePlugin):
    """A reusable enterprise plugin applying callbacks globally."""
    
    async def before_agent_callback(self, *, agent, callback_context):
        print(f"🌍 [Global Plugin] Intercepting agent '{agent.name}' for user '{callback_context.user_id}'")
        return None
```

If a callback applies only to one agent's workflow, configure it directly on `Agent(...)`. If it represents enterprise-wide security, global telemetry, or distributed tracing, package it into a `BasePlugin`!

---

## What I Learned in Part 4

1. **Defense in Depth**: Real-world agents require layered security: auth at the agent level, caching and PII scrubbing at the model level, and safety checks at the tool level.
2. **Short-Circuiting is Clean**: Returning non-None values gives you clean, declarative policy exits without messy `if/else` logic scattered throughout your code.
3. **Know the Gotchas**: Always match exact parameter names and remember that `get_session()` returns a defensive copy.

---

## Conclusion & Cheat Sheet

Congratulations! You now have a production-grade, deterministic control plane for your Google ADK agents. 

Check out the companion [Callbacks Quick Reference Card](callbacks-quick-reference.md) for a handy cheat sheet of all hook signatures and return types!

Happy building, and may your AI agents run safely, cheaply, and reliably in production! 🚀

---

<div align="between">
  <span>[← Previous: Part 3: Tool Execution Callbacks](callbacks-part-3-tool-execution.md)</span> | <span>[Callbacks Quick Reference Card →](callbacks-quick-reference.md)</span>
</div>
