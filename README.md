# DevAssistBot
DevAssistBot is a Telegram bot developed to make coding easier and more efficient.

With DevAssistBot, you can quickly access coding tips and tricks, learn new coding concepts, get help with debugging, and even receive personalized coding assistance. The bot is designed to be user-friendly and accessible to coders of all levels of experience, from beginners to advanced programmers. When you're stuck or need a little guidance in your coding, DevAssistBot is the perfect solution to help you quickly and easily overcome challenges and achieve your coding goals.

Хорошо, вот обновленный код:

```python
import telebot
from telebot.types import Message
from pony.orm import Database, Required, Optional, Json, db_session

from ai import AI


class DB:
    db = Database()

    class MessageLog(db.Entity):
        chat_id = Required(int)
        message_thread_id = Required(int)
        messages = Required(Json)

    @staticmethod
    def init():
        DB.db.bind(provider='sqlite', filename='messages.db', create_db=True)
        DB.db.generate_mapping(create_tables=True)

    @staticmethod
    @db_session
    def get_messages(chat_id: int, message_thread_id: int):
        db_message = DB.MessageLog.get(chat_id=chat_id, message_thread_id=message_thread_id)
        if db_message:
            return db_message.messages
        else:
            return None

    @staticmethod
    @db_session
    def set_messages(chat_id: int, message_thread_id: int, messages: list):
        db_message = DB.MessageLog.get(chat_id=chat_id, message_thread_id=message_thread_id)
        if db_message:
            db_message.messages = messages
        else:
            DB.MessageLog(chat_id=chat_id, message_thread_id=message_thread_id, messages=messages)


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
                # загружаем из БД messages для данного чата и сообщения
                messages = DB.get_messages(message.chat.id, message.message_thread_id)
                if messages:
                    # если сообщения уже есть, добавляем новое и отправляем AI обновленный список
                    messages.append({"role": "user", "content": message.text})
                    response = AI.chat(messages)
                else:
                    response = AI.chat([{"role": "user", "content": message.text}])
                    # сохраняем сообщения в БД
                    DB.set_messages(chat_id=message.chat.id, message_thread_id=message.message_thread_id,
                                    messages=[{"role": "user", "content": message.text},
                                              {"role": "assistant", "content": response}])

            # добавляем в БД "assistant" сообщение
            DB.get_messages(chat_id=message.chat.id, message_thread_id=message.message_thread_id).append(
                {"role": "assistant", "content": response})

            self.bot.send_message(chat_id=message.chat.id, message_thread_id=message.message_thread_id, text=response)

    def run_polling(self):
        self.listen_for_commands()
        self.bot.polling(none_stop=True)
```

Класс `DB` представляет собой абстракцию БД. Мы перенесли функции для работы с БД из основного кода в этот класс. Теперь все операции с БД происходят через методы этого класса.

Метод `get_messages` получает messages из БД по заданным параметрам. Метод `set_messages` добавляет новый message или изменяет уже существующий.

В `listen_for_commands`, мы загружаем messages из БД, если они есть, и добавляем новые в список. Затем отправляем список в AI. Если сообщений нет в БД, создаём новый список и отправляем в AI. Ответ от AI сохраняется в БД, а затем передаётся в качестве ответа пользователю.