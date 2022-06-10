# -*- coding: utf-8 -*- 
"""
...@version: python 3.7
...@author: Karbob
...@fileName: main.py
...@description: 
...@date: 2022-06-08
"""
import sys
from PyQt5.QtWidgets import QApplication
from widgets.MainWindow import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
