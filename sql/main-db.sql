CREATE DATABASE R1Hz /*!40100 DEFAULT CHARACTER SET ascii */ /*!80016 DEFAULT ENCRYPTION='N' */;

CREATE TABLE raw_modbus (
	unix_ts int NOT NULL,
	meter char(1) NOT NULL,
	reg_4021 int NOT NULL,
	reg_4022 int NOT NULL,
	reg_4023 int NOT NULL,
	reg_4024 int NOT NULL,
	reg_4025 int NOT NULL,
	reg_4026 int NOT NULL,
	reg_4027 int NOT NULL,
	reg_4028 int NOT NULL,
	reg_4029 int NOT NULL,
	reg_4030 int NOT NULL,
	reg_4031 int NOT NULL,
	reg_4032 int NOT NULL,
	reg_4033 int NOT NULL,
	reg_4034 int NOT NULL,
	reg_4035 int NOT NULL,
	reg_4036 int NOT NULL,
	reg_4037 int NOT NULL,
	reg_4038 int NOT NULL,
	reg_4039 int NOT NULL,
	reg_4040 int NOT NULL,
	reg_4041 int NOT NULL,
	reg_4042 int NOT NULL,
	reg_4043 int NOT NULL,
	reg_4044 int NOT NULL,
	reg_4045 int NOT NULL,
	reg_4046 int NOT NULL,
	reg_4047 int NOT NULL,
	reg_4048 int NOT NULL,
	reg_4049 int NOT NULL,
	reg_4050 int NOT NULL,
	reg_4051 int NOT NULL,
	reg_4052 int NOT NULL,
	reg_4053 int NOT NULL,
	reg_4054 int NOT NULL,
	reg_4055 int NOT NULL,
	reg_4056 int NOT NULL,
	reg_4057 int NOT NULL,
	reg_4058 int NOT NULL,
	reg_4059 int NOT NULL,
	reg_4060 int NOT NULL,
	reg_4061 int NOT NULL,
	reg_4062 int NOT NULL,
	reg_4063 int NOT NULL,
	PRIMARY KEY (unix_ts,meter)
) ENGINE=InnoDB DEFAULT CHARSET=ascii;

CREATE TABLE smart_meter (
    unix_ts int NOT NULL,
    marker char(1) NOT NULL,
    local_dt char(10) NOT NULL,
    local_tm char(8) NOT NULL,
    power int DEFAULT NULL,
    energy decimal(9,1) DEFAULT NULL,
    PRIMARY KEY (unix_ts,marker),
    KEY LOCAL (local_dt,local_tm)
) ENGINE=InnoDB DEFAULT CHARSET=ascii;

CREATE TABLE apparent_energy (
    unix_ts int NOT NULL,
    meter1 int DEFAULT NULL,
    meter2 int DEFAULT NULL,
    meter3 int DEFAULT NULL,
    meter4 int DEFAULT NULL,
    meter5 int DEFAULT NULL,
    meter6 int DEFAULT NULL,
    meter7 int DEFAULT NULL,
    meter8 int DEFAULT NULL,
    meter9 int DEFAULT NULL,
    meter10 int DEFAULT NULL,
    meter11 int DEFAULT NULL,
    meter12 int DEFAULT NULL,
    meter13 int DEFAULT NULL,
    meter14 int DEFAULT NULL,
    meter15 int DEFAULT NULL,
    meter16 int DEFAULT NULL,
    meter17 int DEFAULT NULL,
    meter18 int DEFAULT NULL,
    meter19 int DEFAULT NULL,
    meter20 int DEFAULT NULL,
    meter21 int DEFAULT NULL,
    PRIMARY KEY (unix_ts)
) ENGINE=InnoDB DEFAULT CHARSET=ascii;

CREATE TABLE apparent_pf (
    unix_ts int NOT NULL,
    meter1 decimal(3,2) DEFAULT NULL,
    meter2 decimal(3,2) DEFAULT NULL,
    meter3 decimal(3,2) DEFAULT NULL,
    meter4 decimal(3,2) DEFAULT NULL,
    meter5 decimal(3,2) DEFAULT NULL,
    meter6 decimal(3,2) DEFAULT NULL,
    meter7 decimal(3,2) DEFAULT NULL,
    meter8 decimal(3,2) DEFAULT NULL,
    meter9 decimal(3,2) DEFAULT NULL,
    meter10 decimal(3,2) DEFAULT NULL,
    meter11 decimal(3,2) DEFAULT NULL,
    meter12 decimal(3,2) DEFAULT NULL,
    meter13 decimal(3,2) DEFAULT NULL,
    meter14 decimal(3,2) DEFAULT NULL,
    meter15 decimal(3,2) DEFAULT NULL,
    meter16 decimal(3,2) DEFAULT NULL,
    meter17 decimal(3,2) DEFAULT NULL,
    meter18 decimal(3,2) DEFAULT NULL,
    meter19 decimal(3,2) DEFAULT NULL,
    meter20 decimal(3,2) DEFAULT NULL,
    meter21 decimal(3,2) DEFAULT NULL,
    PRIMARY KEY (unix_ts)
) ENGINE=InnoDB DEFAULT CHARSET=ascii;

CREATE TABLE apparent_power (
    unix_ts int NOT NULL,
    meter1 int DEFAULT NULL,
    meter2 int DEFAULT NULL,
    meter3 int DEFAULT NULL,
    meter4 int DEFAULT NULL,
    meter5 int DEFAULT NULL,
    meter6 int DEFAULT NULL,
    meter7 int DEFAULT NULL,
    meter8 int DEFAULT NULL,
    meter9 int DEFAULT NULL,
    meter10 int DEFAULT NULL,
    meter11 int DEFAULT NULL,
    meter12 int DEFAULT NULL,
    meter13 int DEFAULT NULL,
    meter14 int DEFAULT NULL,
    meter15 int DEFAULT NULL,
    meter16 int DEFAULT NULL,
    meter17 int DEFAULT NULL,
    meter18 int DEFAULT NULL,
    meter19 int DEFAULT NULL,
    meter20 int DEFAULT NULL,
    meter21 int DEFAULT NULL,
    PRIMARY KEY (unix_ts)
) ENGINE=InnoDB DEFAULT CHARSET=ascii;

CREATE TABLE current (
    unix_ts int NOT NULL,
    meter1 decimal(5,1) DEFAULT NULL,
    meter2 decimal(5,1) DEFAULT NULL,
    meter3 decimal(5,1) DEFAULT NULL,
    meter4 decimal(5,1) DEFAULT NULL,
    meter5 decimal(5,1) DEFAULT NULL,
    meter6 decimal(5,1) DEFAULT NULL,
    meter7 decimal(5,1) DEFAULT NULL,
    meter8 decimal(5,1) DEFAULT NULL,
    meter9 decimal(5,1) DEFAULT NULL,
    meter10 decimal(5,1) DEFAULT NULL,
    meter11 decimal(5,1) DEFAULT NULL,
    meter12 decimal(5,1) DEFAULT NULL,
    meter13 decimal(5,1) DEFAULT NULL,
    meter14 decimal(5,1) DEFAULT NULL,
    meter15 decimal(5,1) DEFAULT NULL,
    meter16 decimal(5,1) DEFAULT NULL,
    meter17 decimal(5,1) DEFAULT NULL,
    meter18 decimal(5,1) DEFAULT NULL,
    meter19 decimal(5,1) DEFAULT NULL,
    meter20 decimal(5,1) DEFAULT NULL,
    meter21 decimal(5,1) DEFAULT NULL,
    PRIMARY KEY (unix_ts)
) ENGINE=InnoDB DEFAULT CHARSET=ascii;

CREATE TABLE displacement_pf (
    unix_ts int NOT NULL,
    meter1 decimal(3,2) DEFAULT NULL,
    meter2 decimal(3,2) DEFAULT NULL,
    meter3 decimal(3,2) DEFAULT NULL,
    meter4 decimal(3,2) DEFAULT NULL,
    meter5 decimal(3,2) DEFAULT NULL,
    meter6 decimal(3,2) DEFAULT NULL,
    meter7 decimal(3,2) DEFAULT NULL,
    meter8 decimal(3,2) DEFAULT NULL,
    meter9 decimal(3,2) DEFAULT NULL,
    meter10 decimal(3,2) DEFAULT NULL,
    meter11 decimal(3,2) DEFAULT NULL,
    meter12 decimal(3,2) DEFAULT NULL,
    meter13 decimal(3,2) DEFAULT NULL,
    meter14 decimal(3,2) DEFAULT NULL,
    meter15 decimal(3,2) DEFAULT NULL,
    meter16 decimal(3,2) DEFAULT NULL,
    meter17 decimal(3,2) DEFAULT NULL,
    meter18 decimal(3,2) DEFAULT NULL,
    meter19 decimal(3,2) DEFAULT NULL,
    meter20 decimal(3,2) DEFAULT NULL,
    meter21 decimal(3,2) DEFAULT NULL,
    PRIMARY KEY (unix_ts)
) ENGINE=InnoDB DEFAULT CHARSET=ascii;

CREATE TABLE meta (
    unix_ts int NOT NULL,
    local_dt char(10) NOT NULL,
    local_tm char(8) NOT NULL,
    imputed char(1) NOT NULL,
    voltage_l1 decimal(4,1) DEFAULT NULL,
    voltage_l2 decimal(4,1) DEFAULT NULL,
    freq decimal(3,1) DEFAULT NULL,
    PRIMARY KEY (unix_ts),
    KEY LOCAL (local_dt,local_tm),
    KEY MISSING (imputed,unix_ts)
) ENGINE=InnoDB DEFAULT CHARSET=ascii;

CREATE TABLE reactive_energy (
    unix_ts int NOT NULL,
    meter1 int DEFAULT NULL,
    meter2 int DEFAULT NULL,
    meter3 int DEFAULT NULL,
    meter4 int DEFAULT NULL,
    meter5 int DEFAULT NULL,
    meter6 int DEFAULT NULL,
    meter7 int DEFAULT NULL,
    meter8 int DEFAULT NULL,
    meter9 int DEFAULT NULL,
    meter10 int DEFAULT NULL,
    meter11 int DEFAULT NULL,
    meter12 int DEFAULT NULL,
    meter13 int DEFAULT NULL,
    meter14 int DEFAULT NULL,
    meter15 int DEFAULT NULL,
    meter16 int DEFAULT NULL,
    meter17 int DEFAULT NULL,
    meter18 int DEFAULT NULL,
    meter19 int DEFAULT NULL,
    meter20 int DEFAULT NULL,
    meter21 int DEFAULT NULL,
    PRIMARY KEY (unix_ts)
) ENGINE=InnoDB DEFAULT CHARSET=ascii;

CREATE TABLE reactive_power (
    unix_ts int NOT NULL,
    meter1 int DEFAULT NULL,
    meter2 int DEFAULT NULL,
    meter3 int DEFAULT NULL,
    meter4 int DEFAULT NULL,
    meter5 int DEFAULT NULL,
    meter6 int DEFAULT NULL,
    meter7 int DEFAULT NULL,
    meter8 int DEFAULT NULL,
    meter9 int DEFAULT NULL,
    meter10 int DEFAULT NULL,
    meter11 int DEFAULT NULL,
    meter12 int DEFAULT NULL,
    meter13 int DEFAULT NULL,
    meter14 int DEFAULT NULL,
    meter15 int DEFAULT NULL,
    meter16 int DEFAULT NULL,
    meter17 int DEFAULT NULL,
    meter18 int DEFAULT NULL,
    meter19 int DEFAULT NULL,
    meter20 int DEFAULT NULL,
    meter21 int DEFAULT NULL,
    PRIMARY KEY (unix_ts)
) ENGINE=InnoDB DEFAULT CHARSET=ascii;

CREATE TABLE real_energy (
    unix_ts int NOT NULL,
    meter1 int DEFAULT NULL,
    meter2 int DEFAULT NULL,
    meter3 int DEFAULT NULL,
    meter4 int DEFAULT NULL,
    meter5 int DEFAULT NULL,
    meter6 int DEFAULT NULL,
    meter7 int DEFAULT NULL,
    meter8 int DEFAULT NULL,
    meter9 int DEFAULT NULL,
    meter10 int DEFAULT NULL,
    meter11 int DEFAULT NULL,
    meter12 int DEFAULT NULL,
    meter13 int DEFAULT NULL,
    meter14 int DEFAULT NULL,
    meter15 int DEFAULT NULL,
    meter16 int DEFAULT NULL,
    meter17 int DEFAULT NULL,
    meter18 int DEFAULT NULL,
    meter19 int DEFAULT NULL,
    meter20 int DEFAULT NULL,
    meter21 int DEFAULT NULL,
    PRIMARY KEY (unix_ts)
) ENGINE=InnoDB DEFAULT CHARSET=ascii;

CREATE TABLE real_power (
    unix_ts int NOT NULL,
    meter1 int DEFAULT NULL,
    meter2 int DEFAULT NULL,
    meter3 int DEFAULT NULL,
    meter4 int DEFAULT NULL,
    meter5 int DEFAULT NULL,
    meter6 int DEFAULT NULL,
    meter7 int DEFAULT NULL,
    meter8 int DEFAULT NULL,
    meter9 int DEFAULT NULL,
    meter10 int DEFAULT NULL,
    meter11 int DEFAULT NULL,
    meter12 int DEFAULT NULL,
    meter13 int DEFAULT NULL,
    meter14 int DEFAULT NULL,
    meter15 int DEFAULT NULL,
    meter16 int DEFAULT NULL,
    meter17 int DEFAULT NULL,
    meter18 int DEFAULT NULL,
    meter19 int DEFAULT NULL,
    meter20 int DEFAULT NULL,
    meter21 int DEFAULT NULL,
    PRIMARY KEY (unix_ts)
) ENGINE=InnoDB DEFAULT CHARSET=ascii;

CREATE ALGORITHM=UNDEFINED DEFINER=root@localhost SQL SECURITY DEFINER VIEW missing AS select meta.unix_ts AS unix_ts,meta.local_dt AS local_dt,meta.local_tm AS local_tm,meta.imputed AS imputed,meta.voltage_l1 AS voltage_l1,meta.voltage_l2 AS voltage_l2,meta.freq AS freq from meta where (meta.imputed = '-');

CREATE ALGORITHM=UNDEFINED DEFINER=root@localhost SQL SECURITY DEFINER VIEW missing_day AS select missing.local_dt AS local_dt,missing.imputed AS imputed,count(missing.imputed) AS readings,round(((count(missing.imputed) / 86400) * 100),2) AS percent,group_concat(missing.unix_ts separator ',') AS missing_ts from missing group by missing.local_dt,missing.imputed;

CREATE ALGORITHM=UNDEFINED DEFINER=root@localhost SQL SECURITY DEFINER VIEW mains_compare AS select a.unix_ts AS unix_ts,a.power AS smart_meter,(b.meter1 + b.meter2) AS bcpm from (smart_meter a join real_power b) where (a.unix_ts = b.unix_ts);

DELIMITER $$
CREATE DEFINER=root@localhost PROCEDURE fill_missing(IN miss_ts INT, IN src_ts INT)
BEGIN
    REPLACE INTO meta            (unix_ts,local_dt,local_tm,imputed,voltage_l1,voltage_l2,freq)                                                                                                           SELECT miss_ts,DATE(FROM_UNIXTIME(miss_ts)),TIME(FROM_UNIXTIME(miss_ts)),'Y',voltage_l1,voltage_l2,freq                                                                       FROM meta            WHERE unix_ts = src_ts;
    REPLACE INTO apparent_energy (unix_ts,meter1,meter2,meter3,meter4,meter5,meter6,meter7,meter8,meter9,meter10,meter11,meter12,meter13,meter14,meter15,meter16,meter17,meter18,meter19,meter20,meter21) SELECT miss_ts,meter1,meter2,meter3,meter4,meter5,meter6,meter7,meter8,meter9,meter10,meter11,meter12,meter13,meter14,meter15,meter16,meter17,meter18,meter19,meter20,meter21 FROM apparent_energy WHERE unix_ts = src_ts;
    REPLACE INTO apparent_pf     (unix_ts,meter1,meter2,meter3,meter4,meter5,meter6,meter7,meter8,meter9,meter10,meter11,meter12,meter13,meter14,meter15,meter16,meter17,meter18,meter19,meter20,meter21) SELECT miss_ts,meter1,meter2,meter3,meter4,meter5,meter6,meter7,meter8,meter9,meter10,meter11,meter12,meter13,meter14,meter15,meter16,meter17,meter18,meter19,meter20,meter21 FROM apparent_pf     WHERE unix_ts = src_ts;
    REPLACE INTO apparent_power  (unix_ts,meter1,meter2,meter3,meter4,meter5,meter6,meter7,meter8,meter9,meter10,meter11,meter12,meter13,meter14,meter15,meter16,meter17,meter18,meter19,meter20,meter21) SELECT miss_ts,meter1,meter2,meter3,meter4,meter5,meter6,meter7,meter8,meter9,meter10,meter11,meter12,meter13,meter14,meter15,meter16,meter17,meter18,meter19,meter20,meter21 FROM apparent_power  WHERE unix_ts = src_ts;
    REPLACE INTO current         (unix_ts,meter1,meter2,meter3,meter4,meter5,meter6,meter7,meter8,meter9,meter10,meter11,meter12,meter13,meter14,meter15,meter16,meter17,meter18,meter19,meter20,meter21) SELECT miss_ts,meter1,meter2,meter3,meter4,meter5,meter6,meter7,meter8,meter9,meter10,meter11,meter12,meter13,meter14,meter15,meter16,meter17,meter18,meter19,meter20,meter21 FROM current         WHERE unix_ts = src_ts;
    REPLACE INTO displacement_pf (unix_ts,meter1,meter2,meter3,meter4,meter5,meter6,meter7,meter8,meter9,meter10,meter11,meter12,meter13,meter14,meter15,meter16,meter17,meter18,meter19,meter20,meter21) SELECT miss_ts,meter1,meter2,meter3,meter4,meter5,meter6,meter7,meter8,meter9,meter10,meter11,meter12,meter13,meter14,meter15,meter16,meter17,meter18,meter19,meter20,meter21 FROM displacement_pf WHERE unix_ts = src_ts;
    REPLACE INTO reactive_energy (unix_ts,meter1,meter2,meter3,meter4,meter5,meter6,meter7,meter8,meter9,meter10,meter11,meter12,meter13,meter14,meter15,meter16,meter17,meter18,meter19,meter20,meter21) SELECT miss_ts,meter1,meter2,meter3,meter4,meter5,meter6,meter7,meter8,meter9,meter10,meter11,meter12,meter13,meter14,meter15,meter16,meter17,meter18,meter19,meter20,meter21 FROM reactive_energy WHERE unix_ts = src_ts;
    REPLACE INTO reactive_power  (unix_ts,meter1,meter2,meter3,meter4,meter5,meter6,meter7,meter8,meter9,meter10,meter11,meter12,meter13,meter14,meter15,meter16,meter17,meter18,meter19,meter20,meter21) SELECT miss_ts,meter1,meter2,meter3,meter4,meter5,meter6,meter7,meter8,meter9,meter10,meter11,meter12,meter13,meter14,meter15,meter16,meter17,meter18,meter19,meter20,meter21 FROM reactive_power  WHERE unix_ts = src_ts;
    REPLACE INTO real_energy     (unix_ts,meter1,meter2,meter3,meter4,meter5,meter6,meter7,meter8,meter9,meter10,meter11,meter12,meter13,meter14,meter15,meter16,meter17,meter18,meter19,meter20,meter21) SELECT miss_ts,meter1,meter2,meter3,meter4,meter5,meter6,meter7,meter8,meter9,meter10,meter11,meter12,meter13,meter14,meter15,meter16,meter17,meter18,meter19,meter20,meter21 FROM real_energy     WHERE unix_ts = src_ts;
    REPLACE INTO real_power      (unix_ts,meter1,meter2,meter3,meter4,meter5,meter6,meter7,meter8,meter9,meter10,meter11,meter12,meter13,meter14,meter15,meter16,meter17,meter18,meter19,meter20,meter21) SELECT miss_ts,meter1,meter2,meter3,meter4,meter5,meter6,meter7,meter8,meter9,meter10,meter11,meter12,meter13,meter14,meter15,meter16,meter17,meter18,meter19,meter20,meter21 FROM real_power      WHERE unix_ts = src_ts;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=root@localhost PROCEDURE nullify_missing(IN miss_ts INT)
BEGIN
    INSERT INTO apparent_energy (unix_ts) VALUES (miss_ts);
    INSERT INTO apparent_pf (unix_ts) VALUES (miss_ts);
    INSERT INTO apparent_power (unix_ts) VALUES (miss_ts);
    INSERT INTO current (unix_ts) VALUES (miss_ts);
    INSERT INTO displacement_pf (unix_ts) VALUES (miss_ts);    
    INSERT INTO reactive_energy (unix_ts) VALUES (miss_ts);
    INSERT INTO reactive_power (unix_ts) VALUES (miss_ts);
    INSERT INTO real_energy (unix_ts) VALUES (miss_ts);
    INSERT INTO real_power (unix_ts) VALUES (miss_ts);
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=root@localhost PROCEDURE report_missing(IN miss_ts INT)
BEGIN
    select * from meta where unix_ts between miss_ts-1 and miss_ts+1;
    select * from apparent_energy where unix_ts between miss_ts-1 and miss_ts+1;
    select * from apparent_pf where unix_ts between miss_ts-1 and miss_ts+1;
    select * from apparent_power where unix_ts between miss_ts-1 and miss_ts+1;
    select * from current where unix_ts between miss_ts-1 and miss_ts+1;
    select * from displacement_pf where unix_ts between miss_ts-1 and miss_ts+1;
    select * from reactive_energy where unix_ts between miss_ts-1 and miss_ts+1;
    select * from reactive_power where unix_ts between miss_ts-1 and miss_ts+1;
    select * from real_energy where unix_ts between miss_ts-1 and miss_ts+1;
    select * from real_power where unix_ts between miss_ts-1 and miss_ts+1;
END$$
DELIMITER ;
