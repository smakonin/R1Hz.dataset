
-- select count(*) from R1Hz.meta; 				#'65404800'
-- select count(*) from R1Hz.apparent_energy; 	#'65404800'
-- select count(*) from R1Hz.apparent_pf; 		#'65404800'
-- select count(*) from R1Hz.apparent_power; 	#'65404800'
-- select count(*) from R1Hz.current; 			#'65404800'
-- select count(*) from R1Hz.displacement_pf; 	#'65404800'
-- select count(*) from R1Hz.reactive_energy; 	#'65404800'
-- select count(*) from R1Hz.reactive_power; 	#'65404800'
-- select count(*) from R1Hz.real_energy; 		#'65404800'
-- select count(*) from R1Hz.real_power; 		#'65404800'
-- select count(*) from R1Hz.utility; 			#'30240'
-- select count(*) from R1Hz.climate; 			#'18984'


-- ####### NEED TO RERUN 2017-09-21
select local_dt, imputed, count(imputed) as readings, round(count(imputed)/86400*100,2) as percent from R1Hz.meta where local_dt between '2017-09-13' and '2017-09-18' group by local_dt, imputed;
-- select local_dt, imputed, count(imputed) as readings, round(count(imputed)/86400*100,2) as percent from R1Hz.meta where imputed = 'N' group by local_dt, imputed having count(imputed) > 0;
