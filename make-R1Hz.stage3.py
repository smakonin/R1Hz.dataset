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
from datetime import datetime, timedelta

input_filename = './raw-modbus/SUB_%s.csv'
start_dt = '2017-09-22' #13'    ####### NEED TO RERUN 2017-09-21
end_dt = '2019-10-10'#'2019-10-09'
submeter_count = 21
meter_count = 8
day = timedelta(days=1)
set_clause = 'meter1=%s,meter2=%s,meter3=%s,meter4=%s,meter5=%s,meter6=%s,meter7=%s,meter8=%s,meter9=%s,meter10=%s,meter11=%s,meter12=%s,meter13=%s,meter14=%s,meter15=%s,meter16=%s,meter17=%s,meter18=%s,meter19=%s,meter20=%s,meter21=%s'

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

                if submeter_id >= submeter_count:
                    break

                current[submeter_id] = round(line[34 + offset] * 0.1, 1)
                displacement_pf[submeter_id] = round(line[31 + offset] * 0.01, 2)
                apparent_pf[submeter_id] = round(line[28 + offset] * 0.01, 2)
                real_power[submeter_id] = line[7 + offset]
                reactive_power[submeter_id] = line[16 + offset]
                apparent_power[submeter_id] = line[25 + offset]
                real_energy[submeter_id] = int32(line[1 + offset], line[2 + offset])
                reactive_energy[submeter_id] = int32(line[10 + offset], line[11 + offset])
                apparent_energy[submeter_id] = int32(line[19 + offset], line[20 + offset])
        
        cur.execute('UPDATE R1Hz.meta SET imputed = %s, voltage_l1 = %s, voltage_l2 = %s, freq = %s WHERE unix_ts = %s;', ('N', voltage_l1, voltage_l2, freq, raw_ts,))
        cur.execute('UPDATE R1Hz.current SET ' + set_clause + ' WHERE unix_ts = %s;', tuple(current) + (raw_ts,))
        cur.execute('UPDATE R1Hz.displacement_pf SET ' + set_clause + ' WHERE unix_ts = %s;', tuple(displacement_pf) + (raw_ts,))
        cur.execute('UPDATE R1Hz.apparent_pf SET ' + set_clause + ' WHERE unix_ts = %s;', tuple(apparent_pf) + (raw_ts,))
        cur.execute('UPDATE R1Hz.real_power SET ' + set_clause + ' WHERE unix_ts = %s;', tuple(real_power) + (raw_ts,))
        cur.execute('UPDATE R1Hz.reactive_power SET ' + set_clause + ' WHERE unix_ts = %s;', tuple(reactive_power) + (raw_ts,))
        cur.execute('UPDATE R1Hz.apparent_power SET ' + set_clause + ' WHERE unix_ts = %s;', tuple(apparent_power) + (raw_ts,))
        cur.execute('UPDATE R1Hz.real_energy SET ' + set_clause + ' WHERE unix_ts = %s;', tuple(real_energy) + (raw_ts,))
        cur.execute('UPDATE R1Hz.reactive_energy SET ' + set_clause + ' WHERE unix_ts = %s;', tuple(reactive_energy) + (raw_ts,))
        cur.execute('UPDATE R1Hz.apparent_energy SET ' + set_clause + ' WHERE unix_ts = %s;', tuple(apparent_energy) + (raw_ts,))
        con.commit()
    date = str(dt + day)[:10]

cur.close()
con.close()

