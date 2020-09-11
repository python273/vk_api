import json

from vk_api import VkApi
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


# Общие
GROUP_ID = "your_group_id"
GROUP_TOKEN = "your_group_token"
API_VERSION = "5.120"

# для callback-кнопки "открыть приложение"
APP_ID = 100500  # id IFrame приложения
OWNER_ID = 123456789  # id владельца приложения

# виды callback-кнопок
CALLBACK_TYPES = ("show_snackbar", "open_link", "open_app")


def main():
    # Запускаем бот
    vk_session = VkApi(token=GROUP_TOKEN, api_version=API_VERSION)
    vk = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, group_id=GROUP_ID)

    # Создаем 2 клавиатуры
    # №1. Клавиатура с 3 кнопками: "показать всплывающее сообщение", "открыть URL" и изменить меню (свой собственный тип)
    keyboard_1 = VkKeyboard(one_time=False, inline=True)
    keyboard_1.add_callback_button(
        label="Покажи pop-up сообщение",
        color=VkKeyboardColor.SECONDARY,
        payload={"type": "show_snackbar", "text": "Это исчезающее сообщение на экране"},
    )
    keyboard_1.add_line()
    keyboard_1.add_callback_button(
        label="Откртыть Url",
        color=VkKeyboardColor.POSITIVE,
        payload={"type": "open_link", "link": "https://vk.com/dev/bots_docs_5"},
    )
    keyboard_1.add_line()
    keyboard_1.add_callback_button(
        label="Открыть приложение",
        color=VkKeyboardColor.NEGATIVE,
        payload={
            "type": "open_app",
            "app_id": APP_ID,
            "owner_id": OWNER_ID,
            "hash": "anything_data_100500",
        },
    )
    keyboard_1.add_line()
    keyboard_1.add_callback_button(
        label="Добавить красного ",
        color=VkKeyboardColor.PRIMARY,
        payload={"type": "my_own_100500_type_edit"},
    )

    # №2. Клавиатура с одной красной callback-кнопкой. Нажатие изменяет меню на предыдущее.
    keyboard_2 = VkKeyboard(one_time=False, inline=True)
    keyboard_2.add_callback_button(
        "Назад",
        color=VkKeyboardColor.NEGATIVE,
        payload={"type": "my_own_100500_type_edit"},
    )

    # Запускаем пуллинг
    f_toggle: bool = False
    for event in longpoll.listen():
        # отправляем меню 1го вида на любое текстовое сообщение от пользователя
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.obj.message["text"] != "":
                if event.from_user:
                    # Если клиент пользователя не поддерживает callback-кнопки, нажатие на них будет отправлять текстовые
                    # сообщения. Т.е. они будут работать как обычные inline кнопки.
                    if "callback" not in event.obj.client_info["button_actions"]:
                        print(
                            f'Клиент user_id{event.obj.message["from_id"]} не поддерживает callback-кнопки.'
                        )

                    vk.messages.send(
                        user_id=event.obj.message["from_id"],
                        random_id=get_random_id(),
                        peer_id=event.obj.message["from_id"],
                        keyboard=keyboard_1.get_keyboard(),
                        message="Меню #1",
                    )
        # обрабатываем клики по callback кнопкам
        elif event.type == VkBotEventType.MESSAGE_EVENT:
            if event.object.payload.get("type") in CALLBACK_TYPES:
                r = vk.messages.sendMessageEventAnswer(
                    event_id=event.object.event_id,
                    user_id=event.object.user_id,
                    peer_id=event.object.peer_id,
                    event_data=json.dumps(event.object.payload),
                )
            elif event.object.payload.get("type") == "my_own_100500_type_edit":
                last_id = vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    message="Меню #2",
                    conversation_message_id=event.obj.conversation_message_id,
                    keyboard=(keyboard_1 if f_toggle else keyboard_2).get_keyboard(),
                )
                f_toggle = not f_toggle


if __name__ == "__main__":
    main()
