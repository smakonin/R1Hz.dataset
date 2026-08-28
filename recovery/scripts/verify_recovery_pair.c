#define _POSIX_C_SOURCE 200809L

#include <ctype.h>
#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_COLS 64

typedef struct {
    int64_t start;
    int64_t end;
} Interval;

static const Interval common_intervals[] = {
    {1528482113LL, 1528598134LL},
    {1559381554LL, 1559398792LL},
};

static const Interval isolated_intervals[] = {
    {1528598292LL, 1528598292LL},
    {1559399189LL, 1559399191LL},
    {1559399207LL, 1559399215LL},
};

static int split_csv_simple(char *line, char **fields, int max_fields) {
    int count = 0;
    fields[count++] = line;
    for (char *p = line; *p && count < max_fields; ++p) {
        if (*p == ',') {
            *p = '\0';
            fields[count++] = p + 1;
        }
    }
    return count;
}

static void trim_line_end(char *line) {
    size_t length = strlen(line);
    while (length > 0 && (line[length - 1] == '\n' || line[length - 1] == '\r')) line[--length] = '\0';
}

static int is_blank(const char *value) {
    while (value && *value) {
        if (!isspace((unsigned char)*value)) return 0;
        ++value;
    }
    return 1;
}

static int in_intervals(int64_t timestamp, const Interval *intervals, size_t count) {
    for (size_t i = 0; i < count; ++i) {
        if (timestamp >= intervals[i].start && timestamp <= intervals[i].end) return 1;
    }
    return 0;
}

static int64_t parse_timestamp(const char *line, int *ok) {
    char *end = NULL;
    errno = 0;
    long long value = strtoll(line, &end, 10);
    *ok = errno == 0 && end != line && *end == ',';
    return (int64_t)value;
}

int main(int argc, char **argv) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s ORIGINAL_CSV RECOVERED_CSV\n", argv[0]);
        return 2;
    }

    FILE *original = fopen(argv[1], "r");
    FILE *recovered = fopen(argv[2], "r");
    if (!original || !recovered) {
        fprintf(stderr, "Cannot open comparison files\n");
        return 1;
    }

    char *original_line = NULL;
    char *recovered_line = NULL;
    size_t original_capacity = 0;
    size_t recovered_capacity = 0;
    ssize_t original_length = getline(&original_line, &original_capacity, original);
    ssize_t recovered_length = getline(&recovered_line, &recovered_capacity, recovered);
    if (original_length < 0 || recovered_length < 0 || strcmp(original_line, recovered_line) != 0) {
        fprintf(stderr, "Header mismatch\n");
        return 1;
    }

    char *header = strdup(original_line);
    trim_line_end(header);
    char *header_fields[MAX_COLS] = {0};
    int column_count = split_csv_simple(header, header_fields, MAX_COLS);
    int marker_column = -1;
    int measurement_start = -1;
    for (int i = 0; i < column_count; ++i) {
        if (strcmp(header_fields[i], "marker") == 0) marker_column = i;
        if (strcmp(header_fields[i], "main") == 0) measurement_start = i;
    }
    if (marker_column < 0 || measurement_start < 0) {
        fprintf(stderr, "Schema mismatch\n");
        return 1;
    }

    int allow_isolated = strstr(argv[1], "power.csv") != NULL || strstr(argv[1], "reactive.csv") != NULL;
    uint64_t rows = 0;
    uint64_t synthesized_rows = 0;
    uint64_t filled_cells = 0;
    uint64_t preserved_cells = 0;

    while (1) {
        original_length = getline(&original_line, &original_capacity, original);
        recovered_length = getline(&recovered_line, &recovered_capacity, recovered);
        if (original_length < 0 || recovered_length < 0) break;
        ++rows;

        int ok_original = 0;
        int ok_recovered = 0;
        int64_t original_timestamp = parse_timestamp(original_line, &ok_original);
        int64_t recovered_timestamp = parse_timestamp(recovered_line, &ok_recovered);
        if (!ok_original || !ok_recovered || original_timestamp != recovered_timestamp) {
            fprintf(stderr, "Timestamp mismatch at row %" PRIu64 "\n", rows + 1);
            return 1;
        }

        int should_be_synthetic =
            in_intervals(original_timestamp, common_intervals, sizeof(common_intervals) / sizeof(common_intervals[0])) ||
            (allow_isolated && in_intervals(original_timestamp, isolated_intervals, sizeof(isolated_intervals) / sizeof(isolated_intervals[0])));

        if (!should_be_synthetic) {
            if (strcmp(original_line, recovered_line) != 0) {
                fprintf(stderr, "Unexpected change outside recovery intervals at timestamp %" PRId64 "\n", original_timestamp);
                return 1;
            }
            continue;
        }

        char *original_copy = strdup(original_line);
        char *recovered_copy = strdup(recovered_line);
        trim_line_end(original_copy);
        trim_line_end(recovered_copy);
        char *original_fields[MAX_COLS] = {0};
        char *recovered_fields[MAX_COLS] = {0};
        int original_count = split_csv_simple(original_copy, original_fields, MAX_COLS);
        int recovered_count = split_csv_simple(recovered_copy, recovered_fields, MAX_COLS);
        if (original_count != column_count || recovered_count != column_count) {
            fprintf(stderr, "Field-count mismatch at timestamp %" PRId64 "\n", original_timestamp);
            return 1;
        }

        for (int i = 0; i < column_count; ++i) {
            if (i == marker_column) {
                if (!is_blank(original_fields[i]) || strcmp(recovered_fields[i], "s") != 0) {
                    fprintf(stderr, "Marker mismatch at timestamp %" PRId64 "\n", original_timestamp);
                    return 1;
                }
            } else if (i < measurement_start) {
                if (strcmp(original_fields[i], recovered_fields[i]) != 0) {
                    fprintf(stderr, "Metadata changed at timestamp %" PRId64 "\n", original_timestamp);
                    return 1;
                }
            } else if (is_blank(original_fields[i])) {
                if (is_blank(recovered_fields[i])) {
                    fprintf(stderr, "Measurement remains blank at timestamp %" PRId64 "\n", original_timestamp);
                    return 1;
                }
                ++filled_cells;
            } else {
                if (strcmp(original_fields[i], recovered_fields[i]) != 0) {
                    fprintf(stderr, "Measured value changed at timestamp %" PRId64 "\n", original_timestamp);
                    return 1;
                }
                ++preserved_cells;
            }
        }
        ++synthesized_rows;
        free(original_copy);
        free(recovered_copy);
    }

    if (original_length >= 0 || recovered_length >= 0) {
        fprintf(stderr, "File lengths differ\n");
        return 1;
    }

    fclose(original);
    fclose(recovered);
    free(original_line);
    free(recovered_line);
    free(header);

    fprintf(stdout,
            "%s vs %s: verified rows=%" PRIu64 ", synthesized_rows=%" PRIu64 ", filled_cells=%" PRIu64 ", preserved_cells=%" PRIu64 "\n",
            argv[1], argv[2], rows, synthesized_rows, filled_cells, preserved_cells);
    return 0;
}
