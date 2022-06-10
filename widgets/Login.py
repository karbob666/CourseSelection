# -*- coding: utf-8 -*- 
"""
...@version: python 3.7
...@author: Karbob
...@fileName: Login.py
...@description: 
...@date: 2022-06-08
"""

from config import config
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPaintEvent, QPainter, QColor, QPixmap
from widgets.Base import Input, Button, RadioButton, Shadow, HLayout, VLayout


class Login(QWidget):

    input_user_name: Input
    input_password: Input
    label_background: QLabel
    label_title: QLabel
    label_error: QLabel
    btn_login: Button
    rb_student: RadioButton
    rb_teacher: RadioButton
    rb_admin: RadioButton

    FORM_WIDTH = 800
    FORM_HEIGHT = 600

    def __init__(self, parent=None) -> None:
        super(Login, self).__init__(parent)
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
        初始化所有控件
        """

        input_stylesheet = """
        QWidget {
            border: 1px solid #b3b3b3;
            border-radius: 5px;
            font-size: 18px;
            padding-left: 10px;
        }
        QWidget:focus {
            border: 1px solid rgba(128, 183, 249, 255);
        }
        """
        rb_stylesheet = """
        QWidget {
            font-size: 18px;
            border: 0;
            outline: none;
        }
        """

        # 标题
        self.label_title = QLabel()
        self.label_title.adjustSize()
        self.label_title.setText("教学选课管理系统")
        self.label_title.setGraphicsEffect(Shadow(3, 5, 12))
        self.label_title.setStyleSheet("""
        QWidget {
            font-size: 42px;
            font-weight: bold;
        }
        """)

        # 用户名输入框
        self.input_user_name = Input()
        self.input_user_name.setPlaceholderText("请输入账号")
        self.input_user_name.setFixedSize(300, 40)
        self.input_user_name.setStyleSheet(input_stylesheet)

        # 密码输入框
        self.input_password = Input()
        self.input_password.setPlaceholderText("请输入密码")
        self.input_password.setFixedSize(300, 40)
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setStyleSheet(input_stylesheet)

        # 错误提示
        self.label_error = QLabel()

        # 单选按钮
        self.rb_student = RadioButton()
        self.rb_student.setText("学生")
        self.rb_student.setStyleSheet(rb_stylesheet)
        self.rb_student.setChecked(True)

        self.rb_teacher = RadioButton()
        self.rb_teacher.setText("教师")
        self.rb_teacher.setStyleSheet(rb_stylesheet)

        self.rb_admin = RadioButton()
        self.rb_admin.setText("管理员")
        self.rb_admin.setStyleSheet(rb_stylesheet)

        # 登录按钮
        self.btn_login = Button()
        self.btn_login.setText("登录")
        self.btn_login.setFixedSize(120, 40)
        self.btn_login.setGraphicsEffect(Shadow(0, 0, 20))
        self.btn_login.setStyleSheet("""
        QWidget {
            border: 0;
            outline: none;
            border-radius: 5px;
            font-size: 24px;
            color: rgba(255, 255, 255, 255);
            background: rgba(128, 183, 249, 255);
        }
        QWidget:hover {
            color: rgba(255, 255, 255, 200);
            background: rgba(128, 183, 249, 200);
        }
        """)

    def init_layout(self) -> None:
        """
        初始化布局
        """
        layout = VLayout()
        layout.setGeometry(QRect(
            self.width()//2 - self.FORM_WIDTH//2,
            self.height()//2 - self.FORM_HEIGHT//2,
            self.FORM_WIDTH,
            self.FORM_HEIGHT
        ))
        layout.setAlignment(Qt.AlignHCenter)

        layout.addWidget(self.label_title, 4, Qt.AlignCenter)
        layout.addWidget(self.input_user_name, 1, Qt.AlignCenter)
        layout.addWidget(self.input_password, 1, Qt.AlignCenter)
        temp_layout = HLayout()
        temp_layout.addWidget(self.rb_student, 0, Qt.AlignCenter)
        temp_layout.addWidget(self.rb_teacher, 0, Qt.AlignCenter)
        temp_layout.addWidget(self.rb_admin, 0, Qt.AlignCenter)
        layout.addLayout(temp_layout, 1)
        layout.addWidget(self.btn_login, 2, Qt.AlignCenter)
        layout.addStretch(1)
        self.setLayout(layout)

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        重写paintEvent事件, 绘制圆角背景和阴影
        """
        painter = QPainter()
        painter.begin(self)
        # 抗锯齿
        painter.setRenderHint(QPainter.Antialiasing)
        # 绘制背景
        background = QPixmap("./assets/bg_login.jpg")
        background = background.scaled(self.width(), self.height())
        painter.drawPixmap(0, 0, background)
        # 绘制登录表单
        painter.setBrush(QColor(255, 255, 255, 200))
        painter.setPen(Qt.transparent)
        painter.drawRoundedRect(
            self.width()//2 - self.FORM_WIDTH//2, self.height()//2 - self.FORM_HEIGHT//2,
            self.FORM_WIDTH, self.FORM_HEIGHT,
            10, 10,
        )
        painter.end()
