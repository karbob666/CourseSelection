# -*- coding: utf-8 -*- 
"""
...@version: python 3.7
...@author: Karbob
...@fileName: Teacher.py
...@description: 
...@date: 2022-06-09
"""
from config import config
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor
from widgets.Base import Shadow, Button, Sidebar


class Teacher(QWidget):

    sidebar: Sidebar
    btn_teach_info: Button
    btn_student_info: Button
    btn_user_info: Button

    def __init__(self, *args, **kwargs) -> None:
        super(Teacher, self).__init__(*args, **kwargs)
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

        # 授课信息按钮
        self.btn_teach_info = Button()
        self.btn_teach_info.setText("授课信息")
        self.btn_teach_info.setFixedSize(btn_sidebar_size)
        self.btn_teach_info.setStyleSheet(btn_sidebar_stylesheet)
        self.btn_teach_info.setGraphicsEffect(Shadow(0, 0, 20))

        # 学生信息按钮
        self.btn_student_info = Button()
        self.btn_student_info.setText("学生信息")
        self.btn_student_info.setFixedSize(btn_sidebar_size)
        self.btn_student_info.setStyleSheet(btn_sidebar_stylesheet)
        self.btn_student_info.setGraphicsEffect(Shadow(0, 0, 20))

        # 个人信息按钮
        self.btn_user_info = Button()
        self.btn_user_info.setText("个人信息")
        self.btn_user_info.setFixedSize(btn_sidebar_size)
        self.btn_user_info.setStyleSheet(btn_sidebar_stylesheet)
        self.btn_user_info.setGraphicsEffect(Shadow(0, 0, 20))

    def init_layout(self) -> None:
        """
        初始化布局
        """
        self.sidebar.add_widget(self.btn_teach_info)
        self.sidebar.add_widget(self.btn_student_info)
        self.sidebar.add_widget(self.btn_user_info)
