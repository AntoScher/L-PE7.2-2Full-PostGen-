import requests

class VKPublisher:
    def __init__(self, vk_api_key, group_id):
        self.vk_api_key = vk_api_key
        self.group_id = group_id

    def upload_photo(self, image_url):
        # 1. Запрос к photos.getWallUploadServer (добавляем verify=False)
        upload_url_response = requests.get(
            'https://api.vk.com/method/photos.getWallUploadServer',  # Укажите реальный URL
            params={
                'access_token': self.vk_api_key,
                'v': '5.236',
                'group_id': self.group_id
            },
            verify=False  #  <searchIndex index="1" ></searchIndex>
        ).json()

        if 'error' in upload_url_response:
            raise Exception(upload_url_response['error']['error_msg'])
        else:
            upload_url = upload_url_response['response']['upload_url']
            image_data = requests.get(image_url).content  # Это внешний URL, verify не нужен
            # 2. Запрос к загрузке фото (добавляем verify=False)
            upload_response = requests.post(
                upload_url,
                files={'photo': ('image.jpg', image_data)},
                verify=False  #  <searchIndex index="2" ></searchIndex>
            ).json()

            # 3. Запрос к photos.saveWallPhoto (добавляем verify=False)
            save_response = requests.get(
                'https://api.vk.com/method/photos.saveWallPhoto',  # Укажите реальный URL
                params={
                    'access_token': self.vk_api_key,
                    'v': '5.236',
                    'group_id': self.group_id,
                    'photo': upload_response['photo'],
                    'server': upload_response['server'],
                    'hash': upload_response['hash']
                },
                verify=False  #  <searchIndex index="3" ></searchIndex>
            ).json()

            photo_id = save_response['response'][0]['id']
            owner_id = save_response['response'][0]['owner_id']

            return f'photo{owner_id}_{photo_id}'

    def publish_post(self, content, image_url=None):
        # 4. Запрос к wall.post (добавляем verify=False)
        params = {
            'access_token': self.vk_api_key,
            'from_group': 1,
            'v': '5.236',
            'owner_id': f'-{self.group_id}',
            'message': content
        }
        if image_url:
            attachment = self.upload_photo(image_url)
            params['attachments'] = attachment

        response = requests.post(
            'https://api.vk.com/method/wall.post',  # Укажите реальный URL
            params=params,
            verify=False  #  <searchIndex index="4" ></searchIndex>
        ).json()
        return response