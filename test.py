# -*- coding: utf-8 -*- 
"""
...@version: python 3.7
...@author: Karbob
...@fileName: test.py
...@description: 
...@date: 2022-06-10
"""
import sys
import threading
import multiprocessing
import time
import tkinter

from reactivex import create, operators
from reactivex.observer.observer import Observer
from reactivex.scheduler import ThreadPoolScheduler, EventLoopScheduler
from reactivex.scheduler.mainloop import QtScheduler, TkinterScheduler
from reactivex.scheduler.scheduler import Scheduler

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5 import QtCore


class MainWindow(QWidget):

    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        self.pool_scheduler = ThreadPoolScheduler(multiprocessing.cpu_count())
        self.main_scheduler = QtScheduler(QtCore)
        source = create(self.test)
        self.disposable_list = []

        self.disposable_list.append(source.pipe(
            operators.observe_on(self.main_scheduler),
            # operators.subscribe_on(self.main_scheduler),
            # operators.observe_on(self.pool_scheduler),
        ).subscribe(
            on_next=lambda x: print("main", threading.current_thread().getName()),
        ))

    def test(self, observer: Observer, scheduler: ThreadPoolScheduler) -> None:
        print("thread start", threading.current_thread().getName())
        for i in range(10):
            observer.on_next(i)
            time.sleep(1)
        observer.on_completed()
        print("thread stop", threading.current_thread().getName())
        return observer.dispose()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
