# -*- coding: utf-8 -*- 
"""
...@version: python 3.7
...@author: Karbob
...@fileName: Admin.py
...@description: 
...@date: 2022-06-10
"""
from PyQt5.QtWidgets import QWidget
from config import config
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor
from widgets.Base import Sidebar, Button, Shadow, Table


class Admin(QWidget):

    sidebar: Sidebar
    btn_student_manage: Button
    btn_teacher_manage: Button
    btn_course_manage: Button
    btn_logout: Button
    table: Table

    def __init__(self, *args, **kwargs) -> None:
        super(Admin, self).__init__(*args, **kwargs)
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

        # 学生管理按钮
        self.btn_student_manage = Button()
        self.btn_student_manage.setText("学生管理")
        self.btn_student_manage.setFixedSize(btn_sidebar_size)
        self.btn_student_manage.setStyleSheet(btn_sidebar_stylesheet)
        self.btn_student_manage.setGraphicsEffect(Shadow(0, 0, 20))

        # 教师管理按钮
        self.btn_teacher_manage = Button()
        self.btn_teacher_manage.setText("教师管理")
        self.btn_teacher_manage.setFixedSize(btn_sidebar_size)
        self.btn_teacher_manage.setStyleSheet(btn_sidebar_stylesheet)
        self.btn_teacher_manage.setGraphicsEffect(Shadow(0, 0, 20))

        # 课程管理
        self.btn_course_manage = Button()
        self.btn_course_manage.setText("课程管理")
        self.btn_course_manage.setFixedSize(btn_sidebar_size)
        self.btn_course_manage.setStyleSheet(btn_sidebar_stylesheet)
        self.btn_course_manage.setGraphicsEffect(Shadow(0, 0, 20))

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

    def init_layout(self) -> None:
        """
        初始化布局
        """
        self.sidebar.add_widget(self.btn_student_manage)
        self.sidebar.add_widget(self.btn_course_manage)
        self.sidebar.add_widget(self.btn_teacher_manage)
        self.sidebar.add_widget(self.btn_logout)
