# -*- coding: utf-8 -*- 
"""
...@version: python 3.7
...@author: Karbob
...@fileName: MainWindow.py
...@description: 
...@date: 2022-06-08
"""
import pymssql
from pymssql import Connection
from typing import List, Dict, Any
from config import config
from widgets.Login import Login
from widgets.Student import Student
from widgets.Teacher import Teacher
from widgets.Admin import Admin
from widgets.Base import MsConnectThread, MsSQLThread
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor


class MainWindow(QWidget):

    login: Login
    student: Student
    teacher: Teacher
    admin: Admin
    connection: Connection
    thread: MsSQLThread

    def __init__(self, *args, **kwargs) -> None:
        super(MainWindow, self).__init__(*args, **kwargs)
        self.init_window()
        self.init_widgets()
        self.bind_slot()
        self.connection = pymssql.connect(**config.DATABASE_CONNECTION)

    def init_window(self) -> None:
        """
        初始化窗口
        """
        self.resize(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)

    def init_widgets(self) -> None:
        """
        初始化控件
        """
        self.login = Login(parent=self)

        self.student = Student(parent=self)
        self.student.hide()

        self.teacher = Teacher(parent=self)
        self.teacher.hide()

        self.admin = Admin(parent=self)
        self.admin.hide()

    def slot_btn_login_click(self) -> None:
        """
        点击登录按钮信号槽
        """
        user_name = self.login.input_user_name.text()
        password = self.login.input_password.text()
        if self.login.rb_student.isChecked():
            sql = f"SELECT * FROM Student WHERE 学号='{user_name}' AND 密码='{password}'"
            self.thread = MsSQLThread(self.connection, sql)
            self.thread.data_signal.connect(self.slot_student_login_data)
            self.thread.start()
        elif self.login.rb_teacher.isChecked():
            self.teacher.show()
            self.login.hide()
        else:
            if user_name == "admin" and password == "123123":
                self.admin.show()
                self.login.hide()

    def slot_student_login_data(self, data: Dict[str, Any]) -> None:
        if data is None:
            print("密码错误")
            print(data)
        else:
            print("密码正确")
            self.login.hide()
            self.student.show()

    def slot_student_fetchall_data(self, data: List[Dict[str, Any]]) -> None:
        """
        学生系统
        查询所有数据信号槽
        """
        header = data[0].keys()
        self.student.table.setColumnCount(len(header))
        self.student.table.horizontalHeader().setDefaultSectionSize(self.student.table.width() // len(header))
        self.student.table.setHorizontalHeaderLabels(header)

    def slot_btn_student_course_info_click(self) -> None:
        """
        学生系统
        点击课程信息按钮
        """
        sql = ""
        thread = MsSQLThread(self.connection, sql)
        thread.data_signal.connect(self.slot_student_fetchall_data)

    def bind_slot(self) -> None:
        """
        绑定信号槽
        """
        self.login.btn_login.clicked.connect(self.slot_btn_login_click)
