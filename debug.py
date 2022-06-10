# -*- coding: utf-8 -*- 
"""
...@version: python 3.7
...@author: Karbob
...@fileName: debug.py
...@description: 
...@date: 2022-06-10
"""
import pymssql
from config import config

connection = pymssql.connect(config.DATABASE_CONNECTION)
