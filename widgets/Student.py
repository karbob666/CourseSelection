# -*- coding: utf-8 -*- 
"""
...@version: python 3.7
...@author: Karbob
...@fileName: Student.py
...@description: 
...@date: 2022-06-09
"""
from config import config
from PyQt5.QtWidgets import QWidget, QLabel, QFrame
from PyQt5.QtGui import QPaintEvent, QPainter, QPixmap, QColor
from PyQt5.QtCore import Qt, QSize, QRect
from widgets.Base import Button, Shadow, VLayout, HLayout, Table, Sidebar


class Student(QWidget):

    sidebar: Sidebar
    btn_course_info: Button
    btn_selected: Button
    btn_select: Button
    btn_cancel: Button
    btn_user_info: Button
    table: Table

    def __init__(self, *args, **kwargs) -> None:
        super(Student, self).__init__(*args, **kwargs)
        self.init_window()
        self.init_widgets()
        self.init_layout()

    def init_window(self) -> None:
        """
        初始化窗口
        """
        self.resize(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)

    def init_widgets(self) -> None:
        """
        初始化控件
        """
        # 侧边栏
        self.sidebar = Sidebar(self.width() // 5, self.height(), parent=self)
        self.sidebar.move(0, 0)
        self.sidebar.setGraphicsEffect(Shadow(4, 0, 20, QColor(0, 0, 0, 30)))

        btn_sidebar_size = QSize(150, 60)
        btn_sidebar_stylesheet = """
        QWidget {
            font-size: 24px;
            font-weight: bold;
            border: 0;
            outline: none;
            border-radius: 5px;
            color: rgb(255, 255, 255);
            background: rgba(128, 183, 249, 255);
        }
        QWidget:hover {
            color: rgba(255, 255, 255, 200);
            background: rgba(128, 183, 249, 200);
        }
        """

        # 课程信息按钮
        self.btn_course_info = Button()
        self.btn_course_info.setText("课程信息")
        self.btn_course_info.setFixedSize(btn_sidebar_size)
        self.btn_course_info.setStyleSheet(btn_sidebar_stylesheet)
        self.btn_course_info.setGraphicsEffect(Shadow(0, 0, 20))

        # 已选课程按钮
        self.btn_selected = Button()
        self.btn_selected.setText("已选课程")
        self.btn_selected.setFixedSize(btn_sidebar_size)
        self.btn_selected.setStyleSheet(btn_sidebar_stylesheet)
        self.btn_selected.setGraphicsEffect(Shadow(0, 0, 20))

        # 选课按钮
        self.btn_select = Button()
        self.btn_select.setText("选课")
        self.btn_select.setFixedSize(btn_sidebar_size)
        self.btn_select.setStyleSheet(btn_sidebar_stylesheet)
        self.btn_select.setGraphicsEffect(Shadow(0, 0, 20))

        # 退选按钮
        self.btn_cancel = Button()
        self.btn_cancel.setText("退选")
        self.btn_cancel.setFixedSize(btn_sidebar_size)
        self.btn_cancel.setStyleSheet(btn_sidebar_stylesheet)
        self.btn_cancel.setGraphicsEffect(Shadow(0, 0, 20))

        # 个人信息按钮
        self.btn_user_info = Button()
        self.btn_user_info.setText("个人信息")
        self.btn_user_info.setFixedSize(btn_sidebar_size)
        self.btn_user_info.setStyleSheet(btn_sidebar_stylesheet)
        self.btn_user_info.setGraphicsEffect(Shadow(0, 0, 20))

        # 表格
        self.table = Table(parent=self)
        self.table.move(self.sidebar.width() + 20, 20)
        self.table.setMinimumSize(self.width() - self.sidebar.width() - 2 * 20, self.height() - 2 * 20)
        self.table.setStyleSheet("""
        QWidget {
            border: 0;
            outline: none;
            font-size: 18px;
        }
        """)
        self.table.setColumnCount(3)
        self.table.horizontalHeader().setDefaultSectionSize(self.table.width() // 3)
        self.table.setHorizontalHeaderLabels(["123", "1321", "312123"])

    def init_layout(self) -> None:
        """
        初始化布局
        """
        self.sidebar.add_widget(self.btn_course_info)
        self.sidebar.add_widget(self.btn_selected)
        self.sidebar.add_widget(self.btn_select)
        self.sidebar.add_widget(self.btn_cancel)
        self.sidebar.add_widget(self.btn_user_info)
