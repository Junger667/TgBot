import telebot
import requests
import json
import sqlite3
import logging




logging.basicConfig(
    filename='error.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


bot = telebot.TeleBot('7609487550:AAE937plObNvRUXLoMLlhoTRvbMrSiKcjVM')
API = '77d7a63614b441a59a076076ce459d38'


def init_db():
    try:
        conn = sqlite3.connect('weatherDB.db')
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS users ( id INTEGER PRIMARY KEY AUTOINCREMENT,telegram_id INTEGER,city TEXT)')
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f'[init_db] Ошибка: {e}')


init_db()


@bot.message_handler(commands=['start'])
def main(message):
    try:
        bot.send_message(message.chat.id, 'Привет, введи город для получения погоды:')
    except Exception as e:
        logging.error(f'[start] Ошибка: {e}')


@bot.message_handler(content_types=['text'])
def get_weather(message):
    try:
        city = message.text.strip().lower()
        res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')

        if res.status_code == 200:
            data = json.loads(res.text)
            temp = data["main"]["temp"]
            bot.reply_to(message, f'Сейчас погода в городе {city.title()}: {temp}°C')

            conn = sqlite3.connect('weatherDB.db')
            cur = conn.cursor()
            cur.execute('INSERT INTO users (telegram_id, city) VALUES (?, ?)', (message.from_user.id, city))
            conn.commit()
            conn.close()

            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton('Список пользователей', callback_data='users'))
            bot.send_message(message.chat.id, 'Город сохранён.', reply_markup=markup)
        else:
            bot.reply_to(message, 'Город не найден. Попробуй снова.')
    except Exception as e:
        logging.error(f'[get_weather] Ошибак:{e}')


@bot.callback_query_handler(func=lambda call: call.data == 'users')
def show_users(call):
    try:
        conn = sqlite3.connect('weatherDB.db')
        cur = conn.cursor()
        cur.execute('SELECT telegram_id, city FROM users')
        rows = cur.fetchall()
        conn.close()

        if rows:
            text = 'Список пользователей и их городов:\n\n'
            for row in rows:
                text += f'ID: {row[0]}, Город: {row[1].title()}\n'
        else:
            text = 'Нет данных о пользователях.'

        bot.send_message(call.message.chat.id, text)
    except Exception as e:
        logging.error(f'[show_users] Ошибка:{e}')


if __name__ == "__main__":
    bot.polling(none_stop=True)

