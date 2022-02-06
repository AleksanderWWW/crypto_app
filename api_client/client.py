"""Polygon.io API client"""

import configparser
import datetime

import requests


class Client:
    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.access_config = self.config["access"]
        self.route_config = self.config["routes"]

        self.headers = {"Authorization": f"Bearer {self.access_config['API_KEY']}"}

    def get_daily_open_close(self, ticker: str, date: datetime.date, adjusted: bool = True) -> dict:
        if adjusted:
            adjusted = "true"
        else:
            adjusted = "false"

        date = date.strftime("%Y-%m-%d")

        url = self.route_config["BASE_URL"] + \
            self.route_config["DAILY"].format(
            stocksTicker=ticker,
            date=date,
            adjusted=adjusted
        )
        r = requests.get(url, headers=self.headers)

        return r.json()

