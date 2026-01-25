import uuid
import asyncio
from dotenv import load_dotenv

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent import root_agent


load_dotenv()


async def main():
    session_service = InMemorySessionService()

    APP_NAME = "Greeting Bot"
    USER_ID = "user_001"
    SESSION_ID = str(uuid.uuid4())

    # ✅ await (async fix)
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state={}
    )

    # ✅ .id (field fix)
    print("Created session:", session.id)

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    while True:
        user_input = input("\nYou: ")
        if user_input == "exit":
            break

        message = types.Content(
            role="user",
            parts=[types.Part(text=user_input)]
        )

        for event in runner.run(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=message,
        ):
            if event.is_final_response():
                print("Agent:", event.content.parts[0].text)


asyncio.run(main())

