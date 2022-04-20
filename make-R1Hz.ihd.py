#! /usr/bin/env python3
#
# Residential 1Hz Dataset (R1Hz)
# =======================================
# STAGE 2: Load smart meter data to table
# FILE: make-R1Hz.ihd.py
# ---------------------------------------
# Copyright (C) 2017-2022 Stephen Makonin
#

import os, os.path, sys, mysql.connector
from datetime import datetime, timedelta

pwd = sys.argv[1]
input_filename = './raw-smartmeter/IHD_%s.csv'
start_dt = '2017-09-13'
end_dt = '2018-09-14' #'IHD_2018-09-13'+1 for proper loop end
day = timedelta(days=1)
sql = 'INSERT INTO R1Hz.smart_meter (unix_ts, marker, local_dt, local_tm, power, energy) VALUES (%s, %s, %s, %s, %s, %s);'

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


    if os.path.isfile(input_filename % (date)):
        raw_fp = open(input_filename % (date), 'r')
        raw_data = list(raw_fp)
        raw_fp.close()

        for line in raw_data:
            line = line.strip()
            line = line.split(',')

            ts = int(line[0])
            dt = datetime.fromtimestamp(ts)
            date = dt.strftime('%Y-%m-%d')
            time = dt.strftime('%H:%M:%S')

            power = int(float(line[1])*1000)
            energy = round(float(line[2]), 1)

            try:
                cur.execute(sql, (ts, '', date, time, power, energy,))
            except mysql.connector.errors.IntegrityError:
                cur.execute(sql, (ts, 'd', date, time, power, energy,))

            con.commit()
    date = str(dt + day)[:10]


# % ./make-R1Hz.ihd.py db123
# Processing raw data from 2017-09-13 ...
# Processing raw data from 2017-09-14 ...
# Traceback (most recent call last):
#   File "/Users/stephen/Library/Mobile Documents/com~apple~CloudDocs/Research/SourceCode/R1Hz.dataset/./make-R1Hz.ihd.py", line 50, in <module>
#     cur.execute(sql, (ts, '', date, time, power, energy,))
#   File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/site-packages/mysql/connector/cursor.py", line 572, in execute
#     self._handle_result(self._connection.cmd_query(stmt))
#   File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/site-packages/mysql/connector/connection.py", line 920, in cmd_query
#     result = self._handle_result(self._send_cmd(ServerCmd.QUERY, query))
#   File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/site-packages/mysql/connector/connection.py", line 730, in _handle_result
#     raise errors.get_exception(packet)
# mysql.connector.errors.IntegrityError: 1062 (23000): Duplicate entry '1505400482-' for key 'smart_meter.PRIMARY'


cur.close()
con.close()
