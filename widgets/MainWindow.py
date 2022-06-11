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
from typing import List, Dict, Any, Optional
from config import config
from widgets.Login import Login
from widgets.Student import Student
from widgets.Teacher import Teacher
from widgets.Admin import Admin
from widgets.Base import MsConnectThread, MsSQLThread, ThreadPool
from PyQt5.QtWidgets import QWidget, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor


class MainWindow(QWidget):

    login: Login
    student: Student
    teacher: Teacher
    admin: Admin
    connection: Connection
    thread_pool: ThreadPool

    def __init__(self, *args, **kwargs) -> None:
        super(MainWindow, self).__init__(*args, **kwargs)
        self.thread_pool = ThreadPool()
        self.connect_database()
        self.init_window()
        self.init_widgets()
        self.bind_slot()

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

    def slot_connect_database(self, connection: Optional[Connection]):
        """
        连接到数据库的信号槽
        """
        if connection is None:
            choice = QMessageBox.critical(self, "错误", "无法连接到数据库", QMessageBox.Retry | QMessageBox.Cancel)
            if choice == QMessageBox.Retry:
                return self.connect_database()
            else:
                return self.close()
        self.connection = connection

    def connect_database(self) -> None:
        """
        连接数据库
        """
        thread = MsConnectThread(**config.DATABASE_CONNECTION)
        thread.connection_signal.connect(self.slot_connect_database)
        self.thread_pool.start(thread)

    def slot_btn_login_click(self) -> None:
        """
        点击登录按钮信号槽
        """
        user_name = self.login.input_user_name.text()
        password = self.login.input_password.text()
        if self.login.rb_student.isChecked():
            sql = f"SELECT * FROM Student WHERE 学号='{user_name}' AND 密码='{password}'"
            thread = MsSQLThread(self.connection, sql)
            thread.data_signal.connect(self.slot_student_login_data)
            self.thread_pool.start(thread)
            return

        if self.login.rb_teacher.isChecked():
            sql = f"SELECT * FROM Teacher WHERE 工号='{user_name}' AND 密码='{password}'"
            thread = MsSQLThread(self.connection, sql)
            thread.data_signal.connect(self.slot_teacher_login_data)
            self.thread_pool.start(thread)
            return

        if user_name == "admin" and password == "123123":
            self.admin.show()
            self.login.hide()
        else:
            QMessageBox.critical(self, "错误", "账号或密码错误", QMessageBox.Ok)

    def slot_student_login_data(self, data: Optional[List[Dict[str, Any]]]) -> None:
        if not data:
            QMessageBox.critical(self, "错误", "账号或密码错误", QMessageBox.Ok)
        else:
            self.login.hide()
            self.student.show()
            self.student.user_data = {k: str(v).encode("latin1").decode("gbk") for k, v in data[0].items()}

    def slot_teacher_login_data(self, data: Optional[List[Dict[str, Any]]]) -> None:
        if not data:
            QMessageBox.critical(self, "错误", "账号或密码错误", QMessageBox.Ok)
        else:
            self.login.hide()
            self.teacher.show()
            self.teacher.user_data = {k: str(v).encode("latin1").decode("gbk") for k, v in data[0].items()}

    def slot_student_fetchall_data(self, data: Optional[List[Dict[str, Any]]]) -> None:
        """
        学生系统
        查询所有数据信号槽
        """
        if data is None:
            QMessageBox.critical(self, "错误", "获取数据失败", QMessageBox.Ok)
            return

        if not data:
            QMessageBox.information(self, "提示", "没有查询到数据", QMessageBox.Ok)
            return

        header = data[0].keys()
        self.student.table.setRowCount(len(data))
        self.student.table.setColumnCount(len(header))
        self.student.table.horizontalHeader().setDefaultSectionSize(self.student.table.width() // len(header))
        self.student.table.setHorizontalHeaderLabels(header)
        for row, course_info in enumerate(data):
            for column, item in enumerate(course_info.values()):
                self.student.table.setItem(row, column, QTableWidgetItem(str(item).encode("latin1").decode("gbk")))

    def slot_student_btn_course_info_click(self) -> None:
        """
        学生系统
        点击课程信息按钮
        """
        sql = "SELECT 课程号,课程名,学分,学时,授课老师 FROM Course_info"
        thread = MsSQLThread(self.connection, sql)
        thread.data_signal.connect(self.slot_student_fetchall_data)
        self.thread_pool.start(thread)

    def slot_student_btn_selected_click(self) -> None:
        """
        学生系统
        点击已选课程按钮
        """
        user_id = self.student.user_data["学号"]
        sql = f"SELECT 已选课程,学分,学时,授课老师 FROM Course_choosen WHERE 学号='{user_id}'"
        thread = MsSQLThread(self.connection, sql)
        thread.data_signal.connect(self.slot_student_fetchall_data)
        self.thread_pool.start(thread)

    def bind_slot(self) -> None:
        """
        绑定信号槽
        """
        self.login.btn_login.clicked.connect(self.slot_btn_login_click)
        self.student.btn_course_info.clicked.connect(self.slot_student_btn_course_info_click)
        self.student.btn_selected.clicked.connect(self.slot_student_btn_selected_click)
