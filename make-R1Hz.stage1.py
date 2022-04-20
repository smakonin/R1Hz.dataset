#! /usr/bin/env python3
#
# Residential 1Hz Dataset (R1Hz)
# =======================================
# STAGE 1: Add timestamp dummy rows
#  **** Need to run main-db.sql first!!!
# FILE: make-R1Hz.stage1.py
# ---------------------------------------
# Copyright (C) 2017-2022 Stephen Makonin
#

import os, sys, threading, mysql.connector
from datetime import datetime

start_ts = 1505286000
end_ts = 1570690799
all_ts = []
pwd = sys.argv[1]

if __name__ == "__main__":
    print('Creating all ts list for meta ...')
    for ts in range(start_ts, end_ts+1):
       dt = datetime.fromtimestamp(ts)
       date = dt.strftime('%Y-%m-%d')
       time = dt.strftime('%H:%M:%S')
       all_ts.append((ts, date, time))

    print('Connecting to RH1z database ...')
    con = mysql.connector.connect(host='localhost', user='root', passwd=pwd, database='R1Hz')
    if not con.is_connected():
        print('ERROR: unable to connect to MySQL!')
        return

    print('Starting meta table insertion ...')
    cur = con.cursor()
    cur.executemany('INSERT IGNORE INTO R1Hz.meta (unix_ts, local_dt, local_tm, imputed) VALUES (%s, %s, %s, \'-\');', all_ts)
    con.commit()
    cur.close()
    con.close()
