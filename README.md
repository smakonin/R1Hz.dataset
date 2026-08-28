# Residential 1 Hz Energy Dataset (R1Hz)

R1Hz is a 757-day, circuit-level residential electricity dataset from one side-attached duplex in Burnaby, British Columbia, Canada. It combines four aligned 1 Hz electrical streams, derived interval-energy products, utility and in-home-display observations, outdoor climate data, and the retained daily Modbus acquisition records used to create the processed files.

- Dataset and canonical citation: [Harvard Dataverse, DOI 10.7910/DVN/RCB5VJ](https://doi.org/10.7910/DVN/RCB5VJ)
- Data-descriptor manuscript: [`paper/ieeedata_descriptor.pdf`](paper/ieeedata_descriptor.pdf)
- Code repository: <https://github.com/smakonin/R1Hz.dataset>

The recovered files replace the earlier files under their canonical root-level names. They are not distributed from GitHub because the four 1 Hz CSVs alone are approximately 23.7 GiB uncompressed. GitHub contains collection, processing, recovery, validation, schema, and manuscript materials; Harvard Dataverse is the authoritative data record.

## Instrumentation and coverage

| Item | Description |
|---|---|
| Site | One side-attached duplex, Burnaby, BC, Canada |
| Time zone | `America/Vancouver` |
| Circuit meter | DENT PowerScout 24; 21 physical inputs mapped to 19 logical channels |
| Smart-meter gateway/IHD | Rainforest Automation Eagle 200 |
| Main 1 Hz interval | 2017-09-13 through 2019-10-09 local time |
| Main 1 Hz rows | 65,404,800 rows in each of four aligned files |

The exact 19-channel order is:

```text
main, beda, bedp, boil, chrg, cwsh, dryr, dwsh, frdg,
gen1, gen2, gen3, gen4, gen5, gen6, kit1, kit2, outp, vacu
```

`main` combines meter inputs 1 and 2, and `dryr` combines inputs 4 and 5. All other logical channels map to one physical input. The complete dictionary and mixed-load notes are in `appliances.csv` in the Dataverse release and in Table 4 of the manuscript.

## Canonical data files

Counts exclude the header row. Sizes are uncompressed; compressed Dataverse objects will differ.

| Logical path | Grain | Rows/files | Coverage | Uncompressed size | Contents |
|---|---:|---:|---|---:|---|
| `appliances.csv` | dictionary | 19 rows | n/a | 895 B | Logical channel names and physical meter mapping |
| `climate.csv` | hourly | 18,984 rows | 2017-09-01--2019-10-31 | 1.271 MiB | Outdoor climate observations |
| `current.csv` | 1 Hz | 65,404,800 rows | 2017-09-13--2019-10-09 | 6.581 GiB | Circuit current (A) |
| `power_factor.csv` | 1 Hz | 65,404,800 rows | 2017-09-13--2019-10-09 | 7.736 GiB | Circuit power factor |
| `power.csv` | 1 Hz | 65,404,800 rows | 2017-09-13--2019-10-09 | 4.768 GiB | Circuit real power (W) and sparse aligned IHD power |
| `reactive.csv` | 1 Hz | 65,404,800 rows | 2017-09-13--2019-10-09 | 4.604 GiB | Circuit reactive power (var) |
| `energy_hourly.csv` | hourly | 18,168 rows | 2017-09-13--2019-10-09 | 1.457 MiB | Utility, main, and circuit energy (Wh) |
| `energy_daily.csv` | daily | 757 rows | 2017-09-13--2019-10-09 | 81.546 KiB | Daily-labelled energy aggregates (Wh) |
| `energy_monthly.csv` | monthly | 26 rows | 2017-09--2019-10 | 3.724 KiB | Monthly-labelled energy aggregates (Wh); edge months are partial |
| `ihd.csv` | native, irregular | 1,619,689 rows | 2017-09-13--2018-09-13 | 67.954 MiB | Eagle 200 power (W) and cumulative energy (kWh) |
| `utility.csv` | hourly | 30,240 rows | 2016-06-09--2019-11-20 | 1.039 MiB | Utility interval energy (Wh, 10 Wh resolution) |
| `raw_modbus/SUB_YYYY-MM-DD.csv` | one local day/file | 757 files | 2017-09-13--2019-10-09 | 76.711 GiB total | Headerless, device-native register records |

The four large 1 Hz files may be supplied as compressed archives or as date-partitioned compressed members to remain within Harvard Dataverse's 2.5 GB per-file limit. Logical filenames, coverage, row counts, uncompressed byte counts, and checksums should be preserved in the release manifest.

## Synthetic-data marker and recovery

Every recovered row has `s` in the `marker` column. An `s` means at least one value on that row is synthetic. In a daily or monthly file, it means at least one lower-grain input was synthetic. It does not imply that every cell on the row was changed.

Two common 1 Hz acquisition gaps were recovered from the same channel and local clock time 364 days away. The 364-day displacement preserves weekday and clock-time alignment:

| Target interval (`America/Vancouver`) | Donor interval |
|---|---|
| 2018-06-08 11:21:53--2018-06-09 19:35:34 PDT | 2019-06-07 11:21:53--2019-06-08 19:35:34 PDT |
| 2019-06-01 02:32:34--07:19:52 PDT | 2018-06-02 02:32:34--07:19:52 PDT |

This is deterministic pattern-based imputation, not recovery of the events that actually occurred during an outage. Thirteen additional isolated real/reactive-power seconds were estimated using local channel regression and bracketing interpolation. Hourly gaps were reconstructed from recovered 1 Hz power, native IHD means, or a month-local utility-to-main model; daily and monthly files were rebuilt from the recovered hourly product.

| File | Rows marked `s` | Imputed cells |
|---|---:|---:|
| `current.csv` | 133,261 | 2,531,958 |
| `power_factor.csv` | 133,261 | 2,531,959 |
| `power.csv` | 133,274 | 2,532,206 |
| `reactive.csv` | 133,274 | 2,532,206 |
| **Four-file total** | n/a | **10,128,329 of 4,970,764,800 circuit cells (0.203758%)** |
| `energy_hourly.csv` | 174 | 876 |
| `energy_daily.csv` | 47 | rebuilt from hourly values |
| `energy_monthly.csv` | 21 | rebuilt from daily values |

Other marker values are distinct: blank = ordinary row, `+` = legacy row inserted during original 1 Hz regularization, `d` = retained duplicate native IHD timestamp, and `t` = local-time discontinuity associated with a daylight-saving transition.

Synthetic intervals should normally be excluded from transient, event-timing, and ground-truth NILM evaluation, or included only in a reported sensitivity analysis. Detailed methods, exact inputs, scripts, cell-level logs, and validation receipts are under [`recovery/`](recovery/).

## Raw Modbus provenance

`raw_modbus/` contains one unprocessed file for every local acquisition date. The complete directory is 82,367,715,595 bytes (82.367716 GB; 76.710913 GiB). Each `SUB_YYYY-MM-DD.csv` is headerless and has 45 fields per row:

```text
unix_ts, bank identifier A-H, 43 integer register values for addresses 4021-4063
```

There are eight bank rows per captured second. A complete ordinary day has 691,200 rows; partial acquisition days and daylight-saving transitions differ. These records are neither normalized nor imputed and are retained so register conversion, channel mapping, timestamp handling, and recovery can be audited.

## Climate source and licence

Hourly observations came from Environment and Climate Change Canada's Historical Climate Data service for **VANCOUVER INTL A**, British Columbia:

| Field | Value |
|---|---|
| Climate / WMO / TC identifiers | 1108395 / 71892 / YVR |
| Coordinates and elevation | 49.19 N, -123.18 W; 4.30 m |
| Current station operator | NAV Canada |

Source units are degrees Celsius for temperature and dew point, percent for relative humidity, mm for precipitation, tens of degrees true for wind direction, km/h for wind speed, km for visibility, and kPa for station pressure. Humidex and wind chill are indices, and `weather` is categorical. The source uses Local Standard Time year-round; one hour is added where daylight-saving time is observed before representing timestamps in `America/Vancouver`.

Source flags mean `E` = estimated, `M` = missing, `NA` = not available, and blank = unobserved; `D`, where present, means subject to further quality control. For the NAV Canada `Weather` field, `NA` means no special weather elements were reported. See the [station report](https://climate.weather.gc.ca/climate_data/hourly_data_e.html?climate_id=1108395&Year=2016&Month=1&Day=1&timeframe=1&time=LST), [technical documentation](https://www.canada.ca/en/environment-climate-change/services/climate-change/canadian-centre-climate-services/display-download/technical-documentation-hourly-data.html), and [FAQ](https://climate.weather.gc.ca/FAQ_e.html#Q5).

The Historical Climate Data technical documentation links the [ECCC Limited Use Software and Data Product Licence Agreement](https://climate.weather.gc.ca/prods_servs/attachment1_e.html). It permits redistribution without an explicit fee for the ECCC product provided that ECCC is acknowledged and recipients accept the same redistribution restrictions. Attribution: *Based on Environment and Climate Change Canada data; Historical Climate Data, VANCOUVER INTL A (Climate Identifier 1108395).* See [`NOTICE.md`](NOTICE.md) for the licence boundary and redistribution conditions.

## Known data characteristics

- The first hourly row intentionally retains 19 blank circuit fields because its preceding source hour lies outside 1 Hz coverage.
- `utility.csv` retains 172 blank hourly-energy values among 30,240 rows.
- `ihd.csv` retains 76 duplicate native timestamps, marked `d`.
- Five climate hours have all observation fields blank; `precip_amt` is blank throughout the processed climate file, while humidex and wind chill are conditionally applicable.
- Mixed circuits are not appliance-state ground truth, and the single monitored dwelling is not a representative household sample.

## Repository layout

| Path | Purpose |
|---|---|
| `data-collection/` | Eagle 200 and PowerScout acquisition code |
| `raw-climate/` | Original monthly ECCC climate downloads and metadata |
| `raw_modbus/` | Raw-file schema and Dataverse pointer; the 76.711 GiB payload is not in Git |
| `raw-utility/` | Source utility exports |
| `sql/` and `make-R1Hz.*` | Original database-oriented processing pipeline |
| `recovery/` | Recovery code, compact method inputs, logs, and validation receipts |
| `paper/` | IEEE Data Descriptions manuscript source and compiled PDF |

## Citation and licensing

Use the dataset DOI when citing the data and record the Git commit when identifying the processing implementation. Machine-readable citation metadata are in [`CITATION.cff`](CITATION.cff).

Repository source code is licensed under the MIT License. That software licence does not replace the terms applying to the Dataverse data, ECCC climate observations, manuscript, or third-party source records. See [`LICENSE`](LICENSE) and [`NOTICE.md`](NOTICE.md).
