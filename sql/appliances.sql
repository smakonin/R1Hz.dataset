CREATE TABLE appliances (
    appliance_id CHAR(4) NOT NULL,
    name VARCHAR(64),
    meter_l1 INT,
    meter_l2 INT,
    is_mains CHAR(1),
    has_mixed_loads CHAR(1),
    notes TEXT,
    PRIMARY KEY (appliance_id)
) ENGINE=InnoDB DEFAULT CHARSET=ascii;

REPLACE INTO R1Hz.appliances (appliance_id, name, meter_l1, meter_l2, is_mains, has_mixed_loads, notes) VALUES
    ('MAIN', 'House Sub-Panel',             1,    2, 'Y', 'Y', 'garage has utility power, garage metering not included due to metering limitations'),
    ('GEN1', 'Lights & Plugs',           NULL,    3, 'N', 'Y', 'general label'),
    ('DRYR', 'Clothes Dryer',               4,    5, 'N', 'N', ''),
    ('BEDP', 'Bedroom Plugs',               6, NULL, 'N', 'Y', ''),
    ('VACU', 'Built-in Vacuum',          NULL,    7, 'N', 'N', ''),
    ('BOIL', 'Boiler',                   NULL,    8, 'N', 'N', 'for hot water and radiant heating'),
    ('GEN2', 'Lights & Plugs',              9, NULL, 'N', 'Y', ''),
    ('CWSH', 'Clothes Washer',           NULL,   10, 'N', 'N', ''),
    ('FRDG', 'Kitchen Fridge',           NULL,   11, 'N', 'N', ''),
    ('GEN3', 'Lights & Plugs',             12, NULL, 'N', 'Y', 'general label, incl. Internet modem and network equipment'),
    ('BEDA', 'Bedroom Plugs',            NULL,   13, 'N', 'Y', 'AFCI Arc-Fault Plugs'),
    ('KIT1', 'Kitchen Counter Plugs',      14, NULL, 'N', 'Y', ''),
    ('KIT2', 'Kitchen Counter Plugs',      15, NULL, 'N', 'Y', ''),
    ('GEN4', 'Lights & Plugs',           NULL,   16, 'N', 'Y', 'general label'),
    ('GEN5', 'Lights & Plugs',             17, NULL, 'N', 'Y', 'general label'),
    ('OUTP', 'Outside Plugs',            NULL,   18, 'N', 'Y', ''),
    ('DWSH', 'Dishwasher',               NULL,   19, 'N', 'N', ''),
    ('GEN6', 'Lights & Plugs',             20, NULL, 'N', 'Y', 'general label'),
    ('CHRG', 'Phone Chargers',           NULL,   21, 'N', 'N', 'garburator & microwave not installed');

SELECT * FROM appliances;


CREATE TABLE appliance_real (
    unix_ts int NOT NULL,
    marker char(1) NOT NULL,
    local_dt char(10) NOT NULL,
    local_tm char(8) NOT NULL,
	ihd int DEFAULT NULL,
    main int DEFAULT NULL,
    beda int DEFAULT NULL,
    bedp int DEFAULT NULL,
    boil int DEFAULT NULL,
    chrg int DEFAULT NULL,
    cwsh int DEFAULT NULL,
    dryr int DEFAULT NULL,
    dwsh int DEFAULT NULL,
    frdg int DEFAULT NULL,
    gen1 int DEFAULT NULL,
    gen2 int DEFAULT NULL,
    gen3 int DEFAULT NULL,
    gen4 int DEFAULT NULL,
    gen5 int DEFAULT NULL,
    gen6 int DEFAULT NULL,
    kit1 int DEFAULT NULL,
    kit2 int DEFAULT NULL,
    outp int DEFAULT NULL,
    vacu int DEFAULT NULL,
    PRIMARY KEY (unix_ts),
    KEY LOCAL (local_dt,local_tm)
) ENGINE=InnoDB DEFAULT CHARSET=ascii;

CREATE TABLE appliance_reactive (
    unix_ts int NOT NULL,
    marker char(1) NOT NULL,
    local_dt char(10) NOT NULL,
    local_tm char(8) NOT NULL,
    main int DEFAULT NULL,
    beda int DEFAULT NULL,
    bedp int DEFAULT NULL,
    boil int DEFAULT NULL,
    chrg int DEFAULT NULL,
    cwsh int DEFAULT NULL,
    dryr int DEFAULT NULL,
    dwsh int DEFAULT NULL,
    frdg int DEFAULT NULL,
    gen1 int DEFAULT NULL,
    gen2 int DEFAULT NULL,
    gen3 int DEFAULT NULL,
    gen4 int DEFAULT NULL,
    gen5 int DEFAULT NULL,
    gen6 int DEFAULT NULL,
    kit1 int DEFAULT NULL,
    kit2 int DEFAULT NULL,
    outp int DEFAULT NULL,
    vacu int DEFAULT NULL,
    PRIMARY KEY (unix_ts),
    KEY LOCAL (local_dt,local_tm)
) ENGINE=InnoDB DEFAULT CHARSET=ascii;

CREATE TABLE appliance_current (
    unix_ts int NOT NULL,
    marker char(1) NOT NULL,
    local_dt char(10) NOT NULL,
    local_tm char(8) NOT NULL,
    main DECIMAL(5,1) DEFAULT NULL,
    beda DECIMAL(5,1) DEFAULT NULL,
    bedp DECIMAL(5,1) DEFAULT NULL,
    boil DECIMAL(5,1) DEFAULT NULL,
    chrg DECIMAL(5,1) DEFAULT NULL,
    cwsh DECIMAL(5,1) DEFAULT NULL,
    dryr DECIMAL(5,1) DEFAULT NULL,
    dwsh DECIMAL(5,1) DEFAULT NULL,
    frdg DECIMAL(5,1) DEFAULT NULL,
    gen1 DECIMAL(5,1) DEFAULT NULL,
    gen2 DECIMAL(5,1) DEFAULT NULL,
    gen3 DECIMAL(5,1) DEFAULT NULL,
    gen4 DECIMAL(5,1) DEFAULT NULL,
    gen5 DECIMAL(5,1) DEFAULT NULL,
    gen6 DECIMAL(5,1) DEFAULT NULL,
    kit1 DECIMAL(5,1) DEFAULT NULL,
    kit2 DECIMAL(5,1) DEFAULT NULL,
    outp DECIMAL(5,1) DEFAULT NULL,
    vacu DECIMAL(5,1) DEFAULT NULL,
    PRIMARY KEY (unix_ts),
    KEY LOCAL (local_dt,local_tm)
) ENGINE=InnoDB DEFAULT CHARSET=ascii;

INSERT INTO appliance_real (unix_ts,local_dt,local_tm,marker,main,beda,bedp,boil,chrg,cwsh,dryr,dwsh,frdg,gen1,gen2,gen3,gen4,gen5,gen6,kit1,kit2,outp,vacu)
    SELECT unix_ts, DATE(FROM_UNIXTIME(unix_ts)), TIME(FROM_UNIXTIME(unix_ts)), '', meter1 + meter2, meter13, meter6, meter8, meter21, meter10, meter4 + meter5, meter19, meter11, meter3, meter9, meter12, meter16, meter17, meter20, meter14, meter15, meter18, meter7
    FROM real_power;

-- ALTER TABLE appliance_real ADD COLUMN ihd INT NULL AFTER local_tm;
UPDATE appliance_real, smart_meter SET ihd = power WHERE smart_meter.marker = '' AND appliance_real.unix_ts = smart_meter.unix_ts;

INSERT INTO appliance_reactive (unix_ts,local_dt,local_tm,marker, main,beda,bedp,boil,chrg,cwsh,dryr,dwsh,frdg,gen1,gen2,gen3,gen4,gen5,gen6,kit1,kit2,outp,vacu)
    SELECT unix_ts, DATE(FROM_UNIXTIME(unix_ts)), TIME(FROM_UNIXTIME(unix_ts)),'', meter1 + meter2, meter13, meter6, meter8, meter21, meter10, meter4 + meter5, meter19, meter11, meter3, meter9, meter12, meter16, meter17, meter20, meter14, meter15, meter18, meter7
    FROM reactive_power;

INSERT INTO appliance_current (unix_ts,local_dt,local_tm,marker,main,beda,bedp,boil,chrg,cwsh,dryr,dwsh,frdg,gen1,gen2,gen3,gen4,gen5,gen6,kit1,kit2,outp,vacu)
    SELECT unix_ts, DATE(FROM_UNIXTIME(unix_ts)), TIME(FROM_UNIXTIME(unix_ts)), '', meter1 + meter2, meter13, meter6, meter8, meter21, meter10, meter4 + meter5, meter19, meter11, meter3, meter9, meter12, meter16, meter17, meter20, meter14, meter15, meter18, meter7
    FROM current;

UPDATE appliance_real SET marker= '+' WHERE unix_ts IN (SELECT unix_ts FROM meta WHERE imputed = 'Y');
UPDATE appliance_reactive SET marker= '+' WHERE unix_ts IN (SELECT unix_ts FROM meta WHERE imputed = 'Y');
UPDATE appliance_current SET marker= '+' WHERE unix_ts IN (SELECT unix_ts FROM meta WHERE imputed = 'Y');


CREATE TABLE appliance_energy (
    unix_ts int NOT NULL,
    marker char(1) NOT NULL,
    local_dt char(10) NOT NULL,
    local_tm char(8) NOT NULL,
    main DECIMAL(6,3) DEFAULT NULL,
    beda DECIMAL(6,3) DEFAULT NULL,
    bedp DECIMAL(6,3) DEFAULT NULL,
    boil DECIMAL(6,3) DEFAULT NULL,
    chrg DECIMAL(6,3) DEFAULT NULL,
    cwsh DECIMAL(6,3) DEFAULT NULL,
    dryr DECIMAL(6,3) DEFAULT NULL,
    dwsh DECIMAL(6,3) DEFAULT NULL,
    frdg DECIMAL(6,3) DEFAULT NULL,
    gen1 DECIMAL(6,3) DEFAULT NULL,
    gen2 DECIMAL(6,3) DEFAULT NULL,
    gen3 DECIMAL(6,3) DEFAULT NULL,
    gen4 DECIMAL(6,3) DEFAULT NULL,
    gen5 DECIMAL(6,3) DEFAULT NULL,
    gen6 DECIMAL(6,3) DEFAULT NULL,
    kit1 DECIMAL(6,3) DEFAULT NULL,
    kit2 DECIMAL(6,3) DEFAULT NULL,
    outp DECIMAL(6,3) DEFAULT NULL,
    vacu DECIMAL(6,3) DEFAULT NULL,
    PRIMARY KEY (unix_ts,marker),
    KEY LOCAL (local_dt,local_tm,marker)
) ENGINE=InnoDB DEFAULT CHARSET=ascii;

INSERT INTO appliance_energy (unix_ts,marker,local_dt,local_tm,main,beda,bedp,boil,chrg,cwsh,dryr,dwsh,frdg,gen1,gen2,gen3,gen4,gen5,gen6,kit1,kit2,outp,vacu)
SELECT unix_ts, 'm', DATE(FROM_UNIXTIME(unix_ts)), TIME(FROM_UNIXTIME(unix_ts)), 
	(meter1 - LAG(meter1) OVER ()) + (meter2 - LAG(meter2) OVER ()),
	meter13 - LAG(meter13) OVER (), 
	meter6 - LAG(meter6) OVER (), 
	meter8 - LAG(meter8) OVER (), 
	meter21 - LAG(meter21) OVER (), 
	meter10 - LAG(meter10) OVER (), 
	(meter4 - LAG(meter4) OVER ()) + (meter5 - LAG(meter5) OVER ()), 
	meter19 - LAG(meter19) OVER (), 
	meter11 - LAG(meter11) OVER (), 
	meter3 - LAG(meter3) OVER (), 
	meter9 - LAG(meter9) OVER (), 
	meter12 - LAG(meter12) OVER (), 
	meter16 - LAG(meter16) OVER (), 
	meter17 - LAG(meter17) OVER (), 
	meter20 - LAG(meter20) OVER (), 
	meter14 - LAG(meter14) OVER (), 
	meter15 - LAG(meter15) OVER (), 
	meter18 - LAG(meter18) OVER (), 
	meter7 - LAG(meter7) OVER ()
FROM (SELECT * FROM real_energy WHERE DAY(FROM_UNIXTIME(unix_ts)) = 1 AND TIME(FROM_UNIXTIME(unix_ts)) = '00:00:00') AS monthly;

SELECT *  FROM appliance_energy WHERE marker = 'm'; 
-- DELETE FROM appliance_energy WHERE marker = 'm' AND DATE(FROM_UNIXTIME(unix_ts)) = '2019-10-01';  -- remove because only a partial month

INSERT INTO appliance_energy (unix_ts,marker,local_dt,local_tm,main,beda,bedp,boil,chrg,cwsh,dryr,dwsh,frdg,gen1,gen2,gen3,gen4,gen5,gen6,kit1,kit2,outp,vacu)
SELECT unix_ts, 'd', DATE(FROM_UNIXTIME(unix_ts)), TIME(FROM_UNIXTIME(unix_ts)), 
	(meter1 - LAG(meter1) OVER ()) + (meter2 - LAG(meter2) OVER ()),
	meter13 - LAG(meter13) OVER (), 
	meter6 - LAG(meter6) OVER (), 
	meter8 - LAG(meter8) OVER (), 
	meter21 - LAG(meter21) OVER (), 
	meter10 - LAG(meter10) OVER (), 
	(meter4 - LAG(meter4) OVER ()) + (meter5 - LAG(meter5) OVER ()), 
	meter19 - LAG(meter19) OVER (), 
	meter11 - LAG(meter11) OVER (), 
	meter3 - LAG(meter3) OVER (), 
	meter9 - LAG(meter9) OVER (), 
	meter12 - LAG(meter12) OVER (), 
	meter16 - LAG(meter16) OVER (), 
	meter17 - LAG(meter17) OVER (), 
	meter20 - LAG(meter20) OVER (), 
	meter14 - LAG(meter14) OVER (), 
	meter15 - LAG(meter15) OVER (), 
	meter18 - LAG(meter18) OVER (), 
	meter7 - LAG(meter7) OVER ()
FROM (SELECT * FROM real_energy WHERE TIME(FROM_UNIXTIME(unix_ts)) = '00:00:00') AS daily;

INSERT INTO appliance_energy (unix_ts,marker,local_dt,local_tm,main,beda,bedp,boil,chrg,cwsh,dryr,dwsh,frdg,gen1,gen2,gen3,gen4,gen5,gen6,kit1,kit2,outp,vacu)
SELECT unix_ts, 'h', DATE(FROM_UNIXTIME(unix_ts)), TIME(FROM_UNIXTIME(unix_ts)), 
	(meter1 - LAG(meter1) OVER ()) + (meter2 - LAG(meter2) OVER ()) / 1000.0,
	meter13 - LAG(meter13) OVER () / 1000.0, 
	meter6 - LAG(meter6) OVER () / 1000.0, 
	meter8 - LAG(meter8) OVER () / 1000.0, 
	meter21 - LAG(meter21) OVER () / 1000.0, 
	meter10 - LAG(meter10) OVER () / 1000.0, 
	(meter4 - LAG(meter4) OVER ()) + (meter5 - LAG(meter5) OVER ()) / 1000.0, 
	meter19 - LAG(meter19) OVER () / 1000.0, 
	meter11 - LAG(meter11) OVER () / 1000.0, 
	meter3 - LAG(meter3) OVER () / 1000.0, 
	meter9 - LAG(meter9) OVER () / 1000.0, 
	meter12 - LAG(meter12) OVER () / 1000.0, 
	meter16 - LAG(meter16) OVER () / 1000.0, 
	meter17 - LAG(meter17) OVER () / 1000.0, 
	meter20 - LAG(meter20) OVER () / 1000.0, 
	meter14 - LAG(meter14) OVER () / 1000.0, 
	meter15 - LAG(meter15) OVER () / 1000.0, 
	meter18 - LAG(meter18) OVER () / 1000.0, 
	meter7 - LAG(meter7) OVER () / 1000.0
FROM (SELECT * FROM real_energy WHERE MINUTE(FROM_UNIXTIME(unix_ts)) = 0 AND SECOND(FROM_UNIXTIME(unix_ts)) = 0) AS hourly;


-- SELECT
-- 	unix_ts, date, 'm' as marker,
--     meter1 as curr,
--     LAG(meter1) OVER () AS prev,
--     meter1 - LAG(meter1) OVER () AS cunsumption
-- from (select unix_ts, date(FROM_UNIXTIME(unix_ts)) as date, meter1 from ttt where DAY(FROM_UNIXTIME(unix_ts)) = 1 and TIME(FROM_UNIXTIME(unix_ts)) = '00:00:00') as monthly;

-- SELECT
-- 	unix_ts, dt, 'd' as marker,
--     meter1 as curr,
--     LAG(meter1) OVER () AS prev,
--     meter1 - LAG(meter1) OVER () AS cunsumption
-- from (select unix_ts, FROM_UNIXTIME(unix_ts) AS dt, meter1 from ttt where TIME(FROM_UNIXTIME(unix_ts)) = '00:00:00') as daily;

-- SELECT
-- 	unix_ts, date, hour, 'h' as marker,
--     meter1 as curr,
--     LAG(meter1) OVER () AS prev,
--     meter1 - LAG(meter1) OVER () AS cunsumption
-- from (select unix_ts, date(FROM_UNIXTIME(unix_ts)) as date, hour(FROM_UNIXTIME(unix_ts)) as hour, meter1 from ttt where minute(FROM_UNIXTIME(unix_ts)) = 0 and second(FROM_UNIXTIME(unix_ts)) = 0) as hourly;




-- INSERT INTO appliance_energy (unix_ts,local_dt,local_tm,marker, main,beda,bedp,boil,chrg,cwsh,dryr,dwsh,frdg,gen1,gen2,gen3,gen4,gen5,gen6,kit1,kit2,outp,vacu)
-- SELECT unix_ts, DATE(FROM_UNIXTIME(unix_ts)), TIME(FROM_UNIXTIME(unix_ts)), '', meter1 + meter2, meter13, meter6, meter8, meter21, meter10, meter4 + meter5, meter19, meter11, meter3, meter9, meter12, meter16, meter17, meter20, meter14, meter15, meter18, meter7
-- FROM real_energy;







-- SELECT
-- 	unix_ts)) 						AS unix_ts,
--     'd'       						AS marker,
-- 	DATE(FROM_UNIXTIME(unix_ts)) 	AS local_dt,
--     0 								AS local_hr,
--     meter1 + meter2 				AS main,
--     max(meter13) 						AS beda,
--     meter6 							AS bedp,
--     meter8 							AS boil,
--     meter21 						AS chrg,
--     meter10 						AS cwsh,
--     meter4 + meter5 AS dryr,
--     meter19 						AS dwsh,
--     meter11 						AS frdg,
--     meter3 AS gen1,
--     meter9 AS gen2,
--     meter12 AS gen3,
--     meter16 AS gen4,
--     meter17 AS gen5,
--     meter20 AS gen6,
--     meter14 AS kit1,
--     meter15 AS kit2,
--     meter18 AS outp,
--     meter7 							AS vacu
-- FROM real_energy GROUP BY DATE(FROM_UNIXTIME(unix_ts)) LIMIT 100;

-- -- SELECT DATE(FROM_UNIXTIME(unix_ts)) AS date, HOUR(FROM_UNIXTIME(unix_ts)) AS hour FROM real_energy GROUP BY DATE(FROM_UNIXTIME(unix_ts)), HOUR(FROM_UNIXTIME(unix_ts))  LIMIT 100;
