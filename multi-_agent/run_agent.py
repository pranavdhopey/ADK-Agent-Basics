import uuid
import asyncio
from dotenv import load_dotenv

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

try:
    from .agent import root_agent
except ImportError:
    from agent import root_agent


load_dotenv()


async def main():
    session_service = InMemorySessionService()

    APP_NAME = "Incident Copilot"
    USER_ID = "user_1"
    SESSION_ID = str(uuid.uuid4())

    # Create session with initial state
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state={}
    )

    print(f"Session created: {session.id}")
    print("Type 'exit' to quit\n")

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Goodbye!")
                break

            if not user_input.strip():
                print("Please enter a message.")
                continue

            message = types.Content(
                role="user",
                parts=[types.Part(text=user_input)]
            )

            response_received = False
            for event in runner.run(
                user_id=USER_ID,
                session_id=SESSION_ID,
                new_message=message,
            ):
                if event.is_final_response():
                    if event.content and event.content.parts:
                        print(f"Agent: {event.content.parts[0].text}")
                        response_received = True
                    else:
                        print("Agent: [No response content]")
                        response_received = True

            if not response_received:
                print("Agent: [No response generated]")

        except KeyboardInterrupt:
            print("\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")
            print("Please try again or type 'exit' to quit.")


if __name__ == "__main__":
    asyncio.run(main())
