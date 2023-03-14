import os
from pprint import pprint

import openai
import tiktoken


class AI:

    openai.api_key = os.getenv('OPENAI_TOKEN')
    MAX_TOKENS = 4096

    @staticmethod
    def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
        """Returns the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        if model == "gpt-3.5-turbo-0301":  # note: future models may deviate from this
            num_tokens = 0
            for message in messages:
                num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
                for key, value in message.items():
                    num_tokens += len(encoding.encode(value))
                    if key == "name":  # if there's a name, the role is omitted
                        num_tokens += -1  # role is always required and always 1 token
            num_tokens += 2  # every reply is primed with <im_start>assistant
            return num_tokens
        else:
            raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
      See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")

    @staticmethod
    def divide_messages_by_token_limit(messages, token_limit, model="gpt-3.5-turbo-0301"):
        """Делит список сообщений на части, где каждая часть имеет количество токенов, не превышающее указанный предел."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        if model == "gpt-3.5-turbo-0301":  # замечание: будущие модели могут отличаться от этого
            num_tokens = 0
            divided_messages = []  # Разделенные сообщения
            for message in messages:
                message_tokens = 4  # каждое сообщение начинается с <im_start>{роль/имя}\\n{содержание}<im_end>\\n
                for key, value in message.items():
                    message_tokens += len(encoding.encode(value))
                    if key == "name":  # если есть имя, то роль опущена
                        message_tokens += -1  # роль всегда обязательна и занимает 1 токен
                if num_tokens + message_tokens <= token_limit:
                    if not divided_messages:
                        divided_messages.append([])  # добавляем список сообщений, если это первое сообщение
                    divided_messages[-1].append(message)
                    num_tokens += message_tokens
                else:
                    divided_messages.append([message])  # добавляем новый список сообщений
                    num_tokens = message_tokens  # начинаем новый список сообщений с текущего сообщения
            return divided_messages
        else:
            raise NotImplementedError(f"""divide_messages_by_token_limit() не реализована для модели {model}.""")

    @staticmethod
    def code(message: str) -> str:
        # метод, который делает запрос к модели code-davinci-002 и возвращает ответ

        # выполняем запрос и получаем ответ
        response = openai.Completion.create(
            engine="code-davinci-002",
            prompt=message,
            max_tokens=2048,
            temperature=0.5
        )

        # возвращаем текст ответа
        return response.choices[0].text

    @staticmethod
    def generate_summary(messages: list[dict], max_tokens: int) -> str:

        messages_ = [*messages, {"role": "user", "content": f"Резюмируй все, что мы обсудили так, чтобы chatgpt смог "
                                                             f"понять весь смысл через один запрос."}]
        tokens = AI.num_tokens_from_messages(messages_)

        # Генерируем выжимку
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[*messages, {"role": "user", "content": f"Резюмируй все, что мы обсудили так, чтобы chatgpt смог "
                                                             f"понять весь смысл через один запрос."}],
            max_tokens=max_tokens if not AI.MAX_TOKENS-tokens < max_tokens else AI.MAX_TOKENS-tokens,
            temperature=0.7,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )

        # Возвращаем результат
        return response.choices[0].message["content"].strip()

    @staticmethod
    def chat(messages: list[dict]) -> tuple[str, list[dict]]:

        summary_messages = messages.copy()
        if AI.num_tokens_from_messages(messages) > AI.MAX_TOKENS*0.75:
            divided_messages = AI.divide_messages_by_token_limit(messages, int(AI.MAX_TOKENS*0.75))
            for dm in divided_messages:
                print("divided_messages TOKENS: ", AI.num_tokens_from_messages(dm))
                pprint(dm)

            if len(divided_messages) > 1:
                # Генерируем короткий текст (1024 токена), содержащий основной смысл первой трети (<3072 токена) сообщений
                summary = AI.generate_summary(divided_messages[0], int(AI.MAX_TOKENS*0.25))

                # Собираем укороченные сообщения (<3072 токена)
                summary_messages = [{"role": "system", "content": summary}, *divided_messages[1]]

        # Запускаем обработку сообщений
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=summary_messages,
            max_tokens=int(AI.MAX_TOKENS*0.25),
            # stream=True,
        )

        # Возвращаем ответ AI
        response = completion.choices[0].message["content"].strip()
        summary_messages.append({"role": "assistant", "content": response})

        return response, summary_messages
