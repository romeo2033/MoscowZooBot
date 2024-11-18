from config import commands

# Приветственное сообщение
hello = '''👋 *Привет!

Давай узнаем твое тотемное животное! Рррр...*

_Отвечай на вопросы, используя кнопки ниже._

Помощь: /help'''

# Сообщение при выводе помощи
def for_help(): # Ф-я для вставки команд в текст из списка существующих
    text = '''🚨 *Спешу на помощь!*
✅ Вот список доступных команд бота:'''

    for command, description in commands.items():
        text += f'\n{command} - {description}'
    text += '''\n\n*🧐 По поводу викторины:*
Викторина проходится путем выбора ответа нажатием на кнопку. После викторины ты получаешь фото с тотемным животным и можешь опубликовать его в соц. сетях.

😻 Так же ты можешь узнать больше о программе опекунства после прохождения викторины либо выбрав соответсвующую команду из списка выше.'''

    return text

# Текст при перезапуске викторины
restart = '''👋 *Хорошо!
Давай попробуем ещё раз.*

_Отвечай на вопросы, используя кнопки ниже._'''

# Текст о программе опеки
custody = '''❤️*Возьмите животное под опеку!*❤️

✅ Участие в программе *«Клуб друзей зоопарка»* — это помощь в содержании наших обитателей, а также ваш личный вклад в дело сохранения биоразнообразия Земли и развитие нашего зоопарка.

📋 Основная задача Московского зоопарка с самого начала его существования это — сохранение биоразнообразия планеты. Когда вы берете под опеку животное, *вы помогаете нам* в этом благородном деле. При нынешних темпах развития цивилизации к 2050 году с лица Земли *могут исчезнуть* около 10 000 биологических видов. Московский зоопарк вместе с другими зоопарками мира делает все возможное, чтобы сохранить их.

🧑‍🧑‍🧒‍🧒 Традиция опекать животных в Московском зоопарке возникло с момента его создания в 1864г. Такая практика есть и в других зоопарках по всему миру. 

🙏 В настоящее время опекуны объединились в неформальное сообщество — *Клуб друзей Московского зоопарка.* Программа «Клуб друзей» дает возможность опекунам ощутить свою причастность к делу сохранения природы, участвовать в жизни Московского зоопарка и его обитателей, видеть конкретные результаты своей деятельности.

💖 *Опекать – значит помогать любимым животным.* Можно взять под крыло любого обитателя Московского зоопарка, в том числе и того, кто живет за городом – в Центре воспроизводства редких видов животных под Волоколамском. Там живут и размножаются виды, которых нет в городской части зоопарка: величественные журавли стерхи, забавные дрофы, исчезнувшая в природе лошадь Пржевальского, изящные антилопы бонго и многие другие. Можете съездить на экскурсию в Центр и познакомиться с обитателями.
'''

# При возникновении ошибки
for_error = 'Произошла ошибочка, мы скоро всё поправим. Обещаю!'

# При возникновении ошибки при обработке викторины
quiz_error = '''Произошла ошибка при обработке ответов :(
Начни викторину заново, нажав /start.'''

# Тотемное животное
totem = '''Твое тотемное животное...
Барабанная дробь!'''

# Подпись к картинке с тотемным животным
totem_caption = '''Опубликуй результат к себе на страничку в соцсетях!
Или заходи на наш канал 👍

*Не забывай, что можешь стать опекуном своего животного! (И не только своего!)*
_Подробнее по кнопке снизу_'''

# Текст ошибки выводимой в консоль при невозможности отправить сообщение сотруднику
no_admin_chat = 'Ошибка: невозможно отправить сообщение сотруднику Зоопарка. Чат не найден или не разрешил сообщения.'