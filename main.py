"""
http://t.me/currency_converter_sf_5_6_bot
"""

import telebot

from config import bot_token
from extensions import (
    CurrencyConverter,
    APIException,
)
bot = telebot.TeleBot(bot_token)
cc = CurrencyConverter()


def exception_logger(f):
    def wrapper(message: telebot.types.Message):
        try:
            res = f(message)
        except APIException as e:
            bot.reply_to(message, f"Ошибка ввода.\n{e}")
        except Exception as e:
            bot.reply_to(message, f"Не удалось обработать команду.\n{e}")
        else:
            return res
    return wrapper


@bot.message_handler(commands=["start", "help"])
@exception_logger
def show_help(message: telebot.types.Message):
    help_text = (
        "Для конвертации отправьте сообщение в следующем формате:"
        "\n<валюта из которой переводим> <валюта в которую переводим> <сумма>"
        "\nПример: USD RUB 10.5"
        "\nСписок всех доступных валют можно узнать выполнив /values"
    )
    bot.send_message(
        message.chat.id,
        help_text
    )


@bot.message_handler(commands=["values"])
@exception_logger
def show_currencies(message: telebot.types.Message):
    text = "Все доступные валюты:\n"
    text += "\n".join(cc.available_currencies())
    bot.send_message(
        message.chat.id,
        text
    )


@bot.message_handler(content_types=["text"])
@exception_logger
def convert(message: telebot.types.Message):
    values = message.text.split()
    if len(values) != 3:
        raise APIException("Должно быть передано ровно 3 аргумента /help")
    base, quote, amount = values
    res = str(
        cc.get_price(base, quote, amount)
    )
    bot.reply_to(
        message,
        res
    )


bot.polling(none_stop=True)
