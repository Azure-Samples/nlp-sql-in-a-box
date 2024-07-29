import os
import asyncio
import logging

from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions import KernelArguments
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.connectors.ai.function_call_behavior import FunctionCallBehavior
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents.author_role import AuthorRole
from semantic_kernel.contents.finish_reason import FinishReason

from database import Database
from speech import Speech

# Set the logging level for  semantic_kernel.kernel to DEBUG.
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

    speech_service = Speech(key=speech_service_key, region=azure_location)
    database_service = Database(server_name=server_name, database_name=database_name, username=username, password=password)

    # Setup the database
    database_service.setup()

    # Create a new kernel
    kernel = Kernel()

    chat_completion = AzureChatCompletion(env_file_path=".env")

    # Add Azure OpenAI chat completion
    kernel.add_service(chat_completion)

    # Add plugins located under /plugins folder
    parent_directory = os.path.join(__file__, "../")
    kernel.add_plugin(parent_directory=parent_directory,
                      plugin_name="plugins",
                      class_init_arguments={"DatabasePlugin": {"db": database_service}})

    # Enable automatic function calling
    execution_settings = AzureChatPromptExecutionSettings(tool_choice="auto")
    execution_settings.function_call_behavior = FunctionCallBehavior.EnableFunctions(auto_invoke=True, filters={})

    # Create a history of the conversation
    chat_history = ChatHistory()

    # Starting the conversation
    speech_service.synthesize("....Welcome to the Kiosk Bot!! I am here to help you with your queries. I am still learning. So, please bear with me.")

    while True:
        try:
            speech_service.synthesize("Please ask your query through the Microphone:")
            print("Listening:")

            # Collect user input
            user_input = speech_service.recognize()
            print("User > " + user_input)

            # Terminate the loop if the user says "exit"
            if user_input == "exit":
                break

            chat_history.add_user_message(user_input)
            chat_history_count = len(chat_history)
            response = await chat_completion.get_chat_message_contents(
                chat_history=chat_history,
                settings=execution_settings,
                kernel=kernel,
                arguments=KernelArguments(),
            )

            # print assistant/tool actions
            for message in chat_history[chat_history_count:]:
                if message.role == AuthorRole.TOOL:
                    for item in message.items:
                        print("tool {} called and returned {}".format(item.name, item.result))
                elif message.role == AuthorRole.ASSISTANT and message.finish_reason == FinishReason.TOOL_CALLS:
                    for item in message.items:
                        print("tool {} needs to be called with parameters {}".format(item.name, item.arguments))

            print("Assistant > " + str(response[0]))
            speech_service.synthesize(str(response[0]))

            speech_service.synthesize("Do you have any other query? Say Yes to Continue")

            # Taking Input from the user
            print("Listening:")
            user_input = speech_service.recognize()
            print("User > " + user_input)
            if user_input != 'Yes.':
                speech_service.synthesize("Thank you for using the Kiosk Bot. Have a nice day.")
                break
        except Exception as e:
            logger.error("An exception occurred: {}".format(e))
            speech_service.synthesize("An error occurred. Let's try again.")
            continue


if __name__ == "__main__":
    asyncio.run(main())
