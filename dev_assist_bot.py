import telebot
from telebot.types import Message

from ai import AI
from database import DB


class DevAssistBot:

    def __init__(self, token: str) -> None:

        self.bot = telebot.TeleBot(token)
        DB.init()

    def listen_for_commands(self):

        @self.bot.message_handler(commands=['start'])
        def handle_start(message: Message):

            self.bot.send_message(chat_id=message.chat.id, message_thread_id=message.message_thread_id,
                                  text="Я здесь")

        @self.bot.message_handler(func=lambda message: True)
        def handle_message(message: Message):

            if message.text.startswith('\n'):
                return

            elif message.text.startswith('code\n'):
                response = AI.code(message.text[len('code\n'):])

            else:
                init_messages = [
                    {"role": "system", "content": "You are an assistant programmer."},
                    {"role": "user", "content": "We will be developing the project in python."},
                    {"role": "assistant", "content": "Great! What will the project be like?"}
                ]

                messages = DB.get_messages(message.chat.id, message.message_thread_id)

                if not messages:
                    messages.extend(init_messages)

                messages.append({"role": "user", "content": message.text})
                response, new_messages = AI.chat(messages)

                DB.set_messages(chat_id=message.chat.id, message_thread_id=message.message_thread_id,
                                messages=new_messages)

            max_message_length = 4096  # максимальная длина сообщения telegram

            for i in range(0, len(response), max_message_length):
                chunk = response[i:i + max_message_length]
                self.bot.send_message(chat_id=message.chat.id, message_thread_id=message.message_thread_id, text=chunk)

    def run_polling(self):

        self.listen_for_commands()
        self.bot.polling(none_stop=True)
