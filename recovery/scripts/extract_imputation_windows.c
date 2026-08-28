#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int64_t start;
    int64_t end;
} Window;

static const Window auxiliary_windows[] = {
    {1528597692LL, 1528598892LL},
    {1559398589LL, 1559399815LL},
};

static const Window common_gaps[] = {
    {1528482113LL, 1528598134LL},
    {1559381554LL, 1559398792LL},
};

static int in_windows(int64_t timestamp, const Window *windows, size_t count) {
    for (size_t i = 0; i < count; ++i) {
        if (timestamp >= windows[i].start && timestamp <= windows[i].end) return 1;
    }
    return 0;
}

static int extract_field(const char *line, int field_index, char *output, size_t output_size) {
    int current_field = 0;
    const char *start = line;
    for (const char *p = line;; ++p) {
        if (*p == ',' || *p == '\0') {
            if (current_field == field_index) {
                size_t length = (size_t)(p - start);
                if (length >= output_size) length = output_size - 1;
                memcpy(output, start, length);
                output[length] = '\0';
                return 1;
            }
            if (*p == '\0') return 0;
            ++current_field;
            start = p + 1;
        }
    }
}

int main(int argc, char **argv) {
    if (argc != 4) {
        fprintf(stderr, "Usage: %s INPUT_CSV WINDOW_OUTPUT_CSV IHD_OUTPUT_CSV_OR_DASH\n", argv[0]);
        return 2;
    }

    FILE *input = fopen(argv[1], "r");
    FILE *window_output = fopen(argv[2], "w");
    FILE *ihd_output = strcmp(argv[3], "-") == 0 ? NULL : fopen(argv[3], "w");
    if (!input || !window_output || (strcmp(argv[3], "-") != 0 && !ihd_output)) {
        fprintf(stderr, "Unable to open input or output: %s\n", strerror(errno));
        if (input) fclose(input);
        if (window_output) fclose(window_output);
        if (ihd_output) fclose(ihd_output);
        return 1;
    }

    char *line = NULL;
    size_t capacity = 0;
    ssize_t length = getline(&line, &capacity, input);
    if (length < 0) {
        fprintf(stderr, "Input is empty\n");
        fclose(input);
        fclose(window_output);
        if (ihd_output) fclose(ihd_output);
        free(line);
        return 1;
    }

    fputs(line, window_output);
    int has_ihd = strstr(line, ",ihd,") != NULL;
    if (ihd_output) fputs("unix_ts,ihd\n", ihd_output);

    uint64_t window_rows = 0;
    uint64_t gap_ihd_rows = 0;
    while ((length = getline(&line, &capacity, input)) >= 0) {
        char *end = NULL;
        errno = 0;
        long long timestamp_value = strtoll(line, &end, 10);
        if (errno != 0 || end == line || *end != ',') continue;
        int64_t timestamp = (int64_t)timestamp_value;

        if (in_windows(timestamp, auxiliary_windows, sizeof(auxiliary_windows) / sizeof(auxiliary_windows[0]))) {
            fputs(line, window_output);
            ++window_rows;
        }

        if (ihd_output && has_ihd &&
            in_windows(timestamp, common_gaps, sizeof(common_gaps) / sizeof(common_gaps[0]))) {
            char ihd[128];
            if (extract_field(line, 4, ihd, sizeof(ihd)) && ihd[0] != '\0') {
                fprintf(ihd_output, "%" PRId64 ",%s\n", timestamp, ihd);
                ++gap_ihd_rows;
            }
        }
    }

    fclose(input);
    fclose(window_output);
    if (ihd_output) fclose(ihd_output);
    free(line);

    fprintf(stdout, "%s: extracted %" PRIu64 " auxiliary rows and %" PRIu64 " in-gap IHD readings\n",
            argv[1], window_rows, gap_ihd_rows);
    return 0;
}
