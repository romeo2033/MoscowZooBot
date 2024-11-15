import telebot
from telebot import types
from config import TOKEN, animals, mapping, questions, pics, custody_text, admin_id, commands
import random
import time
from telebot.apihelper import ApiTelegramException
from extensions import QuizException, TelegramException

# Ваш токен Telegram бота
bot = telebot.TeleBot(TOKEN)

# Словарь для хранения данных пользователей
user_states = {}

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_quiz(message):
    chat_id = message.chat.id
    user_states[chat_id] = {'answers': [], 'current_question': 0}
    bot.send_message(chat_id, "👋 *Привет!\n\nДавай узнаем твое тотемное животное! Рррр...*\n\n_Отвечай на вопросы, используя кнопки ниже._\n\nПомощь: /help", parse_mode='Markdown')
    send_question(chat_id)

@bot.message_handler(commands=['help'])
def show_help(message):
    chat_id = message.chat.id
    text = '🚨 *Спешу на помощь!*\n\n✅ Вот список доступных команд бота:'
    for command, description in commands.items():
        text += f'\n{command} - {description}'
    text += ('\n\n*🧐 По поводу викторины:*'
             '\nВикторина проходится путем выбора ответа нажатием на кнопку. После викторины ты получаешь фото с тотемным животным и можешь опубликовать его в соц. сетях.'
             '\n\n😻 Так же ты можешь узнать больше о программе опекунства после прохождения викторины либо выбрав соответсвующую команду из списка выше.')
    bot.send_message(chat_id, text, parse_mode='Markdown')


def restart_quiz(call):
    chat_id = call.message.chat.id
    user_states[chat_id] = {'answers': [], 'current_question': 0}
    bot.send_message(chat_id, "👋 *Хорошо!\nДавай попробуем ещё раз.*\n\n_Отвечай на вопросы, используя кнопки ниже._", parse_mode='Markdown')
    send_question(chat_id)

@bot.message_handler(commands=['custody'])
def custody_info(call, totem_animal = 'Не прошел тест'):
    try:
        chat_id = call.message.chat.id
    except AttributeError:
        chat_id = call.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Подробнее о программе', url='https://moscowzoo.ru/about/guardianship'))
    markup.add(types.InlineKeyboardButton('💬 Сотрудник', callback_data=f'worker_{totem_animal}'))
    bot.send_message(chat_id, custody_text, parse_mode='Markdown')
    bot.send_photo(chat_id, open('pics/custody.png', 'rb'),reply_markup=markup)

def info_for_worker(message, totem_animal):
    chat_id = message.chat.id
    try:
        bot.send_message(admin_id, f'Пользователь хочет связаться с Вами\n\nРезультат викторины: {totem_animal}\n\nКонтактные данные и информация:\n\n📋{message.text}')
    except ApiTelegramException as e:
        if e.description == "Bad Request: chat not found":
            bot.send_message(chat_id, f'Произошла ошибка, мы скоро всё поправим. Обещаю!')
            raise TelegramException(f"Ошибка, невозможно отправить сообщение сотруднику Зоопарка")
        else:
            bot.send_message(chat_id, f'Произошла ошибка, мы скоро всё поправим. Обещаю!')
            raise TelegramException(f'Ошибка телеграмма: {e}')
    else:
        bot.send_message(chat_id,f'В ближайшее время с тобой свяжется сотрудник Зоопарка.\n\nТвои контактные данные и информация:\n\n📋{message.text}\n\n⏰Ожидай.')


@bot.message_handler(commands=['communicate'])
def chat_with_worker(call, totem_animal = 'Не проходил'):
    try:
        username = call.message.chat.username
        chat_id = call.message.chat.id
    except AttributeError:
        username = call.chat.username
        chat_id = call.chat.id
    else: pass

    if totem_animal in animals.keys():
        if username is not None:
            bot.send_message(admin_id,f'Пользователь @{username} хочет связаться с Вами\n\nРезультат викторины: {totem_animal}')
            bot.send_message(chat_id, f'В ближайшее время с тобой свяжется сотрудник Зоопарка.\n\n⏰Ожидай.')
        else:
            msg = bot.send_message(chat_id, f'Напиши свои контактные данные и информацию, чтобы сотрудник связался с тобой.')
            bot.register_next_step_handler(msg, info_for_worker, totem_animal)
    else:
        msg = bot.send_message(chat_id,f'Напиши свои контактные данные и информацию, чтобы сотрудник связался с тобой.')
        bot.register_next_step_handler(msg, info_for_worker, totem_animal)

@bot.callback_query_handler(func=lambda call: call.data.startswith('worker'))
def handle_callback_query(call):
    totem_animal = call.data.split('_')[1]
    chat_with_worker(call, totem_animal)

# Функция отправки вопроса
def send_question(chat_id):
    user_state = user_states[chat_id]
    question_index = user_state['current_question']

    if question_index < len(questions):
        question_data = questions[question_index]
        markup = types.InlineKeyboardMarkup()
        for idx, option in enumerate(question_data['options']):
            callback_data = f"q_{question_index}_a_{idx}"
            button = types.InlineKeyboardButton(option, callback_data=callback_data)
            markup.add(button)
        bot.send_message(chat_id, question_data['question'], reply_markup=markup, parse_mode='Markdown')
    else:
        # Все вопросы заданы, определить тотемное животное
        determine_totem_animal(chat_id)

# Обработчик callback_query
@bot.callback_query_handler(func=lambda call: call.data.startswith('q_'))
def handle_callback_query(call):
    chat_id = call.message.chat.id
    data = call.data.split('_')
    question_index = int(data[1])
    answer_index = int(data[3])

    if chat_id in user_states:
        user_state = user_states[chat_id]
        if user_state['current_question'] == question_index:
            # Получаем текст ответа по индексу
            question_data = questions[question_index]
            answer = question_data['options'][answer_index]
            # Сохранить ответ пользователя
            user_state['answers'].append(answer)
            user_state['current_question'] += 1
            # Удаляем предыдущие кнопки
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=None)
            send_question(chat_id)
        else:
            bot.answer_callback_query(call.id, text="Пожалуйста, дождись следующего вопроса!")
    else:
        bot.send_message(chat_id, "Нажми /start, чтобы начать викторину.")

# Функция определения тотемного животного
def determine_totem_animal(chat_id):
    user_state = user_states[chat_id]
    user_characteristics = []
    for i, answer in enumerate(user_state['answers']):
        characteristic = map_answer_to_characteristic(i, answer, chat_id)
        if characteristic:
            user_characteristics.append(characteristic)
        else:
            bot.send_message(chat_id, "Произошла ошибка при обработке ответов :(\nНачните викторину заново, нажав /start.", parse_mode='Markdown')
            del user_states[chat_id]
            raise QuizException('Ошибка при обработке ответов: ответы пользователя не записаны')


    # Подсчет совпадений с животными
    scores = {}
    for animal, characteristics in animals.items():
        score = sum(1 for char in user_characteristics if char in characteristics)
        scores[animal] = score

    max_score = max(scores.values())
    top_animals = [animal for animal, score in scores.items() if score == max_score]

    totem_animal = random.choice(top_animals)
    photo_path = f'pics/{pics[totem_animal]}.jpg'
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Instagram', url='https://instagram.com'))
    markup.add(types.InlineKeyboardButton('ВКонтакте', url='https://vk.com'))
    markup.add(types.InlineKeyboardButton('Наш Telegram!', url='https://t.me/Moscowzoo_official'))
    markup.add(types.InlineKeyboardButton('Попробовать ещё раз?', callback_data='continue_restart'))
    markup.add(types.InlineKeyboardButton('❗️Опекунство❗️', callback_data=f'continue_custody|{totem_animal}'))

    bot.send_message(chat_id, f"Твое тотемное животное...\nБарабанная дробь!", parse_mode='Markdown')
    time.sleep(2)
    bot.send_photo(chat_id, open(photo_path, 'rb'), caption='Опубликуй результат к себе на страничку в соцсетях!\nИли заходи на наш канал 👍\n\n*Не забывай, что можешь стать опекуном своего животного!*\n_Подробнее по кнопке снизу_',reply_markup=markup, parse_mode='Markdown')
    # Очистка данных пользователя
    del user_states[chat_id]

@bot.callback_query_handler(func=lambda call: call.data.startswith('continue'))
def handle_callback_query(call):
    if call.data == 'continue_restart':
        restart_quiz(call)
    elif call.data.startswith('continue_custody'):
        totem_animal = call.data.split('|')[1]
        custody_info(call, totem_animal = totem_animal)

# Функция сопоставления ответа пользователя с характеристикой
def map_answer_to_characteristic(question_index, answer, chat_id):
    try:
        return mapping[question_index][answer]
    except KeyError:
        bot.send_message(chat_id, "Произошла ошибочка... Возвращайся позднее, мы все поправим!")
        raise QuizException(f"Ошибка: вопрос {question_index}, ответ '{answer}' не найден")

# Запуск бота
bot.infinity_polling(allowed_updates=['message', 'callback_query'])