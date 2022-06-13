# -*- coding: utf-8 -*-
"""
...@version: python 3.7
...@author: Karbob
...@fileName: MainWindow.py
...@description:
...@date: 2022-06-08
"""
from pymssql import Connection
from typing import List, Dict, Any, Optional
from config import config
from widgets.Login import Login
from widgets.Student import Student
from widgets.Teacher import Teacher
from widgets.Admin import Admin
from widgets.Base import MsConnectThread, MsSQLThread, ThreadPool, HLayout, TableModal
from PyQt5.QtWidgets import QWidget, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCloseEvent


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

        if user_name == config.ADMIN_ACCOUNT and password == config.ADMIN_PASSWORD:
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
        self.student.table.clear()
        self.student.table.setRowCount(len(data))
        self.student.table.setColumnCount(len(header))
        self.student.table.setHorizontalHeaderLabels(header)
        for row, course_info in enumerate(data):
            for column, item in enumerate(course_info.values()):
                self.student.table.setItem(row, column, QTableWidgetItem(str(item).encode("latin1").decode("gbk")))

    def slot_student_course_manage_data(self, data: Optional[List[Dict[str, Any]]]) -> None:
        """
        学生系统
        查询所有选课信息信号槽
        """
        if data is None:
            QMessageBox.critical(self, "错误", "获取数据失败", QMessageBox.Ok)
            return

        if not data:
            QMessageBox.information(self, "提示", "没有查询到数据", QMessageBox.Ok)
            return

        header = data[0].keys()
        self.student.table.clear()
        self.student.table.setRowCount(len(data))
        self.student.table.setColumnCount(len(header))
        self.student.table.setHorizontalHeaderLabels(header)
        for row, course_info in enumerate(data):
            for column, item in enumerate(course_info.values()):
                if column+1 == self.student.table.columnCount():
                    # 表格内的按钮
                    button = self.student.get_btn_select_course() if str(item) == "0" \
                             else self.student.get_btn_cancel_course()
                    button.setObjectName(str(row))
                    button.clicked.connect(self.slot_student_table_btn_course_manage_click)
                    # 空白widget, 使按钮在表格中居中
                    widget = QWidget()
                    widget.setObjectName(str(item))
                    layout = HLayout()
                    layout.setAlignment(Qt.AlignCenter)
                    layout.addWidget(button)
                    widget.setLayout(layout)
                    # 表格最后一行添加按钮
                    self.student.table.setCellWidget(row, column, widget)
                    continue
                self.student.table.setItem(row, column, QTableWidgetItem(str(item).encode("latin1").decode("gbk")))

    def slot_student_table_course_manage_data(self, data: Optional[bool]) -> None:
        """
        学生系统
        选课或退选信号槽
        """
        if data is None:
            QMessageBox.critical(self, "错误", "获取数据失败", QMessageBox.Ok)
            return

        if not data:
            QMessageBox.information(self, "提示", "没有查询到数据", QMessageBox.Ok)
            return

        # 获取按钮所在行和列
        row = self.student.table.row
        column = self.student.table.columnCount() - 1
        # 获取按钮所在的控件上
        widget: QWidget = self.student.table.cellWidget(row, column)
        # 切换按钮
        if widget.objectName() == "0":
            button = self.student.get_btn_cancel_course()
            widget = QWidget()
            widget.setObjectName("1")
        else:
            button = self.student.get_btn_select_course()
            widget = QWidget()
            widget.setObjectName("0")
        button.setObjectName(str(row))
        button.clicked.connect(self.slot_student_table_btn_course_manage_click)
        layout = HLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(button)
        widget.setLayout(layout)
        self.student.table.setCellWidget(row, column, widget)

    def slot_student_btn_course_info_click(self) -> None:
        """
        学生系统
        点击课程信息按钮信号槽
        """
        sql = "SELECT 课程号,课程名,学时,学分,授课老师 FROM Course_info"
        thread = MsSQLThread(self.connection, sql)
        thread.data_signal.connect(self.slot_student_fetchall_data)
        self.thread_pool.start(thread)

    def slot_student_btn_selected_course_click(self) -> None:
        """
        学生系统
        点击已选课程按钮信号槽
        """
        user_id = self.student.user_data["学号"]
        sql = f"SELECT 课程号,已选课程 as 课程名,学时,学分,授课老师 FROM Course_choosen WHERE 学号='{user_id}'"
        thread = MsSQLThread(self.connection, sql)
        thread.data_signal.connect(self.slot_student_fetchall_data)
        self.thread_pool.start(thread)

    def slot_student_table_btn_course_manage_click(self) -> None:
        """
        学生系统
        点击选课按钮信号槽
        """
        # 获取学号和课程号
        user_id = self.student.user_data["学号"]
        row = int(self.student.table.sender().objectName())
        course_id = self.student.table.item(row, 0).text()
        # 设置当前行
        self.student.table.row = row
        # 执行sql
        sql = f"exec Choose_or_not '{user_id}','{course_id}'"
        thread = MsSQLThread(self.connection, sql)
        thread.data_signal.connect(self.slot_student_table_course_manage_data)
        self.thread_pool.start(thread)

    def slot_student_btn_course_manage_click(self) -> None:
        """
        学生系统
        点击选课按钮信号槽
        """
        user_id = self.student.user_data["学号"]
        sql = f"select 课程号,课程名,学时,学分,授课老师,选课状态 as 操作 from Course_status('{user_id}')"
        thread = MsSQLThread(self.connection, sql)
        thread.data_signal.connect(self.slot_student_course_manage_data)
        self.thread_pool.start(thread)

    def slot_student_btn_logout_click(self) -> None:
        """
        学生系统
        点击退出登录按钮的信号槽
        """
        self.student.user_data = None
        self.student.hide()
        self.login.input_user_name.clear()
        self.login.input_password.clear()
        self.login.show()

    def slot_teacher_login_data(self, data: Optional[List[Dict[str, Any]]]) -> None:
        if not data:
            QMessageBox.critical(self, "错误", "账号或密码错误", QMessageBox.Ok)
        else:
            self.login.hide()
            self.teacher.show()
            self.teacher.user_data = {k: str(v).encode("latin1").decode("gbk") for k, v in data[0].items()}

    def slot_teacher_teach_info_data(self, data: Optional[List[Dict[str, Any]]]) -> None:
        """
        教师系统
        查询所有选课学生信息数据的信号槽
        """
        if data is None:
            QMessageBox.critical(self, "错误", "获取数据失败", QMessageBox.Ok)
            return

        if not data:
            QMessageBox.information(self, "提示", "没有查询到数据", QMessageBox.Ok)
            return

        header = list(data[0].keys())
        header.append("")
        self.teacher.table.clear()
        self.teacher.table.setRowCount(len(data))
        self.teacher.table.setColumnCount(len(header))
        self.teacher.table.setHorizontalHeaderLabels(header)
        for row, teach_info in enumerate(data):
            for column, item in enumerate(teach_info.values()):
                # 最后一列添加操作按钮
                if column+2 == self.teacher.table.columnCount():
                    button = self.teacher.get_btn_detail()
                    button.setObjectName(str(row))
                    button.clicked.connect(self.slot_teacher_table_btn_detail_click)
                    widget = QWidget()
                    layout = HLayout()
                    layout.setAlignment(Qt.AlignCenter)
                    layout.addWidget(button)
                    widget.setLayout(layout)
                    self.teacher.table.setCellWidget(row, column+1, widget)
                self.teacher.table.setItem(row, column, QTableWidgetItem(str(item).encode("latin1").decode("gbk")))

    def slot_teacher_table_detail_data(self, data: Optional[List[Dict[str, Any]]]) -> None:
        """
        教师系统
        查询课程的学生详情的信号槽
        """
        if data is None:
            QMessageBox.critical(self, "错误", "获取数据失败", QMessageBox.Ok)
            return

        if not data:
            QMessageBox.information(self, "提示", "没有查询到数据", QMessageBox.Ok)
            return

        # 表格数据
        table_modal = TableModal(self.width(), self.height(), parent=self)
        header = data[0].keys()
        table_modal.table.clear()
        table_modal.table.setRowCount(len(data))
        table_modal.table.setColumnCount(len(header))
        table_modal.table.setHorizontalHeaderLabels(header)
        for row, student_info in enumerate(data):
            for column, item in enumerate(student_info.values()):
                table_modal.table.setItem(row, column, QTableWidgetItem(str(item).encode("latin1").decode("gbk")))
        table_modal.show()

    def slot_teacher_btn_teach_info_click(self) -> None:
        """
        教师系统
        点击授课信息按钮的信号槽
        """
        user_id = self.teacher.user_data["工号"]
        sql = f"SELECT 课程号,已选课程 as 课程名,学时,学分,已选人数 FROM Teach_view WHERE 工号={user_id}"
        thread = MsSQLThread(self.connection, sql)
        thread.data_signal.connect(self.slot_teacher_teach_info_data)
        self.thread_pool.start(thread)

    def slot_teacher_table_btn_detail_click(self) -> None:
        """
        教师系统
        点击表格内的查看详情按钮的信号槽
        """
        user_id = self.teacher.user_data["工号"]
        row = self.teacher.table.sender().objectName()
        course_id = self.teacher.table.item(int(row), 0).text()
        sql = f"SELECT 学号,姓名,学生性别,专业名 FROM Course_choosen WHERE 工号={user_id} AND 课程号={course_id}"
        thread = MsSQLThread(self.connection, sql)
        thread.data_signal.connect(self.slot_teacher_table_detail_data)
        self.thread_pool.start(thread)

    def slot_teacher_btn_logout_click(self) -> None:
        """
        教师系统
        点击退出登录按钮的信号槽
        """
        self.teacher.user_data.clear()
        self.teacher.hide()
        self.login.input_user_name.clear()
        self.login.input_password.clear()
        self.login.show()

    def slot_admin_btn_logout_click(self) -> None:
        """
        管理员
        点击退出登录按钮的信号槽
        """
        self.admin.hide()
        self.login.input_user_name.clear()
        self.login.input_password.clear()
        self.login.show()

    def bind_slot(self) -> None:
        """
        绑定信号槽
        """
        self.login.btn_login.clicked.connect(self.slot_btn_login_click)
        self.student.btn_course_info.clicked.connect(self.slot_student_btn_course_info_click)
        self.student.btn_selected_course.clicked.connect(self.slot_student_btn_selected_course_click)
        self.student.btn_course_manage.clicked.connect(self.slot_student_btn_course_manage_click)
        self.student.btn_logout.clicked.connect(self.slot_student_btn_logout_click)
        self.teacher.btn_teach_info.clicked.connect(self.slot_teacher_btn_teach_info_click)
        self.teacher.btn_logout.clicked.connect(self.slot_teacher_btn_logout_click)
        self.admin.btn_logout.clicked.connect(self.slot_admin_btn_logout_click)

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        窗口关闭事件
        """
        # 关闭数据库连接
        self.connection.close()
        return super().closeEvent(event)
