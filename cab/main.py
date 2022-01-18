from __init__ import bot, join, DBSession, User, DBManager, exists, check_photos, \
    TgRequest, Telegram, AuthorizationState, api_id, api_hash, database_encryption_key
tg_requests = {}


@bot.message_handler(commands=['start'])
def register(message):
    session = DBSession()
    db = DBManager(session)
    with db:
        user = User(chat_id=message.chat.id)
        user_already_exists = db.add_new_user(user)
        if user_already_exists is False:
            bot.send_message(message.chat.id, 'Приветствую, новый пользователь!')
        bot.send_message(message.chat.id, 'Я меняю аватарку в твоём профиле телеграмм в соответсвии со статусом, который ты поставишь! '
                                          'Отправь мне фото с подписью названием статуса для этого фото, например:')
        bot.send_photo(chat_id=message.chat.id, caption="отпуск", photo=open("example.jpg", 'rb'))
        bot.send_message(message.chat.id,
                         'Когда ты создашь свой первый фото-статус, я запомню ключевое слово в подписи. '
                         'Поэтому когда ты захочешь поменять аватарку, просто напиши мне "отпуск", и твоя ава поменяется на отпускную)')
        bot.send_message(message.chat.id,
                         "Ты можешь переслать мне сообщение с фото-примером выше, для того, чтобы сразу проверить как это работает!")


@bot.message_handler(content_types=["photo"])
def get_photo(message):
    session = DBSession()
    db = DBManager(session)
    with db:
        user = User(chat_id=message.chat.id)
        user = db.get_user_from_db(user)
        if user:
            i = check_photos(message.photo)
            file_id_info = bot.get_file(message.photo[i].file_id)
            downloaded_file = bot.download_file(file_id_info.file_path)
            with open(f'avatars/{message.chat.id}{message.caption}.jpg', 'wb') as new_file:
                new_file.write(downloaded_file)
            bot.send_message(message.chat.id, text='Ваше фото успешно загружено! Чтобы установить фото-статус напишите слово, которое вы указали в подписи к фото.')
        else:
            bot.send_message(message.chat.id, text="Прежде чем отправлять мне фото, начните работу через команду /start")


@bot.message_handler(content_types=["contact"])
def get_contact(message):
    session = DBSession()
    db = DBManager(session)
    with db:
        user = User(chat_id=message.chat.id, phone=message.contact.phone_number)
        user = db.update_or_add(user)
        bot.send_message(message.chat.id, text=f"Проверьте ваш номер телефона {user.phone} \n "
                                               f"Чтобы пройти авторизацию, используйте команду /auth")


@bot.message_handler(commands=['auth'])
def auth(message):
    session = DBSession()
    db = DBManager(session)
    with db:
        user = db.get_user_from_db(User(chat_id=message.chat.id))
        if user.phone is not None:
            tr = TgRequest(tg_class=Telegram(api_id=api_id,
                                             api_hash=api_hash,
                                             phone=user.phone,
                                             database_encryption_key=database_encryption_key, ),
                           data=None,
                           user_id=user.chat_id)
            auth_state = tr.tg_class.login(blocking=False)
            if auth_state == AuthorizationState.WAIT_CODE:
                bot.send_message(message.chat.id, text="Отправьте код подтверждения с помощью команды /code код подтверждения")
            if auth_state == AuthorizationState.WAIT_PASSWORD:
                bot.send_message(message.chat.id, text="Отправьте облачный пароль с помощью команды /password пароль")
            tg_requests.update({user.chat_id: tr})
            print(tg_requests)
        else:
            bot.send_message(message.chat.id, text="Для начала отправьте свой контакт, чтобы я узнал ваш номер телефона")


@bot.message_handler(commands=['code'])
def send_code(message):
    code = int(message.text.split(" ")[1])
    tr = tg_requests[message.chat.id]
    tr.tg_class.send_code(code)
    auth_state = tr.tg_class.login(blocking=False)
    if auth_state == AuthorizationState.WAIT_CODE:
        bot.send_message(message.chat.id, text="Отправьте код подтверждения с помощью команды /code код подтверждения")
    if auth_state == AuthorizationState.WAIT_PASSWORD:
        bot.send_message(message.chat.id, text="Отправьте облачный пароль с помощью команды /password пароль")
    bot.send_message(message.chat.id, text={auth_state})


@bot.message_handler(commands=['password'])
def send_password(message):
    password = int(message.text.split(" ")[1])
    tr = tg_requests[message.chat.id]
    tr.tg_class.send_password(password)
    auth_state = tr.tg_class.login(blocking=False)
    bot.send_message(message.chat.id, text={auth_state})


@bot.message_handler(content_types=["text"])
def set_photo(message):
    try:
        print(tg_requests[message.chat.id].tg_class.authorization_state)
        if tg_requests[message.chat.id].tg_class.authorization_state == AuthorizationState.READY:
            photo_path = join("avatars", f"{message.chat_id}{message.text}.jpg")
            if exists(photo_path):
                tr = tg_requests[message.chat.id]
                data = {
                    '@type': 'setProfilePhoto',
                    'photo': {
                        '@type': 'inputChatPhotoStatic',
                        'photo': {
                            "@type": "inputFileLocal",
                            "path": photo_path
                        }
                    }
                }
                tr.data = data
                r = tr.tg_class._send_data(data)
                r.wait()
                if r.error():
                    print(r.error_info)

            else:
                bot.send_message(message.chat.id, text=f"Фото для статуса '{message.text}' не было отправлено боту.")
                return None
        else:
            bot.send_message(message.chat.id, text="Для начала необходимо пройти авторизацию! Используй команду /auth")
    except Exception as e:
        print(e.args[0], e.args[1])


bot.polling(none_stop=True)
