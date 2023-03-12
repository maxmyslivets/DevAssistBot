import os

import openai


class AI:

    openai.api_key = os.getenv('OPENAI_TOKEN')

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
    def chat(messages: list[dict]) -> list[dict]:
        # метод, который принимает контекст, делает запрос к модели gpt-3.5-turbo и возвращает ответ

        # формируем контекст запроса
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        # возвращаем текст ответа
        return completion.choices[0].message["content"]

