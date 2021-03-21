import os
import telebot

from telebot import types
from logic import (
    get_answer
)
from database_functions import (
    get_user, 
    add_user,
    update_user
)


TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)

GENDER = {
    'Женский': 2,
    'Мужской': 1,
    'Не указывать': 0
}

ADULT = {
    'Да': 1,
    'Нет': 0
}

@bot.message_handler(content_types=['text'])
def handle_messages(message):
    bot.send_message(message.from_user.id, "Привет")
    user = get_user(message.from_user.id)
    print(user)
    if not user:
        add_user(message.from_user.id,0,0)
        keyboard = types.ReplyKeyboardMarkup()
        key_yes = types.KeyboardButton(text='Да')
        keyboard.add(key_yes)
        key_no = types.KeyboardButton(text='Нет')
        keyboard.add(key_no)
        question = 'Вы совершеннолетний?'
        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
        bot.register_next_step_handler(message, get_adult)
    else:
        bot.send_message(message.from_user.id, "Опишите Ваши симптомы")
        bot.register_next_step_handler(message, handle_symptoms)

def get_gender(message):
    gender = GENDER[message.text]
    _, _, adult, _, _ = get_user(message.from_user.id)
    update_user(message.from_user.id,adult,gender)
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.from_user.id, "Опишите Ваши симптомы", reply_markup=markup)
    bot.register_next_step_handler(message, handle_symptoms)

def get_adult(message):
    adult = ADULT[message.text]
    update_user(message.from_user.id,adult,0)
    keyboard = types.ReplyKeyboardMarkup()
    key_female = types.KeyboardButton(text='Женский')
    keyboard.add(key_female)
    key_male = types.KeyboardButton(text='Мужской')
    keyboard.add(key_male)
    key_deny = types.KeyboardButton(text='Не указывать')
    keyboard.add(key_deny)
    question = 'Укажите Ваш пол'
    gender = bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
    bot.register_next_step_handler(message, get_gender)

def handle_symptoms(message):
    _, _, adult, gender, _ = get_user(message.from_user.id)
    answer = get_answer(message.text, adult, gender)
    bot.send_message(message.from_user.id, answer, parse_mode='Markdown')
    if answer == "Не достаточно симптомов":
        bot.register_next_step_handler(message, handle_symptoms)

if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)