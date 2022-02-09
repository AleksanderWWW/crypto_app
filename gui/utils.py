"""Utility functions for the application GUI"""

import tkinter as tk
from PIL import Image, ImageTk
from itertools import count, cycle

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ImageLabel(tk.Label):
    """
    A Label that displays images, and plays them if they are gifs
    :im: A PIL Image instance or a string filename
    Source: https://pythonprogramming.altervista.org/animate-gif-in-tkinter/
    """

    def load(self, im):
        if isinstance(im, str):
            im = Image.open(im)
        frames = []

        try:
            for i in count(1):
                frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(i)
        except EOFError:
            pass
        self.frames = cycle(frames)

        try:
            self.delay = im.info['duration']
        except:
            self.delay = 100

        if len(frames) == 1:
            self.config(image=next(self.frames))
        else:
            self.next_frame()

    def unload(self):
        self.config(image=None)
        self.frames = None

    def next_frame(self):
        if self.frames:
            self.config(image=next(self.frames))
            self.after(self.delay, self.next_frame)


def transform_ticker(ticker: str) -> str:
    ticker_no_x = ticker.split(":")[1]
    curr = ticker_no_x[-3:]
    base = ticker_no_x[:-3]
    return base + "-" + curr


def build_chart(frame, ticker, table=None, legend=None):
    if table.empty:
        error_label = tk.Label(frame, text=f"Could not load data for {ticker}",
                                    font=("MS Serif", 15, "bold"))
        error_label.grid(row=2, column=1)
        return
    figure = plt.Figure(figsize=(7, 5.5), dpi=100)
    table["Close"].plot(kind="line", title=f"Close for {ticker}", ax=figure.add_subplot(111), legend=legend)
    chart_type = FigureCanvasTkAgg(figure, frame)
    chart_type.draw()
    chart_type.get_tk_widget().grid(row=2, column=0, columnspan=3)
