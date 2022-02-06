import configparser

from gui.gui import Gui


def main():
    config = configparser.ConfigParser()
    config.read("config.ini")
    gui = Gui(config)
    gui.run()


if __name__ == '__main__':
    main()
