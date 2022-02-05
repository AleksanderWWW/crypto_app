import datetime

from gui.gui import Gui


def main():
    ticker = "AAPL"
    date = datetime.date.today() - datetime.timedelta(days=1)

    gui = Gui()
    gui.get_daily_open_close(ticker, date)
    print(gui.current_result)


if __name__ == '__main__':
    main()