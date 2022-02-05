import tkinter
import threading
import datetime

from api_client.client import Client


class Gui:

    def __init__(self) -> None:
        self.api_client = Client()  # will be used to execute user's queries
        self.current_result = {}

    def get_daily_open_close(self, ticker: str, date: datetime.date, adjusted: bool = True):
        thread = threading.Thread(
            target=self.api_client.get_daily_open_close,
            args=(ticker, date, adjusted, self.current_result)
        )
        thread.start()
        print("Waiting for result...")
        thread.join()
