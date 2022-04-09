#! /usr/bin/env python3
#
# Residential 1Hz Dataset (R1Hz)
# =======================================
# STAGE 1: Create tables & appliance data
# FILE: make-R1Hz.stage1.py
# ---------------------------------------
# Copyright (C) 2017-2022 Stephen Makonin
#

import os, sys, mysql.connector
from datetime import datetime

con = mysql.connector.connect(host='localhost', user='smakonin', passwd=sys.argv[1])

if not con.is_connected():
    print('ERROR: unable to connect to MySQL!')
    exit(1)
cur = con.cursor()

cur.execute('CREATE DATABASE R1Hz /*!40100 DEFAULT CHARACTER SET ascii COLLATE ascii_bin */;')
con.commit()

cur.execute('USE R1Hz;')
cur.execute('CREATE TABLE appliances ( appliance_id char(4) PRIMARY KEY NOT NULL, name varchar(64), meter_l1 integer, meter_l2 integer, is_mains char(1), has_mixed_loads char(1), notes text );')
cur.execute('CREATE TABLE meta ( unix_ts integer PRIMARY KEY NOT NULL, local_dt char(10) NOT NULL, local_tm char(8) NOT NULL, imputed char(1) NOT NULL, voltage_l1 real, voltage_l2 real, freq real );')
cur.execute('CREATE TABLE current ( unix_ts integer PRIMARY KEY NOT NULL, meter1 real, meter2 real, meter3 real, meter4 real, meter5 real, meter6 real, meter7 real, meter8 real, meter9 real, meter10 real, meter11 real, meter12 real, meter13 real, meter14 real, meter15 real, meter16 real, meter17 real, meter18 real, meter19 real, meter20 real, meter21 real );')
cur.execute('CREATE TABLE displacement_pf ( unix_ts integer PRIMARY KEY NOT NULL, meter1 real, meter2 real, meter3 real, meter4 real, meter5 real, meter6 real, meter7 real, meter8 real, meter9 real, meter10 real, meter11 real, meter12 real, meter13 real, meter14 real, meter15 real, meter16 real, meter17 real, meter18 real, meter19 real, meter20 real, meter21 real );')
cur.execute('CREATE TABLE apparent_pf ( unix_ts integer PRIMARY KEY NOT NULL, meter1 real, meter2 real, meter3 real, meter4 real, meter5 real, meter6 real, meter7 real, meter8 real, meter9 real, meter10 real, meter11 real, meter12 real, meter13 real, meter14 real, meter15 real, meter16 real, meter17 real, meter18 real, meter19 real, meter20 real, meter21 real );')
cur.execute('CREATE TABLE real_power ( unix_ts integer PRIMARY KEY NOT NULL, meter1 integer, meter2 integer, meter3 integer, meter4 integer, meter5 integer, meter6 integer, meter7 integer, meter8 integer, meter9 integer, meter10 integer, meter11 integer, meter12 integer, meter13 integer, meter14 integer, meter15 integer, meter16 integer, meter17 integer, meter18 integer, meter19 integer, meter20 integer, meter21 integer );')
cur.execute('CREATE TABLE reactive_power ( unix_ts integer PRIMARY KEY NOT NULL, meter1 integer, meter2 integer, meter3 integer, meter4 integer, meter5 integer, meter6 integer, meter7 integer, meter8 integer, meter9 integer, meter10 integer, meter11 integer, meter12 integer, meter13 integer, meter14 integer, meter15 integer, meter16 integer, meter17 integer, meter18 integer, meter19 integer, meter20 integer, meter21 integer );')
cur.execute('CREATE TABLE apparent_power ( unix_ts integer PRIMARY KEY NOT NULL, meter1 integer, meter2 integer, meter3 integer, meter4 integer, meter5 integer, meter6 integer, meter7 integer, meter8 integer, meter9 integer, meter10 integer, meter11 integer, meter12 integer, meter13 integer, meter14 integer, meter15 integer, meter16 integer, meter17 integer, meter18 integer, meter19 integer, meter20 integer, meter21 integer );')
cur.execute('CREATE TABLE real_energy ( unix_ts integer PRIMARY KEY NOT NULL, meter1 integer, meter2 integer, meter3 integer, meter4 integer, meter5 integer, meter6 integer, meter7 integer, meter8 integer, meter9 integer, meter10 integer, meter11 integer, meter12 integer, meter13 integer, meter14 integer, meter15 integer, meter16 integer, meter17 integer, meter18 integer, meter19 integer, meter20 integer, meter21 integer );')
cur.execute('CREATE TABLE reactive_energy ( unix_ts integer PRIMARY KEY NOT NULL, meter1 integer, meter2 integer, meter3 integer, meter4 integer, meter5 integer, meter6 integer, meter7 integer, meter8 integer, meter9 integer, meter10 integer, meter11 integer, meter12 integer, meter13 integer, meter14 integer, meter15 integer, meter16 integer, meter17 integer, meter18 integer, meter19 integer, meter20 integer, meter21 integer );')
cur.execute('CREATE TABLE apparent_energy ( unix_ts integer PRIMARY KEY NOT NULL, meter1 integer, meter2 integer, meter3 integer, meter4 integer, meter5 integer, meter6 integer, meter7 integer, meter8 integer, meter9 integer, meter10 integer, meter11 integer, meter12 integer, meter13 integer, meter14 integer, meter15 integer, meter16 integer, meter17 integer, meter18 integer, meter19 integer, meter20 integer, meter21 integer );')
con.commit()

cur.execute("""
    INSERT INTO appliances (appliance_id, name, meter_l1, meter_l2, is_mains, has_mixed_loads, notes) VALUES
    ('MAIN', 'House Sub-Panel',          1,    2, 'Y', 'Y', ''),
    ('GEN1', 'Lights & Plugs',           3, NULL, 'N', 'Y', 'general label'),
    ('DRYR', 'Clothes Dryer',            4,    5, 'N', 'N', ''),
    ('BEDP', 'Bedroom Plugs',            6, NULL, 'N', 'Y', ''),
    ('VACU', 'Built-in Vacuum',          7, NULL, 'N', 'N', ''),
    ('BOIL', 'Boiler',                   8, NULL, 'N', 'N', 'for hot water and radiant heating'),
    ('GEN2', 'Lights & Plugs',           9, NULL, 'N', 'Y', ''),
    ('CWSH', 'Clothes Washer',          10, NULL, 'N', 'N', ''),
    ('FRDG', 'Kitchen Fridge',          11, NULL, 'N', 'N', ''),
    ('GEN3', 'Lights & Plugs',          12, NULL, 'N', 'Y', 'general label, incl. Internet modem and network equipment'),
    ('BEDA', 'Bedroom Plugs',           13, NULL, 'N', 'Y', 'AFCI Arc-Fault Plugs'),
    ('KIT1', 'Kitchen Counter Plugs',   14, NULL, 'N', 'Y', ''),
    ('KIT2', 'Kitchen Counter Plugs',   15, NULL, 'N', 'Y', ''),
    ('GEN4', 'Lights & Plugs',          16, NULL, 'N', 'Y', 'general label'),
    ('GEN5', 'Lights & Plugs',          17, NULL, 'N', 'Y', 'general label'),
    ('OUTP', 'Outside Plugs',           18, NULL, 'N', 'Y', ''),
    ('DWSH', 'Dishwasher',              19, NULL, 'N', 'N', ''),
    ('GEN6', 'Lights & Plugs',          20, NULL, 'N', 'Y', 'general label'),
    ('CHRG', 'Phone Changers',          21, NULL, 'N', 'N', 'garburator & microwave not installed');
    """)
con.commit()

cur.close()
con.close()

