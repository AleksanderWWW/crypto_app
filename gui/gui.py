import tkinter
import datetime

import tkcalendar

from api_client.client import Client


class Gui:

    def __init__(self) -> None:
        self.api_client = Client()  # will be used to execute user's queries

        self.root = tkinter.Tk(screenName="main")
        self.root.title("Stock Prices App")
        self.root.geometry("600x600")
        self._build_window()

    def _build_window(self):
        ticker_entry = tkinter.Entry(self.root, width=50)
        ticker_entry.pack()

        date_entry = tkcalendar.DateEntry(self.root,
                                          width=30,
                                          bg="darkblue",
                                          fg="white",
                                          year=datetime.date.today().year)
        date_entry.pack()

        button = tkinter.Button(self.root, text="Submit", command=lambda: self.get_daily_open_close())
        button.pack()

        result_label = tkinter.Label(self.root)
        result_label.pack()

    def get_daily_open_close(self,  adjusted: bool = True):
        ticker = self.root.children["!entry"].get()
        date = datetime.datetime.strptime(self.root.children["!dateentry"].get(), "%m/%d/%y")

        result = self.api_client.get_daily_open_close(ticker, date)

        try:
            close = result["close"]
            text = f"{ticker} closing price: {close}$"
        except KeyError:
            text = f"Data for {date.strftime('%d/%m/%Y')} unavailable"

        self.root.children["!label"].config(text=text)


    def run(self):
        self.root.mainloop()
