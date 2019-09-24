#!/usr/bin/python3
import MySQLdb
db = MySQLdb.connect(host="127.0.0.1",          # your host, usually localhost
                     user="",                   # your username
                     passwd="",                 # your password
                     db="oasis")                # name of the data base