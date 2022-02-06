import tkinter
import datetime

import tkcalendar

from api_client.client import Client


class StartScreen:

    def __init__(self, config) -> None:
        self.original_config = config
        self.config = config["gui"]
        self.root = tkinter.Tk(screenName="start_screen")
        self.root.title(self.config["TITLE"])
        self.root.geometry(self.config["GEOM"])
        self._build_window()

    def _build_window(self):
        welcome_label = tkinter.Label(text="Welcome to Crypto App!")
        welcome_label.pack()
        button_text = "Start"
        start_button = tkinter.Button(self.root, text=button_text,
                                      name="start_button",
                                      command=self._transition,
                                      width=50)
        start_button.pack(side="bottom")

    def _transition(self):
        self.root.destroy()
        new_screen = Gui(self.original_config)
        new_screen.run()

    def run(self):
        self.root.mainloop()


class Gui:

    def __init__(self, config) -> None:
        self.api_client = Client(config)  # will be used to execute user's queries
        self.config = config["gui"]

        self.ticker_list = [info["ticker"] for info in self.api_client.tickers]
        self.asset_names = [info["base_currency_name"] for info in self.api_client.tickers]

        self.root = tkinter.Tk(screenName="main")
        self.root.title(self.config["TITLE"])
        self.root.geometry(self.config["GEOM"])
        self.ticker_var = tkinter.StringVar(self.root)
        self.ticker_var.set(self.ticker_list[0])  # default option

        self._build_window()

    def _build_window(self):
        ticker_choice = tkinter.ttk.Combobox(self.root, textvariable=self.ticker_var
                                             ,
                                             values=self.ticker_list)
        ticker_choice.pack()

        date_entry = tkcalendar.DateEntry(self.root,
                                          width=30,
                                          bg="darkblue",
                                          fg="white",
                                          year=datetime.date.today().year)
        date_entry.pack()

        button = tkinter.Button(self.root, text="Search",
                                command=lambda: self.get_daily_open_close())
        button.pack()

        result_label = tkinter.Label(self.root, name="close_price")
        result_label.pack()

    def get_daily_open_close(self,  adjusted: bool = True):
        date = datetime.datetime.strptime(self.root.children["!dateentry"].get(), "%m/%d/%y")
        ticker = self.ticker_var.get()
        asset = [data for data in self.api_client.tickers
                 if data["ticker"] == ticker][0]

        result = self.api_client.get_daily_open_close(ticker, date, adjusted)

        try:
            close = result["close"]
            text = f"Name: {asset['base_currency_name']}\n" \
                   f"In relation to: {asset['currency_name']}\n" \
                   f" Closing price: {close} {asset['currency_symbol']}"
        except KeyError:
            if result["status"] == "ERROR":
                text = result['error']
            else:
                text = result["message"]

        self.root.children["close_price"].config(text=text)

    def run(self):
        self.root.mainloop()
