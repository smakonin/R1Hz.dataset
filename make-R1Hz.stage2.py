#! /usr/bin/env python3
#
# Residential 1Hz Dataset (R1Hz)
# =======================================
# STAGE 2: Add timestamp dummy rows
# FILE: make-R1Hz.stage2.py
# ---------------------------------------
# Copyright (C) 2017-2022 Stephen Makonin
#

import os, sys, threading, mysql.connector
from datetime import datetime

start_ts = 1505286000
end_ts = 1570690799
all_ts_meta = []
all_ts = []
params = (sys.argv[1],)

def insert_meta(pwd):
    con = mysql.connector.connect(host='localhost', user='smakonin', passwd=pwd, database='R1Hz')
    if not con.is_connected():
        print('ERROR: unable to connect to MySQL!')
        return

    cur = con.cursor()
    cur.executemany('INSERT IGNORE INTO R1Hz.meta (unix_ts, local_dt, local_tm, imputed) VALUES (%s, %s, %s, %s);', all_ts_meta)
    con.commit()
    cur.close()
    con.close()

def insert_current(pwd):
    con = mysql.connector.connect(host='localhost', user='smakonin', passwd=pwd, database='R1Hz')
    if not con.is_connected():
        print('ERROR: unable to connect to MySQL!')
        return

    cur = con.cursor()
    cur.executemany('INSERT IGNORE INTO R1Hz.current (unix_ts) VALUES (%s);', all_ts)
    con.commit()
    cur.close()
    con.close()

def insert_displacement_pf(pwd):
    con = mysql.connector.connect(host='localhost', user='smakonin', passwd=pwd, database='R1Hz')
    if not con.is_connected():
        print('ERROR: unable to connect to MySQL!')
        return
    
    cur = con.cursor()
    cur.executemany('INSERT IGNORE INTO R1Hz.displacement_pf (unix_ts) VALUES (%s);', all_ts)
    con.commit()
    cur.close()
    con.close()

def insert_apparent_pf(pwd):
    con = mysql.connector.connect(host='localhost', user='smakonin', passwd=pwd, database='R1Hz')
    if not con.is_connected():
        print('ERROR: unable to connect to MySQL!')
        return
    
    cur = con.cursor()
    cur.executemany('INSERT IGNORE INTO R1Hz.apparent_pf (unix_ts) VALUES (%s);', all_ts)
    con.commit()
    cur.close()
    con.close()

def insert_real_power(pwd):
    con = mysql.connector.connect(host='localhost', user='smakonin', passwd=pwd, database='R1Hz')
    if not con.is_connected():
        print('ERROR: unable to connect to MySQL!')
        return
    
    cur = con.cursor()
    cur.executemany('INSERT IGNORE INTO R1Hz.real_power (unix_ts) VALUES (%s);', all_ts)
    con.commit()
    cur.close()
    con.close()

def insert_reactive_power(pwd):
    con = mysql.connector.connect(host='localhost', user='smakonin', passwd=pwd, database='R1Hz')
    if not con.is_connected():
        print('ERROR: unable to connect to MySQL!')
        return
    
    cur = con.cursor()
    cur.executemany('INSERT IGNORE INTO R1Hz.reactive_power (unix_ts) VALUES (%s);', all_ts)
    con.commit()
    cur.close()
    con.close()

def insert_apparent_power(pwd):
    con = mysql.connector.connect(host='localhost', user='smakonin', passwd=pwd, database='R1Hz')
    if not con.is_connected():
        print('ERROR: unable to connect to MySQL!')
        return

    cur = con.cursor()
    cur.executemany('INSERT IGNORE INTO R1Hz.apparent_power (unix_ts) VALUES (%s);', all_ts)
    con.commit()
    cur.close()
    con.close()

def insert_real_energy(pwd):
    con = mysql.connector.connect(host='localhost', user='smakonin', passwd=pwd, database='R1Hz')
    if not con.is_connected():
        print('ERROR: unable to connect to MySQL!')
        return

    cur = con.cursor()
    cur.executemany('INSERT IGNORE INTO R1Hz.real_energy (unix_ts) VALUES (%s);', all_ts)
    con.commit()
    cur.close()
    con.close()

def insert_reactive_energy(pwd):
    con = mysql.connector.connect(host='localhost', user='smakonin', passwd=pwd, database='R1Hz')
    if not con.is_connected():
        print('ERROR: unable to connect to MySQL!')
        return
    
    cur = con.cursor()
    cur.executemany('INSERT IGNORE INTO R1Hz.reactive_energy (unix_ts) VALUES (%s);', all_ts)
    con.commit()
    cur.close()
    con.close()

def insert_apparent_energy(pwd):
    con = mysql.connector.connect(host='localhost', user='smakonin', passwd=pwd, database='R1Hz')
    if not con.is_connected():
        print('ERROR: unable to connect to MySQL!')
        return

    cur = con.cursor()
    cur.executemany('INSERT IGNORE INTO R1Hz.apparent_energy (unix_ts) VALUES (%s);', all_ts)
    con.commit()
    cur.close()
    con.close()


if __name__ == "__main__":
    print('Creating all ts list for meta ...')
    all_ts = [(ts,) for ts in range(start_ts, end_ts+1)]
    #for ts in range(start_ts, end_ts+1):
    #    dt = datetime.fromtimestamp(ts)
    #    date = dt.strftime('%Y-%m-%d')
    #    time = dt.strftime('%H:%M:%S')
    #    all_ts_meta.append((ts, date, time, '?'))

    print('Starting table insertion threads ...')
    #t0 = threading.Thread(target=insert_meta, args=params)
    #t1 = threading.Thread(target=insert_current, args=params)
    #t2 = threading.Thread(target=insert_displacement_pf, args=params)
    #t3 = threading.Thread(target=insert_apparent_pf, args=params)
    #t4 = threading.Thread(target=insert_real_power, args=params)
    #t5 = threading.Thread(target=insert_reactive_power, args=params)
    t6 = threading.Thread(target=insert_apparent_power, args=params)
    #t7 = threading.Thread(target=insert_real_energy, args=params)
    #t8 = threading.Thread(target=insert_reactive_energy, args=params)
    #t9 = threading.Thread(target=insert_apparent_energy, args=params)

    #t0.start()
    #t1.start()
    #t2.start()
    #t3.start()
    #t4.start()
    #t5.start()
    t6.start()
    #t7.start()
    #t8.start()
    #t9.start()

    #t0.join()
    #t1.join()
    #t2.join()
    #t3.join()
    #t4.join()
    #t5.join()
    t6.join()
    #t7.join()
    #t8.join()
    #t9.join()


