# -*- coding: utf-8 -*- 
"""
...@version: python 3.7
...@author: Karbob
...@fileName: Student.py
...@description: 
...@date: 2022-06-09
"""
from config import config
from typing import Dict, Any
from PyQt5.QtWidgets import QWidget, QLabel, QFrame, QAbstractItemView
from PyQt5.QtGui import QPaintEvent, QPainter, QPixmap, QColor
from PyQt5.QtCore import Qt, QSize, QRect
from widgets.Base import Button, Shadow, VLayout, HLayout, Table, Sidebar


class Student(QWidget):

    sidebar: Sidebar
    btn_course_info: Button
    btn_selected_course: Button
    btn_course_manage: Button
    btn_user_info: Button
    btn_logout: Button
    table: Table
    user_data: Dict[str, Any]

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
        self.btn_selected_course = Button()
        self.btn_selected_course.setText("已选课程")
        self.btn_selected_course.setFixedSize(btn_sidebar_size)
        self.btn_selected_course.setStyleSheet(btn_sidebar_stylesheet)
        self.btn_selected_course.setGraphicsEffect(Shadow(0, 0, 20))

        # 选课/退选按钮
        self.btn_course_manage = Button()
        self.btn_course_manage.setText("选课/退选")
        self.btn_course_manage.setFixedSize(btn_sidebar_size)
        self.btn_course_manage.setStyleSheet(btn_sidebar_stylesheet)
        self.btn_course_manage.setGraphicsEffect(Shadow(0, 0, 20))

        # 个人信息按钮
        self.btn_user_info = Button()
        self.btn_user_info.setText("个人信息")
        self.btn_user_info.setFixedSize(btn_sidebar_size)
        self.btn_user_info.setStyleSheet(btn_sidebar_stylesheet)
        self.btn_user_info.setGraphicsEffect(Shadow(0, 0, 20))

        # 退出登录按钮
        self.btn_logout = Button()
        self.btn_logout.setText("退出登录")
        self.btn_logout.setFixedSize(btn_sidebar_size)
        self.btn_logout.setStyleSheet(btn_sidebar_stylesheet)
        self.btn_logout.setGraphicsEffect(Shadow(0, 0, 20))

        # 表格
        self.table = Table(parent=self)
        self.table.move(self.sidebar.width() + 20, 20)
        self.table.setMinimumSize(self.width() - self.sidebar.width() - 2 * 20, self.height() - 2 * 20)
        # 表格不能选中
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        # 表格不可编辑
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def init_layout(self) -> None:
        """
        初始化布局
        """
        self.sidebar.add_widget(self.btn_course_info)
        self.sidebar.add_widget(self.btn_selected_course)
        self.sidebar.add_widget(self.btn_course_manage)
        self.sidebar.add_widget(self.btn_user_info)
        self.sidebar.add_widget(self.btn_logout)

    @staticmethod
    def get_btn_select_course() -> Button:
        """
        获取选课按钮
        """
        button = Button()
        button.setFixedSize(80, 30)
        button.setText("选课")
        button.setStyleSheet("""
        QWidget {
            font-size: 18px;
            border: 0;
            outline: none;
            color: #FFF;
            border-radius: 3px;
            background: rgba(64, 169, 255, 255);
        }
        QWidget:hover {
            background: rgba(64, 169, 255, 200);
        }
        """)
        return button

    @staticmethod
    def get_btn_cancel_course() -> Button:
        """
        获取退选课程按钮
        """
        button = Button()
        button.setFixedSize(80, 30)
        button.setText("退选")
        button.setStyleSheet("""
        QWidget {
            font-size: 18px;
            border: 0;
            outline: none;
            color: #FFF;
            border-radius: 3px;
            background: rgba(255, 77, 79, 255);
        }
        QWidget:hover {
            background: rgba(255, 77, 79, 200);
        }
        """)
        return button
