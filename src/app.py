import os
import asyncio
import logging

from dotenv import load_dotenv
from semantic_kernel.contents.chat_history import ChatHistory


from speech import Speech
from kernel import Kernel
from database import Database
from orchestrator import Orchestrator


logging.basicConfig(
    filename="app.log",
    format="[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def main():
    load_dotenv()

    server_name = "{}.database.windows.net".format(os.getenv("SQL_SERVER_NAME"))
    database_name = os.getenv("SQL_DATABASE_NAME")
    username = os.getenv("SQL_USERNAME")
    password = os.getenv("SQL_PASSWORD")
    speech_service_key = os.getenv("SPEECH_SERVICE_API_KEY")
    azure_location = os.getenv("AZURE_LOCATION")
    openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    openai_deployment_name = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")

    speech_service = Speech(key=speech_service_key, region=azure_location)
    database_service = Database(server_name=server_name, database_name=database_name, username=username, password=password)

    # Setup the database
    database_service.setup()

    kernel = Kernel(database_service=database_service, openai_api_key=openai_api_key, openai_endpoint=openai_endpoint, openai_deployment_name=openai_deployment_name)

    # Create a history of the conversation
    chat_history = ChatHistory()

    orchestrator = Orchestrator(speech_service=speech_service, kernel=kernel)

    await orchestrator.run(chat_history=chat_history)


if __name__ == "__main__":
    asyncio.run(main())
