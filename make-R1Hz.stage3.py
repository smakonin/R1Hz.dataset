#! /usr/bin/env python3
#
# Residential 1Hz Dataset (R1Hz)
# =======================================
# STAGE 3: Convert raw MODBUS into tables
# FILE: make-R1Hz.stage3.py
# ---------------------------------------
# Copyright (C) 2017-2022 Stephen Makonin
#

import os, sys, mysql.connector
from datetime import datetime

input_filename = './raw-modbus/SUB_%s.csv'
start_dt = '2017-09-13'
end_dt = '2019-10-09'
submeter_count = 21
meter_count = 8

def int32(lsw, msw):
    return msw * 0x10000 + lsw

con = mysql.connector.connect(host='localhost', user='smakonin', passwd=sys.argv[1], database='R1Hz')

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
    raw_data = []
    for l in raw_lines:
        l = l.strip()
        l = l.split(',')
        for i in range(len(l)):
            if i != 1:
                l[i] = int(l[i])
        raw_data.append(l)

    offset = 2
    for subs_i in range(0, len(raw_data), meter_count):
        raw_ts = raw_data[subs_i][0]
        cur.execute('UPDATE meta SET imputed = %s, voltage_l1 = %s, voltage_l2 = %s, freq = %s WHERE unix_ts = %s;', ('N', round(raw_data[subs_i][37 + offset] * 0.1, 1), round(raw_data[subs_i][38 + offset] * 0.1, 1), round(raw_data[subs_i][0 + offset] * 0.1, 1), raw_ts,))

        for i in range(meter_count):
            line = raw_data[subs_i + i]

            if ord(line[1]) != ord('A') + i:
                print('\t ERROR: meter not equal at line', subs_i + i, ":", line)
                exit(1)

            submeter_id = i * 3 + 1
            offset2 = offset
            for j in [0, 1, 2]:
                submeter_id = i * 3 + j + 1
                offset2 = offset + j

                if submeter_id > submeter_count:
                    break

                cur.execute('UPDATE current SET meter'+str(submeter_id)+' = %s WHERE unix_ts = %s;', (round(line[34 + offset] * 0.1, 1), raw_ts,))
                cur.execute('UPDATE displacement_pf SET meter'+str(submeter_id)+' = %s WHERE unix_ts = %s;', round(line[31 + offset] * 0.01, 2), raw_ts,))
                cur.execute('UPDATE apparent_pf SET meter'+str(submeter_id)+' = %s WHERE unix_ts = %s;', round(line[28 + offset] * 0.01, 2), raw_ts,))
                cur.execute('UPDATE real_power SET meter'+str(submeter_id)+' = %s WHERE unix_ts = %s;', line[7 + offset], raw_ts,))
                cur.execute('UPDATE reactive_power SET meter'+str(submeter_id)+' = %s WHERE unix_ts = %s;', line[16 + offset], raw_ts,))
                cur.execute('UPDATE apparent_power SET meter'+str(submeter_id)+' = %s WHERE unix_ts = %s;', line[25 + offset], raw_ts,))
                cur.execute('UPDATE real_energy SET meter'+str(submeter_id)+' = %s WHERE unix_ts = %s;', int32(line[1 + offset], line[2 + offset]), raw_ts,))
                cur.execute('UPDATE reactive_energy SET meter'+str(submeter_id)+' = %s WHERE unix_ts = %s;', int32(line[10 + offset], line[11 + offset]), raw_ts,))
                cur.execute('UPDATE apparent_energy SET meter'+str(submeter_id)+' = %s WHERE unix_ts = %s;', int32(line[19 + offset], line[20 + offset]), raw_ts,))
        con.commit()
    date = str(dt + timedelta(days=1))[:10]

cur.close()
con.close()

