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

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent import root_agent

load_dotenv()


async def main():
    print("=" * 70)
    print("🛡️ Google ADK Enterprise Callback Demo")
    print("=" * 70)
    print("This agent is guarded by 3 levels of callbacks:")
    print("1. Agent Lifecycle : before_agent_callback (Auth gate) & after_agent_callback")
    print("2. Model Level     : before_model_callback (Cache) & after_model_callback (PII scrub)")
    print("3. Tool Level      : before_tool_callback (Safety) & after_tool_callback (Secret scrub)")
    print("-" * 70)
    print("Special test commands:")
    print("  'login'        -> Toggles authentication in session state to True")
    print("  'logout'       -> Sets authentication in session state to False")
    print("  'hours'        -> Triggers in-memory query cache ('what are your support hours?')")
    print("  'danger'       -> Triggers blocked command ('rm -rf /var/data')")
    print("  'account'      -> Triggers secret redaction ('lookup account ACC-101')")
    print("  'crash'        -> Triggers tool error recovery ('lookup corrupt_acc')")
    print("  'exit'         -> Quits the runner")
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
        if user_input.lower() == "login":
            current_session = await session_service.get_session(
                app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
            )
            current_session.state["authenticated"] = True
            print("🔑 [State Updated] 'authenticated' set to True! You can now talk to the agent.")
            continue

        if user_input.lower() == "logout":
            current_session = await session_service.get_session(
                app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
            )
            current_session.state["authenticated"] = False
            print("🔒 [State Updated] 'authenticated' set to False! The before_agent_callback will now block requests.")
            continue

        # Shortcuts for common tests
        if user_input.lower() == "hours":
            user_input = "What are your support hours?"
            print(f"Executing: '{user_input}'")
        elif user_input.lower() == "danger":
            user_input = "Please run execute_server_command with command 'rm -rf /var/data'"
            print(f"Executing: '{user_input}'")
        elif user_input.lower() == "account":
            user_input = "Please lookup account details for 'ACC-101'"
            print(f"Executing: '{user_input}'")
        elif user_input.lower() == "crash":
            user_input = "Please lookup account details for 'corrupt_acc'"
            print(f"Executing: '{user_input}'")

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

