from telegram.client import Telegram


def check_photos(photo: list) -> int:
    for i in range(3, 0, -1):
        try:
            if photo[i].height < 1280 and photo[i].height < 1280:
                return i
        except IndexError:
            continue


class TgRequest:
    def __init__(self, tg_class: Telegram, data, user_id):
        self.tg_class = tg_class
        self.data = data
        self.user_id = user_id
