"""Polygon.io API client"""

import datetime
import os

import requests
import requests.exceptions

import pandas_datareader.data as web


class Client:
    def __init__(self, config) -> None:
        self.config = config
        _api_key = os.environ["Polygon_API_Key"]
        self.route_config = self.config["routes"]

        self.headers = {"Authorization": f"Bearer {self.access_config['API_KEY']}"}

        self.tickers = self._load_tickers()

    def _load_tickers(self) -> list:
        url = self.route_config["BASE_URL"] + self.route_config["TICKERS"]
        try:
            r = requests.get(url, headers=self.headers)
            results = r.json()["results"]
        except requests.exceptions.ConnectionError:
            return []

        return results

    def get_daily_open_close(self, ticker: str, date: datetime.date, adjusted):
        result = web.DataReader(name=ticker, data_source='yahoo',
                                start=date,
                                end=date.strftime("%Y-%m-%d"))
        if adjusted == "adjusted":
            close = result.iloc[0, -1]
        else:
            close = result.iloc[0, -3]
        return close
