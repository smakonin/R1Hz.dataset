#! /usr/bin/env python3
#
# Residential 1Hz Dataset (R1Hz)
# =======================================
# STAGE 2: Convert raw MODBUS into tables
# FILE: make-R1Hz.stage2.py
# ---------------------------------------
# Copyright (C) 2017-2022 Stephen Makonin
#

import os, sys, mysql.connector
from datetime import datetime, timedelta

pwd = sys.argv[1]
input_filename = './raw-modbus/SUB_%s.csv'
start_dt = '2018-06-09' #'2017-09-13'
end_dt = '2018-06-10' #'2019-10-10' #'2019-10-09'+1 for proper loop end
submeter_count = 21
meter_count = 8
day = timedelta(days=1)
ins_set_clause = 'unix_ts,meter1,meter2,meter3,meter4,meter5,meter6,meter7,meter8,meter9,meter10,meter11,meter12,meter13,meter14,meter15,meter16,meter17,meter18,meter19,meter20,meter21'

def int32(lsw, msw):
    return (msw << 16) + lsw

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
        voltage_l1 = round(raw_data[subs_i][37 + offset] * 0.1, 1)
        voltage_l2 = round(raw_data[subs_i][38 + offset] * 0.1, 1)
        freq = round(raw_data[subs_i][0 + offset] * 0.1, 1)
        current = [0] * submeter_count
        displacement_pf = [0] * submeter_count
        apparent_pf = [0] * submeter_count
        real_power = [0] * submeter_count
        reactive_power = [0] * submeter_count
        apparent_power = [0] * submeter_count
        real_energy = [0] * submeter_count
        reactive_energy = [0] * submeter_count
        apparent_energy = [0] * submeter_count

        for i in range(meter_count):
            line = raw_data[subs_i + i]

            if ord(line[1]) != ord('A') + i:
                print('\t ERROR: meter not equal at line', subs_i + i, ":", line)
                exit(1)

            submeter_id = i * 3
            offset2 = offset
            for j in [0, 1, 2]:
                submeter_id = i * 3 + j
                offset2 = offset + j
                offset3 = offset + 2 * j

                if submeter_id >= submeter_count:
                    break

                current[submeter_id] = round(line[34 + offset2] * 0.1, 1)
                displacement_pf[submeter_id] = round(line[31 + offset2] * 0.01, 2)
                apparent_pf[submeter_id] = round(line[28 + offset2] * 0.01, 2)
                real_power[submeter_id] = line[7 + offset2]
                reactive_power[submeter_id] = line[16 + offset2]
                apparent_power[submeter_id] = line[25 + offset2]
                real_energy[submeter_id] = int32(line[1 + offset3], line[2 + offset3])
                reactive_energy[submeter_id] = int32(line[10 + offset3], line[11 + offset3])
                apparent_energy[submeter_id] = int32(line[19 + offset3], line[20 + offset3])

        cur.execute('UPDATE R1Hz.meta SET imputed = %s, voltage_l1 = %s, voltage_l2 = %s, freq = %s WHERE unix_ts = %s;', ('N', voltage_l1, voltage_l2, freq, raw_ts,))
        cur.execute('INSERT IGNORE INTO R1Hz.current         (' + ins_set_clause + ') VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);', (raw_ts,) + tuple(current))
        cur.execute('INSERT IGNORE INTO R1Hz.displacement_pf (' + ins_set_clause + ') VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);', (raw_ts,) + tuple(displacement_pf))
        cur.execute('INSERT IGNORE INTO R1Hz.apparent_pf     (' + ins_set_clause + ') VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);', (raw_ts,) + tuple(apparent_pf))
        cur.execute('INSERT IGNORE INTO R1Hz.real_power      (' + ins_set_clause + ') VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);', (raw_ts,) + tuple(real_power))
        cur.execute('INSERT IGNORE INTO R1Hz.reactive_power  (' + ins_set_clause + ') VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);', (raw_ts,) + tuple(reactive_power))
        cur.execute('INSERT IGNORE INTO R1Hz.apparent_power  (' + ins_set_clause + ') VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);', (raw_ts,) + tuple(apparent_power))
        cur.execute('INSERT IGNORE INTO R1Hz.real_energy     (' + ins_set_clause + ') VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);', (raw_ts,) + tuple(real_energy))
        cur.execute('INSERT IGNORE INTO R1Hz.reactive_energy (' + ins_set_clause + ') VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);', (raw_ts,) + tuple(reactive_energy))
        cur.execute('INSERT IGNORE INTO R1Hz.apparent_energy (' + ins_set_clause + ') VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);', (raw_ts,) + tuple(apparent_energy))

        con.commit()
    date = str(dt + day)[:10]

cur.close()
con.close()
