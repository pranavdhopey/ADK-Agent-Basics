"""
Interactive terminal test script for Google ADK Callbacks.
Allows you to test:
1. Agent Authentication Check (before_agent_callback)
2. Query Caching (before_model_callback)
3. Destructive Command Blocking (before_tool_callback)
4. Secret Sanitization & Slimming (after_tool_callback)
5. Tool Error Recovery (on_tool_error_callback)
6. Compliance Disclaimer (after_agent_callback)
"""

import asyncio
import os
import uuid
from dotenv import load_dotenv

from google.adk.events import Event, EventActions
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent import root_agent

load_dotenv()


async def main():
    print("=" * 70)
    print("🛡️ Google ADK Enterprise Callback Demo - Step-by-Step Lab")
    print("=" * 70)
    print("Type a number (1-8) or keyword to test each callback individually:")
    print("  [1] login   -> Authenticate session (Required for tests 3-8)")
    print("  [2] logout  -> Test 'before_agent_callback' (Rejects unauthenticated)")
    print("  [3] cache   -> Test 'before_model_callback' (Zero-cost FAQ cache hit)")
    print("  [4] danger  -> Test 'before_tool_callback' (Blocks 'rm -rf' command)")
    print("  [5] secret  -> Test 'after_tool_callback' (Masks DB API secret)")
    print("  [6] crash   -> Test 'on_tool_error_callback' (Recovers from DB failure)")
    print("  [7] pii     -> Test 'after_model_callback' (Redacts Credit Card numbers)")
    print("  [8] normal  -> Test 'after_agent_callback' (Appends ISO audit notice)")
    print("  exit        -> Quits the runner")
    print("=" * 70)

    session_service = InMemorySessionService()
    APP_NAME = "EnterpriseCallbackDemo"
    USER_ID = "corp_user_001"
    SESSION_ID = str(uuid.uuid4())

    # Create session initially unauthenticated
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state={"authenticated": False}
    )
    print(f"Session started: {session.id} (Initial state: authenticated=False)\n")

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input or user_input.lower() == "exit":
            print("\nExiting. Goodbye!")
            break

        # Interactive state toggles for testing
        if user_input.lower() in ["1", "login"]:
            # 1. Update internal storage if available (InMemorySessionService)
            if hasattr(session_service, "sessions") and APP_NAME in session_service.sessions:
                session_service.sessions[APP_NAME][USER_ID][SESSION_ID].state["authenticated"] = True
            # 2. Append event with state_delta to persist in session service
            current_session = await session_service.get_session(
                app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
            )
            evt = Event(author="system", actions=EventActions(state_delta={"authenticated": True}))
            await session_service.append_event(session=current_session, event=evt)
            print("\n" + "="*60)
            print("🔑 [State Updated] 'authenticated' set to True!")
            print("You are now logged in. Try tests [3] to [8]!")
            print("="*60 + "\n")
            continue

        if user_input.lower() in ["2", "logout"]:
            # 1. Update internal storage if available (InMemorySessionService)
            if hasattr(session_service, "sessions") and APP_NAME in session_service.sessions:
                session_service.sessions[APP_NAME][USER_ID][SESSION_ID].state["authenticated"] = False
            # 2. Append event with state_delta to persist in session service
            current_session = await session_service.get_session(
                app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
            )
            evt = Event(author="system", actions=EventActions(state_delta={"authenticated": False}))
            await session_service.append_event(session=current_session, event=evt)
            print("\n" + "="*60)
            print("🔒 [State Updated] 'authenticated' set to False!")
            print("Now send any message (e.g. 'hello') to observe 'before_agent_callback' block you.")
            print("="*60 + "\n")
            continue

        # Shortcuts for common tests
        if user_input.lower() in ["3", "cache", "hours"]:
            print("\n▶ [TESTING: before_model_callback]")
            print("Query matches FAQ cache. Expecting instant response without calling Gemini API...")
            user_input = "What are your support hours?"
        elif user_input.lower() in ["4", "danger"]:
            print("\n▶ [TESTING: before_tool_callback]")
            print("Request contains 'rm -rf'. Expecting tool callback to block execution...")
            user_input = "Please run execute_server_command with command 'rm -rf /var/data'"
        elif user_input.lower() in ["5", "secret", "account"]:
            print("\n▶ [TESTING: after_tool_callback]")
            print("Fetching customer account. Expecting tool callback to scrub internal API secrets...")
            user_input = "Please lookup account details for 'ACC-101'"
        elif user_input.lower() in ["6", "crash"]:
            print("\n▶ [TESTING: on_tool_error_callback]")
            print("Calling failing account ID. Expecting error callback to catch DB exception...")
            user_input = "Please lookup account details for 'corrupt_acc'"
        elif user_input.lower() in ["7", "pii"]:
            print("\n▶ [TESTING: after_model_callback]")
            print("Prompting LLM with a fake card. Expecting model callback to redact credit card pattern...")
            user_input = "Print this receipt: Card 4532-1111-2222-3333 charged $50."
        elif user_input.lower() in ["8", "normal"]:
            print("\n▶ [TESTING: after_agent_callback]")
            print("Standard conversation turn. Expecting compliance disclaimer appended at the bottom...")
            user_input = "Hello! What services do you offer?"

        message = types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_input)]
        )

        try:
            async for event in runner.run_async(
                user_id=USER_ID,
                session_id=SESSION_ID,
                new_message=message,
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            print(f"\n[{event.author or 'Agent'}]:\n{part.text}")
        except Exception as e:
            print(f"\n❌ Error during execution: {e}")


if __name__ == "__main__":
    asyncio.run(main())

