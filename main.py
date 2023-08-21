import openai
from decouple import config
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold


# Load API keys for OpenAI GPT-3 and the Telegram bot from configuration variables.
openai.api_key = config('OPENAI_API_KEY')
BOT_TOKEN= config('BOT_API_KEY')

# Initialize the bot instance
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.MARKDOWN)
dp = Dispatcher()

# Create an empty list to store the dialogue messages
messages = []

# Create an instance of the router to be used for defining message handlers.
router = Router()

# Function to start a chat with GPT-3 (bot version)
def start_chat_bot(request, messages):
    try:

        message = str(request)  # Get the user's input

        # Add the user's message to the list of messages with its role and content
        messages.append({"role": "user", "content": message})

        # Create a dialogue context using the GPT-3.5 Turbo model and the list of messages
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages)

        # Get the generated response from the model
        answer = chat.choices[0].message.content

        # Add the model's response to the list of messages with its role and content
        messages.append({"role": "assistant", "content": answer})

        # Return the generated answer from the model
        return answer

    except Exception as e:
        logging.error(e)  # Log the error message if something goes wrong

# Handler function for the /start command
@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    user_first_name = message.from_user.first_name
    greeting = (f"🚀 Hello, {hbold(user_first_name)}!\n\n"
                "I'm here to help you. Just type your question, and I'll try to provide an answer. 🚀")
    await message.answer(greeting, parse_mode=ParseMode.HTML)

# Handler function for user messages
@router.message()
async def chat_handler(message: types.Message):
    try:
        # Show a loading message while processing the request
        loading_info = await message.answer("Thinking...🤔", parse_mode=ParseMode.MARKDOWN)

        # Get the response from the chatbot function
        text_answer = start_chat_bot(message.text, messages)

        # Send the response to the user and delete the loading message
        await message.answer(text_answer, parse_mode=ParseMode.MARKDOWN)
        await bot.delete_message(message.chat.id, loading_info.message_id)

    except Exception as e:
        logging.error(e)

@router.message(Command("exit"))
async def comand_exit_handler(message: Message) -> None:
    messages = messages.clear()
    await message.answer("Good luck 😉")

async def main() -> None:
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped!")
