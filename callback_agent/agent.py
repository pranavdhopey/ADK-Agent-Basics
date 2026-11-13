"""
Google ADK Callbacks - Runnable Example Agents
Demonstrating the 3 levels of callbacks based on https://adk.dev/callbacks/:
1. Agent Lifecycle Callbacks: before_agent_callback, after_agent_callback
2. Model Interaction Callbacks: before_model_callback, after_model_callback, on_model_error_callback
3. Tool Execution Callbacks: before_tool_callback, after_tool_callback, on_tool_error_callback
"""

import re
from typing import Any, Dict, Optional
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools import BaseTool, ToolContext
from google.genai import types

# ==============================================================================
# PART 1: AGENT LIFECYCLE CALLBACKS (Agent Boundary)
# ==============================================================================

def auth_guard_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Agent Lifecycle: before_agent_callback
    Runs right before the agent starts processing.
    
    IMPORTANT: The argument name MUST be 'callback_context' (ADK passes by keyword).
    
    Behavior:
    - If user is not authenticated in session state, return Content to short-circuit!
    - Returning Content skips the agent and LLM call completely.
    - Returning None allows normal execution to proceed.
    """
    user_text = ""
    if callback_context.user_content and callback_context.user_content.parts:
        user_text = (callback_context.user_content.parts[0].text or "").strip().lower()

    # Allow users to authenticate or log out directly through conversation
    if user_text in ["login", "log in", "authenticate"]:
        callback_context.state["authenticated"] = True
        print(f"🔑 [before_agent] User authenticated via conversation! State updated.")
        return types.Content(
            parts=[
                types.Part.from_text(
                    text="🔑 Login successful! Your session is now authenticated. How can I help you today?"
                )
            ]
        )

    if user_text in ["logout", "log out"]:
        callback_context.state["authenticated"] = False
        print(f"🔒 [before_agent] User logged out via conversation! State updated.")
        return types.Content(
            parts=[
                types.Part.from_text(
                    text="🔒 You have been logged out. Type 'login' to authenticate again."
                )
            ]
        )

    is_authenticated = callback_context.state.get("authenticated", False)
    user_id = callback_context.user_id or "anonymous"
    
    print(f"🔒 [Agent Hook: before_agent] Validating session for user: '{user_id}' (authenticated={is_authenticated})")
    
    if not is_authenticated:
        # Short-circuit: Return canned response directly to the user
        return types.Content(
            parts=[
                types.Part.from_text(
                    text="⛔ [Access Denied] You are not authenticated. Type 'login' to authenticate."
                )
            ]
        )
    return None


def compliance_disclaimer_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Agent Lifecycle: after_agent_callback
    Runs right after the agent produces its final response.
    
    Behavior:
    - Returning Content appends an additional event to the conversation history.
    - Returning None keeps the agent's output as-is without appending anything.
    """
    print("📋 [Agent Hook: after_agent] Appending compliance disclaimer...")
    return types.Content(
        parts=[
            types.Part.from_text(
                text="\n\n---\n*🔒 Security Notice: This transaction was verified under ISO-27001 audit standards.*"
            )
        ]
    )


# ==============================================================================
# PART 2: MODEL INTERACTION CALLBACKS (LLM Boundary)
# ==============================================================================

# Simple in-memory response cache for frequent questions
QUERY_CACHE: Dict[str, str] = {
    "what are your support hours?": "Our support team is available 24/7 via chat and phone (1-800-555-0199).",
    "what is your refund policy?": "Full refunds are processed within 30 days of purchase with receipt.",
}

def query_cache_callback(
    callback_context: CallbackContext, 
    llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Model Interaction: before_model_callback
    Runs immediately before the request is sent to the LLM.
    
    IMPORTANT: Parameters MUST be named 'callback_context' and 'llm_request'.
    
    Behavior:
    - Returning LlmResponse skips the LLM call entirely (Semantic Caching / Cost Saving).
    - Returning None allows the LLM call to proceed normally.
    """
    # Extract user text from context
    user_query = ""
    if callback_context.user_content and callback_context.user_content.parts:
        user_query = callback_context.user_content.parts[0].text or ""
    
    clean_query = user_query.strip().lower()
    print(f"🧠 [Model Hook: before_model] Checking query cache for: '{clean_query}'")
    
    if clean_query in QUERY_CACHE:
        cached_text = QUERY_CACHE[clean_query]
        print(f"⚡ [Cache Hit] Found cached answer! Skipping LLM call.")
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part.from_text(text=f"[Cached Response] {cached_text}")]
            )
        )
    
    return None


def pii_scrubber_callback(
    callback_context: CallbackContext, 
    llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """
    Model Interaction: after_model_callback
    Runs immediately after receiving the response from the LLM.
    
    IMPORTANT: Parameters MUST be named 'callback_context' and 'llm_response'.
    
    Behavior:
    - Inspects the generated text.
    - If sensitive data (like a 16-digit credit card) is found, redacts it.
    - Returning an LlmResponse replaces the model's raw response.
    - Returning None preserves the model's response unmodified.
    """
    print("🛡️ [Model Hook: after_model] Inspecting model response for PII...")
    if not llm_response.content or not llm_response.content.parts:
        return None
        
    cc_regex = re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")
    modified = False
    new_parts = []
    
    for part in llm_response.content.parts:
        if part.text and cc_regex.search(part.text):
            print("🚨 [PII Redaction] Found credit card pattern! Redacting before display.")
            redacted_text = cc_regex.sub("[REDACTED CARD NUMBER]", part.text)
            new_parts.append(types.Part.from_text(text=redacted_text))
            modified = True
        else:
            new_parts.append(part)
            
    if modified:
        return LlmResponse(content=types.Content(role="model", parts=new_parts))
    
    return None


def model_error_recovery_callback(
    callback_context: CallbackContext, 
    llm_request: LlmRequest, 
    error: Exception
) -> Optional[LlmResponse]:
    """
    Model Interaction: on_model_error_callback
    Runs when the model API call raises an exception (quota, timeout, network error).
    
    IMPORTANT: Parameters MUST be named 'callback_context', 'llm_request', 'error'.
    """
    print(f"⚠️ [Model Hook: on_model_error] LLM call failed with error: {error}")
    # Return a graceful fallback response instead of crashing
    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[
                types.Part.from_text(
                    text="Our AI services are temporarily experiencing heavy load. Please try again shortly."
                )
            ]
        )
    )


# ==============================================================================
# PART 3: TOOL EXECUTION CALLBACKS (Tool Boundary)
# ==============================================================================

def execute_server_command(command: str) -> Dict[str, Any]:
    """Executes an infrastructure command on the server.
    
    Args:
        command: The shell command to run (e.g. 'uptime', 'cat /var/log/app.log')
    """
    return {"status": "success", "output": f"Simulated output for command: '{command}'"}


def lookup_customer_account(account_id: str) -> Dict[str, Any]:
    """Looks up customer account details by ID.
    
    Args:
        account_id: The customer account identifier
    """
    if account_id == "corrupt_acc":
        raise ConnectionError("Backend database connection timed out after 3000ms")
        
    return {
        "account_id": account_id,
        "customer_name": "Alice Johnson",
        "balance": 14250.75,
        "internal_api_secret": "sk_live_super_secret_99882233",
        "server_token": "bearer_internal_token_xyz"
    }


def safety_command_validator(
    tool: BaseTool, 
    args: Dict[str, Any], 
    tool_context: ToolContext
) -> Optional[Dict[str, Any]]:
    """
    Tool Execution: before_tool_callback
    Runs before any tool function is executed.
    
    IMPORTANT: Parameters MUST be named 'tool', 'args', 'tool_context'.
    
    Behavior:
    - Inspects arguments for destructive commands (rm -rf, DROP TABLE).
    - Returning a dict short-circuits execution: the tool is NOT run, and the dict
      is passed back to the LLM as the tool result!
    - Returning None allows the tool to run normally.
    """
    print(f"🛠️ [Tool Hook: before_tool] Validating call to '{tool.name}' with args: {args}")
    
    if tool.name == "execute_server_command":
        cmd = args.get("command", "").lower()
        blocked_keywords = ["rm -rf", "drop table", "mkfs", "delete from", ":(){ :|:& };:"]
        for bad_word in blocked_keywords:
            if bad_word in cmd:
                print(f"🛑 [Tool Guard Blocked] Dangerous pattern '{bad_word}' detected in command!")
                return {
                    "status": "blocked",
                    "error": f"Security Policy Violation: Command contains prohibited keyword '{bad_word}'. Execution halted."
                }
                
    return None


def secret_sanitizer_and_slimmer(
    tool: BaseTool, 
    args: Dict[str, Any], 
    tool_context: ToolContext, 
    tool_response: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Tool Execution: after_tool_callback
    Runs immediately after a tool finishes execution.
    
    IMPORTANT: Parameters MUST be named 'tool', 'args', 'tool_context', 'tool_response'.
    
    Behavior:
    - Sanitizes sensitive credentials (API keys, internal tokens) from tool output.
    - Implements the 'store-and-slim' pattern: saves full details to session state,
      and returns a slim summary to the LLM to save tokens!
    - Returning a dict replaces the tool output seen by the LLM.
    - Returning None leaves the response untouched.
    """
    print(f"🧼 [Tool Hook: after_tool] Sanitizing output from tool: '{tool.name}'")
    
    if isinstance(tool_response, dict):
        sanitized = dict(tool_response)
        
        # Redact secrets
        for secret_key in ["internal_api_secret", "server_token", "password"]:
            if secret_key in sanitized:
                sanitized[secret_key] = "[REDACTED_SECRET]"
                
        # Store-and-slim pattern: persist account info to state, trim payload
        if "customer_name" in sanitized:
            tool_context.state["last_viewed_customer"] = sanitized["customer_name"]
            
        return sanitized
        
    return None


def tool_error_fallback(
    tool: BaseTool, 
    args: Dict[str, Any], 
    tool_context: ToolContext, 
    error: Exception
) -> Optional[Dict[str, Any]]:
    """
    Tool Execution: on_tool_error_callback
    Runs when a tool throws an unhandled exception.
    
    IMPORTANT: Parameters MUST be named 'tool', 'args', 'tool_context', 'error'.
    
    Behavior:
    - Catches exceptions (e.g. database timeout, network glitch) and returns a clean
      error dictionary so the LLM can explain the situation gracefully without crashing.
    """
    print(f"🩹 [Tool Hook: on_tool_error] Tool '{tool.name}' threw error: {error}. Recovering...")
    return {
        "status": "degraded_error",
        "message": f"Tool '{tool.name}' is currently unreachable due to a backend connection timeout.",
        "suggestion": "Please inform the user and recommend trying again in a few moments."
    }


# ==============================================================================
# ROOT AGENT: THE UNIFIED ENTERPRISE PIPELINE
# ==============================================================================

root_agent = Agent(
    name="enterprise_callback_agent",
    model="gemini-2.0-flash",
    description="A comprehensive enterprise agent protected by all 3 callback tiers",
    tools=[execute_server_command, lookup_customer_account],
    instruction="""
    You are an Enterprise Operations & Banking Assistant.
    
    You have tools to:
    - Execute server infrastructure commands (`execute_server_command`)
    - Look up customer accounts (`lookup_customer_account`)
    
    Always be professional, concise, and helpful.
    If a tool returns an error or blocked status, explain it politely to the user.
    """,
    # 1. Agent Lifecycle Callbacks
    before_agent_callback=auth_guard_callback,
    after_agent_callback=compliance_disclaimer_callback,
    # 2. Model Interaction Callbacks
    before_model_callback=query_cache_callback,
    after_model_callback=pii_scrubber_callback,
    on_model_error_callback=model_error_recovery_callback,
    # 3. Tool Execution Callbacks
    before_tool_callback=safety_command_validator,
    after_tool_callback=secret_sanitizer_and_slimmer,
    on_tool_error_callback=tool_error_fallback,
)

