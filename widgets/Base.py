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
from PyQt5.Qt import (
    QColor,
    QPainter,
    QPaintEvent,
    QResizeEvent,
    QFocusEvent,
    QCursor,
    QFontMetrics,
    Qt,
    pyqtSignal,
    QObject,
    QRunnable,
    QThreadPool,
    QSize,
    QModelIndex,
    QSequentialAnimationGroup,
    QPropertyAnimation,
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
    QGraphicsOpacityEffect,
)


class Button(QPushButton):

    animation: QSequentialAnimationGroup
    last_text: str

    def __init__(self, *args, **kwargs) -> None:
        super(Button, self).__init__(*args, **kwargs)
        self.setContentsMargins(0, 0, 0, 0)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
        QWidget {
            border: 0;
            outline: none;
            color: #FFF;
            font-size: 18px;
            border-radius: 3px;
            background: rgba(64, 169, 255, 255);
        }
        QWidget:hover {
            background: rgba(64, 169, 255, 200);
        }
        """)

    def init_animation(self) -> None:
        """
        初始化动画
        """
        # 三个点的加载动画
        layout = QHBoxLayout()
        layout.addStretch(1)
        for i in range(3):
            dot = QLabel(parent=self)
            effect = QGraphicsOpacityEffect()
            effect.setOpacity(0.2)
            dot.setGraphicsEffect(effect)
            dot.setFixedSize(QSize(8, 8))
            dot.setStyleSheet("""
            QWidget {
                font-size: 18px;
                border-radius: 4px;
                background: rgba(255, 255, 255, 255);
            }
            """)
            layout.addWidget(dot, 0, Qt.AlignCenter)
            setattr(self, f"dot{i}", dot)
            setattr(self, f"effect{i}", effect)
        layout.addStretch(1)
        self.setLayout(layout)

        # 添加串行动画组
        self.animation = QSequentialAnimationGroup(parent=self)
        for i in range(3):
            effect = getattr(self, f"effect{i}")
            animation = QPropertyAnimation(effect, b"opacity")
            animation.setDuration(500)
            animation.setKeyValueAt(0, 0.2)
            animation.setKeyValueAt(0.5, 1)
            animation.setKeyValueAt(1, 0.2)
            self.animation.addAnimation(animation)
        self.animation.setLoopCount(-1)
        self.last_text = str()

    def set_loading(self, loading: bool) -> None:
        """
        设置加载动画
        """
        if not loading and not hasattr(self, "animation"):
            return
        if not hasattr(self, "animation"):
            self.init_animation()
        for i in range(3):
            dot = getattr(self, f"dot{i}")
            dot.show() if loading else dot.hide()
        last_text = self.text()
        self.setText(self.last_text)
        self.last_text = last_text
        self.animation.start() if loading else self.animation.stop()


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
        self.setStyleSheet("""
        QWidget {
            border: 1px solid #D9D9D9;
            border-radius: 5px;
            font-size: 18px;
            padding-left: 10px;
        }
        QWidget:focus {
            border: 1px solid rgba(64, 169, 255, 255);
        }
        QWidget:hover {
            border: 1px solid rgba(64, 169, 255, 255);
        }
        """)

    def setReadOnly(self, readonly: bool) -> None:
        super().setReadOnly(readonly)
        if readonly:
            self.setCursor(Qt.ForbiddenCursor)
            self.setStyleSheet("""
            QWidget {
                border: 1px solid #D9D9D9;
                border-radius: 5px;
                font-size: 18px;
                padding-left: 10px;
                background: #F5F5F5;
            }
            """)
        else:
            self.setCursor(Qt.CustomCursor)
            self.setStyleSheet("""
            QWidget {
                border: 1px solid #D9D9D9;
                border-radius: 5px;
                font-size: 18px;
                padding-left: 10px;
            }
            QWidget:focus {
                border: 1px solid rgba(64, 169, 255, 255);
            }
            QWidget:hover {
                border: 1px solid rgba(64, 169, 255, 255);
            }
            """)

    def focusInEvent(self, event: QFocusEvent) -> None:
        """
        获取焦点事件
        """
        if self.isReadOnly():
            return
        self.setGraphicsEffect(Shadow(0, 0, 10, QColor(64, 169, 255)))
        return super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        """
        失去焦点事件
        """
        if self.isReadOnly():
            return
        self.setGraphicsEffect(Shadow(0, 0, 0, Qt.transparent))
        return super().focusOutEvent(event)


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
            border: 1 solid #D8D8D8;
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
        for index, button in enumerate(self.button_list[::-1]):
            margin = self.button_block_size.height() // 6
            button_size = QSize(
                self.main_widget.width() // 8,
                self.button_block_size.height() - 2*margin
            )
            if button_size.height() >= 40:
                button_size = QSize(button_size.width(), 40)
            button.resize(button_size)
            button.move(
                self.width()//2 + self.main_widget.width()//2 - (index+1)*margin - (index+1)*button_size.width(),
                self.height()//2 + self.main_widget.height()//2 - \
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

    def set_widget_shadow(self, shadow: Shadow) -> None:
        """
        设置内容区域的阴影
        """
        self.widget.setGraphicsEffect(shadow)

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


class InputModal(Modal):

    label_list: List[QLabel]
    input_list: List[Input]
    btn_complete: Button

    def __init__(self, width: int, height: int, *args, **kwargs) -> None:
        super(InputModal, self).__init__(width, height, *args, **kwargs)
        self.label_list = list()
        self.input_list = list()
        self.btn_complete = Button()
        self.btn_complete.setText("完成")
        self.btn_complete.setGraphicsEffect(Shadow(3, 3, 6))
        self.btn_complete.setStyleSheet("""
        QWidget {
            font-size: 18px;
            border: 0;
            outline: none;
            border-radius: 3px;
            color: #FFF;
            background: rgba(64, 169, 255, 255);
        }
        QWidget:hover {
            background: rgba(64, 169, 255, 200);
        }
        """)
        self.add_button(self.btn_complete)

    def set_content(self, labels: List[str], inputs: List[str]) -> None:
        """
        设置以输入框为主的内容
        """
        layout = VLayout()
        for label_text, input_text in zip(labels, inputs):
            temp_layout = HLayout()
            temp_layout.addStretch(1)
            # 左边的label
            label = QLabel()
            label.setText(f"{label_text}:  ")
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            label.setStyleSheet("""
            QWidget {
                font-size: 18px;
            }
            """)
            temp_layout.addWidget(label)
            # 右边的输入框
            _input = Input()
            _input.setText(input_text)
            temp_layout.addWidget(_input)
            temp_layout.addStretch(1)
            # 添加布局
            layout.addLayout(temp_layout)
            # 添加到列表
            self.label_list.append(label)
            self.input_list.append(_input)
        self.resize_content()
        self.widget.setLayout(layout)

    def resize_content(self) -> None:
        """
        重新设置控件大小
        """
        for label, _input in zip(self.label_list, self.input_list):
            label.setFixedSize(self.widget.width() // 6, 40)
            _input.setFixedSize(self.widget.width()*3 // 5, 40)

    def label_at(self, index: int) -> QLabel:
        """
        根据下标获取Label
        """
        return self.label_list[index]

    def input_at(self, index: int) -> Input:
        """
        根据下标获取输入框控件
        """
        return self.input_list[index]

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        重绘大小事件
        """
        super().resizeEvent(event)
        self.resize_content()


class Sidebar(QWidget):

    background: QLabel
    layout: VLayout

    def __init__(self, width: int, height: int, *args, **kwargs) -> None:
        super(Sidebar, self).__init__(*args, **kwargs)
        self.resize(QSize(width, height))
        # 背景
        self.background = QLabel(self)
        self.background.setFixedSize(width, height)
        self.background.setStyleSheet("""
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

    def resize(self, size: QSize) -> None:
        """
        重绘大小
        """
        if size.width() >= 300:
            size = QSize(300, size.height())
        if hasattr(self, "background"):
            self.background.setFixedSize(size)
        super().resize(size)


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
                self.data_signal.emit(True)
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

