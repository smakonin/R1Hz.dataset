Raw Modbus files are not stored in Git because the complete directory is
82,367,715,595 bytes (82.367716 GB; 76.710913 GiB) across 757 daily CSV files.

The canonical dataset release places them under raw_modbus/ with names
SUB_YYYY-MM-DD.csv, covering every local date from 2017-09-13 through
2019-10-09. Each file is headerless. Every row has 45 fields:

  unix_ts, bank identifier A-H, 43 integer values for registers 4021-4063

There are eight bank rows per captured second. A complete ordinary 24-hour
day therefore has 691,200 rows. Counts differ for partial acquisition days and
daylight-saving transitions; consumers must not assume a fixed row count.

The raw files are retained for provenance and audit. They are not imputed or
normalized. Obtain them from the Harvard Dataverse release identified by
https://doi.org/10.7910/DVN/RCB5VJ.
