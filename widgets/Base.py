# -*- coding: utf-8 -*- 
"""
...@version: python 3.7
...@author: Karbob
...@fileName: Base.py
...@description: 
...@date: 2022-06-08
"""
import pymssql
from pymssql import Connection, Cursor, Error
from typing import Any
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QGraphicsDropShadowEffect,
    QLineEdit,
    QRadioButton,
    QTableWidget,
)


class Button(QPushButton):

    def __init__(self, *args, **kwargs) -> None:
        super(Button, self).__init__(*args, **kwargs)
        self.setContentsMargins(0, 0, 0, 0)
        self.setCursor(Qt.PointingHandCursor)


class RadioButton(QRadioButton):

    def __init__(self, *args, **kwargs) -> None:
        super(RadioButton, self).__init__(*args, **kwargs)
        self.setContentsMargins(0, 0, 0, 0)
        self.setCursor(Qt.PointingHandCursor)


class HLayout(QHBoxLayout):

    def __init__(self, *args, **kwargs) -> None:
        super(HLayout, self).__init__(*args, **kwargs)
        self.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)


class VLayout(QVBoxLayout):

    def __init__(self, *args, **kwargs) -> None:
        super(VLayout, self).__init__(*args, **kwargs)
        self.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)


class Shadow(QGraphicsDropShadowEffect):

    def __init__(self, x_offset: int, y_offset: int, blur: int, color=QColor(0, 0, 0, 50)) -> None:
        super(Shadow, self).__init__()
        self.setOffset(x_offset, y_offset)
        self.setBlurRadius(blur)
        self.setColor(color)


class Input(QLineEdit):

    def __init__(self, *args, **kwargs) -> None:
        super(Input, self).__init__(*args, **kwargs)
        self.setContentsMargins(0, 0, 0, 0)


class Table(QTableWidget):

    def __init__(self, *args, **kwargs) -> None:
        super(Table, self).__init__(*args, **kwargs)
        self.horizontalHeader().setStyleSheet("""
        QHeaderView::section {
            font-weight: bold;
        }
        """)


class Sidebar(QWidget):

    background: QLabel
    layout: VLayout

    def __init__(self, width: int, height: int, *args, **kwargs) -> None:
        super(Sidebar, self).__init__(*args, **kwargs)
        self.resize(width, height)
        # 背景
        background = QLabel(self)
        background.setFixedSize(width, height)
        background.setStyleSheet("""
        QWidget {
            background: rgba(255, 255, 255, 255);
            border-top-right-radius: 30px;
            border-bottom-right-radius: 30px;
        }
        """)
        # 垂直布局
        self.layout = VLayout()
        self.setLayout(self.layout)

    def add_widget(self, widget: QWidget) -> None:
        """
        添加控件到侧边栏
        """
        self.layout.addWidget(widget, 1, Qt.AlignCenter)


class MsConnectThread(QThread):

    connection_signal = pyqtSignal(Connection)

    def __init__(self, *args, **kwargs) -> None:
        super(MsConnectThread, self).__init__()
        self.args = args
        self.kwargs = kwargs

    def run(self) -> None:
        """
        连接数据库
        """
        try:
            connection = pymssql.connect(*self.args, **self.kwargs)
            self.connection_signal.emit(connection)
        except Error:
            self.connection_signal.emit(None)


class MsSQLThread(QThread):

    data_signal = pyqtSignal(object)

    def __init__(self, connection: Connection, sql: str) -> None:
        super(MsSQLThread, self).__init__()
        self.connection = connection
        self.sql = sql

    def run(self) -> None:
        """
        执行SQL语句
        """
        cursor: Cursor = self.connection.cursor()
        try:
            if "SELECT" == self.sql[:6].upper():
                data = cursor.execute(self.sql).fetchall()
                self.data_signal.emit(data)
            elif "INSERT" == self.sql[:6].upper():
                cursor.execute(self.sql)
                self.connection.commit()
                self.data_signal.emit(cursor.lastrowid)
            else:
                cursor.execute(self.sql)
                self.connection.commit()
                self.data_signal.emit(True)
        except Error:
            self.data_signal.emit(None)
        finally:
            cursor.close()