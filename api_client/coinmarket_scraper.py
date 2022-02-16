"""Contains a Scraper objects that feed the list of crypto coins to the application"""
import configparser

import requests
from bs4 import BeautifulSoup


def extract_name(full_name: str, symbol: str) -> str:
    """Due to the fact that the web page provides names that are combined with symbol name
    (without space in between), this function helps to extract the actual name of the coin
    based on the symbol string"""
    return full_name[len(symbol):]


class Scraper:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.url = config["scraper"]["url"]

        self.soup = BeautifulSoup(self._get_html_text(), 'lxml')

    def _get_html_text(self):
        r = requests.get(self.url)

        return r.text

    def scrape_coin_names(self) -> list:
        result = []
        table = self.soup.find("tbody")
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            full_name = cells[1].text
            symbol_str = cells[2].text
            name = extract_name(full_name, symbol_str)
            result.append(name)

        return result




