import requests
from config import vk_api_key, vk_group_id


def check_vk_api():
    base_url = "https://api.vk.com/method/"
    method = "groups.getById"
    params = {
        "group_id": vk_group_id,
        "access_token": vk_api_key,
        "v": "5.199"
    }

    try:
        # Временно отключаем проверку SSL
        response = requests.get(
            f"{base_url}{method}",
            params=params,
            verify=False  # <-- Отключение проверки сертификата
        )
        response.raise_for_status()

        data = response.json()
        print("Ответ:", data)  # Для детального анализа

    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    check_vk_api()