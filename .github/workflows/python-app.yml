import unittest
import sqlite3
import os
from unittest.mock import patch, MagicMock
import main
import logging

print("Тестовый файл запущен")


class TestWeatherBot(unittest.TestCase):

    @patch('main.requests.get')
    def test_weather_valid_city(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"main": {"temp": 15}}'
        mock_get.return_value = mock_response

        response = main.requests.get("fake_url")
        self.assertIn('"temp": 15', response.text)

    @patch('main.requests.get')
    def test_weather_invalid_city(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        response = main.requests.get("fake_url")
        self.assertEqual(response.status_code, 404)

   
    def test_db_creation(self):
        if os.path.exists("weatherDB.db"):
            os.remove("weatherDB.db")

        main.init_db()

        conn = sqlite3.connect("weatherDB.db")
        cur = conn.cursor()

        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        table_exists = cur.fetchone()
        conn.close()

        self.assertIsNotNone(table_exists)

    
    @patch('main.bot.send_message')
    def test_start_command(self, mock_send):
        message = MagicMock()
        message.chat.id = 12345

        main.main(message)

        mock_send.assert_called_once_with(12345, 'Привет, введи город для получения погоды:')

    
    @patch('main.requests.get')
    @patch('main.bot.reply_to')
    @patch('main.bot.send_message')
    def test_get_weather_integration(self, mock_send, mock_reply, mock_get):
        message = MagicMock()
        message.text = "moscow"
        message.chat.id = 12345
        message.from_user.id = 54321

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"main": {"temp": 10}}'
        mock_get.return_value = mock_response

        main.get_weather(message)

        mock_reply.assert_called_once()
        mock_send.assert_called_once()

    
    def test_logging_on_error(self):
        if os.path.exists("error.log"):
            with open("error.log", "w", encoding="utf-8") as f:
                f.truncate(0)

        message = MagicMock()
        message.text = None  
        message.chat.id = 123
        message.from_user.id = 321

        main.get_weather(message)

        self.assertTrue(os.path.exists("error.log"))

        with open("error.log", "r", encoding="cp1251") as f:
            log_contents = f.read()
            self.assertIn("get_weather", log_contents)

logging.shutdown()

if __name__ == '__main__':
    unittest.main(verbosity=2)
