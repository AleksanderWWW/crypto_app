import tkinter
import datetime
import abc
import threading

import tkcalendar
import tkinter.font
import pandas_datareader._utils
import requests.exceptions

from PIL import ImageTk, Image
from api_client.client import Client
import gui.utils as utils


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
        """Screen layout goes here"""
        ...

    def _transition(self, new_screen):
        """Switch to a given screen. Results in destruction of the current screen"""
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
        # TODO: ticker list and/or asset names
        self.ticker_list = [utils.transform_ticker(tic["ticker"])
                            for tic in self.api_client.tickers]

        super().__init__(config, screen_name="main")
        self.ticker_var = tkinter.StringVar(self.root)
        if self.ticker_list:
            self.ticker_var.set(self.ticker_list[0])  # default option
        else:
            self.ticker_var.set("Failed to load tickers")
            tkinter.Label(self.root, text="No internet connection!",
                          font=("MS Serif", 15, "bold")).pack()

        self._build_window()

        self.daily_res = {"result": None}
        self.loading_lbl = None

    def _build_window(self):
        # background_image = ImageTk.PhotoImage(Image.open("background.png"))
        # background_label = tkinter.Label(self.root, image=background_image)
        # background_label.image = background_image
        # background_label.place(x=0, y=0, relwidth=1, relheight=1)
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
                                command=lambda: self.get_daily_open_close(),
                                font=("MS Serif", 15, "bold"))
        button.pack()

        refresh_button = tkinter.Button(self.root, text="Refresh",
                                        command=lambda: self._transition(Gui),
                                        font=("MS Serif", 15, "bold"))
        refresh_button.pack()

        back_button = tkinter.Button(self.root, text="Back",
                                     command=lambda: self._transition(StartScreen),
                                     font=("MS Serif", 15, "bold"))
        back_button.pack(side="bottom")

    def _get_quote(self, ticker, date, adjusted=True):
        import time; time.sleep(10)
        try:
            close = self.api_client.get_daily_open_close(ticker, date, adjusted)
            text = f"Closing price for {ticker.upper()}: {close}"
        except KeyError:
            text = f"No data for {date.strftime('%Y-%m-%d')}"
        except pandas_datareader._utils.RemoteDataError as e:
            text = str(e)
        except requests.exceptions.ConnectionError:
            text = "Query failed. Please check your network connection and try again."
        self.loading_lbl.destroy()
        self.root.children["close_price"].config(text=text)

    def get_daily_open_close(self, adjusted: bool = True):
        date = datetime.datetime.strptime(self.root.children["!dateentry"].get(), "%m/%d/%y")
        ticker = self.ticker_var.get().lower()
        self.loading_lbl = utils.ImageLabel(self.root)
        self.loading_lbl.pack()
        self.loading_lbl.load('loading.gif')
        result_label = tkinter.Label(self.root, name="close_price", font=("MS Serif", 15, "bold"),
                                     text="waiting for the query to complete...")
        result_label.pack()
        self.root.update()

        thread = threading.Thread(target=self._get_quote, args=(ticker, date, adjusted))
        thread.start()

    def run(self):
        self.root.mainloop()
