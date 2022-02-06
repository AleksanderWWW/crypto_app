import tkinter
import datetime
import abc

import tkcalendar
import tkinter.font

from PIL import ImageTk, Image
from api_client.client import Client


class Screen:
    def __init__(self, config, screen_name):

        self.original_config = config
        self.config = config["gui"]
        self.root = tkinter.Tk(screenName=screen_name)
        self.root.title(self.config["TITLE"])
        self.root.resizable(False, False)
        self.root.geometry(self.config["GEOM"])

    @abc.abstractmethod
    def _build_window(self):
        ...

    def _transition(self, new_screen):
        self.root.destroy()
        new_screen_obj = new_screen(self.original_config)
        new_screen_obj.run()

    def run(self):
        self.root.mainloop()


class StartScreen(Screen):

    def __init__(self, config) -> None:
        super().__init__(config, screen_name="start_screen")
        self._build_window()

    def _build_window(self):
        frame = tkinter.Frame(self.root, padx=20, pady=20)
        frame.pack(fill="both", expand=True)
        welcome_label = tkinter.Label(frame, text="Welcome to Crypto App!",
                                      font=("MS Serif", 20, "bold"))
        welcome_label.pack()

        im = Image.open("title_page.jpg")

        im = im.resize((1000, 600))
        image = ImageTk.PhotoImage(im)
        img_label = tkinter.Label(frame, image=image)
        img_label.image = image
        img_label.pack()

        button_text = "Start"
        start_button = tkinter.Button(frame, text=button_text,
                                      name="start_button",
                                      command=lambda: self._transition(Gui),
                                      width=50,
                                      pady=20,
                                      font=("MS Serif", 15, "bold"))
        start_button.pack(side='bottom')


class Gui(Screen):

    def __init__(self, config) -> None:
        self.api_client = Client(config)  # will be used to execute user's queries

        self.ticker_list = [info["ticker"] for info in self.api_client.tickers]
        self.asset_names = [info["base_currency_name"] for info in self.api_client.tickers]

        super().__init__(config, screen_name="main")
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

        back_button = tkinter.Button(self.root, text="Back",
                                     command=lambda: self._transition(StartScreen))
        back_button.pack()

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
