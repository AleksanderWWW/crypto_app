"""Polygon.io API client"""

import datetime
import os

import requests
import requests.exceptions

import pandas_datareader.data as web


class Client:
    BASE_URL = "https://api.polygon.io"
    TICKERS = "/v3/reference/tickers?market=crypto&active=true&sort=ticker&order=asc&limit=1000"

    def __init__(self) -> None:
        _api_key = os.environ["Polygon_API_Key"]
        self.headers = {"Authorization": f"Bearer {_api_key}"}

        self.tickers = self._load_tickers()

    def _load_tickers(self) -> list:
        url = self.BASE_URL + self.TICKERS
        try:
            r = requests.get(url, headers=self.headers)
            results = r.json()["results"]
        except (requests.exceptions.ConnectionError, KeyError):
            return []

        return results

    def get_daily_open_close(self, ticker: str, date: datetime.date, adjusted):
        result = self.get_hist_data(ticker, date, date.strftime("%Y-%m-%d"))

        if adjusted == "adjusted":
            close = result.iloc[0, -1]
        else:
            close = result.iloc[0, -3]
        return close

    def get_hist_data(self, ticker, start_date, end_date):
        return web.DataReader(name=ticker, data_source='yahoo',
                              start=start_date,
                              end=end_date)
