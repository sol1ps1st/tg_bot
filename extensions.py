from datetime import (
    datetime,
    timedelta,
)

import requests
import json

from config import api_token


class CurrencyConverter:
    def __init__(self, refresh_delta=timedelta(hours=1)):
        self.refresh_delta = refresh_delta
        # Курсы валют, словарик вида
        # {'timestamp': 1632654543, 'rates': {'AED': 4.304841, 'AFN':...}}
        # Базовой валютой является EUR
        self.__latest = {"timestamp": None, "rates": {}}
        self.__base = "EUR"

    @property
    def latest(self):
        need_refresh_data = self.__latest["timestamp"] is None
        if not need_refresh_data:
            delta = timedelta(
                seconds=datetime.now().timestamp() - self.__latest["timestamp"]
            )
            need_refresh_data = delta > self.refresh_delta
        if need_refresh_data:
            r = requests.get(f"http://api.exchangeratesapi.io/v1/latest?access_key={api_token}")
            r.raise_for_status()
            r = json.loads(r.content)
            self.__latest["timestamp"] = datetime.now().timestamp()
            self.__latest["rates"] = r["rates"]
        return self.__latest

    def available_currencies(self):
        return self.latest["rates"].keys()

    def get_price(self, base, quote, amount):
        try:
            amount = float(amount)
        except ValueError:
            raise APIException("Неверная сумма.")
        all_cur = self.available_currencies()
        for c in (base, quote):
            if c not in all_cur:
                raise APIException(f"Валюта {c} недоступна.")

        if base == self.__base:
            res = self.latest["rates"][quote] * amount
        else:
            res = self.latest["rates"][quote] / self.latest["rates"][base] * amount
        return round(res, 2)


class APIException(Exception):
    pass
