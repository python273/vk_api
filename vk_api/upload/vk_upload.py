class vk_upload():
    def __init__(self, vk):
        self.vk = vk

    def photo(self, aid, photos):
        """ Загрузка изображений в альбом пользователя
        file1-file5
        photos = {'file1': open('my_photo.jpg', 'rb'), ...}
        """

        response = self.vk.method('photos.getUploadServer', {'aid': aid})
        response = response['response']

        url = response['upload_url']

        response = self.http.post(url, files=photos).json()
        response = self.vk.method('photos.save', response)
        return response
