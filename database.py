import json
from pony.orm import Database, Required, Json, db_session


class DB:
    db = Database()

    class MessageLog(db.Entity):
        chat_id = Required(str)
        message_thread_id = Required(str)
        messages = Required(Json)

    @staticmethod
    def init():
        DB.db.bind(provider='sqlite', filename='messages.sqlite', create_db=True)
        DB.db.generate_mapping(create_tables=True)

    @staticmethod
    @db_session
    def get_messages(chat_id: int, message_thread_id: int) -> list[dict]:
        db_message = DB.MessageLog.get(chat_id=str(chat_id), message_thread_id=str(message_thread_id))
        if db_message:
            return db_message.messages
        else:
            return list()

    @staticmethod
    @db_session
    def set_messages(chat_id: int, message_thread_id: int, messages: list):
        db_message = DB.MessageLog.get(chat_id=str(chat_id), message_thread_id=str(message_thread_id))
        if db_message:
            db_message.messages = messages
        else:
            DB.MessageLog(chat_id=str(chat_id), message_thread_id=str(message_thread_id), messages=messages)

