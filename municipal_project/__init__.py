import pymysql

pymysql.install_as_MySQLdb()
import MySQLdb

# Monkeypatch version to satisfy Django
MySQLdb.version_info = (2, 2, 7, 'final', 0)
MySQLdb.__version__ = '2.2.7'
