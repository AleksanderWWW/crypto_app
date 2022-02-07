import tkinter
import datetime
import abc
import threading

import tkcalendar
import tkinter.font
import pandas_datareader._utils
import requests.exceptions
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
        self.root.iconbitmap(r"static\window_icon.ico")

    @abc.abstractmethod
    def _build_window(self):
        """Screen layout goes here"""
        ...

    def _transition(self, new_screen):
        """Switch to a given screen. Results in destruction of the current screen"""
        self.root.destroy()
        new_screen_obj = new_screen(self.original_config)
        new_screen_obj.run()

    def _add_footer_buttons(self, parent, **kwargs):
        back_button = tkinter.Button(parent, text="Back",
                                     command=lambda: self._transition(StartScreen),
                                     font=("MS Serif", 15, "bold"), bg='#d4af37')
        back_button.grid(row=kwargs["row"], column=0, padx=kwargs["padx"], pady=20)

        refresh_button = tkinter.Button(parent, text="Refresh",
                                        command=lambda: self._transition(self.__class__),
                                        font=("MS Serif", 15, "bold"), bg='#d4af37')
        refresh_button.grid(row=kwargs["row"], column=2, padx=kwargs["padx"], pady=20)

    def run(self):
        self._build_window()
        self.root.mainloop()


class StartScreen(Screen):

    def __init__(self, config) -> None:
        super().__init__(config, screen_name="start_screen")

    def _build_window(self):
        frame = tkinter.Frame(self.root, pady=20, bg="black")
        frame.pack(fill="both", expand=True)
        welcome_label = tkinter.Label(frame, text="Welcome to Crypto App!",
                                      font=("MS Serif", 20, "bold"))
        welcome_label.grid(row=0, column=0, columnspan=3)

        im_frame = tkinter.Frame(frame, padx=5, pady=10, bg="black")
        im_frame.grid(row=1, column=0, sticky="", columnspan=3)

        im = Image.open(r"static\title_page.jpg")

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
                              bg='#d4af37',
                              command=lambda: self._transition(HistoricalQuotes))
        btn1.grid(row=2, column=1)
        btn2.grid(row=2, column=2)


class Gui(Screen):

    def __init__(self, config, screen_name="main") -> None:
        self.api_client = Client(config)  # will be used to execute user's queries
        # TODO: ticker list and/or asset names
        self.ticker_list = [utils.transform_ticker(tic["ticker"])
                            for tic in self.api_client.tickers]

        super().__init__(config, screen_name)
        self.ticker_var = tkinter.StringVar(self.root)
        self.adjusted_var = tkinter.StringVar(self.root)
        self.adjusted_var.set("adjusted")  # default option
        if self.ticker_list:
            self.ticker_var.set(self.ticker_list[0])  # default option
        else:
            self.ticker_var.set("Failed to load tickers")
            tkinter.Label(self.root, text="No internet connection!",
                          font=("MS Serif", 15, "bold")).pack()

        self.loading_lbl = None

    def _build_window(self):
        padx = 20
        frame = tkinter.Frame(self.root, padx=20, pady=20, bg="black")
        frame.pack(expand=True, fill="both")

        background_image = ImageTk.PhotoImage(Image.open(r"static\background.jpg"))
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
                                       font=("MS Serif", 15, "bold"), bg='#d4af37'
                                       )
        adjusted_choice.grid(row=0, column=2, padx=padx, pady=20, columnspan=2)

        search_button.grid(row=1, column=1, padx=padx, pady=60)


        self._add_footer_buttons(frame, padx=20, row=3)

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
        date = datetime.datetime.strptime(frame.children["!dateentry"].get(), "%m/%d/%y")
        ticker = self.ticker_var.get().lower()
        self.loading_lbl = utils.ImageLabel(frame)
        self.loading_lbl.grid(row=2, column=1, pady=60)
        self.loading_lbl.load(r'static\loading.gif')
        result_label = tkinter.Label(frame, name="close_price", font=("MS Serif", 15, "bold"),
                                     text="waiting for the query to complete...")
        result_label.grid(row=2, column=1, pady=60)
        self.root.update()

        thread = threading.Thread(target=self._get_quote, args=(ticker, date, result_label))
        thread.start()


class HistoricalQuotes(Gui):
    def __init__(self, config, screen_name="historical_quotes") -> None:
        super().__init__(config, screen_name)
        self.res_container = {"result": None}

    def _build_chart(self, frame, ticker, table=None):
        if table is None:
            error_label = tkinter.Label(frame, text=f"Could not load data for {ticker}",
                                        font=("MS Serif", 15, "bold"))
            error_label.grid(row=2, column=1)
            return

        figure = plt.Figure(figsize=(6, 6), dpi=100)
        table["Close"].plot(kind="line", title=f"Close for {ticker}", ax=figure.add_subplot(111))
        chart_type = FigureCanvasTkAgg(figure, frame)
        chart_type.draw()
        chart_type.get_tk_widget().grid(row=2, column=0, columnspan=4)

    def _get_table(self, ticker, start_date, end_date, frame):
        try:
            table = self.api_client.get_hist_data(ticker, start_date, end_date)
        except pandas_datareader._utils.RemoteDataError:
            table = None
        self.res_container["result"] = table

        self.loading_lbl.unload()
        self.loading_lbl.destroy()

        self._build_chart(frame, ticker, table)

    def run_process(self):
        frame = self.root.children["!frame"]

        start_date = datetime.datetime.strptime(frame.children["!dateentry"].get(), "%m/%d/%y")
        end_date = datetime.datetime.strptime(frame.children["!dateentry2"].get(), "%m/%d/%y")
        ticker = self.ticker_var.get().lower()
        self.loading_lbl = utils.ImageLabel(frame)
        self.loading_lbl.grid(row=2, column=1)
        self.loading_lbl.load(r'static\loading.gif')
        self.root.update()

        thread = threading.Thread(target=self._get_table, args=(ticker, start_date, end_date, frame))
        thread.start()

    def _build_window(self):
        padx = 10

        # ===========================================================================
        # Background image
        # ===========================================================================
        frame = tkinter.Frame(self.root, padx=20, pady=20, bg="black")
        frame.pack(expand=True, fill="both")

        background_image = ImageTk.PhotoImage(Image.open(r"static\background.jpg"))
        background_label = tkinter.Label(frame, image=background_image)
        background_label.image = background_image
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # ===========================================================================
        # Input controls
        # ===========================================================================
        ticker_choice = tkinter.ttk.Combobox(frame, textvariable=self.ticker_var,
                                             values=self.ticker_list, font=("MS Serif", 15, "bold"))
        ticker_choice.grid(row=0, column=0, padx=padx, pady=20)

        start_date_entry = tkcalendar.DateEntry(frame,
                                                width=20,
                                                bg="darkblue",
                                                fg="white",
                                                year=datetime.date.today().year,
                                                font=("MS Serif", 15, "bold"))
        start_date_entry.grid(row=0, column=1, padx=padx, pady=20)

        end_date_entry = tkcalendar.DateEntry(frame,
                                              width=20,
                                              bg="darkblue",
                                              fg="white",
                                              year=datetime.date.today().year,
                                              font=("MS Serif", 15, "bold"))
        end_date_entry.grid(row=0, column=2, padx=padx, pady=20)

        run_button = tkinter.Button(frame, text="Get Data",
                                    command=lambda: self.run_process(),
                                    font=("MS Serif", 15, "bold"), bg='#d4af37')
        run_button.grid(row=0, column=4, padx=padx, pady=20)

        self._add_footer_buttons(frame, padx=20, row=3)
