import requests
import datetime

class VKStats:
    def __init__(self, vk_api_key, group_id):
        self.vk_api_key = vk_api_key
        self.group_id = group_id

    def get_stats(self, start_date, end_date):
        # Укажите корректный URL для метода stats.get (допустим, он должен быть "https://api.vk.com/method/stats.get")
        url = "https://api.vk.com/method/stats.get"  # <-- Исправлено: укажите реальный URL API
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

        start_date = start_date.replace(tzinfo=datetime.timezone.utc)
        end_date = end_date.replace(tzinfo=datetime.timezone.utc)

        start_unix_time = start_date.timestamp()
        end_unix_time = end_date.timestamp()

        params = {
            'access_token': self.vk_api_key,
            'v': '5.236',
            'group_id': self.group_id,
            'timestamp_from': start_unix_time,
            'timestamp_to': end_unix_time
        }
        # Добавляем verify=False для отключения проверки SSL
        response = requests.get(url, params=params, verify=False).json()  #  <searchIndex index="1" ></searchIndex>
        if 'error' in response:
            raise Exception(response['error']['error_msg'])
        else:
            return response['response'][0]

    def get_followers(self):
        # Укажите корректный URL для метода groups.getMembers (допустим, "https://api.vk.com/method/groups.getMembers")
        url = "https://api.vk.com/method/groups.getMembers"  # <-- Исправлено: укажите реальный URL API
        params = {
            'access_token': self.vk_api_key,
            'v': '5.236',
            'group_id': self.group_id
        }
        # Добавляем verify=False для отключения проверки SSL
        response = requests.get(url, params=params, verify=False).json()  #  <searchIndex index="2" ></searchIndex>
        if 'error' in response:
            raise Exception(response['error']['error_msg'])
        else:
            return response['response']['count']