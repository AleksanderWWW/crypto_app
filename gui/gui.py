"""Module providing screen objects for the application GUI.
Each screen object must inherit from the Screen class.
It needs to be supplied with config object and a screen name.
Static dependencies for the screens are stored in the './static' dir."""

import tkinter
import tkinter.font
from tkinter import messagebox

import datetime
import abc
import threading

import tkcalendar
import pandas_datareader._utils
import requests.exceptions
import pandas as pd

from PIL import ImageTk, Image
from GoogleNews import GoogleNews

from api_client.client import Client
from gui import utils

# ===============================================================
# SETUP

# setup API client
api_client = Client()  # will be used to execute user's queries

try:
    ticker_list = [utils.transform_ticker(tic["ticker"])
                   for tic in api_client.tickers]
except Exception as e:
    print(e)
    ticker_list = []

# setup Google News API client
google_news = GoogleNews(
    period="7d",
    lang="en",
    encode="utf-8"
)

# ===============================================================


class Screen:
    def __init__(self, config, screen_name: str):
        self.original_config = config
        self.config = config["gui"]
        self.root = tkinter.Tk(screenName=screen_name)
        self.root.title(self.config["TITLE"] + " - " + screen_name)
        self.root.resizable(False, False)
        self.root.geometry(self.config["GEOM"])
        self.root.iconbitmap(r"static\window_icon.ico")
        self.ticker_var = tkinter.StringVar(self.root)

    def get_original_config(self):
        return self.original_config

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
        back_button.grid(row=kwargs["row"], column=kwargs["col_back"], padx=kwargs["padx"], pady=20)

        refresh_button = tkinter.Button(parent, text="Refresh",
                                        command=lambda: self._transition(self.__class__),
                                        font=("MS Serif", 15, "bold"), bg='#d4af37')
        refresh_button.grid(row=kwargs["row"], column=kwargs["col_refresh"],
                            padx=kwargs["padx"], pady=20)

    def _add_frame_with_background(self, im_path):
        frame = tkinter.Frame(self.root, padx=20, pady=20, bg="black")
        frame.pack(expand=True, fill="both")

        background_image = ImageTk.PhotoImage(Image.open(im_path))
        background_label = tkinter.Label(frame, image=background_image)
        background_label.image = background_image
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        return frame

    def run(self):
        self._build_window()
        self.root.mainloop()


class ScreenWithTickers(Screen):
    def __init__(self, config, screen_name=""):
        super().__init__(config, screen_name)
        self.loading_lbl = None

    @abc.abstractmethod
    def _build_window(self):
        ...

    def _build_ticker_choice(self, parent, tickers=ticker_list, **kwargs):
        ticker_choice = tkinter.ttk.Combobox(parent, textvariable=self.ticker_var,
                                             values=tickers,
                                             font=("MS Serif", 15, "bold"))

        def check_input(event):
            value = event.widget.get()

            if value == '':
                ticker_choice['values'] = tickers
            else:
                data = []
                for item in tickers:
                    if value.lower() in item.lower():
                        data.append(item)

                ticker_choice['values'] = data

        ticker_choice.bind('<KeyRelease>', check_input)
        padx = kwargs.pop("padx", 20)
        pady = kwargs.pop("pady", 20)
        ticker_choice.grid(row=0, column=0, padx=padx, pady=pady)


class StartScreen(Screen):

    def __init__(self, config) -> None:
        super().__init__(config, screen_name="home")

    def _build_window(self):
        frame = tkinter.Frame(self.root, pady=20, bg="black")
        frame.pack(fill="both", expand=True)
        welcome_label = tkinter.Label(frame, text="Welcome to Crypto App!",
                                      font=("MS Serif", 20, "bold"))
        welcome_label.grid(row=0, column=0, columnspan=3)

        im_frame = tkinter.Frame(frame, padx=5, pady=10, bg="black")
        im_frame.grid(row=1, column=0, sticky="", columnspan=3)

        im_obj = Image.open(r"static\title_page.jpg")

        im_obj = im_obj.resize((1000, 600))
        image = ImageTk.PhotoImage(im_obj)
        img_label = tkinter.Label(im_frame, image=image)
        img_label.image = image
        img_label.pack()

        start_button = tkinter.Button(frame, text="Spot quotes",
                                      name="daily_close",
                                      command=lambda: self._transition(SpotQuotes),
                                      width=20,
                                      pady=20,
                                      font=("MS Serif", 15, "bold"),
                                      bg='#d4af37')
        start_button.grid(row=2, column=0)
        btn1 = tkinter.Button(frame, text="Crypto news", width=20,
                              pady=20,
                              font=("MS Serif", 15, "bold"),
                              bg='#d4af37',
                              command=lambda: self._transition(CryptoNews))
        btn2 = tkinter.Button(frame, text="Historical data", width=20,
                              pady=20,
                              font=("MS Serif", 15, "bold"),
                              bg='#d4af37',
                              command=lambda: self._transition(HistoricalQuotes))
        btn1.grid(row=2, column=1)
        btn2.grid(row=2, column=2)


class SpotQuotes(ScreenWithTickers):

    def __init__(self, config, screen_name="spot quotes") -> None:
        super().__init__(config, screen_name)
        self.adjusted_var = tkinter.StringVar(self.root)
        self.adjusted_var.set("adjusted")  # default option

        if not ticker_list:
            self.ticker_var.set("Failed to load tickers")
            tkinter.Label(self.root, text="No internet connection!",
                          font=("MS Serif", 15, "bold")).pack()

    def _build_window(self):
        padx = 20
        frame = self._add_frame_with_background(r"static\background.jpg")

        self._build_ticker_choice(frame, padx=20)

        date_entry = tkcalendar.DateEntry(frame,
                                          width=30,
                                          bg="darkblue",
                                          fg="white",
                                          year=datetime.date.today().year,
                                          font=("MS Serif", 15, "bold"))
        date_entry.grid(row=0, column=1, padx=padx, pady=20)

        adjusted_choice = tkinter.ttk.Combobox(frame, textvariable=self.adjusted_var,
                                               values=["adjusted", "not adjusted"],
                                               font=("MS Serif", 15, "bold"),
                                               state="readonly")

        search_button = tkinter.Button(frame, text="Search",
                                       command=lambda: self.get_daily_open_close(),
                                       font=("MS Serif", 15, "bold"), bg='#d4af37'
                                       )
        adjusted_choice.grid(row=0, column=2, padx=padx, pady=20, columnspan=2)

        search_button.grid(row=1, column=1, padx=padx, pady=60)

        self._add_footer_buttons(frame, padx=20, row=3, col_refresh=2, col_back=0)

    def _get_quote(self, ticker, date, out_label):
        try:
            close = api_client.get_daily_open_close(ticker, date, str(self.adjusted_var))
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


class HistoricalQuotes(ScreenWithTickers):
    def __init__(self, config, screen_name="historical quotes") -> None:
        super().__init__(config, screen_name)
        self.res_container = {"result": None}
        self.export_formats = ["csv", "xlsx", "json", "html"]
        self.export_format_var = tkinter.StringVar(self.root)
        self.export_format_var.set(self.export_formats[0])
        self.chosen_tickers = []
        self.table = pd.DataFrame()

    def _get_table(self, ticker, start_date, end_date, frame):
        graph = True
        if ticker in self.chosen_tickers:
            graph = False
        else:

            self.chosen_tickers.append(ticker)
            try:
                table = api_client.get_hist_data(ticker, start_date, end_date)
                if self.table.empty:
                    self.table = table
                else:
                    self.table = pd.concat([self.table, table], axis=1)

            except pandas_datareader._utils.RemoteDataError:
                pass

        self.loading_lbl.unload()
        self.loading_lbl.destroy()
        if graph:
            utils.build_chart(frame, ticker, self.table, legend=self.chosen_tickers)

    def run_process(self):
        frame = self.root.children["!frame"]

        start_date = datetime.datetime.strptime(frame.children["!dateentry"].get(), "%m/%d/%y")
        end_date = datetime.datetime.strptime(frame.children["!dateentry2"].get(), "%m/%d/%y")
        ticker = self.ticker_var.get().lower()
        self.loading_lbl = utils.ImageLabel(frame)
        self.loading_lbl.grid(row=2, column=1)
        self.loading_lbl.load(r'static\loading.gif')

        self.root.update()

        thread = threading.Thread(target=self._get_table,
                                  args=(ticker, start_date, end_date, frame))
        thread.start()

    def export_to_excel(self):
        exp_format = self.export_format_var.get()
        file_root = "&".join(self.chosen_tickers)
        file_name = f"{file_root}_historical_data" + "." + exp_format
        if self.table.empty:
            messagebox.showerror("Error", "No data to export")
            return

        if exp_format == "csv":
            self.table.to_csv(file_name)

        elif exp_format == "xlsx":
            self.table.to_excel(file_name)

        elif exp_format == "json":
            self.table.to_json(file_name)

        elif exp_format == "html":
            self.table.to_html(file_name)

        else:
            messagebox.showerror("Invalid export format", f"Export format '{exp_format}' "
                                                          f"not recoginzed.")
            return
        messagebox.showinfo("Export complete", "Data successfully exported")

    def _build_window(self):
        padx = 10

        frame = self._add_frame_with_background(r"static\background.jpg")

        # ===========================================================================
        # Input controls
        # ===========================================================================
        self._build_ticker_choice(frame, padx=padx)

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

        # ===========================================================================
        # Fetch data and draw graph
        # ===========================================================================

        run_button = tkinter.Button(frame, text="Graph",
                                    command=lambda: self.run_process() or start_date_entry.config(state="disabled")
                                    or end_date_entry.config(state="disabled"),
                                    font=("MS Serif", 15, "bold"), bg='#d4af37')
        run_button.grid(row=0, column=3, padx=padx, pady=20)

        # ===========================================================================
        # Export data to excel
        # ===========================================================================
        format_choice = tkinter.ttk.Combobox(frame, textvariable=self.export_format_var,
                                             values=self.export_formats,
                                             width=10,
                                             state="readonly",
                                             font=("MS Serif", 15, "bold"))
        format_choice.grid(row=3, column=1, padx=padx, pady=20)
        save_button = tkinter.Button(frame, text="Export",
                                     command=lambda: self.export_to_excel(),
                                     font=("MS Serif", 15, "bold"), bg='#d4af37')
        save_button.grid(row=3, column=2, padx=padx, pady=20)

        self._add_footer_buttons(frame, padx=20, row=3, col_back=0, col_refresh=3)


class CryptoNews(ScreenWithTickers):
    def __init__(self, config, screen_name="crypto_news") -> None:
        super().__init__(config, screen_name)
        self.tickers_news: list = ["Bitcoin", "Ethereum", "Tether", "BNB"]
        self.ticker_var.set(self.tickers_news[0])

    def search_news(self, frame):
        ticker = self.ticker_var.get()
        google_news.search(ticker)
        news = google_news.result()

        row = 1
        for news_piece in news[:5]:
            news_frame = tkinter.Frame(frame, borderwidth=2, padx=10)
            news_frame.grid(row=row, column=0)
            tkinter.Label(news_frame, text=news_piece["date"],
                          font=("Times New Roman", 12, "bold"),
                          padx=10, pady=10).grid(row=0, column=0, columnspan=1)
            tkinter.Label(news_frame, text=news_piece["title"],
                          font=("Times New Roman", 12, "bold"),
                          padx=10, pady=10).grid(row=0, column=1, columnspan=2)
            tkinter.Label(news_frame, text=news_piece["desc"],
                          padx=10, pady=10).grid(row=1, column=1, columnspan=2)
            tkinter.Label(news_frame, text=news_piece["link"],
                          padx=10, fg="blue").grid(row=2, column=0, columnspan=3)
            row += 1

    def _build_window(self):
        frame = self._add_frame_with_background(r"static\background2.jpg")
        self._build_ticker_choice(frame, self.tickers_news, padx=20)
        search_button = tkinter.Button(
            frame,
            text="Search News",
            command=lambda: self.search_news(frame),
            font=("MS Serif", 15, "bold"),
            bg='#d4af37'
        )
        search_button.grid(row=0, column=1)


