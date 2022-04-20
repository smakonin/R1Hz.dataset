# Residential 1Hz Dataset (R1Hz)
*Copyright (C) 2017-2022 Stephen Makonin.*

Welcome to using the R1Hz (*pronounced* |rīz|) dataset.
Data was downloaded from [http://doi.org/](http://doi.org/)

### Need help? 
Please read: [http://doi.org/](http://doi.org/)
(*Paper included, see* **.pdf**)

### Using R1Hz? 
You **must cite** the above paper.
(*BibTeX included, see* **.bib**)

## House Details
| Item | Description |
|:--|:--|
| Type Details:    | Residential side-attached duplex |
| Location:        | Burnaby, BC, Canada |
| Local Timezone:  | America/Vancouver |
| Year Built:      | 2016 |
| Average Occupants: | 3| 
| Floors:           | 1: Level 1, 105.4 m^2 |
| |2: Level 2, 67.5 m^2 |
| Lighting:        | Mainly LED with some zirconia light bulbs in the bathrooms |
| HVAC Type (data not included):	     | In-floor radiant (with gas boiler) |
| Thermostats (data not included):   | 1x Ecobee 3, 4x Ecobee 3 Lite |
| Metering Date Range: | 2017-09-13 to 2018-10-31 |
| IHD Device (smart meter):       | Rainforest Eagle 200 |
| Sub-meter Equip (BCPM): | DENT PowerScout 24 |
| Sub-meter Count: | 21 |
| Sub-meter Mains: | meter1,meter2 |

## Files
|File | Description |
|:--|:--|
|Voltage.csv         | |
|Frequency.csv       | |
|Current.csv         | |
|ApparentPF.csv     | |
|DisplacementPF.csv | |
|RealPower.csv       | |
|ReactivePower.csv   | |
|ApparentPower.csv   | |
|RealEnergy.csv      | |
|ReactiveEnergy.csv  | |
|ApparentEnergy.csv  | |
|R1Hz-PowerPanel.pdf  | |


## CSV Columns
|Sub-Meter | Description |
|:--|:--|
|  |  |
|meter1  | House Sub-Panel L1 |
|meter2  | House Sub-Panel L2 |
|meter3  | Lights & Plugs (general label) |
|meter4  | Clothes Dryer L1 |
|meter5  | Clothes Dryer L2 |
|meter6  | Bedroom Plugs |
|meter7  | Built-in Vacuum |
|meter8  | Boiler (for hot water and radiant heating) |
|meter9  | Lights & Plugs (general label) |
|meter10 | Clothes Washer |
|meter11 | Kitchen Fridge |
|meter12 | Lights & Plugs (general label, incl. Internet modem and network equipment) |
|meter13 | Bedrooms AFCI Arc-Fault Plugs |
|meter14 | Kitchen Counter Plugs |
|meter15 | Kitchen Counter Plugs |
|meter16 | Lights & Plugs (general label) |
|meter17 | Lights & Plugs (general label) |
|meter18 | Outside Plugs |
|meter19 | Dishwasher |
|meter20 | Lights & Plugs (general label) |
|meter21 | Mobile Phone Changers (garburator & microwave not installed) |

## Appliance Information
| ID | Name | L1 | L2 | Mains? | Mixed Loads? | Notes                                                     |
|:--|:--|:-:|:-:|:-:|:-:|:--|
| MAIN | House Sub-Panel       | 1 | 2 | Y | Y | *see* † |
| BEDA | Bedroom Plugs         | | 13 | N | Y | AFCI Arc-Fault Plugs |
| BEDP | Bedroom Plugs         | 6 | | N | Y | |
| BOIL | Boiler                | | 8 | N | N | for hot water and radiant heating |
| CHRG | Phone Changers        | | 21 | N | N | garburator & microwave not installed |
| CWSH | Clothes Washer        | | 10 | N | N | |
| DRYR | Clothes Dryer         | 4 | 5 | N | N | |
| DWSH | Dishwasher            | | 19 | N | N | |
| FRDG | Kitchen Fridge        | | 11 | N | N | |
| GEN1 | Lights & Plugs        | | 3 | N | Y | general label |
| GEN2 | Lights & Plugs        | 9 | | N | Y | |
| GEN3 | Lights & Plugs        | 12 | | N | Y | general label, incl. Internet modem and network equipment |
| GEN4 | Lights & Plugs        | | 16 | N | Y | general label |
| GEN5 | Lights & Plugs        | 17 | | N | Y | general label |
| GEN6 | Lights & Plugs        | 20 | | N | Y | general label |
| KIT1 | Kitchen Counter Plugs | 14 | | N | Y | |
| KIT2 | Kitchen Counter Plugs | 15 | | N | Y | |
| OUTP | Outside Plugs         | | 18 | N | Y | |
| VACU | Built-in Vacuum       | | 7 | N | N | |

† *garage has utility power, garage metering not included due to metering limitations*
