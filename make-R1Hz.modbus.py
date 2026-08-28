#! /usr/bin/env python3
#
# Residential 1Hz Dataset (R1Hz)
# =======================================
# Load MODBUS data on R1Hz database
# make-R1Hz.modbus.py
# ---------------------------------------
# Copyright (C) 2017-2022 Stephen Makonin
#

import os, sys, mysql.connector
from datetime import datetime, timedelta

pwd = sys.argv[1]
input_filename = './raw_modbus/SUB_%s.csv'
start_dt = '2017-09-13'
end_dt = '2019-10-10' #'2019-10-09'+1 for proper loop end
day = timedelta(days=1)
sql = "INSERT INTO raw_modbus (unix_ts, meter, reg_4021, reg_4022, reg_4023, reg_4024, reg_4025, reg_4026, reg_4027, reg_4028, reg_4029, reg_4030, reg_4031, reg_4032, reg_4033, reg_4034, reg_4035, reg_4036, reg_4037, reg_4038, reg_4039, reg_4040, reg_4041, reg_4042, reg_4043, reg_4044, reg_4045, reg_4046, reg_4047, reg_4048, reg_4049, reg_4050, reg_4051, reg_4052, reg_4053, reg_4054, reg_4055, reg_4056, reg_4057, reg_4058, reg_4059, reg_4060, reg_4061, reg_4062, reg_4063) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

con = mysql.connector.connect(host='localhost', user='root', passwd=pwd, database='R1Hz')

if not con.is_connected():
    print('ERROR: unable to connect to MySQL!')
    exit(1)
cur = con.cursor()


date = start_dt
while date != end_dt:
    print('Processing raw data from', date, '...')
    dt = datetime.strptime(date, '%Y-%m-%d')
    ts = int(dt.timestamp())

    raw_fp = open(input_filename % (date), 'r')
    raw_lines = list(raw_fp)
    raw_fp.close()
    for l in raw_lines:
        data = l.strip()
        cur.execute(sql, tuple(data.split(',')))
        con.commit()
    date = str(dt + day)[:10]

cur.close()
con.close()
