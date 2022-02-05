import datetime

from gui.gui import Gui


def main():
    ticker = "AAPL"
    date = datetime.date.today() - datetime.timedelta(days=1)

    gui = Gui()
    #gui.get_daily_open_close(ticker, date)
    gui.run()


if __name__ == '__main__':
    main()
