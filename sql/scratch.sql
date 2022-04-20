
-- select count(*) from R1Hz.meta; 					#'65404800'
-- select count(*) from R1Hz.apparent_energy; 		#'65404800'
-- select count(*) from R1Hz.apparent_pf; 			#'65404800'
-- select count(*) from R1Hz.apparent_power; 		#'65404800'
-- select count(*) from R1Hz.current; 				#'65404800'
-- select count(*) from R1Hz.displacement_pf; 		#'65404800'
-- select count(*) from R1Hz.reactive_energy; 		#'65404800'
-- select count(*) from R1Hz.reactive_power; 		#'65404800'
-- select count(*) from R1Hz.real_energy; 			#'65404800'
-- select count(*) from R1Hz.real_power; 			#'65404800'
-- select count(*) from R1Hz.utility; 				#'30240'
-- select count(*) from R1Hz.climate; 				#'18984'
-- select count(*) from R1Hz.appliance_current; 	#'65271526'
-- select count(*) from R1Hz.appliance_energy; 		#
-- select count(*) from R1Hz.appliance_reactive;	#'65404800'
-- elect count(*) from R1Hz.appliance_real; 		#'65404800'

-- check number si from TS 1559398793 & 15593815534.8 hrs outage at 2:32am on June 1, 2019

-- select local_dt, imputed, count(imputed) as readings, round(count(imputed)/86400*100,2) as percent from R1Hz.meta where imputed = '?' group by local_dt, imputed having count(imputed) > 0;
-- select local_dt, imputed, count(imputed) as readings, round(count(imputed)/86400*100,2) as percent from R1Hz.meta where imputed = 'N' group by local_dt, imputed having count(imputed) > 0;


-- select * from utility where consumption is null;

-- select * from missing where local_dt in ('2018-06-09', '2018-06-09');

-- select local_dt, imputed, count(imputed) as readings, round(count(imputed)/86400*100,2) as percent from missing where imputed = '?' group by local_dt, imputed having count(imputed) > 0;



-- LOCK TABLES apparent_energy WRITE, reactive_energy WRITE, real_energy WRITE;

-- ALTER TABLE apparent_energy CHANGE COLUMN meter1 meter1 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter2 meter2 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter3 meter3 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter4 meter4 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter5 meter5 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter6 meter6 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter7 meter7 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter8 meter8 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter9 meter9 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter10 meter10 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter11 meter11 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter12 meter12 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter13 meter13 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter14 meter14 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter15 meter15 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter16 meter16 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter17 meter17 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter18 meter18 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter19 meter19 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter20 meter20 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter21 meter21 BIGINT NULL DEFAULT NULL ;
-- ALTER TABLE reactive_energy CHANGE COLUMN meter1 meter1 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter2 meter2 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter3 meter3 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter4 meter4 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter5 meter5 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter6 meter6 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter7 meter7 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter8 meter8 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter9 meter9 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter10 meter10 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter11 meter11 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter12 meter12 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter13 meter13 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter14 meter14 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter15 meter15 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter16 meter16 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter17 meter17 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter18 meter18 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter19 meter19 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter20 meter20 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter21 meter21 BIGINT NULL DEFAULT NULL ;
-- ALTER TABLE real_energy CHANGE COLUMN meter1 meter1 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter2 meter2 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter3 meter3 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter4 meter4 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter5 meter5 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter6 meter6 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter7 meter7 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter8 meter8 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter9 meter9 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter10 meter10 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter11 meter11 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter12 meter12 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter13 meter13 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter14 meter14 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter15 meter15 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter16 meter16 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter17 meter17 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter18 meter18 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter19 meter19 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter20 meter20 BIGINT NULL DEFAULT NULL ,CHANGE COLUMN meter21 meter21 BIGINT NULL DEFAULT NULL ;

-- UNLOCK TABLES;


-- select min(unix_ts), max(unix_ts) from meta where local_dt = '2017-09-21';
-- select * from apparent_energy where unix_ts between 1505977200 and 1506063599;


-- stephen@junhao-M1 R1Hz.dataset % ./make-R1Hz.stage3.py db123
-- Processing raw data from 2017-09-13 ...
-- Processing raw data from 2017-09-14 ...
-- Processing raw data from 2017-09-15 ...
-- Processing raw data from 2017-09-16 ...
-- Processing raw data from 2017-09-17 ...
-- Processing raw data from 2017-09-18 ...
-- Processing raw data from 2017-09-19 ...
-- Processing raw data from 2017-09-20 ...
-- Processing raw data from 2017-09-21 ...
-- Traceback (most recent call last):
--   File "/Users/stephen/Library/Mobile Documents/com~apple~CloudDocs/Research/SourceCode/R1Hz.dataset/./make-R1Hz.stage3.py", line 101, in <module>
--     cur.execute('UPDATE R1Hz.apparent_energy SET ' + set_clause + ' WHERE unix_ts = %s;', tuple(apparent_energy) + (raw_ts,))
--   File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/site-packages/mysql/connector/cursor.py", line 572, in execute
--     self._handle_result(self._connection.cmd_query(stmt))
--   File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/site-packages/mysql/connector/connection.py", line 920, in cmd_query
--     result = self._handle_result(self._send_cmd(ServerCmd.QUERY, query))
--   File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/site-packages/mysql/connector/connection.py", line 730, in _handle_result
--     raise errors.get_exception(packet)
-- mysql.connector.errors.DataError: 1264 (22003): Out of range value for column 'meter2' at row 1




select DATE(FROM_UNIXTIME(unix_ts)) AS date, meter1 as curr ,
lag(meter1) over(PARTITION BY DATE(FROM_UNIXTIME(unix_ts)) order by unix_ts)  as prev,
meter1 - lag(meter1) over(PARTITION BY DATE(FROM_UNIXTIME(unix_ts)) order by unix_ts)  as energy
from ttt group by DATE(FROM_UNIXTIME(unix_ts)) ;



select DATE(FROM_UNIXTIME(unix_ts)) AS date, meter1 from ttt group by DATE(FROM_UNIXTIME(unix_ts)) ;


meter1 as curr ,
lag(meter1) over(PARTITION BY DATE(FROM_UNIXTIME(unix_ts)) order by unix_ts)  as prev,
meter1 - lag(meter1) over(PARTITION BY DATE(FROM_UNIXTIME(unix_ts)) order by unix_ts)  as energy
from ttt group by DATE(FROM_UNIXTIME(unix_ts)) ;



select DATE(FROM_UNIXTIME(unix_ts)) AS date, max(meter1), min(meter1), max(meter1)-min(meter1) as consumption from ttt group by date;



first_value(meter1) over (partition by DATE(FROM_UNIXTIME(unix_ts))) from ttt group by date;



select (FROM_UNIXTIME(unix_ts)) AS date, meter1 from ttt where minute(FROM_UNIXTIME(unix_ts)) = 0 and second(FROM_UNIXTIME(unix_ts)) = 0;





SELECT
	date, 'm' as marker,
    meter1 as curr,
    LAG(meter1) OVER () AS prev,
    meter1 - LAG(meter1) OVER () AS cunsumption
from (select date(FROM_UNIXTIME(unix_ts)) as date, meter1 from ttt where DAY(FROM_UNIXTIME(unix_ts)) = 1 and TIME(FROM_UNIXTIME(unix_ts)) = '00:00:00') as monthly;

SELECT
	dt, 'd' as marker,
    meter1 as curr,
    LAG(meter1) OVER () AS prev,
    meter1 - LAG(meter1) OVER () AS cunsumption
from (select FROM_UNIXTIME(unix_ts) AS dt, meter1 from ttt where TIME(FROM_UNIXTIME(unix_ts)) = '00:00:00') as daily;

SELECT
	date, hour, 'h' as marker,
    meter1 as curr,
    LAG(meter1) OVER () AS prev,
    meter1 - LAG(meter1) OVER () AS cunsumption
from (select date(FROM_UNIXTIME(unix_ts)) as date, hour(FROM_UNIXTIME(unix_ts)) as hour, meter1 from ttt where minute(FROM_UNIXTIME(unix_ts)) = 0 and second(FROM_UNIXTIME(unix_ts)) = 0) as hourly;



select FROM_UNIXTIME(unix_ts) AS dt, meter1 from ttt where TIME(FROM_UNIXTIME(unix_ts)) = '00:00:00';



select FROM_UNIXTIME(unix_ts) AS dt, meter1 from ttt where DAY(FROM_UNIXTIME(unix_ts)) = 1 and TIME(FROM_UNIXTIME(unix_ts)) = '00:00:00';






S-- ELECT
--     employee_name,
--     hours,
--     FIRST_VALUE(employee_name) OVER (
--         ORDER BY hours
--     ) least_over_time
-- FROM
--     overtime;


-- SELECT
--     employee_name,
--     hours,
--     LAST_VALUE(employee_name) OVER (
--         ORDER BY hours
--         RANGE BETWEEN
--             UNBOUNDED PRECEDING AND
--             UNBOUNDED FOLLOWING
--     ) highest_overtime_employee
-- FROM
--     overtime;






-- SELECT
--   city,
--   year,
--   population_needing_house,
--   LAG(population_needing_house)
--     OVER (PARTITION BY city ORDER BY year ) AS previous_year,
--   population_needing_house - LAG(population_needing_house)
--    OVER (PARTITION BY city ORDER BY year ) AS difference_previous_year
-- FROM housing
-- ORDER BY city, year


-- LOCK TABLES apparent_pf WRITE, displacement_pf WRITE, current WRITE, utility WRITE, climate WRITE;


-- ALTER TABLE apparent_pf CHANGE COLUMN meter1 meter1 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter2 meter2 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter3 meter3 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter4 meter4 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter5 meter5 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter6 meter6 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter7 meter7 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter8 meter8 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter9 meter9 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter10 meter10 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter11 meter11 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter12 meter12 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter13 meter13 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter14 meter14 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter15 meter15 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter16 meter16 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter17 meter17 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter18 meter18 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter19 meter19 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter20 meter20 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter21 meter21 DECIMAL(3,2) NULL DEFAULT NULL ;

-- ALTER TABLE displacement_pf CHANGE COLUMN meter1 meter1 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter2 meter2 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter3 meter3 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter4 meter4 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter5 meter5 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter6 meter6 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter7 meter7 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter8 meter8 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter9 meter9 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter10 meter10 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter11 meter11 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter12 meter12 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter13 meter13 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter14 meter14 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter15 meter15 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter16 meter16 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter17 meter17 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter18 meter18 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter19 meter19 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter20 meter20 DECIMAL(3,2) NULL DEFAULT NULL ,CHANGE COLUMN meter21 meter21 DECIMAL(3,2) NULL DEFAULT NULL ;

-- ALTER TABLE current CHANGE COLUMN meter1 meter1 DECIMAL(5,1) NULL DEFAULT NULL ,CHANGE COLUMN meter2 meter2 DECIMAL(5,1) NULL DEFAULT NULL ,CHANGE COLUMN meter3 meter3 DECIMAL(5,1) NULL DEFAULT NULL ,CHANGE COLUMN meter4 meter4 DECIMAL(5,1) NULL DEFAULT NULL ,CHANGE COLUMN meter5 meter5 DECIMAL(5,1) NULL DEFAULT NULL ,CHANGE COLUMN meter6 meter6 DECIMAL(5,1) NULL DEFAULT NULL ,CHANGE COLUMN meter7 meter7 DECIMAL(5,1) NULL DEFAULT NULL ,CHANGE COLUMN meter8 meter8 DECIMAL(5,1) NULL DEFAULT NULL ,CHANGE COLUMN meter9 meter9 DECIMAL(5,1) NULL DEFAULT NULL ,CHANGE COLUMN meter10 meter10 DECIMAL(5,1) NULL DEFAULT NULL ,CHANGE COLUMN meter11 meter11 DECIMAL(5,1) NULL DEFAULT NULL ,CHANGE COLUMN meter12 meter12 DECIMAL(5,1) NULL DEFAULT NULL ,CHANGE COLUMN meter13 meter13 DECIMAL(5,1) NULL DEFAULT NULL ,CHANGE COLUMN meter14 meter14 DECIMAL(5,1) NULL DEFAULT NULL ,CHANGE COLUMN meter15 meter15 DECIMAL(5,1) NULL DEFAULT NULL ,CHANGE COLUMN meter16 meter16 DECIMAL(5,1) NULL DEFAULT NULL ,CHANGE COLUMN meter17 meter17 DECIMAL(5,1) NULL DEFAULT NULL ,CHANGE COLUMN meter18 meter18 DECIMAL(5,1) NULL DEFAULT NULL ,CHANGE COLUMN meter19 meter19 DECIMAL(5,1) NULL DEFAULT NULL ,CHANGE COLUMN meter20 meter20 DECIMAL(5,1) NULL DEFAULT NULL ,CHANGE COLUMN meter21 meter21 DECIMAL(5,1) NULL DEFAULT NULL ;


-- ALTER TABLE utility CHANGE COLUMN consumption consumption DECIMAL(6,3) NULL DEFAULT NULL ;

-- ALTER TABLE climate CHANGE COLUMN temp temp REAL NULL DEFAULT NULL ,CHANGE COLUMN dew_point dew_point REAL NULL DEFAULT NULL ,CHANGE COLUMN visibility visibility REAL NULL DEFAULT NULL ,CHANGE COLUMN stn_press stn_press REAL NULL DEFAULT NULL ,CHANGE COLUMN hmdx hmdx REAL NULL DEFAULT NULL ,CHANGE COLUMN wind_chill wind_chill REAL NULL DEFAULT NULL ;

-- UNLOCK TABLES;




-- ALTER TABLE `R1Hz`.`meta` 
-- CHANGE COLUMN `voltage_l1` `voltage_l1` DECIMAL(4,1) NULL DEFAULT NULL ,
-- CHANGE COLUMN `voltage_l2` `voltage_l2` DECIMAL(4,1) NULL DEFAULT NULL ,
-- CHANGE COLUMN `freq` `freq` DECIMAL(3,1) NULL DEFAULT NULL ;

-- select * from meta where unix_ts in (1528598135, 1528598136, 1528598137, 1528598138, 1528598139, 1528598140, 1528598141, 1528598142, 1528598143, 1528598144, 1528598145, 1528598146, 1528598147, 1528598148, 1528598149, 1528598150, 1528598151, 1528598152, 1528598153, 1528598154, 1528598155, 1528598156, 1528598157, 1528598158, 1528598159, 1528598160, 1528598161, 1528598162, 1528598163, 1528598164, 1528598165, 1528598166, 1528598167, 1528598168, 1528598169, 1528598170, 1528598171, 1528598172, 1528598173, 1528598174, 1528598175, 1528598176, 1528598177, 1528598178, 1528598179, 1528598180, 1528598181, 1528598182, 1528598183, 1528598184, 1528598185, 1528598186, 1528598187, 1528598188, 1528598189, 1528598190, 1528598191, 1528598192, 1528598193, 1528598194, 1528598195, 1528598196, 1528598197, 1528598198, 1528598199, 1528598200, 1528598201, 1528598202, 1528598203, 1528598204, 1528598205, 1528598206, 1528598207, 1528598208, 1528598209, 1528598210, 1528598211, 1528598212, 1528598213, 1528598214, 1528598215, 1528598216, 1528598217, 1528598218, 1528598219, 1528598220, 1528598221, 1528598222, 1528598223, 1528598224, 1528598225, 1528598226, 1528598227, 1528598228, 1528598229, 1528598230, 1528598231, 1528598232, 1528598233, 1528598234, 1528598235, 1528598236, 1528598237, 1528598238, 1528598239, 1528598240, 1528598241, 1528598242, 1528598243, 1528598244, 1528598245, 1528598246, 1528598247, 1528598248, 1528598249, 1528598250, 1528598251, 1528598252, 1528598253, 1528598254, 1528598255, 1528598256, 1528598257, 1528598258, 1528598259, 1528598260, 1528598261, 1528598262, 1528598263, 1528598264, 1528598265, 1528598266, 1528598267, 1528598268, 1528598269, 1528598270, 1528598271, 1528598272, 1528598273, 1528598274, 1528598275, 1528598276, 1528598277, 1528598278, 1528598279, 1528598280, 1528598281, 1528598282, 1528598283, 1528598284, 1528598285, 1528598286, 1528598287, 1528598288, 1528598289, 1528598290, 1528598291);
-- 1528598135, 1528598136, 1528598137, 1528598138, 1528598139, 1528598140, 1528598141, 1528598142, 1528598143, 1528598144, 1528598145, 1528598146, 1528598147, 1528598148, 1528598149, 1528598150, 1528598151, 1528598152, 1528598153, 1528598154, 1528598155, 1528598156, 1528598157, 1528598158, 1528598159, 1528598160, 1528598161, 1528598162, 1528598163, 1528598164, 1528598165, 1528598166, 1528598167, 1528598168, 1528598169, 1528598170, 1528598171, 1528598172, 1528598173, 1528598174, 1528598175, 1528598176, 1528598177, 1528598178, 1528598179, 1528598180, 1528598181, 1528598182, 1528598183, 1528598184, 1528598185, 1528598186, 1528598187, 1528598188, 1528598189, 1528598190, 1528598191, 1528598192, 1528598193, 1528598194, 1528598195, 1528598196, 1528598197, 1528598198, 1528598199, 1528598200, 1528598201, 1528598202, 1528598203, 1528598204, 1528598205, 1528598206, 1528598207, 1528598208, 1528598209, 1528598210, 1528598211, 1528598212, 1528598213, 1528598214, 1528598215, 1528598216, 1528598217, 1528598218, 1528598219, 1528598220, 1528598221, 1528598222, 1528598223, 1528598224, 1528598225, 1528598226, 1528598227, 1528598228, 1528598229, 1528598230, 1528598231, 1528598232, 1528598233, 1528598234, 1528598235, 1528598236, 1528598237, 1528598238, 1528598239, 1528598240, 1528598241, 1528598242, 1528598243, 1528598244, 1528598245, 1528598246, 1528598247, 1528598248, 1528598249, 1528598250, 1528598251, 1528598252, 1528598253, 1528598254, 1528598255, 1528598256, 1528598257, 1528598258, 1528598259, 1528598260, 1528598261, 1528598262, 1528598263, 1528598264, 1528598265, 1528598266, 1528598267, 1528598268, 1528598269, 1528598270, 1528598271, 1528598272, 1528598273, 1528598274, 1528598275, 1528598276, 1528598277, 1528598278, 1528598279, 1528598280, 1528598281, 1528598282, 1528598283, 1528598284, 1528598285, 1528598286, 1528598287, 1528598288, 1528598289, 1528598290, 1528598291
-- Warning (code 1062): Duplicate entry '1528598135' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598136' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598137' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598138' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598139' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598140' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598141' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598142' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598143' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598144' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598145' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598146' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598147' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598148' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598149' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598150' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598151' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598152' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598153' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598154' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598155' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598156' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598157' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598158' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598159' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598160' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598161' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598162' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598163' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598164' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598165' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598166' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598167' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598168' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598169' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598170' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598171' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598172' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598173' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598174' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598175' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598176' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598177' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598178' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598179' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598180' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598181' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598182' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598183' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598184' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598185' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598186' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598187' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598188' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598189' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598190' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598191' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598192' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598193' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598194' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598195' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598196' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598197' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598198' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598199' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598200' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598201' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598202' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598203' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598204' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598205' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598206' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598207' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598208' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598209' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598210' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598211' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598212' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598213' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598214' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598215' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598216' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598217' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598218' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598219' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598220' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598221' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598222' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598223' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598224' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598225' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598226' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598227' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598228' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598229' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598230' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598231' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598232' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598233' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598234' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598235' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598236' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598237' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598238' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598239' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598240' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598241' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598242' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598243' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598244' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598245' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598246' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598247' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598248' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598249' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598250' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598251' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598252' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598253' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598254' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598255' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598256' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598257' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598258' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598259' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598260' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598261' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598262' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598263' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598264' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598265' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598266' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598267' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598268' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598269' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598270' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598271' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598272' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598273' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598274' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598275' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598276' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598277' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598278' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598279' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598280' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598281' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598282' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598283' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598284' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598285' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598286' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598287' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598288' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598289' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598290' for key 'reactive_energy.PRIMARY'
-- Warning (code 1062): Duplicate entry '1528598291' for key 'reactive_energy.PRIMARY'
