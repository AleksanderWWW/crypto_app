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
        self.root.iconbitmap("window_icon.ico")

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
        frame = tkinter.Frame(self.root, pady=20, bg="black")
        frame.pack(fill="both", expand=True)
        welcome_label = tkinter.Label(frame, text="Welcome to Crypto App!",
                                      font=("MS Serif", 20, "bold"))
        welcome_label.grid(row=0, column=0, columnspan=3)

        im_frame = tkinter.Frame(frame, padx=5, pady=10, bg="black")
        im_frame.grid(row=1, column=0, sticky="", columnspan=3)

        im = Image.open("title_page.jpg")

        im = im.resize((1000, 600))
        image = ImageTk.PhotoImage(im)
        img_label = tkinter.Label(im_frame, image=image)
        img_label.image = image
        img_label.pack()

        start_button = tkinter.Button(frame, text="Daily quotes",
                                      name="daily_close",
                                      command=lambda: self._transition(Gui),
                                      width=20,
                                      pady=20,
                                      font=("MS Serif", 15, "bold"),
                                      bg='#d4af37')
        start_button.grid(row=2, column=0)
        btn1 = tkinter.Button(frame, text="About", width=20,
                                      pady=20,
                                      font=("MS Serif", 15, "bold"),
                                      bg='#d4af37')
        btn2 = tkinter.Button(frame, text="Historical data", width=20,
                                      pady=20,
                                      font=("MS Serif", 15, "bold"),
                                      bg='#d4af37')
        btn1.grid(row=2, column=1)
        btn2.grid(row=2, column=2)


class Gui(Screen):

    def __init__(self, config) -> None:
        self.api_client = Client(config)  # will be used to execute user's queries
        # TODO: ticker list and/or asset names
        self.ticker_list = [utils.transform_ticker(tic["ticker"])
                            for tic in self.api_client.tickers]

        super().__init__(config, screen_name="main")
        self.ticker_var = tkinter.StringVar(self.root)
        self.adjusted_var = tkinter.StringVar(self.root)
        self.adjusted_var.set("adjusted")  # default option
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
        padx = 20
        frame = tkinter.Frame(self.root, padx=20, pady=20, bg="black")
        frame.pack(expand=True, fill="both")

        background_image = ImageTk.PhotoImage(Image.open("background.jpg"))
        background_label = tkinter.Label(frame, image=background_image)
        background_label.image = background_image
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        ticker_choice = tkinter.ttk.Combobox(frame, textvariable=self.ticker_var,
                                             values=self.ticker_list, font=("MS Serif", 15, "bold"))
        ticker_choice.grid(row=0, column=0, padx=padx, pady=20)

        date_entry = tkcalendar.DateEntry(frame,
                                          width=30,
                                          bg="darkblue",
                                          fg="white",
                                          year=datetime.date.today().year,
                                          font=("MS Serif", 15, "bold"))
        date_entry.grid(row=0, column=1, padx=padx, pady=20)

        adjusted_choice = tkinter.ttk.Combobox(frame, textvariable=self.adjusted_var,
                                               values=["adjusted", "not adjusted"],
                                               font=("MS Serif", 15, "bold"))

        search_button = tkinter.Button(frame, text="Search",
                                       command=lambda: self.get_daily_open_close(),
                                       font=("MS Serif", 15, "bold"),
                                       )
        adjusted_choice.grid(row=0, column=2, padx=padx, pady=20, columnspan=2)

        search_button.grid(row=1, column=1, padx=padx, pady=60)

        refresh_button = tkinter.Button(frame, text="Refresh",
                                        command=lambda: self._transition(Gui),
                                        font=("MS Serif", 15, "bold"))
        refresh_button.grid(row=3, column=2, padx=padx, pady=20)

        back_button = tkinter.Button(frame, text="Back",
                                     command=lambda: self._transition(StartScreen),
                                     font=("MS Serif", 15, "bold"))
        back_button.grid(row=3, column=0, padx=padx, pady=20)

    def _get_quote(self, ticker, date, out_label):
        try:
            close = self.api_client.get_daily_open_close(ticker, date, str(self.adjusted_var))
            text = f"Closing price for {ticker.upper()}:\n {close}"
        except KeyError:
            text = f"No data for {date.strftime('%Y-%m-%d')}"
        except pandas_datareader._utils.RemoteDataError:
            text = f"No data fetched for symbol {ticker}\n using YahooDailyReader"
        except requests.exceptions.ConnectionError:
            text = "Query failed. \nPlease check your network connection and try again."

        self.loading_lbl.unload()
        self.loading_lbl.destroy()
        out_label.config(text=text)

    def get_daily_open_close(self):
        frame = self.root.children["!frame"]
        #frame = self.root
        date = datetime.datetime.strptime(frame.children["!dateentry"].get(), "%m/%d/%y")
        ticker = self.ticker_var.get().lower()
        self.loading_lbl = utils.ImageLabel(frame)
        self.loading_lbl.grid(row=2, column=1, pady=60)
        self.loading_lbl.load('loading.gif')
        result_label = tkinter.Label(frame, name="close_price", font=("MS Serif", 15, "bold"),
                                     text="waiting for the query to complete...")
        result_label.grid(row=2, column=1, pady=60)
        self.root.update()

        thread = threading.Thread(target=self._get_quote, args=(ticker, date, result_label))
        thread.start()

    def run(self):
        self.root.mainloop()
