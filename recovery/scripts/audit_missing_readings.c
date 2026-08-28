#define _POSIX_C_SOURCE 200809L

#include <ctype.h>
#include <errno.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_COLS 64
#define MAX_NAME 128

typedef struct {
    char name[MAX_NAME];
    uint64_t blank_count;
} Column;

typedef struct {
    uint64_t rows;
    uint64_t malformed_rows;
    uint64_t timestamp_gaps;
    uint64_t missing_timestamps;
    uint64_t duplicate_or_backwards;
    uint64_t rows_with_null_measurements;
    uint64_t null_measurement_cells;
    uint64_t ihd_blank_rows;
    uint64_t ihd_present_rows;
    uint64_t marker_s_rows;
    uint64_t marker_other_nonblank_rows;
    int64_t first_ts;
    int64_t last_ts;
    int have_ts;
} Stats;

static const char *base_name(const char *path) {
    const char *slash = strrchr(path, '/');
    return slash ? slash + 1 : path;
}

static void stem_name(const char *path, char *out, size_t out_size) {
    const char *base = base_name(path);
    snprintf(out, out_size, "%s", base);
    char *dot = strrchr(out, '.');
    if (dot) *dot = '\0';
}

static int split_csv_simple(char *line, char **fields, int max_fields) {
    int count = 0;
    if (max_fields <= 0) return 0;
    fields[count++] = line;
    for (char *p = line; *p && count < max_fields; ++p) {
        if (*p == ',') {
            *p = '\0';
            fields[count++] = p + 1;
        }
    }
    return count;
}

static int is_blank(const char *value) {
    if (!value) return 1;
    while (*value) {
        if (!isspace((unsigned char)*value)) return 0;
        ++value;
    }
    return 1;
}

static int64_t parse_ts(const char *value, int *ok) {
    char *end = NULL;
    errno = 0;
    long long parsed = strtoll(value, &end, 10);
    *ok = (errno == 0 && end != value && *end == '\0');
    return (int64_t)parsed;
}

static void iso_utc(int64_t ts, char *out, size_t out_size) {
    time_t t = (time_t)ts;
    struct tm tm_value;
    if (!gmtime_r(&t, &tm_value)) {
        out[0] = '\0';
        return;
    }
    strftime(out, out_size, "%Y-%m-%dT%H:%M:%SZ", &tm_value);
}

static int find_col(Column *columns, int ncols, const char *name) {
    for (int i = 0; i < ncols; ++i) {
        if (strcmp(columns[i].name, name) == 0) return i;
    }
    return -1;
}

static int is_measurement_col(const char *name) {
    return strcmp(name, "unix_ts") != 0 &&
           strcmp(name, "marker") != 0 &&
           strcmp(name, "date") != 0 &&
           strcmp(name, "time") != 0 &&
           strcmp(name, "ihd") != 0;
}

static int audit_file(const char *path, const char *out_dir) {
    FILE *input = fopen(path, "r");
    if (!input) {
        fprintf(stderr, "Cannot open %s: %s\n", path, strerror(errno));
        return 1;
    }

    char stem[MAX_NAME];
    stem_name(path, stem, sizeof(stem));

    char detail_path[1024], gaps_path[1024], summary_path[1024], columns_path[1024], malformed_path[1024];
    snprintf(detail_path, sizeof(detail_path), "%s/%s_null_measurement_rows.csv", out_dir, stem);
    snprintf(gaps_path, sizeof(gaps_path), "%s/%s_missing_timestamp_ranges.csv", out_dir, stem);
    snprintf(summary_path, sizeof(summary_path), "%s/%s_summary.csv", out_dir, stem);
    snprintf(columns_path, sizeof(columns_path), "%s/%s_nulls_by_column.csv", out_dir, stem);
    snprintf(malformed_path, sizeof(malformed_path), "%s/%s_malformed_rows.csv", out_dir, stem);

    FILE *detail = fopen(detail_path, "w");
    FILE *gaps = fopen(gaps_path, "w");
    FILE *malformed = fopen(malformed_path, "w");
    if (!detail || !gaps || !malformed) {
        fprintf(stderr, "Cannot create audit output for %s\n", path);
        fclose(input);
        if (detail) fclose(detail);
        if (gaps) fclose(gaps);
        if (malformed) fclose(malformed);
        return 1;
    }

    fprintf(detail, "file,row_number,unix_ts,date,time,missing_columns\n");
    fprintf(gaps, "file,start_unix_ts,end_unix_ts,missing_seconds,start_utc,end_utc\n");
    fprintf(malformed, "file,row_number,reason\n");

    char *line = NULL;
    size_t capacity = 0;
    ssize_t length = getline(&line, &capacity, input);
    if (length < 0) {
        fprintf(stderr, "%s is empty\n", path);
        fclose(input); fclose(detail); fclose(gaps); fclose(malformed); free(line);
        return 1;
    }
    while (length > 0 && (line[length - 1] == '\n' || line[length - 1] == '\r')) line[--length] = '\0';

    char *header_fields[MAX_COLS];
    int ncols = split_csv_simple(line, header_fields, MAX_COLS);
    Column columns[MAX_COLS] = {0};
    for (int i = 0; i < ncols; ++i) snprintf(columns[i].name, sizeof(columns[i].name), "%s", header_fields[i]);

    int ts_col = find_col(columns, ncols, "unix_ts");
    int date_col = find_col(columns, ncols, "date");
    int time_col = find_col(columns, ncols, "time");
    int ihd_col = find_col(columns, ncols, "ihd");
    int marker_col = find_col(columns, ncols, "marker");
    if (ts_col < 0) {
        fprintf(stderr, "%s has no unix_ts column\n", path);
        fclose(input); fclose(detail); fclose(gaps); fclose(malformed); free(line);
        return 1;
    }

    Stats stats = {0};
    int64_t previous_ts = 0;
    int have_previous = 0;

    while ((length = getline(&line, &capacity, input)) >= 0) {
        ++stats.rows;
        while (length > 0 && (line[length - 1] == '\n' || line[length - 1] == '\r')) line[--length] = '\0';

        char *fields[MAX_COLS] = {0};
        int field_count = split_csv_simple(line, fields, MAX_COLS);
        if (field_count != ncols) {
            ++stats.malformed_rows;
            fprintf(malformed, "%s,%" PRIu64 ",expected_%d_fields_got_%d\n", base_name(path), stats.rows + 1, ncols, field_count);
            continue;
        }

        int ts_ok = 0;
        int64_t ts = parse_ts(fields[ts_col], &ts_ok);
        if (!ts_ok) {
            ++stats.malformed_rows;
            fprintf(malformed, "%s,%" PRIu64 ",invalid_unix_ts\n", base_name(path), stats.rows + 1);
            continue;
        }

        if (!stats.have_ts) {
            stats.first_ts = ts;
            stats.have_ts = 1;
        }
        stats.last_ts = ts;

        if (have_previous) {
            if (ts > previous_ts + 1) {
                int64_t start = previous_ts + 1;
                int64_t end = ts - 1;
                uint64_t missing = (uint64_t)(end - start + 1);
                char start_iso[32], end_iso[32];
                iso_utc(start, start_iso, sizeof(start_iso));
                iso_utc(end, end_iso, sizeof(end_iso));
                ++stats.timestamp_gaps;
                stats.missing_timestamps += missing;
                fprintf(gaps, "%s,%" PRId64 ",%" PRId64 ",%" PRIu64 ",%s,%s\n", base_name(path), start, end, missing, start_iso, end_iso);
            } else if (ts <= previous_ts) {
                ++stats.duplicate_or_backwards;
                fprintf(malformed, "%s,%" PRIu64 ",timestamp_not_strictly_increasing\n", base_name(path), stats.rows + 1);
            }
        }
        previous_ts = ts;
        have_previous = 1;

        if (ihd_col >= 0) {
            if (is_blank(fields[ihd_col])) ++stats.ihd_blank_rows;
            else ++stats.ihd_present_rows;
        }
        if (marker_col >= 0 && !is_blank(fields[marker_col])) {
            if (strcmp(fields[marker_col], "s") == 0) ++stats.marker_s_rows;
            else ++stats.marker_other_nonblank_rows;
        }

        int missing_count = 0;
        for (int i = 0; i < ncols; ++i) {
            if (is_measurement_col(columns[i].name) && is_blank(fields[i])) {
                ++columns[i].blank_count;
                ++missing_count;
            }
        }

        if (missing_count > 0) {
            ++stats.rows_with_null_measurements;
            stats.null_measurement_cells += (uint64_t)missing_count;
            fprintf(detail, "%s,%" PRIu64 ",%" PRId64 ",%s,%s,\"", base_name(path), stats.rows + 1, ts,
                    date_col >= 0 ? fields[date_col] : "", time_col >= 0 ? fields[time_col] : "");
            int emitted = 0;
            for (int i = 0; i < ncols; ++i) {
                if (is_measurement_col(columns[i].name) && is_blank(fields[i])) {
                    fprintf(detail, "%s%s", emitted ? ";" : "", columns[i].name);
                    emitted = 1;
                }
            }
            fprintf(detail, "\"\n");
        }

        if (stats.rows % 10000000ULL == 0) {
            fprintf(stdout, "%s: processed %" PRIu64 " rows\n", base_name(path), stats.rows);
            fflush(stdout);
        }
    }

    fclose(input);
    fclose(detail);
    fclose(gaps);
    fclose(malformed);
    free(line);

    FILE *summary = fopen(summary_path, "w");
    FILE *by_column = fopen(columns_path, "w");
    if (!summary || !by_column) {
        fprintf(stderr, "Cannot create summary output for %s\n", path);
        if (summary) fclose(summary);
        if (by_column) fclose(by_column);
        return 1;
    }

    uint64_t expected_seconds = 0;
    if (stats.have_ts && stats.last_ts >= stats.first_ts) expected_seconds = (uint64_t)(stats.last_ts - stats.first_ts + 1);
    char first_iso[32] = "", last_iso[32] = "";
    if (stats.have_ts) {
        iso_utc(stats.first_ts, first_iso, sizeof(first_iso));
        iso_utc(stats.last_ts, last_iso, sizeof(last_iso));
    }

    fprintf(summary, "file,rows,first_unix_ts,last_unix_ts,first_utc,last_utc,expected_seconds,missing_timestamp_ranges,missing_timestamps,duplicate_or_backwards,malformed_rows,rows_with_null_measurements,null_measurement_cells,ihd_present_rows,ihd_blank_rows,marker_s_rows,marker_other_nonblank_rows\n");
    fprintf(summary, "%s,%" PRIu64 ",%" PRId64 ",%" PRId64 ",%s,%s,%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 "\n",
            base_name(path), stats.rows, stats.first_ts, stats.last_ts, first_iso, last_iso, expected_seconds,
            stats.timestamp_gaps, stats.missing_timestamps, stats.duplicate_or_backwards, stats.malformed_rows,
            stats.rows_with_null_measurements, stats.null_measurement_cells, stats.ihd_present_rows, stats.ihd_blank_rows,
            stats.marker_s_rows, stats.marker_other_nonblank_rows);

    fprintf(by_column, "file,column,null_cells,total_rows,null_rate\n");
    for (int i = 0; i < ncols; ++i) {
        if (is_measurement_col(columns[i].name)) {
            double rate = stats.rows ? (double)columns[i].blank_count / (double)stats.rows : 0.0;
            fprintf(by_column, "%s,%s,%" PRIu64 ",%" PRIu64 ",%.12f\n", base_name(path), columns[i].name, columns[i].blank_count, stats.rows, rate);
        }
    }
    if (ihd_col >= 0) {
        double rate = stats.rows ? (double)stats.ihd_blank_rows / (double)stats.rows : 0.0;
        fprintf(by_column, "%s,ihd,%" PRIu64 ",%" PRIu64 ",%.12f\n", base_name(path), stats.ihd_blank_rows, stats.rows, rate);
    }

    fclose(summary);
    fclose(by_column);

    fprintf(stdout, "%s: done (%" PRIu64 " rows, %" PRIu64 " missing timestamps, %" PRIu64 " rows with null measurements)\n",
            base_name(path), stats.rows, stats.missing_timestamps, stats.rows_with_null_measurements);
    fflush(stdout);
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 4 || strcmp(argv[1], "--out-dir") != 0) {
        fprintf(stderr, "Usage: %s --out-dir OUTPUT_DIR FILE...\n", argv[0]);
        return 2;
    }

    int status = 0;
    for (int i = 3; i < argc; ++i) status |= audit_file(argv[i], argv[2]);
    return status;
}
