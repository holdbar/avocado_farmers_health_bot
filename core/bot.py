import os
import telebot


from logic import (
    get_answer
)
from database_functions import (
    get_user, 
    add_user,
    update_chat_status
)


TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(content_types=['text'])
def handle_messages(message):
    user = get_user(message.from_user.id)
    print(user)
    if not user:
        new_user = {'telegram_id': message.from_user.id, 'gender': None, 'adult': None}
        bot.register_next_step_handler(message,new_user,get_gender)
    elif message.text == "Привет":
        bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Напиши привет")
    else:
        answer = get_answer(message.text)
        bot.send_message(message.from_user.id, answer, parse_mode='Markdown')

def get_gender(message, user):
    keyboard = types.InlineKeyboardMarkup()
    key_female = types.InlineKeyboardButton(text='Женский', callback_data=2)
    keyboard.add(key_female)
    key_male = types.InlineKeyboardButton(text='Мужской', callback_data=1)
    keyboard.add(key_male)
    key_deny = types.InlineKeyboardButton(text='Не указывать', callback_data=0)
    keyboard.add(key_deny)
    question = 'Укажите Ваш пол'
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)