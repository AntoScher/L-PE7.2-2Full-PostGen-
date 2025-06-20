import os
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
from google.cloud import storage
from datetime import datetime, timedelta
from PIL import Image
from io import BytesIO
import logging
import re
from google.api_core.exceptions import ResourceExhausted

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImagenGenerator:
    """
    Класс для генерации изображений с использованием Google Cloud Imagen.
    """

    def __init__(self, project_id: str, location: str, gcs_bucket_name: str):
        """
        Инициализация генератора изображений.

        Args:
            project_id (str): ID проекта Google Cloud
            location (str): Регион (например, 'us-central1')
            gcs_bucket_name (str): Имя GCS бакета
        """
        logger.info("Инициализация ImagenGenerator...")
        vertexai.init(project=project_id, location=location)
        self.storage_client = storage.Client(project=project_id)
        self.bucket = self.storage_client.bucket(gcs_bucket_name)
        self.model = ImageGenerationModel.from_pretrained("imagegeneration@005")  # Исправленная версия модели
        logger.info("Генератор готов к работе")

    def generate_image(self, prompt: str) -> str | None:
        """
        Генерирует изображение, сохраняет локально и в GCS, возвращает временный URL

        Args:
            prompt (str): Описание для генерации изображения

        Returns:
            str | None: Signed URL изображения или None при ошибке
        """
        logger.info(f"Генерация изображения по промпту: '{prompt}'")

        # Генерация безопасного имени файла
        safe_prompt = re.sub(r"[^\w\d-]", "_", prompt)[:50]
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_prompt}.jpg"
        local_path = os.path.join("generated_images", filename)

        try:
            # 1. Генерация изображения
            response = self.model.generate_images(
                prompt=prompt,
                number_of_images=1
            )

            if not response.images:
                logger.error("API не вернуло изображений")
                return None

            # 2. Получение изображения в виде байтов
            image_bytes = response.images[0]._image_bytes


            """# 3. Сохранение локально
            os.makedirs("generated_images", exist_ok=True)
            with Image.open(BytesIO(image_bytes)) as img:
                img.save(local_path)
            logger.info(f"Изображение сохранено локально: {local_path}")
            """
            # 4. Загрузка в GCS
            blob = self.bucket.blob(f"project-images/{filename}")
            blob.upload_from_string(image_bytes, content_type="image/jpeg")
            logger.info(f"Изображение загружено в GCS: gs://{self.bucket.name}/project-images/{filename}")

            # 5. Генерация временного URL
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=60),
                method="GET"
            )
            logger.info("Временный URL сгенерирован")

            return signed_url

        except ResourceExhausted:
            logger.error("Достигнут лимит квот Vertex AI. Повторите попытку позже.")
            return None
        except Exception as e:
            logger.error(f"Ошибка при генерации изображения: {str(e)}")
            return None