#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <inttypes.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_COLS 64
#define MAX_MEASUREMENTS 24
#define RANGE_COUNT 6
#define WEEK_SECONDS 604800
#define HOURS_PER_WEEK 168
#define YEAR_SHIFT_SECONDS 31449600LL

typedef struct {
    const char *target_label;
    const char *donor_label;
    int64_t start_ts;
    int64_t end_ts;
    int32_t *values;
    uint32_t *valid_masks;
} Range;

typedef struct {
    uint64_t n;
    uint64_t exact;
    double sum_x;
    double sum_y;
    double sum_x2;
    double sum_y2;
    double sum_xy;
    double sum_abs_error;
    double sum_squared_error;
} Stats;

typedef struct {
    double sum_x;
    double sum_y;
    uint32_t n;
} HourBin;

static Range ranges[RANGE_COUNT] = {
    {"2018-05-04 to 2018-05-10", "2019-05-03 to 2019-05-09", 1525417200LL, 1526021999LL, NULL, NULL},
    {"2018-05-11 to 2018-05-17", "2019-05-10 to 2019-05-16", 1526022000LL, 1526626799LL, NULL, NULL},
    {"2018-05-18 to 2018-05-24", "2019-05-17 to 2019-05-23", 1526626800LL, 1527231599LL, NULL, NULL},
    {"2018-05-25 to 2018-05-31", "2019-05-24 to 2019-05-30", 1527231600LL, 1527836399LL, NULL, NULL},
    {"2018-06-15 to 2018-06-21", "2019-06-14 to 2019-06-20", 1529046000LL, 1529650799LL, NULL, NULL},
    {"2018-06-22 to 2018-06-28", "2019-06-21 to 2019-06-27", 1529650800LL, 1530255599LL, NULL, NULL},
};

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

static int is_measurement(const char *name) {
    return strcmp(name, "unix_ts") != 0 &&
           strcmp(name, "marker") != 0 &&
           strcmp(name, "date") != 0 &&
           strcmp(name, "time") != 0 &&
           strcmp(name, "ihd") != 0;
}

static int find_range(int64_t timestamp) {
    for (int i = 0; i < RANGE_COUNT; ++i) {
        if (timestamp >= ranges[i].start_ts && timestamp <= ranges[i].end_ts) return i;
    }
    return -1;
}

static int parse_int32(const char *value, int32_t *output) {
    if (!value || *value == '\0') return 0;
    char *end = NULL;
    errno = 0;
    long parsed = strtol(value, &end, 10);
    if (errno != 0 || end == value || *end != '\0' || parsed < INT32_MIN || parsed > INT32_MAX) return 0;
    *output = (int32_t)parsed;
    return 1;
}

static int parse_int64(const char *value, int64_t *output) {
    char *end = NULL;
    errno = 0;
    long long parsed = strtoll(value, &end, 10);
    if (errno != 0 || end == value || *end != '\0') return 0;
    *output = (int64_t)parsed;
    return 1;
}

static void update_stats(Stats *stats, double x, double y) {
    double error = y - x;
    ++stats->n;
    if (x == y) ++stats->exact;
    stats->sum_x += x;
    stats->sum_y += y;
    stats->sum_x2 += x * x;
    stats->sum_y2 += y * y;
    stats->sum_xy += x * y;
    stats->sum_abs_error += fabs(error);
    stats->sum_squared_error += error * error;
}

static double correlation(const Stats *stats) {
    if (stats->n < 2) return NAN;
    double n = (double)stats->n;
    double numerator = n * stats->sum_xy - stats->sum_x * stats->sum_y;
    double denom_x = n * stats->sum_x2 - stats->sum_x * stats->sum_x;
    double denom_y = n * stats->sum_y2 - stats->sum_y * stats->sum_y;
    if (denom_x <= 0.0 || denom_y <= 0.0) return NAN;
    return numerator / sqrt(denom_x * denom_y);
}

static void print_metric_row(FILE *output, const char *channel, const Stats *stats, const Stats *hourly_stats) {
    double n = (double)stats->n;
    double mean_x = stats->n ? stats->sum_x / n : NAN;
    double mean_y = stats->n ? stats->sum_y / n : NAN;
    double mae = stats->n ? stats->sum_abs_error / n : NAN;
    double rmse = stats->n ? sqrt(stats->sum_squared_error / n) : NAN;
    double normalized_mae = mean_x != 0.0 ? 100.0 * mae / fabs(mean_x) : NAN;
    double energy_bias = stats->sum_x != 0.0 ? 100.0 * (stats->sum_y - stats->sum_x) / stats->sum_x : NAN;
    double exact_rate = stats->n ? (double)stats->exact / n : NAN;
    double hourly_mae = hourly_stats->n ? hourly_stats->sum_abs_error / (double)hourly_stats->n : NAN;

    fprintf(output,
            "%s,%" PRIu64 ",%.6f,%.6f,%.6f,%.6f,%.6f,%.9f,%.9f,%.9f,%" PRIu64 ",%.6f,%.9f\n",
            channel, stats->n, mean_x, mean_y, energy_bias, mae, normalized_mae,
            rmse, correlation(stats), exact_rate, hourly_stats->n, hourly_mae, correlation(hourly_stats));
}

int main(int argc, char **argv) {
    if (argc != 4) {
        fprintf(stderr, "Usage: %s POWER_CSV BY_CHANNEL_CSV MAIN_BY_WEEK_CSV\n", argv[0]);
        return 2;
    }

    FILE *input = fopen(argv[1], "r");
    if (!input) {
        fprintf(stderr, "Cannot open %s: %s\n", argv[1], strerror(errno));
        return 1;
    }

    char *line = NULL;
    size_t capacity = 0;
    ssize_t length = getline(&line, &capacity, input);
    if (length < 0) {
        fprintf(stderr, "Input is empty\n");
        fclose(input);
        return 1;
    }
    while (length > 0 && (line[length - 1] == '\n' || line[length - 1] == '\r')) line[--length] = '\0';

    char *header_fields[MAX_COLS];
    int column_count = split_csv_simple(line, header_fields, MAX_COLS);
    int timestamp_column = -1;
    int measurement_columns[MAX_MEASUREMENTS];
    const char *measurement_names[MAX_MEASUREMENTS];
    int measurement_count = 0;

    for (int i = 0; i < column_count; ++i) {
        if (strcmp(header_fields[i], "unix_ts") == 0) timestamp_column = i;
        if (is_measurement(header_fields[i])) {
            if (measurement_count >= MAX_MEASUREMENTS) {
                fprintf(stderr, "Too many measurement columns\n");
                fclose(input);
                free(line);
                return 1;
            }
            measurement_columns[measurement_count] = i;
            measurement_names[measurement_count] = strdup(header_fields[i]);
            ++measurement_count;
        }
    }

    if (timestamp_column < 0 || measurement_count == 0 || measurement_count > 31) {
        fprintf(stderr, "Unexpected CSV schema\n");
        fclose(input);
        free(line);
        return 1;
    }

    int main_measurement = -1;
    for (int i = 0; i < measurement_count; ++i) {
        if (strcmp(measurement_names[i], "main") == 0) main_measurement = i;
    }
    if (main_measurement < 0) {
        fprintf(stderr, "No main measurement column\n");
        fclose(input);
        free(line);
        return 1;
    }

    for (int r = 0; r < RANGE_COUNT; ++r) {
        ranges[r].values = calloc((size_t)WEEK_SECONDS * (size_t)measurement_count, sizeof(int32_t));
        ranges[r].valid_masks = calloc(WEEK_SECONDS, sizeof(uint32_t));
        if (!ranges[r].values || !ranges[r].valid_masks) {
            fprintf(stderr, "Memory allocation failed for range %d\n", r);
            fclose(input);
            free(line);
            return 1;
        }
    }

    Stats overall[MAX_MEASUREMENTS] = {{0}};
    Stats by_range[RANGE_COUNT][MAX_MEASUREMENTS] = {{{0}}};
    HourBin hourly_bins[RANGE_COUNT][HOURS_PER_WEEK][MAX_MEASUREMENTS] = {{{{0}}}};
    uint64_t rows_read = 0;
    uint64_t source_rows_stored = 0;
    uint64_t donor_rows_matched = 0;

    while ((length = getline(&line, &capacity, input)) >= 0) {
        ++rows_read;
        while (length > 0 && (line[length - 1] == '\n' || line[length - 1] == '\r')) line[--length] = '\0';
        char *fields[MAX_COLS] = {0};
        int fields_read = split_csv_simple(line, fields, MAX_COLS);
        if (fields_read != column_count) continue;

        int64_t timestamp;
        if (!parse_int64(fields[timestamp_column], &timestamp)) continue;

        int source_range = find_range(timestamp);
        if (source_range >= 0) {
            size_t row_index = (size_t)(timestamp - ranges[source_range].start_ts);
            uint32_t mask = 0;
            for (int m = 0; m < measurement_count; ++m) {
                int32_t value;
                if (parse_int32(fields[measurement_columns[m]], &value)) {
                    ranges[source_range].values[row_index * (size_t)measurement_count + (size_t)m] = value;
                    mask |= (uint32_t)1U << m;
                }
            }
            ranges[source_range].valid_masks[row_index] = mask;
            ++source_rows_stored;
            continue;
        }

        int64_t source_timestamp = timestamp - YEAR_SHIFT_SECONDS;
        int donor_range = find_range(source_timestamp);
        if (donor_range >= 0) {
            size_t row_index = (size_t)(source_timestamp - ranges[donor_range].start_ts);
            uint32_t source_mask = ranges[donor_range].valid_masks[row_index];
            int hour_index = (int)(row_index / 3600U);
            ++donor_rows_matched;

            for (int m = 0; m < measurement_count; ++m) {
                int32_t donor_value;
                uint32_t bit = (uint32_t)1U << m;
                if ((source_mask & bit) == 0 || !parse_int32(fields[measurement_columns[m]], &donor_value)) continue;
                int32_t source_value = ranges[donor_range].values[row_index * (size_t)measurement_count + (size_t)m];
                update_stats(&overall[m], (double)source_value, (double)donor_value);
                update_stats(&by_range[donor_range][m], (double)source_value, (double)donor_value);
                HourBin *bin = &hourly_bins[donor_range][hour_index][m];
                bin->sum_x += (double)source_value;
                bin->sum_y += (double)donor_value;
                ++bin->n;
            }
        }

        if (rows_read % 10000000ULL == 0) {
            fprintf(stdout, "Processed %" PRIu64 " rows\n", rows_read);
            fflush(stdout);
        }
    }

    fclose(input);
    free(line);

    Stats hourly_overall[MAX_MEASUREMENTS] = {{0}};
    for (int r = 0; r < RANGE_COUNT; ++r) {
        for (int h = 0; h < HOURS_PER_WEEK; ++h) {
            for (int m = 0; m < measurement_count; ++m) {
                HourBin *bin = &hourly_bins[r][h][m];
                if (bin->n > 0) {
                    update_stats(&hourly_overall[m], bin->sum_x / (double)bin->n, bin->sum_y / (double)bin->n);
                }
            }
        }
    }

    FILE *by_channel = fopen(argv[2], "w");
    FILE *main_by_week = fopen(argv[3], "w");
    if (!by_channel || !main_by_week) {
        fprintf(stderr, "Cannot create output files\n");
        if (by_channel) fclose(by_channel);
        if (main_by_week) fclose(main_by_week);
        return 1;
    }

    fprintf(by_channel,
            "channel,paired_seconds,mean_2018_w,mean_2019_donor_w,energy_bias_pct,mae_w,normalized_mae_pct,rmse_w,correlation_1hz,exact_match_rate_1hz,paired_hours,hourly_mean_mae_w,hourly_mean_correlation\n");
    for (int m = 0; m < measurement_count; ++m) {
        print_metric_row(by_channel, measurement_names[m], &overall[m], &hourly_overall[m]);
    }

    fprintf(main_by_week,
            "target_week,donor_week,paired_seconds,mean_target_w,mean_donor_w,energy_bias_pct,mae_w,normalized_mae_pct,rmse_w,correlation_1hz,exact_match_rate\n");
    for (int r = 0; r < RANGE_COUNT; ++r) {
        Stats *stats = &by_range[r][main_measurement];
        double n = (double)stats->n;
        double mean_x = stats->n ? stats->sum_x / n : NAN;
        double mean_y = stats->n ? stats->sum_y / n : NAN;
        double mae = stats->n ? stats->sum_abs_error / n : NAN;
        double normalized_mae = mean_x != 0.0 ? 100.0 * mae / fabs(mean_x) : NAN;
        double bias = stats->sum_x != 0.0 ? 100.0 * (stats->sum_y - stats->sum_x) / stats->sum_x : NAN;
        double rmse = stats->n ? sqrt(stats->sum_squared_error / n) : NAN;
        double exact_rate = stats->n ? (double)stats->exact / n : NAN;
        fprintf(main_by_week, "%s,%s,%" PRIu64 ",%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.9f,%.9f\n",
                ranges[r].target_label, ranges[r].donor_label, stats->n, mean_x, mean_y, bias, mae,
                normalized_mae, rmse, correlation(stats), exact_rate);
    }

    fclose(by_channel);
    fclose(main_by_week);

    for (int r = 0; r < RANGE_COUNT; ++r) {
        free(ranges[r].values);
        free(ranges[r].valid_masks);
    }
    for (int m = 0; m < measurement_count; ++m) free((void *)measurement_names[m]);

    fprintf(stdout, "Stored %" PRIu64 " source rows and matched %" PRIu64 " donor rows across %d validation weeks.\n",
            source_rows_stored, donor_rows_matched, RANGE_COUNT);
    return 0;
}
