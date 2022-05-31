from vk_api import VkUpload, VkApi
from vk_api.utils import get_random_id

def main():
    """ Пример отправки сообщения с фотографией, как вложения, загружаемого из ссылки """
    vk_session = VkApi(token="")
    link = "https://raw.githubusercontent.com/python273/vk_api/master/examples/messages_bot/bot.png" # ссылка для отправки
    peer_id = '' # ID получателя сообщения

    vk = vk_session.get_api()
    upload = VkUpload(vk)
    vk.messages.send(
        attachment=
            upload.from_link("photo_messages", link, peer_id = peer_id)
                .to_attachments(),
        user_id = peer_id,
        random_id = get_random_id(),
    )


if __name__ == "__main__":
    main()