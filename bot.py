import telebot
import random
import time
import texts
from telebot import types
from telebot.apihelper import ApiTelegramException
from extensions import QuizException, TelegramException
from config import TOKEN, animals, mapping, questions, pics, admin_id

# Создание объекта бота
bot = telebot.TeleBot(TOKEN)

# Словарь для хранения данных пользователей
user_states = {}

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_quiz(message):
    chat_id = message.chat.id # Получение ID пользователя
    user_states[chat_id] = {'answers': [], 'current_question': 0} # Создание элемента словаря для пользователя с его ответами и текущим вопросом
    bot.send_message(chat_id, texts.hello, parse_mode='Markdown') # Отправка сообщения пользователю с форматированием Markdown для жирного и курсивного текста
    send_question(chat_id) # Запуск функции для прохождения викторины

# Обработчик команды /help
@bot.message_handler(commands=['help'])
def show_help(message):
    chat_id = message.chat.id
    text = texts.for_help()
    bot.send_message(chat_id, text, parse_mode='Markdown')

# Ф-я перезапуска викторины
def restart_quiz(call):
    chat_id = call.message.chat.id
    user_states[chat_id] = {'answers': [], 'current_question': 0}
    bot.send_message(chat_id, texts.restart, parse_mode='Markdown')
    send_question(chat_id)

# Обработчик команды /custody
@bot.message_handler(commands=['custody'])
def custody_info(call, totem_animal = 'Не проходил тест'): # Ф-я для отправки пользователю информации о программе опекунства
    # Получение chat_id при вызове по кнопке или при написании команды
    try:
        chat_id = call.message.chat.id
    except AttributeError:
        chat_id = call.chat.id

    # Создание кнопок под сообщением
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Подробнее о программе', url='https://moscowzoo.ru/about/guardianship'))
    markup.add(types.InlineKeyboardButton('💬 Сотрудник', callback_data=f'worker_{totem_animal}'))

    bot.send_message(chat_id, texts.custody, parse_mode='Markdown')
    # Отправка фото
    bot.send_photo(chat_id, open('pics/custody.png', 'rb'),reply_markup=markup)

# Ф-я для отправки сообщения сотруднику при необходимости связаться
def info_for_worker(message, totem_animal):
    chat_id = message.chat.id
    # Попытка отправить сообщение сотруднику
    try:
        bot.send_message(admin_id, f'Пользователь хочет связаться с Вами\n\nРезультат викторины: {totem_animal}\n\nКонтактные данные и информация:\n\n📋{message.text}')
    except ApiTelegramException as e:
        # При несуществующем чате
        if e.description == "Bad Request: chat not found":
            bot.send_message(chat_id, texts.for_error)
            raise TelegramException(texts.no_admin_chat)
        # При другой ошибке телеграмма
        else:
            bot.send_message(chat_id, texts.for_error)
            raise TelegramException(f'Ошибка телеграмма: {e}')
    else:
        bot.send_message(chat_id,f'В ближайшее время с тобой свяжется сотрудник Зоопарка.\n\nТвои контактные данные и информация:\n\n📋{message.text}\n\n⏰Ожидай.')

@bot.message_handler(commands=['communicate'])
def chat_with_worker(call, totem_animal = 'Нет данных'): # Ф-я для связи с работником
    try:
        username = call.message.chat.username
        chat_id = call.message.chat.id
    except AttributeError:
        username = call.chat.username
        chat_id = call.chat.id
    else: pass

    # Проверка, проходил ли пользователь викторину
    if totem_animal in animals.keys():
        # Проверка, имеет ли пользователь username в TG
        if username is not None:
            bot.send_message(admin_id,f'Пользователь @{username} хочет связаться с Вами\n\nРезультат викторины: {totem_animal}')
            bot.send_message(chat_id, f'В ближайшее время с тобой свяжется сотрудник Зоопарка.\n\n⏰Ожидай.')
        else:
            msg = bot.send_message(chat_id, f'Напиши свои контактные данные и информацию, чтобы сотрудник связался с тобой.')
            bot.register_next_step_handler(msg, info_for_worker, totem_animal)
    else:
        msg = bot.send_message(chat_id,f'Напиши свои контактные данные и информацию, чтобы сотрудник связался с тобой.')
        bot.register_next_step_handler(msg, info_for_worker, totem_animal)

# Обработчик кнопки для связи с сотрудником
@bot.callback_query_handler(func=lambda call: call.data.startswith('worker'))
def handle_callback_query(call):
    # Определение результата викторины из данных от кнопки
    totem_animal = call.data.split('_')[1]
    # Вызов функции для связи с сотрудником
    chat_with_worker(call, totem_animal)

# Функция отправки вопросов
def send_question(chat_id):
    user_state = user_states[chat_id]
    question_index = user_state['current_question']

    # Проверка, все ли вопросы заданы, если нет, то отправка следующего
    if question_index < len(questions):
        # Определение данных вопроса по его номеру
        question_data = questions[question_index]
        markup = types.InlineKeyboardMarkup()

        # Создание кнопок с вариантами ответа
        for idx, option in enumerate(question_data['options']):
            callback_data = f"q_{question_index}_a_{idx}"
            button = types.InlineKeyboardButton(option, callback_data=callback_data)
            markup.add(button)
        # Отправка сообщения с кнопками ответов
        bot.send_message(chat_id, question_data['question'], reply_markup=markup, parse_mode='Markdown')
    else:
        # Все вопросы заданы, определяем тотемное животное
        determine_totem_animal(chat_id)

# Обработчик кнопок с ответами
@bot.callback_query_handler(func=lambda call: call.data.startswith('q_'))
def handle_callback_query(call):
    chat_id = call.message.chat.id
    data = call.data.split('_')
    question_index = int(data[1])
    answer_index = int(data[3])

    # Проверка, проходил ли пользователь викторину
    if chat_id in user_states:
        user_state = user_states[chat_id]
        if user_state['current_question'] == question_index:
            # Получаем текст ответа по индексу
            question_data = questions[question_index]
            answer = question_data['options'][answer_index]
            # Сохраняем ответ пользователя
            user_state['answers'].append(answer)
            user_state['current_question'] += 1
            # Удаляем предыдущие кнопки
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=None)
            send_question(chat_id)
        else:
            bot.answer_callback_query(call.id, text="Пожалуйста, дождись следующего вопроса!")
    else:
        bot.send_message(chat_id, "Нажми /start, чтобы начать викторину.")

# Ф-я отправки отзыва сотруднику
def send_feedback(message):
    chat_id = message.chat.id
    username = message.chat.username
    try:
        if username is not None:
            bot.send_message(admin_id, f'Пользователь @{username} оставил ОС:\n\n⭐️ Отзыв:\n{message.text}')
        else:
            bot.send_message(admin_id, f'Пользователь оставил ОС:\n\n⭐️ Отзыв:\n{message.text}')
    except ApiTelegramException as e:
        if e.description == "Bad Request: chat not found":
            bot.send_message(chat_id, texts.for_error)
            raise TelegramException(texts.no_admin_chat)
        else:
            bot.send_message(chat_id, texts.for_error)
            raise TelegramException(f'Ошибка телеграмма: {e}')
    else:
        bot.send_message(chat_id,f'Спасибо за оставленную обратную связь, стараемся для тебя! 💖')

# Обработчик команды для оставления ОС
@bot.message_handler(commands=['feedback'])
def feedback(call):
    try:
        chat_id = call.message.chat.id
    except AttributeError:
        chat_id = call.chat.id

    msg = bot.send_message(chat_id,f'⭐️ Оставь обратную связь о нашей викторине, написав оценку и твои пожелания в сообщении:')
    # Регистрируем обработчик для конкретного сообщения
    bot.register_next_step_handler(msg, send_feedback)


# Функция определения тотемного животного
def determine_totem_animal(chat_id):
    user_state = user_states[chat_id]
    user_characteristics = []
    for i, answer in enumerate(user_state['answers']):
        characteristic = map_answer_to_characteristic(i, answer, chat_id)
        if characteristic:
            user_characteristics.append(characteristic)
        else:
            bot.send_message(chat_id, texts.quiz_error, parse_mode='Markdown')
            del user_states[chat_id]
            raise QuizException('Ошибка при обработке ответов: ответы пользователя не записаны')

    # Подсчет совпадений с животными
    scores = {}
    for animal, characteristics in animals.items():
        score = sum(1 for char in user_characteristics if char in characteristics)
        scores[animal] = score

    max_score = max(scores.values())
    top_animals = [animal for animal, score in scores.items() if score == max_score]

    # Выбор рандомного животного, если по результатам несколько подходят
    totem_animal = random.choice(top_animals)
    # Выбор конкретной фотографии животного
    photo_path = f'pics/{pics[totem_animal]}.jpg'

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Instagram', url='https://instagram.com'))
    markup.add(types.InlineKeyboardButton('ВКонтакте', url='https://vk.com'))
    markup.add(types.InlineKeyboardButton('Наш Telegram!', url='https://t.me/Moscowzoo_official'))
    markup.add(types.InlineKeyboardButton('Попробовать ещё раз?', callback_data='continue_restart'))
    markup.add(types.InlineKeyboardButton('⭐️ Оставить отзыв', callback_data='continue_feedback'))
    markup.add(types.InlineKeyboardButton('❗️Опекунство❗️', callback_data=f'continue_custody|{totem_animal}'))

    bot.send_message(chat_id, texts.totem, parse_mode='Markdown')
    # 2-х секундная пауза для "интриги"
    time.sleep(2)
    # Отправка фото с животным, подходящего для публикации в соц. сети
    bot.send_photo(chat_id, open(photo_path, 'rb'), caption=texts.totem_caption, reply_markup=markup, parse_mode='Markdown')
    # Очистка данных пользователя
    del user_states[chat_id]

# Обработчик кнопок по завершении викторины
@bot.callback_query_handler(func=lambda call: call.data.startswith('continue'))
def handle_callback_query(call):
    if call.data == 'continue_restart':
        restart_quiz(call)
    elif call.data.startswith('continue_custody'):
        totem_animal = call.data.split('|')[1]
        custody_info(call, totem_animal = totem_animal)
    elif call.data == 'continue_feedback':
        feedback(call)

# Функция сопоставления ответа пользователя с характеристикой
def map_answer_to_characteristic(question_index, answer, chat_id):
    # Проверка, существует ли хар-ка, подходящая к ответу пользователя
    try:
        return mapping[question_index][answer]
    except KeyError:
        bot.send_message(chat_id, texts.for_error)
        raise QuizException(f"Ошибка: вопрос {question_index}, ответ '{answer}' не найден")

# Запуск бота в режиме постоянного ожидания новых сообщений
bot.infinity_polling(allowed_updates=['message', 'callback_query'], none_stop = True)