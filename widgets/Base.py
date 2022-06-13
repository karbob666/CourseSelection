# -*- coding: utf-8 -*- 
"""
...@version: python 3.7
...@author: Karbob
...@fileName: Base.py
...@description: 
...@date: 2022-06-08
"""
import pymssql
import multiprocessing
from typing import List
from pymssql import Connection, Cursor, Error
from PyQt5.QtGui import QColor, QPainter, QPaintEvent, QFontMetrics, QCursor, QResizeEvent
from PyQt5.QtCore import Qt, pyqtSignal, QThreadPool, QRunnable, QObject, QModelIndex, QSize
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QToolTip,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QGraphicsDropShadowEffect,
    QLineEdit,
    QRadioButton,
    QTableWidget,
    QHeaderView,
    QAbstractItemView,
    QTableWidgetItem,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
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

    class Delegate(QStyledItemDelegate):

        def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
            # 去除虚线框
            if option.state & QStyle.State_HasFocus:
                option.state = option.state ^ QStyle.State_HasFocus
            # 交错颜色
            painter.fillRect(option.rect, QColor("#FFF") if index.row() & 1 else QColor("#EFEFEF"))
            return super().paint(painter, option, index)

    def __init__(self, *args, **kwargs) -> None:
        super(Table, self).__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.row = -1
        # 不显示垂直的表头
        self.verticalHeader().setVisible(False)
        # 自动调整列宽
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 表格不能选中
        self.setSelectionMode(QAbstractItemView.NoSelection)
        # 表格不可编辑
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 表格样式
        self.setItemDelegate(self.Delegate())
        self.setStyleSheet("""
        QTableWidget {
            border: 0;
            outline: none;
            font-size: 18px;
            color: #2E2E2E;
        }
        QTableWidget::item::hover {}
        QTableWidget::item:selected {
            color: #2E2E2E;
            background: #D9EBF9;
        }
        """)
        self.horizontalHeader().setStyleSheet("""
        QHeaderView::section {
            font-size: 20px;
            font-weight: bold;
        }
        """)
        # 绑定信号槽
        self.itemEntered.connect(self.slot_item_entered)

    def slot_item_entered(self, item: QTableWidgetItem) -> None:
        """
        进入单元格事件的信号槽
        """
        metrics = QFontMetrics(self.font())
        font_width = metrics.width(item.text())
        index = self.indexFromItem(item)
        column_width = self.columnWidth(index.column())
        if font_width > column_width:
            QToolTip.showText(QCursor.pos(), item.text())


class Modal(QWidget):

    main_widget: QWidget
    title: QLabel
    widget: QWidget
    title_block_size: QSize
    button_block_size: QSize
    button_list: List[Button]

    def __init__(self, width: int, height: int, *args, **kwargs) -> None:
        super(Modal, self).__init__(*args, **kwargs)
        self.resize(width, height)
        self.init_widgets()
        self.resize_widgets()
        button = Button()
        button.setText("取消")
        button.clicked.connect(self.close)
        button.setStyleSheet("""
        QWidget {
            font-size: 18px;
            border: 1px solid #D9D9D9;
            outline: none;
            border-radius: 3px;
        }
        QWidget:hover {
            color: rgba(64, 169, 255, 255);
            border: 1px solid rgba(64, 169, 255, 255);
        }
        """)
        self.add_button(button)

    def init_widgets(self) -> None:
        """
        初始化控件
        """
        # 显示内容区域
        self.main_widget = QWidget(parent=self)
        # 标题
        self.title = QLabel(parent=self)
        self.title.setStyleSheet("""
        QWidget {
            font-size: 24px;
        }
        """)
        # 内容区域
        self.widget = QWidget(parent=self)
        self.widget.setGraphicsEffect(Shadow(0, 0, 20))
        # 按钮列表
        self.button_list = list()

    def resize_widgets(self) -> None:
        """
        重新设置控件大小
        """
        # 修改显示内容的控件的位置和大小
        self.main_widget.resize(self.width()*3 // 5, self.height()*4 // 5)
        self.main_widget.move(
            self.width()//2 - self.main_widget.width()//2,
            self.height()//2 - self.main_widget.height()//2
        )
        # 标题区域的大小
        self.title_block_size = QSize(self.main_widget.width(), self.main_widget.height() // 10)
        # 按钮区域的大小
        self.button_block_size = QSize(self.main_widget.width(), self.main_widget.height() // 10)
        # 修改标题的位置和大小
        metrics = QFontMetrics(self.title.font())
        font_height = metrics.height()
        self.title.move(
            self.width()//2 - self.main_widget.width()//2 + self.main_widget.width()//50,
            self.height()//2 - self.main_widget.height()//2 + self.title_block_size.height()//2 - font_height//2
        )
        # 修改内容区域的位置和大小
        self.widget.resize(self.main_widget.width()*9 // 10, self.main_widget.height()*7 // 10)
        self.widget.move(
            self.width()//2 - self.widget.width()//2,
            self.height()//2 - self.widget.height()//2
        )
        # 修改按钮的位置和大小
        for index, button in enumerate(self.button_list):
            margin = self.button_block_size.height() // 6
            button_size = QSize(
                self.main_widget.width() // 8,
                self.button_block_size.height() - 2*margin
            )
            if button_size.height() >= 40:
                button_size = QSize(button_size.width(), 40)
            button.resize(button_size)
            button.move(
                self.width()//2 + self.main_widget.width()//2 - (index+1)*margin - button_size.width(),
                self.height()//2 + self.main_widget.height()//2 -\
                self.button_block_size.height()//2 - button_size.height()//2
            )

    def add_button(self, button: Button) -> None:
        """
        添加按钮
        """
        self.button_list.append(button)
        button.setParent(self)
        self.resize_widgets()

    def set_title(self, title: str) -> None:
        """
        设置标题
        """
        self.title.setText(title)

    def set_widget(self, widget: QWidget) -> None:
        """
        设置内容区域的控件
        """
        layout = VLayout()
        layout.addWidget(widget)
        self.widget.setLayout(layout)

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        绘制背景蒙版和显示内容区域的背景
        """
        painter = QPainter()
        painter.begin(self)
        # 抗锯齿
        painter.setRenderHint(QPainter.Antialiasing)
        # 绘制蒙版
        mask = QColor(0, 0, 0, 50)
        painter.fillRect(0, 0, self.width(), self.height(), mask)
        # 绘制内容区域
        background = QColor("#FFF")
        painter.setBrush(background)
        painter.setPen(Qt.transparent)
        painter.drawRoundedRect(
            self.width()//2 - self.main_widget.width()//2, self.height()//2 - self.main_widget.height()//2,
            self.main_widget.width(), self.main_widget.height(),
            10, 10
        )
        # 绘制两条分割线
        divider = QColor("#EFEFEF")
        painter.setPen(divider)
        painter.setBrush(Qt.transparent)
        painter.drawLine(
            self.width()//2 - self.main_widget.width()//2,
            self.height()//2 - self.main_widget.height()//2 + self.title_block_size.height(),
            self.width()//2 + self.main_widget.width()//2,
            self.height()//2 - self.main_widget.height()//2 + self.title_block_size.height(),
        )
        painter.drawLine(
            self.width()//2 - self.main_widget.width()//2,
            self.height()//2 - self.main_widget.height()//2 + self.main_widget.height()-self.button_block_size.height(),
            self.width()//2 + self.main_widget.width()//2,
            self.height()//2 - self.main_widget.height()//2 + self.main_widget.height()-self.button_block_size.height(),
        )
        painter.end()

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        窗口大小变化事件
        """
        self.resize_widgets()


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


class MsConnectThread(QRunnable):

    class Signals(QObject):
        connection_signal = pyqtSignal(object)

    def __init__(self, signals=Signals(), *args, **kwargs) -> None:
        super(MsConnectThread, self).__init__()
        self.args = args
        self.kwargs = kwargs
        self.setAutoDelete(True)
        try:
            signals.connection_signal.disconnect()
        except Exception:
            pass
        self.connection_signal = signals.connection_signal

    def run(self) -> None:
        """
        连接数据库
        """
        try:
            connection = pymssql.connect(*self.args, **self.kwargs)
            self.connection_signal.emit(connection)
        except Error:
            self.connection_signal.emit(None)


class MsSQLThread(QRunnable):

    class Signals(QObject):
        data_signal = pyqtSignal(object)

    def __init__(self, connection: Connection, sql: str, signals=Signals()) -> None:
        super(MsSQLThread, self).__init__()
        self.connection = connection
        self.sql = sql
        self.setAutoDelete(True)
        try:
            signals.data_signal.disconnect()
        except Exception:
            pass
        self.data_signal = signals.data_signal

    def run(self) -> None:
        """
        执行SQL语句
        """
        cursor: Cursor = self.connection.cursor()
        try:
            if "SELECT" == self.sql[:6].upper():
                cursor.execute(self.sql)
                data = cursor.fetchall()
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


class ThreadPool(QThreadPool):

    def __init__(self, max_count=multiprocessing.cpu_count()) -> None:
        super(ThreadPool, self).__init__()
        self.setMaxThreadCount(max_count)

