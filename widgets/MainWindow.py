# -*- coding: utf-8 -*-
"""
...@version: python 3.7
...@author: Karbob
...@fileName: MainWindow.py
...@description:
...@date: 2022-06-08
"""
from pymssql import Connection
from typing import List, Dict, Any, Optional, Union
from config import config
from widgets.Login import Login
from widgets.Student import Student
from widgets.Teacher import Teacher
from widgets.Admin import Admin
from widgets.Base import MsConnectThread, MsSQLThread, ThreadPool, HLayout, Modal, Table, InputModal, Button
from PyQt5.QtWidgets import QWidget, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCloseEvent, QResizeEvent


class MainWindow(QWidget):

    login: Login
    student: Student
    teacher: Teacher
    admin: Admin
    modal: Union[Modal, InputModal]
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
        self.login.btn_login.set_loading(True)
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
        self.login.btn_login.set_loading(False)

    def slot_student_login_data(self, data: Optional[List[Dict[str, Any]]]) -> None:
        if not data:
            QMessageBox.critical(self, "错误", "账号或密码错误", QMessageBox.Ok)
        else:
            self.login.hide()
            self.student.show()
            self.student.user_data = {k: str(v).strip().encode("latin1").decode("gbk") for k, v in data[0].items()}
        self.login.btn_login.set_loading(False)

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
                item = QTableWidgetItem(str(item).strip().encode("latin1").decode("gbk"))
                self.student.table.setItem(row, column, item)

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
                item = QTableWidgetItem(str(item).strip().encode("latin1").decode("gbk"))
                self.student.table.setItem(row, column, item)

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
        sql = "SELECT 课程号,课程名,学时,学分,授课老师 FROM Course_taught"
        thread = MsSQLThread(self.connection, sql)
        thread.data_signal.connect(self.slot_student_fetchall_data)
        self.thread_pool.start(thread)

    def slot_student_btn_selected_course_click(self) -> None:
        """
        学生系统
        点击已选课程按钮信号槽
        """
        user_id = self.student.user_data["学号"]
        sql = f"SELECT 课程号,已选课程 AS 课程名,学时,学分,授课老师 FROM Course_choosen WHERE 学号='{user_id}'"
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
        sql = f"SELECT 课程号,课程名,学时,学分,授课老师,选课状态 AS 操作 FROM Course_status('{user_id}')"
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
            self.teacher.user_data = {k: str(v).strip().encode("latin1").decode("gbk") for k, v in data[0].items()}
        self.login.btn_login.set_loading(False)

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
                item = QTableWidgetItem((str(item).strip().encode("latin1").decode("gbk")))
                self.teacher.table.setItem(row, column, item)

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
        self.modal = Modal(self.width(), self.height(), parent=self)
        self.modal.set_title("授课详情")
        table = Table()
        header = data[0].keys()
        table.setRowCount(len(data))
        table.setColumnCount(len(header))
        table.setHorizontalHeaderLabels(header)
        for row, student_info in enumerate(data):
            for column, item in enumerate(student_info.values()):
                item = QTableWidgetItem(str(item).strip().encode("latin1").decode("gbk"))
                table.setItem(row, column, item)
        self.modal.set_widget(table)
        self.modal.show()

    def slot_teacher_btn_teach_info_click(self) -> None:
        """
        教师系统
        点击授课信息按钮的信号槽
        """
        user_id = self.teacher.user_data["工号"]
        sql = f"SELECT 课程号,已选课程 AS 课程名,学时,学分,已选人数 FROM Teach_view WHERE 工号={user_id}"
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

    def slot_admin_student_manage_data(self, data: Optional[List[Dict[str, Any]]]) -> None:
        """
        管理员
        查询学生管理信息的信号槽
        """
        if data is None:
            QMessageBox.critical(self, "错误", "获取数据失败", QMessageBox.Ok)
            return

        if not data:
            QMessageBox.information(self, "提示", "没有查询到数据", QMessageBox.Ok)
            return

        header = list(data[0].keys())
        header.extend(["" for _ in range(2)])
        self.admin.table.clear()
        self.admin.table.setRowCount(len(data))
        self.admin.table.setColumnCount(len(header))
        self.admin.table.setHorizontalHeaderLabels(header)
        for row, student_info in enumerate(data):
            for column, item in enumerate(student_info.values()):
                # 最后一列添加操作按钮
                if column+1 == self.admin.table.columnCount()-2:
                    # 修改按钮
                    button = self.admin.get_btn_modify()
                    button.setObjectName(str(row))
                    button.clicked.connect(self.slot_admin_table_btn_student_manage_modify_click)
                    widget = QWidget()
                    layout = HLayout()
                    layout.setAlignment(Qt.AlignCenter)
                    layout.addWidget(button)
                    widget.setLayout(layout)
                    self.admin.table.setCellWidget(row, column+1, widget)
                    # 删除按钮
                    button = self.admin.get_btn_delete()
                    button.setObjectName(str(row))
                    button.clicked.connect(self.slot_admin_table_btn_student_manage_delete_click)
                    widget = QWidget()
                    layout = HLayout()
                    layout.setAlignment(Qt.AlignCenter)
                    layout.addWidget(button)
                    widget.setLayout(layout)
                    self.admin.table.setCellWidget(row, column+2, widget)
                item = QTableWidgetItem(str(item).strip().encode("latin1").decode("gbk"))
                self.admin.table.setItem(row, column, item)

    def slot_admin_course_manage_data(self, data: Optional[List[Dict[str, Any]]]) -> None:
        """
        管理员
        查询课程管理数据的信号槽
        """
        if data is None:
            QMessageBox.critical(self, "错误", "获取数据失败", QMessageBox.Ok)
            return

        if not data:
            QMessageBox.information(self, "提示", "没有查询到数据", QMessageBox.Ok)
            return

        header = list(data[0].keys())
        header.extend([""] * 3)
        self.admin.table.clear()
        self.admin.table.setRowCount(len(data))
        self.admin.table.setColumnCount(len(header))
        self.admin.table.setHorizontalHeaderLabels(header)
        for row, student_info in enumerate(data):
            for column, item in enumerate(student_info.values()):
                # 最后一列添加操作按钮
                if column+1 >= self.admin.table.columnCount()-3:
                    # 管理按钮
                    button = self.admin.get_btn_modify()
                    button.setObjectName(str(row))
                    button.setText("管理")
                    button.clicked.connect(self.slot_admin_table_btn_course_manage_student_click)
                    widget = QWidget()
                    layout = HLayout()
                    layout.setAlignment(Qt.AlignCenter)
                    layout.addWidget(button)
                    widget.setLayout(layout)
                    self.admin.table.setCellWidget(row, column+1, widget)
                    # 修改课程
                    button = self.admin.get_btn_modify()
                    button.setObjectName(str(row))
                    button.setText("修改")
                    button.clicked.connect(self.slot_admin_table_btn_course_manage_modify_click)
                    widget = QWidget()
                    layout = HLayout()
                    layout.setAlignment(Qt.AlignCenter)
                    layout.addWidget(button)
                    widget.setLayout(layout)
                    self.admin.table.setCellWidget(row, column+2, widget)
                    # 删除课程
                    button = self.admin.get_btn_delete()
                    button.setObjectName(str(row))
                    button.clicked.connect(self.slot_admin_table_btn_course_manage_delete_click)
                    widget = QWidget()
                    layout = HLayout()
                    layout.setAlignment(Qt.AlignCenter)
                    layout.addWidget(button)
                    widget.setLayout(layout)
                    self.admin.table.setCellWidget(row, column+3, widget)

                item = QTableWidgetItem(str(item).strip().encode("latin1").decode("gbk"))
                self.admin.table.setItem(row, column, item)

    def slot_admin_teacher_manage_data(self, data: Optional[List[Dict[str, Any]]]) -> None:
        """
        管理员
        教师管理数据的信号槽
        """
        if data is None:
            QMessageBox.critical(self, "错误", "获取数据失败", QMessageBox.Ok)
            return

        if not data:
            QMessageBox.information(self, "提示", "没有查询到数据", QMessageBox.Ok)
            return

        # 添加数据到表格
        header = list(data[0].keys())
        header.extend(["" for _ in range(3)])
        self.admin.table.clear()
        self.admin.table.setRowCount(len(data))
        self.admin.table.setColumnCount(len(header))
        self.admin.table.setHorizontalHeaderLabels(header)
        for row, student_info in enumerate(data):
            for column, item in enumerate(student_info.values()):
                # 最后一列添加操作按钮
                if column+1 == self.admin.table.columnCount()-3:
                    # 授课管理按钮
                    button = self.admin.get_btn_modify()
                    button.setObjectName(str(row))
                    button.setText("管理")
                    button.clicked.connect(self.slot_admin_table_btn_teacher_manage_course_click)
                    widget = QWidget()
                    layout = HLayout()
                    layout.setAlignment(Qt.AlignCenter)
                    layout.addWidget(button)
                    widget.setLayout(layout)
                    self.admin.table.setCellWidget(row, column+1, widget)
                    # 修改按钮
                    button = self.admin.get_btn_modify()
                    button.setObjectName(str(row))
                    button.clicked.connect(self.slot_admin_table_btn_teacher_manage_modify_click)
                    widget = QWidget()
                    layout = HLayout()
                    layout.setAlignment(Qt.AlignCenter)
                    layout.addWidget(button)
                    widget.setLayout(layout)
                    self.admin.table.setCellWidget(row, column+2, widget)
                    # 删除按钮
                    button = self.admin.get_btn_delete()
                    button.setObjectName(str(row))
                    button.clicked.connect(self.slot_admin_table_btn_teacher_manage_delete_click)
                    widget = QWidget()
                    layout = HLayout()
                    layout.setAlignment(Qt.AlignCenter)
                    layout.addWidget(button)
                    widget.setLayout(layout)
                    self.admin.table.setCellWidget(row, column+3, widget)
                item = QTableWidgetItem(str(item).strip().encode("latin1").decode("gbk"))
                self.admin.table.setItem(row, column, item)

    def slot_admin_modal_student_manage_insert_data(self, data: Optional[bool]) -> None:
        """
        管理员
        学生管理添加按钮弹出的模态框中完成按钮返回数据的信号槽
        """
        if not data:
            QMessageBox.critical(self, "错误", "修改失败", QMessageBox.Ok)
            return
        # 刷新数据表
        self.slot_admin_btn_student_manage_click()
        self.modal.close()

    def slot_admin_modal_student_manage_modify_data(self, data: Optional[bool]) -> None:
        """
        管理员
        学生管理修改按钮弹出的模态框中的完成按钮返回数据的信号槽
        """
        if not data:
            QMessageBox.critical(self, "错误", "修改失败", QMessageBox.Ok)
            return
        # 修改表格中数据
        items = [_input.text() for _input in self.modal.input_list]
        row = self.admin.table.row
        for column, item in enumerate(items):
            self.admin.table.setItem(row, column, QTableWidgetItem(item))
        # 关闭模态框
        self.modal.close()

    def slot_admin_table_student_manage_delete_data(self, data: Optional[bool]) -> None:
        """
        管理员
        学生管理表中删除按钮数据的信号槽
        """
        if not data:
            QMessageBox.critical(self, "错误", "删除失败", QMessageBox.Ok)
            return
        # 删除表格数据
        row = self.admin.table.row
        self.admin.table.removeRow(row)

    def slot_admin_modal_course_manage_insert_data(self, data: Optional[bool]) -> None:
        """
        管理员
        课程管理表中添加按钮弹出的模态框完成按钮数据的信号槽
        """
        if not data:
            QMessageBox.critical(self, "错误", "添加失败", QMessageBox.Ok)
            return
        # 刷新数据表
        self.slot_admin_btn_course_manage_click()
        self.modal.close()

    def slot_admin_modal_course_manage_modify_data(self, data: Optional[bool]) -> None:
        """
        管理员
        """
        if not data:
            QMessageBox.critical(self, "错误", "修改失败", QMessageBox.Ok)
            return
        # 修改表格中的数据
        items = [_input.text() for _input in self.modal.input_list]
        row = self.admin.table.row
        for column, item in enumerate(items):
            self.admin.table.setItem(row, column, QTableWidgetItem(item))
        # 关闭模态框
        self.modal.close()

    def slot_admin_table_course_manage_student_data(self, data: Optional[List[Dict[str, Any]]]) -> None:
        """
        管理员
        课程管理表中管理按钮数据的信号槽
        """
        if data is None:
            QMessageBox.critical(self, "错误", "获取数据失败", QMessageBox.Ok)
            return

        if not data:
            QMessageBox.information(self, "提示", "该课程还没有授课老师！", QMessageBox.Ok)
            return

        # 添加数据
        table = Table()
        header = data[0].keys()
        table.setRowCount(len(data))
        table.setColumnCount(len(header))
        table.setHorizontalHeaderLabels(header)
        for row, student_info in enumerate(data):
            for column, item in enumerate(student_info.values()):
                if column+1 == table.columnCount():
                    # 表格内的按钮
                    button = self.student.get_btn_select_course() if str(item) == "0" \
                             else self.student.get_btn_cancel_course()
                    button.setObjectName(str(row))
                    button.clicked.connect(self.slot_admin_modal_btn_course_manage_student_click)
                    # 空白widget, 使按钮在表格中居中
                    widget = QWidget()
                    widget.setObjectName(str(item))
                    layout = HLayout()
                    layout.setAlignment(Qt.AlignCenter)
                    layout.addWidget(button)
                    widget.setLayout(layout)
                    # 表格最后一行添加按钮
                    table.setCellWidget(row, column, widget)
                    continue
                item = QTableWidgetItem(str(item).strip().encode("latin1").decode("gbk"))
                table.setItem(row, column, item)
        self.modal = Modal(self.width(), self.height(), parent=self)
        self.modal.set_title("学生课程管理")
        self.modal.set_widget(table)
        self.modal.show()
        setattr(self.modal, "table", table)

    def slot_admin_modal_course_manage_student_data(self, data: Optional[bool]) -> None:
        """
        管理员
        课程管理表中管理按钮弹出的模态框中 选课/退选 按钮数据的信号槽
        """
        if data is None:
            QMessageBox.critical(self, "错误", "获取数据失败", QMessageBox.Ok)
            return

        if not data:
            QMessageBox.information(self, "提示", "没有查询到数据", QMessageBox.Ok)
            return

        # 获取按钮所在行和列
        table: Table = getattr(self.modal, "table")
        row = table.row
        column = table.columnCount() - 1
        # 获取按钮所在的控件上
        widget: QWidget = table.cellWidget(row, column)
        # 切换按钮
        if widget.objectName() == "0":
            button = self.student.get_btn_cancel_course()
            widget = QWidget()
            widget.setObjectName("1")
            item = QTableWidgetItem(str(int(self.admin.table.item(self.admin.table.row, 2).text()) + 1))
            self.admin.table.setItem(self.admin.table.row, 2, item)
        else:
            button = self.student.get_btn_select_course()
            widget = QWidget()
            widget.setObjectName("0")
            item = QTableWidgetItem(str(int(self.admin.table.item(self.admin.table.row, 2).text()) - 1))
            self.admin.table.setItem(self.admin.table.row, 2, item)
        button.setObjectName(str(row))
        button.clicked.connect(self.slot_admin_modal_btn_course_manage_student_click)
        layout = HLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(button)
        widget.setLayout(layout)
        table.setCellWidget(row, column, widget)

    def slot_admin_table_course_manage_delete_data(self, data: Optional[bool]) -> None:
        """
        管理员
        课程管理表中删除按钮数据的信号槽
        """
        if not data:
            QMessageBox.critical(self, "错误", "删除失败", QMessageBox.Ok)
            return
        # 删除表格数据
        row = self.admin.table.row
        self.admin.table.removeRow(row)

    def slot_admin_modal_teacher_manage_insert_data(self, data: Optional[bool]) -> None:
        """
        管理员
        教师管理中添加按钮弹出的模态框中完成按钮的信号槽
        """
        if not data:
            QMessageBox.critical(self, "错误", "添加失败", QMessageBox.Ok)
            return
        # 刷新数据表
        self.slot_admin_btn_teacher_manage_click()
        self.modal.close()

    def slot_admin_modal_teacher_manage_modify_data(self, data: Optional[bool]) -> None:
        """
        管理员
        教师管理表中删除按钮弹出的模态框中完成按钮的信号槽
        """
        if not data:
            QMessageBox.critical(self, "错误", "修改失败", QMessageBox.Ok)
            return
        # 修改表格中的数据
        items = [_input.text() for _input in self.modal.input_list]
        row = self.admin.table.row
        for column, item in enumerate(items):
            self.admin.table.setItem(row, column, QTableWidgetItem(item))
        # 关闭模态框
        self.modal.close()

    def slot_admin_table_teacher_manage_delete_data(self, data: Optional[bool]) -> None:
        """
        管理员
        教师管理表中删除按钮数据的信号槽
        """
        if not data:
            QMessageBox.critical(self, "错误", "删除失败", QMessageBox.Ok)
            return
        # 删除表格数据
        row = self.admin.table.row
        self.admin.table.removeRow(row)

    def slot_admin_table_teacher_manage_course_data(self, data: Optional[List[Dict[str, Any]]]) -> None:
        """
        管理员
        教师管理表中管理按钮数据的信号槽
        """
        if data is None:
            QMessageBox.critical(self, "错误", "获取数据失败", QMessageBox.Ok)
            return

        if not data:
            QMessageBox.information(self, "提示", "没有查询到数据", QMessageBox.Ok)
            return

        # 添加数据
        table = Table()
        header = data[0].keys()
        table.setRowCount(len(data))
        table.setColumnCount(len(header))
        table.setHorizontalHeaderLabels(header)
        for row, course_info in enumerate(data):
            for column, item in enumerate(course_info.values()):
                if column+1 == table.columnCount():
                    # 表格内的按钮
                    if str(item) == "0":
                        button = self.teacher.get_btn_detail()
                        button.setText("授课")
                        button.clicked.connect(self.slot_admin_modal_btn_teacher_manage_course_teach_click)
                    else:
                        button = self.teacher.get_btn_cancel()
                        button.clicked.connect(self.slot_admin_modal_btn_teacher_manage_course_cancel_click)
                    button.setObjectName(str(row))
                    # 空白widget, 使按钮在表格中居中
                    widget = QWidget()
                    widget.setObjectName(str(item))
                    layout = HLayout()
                    layout.setAlignment(Qt.AlignCenter)
                    layout.addWidget(button)
                    widget.setLayout(layout)
                    # 表格最后一行添加按钮
                    table.setCellWidget(row, column, widget)
                    continue
                item = QTableWidgetItem(str(item or "").strip().encode("latin1").decode("gbk"))
                table.setItem(row, column, item)
        self.modal = Modal(self.width(), self.height(), parent=self)
        self.modal.set_title("教师授课管理")
        self.modal.set_widget(table)
        self.modal.show()
        setattr(self.modal, "table", table)

    def slot_admin_modal_teacher_manage_course_teach_data(self, data: Optional[bool]) -> None:
        """
        管理员
        教师管理表中管理按钮弹出的模态框中授课按钮数据的信号槽
        """
        if data is None:
            QMessageBox.critical(self, "错误", "获取数据失败", QMessageBox.Ok)
            return

        if not data:
            QMessageBox.information(self, "提示", "没有查询到数据", QMessageBox.Ok)
            return

        # 获取按钮所在行和列
        table: Table = getattr(self.modal, "table")
        row = table.row
        column = table.columnCount() - 1
        # 关闭编辑模式
        table.closePersistentEditor(table.item(row, 2))
        table.closePersistentEditor(table.item(row, 3))
        # 授课数目 +1
        item = QTableWidgetItem(str(int(self.admin.table.item(self.admin.table.row, 4).text()) + 1))
        self.admin.table.setItem(self.admin.table.row, 4, item)
        # 切换按钮
        button = self.teacher.get_btn_cancel()
        button.setObjectName(str(row))
        button.clicked.connect(self.slot_admin_modal_btn_teacher_manage_course_cancel_click)
        widget = QWidget()
        layout = HLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(button)
        widget.setLayout(layout)
        table.setCellWidget(row, column, widget)

    def slot_admin_modal_teacher_manage_course_cancel_data(self, data: Optional[bool]) -> None:
        """
        管理员
        教师管理表中管理按钮弹出的模态框中授课按钮数据的信号槽
        """
        if data is None:
            QMessageBox.critical(self, "错误", "获取数据失败", QMessageBox.Ok)
            return

        if not data:
            QMessageBox.information(self, "提示", "没有查询到数据", QMessageBox.Ok)
            return

        # 获取按钮所在行和列
        table: Table = getattr(self.modal, "table")
        row = table.row
        column = table.columnCount() - 1
        # 授课数目 -1
        item = QTableWidgetItem(str(int(self.admin.table.item(self.admin.table.row, 4).text()) - 1))
        self.admin.table.setItem(self.admin.table.row, 4, item)
        # 设置学时和学分为空
        table.setItem(row, 2, QTableWidgetItem(str()))
        table.setItem(row, 3, QTableWidgetItem(str()))
        # 切换按钮
        button = self.teacher.get_btn_detail()
        button.setText("授课")
        button.setObjectName(str(row))
        button.clicked.connect(self.slot_admin_modal_btn_teacher_manage_course_teach_click)
        widget = QWidget()
        layout = HLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(button)
        widget.setLayout(layout)
        table.setCellWidget(row, column, widget)

    def slot_admin_modal_btn_student_manage_insert_click(self) -> None:
        """
        管理员
        学生管理添加按钮弹出的模态框中完成按钮的信号槽
        """
        data = [_input.text() for _input in self.modal.input_list]
        sql = "INSERT INTO Student VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(*data)
        thread = MsSQLThread(self.connection, sql)
        thread.data_signal.connect(self.slot_admin_modal_student_manage_insert_data)
        self.thread_pool.start(thread)

    def slot_admin_table_btn_student_manage_modify_click(self) -> None:
        """
        管理员
        学生管理表格中点击修改按钮的信号槽
        """
        row = int(self.admin.table.sender().objectName())
        self.admin.table.row = row
        header = [self.admin.table.horizontalHeaderItem(i).text() for i in range(self.admin.table.columnCount()-1)]
        items = [self.admin.table.item(row, column).text() for column in range(self.admin.table.columnCount()-1)]
        self.modal = InputModal(self.width(), self.height(), parent=self)
        self.modal.set_content(header, items)
        self.modal.set_title("修改学生信息")
        self.modal.input_at(0).setReadOnly(True)
        self.modal.btn_complete.clicked.connect(self.slot_admin_modal_btn_student_manage_modify_click)
        self.modal.show()

    def slot_admin_modal_btn_student_manage_modify_click(self) -> None:
        """
        管理员
        学生管理修改按钮弹出的模态框中的完成按钮的信号槽
        """
        data = [_input.text() for _input in self.modal.input_list]
        user_id = data.pop(0)
        data.append(user_id)
        sql = "UPDATE Student SET 姓名='{}',性别='{}',年龄='{}',专业名='{}',密码='{}',备注='{}' WHERE 学号='{}'".format(*data)
        thread = MsSQLThread(self.connection, sql)
        thread.data_signal.connect(self.slot_admin_modal_student_manage_modify_data)
        self.thread_pool.start(thread)

    def slot_admin_table_btn_student_manage_delete_click(self) -> None:
        """
        管理员
        学生管理表中删除按钮的信号槽
        """
        choice = QMessageBox.warning(self, "警告", "你确定要删除吗？", QMessageBox.Ok | QMessageBox.Cancel)
        if choice == QMessageBox.Ok:
            row = int(self.admin.table.sender().objectName())
            self.admin.table.row = row
            user_id = self.admin.table.item(row, 0).text()
            sql = f"DELETE FROM Student WHERE 学号='{user_id}'"
            thread = MsSQLThread(self.connection, sql)
            thread.data_signal.connect(self.slot_admin_table_student_manage_delete_data)
            self.thread_pool.start(thread)

    def slot_admin_modal_btn_course_manage_insert_click(self) -> None:
        """
        管理员
        课程管理中点击添加按钮弹出的模态框中完成按钮的数据
        """
        data = [_input.text().strip() for _input in self.modal.input_list]
        sql = "INSERT INTO Course VALUES('{}', '{}')".format(*data[:2])
        thread = MsSQLThread(self.connection, sql)
        thread.data_signal.connect(self.slot_admin_modal_course_manage_insert_data)
        self.thread_pool.start(thread)

    def slot_admin_modal_btn_course_manage_modify_click(self) -> None:
        """
        管理员
        课程管理表中修改按钮弹出的模态框的完成按钮的信号槽
        """
        data = [_input.text() for _input in self.modal.input_list]
        user_id = data.pop(0)
        data[-1] = user_id
        sql = "UPDATE Course SET 课程名='{}' WHERE 课程号='{}'".format(*data)
        thread = MsSQLThread(self.connection, sql)
        thread.data_signal.connect(self.slot_admin_modal_course_manage_modify_data)
        self.thread_pool.start(thread)

    def slot_admin_table_btn_course_manage_student_click(self) -> None:
        """
        管理员
        课程管理表中管理按钮的信号槽
        主要用于管理学生的选课
        """
        row = int(self.admin.table.sender().objectName())
        self.admin.table.row = row
        course_id = self.admin.table.item(row, 0).text()
        sql = f"SELECT 学号,姓名,专业名,选课管理 AS 操作 FROM Course_stuinfo('{course_id}')"
        thread = MsSQLThread(self.connection, sql)
        thread.data_signal.connect(self.slot_admin_table_course_manage_student_data)
        self.thread_pool.start(thread)

    def slot_admin_modal_btn_course_manage_student_click(self) -> None:
        """
        管理员
        课程管理表中管理按钮弹出的模态框中 选课/退选 按钮的信号槽
        """
        # 获取学号和课程号
        row = int(self.modal.sender().objectName())
        table: Table = getattr(self.modal, "table")
        table.row = row
        user_id = table.item(row, 0).text()
        course_id = self.admin.table.item(self.admin.table.row, 0).text()
        # 执行sql
        sql = f"exec Choose_or_not '{user_id}','{course_id}'"
        thread = MsSQLThread(self.connection, sql)
        thread.data_signal.connect(self.slot_admin_modal_course_manage_student_data)
        self.thread_pool.start(thread)

    def slot_admin_table_btn_course_manage_modify_click(self) -> None:
        """
        管理员
        课程管理表中修改按钮的信号槽
        """
        row = int(self.admin.sender().objectName())
        self.admin.table.row = row
        header = [self.admin.table.horizontalHeaderItem(i).text() for i in range(self.admin.table.columnCount())]
        header = list(filter(lambda x: len(x) > 0, header))
        items = [self.admin.table.item(row, column).text() for column in range(len(header))]
        self.modal = InputModal(self.width(), self.height(), parent=self)
        self.modal.set_title("修改课程信息")
        self.modal.set_content(header, items)
        self.modal.input_at(0).setReadOnly(True)
        self.modal.input_at(-1).setReadOnly(True)
        self.modal.btn_complete.clicked.connect(self.slot_admin_modal_btn_course_manage_modify_click)
        self.modal.show()

    def slot_admin_table_btn_course_manage_delete_click(self) -> None:
        """
        管理员
        课程管理表中点击删除按钮的信号槽
        """
        choice = QMessageBox.warning(self, "警告", "你确定要删除吗？", QMessageBox.Ok | QMessageBox.Cancel)
        if choice == QMessageBox.Ok:
            row = int(self.admin.table.sender().objectName())
            self.admin.table.row = row
            course_id = self.admin.table.item(row, 0).text()
            sql = f"DELETE FROM Course WHERE 课程号={course_id}"
            thread = MsSQLThread(self.connection, sql)
            thread.data_signal.connect(self.slot_admin_table_course_manage_delete_data)
            self.thread_pool.start(thread)

    def slot_admin_modal_btn_teacher_manage_insert_click(self) -> None:
        """
        管理员
        教师管理添加按钮弹出的模态框中完成按钮的信号槽
        """
        data = [_input.text() for _input in self.modal.input_list]
        sql = "INSERT INTO Teacher VALUES('{}', '{}', '{}', '{}')".format(*data[:-1])
        thread = MsSQLThread(self.connection, sql)
        thread.data_signal.connect(self.slot_admin_modal_teacher_manage_insert_data)
        self.thread_pool.start(thread)

    def slot_admin_modal_btn_teacher_manage_modify_click(self) -> None:
        """
        管理员
        教师管理表中修改按钮弹出的模态框中完成按钮的信号槽
        """
        data = [_input.text() for _input in self.modal.input_list]
        user_id = data.pop(0)
        data[-1] = user_id
        sql = "UPDATE Teacher SET 姓名='{}',性别='{}',密码='{}' WHERE 工号='{}'".format(*data)
        thread = MsSQLThread(self.connection, sql)
        thread.data_signal.connect(self.slot_admin_modal_teacher_manage_modify_data)
        self.thread_pool.start(thread)

    def slot_admin_table_btn_teacher_manage_modify_click(self) -> None:
        """
        管理员
        教师管理表中修改按钮的信号槽
        """
        row = int(self.admin.sender().objectName())
        self.admin.table.row = row
        header = [self.admin.table.horizontalHeaderItem(i).text() for i in range(self.admin.table.columnCount())]
        header = list(filter(lambda x: len(x) > 0, header))
        items = [self.admin.table.item(row, column).text() for column in range(len(header))]
        self.modal = InputModal(self.width(), self.height(), parent=self)
        self.modal.set_title("修改教师信息")
        self.modal.set_content(header, items)
        self.modal.input_at(0).setReadOnly(True)
        self.modal.input_at(-1).setReadOnly(True)
        self.modal.btn_complete.clicked.connect(self.slot_admin_modal_btn_teacher_manage_modify_click)
        self.modal.show()

    def slot_admin_table_btn_teacher_manage_delete_click(self) -> None:
        """
        管理员
        教师管理表中删除按钮的信号槽
        """
        choice = QMessageBox.warning(self, "警告", "你确定要删除吗？", QMessageBox.Ok | QMessageBox.Cancel)
        if choice == QMessageBox.Ok:
            row = int(self.admin.table.sender().objectName())
            self.admin.table.row = row
            user_id = self.admin.table.item(row, 0).text()
            sql = f"DELETE FROM Teacher WHERE 工号='{user_id}'"
            thread = MsSQLThread(self.connection, sql)
            thread.data_signal.connect(self.slot_admin_table_teacher_manage_delete_data)
            self.thread_pool.start(thread)

    def slot_admin_table_btn_teacher_manage_course_click(self) -> None:
        """
        管理员
        教师管理表中管理按钮的信号槽
        主要用户给教师授课
        """
        row = int(self.admin.table.sender().objectName())
        self.admin.table.row = row
        user_id = self.admin.table.item(row, 0).text()
        sql = f"SELECT 课程号,课程名,学时,学分,选择 AS 操作 FROM Course_teainfo('{user_id}')"
        thread = MsSQLThread(self.connection, sql)
        thread.data_signal.connect(self.slot_admin_table_teacher_manage_course_data)
        self.thread_pool.start(thread)

    def slot_admin_modal_btn_teacher_manage_course_teach_click(self) -> None:
        """
        管理员
        教师管理表中管理按钮弹出的模态框中授课按钮的信号槽
        """
        # 获取行号
        button = self.modal.sender()
        row = int(button.objectName())
        table: Table = getattr(self.modal, "table")
        table.row = row
        # 开启编辑模式
        table.openPersistentEditor(table.item(row, 2))
        table.openPersistentEditor(table.item(row, 3))
        # 修改按钮的信号槽
        button.setText("完成")
        button.clicked.disconnect()
        button.clicked.connect(self.slot_admin_modal_btn_teacher_manage_course_teach_next_click)

    def slot_admin_modal_btn_teacher_manage_course_teach_next_click(self) -> None:
        """
        管理员
        教师管理表中管理按钮弹出的模态框中授课按钮 -> 完成按钮的信号槽
        """
        # 获取学号 课程号 学时 学分
        table: Table = getattr(self.modal, "table")
        row = table.row
        data = [
            self.admin.table.item(self.admin.table.row, 0).text(),
            table.item(row, 0).text(),
            table.item(row, 2).text(),
            table.item(row, 3).text(),
        ]
        try:
            int(data[-1]) and int(data[-2])
        except ValueError:
            QMessageBox.critical(self, "错误", "学时或学分格式错误", QMessageBox.Ok)
            return
        # 执行sql
        sql = "INSERT INTO TeaCourse VALUES('{}','{}','{}','{}')".format(*data)
        thread = MsSQLThread(self.connection, sql)
        thread.data_signal.connect(self.slot_admin_modal_teacher_manage_course_teach_data)
        self.thread_pool.start(thread)

    def slot_admin_modal_btn_teacher_manage_course_cancel_click(self) -> None:
        """
        管理员
        教师管理表中管理按钮弹出的模态框中取消授课按钮的信号槽
        """
        # 获取工号和课程号
        row = int(self.modal.sender().objectName())
        table: Table = getattr(self.modal, "table")
        table.row = row
        user_id = self.admin.table.item(self.admin.table.row, 0).text()
        course_id = table.item(row, 0).text()
        # 执行sql
        sql = f"DELETE FROM TeaCourse WHERE 工号='{user_id}' AND 课程号='{course_id}'"
        thread = MsSQLThread(self.connection, sql)
        thread.data_signal.connect(self.slot_admin_modal_teacher_manage_course_cancel_data)
        self.thread_pool.start(thread)

    def slot_admin_btn_student_manage_insert_click(self) -> None:
        """
        管理员
        学生管理中添加按钮的信号槽
        """
        header = ["学号", "姓名", "性别", "年龄", "专业名", "密码", "备注"]
        items = ["" for _ in range(len(header))]
        item = self.admin.table.item(self.admin.table.rowCount() - 1, 0)
        if item is not None:
            item = str(int(item.text()) + 1)
        items[0] = item or "200001"
        self.modal = InputModal(self.width(), self.height(), parent=self)
        self.modal.set_title("添加学生")
        self.modal.set_content(header, items)
        self.modal.input_at(0).setReadOnly(True)
        self.modal.btn_complete.clicked.connect(self.slot_admin_modal_btn_student_manage_insert_click)
        self.modal.show()

    def slot_admin_btn_course_manage_insert_click(self) -> None:
        """
        管理员
        课程管理添加按钮的信号槽
        """
        header = ["课程号", "课程名", "选课人数"]
        items = ["" for _ in range(len(header))]
        item = self.admin.table.item(self.admin.table.rowCount() - 1, 0)
        if item is not None:
            item = "%04d" % (int(item.text()) + 1)
        items[0] = item or "0001"
        items[-1] = "0"
        self.modal = InputModal(self.width(), self.height(), parent=self)
        self.modal.set_title("添加课程")
        self.modal.set_content(header, items)
        self.modal.input_at(0).setReadOnly(True)
        self.modal.input_at(-1).setReadOnly(True)
        self.modal.btn_complete.clicked.connect(self.slot_admin_modal_btn_course_manage_insert_click)
        self.modal.show()

    def slot_admin_btn_teacher_manage_insert_click(self) -> None:
        """
        管理员
        教师管理添加按钮的信号槽
        """
        header = ["工号", "姓名", "性别", "密码", "授课数目"]
        items = ["" for _ in range(len(header))]
        item = self.admin.table.item(self.admin.table.rowCount() - 1, 0)
        if item is not None:
            item = "%06d" % (int(item.text()) + 1)
        items[0] = item or "0000001"
        items[-1] = "0"
        self.modal = InputModal(self.width(), self.height(), parent=self)
        self.modal.set_title("添加教师")
        self.modal.set_content(header, items)
        self.modal.input_at(0).setReadOnly(True)
        self.modal.input_at(-1).setReadOnly(True)
        self.modal.btn_complete.clicked.connect(self.slot_admin_modal_btn_teacher_manage_insert_click)
        self.modal.show()

    def slot_admin_btn_student_manage_click(self) -> None:
        """
        管理员
        点击学生管理按钮的信号槽
        """
        # 绑定添加按钮的信号槽
        try:
            self.admin.btn_insert.clicked.disconnect()
        except Exception:
            pass
        finally:
            self.admin.btn_insert.clicked.connect(self.slot_admin_btn_student_manage_insert_click)
        # 执行sql
        sql = "SELECT 学号,姓名,性别,年龄,专业名,密码,备注 FROM Student"
        thread = MsSQLThread(self.connection, sql)
        thread.data_signal.connect(self.slot_admin_student_manage_data)
        self.thread_pool.start(thread)

    def slot_admin_btn_course_manage_click(self) -> None:
        """
        管理员
        点击课程管理按钮的信号槽
        """
        # 绑定添加按钮的信号槽
        try:
            self.admin.btn_insert.clicked.disconnect()
        except Exception:
            pass
        finally:
            self.admin.btn_insert.clicked.connect(self.slot_admin_btn_course_manage_insert_click)
        # 执行sql
        sql = "SELECT 课程号,课程名,选课人数 FROM Course_stu"
        thread = MsSQLThread(self.connection, sql)
        thread.data_signal.connect(self.slot_admin_course_manage_data)
        self.thread_pool.start(thread)

    def slot_admin_btn_teacher_manage_click(self) -> None:
        """
        管理员
        点击教师管理按钮的信号槽
        """
        # 绑定添加按钮的信号槽
        try:
            self.admin.btn_insert.clicked.disconnect()
        except Exception:
            pass
        finally:
            self.admin.btn_insert.clicked.connect(self.slot_admin_btn_teacher_manage_insert_click)
        # 执行sql
        sql = "SELECT 工号,姓名,性别,密码,授课数目 FROM Teacher_info"
        thread = MsSQLThread(self.connection, sql)
        thread.data_signal.connect(self.slot_admin_teacher_manage_data)
        self.thread_pool.start(thread)

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
        self.admin.btn_student_manage.clicked.connect(self.slot_admin_btn_student_manage_click)
        self.admin.btn_course_manage.clicked.connect(self.slot_admin_btn_course_manage_click)
        self.admin.btn_teacher_manage.clicked.connect(self.slot_admin_btn_teacher_manage_click)
        self.admin.btn_logout.clicked.connect(self.slot_admin_btn_logout_click)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        重绘制窗口事件
        """
        self.login.resize(event.size())
        self.student.resize(event.size())
        self.teacher.resize(event.size())
        self.admin.resize(event.size())
        if hasattr(self, "modal") and self.modal:
            self.modal.resize(event.size())

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        窗口关闭事件
        """
        # 关闭数据库连接
        self.connection.close()
        return super().closeEvent(event)
