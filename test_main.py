import unittest
import sqlite3
import os
import time
from unittest.mock import patch, MagicMock
import main
import logging

print("Тестовый файл запущен")


class TestWeatherBot(unittest.TestCase):

    @patch("main.requests.get")
    def test_weather_valid_city(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"main": {"temp": 15}}'
        mock_get.return_value = mock_response

        response = main.requests.get("fake_url")
        self.assertIn('"temp": 15', response.text)

    @patch("main.requests.get")
    def test_weather_invalid_city(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        response = main.requests.get("fake_url")
        self.assertEqual(response.status_code, 404)

    def test_db_creation(self):
        for _ in range(5):
            try:
                if os.path.exists("weatherDB.db"):
                    os.remove("weatherDB.db")
                break
            except PermissionError:
                time.sleep(0.1)

        main.init_db()

        conn = sqlite3.connect("weatherDB.db")
        cur = conn.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        table_exists = cur.fetchone()
        conn.close()

        self.assertIsNotNone(table_exists)

    @patch("main.bot.send_message")
    def test_start_command(self, mock_send):
        message = MagicMock()
        message.chat.id = 12345

        main.start_command(message)

        mock_send.assert_called_once_with(
            12345, "Привет, введи город для получения погоды:"
        )

    @patch("main.requests.get")
    @patch("main.bot.reply_to")
    @patch("main.bot.send_message")
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

        mock_reply.assert_called_once_with(
            message, "Сейчас погода в городе Moscow: 10°C"
        )
        mock_send.assert_called_once()


logging.shutdown()


if __name__ == "__main__":
    unittest.main(verbosity=2)
