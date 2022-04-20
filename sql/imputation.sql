-- -----------------------------------------------
-- 
-- Inspect missing readings
-- 
-- -----------------------------------------------
SELECT * FROM missing_day;
-- SELECT * FROM meta WHERE imputed='-' AND local_dt='2017-10-02';
-- CALL report_missing(1553136300);


-- -----------------------------------------------
-- 
-- Foward/backward fill occasional missed readings
-- 
-- -----------------------------------------------
CALL fill_missing(1505568338, 1505568338-1);
CALL fill_missing(1505568339, 1505568339+1);
CALL fill_missing(1506966182, 1506966182-1);
CALL fill_missing(1509855469, 1509855469-1);
CALL fill_missing(1511182759, 1511182759-1);
CALL fill_missing(1513412249, 1513412249-1);
CALL fill_missing(1514116172, 1514116172-1);
CALL fill_missing(1517588996, 1517588996-1);
CALL fill_missing(1517842914, 1517842914-1);
CALL fill_missing(1518634954, 1518634954-1);
CALL fill_missing(1520071747, 1520071747-1);
CALL fill_missing(1521117173, 1521117173-1);
CALL fill_missing(1521611738, 1521611738-1);
CALL fill_missing(1522357518, 1522357518-1);
CALL fill_missing(1529427666, 1529427666-1);
CALL fill_missing(1537711378, 1537711378-1);
CALL fill_missing(1538650144, 1538650144-1);
CALL fill_missing(1540041921, 1540041921-1);
CALL fill_missing(1541855017, 1541855017-1);
CALL fill_missing(1542481278, 1542481278-1);
CALL fill_missing(1543608035, 1543608035-1);
CALL fill_missing(1545032373, 1545032373-1);
CALL fill_missing(1545255165, 1545255165-1);
CALL fill_missing(1547749746, 1547749746-1);
CALL fill_missing(1549081039, 1549081039-1);
CALL fill_missing(1549537131, 1549537131-1);
CALL fill_missing(1551952022, 1551952022-1);
CALL fill_missing(1551953217, 1551953217-1);
CALL fill_missing(1552982175, 1552982175-1);
CALL fill_missing(1553136300, 1553136300-1);
CALL fill_missing(1553136301, 1553136301+1);
CALL fill_missing(1554105884, 1554105884-1);
CALL fill_missing(1554647244, 1554647244-1);
CALL fill_missing(1556457937, 1556457937-1);
CALL fill_missing(1559200765, 1559200765-1);
CALL fill_missing(1559464755, 1559464755-1);
CALL fill_missing(1559551139, 1559551139-1);
CALL fill_missing(1560064467, 1560064467-1);
CALL fill_missing(1561017408, 1561017408-1);
CALL fill_missing(1561471427, 1561471427-1);
CALL fill_missing(1562133985, 1562133985-1);
CALL fill_missing(1562191478, 1562191478-1);
CALL fill_missing(1562191491, 1562191491-1);
CALL fill_missing(1563009624, 1563009624-1);
CALL fill_missing(1565111327, 1565111327-1);
CALL fill_missing(1565766099, 1565766099-1);
CALL fill_missing(1565766330, 1565766330-1);
CALL fill_missing(1566131878, 1566131878-1);
CALL fill_missing(1566808502, 1566808502-1);
CALL fill_missing(1568198424, 1568198424-1);
CALL fill_missing(1568227989, 1568227989-1);






-- INSERT IGNORE INTO real_energy (unix_ts) SELECT unix_ts FROM missing;



-- SELECT unix_ts FROM meta WHERE imputed = '-' limit 1; 
-- OUTER APPLY 
--    ( 
--     
--    WHERE E.DepartmentID = D.DepartmentID 
--    ) A 
--    
  
  
  
  


-- -----------------------------------------------
-- 
-- 1 Meter/logging error, so data is truly missing
-- 
-- -----------------------------------------------
-- UPDATE meta            SET imputed='-', voltage_l1=NULL, voltage_l2=NULL, freq=NULL WHERE unix_ts BETWEEN 1528482113 AND 1528598292;
-- UPDATE apparent_energy SET meter1=NULL, meter2=NULL, meter3=NULL, meter4=NULL, meter5=NULL, meter6=NULL, meter7=NULL, meter8=NULL, meter9=NULL, meter10=NULL, meter11=NULL, meter12=NULL, meter13=NULL, meter14=NULL, meter15=NULL, meter16=NULL, meter17=NULL, meter18=NULL, meter19=NULL, meter20=NULL, meter21=NULL WHERE unix_ts BETWEEN 1528482113 AND 1528598292;
-- UPDATE apparent_pf     SET meter1=NULL, meter2=NULL, meter3=NULL, meter4=NULL, meter5=NULL, meter6=NULL, meter7=NULL, meter8=NULL, meter9=NULL, meter10=NULL, meter11=NULL, meter12=NULL, meter13=NULL, meter14=NULL, meter15=NULL, meter16=NULL, meter17=NULL, meter18=NULL, meter19=NULL, meter20=NULL, meter21=NULL WHERE unix_ts BETWEEN 1528482113 AND 1528598292;
-- UPDATE apparent_power  SET meter1=NULL, meter2=NULL, meter3=NULL, meter4=NULL, meter5=NULL, meter6=NULL, meter7=NULL, meter8=NULL, meter9=NULL, meter10=NULL, meter11=NULL, meter12=NULL, meter13=NULL, meter14=NULL, meter15=NULL, meter16=NULL, meter17=NULL, meter18=NULL, meter19=NULL, meter20=NULL, meter21=NULL WHERE unix_ts BETWEEN 1528482113 AND 1528598292;
-- UPDATE current         SET meter1=NULL, meter2=NULL, meter3=NULL, meter4=NULL, meter5=NULL, meter6=NULL, meter7=NULL, meter8=NULL, meter9=NULL, meter10=NULL, meter11=NULL, meter12=NULL, meter13=NULL, meter14=NULL, meter15=NULL, meter16=NULL, meter17=NULL, meter18=NULL, meter19=NULL, meter20=NULL, meter21=NULL WHERE unix_ts BETWEEN 1528482113 AND 1528598292;
-- UPDATE displacement_pf SET meter1=NULL, meter2=NULL, meter3=NULL, meter4=NULL, meter5=NULL, meter6=NULL, meter7=NULL, meter8=NULL, meter9=NULL, meter10=NULL, meter11=NULL, meter12=NULL, meter13=NULL, meter14=NULL, meter15=NULL, meter16=NULL, meter17=NULL, meter18=NULL, meter19=NULL, meter20=NULL, meter21=NULL WHERE unix_ts BETWEEN 1528482113 AND 1528598292;
-- UPDATE reactive_energy SET meter1=NULL, meter2=NULL, meter3=NULL, meter4=NULL, meter5=NULL, meter6=NULL, meter7=NULL, meter8=NULL, meter9=NULL, meter10=NULL, meter11=NULL, meter12=NULL, meter13=NULL, meter14=NULL, meter15=NULL, meter16=NULL, meter17=NULL, meter18=NULL, meter19=NULL, meter20=NULL, meter21=NULL WHERE unix_ts BETWEEN 1528482113 AND 1528598292;
-- UPDATE reactive_power  SET meter1=NULL, meter2=NULL, meter3=NULL, meter4=NULL, meter5=NULL, meter6=NULL, meter7=NULL, meter8=NULL, meter9=NULL, meter10=NULL, meter11=NULL, meter12=NULL, meter13=NULL, meter14=NULL, meter15=NULL, meter16=NULL, meter17=NULL, meter18=NULL, meter19=NULL, meter20=NULL, meter21=NULL WHERE unix_ts BETWEEN 1528482113 AND 1528598292;
-- UPDATE real_energy     SET meter1=NULL, meter2=NULL, meter3=NULL, meter4=NULL, meter5=NULL, meter6=NULL, meter7=NULL, meter8=NULL, meter9=NULL, meter10=NULL, meter11=NULL, meter12=NULL, meter13=NULL, meter14=NULL, meter15=NULL, meter16=NULL, meter17=NULL, meter18=NULL, meter19=NULL, meter20=NULL, meter21=NULL WHERE unix_ts BETWEEN 1528482113 AND 1528598292;
-- UPDATE real_power      SET meter1=NULL, meter2=NULL, meter3=NULL, meter4=NULL, meter5=NULL, meter6=NULL, meter7=NULL, meter8=NULL, meter9=NULL, meter10=NULL, meter11=NULL, meter12=NULL, meter13=NULL, meter14=NULL, meter15=NULL, meter16=NULL, meter17=NULL, meter18=NULL, meter19=NULL, meter20=NULL, meter21=NULL WHERE unix_ts BETWEEN 1528482113 AND 1528598292;
-- select *, DATE(FROM_UNIXTIME(unix_ts)) as date,TIME(FROM_UNIXTIME(unix_ts)) as time from real_energy where unix_ts in (1528482113-1, 1528598292+1, 1528482113+31536000-1, 1528598292+31536000+1);
-- How many seconds are there in a year of 365 days?
-- 31,536,000 seconds, 31536000
-- one year would equal 365 times 24 times 60 times 60 seconds…or 31,536,000 seconds!




-- -----------------------------------------------
-- 
-- 2 Meter/logging error, so data is truly missing
-- 
-- -----------------------------------------------
-- '2019-06-01','?','17251','19.97','1559381554,1559381555,1559381556,1559381557,1559381558,1559381559,1559381560,1559381561,1559381562,1559381563,1559381564,1559381565,1559381566,1559381567,1559381568,1559381569,1559381570,1559381571,1559381572,1559381573,1559381574,1559381575,1559381576,1559381577,1559381578,1559381579,1559381580,1559381581,1559381582,1559381583,1559381584,1559381585,1559381586,1559381587,1559381588,1559381589,1559381590,1559381591,1559381592,1559381593,1559381594,1559381595,1559381596,1559381597,1559381598,1559381599,1559381600,1559381601,1559381602,1559381603,1559381604,1559381605,1559381606,1559381607,1559381608,1559381609,1559381610,1559381611,1559381612,1559381613,1559381614,1559381615,1559381616,1559381617,1559381618,1559381619,1559381620,1559381621,1559381622,1559381623,1559381624,1559381625,1559381626,1559381627,1559381628,1559381629,1559381630,1559381631,1559381632,1559381633,1559381634,1559381635,1559381636,1559381637,1559381638,1559381639,1559381640,1559381641,1559381642,1559381643,1559381644,1559381645,1559381646,1'
-- '1559381554','2019-06-01','02:32:34','?',NULL,NULL,NULL
-- '1559399215','2019-06-01','07:26:55','?',NULL,NULL,NULL
-- WHERE unix_ts BETWEEN 1559381554 AND 1559399215;
-- select * from real_energy where unix_ts in (1559381554-1, 1559399215+1);

SELECT * FROM missing_day;