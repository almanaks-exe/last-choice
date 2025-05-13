import telebot
import time
import threading

TOKEN = '8148223584:AAEK3RefhDYpfdV5yC4pUw7AWLFaL-kluhw'
bot = telebot.TeleBot(TOKEN)

# Глобальные переменные
creator_id = None
companion_id = None
password_required = True
messages_from_creator = []
activated = False

# Состояния пользователей
user_states = {}

# Пароль и правильный ответ
PASSWORD = "newfreedom"
TRUE_NAME = "Айден"

# Хендлер команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    global password_required
    user_id = message.from_user.id

    if not password_required:
        if creator_id is None:
            bot.send_message(user_id, "Бот уже активирован.")
        elif user_id == creator_id:
            bot.send_message(user_id, "Вы уже авторизованы как создатель.")
        else:
            bot.send_message(user_id, "Введите ответ на вопрос: моё настоящее имя.")
            user_states[user_id] = "awaiting_name"
        return

    if creator_id is None:
        bot.send_message(user_id, "Введите пароль:")
        user_states[user_id] = "awaiting_password"
    else:
        bot.send_message(user_id, "Ожидается активация от другого пользователя.")

# Обработка текстовых сообщений
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    global creator_id, password_required, companion_id, activated

    user_id = message.from_user.id
    text = message.text.strip()

    state = user_states.get(user_id)

    # Проверка пароля
    if state == "awaiting_password":
        if text == PASSWORD:
            creator_id = user_id
            password_required = False
            user_states[user_id] = "writing_messages"
            bot.send_message(user_id, "Вы стали создателем. Введите ваши сообщения, одно за другим. Напишите /done, когда закончите.")
        else:
            bot.send_message(user_id, "Неверный пароль. Попробуйте снова.")
        return

    # Сбор сообщений от создателя
    if state == "writing_messages" and user_id == creator_id:
        if text == "/done":
            bot.send_message(user_id, "Сообщения сохранены. Ожидаем собеседника.")
            user_states[user_id] = "waiting_companion"
        else:
            messages_from_creator.append(text)
        return

    # Проверка имени
    if state == "awaiting_name":
        if text == TRUE_NAME and companion_id is None:
            companion_id = user_id
            bot.send_message(user_id, "Вы стали собеседником.")
            bot.send_message(creator_id, "Собеседник найден. Начинаем диалог.")
            threading.Thread(target=send_creator_messages).start()
        else:
            bot.send_message(user_id, "Неверно. Попробуйте снова.")
        return

    # Опрос
    if state == "awaiting_confirmation" and user_id == companion_id:
        if text.lower() == "да":
            activated = True
            user_states[user_id] = "chatting"
            user_states[creator_id] = "chatting"
            bot.send_message(user_id, "Теперь вы можете общаться с создателем.")
            bot.send_message(creator_id, "Собеседник готов к общению.")
        elif text.lower() == "нет":
            bot.send_message(user_id, "Вы не предприняли попытку понять. Бот отключается.")
            bot.send_message(creator_id, "Попытка общения не удалась.")
            user_states.clear()
        else:
            bot.send_message(user_id, "Пожалуйста, прочитайте сообщение внимательно и ответьте 'Да' или 'Нет'.")
        return

    # Обмен сообщениями
    if activated and user_states.get(user_id) == "chatting":
        if user_id == creator_id:
            bot.send_message(companion_id, f"{text}")
        elif user_id == companion_id:
            bot.send_message(creator_id, f"{text}")
        return

def send_creator_messages():
    time.sleep(1)
    bot.send_message(companion_id, "Внимательно прочитайте следующие сообщения от создателя. Отвечать не нужно до конца.")
    for msg in messages_from_creator:
        time.sleep(1)
        bot.send_message(companion_id, msg)
    time.sleep(1)
    bot.send_message(companion_id, "Вы поняли сообщение и готовы поговорить со мной? Ответьте: Да или Нет")
    user_states[companion_id] = "awaiting_confirmation"

bot.polling()