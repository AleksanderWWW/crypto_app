import configparser

from gui.gui import StartScreen


def main():
    config = configparser.ConfigParser()
    config.read("config.ini")
    app = StartScreen(config)
    app.run()


if __name__ == '__main__':
    main()
