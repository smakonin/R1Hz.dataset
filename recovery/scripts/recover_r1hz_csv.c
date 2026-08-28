#define _POSIX_C_SOURCE 200809L

#include <ctype.h>
#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_COLS 64
#define GAP_COUNT 2
#define CANDIDATE_COUNT 13

typedef struct {
    int64_t target_start;
    int64_t target_end;
    int64_t donor_start;
    int64_t donor_end;
    size_t length;
    char **donor_values;
    size_t captured;
} Gap;

typedef struct {
    int64_t timestamp;
    char *values;
} Candidate;

static Gap gaps[GAP_COUNT] = {
    {1528482113LL, 1528598134LL, 1559931713LL, 1560047734LL, 116022U, NULL, 0U},
    {1559381554LL, 1559398792LL, 1527931954LL, 1527949192LL, 17239U, NULL, 0U},
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

static void trim_line_end(char *line) {
    size_t length = strlen(line);
    while (length > 0 && (line[length - 1] == '\n' || line[length - 1] == '\r')) {
        line[--length] = '\0';
    }
}

static int is_blank(const char *value) {
    if (!value) return 1;
    while (*value) {
        if (!isspace((unsigned char)*value)) return 0;
        ++value;
    }
    return 1;
}

static int64_t parse_timestamp(const char *line, int *ok) {
    char *end = NULL;
    errno = 0;
    long long value = strtoll(line, &end, 10);
    *ok = errno == 0 && end != line && *end == ',';
    return (int64_t)value;
}

static const char *field_start(const char *line, int field_index) {
    if (field_index == 0) return line;
    int commas = 0;
    for (const char *p = line; *p; ++p) {
        if (*p == ',') {
            ++commas;
            if (commas == field_index) return p + 1;
        }
    }
    return NULL;
}

static int find_gap_by_donor(int64_t timestamp) {
    for (int i = 0; i < GAP_COUNT; ++i) {
        if (timestamp >= gaps[i].donor_start && timestamp <= gaps[i].donor_end) return i;
    }
    return -1;
}

static int find_gap_by_target(int64_t timestamp) {
    for (int i = 0; i < GAP_COUNT; ++i) {
        if (timestamp >= gaps[i].target_start && timestamp <= gaps[i].target_end) return i;
    }
    return -1;
}

static int validate_value_string(const char *values, int measurement_count) {
    char *copy = strdup(values);
    if (!copy) return 0;
    trim_line_end(copy);
    char *fields[MAX_COLS] = {0};
    int count = split_csv_simple(copy, fields, MAX_COLS);
    int valid = count == measurement_count;
    for (int i = 0; valid && i < count; ++i) {
        if (is_blank(fields[i])) valid = 0;
    }
    free(copy);
    return valid;
}

static int load_candidates(
    const char *path,
    char **measurement_names,
    int measurement_count,
    Candidate *candidates,
    int *candidate_count
) {
    *candidate_count = 0;
    if (strcmp(path, "-") == 0) return 1;

    FILE *input = fopen(path, "r");
    if (!input) {
        fprintf(stderr, "Cannot open candidate file %s: %s\n", path, strerror(errno));
        return 0;
    }

    char *line = NULL;
    size_t capacity = 0;
    ssize_t length = getline(&line, &capacity, input);
    if (length < 0) {
        fprintf(stderr, "Candidate file is empty: %s\n", path);
        fclose(input);
        free(line);
        return 0;
    }
    trim_line_end(line);
    char *header_fields[MAX_COLS] = {0};
    int header_count = split_csv_simple(line, header_fields, MAX_COLS);
    if (header_count != measurement_count + 1 || strcmp(header_fields[0], "unix_ts") != 0) {
        fprintf(stderr, "Candidate schema mismatch: %s\n", path);
        fclose(input);
        free(line);
        return 0;
    }
    for (int i = 0; i < measurement_count; ++i) {
        if (strcmp(header_fields[i + 1], measurement_names[i]) != 0) {
            fprintf(stderr, "Candidate column mismatch at %d: %s vs %s\n", i, header_fields[i + 1], measurement_names[i]);
            fclose(input);
            free(line);
            return 0;
        }
    }

    while ((length = getline(&line, &capacity, input)) >= 0) {
        if (*candidate_count >= CANDIDATE_COUNT) {
            fprintf(stderr, "Too many candidate rows in %s\n", path);
            fclose(input);
            free(line);
            return 0;
        }
        int ok = 0;
        int64_t timestamp = parse_timestamp(line, &ok);
        const char *values = field_start(line, 1);
        if (!ok || !values || !validate_value_string(values, measurement_count)) {
            fprintf(stderr, "Invalid candidate row in %s\n", path);
            fclose(input);
            free(line);
            return 0;
        }
        candidates[*candidate_count].timestamp = timestamp;
        candidates[*candidate_count].values = strdup(values);
        if (!candidates[*candidate_count].values) {
            fclose(input);
            free(line);
            return 0;
        }
        trim_line_end(candidates[*candidate_count].values);
        ++(*candidate_count);
    }

    fclose(input);
    free(line);
    return *candidate_count == CANDIDATE_COUNT;
}

static const char *find_candidate(Candidate *candidates, int candidate_count, int64_t timestamp) {
    for (int i = 0; i < candidate_count; ++i) {
        if (candidates[i].timestamp == timestamp) return candidates[i].values;
    }
    return NULL;
}

static int write_merged_row(
    FILE *output,
    const char *target_line,
    const char *synthetic_values,
    int column_count,
    int marker_column,
    int measurement_start,
    uint64_t *filled_cells,
    uint64_t *preserved_measurement_cells
) {
    char *target_copy = strdup(target_line);
    char *synthetic_copy = strdup(synthetic_values);
    if (!target_copy || !synthetic_copy) {
        free(target_copy);
        free(synthetic_copy);
        return 0;
    }
    trim_line_end(target_copy);
    trim_line_end(synthetic_copy);

    char *target_fields[MAX_COLS] = {0};
    char *synthetic_fields[MAX_COLS] = {0};
    int target_count = split_csv_simple(target_copy, target_fields, MAX_COLS);
    int synthetic_count = split_csv_simple(synthetic_copy, synthetic_fields, MAX_COLS);
    int measurement_count = column_count - measurement_start;
    if (target_count != column_count || synthetic_count != measurement_count) {
        free(target_copy);
        free(synthetic_copy);
        return 0;
    }

    for (int i = 0; i < column_count; ++i) {
        if (i > 0) fputc(',', output);
        if (i == marker_column) {
            fputc('s', output);
        } else if (i >= measurement_start) {
            int measurement_index = i - measurement_start;
            if (is_blank(target_fields[i])) {
                fputs(synthetic_fields[measurement_index], output);
                ++(*filled_cells);
            } else {
                fputs(target_fields[i], output);
                ++(*preserved_measurement_cells);
            }
        } else {
            fputs(target_fields[i], output);
        }
    }
    fputc('\n', output);

    free(target_copy);
    free(synthetic_copy);
    return !ferror(output);
}

int main(int argc, char **argv) {
    if (argc != 4) {
        fprintf(stderr, "Usage: %s INPUT_CSV OUTPUT_CSV CANDIDATE_CSV_OR_DASH\n", argv[0]);
        return 2;
    }

    if (strcmp(argv[1], argv[2]) == 0) {
        fprintf(stderr, "Input and output must differ\n");
        return 2;
    }

    FILE *input = fopen(argv[1], "r");
    if (!input) {
        fprintf(stderr, "Cannot open input %s: %s\n", argv[1], strerror(errno));
        return 1;
    }

    char *line = NULL;
    size_t capacity = 0;
    ssize_t length = getline(&line, &capacity, input);
    if (length < 0) {
        fprintf(stderr, "Input is empty\n");
        fclose(input);
        free(line);
        return 1;
    }
    trim_line_end(line);

    char *header_copy = strdup(line);
    char *header_fields[MAX_COLS] = {0};
    int column_count = split_csv_simple(header_copy, header_fields, MAX_COLS);
    int marker_column = -1;
    int measurement_start = -1;
    char *measurement_names[MAX_COLS] = {0};

    for (int i = 0; i < column_count; ++i) {
        if (strcmp(header_fields[i], "marker") == 0) marker_column = i;
        if (strcmp(header_fields[i], "main") == 0) measurement_start = i;
    }
    if (marker_column < 0 || measurement_start < 0) {
        fprintf(stderr, "Required marker/main columns not found\n");
        fclose(input);
        free(line);
        free(header_copy);
        return 1;
    }

    int measurement_count = column_count - measurement_start;
    for (int i = 0; i < measurement_count; ++i) {
        measurement_names[i] = strdup(header_fields[measurement_start + i]);
    }
    free(header_copy);

    for (int i = 0; i < GAP_COUNT; ++i) {
        gaps[i].donor_values = calloc(gaps[i].length, sizeof(char *));
        if (!gaps[i].donor_values) {
            fprintf(stderr, "Unable to allocate donor index\n");
            fclose(input);
            free(line);
            return 1;
        }
    }

    Candidate candidates[CANDIDATE_COUNT] = {{0}};
    int candidate_count = 0;
    if (!load_candidates(argv[3], measurement_names, measurement_count, candidates, &candidate_count)) {
        fprintf(stderr, "Unable to load all candidate estimates from %s\n", argv[3]);
        fclose(input);
        free(line);
        return 1;
    }

    uint64_t rows_scanned = 0;
    while ((length = getline(&line, &capacity, input)) >= 0) {
        ++rows_scanned;
        int ok = 0;
        int64_t timestamp = parse_timestamp(line, &ok);
        if (!ok) continue;
        int gap_index = find_gap_by_donor(timestamp);
        if (gap_index >= 0) {
            size_t offset = (size_t)(timestamp - gaps[gap_index].donor_start);
            const char *values = field_start(line, measurement_start);
            if (!values || !validate_value_string(values, measurement_count) || gaps[gap_index].donor_values[offset]) {
                fprintf(stderr, "Invalid or duplicate donor row at %" PRId64 "\n", timestamp);
                fclose(input);
                free(line);
                return 1;
            }
            gaps[gap_index].donor_values[offset] = strdup(values);
            if (!gaps[gap_index].donor_values[offset]) {
                fclose(input);
                free(line);
                return 1;
            }
            trim_line_end(gaps[gap_index].donor_values[offset]);
            ++gaps[gap_index].captured;
        }
        if (rows_scanned % 20000000ULL == 0) {
            fprintf(stdout, "%s: indexed donors through %" PRIu64 " rows\n", argv[1], rows_scanned);
            fflush(stdout);
        }
    }

    for (int i = 0; i < GAP_COUNT; ++i) {
        if (gaps[i].captured != gaps[i].length) {
            fprintf(stderr, "Captured %zu of %zu donor rows for gap %d\n", gaps[i].captured, gaps[i].length, i);
            fclose(input);
            free(line);
            return 1;
        }
    }

    if (fseek(input, 0, SEEK_SET) != 0) {
        fprintf(stderr, "Unable to rewind input\n");
        fclose(input);
        free(line);
        return 1;
    }

    FILE *output = fopen(argv[2], "wx");
    if (!output) {
        fprintf(stderr, "Cannot create output %s: %s\n", argv[2], strerror(errno));
        fclose(input);
        free(line);
        return 1;
    }

    uint64_t output_rows = 0;
    uint64_t marked_rows = 0;
    uint64_t filled_cells = 0;
    uint64_t preserved_measurement_cells = 0;
    length = getline(&line, &capacity, input);
    if (length < 0 || fputs(line, output) == EOF) {
        fprintf(stderr, "Unable to write header\n");
        fclose(input);
        fclose(output);
        free(line);
        return 1;
    }

    while ((length = getline(&line, &capacity, input)) >= 0) {
        ++output_rows;
        int ok = 0;
        int64_t timestamp = parse_timestamp(line, &ok);
        if (!ok) {
            fprintf(stderr, "Invalid timestamp at output row %" PRIu64 "\n", output_rows + 1);
            fclose(input);
            fclose(output);
            free(line);
            return 1;
        }

        const char *synthetic_values = NULL;
        int target_gap = find_gap_by_target(timestamp);
        if (target_gap >= 0) {
            size_t offset = (size_t)(timestamp - gaps[target_gap].target_start);
            synthetic_values = gaps[target_gap].donor_values[offset];
        } else {
            synthetic_values = find_candidate(candidates, candidate_count, timestamp);
        }

        if (synthetic_values) {
            if (!write_merged_row(
                    output,
                    line,
                    synthetic_values,
                    column_count,
                    marker_column,
                    measurement_start,
                    &filled_cells,
                    &preserved_measurement_cells)) {
                fprintf(stderr, "Unable to synthesize row at %" PRId64 "\n", timestamp);
                fclose(input);
                fclose(output);
                free(line);
                return 1;
            }
            ++marked_rows;
        } else if (fputs(line, output) == EOF) {
            fprintf(stderr, "Write failed at row %" PRIu64 "\n", output_rows + 1);
            fclose(input);
            fclose(output);
            free(line);
            return 1;
        }

        if (output_rows % 10000000ULL == 0) {
            fprintf(stdout, "%s: wrote %" PRIu64 " rows\n", argv[2], output_rows);
            fflush(stdout);
        }
    }

    int close_error = fclose(output);
    fclose(input);
    free(line);

    for (int i = 0; i < GAP_COUNT; ++i) {
        for (size_t j = 0; j < gaps[i].length; ++j) free(gaps[i].donor_values[j]);
        free(gaps[i].donor_values);
    }
    for (int i = 0; i < candidate_count; ++i) free(candidates[i].values);
    for (int i = 0; i < measurement_count; ++i) free(measurement_names[i]);

    if (close_error != 0) {
        fprintf(stderr, "Failed to finalize output %s\n", argv[2]);
        return 1;
    }

    fprintf(stdout,
            "%s: complete; rows=%" PRIu64 ", marked=%" PRIu64 ", filled_cells=%" PRIu64 ", preserved_measurement_cells=%" PRIu64 "\n",
            argv[2], output_rows, marked_rows, filled_cells, preserved_measurement_cells);
    return 0;
}
