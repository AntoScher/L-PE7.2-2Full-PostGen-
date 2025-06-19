# generators/text_gen_ds.py

import os
import logging
import time
from openai import OpenAI
from google.api_core.exceptions import ResourceExhausted

logger = logging.getLogger(__name__)


class PostGenerator:
    """
    Класс для генерации текстового контента с помощью модели DeepSeek.
    """

    def __init__(self, api_key: str, tone: str, topic: str, model_name: str = "deepseek-chat"):
        """
        Инициализация клиента и параметров поста.

        Args:
            api_key (str): API-ключ от DeepSeek.
            tone (str): Тон, в котором должен быть написан пост.
            topic (str): Тема поста.
            model_name (str): Название используемой модели.
        """
        logger.info("Инициализация генератора текста DeepSeek...")

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        self.model = model_name
        self.tone = tone
        self.topic = topic
        logger.info("Текстовый генератор DeepSeek готов к работе.")

    def _generate_content(self, system_prompt: str, user_prompt: str, max_retries: int = 3) -> str | None:
        """
        Общий метод для генерации контента с обработкой ошибок и повторными попытками.

        Args:
            system_prompt (str): Системная инструкция
            user_prompt (str): Пользовательский запрос
            max_retries (int): Максимальное количество попыток

        Returns:
            str | None: Сгенерированный текст
        """
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7 if "описание" in system_prompt else 0.4,
                    max_tokens=2048
                )

                if response.choices and response.choices[0].message.content:
                    return response.choices[0].message.content.strip().strip('"')
                else:
                    logger.warning(f"Пустой ответ от DeepSeek (попытка {attempt + 1}/{max_retries})")

            except Exception as e:
                logger.error(f"Ошибка генерации: {e}")
                if "rate limit" in str(e).lower():
                    wait_time = (attempt + 1) * 5
                    logger.warning(f"Достигнут лимит квот. Повтор через {wait_time} сек...")
                    time.sleep(wait_time)
                else:
                    return None

        logger.error(f"Не удалось получить ответ после {max_retries} попыток")
        return None

    def generate_post(self) -> str | None:
        """
        Генерирует текст поста для социальных сетей.
        """
        system_prompt = f"Ты высококвалифицированный SMM специалист, который генерирует тексты для постов. Тон сообщений: {self.tone}."
        user_prompt = f"Сгенерируй пост для соцсетей на тему: '{self.topic}'. Пост должен быть привлекательным, содержательным и соответствовать тону {self.tone}."

        logger.info(f"Генерация поста: тема='{self.topic}', тон='{self.tone}'")
        return self._generate_content(system_prompt, user_prompt)

    def generate_post_image_description(self) -> str | None:
        """
        Генерирует детализированный промпт для модели генерации изображений.
        """
        system_prompt = (
            "Ты — эксперт по созданию промптов для генерации изображений. "
            "Генерируй только англоязычные промпты для моделей типа Imagen или Midjourney. "
            "Промпт должен включать: объект, окружение, стиль, освещение, детали. Пример: "
            "'photo of a sleek, modern kitchen knife with Damascus steel pattern, resting on dark granite next to chopped vegetables, cinematic lighting, ultra-realistic, 8k'."
        )
        user_prompt = f"Создай промпт для генерации изображения на тему: '{self.topic}'."

        logger.info(f"Генерация промпта для изображения: тема='{self.topic}'")
        return self._generate_content(system_prompt, user_prompt)