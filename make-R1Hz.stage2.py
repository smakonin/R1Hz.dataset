#! /usr/bin/env python3
#
# Residential 1Hz Dataset (R1Hz)
# =======================================
# STAGE 2: Add timestamp dummy rows
# FILE: make-R1Hz.stage2.py
# ---------------------------------------
# Copyright (C) 2017-2022 Stephen Makonin
#

import os, sys, mysql.connector
from datetime import datetime

start_ts = 1505286000
end_ts = 1570690799

con = mysql.connector.connect(host='localhost', user='smakonin', passwd=sys.argv[1], database='R1Hz')

if not con.is_connected():
    print('ERROR: unable to connect to MySQL!')
    exit(1)
cur = con.cursor()

for ts in range(start_ts, end_ts+1):
    dt = datetime.fromtimestamp(ts)
    date = dt.strftime('%Y-%m-%d')
    time = dt.strftime('%H:%M:%S')

    cur.execute('INSERT INTO meta (unix_ts, local_date, local_time, imputed) VALUES (%s, %s, %s, %s);', (ts, date, time, '?',))
    cur.execute('INSERT INTO current (unix_ts) VALUES (%s);', (ts,))
    cur.execute('INSERT INTO displacement_pf (unix_ts) VALUES (%s);', (ts,))
    cur.execute('INSERT INTO apparent_pf (unix_ts) VALUES (%s);', (ts,))
    cur.execute('INSERT INTO real_power (unix_ts) VALUES (%s);', (ts,))
    cur.execute('INSERT INTO reactive_power (unix_ts) VALUES (%s);', (ts,))
    cur.execute('INSERT INTO apparent_power (unix_ts) VALUES (%s);', (ts,))
    cur.execute('INSERT INTO real_energy (unix_ts) VALUES (%s);', (ts,))
    cur.execute('INSERT INTO reactive_energy (unix_ts) VALUES (%s);', (ts,))
    cur.execute('INSERT INTO apparent_energy (unix_ts) VALUES (%s);', (ts,))
    con.commit()

cur.close()
con.close()

