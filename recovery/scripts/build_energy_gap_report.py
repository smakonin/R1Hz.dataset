#!/usr/bin/env python3
"""Build the canonical portable-report artifact from reviewed audit outputs."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "analysis" / "energy_gap_report"


def records(name: str) -> list[dict]:
    frame = pd.read_csv(OUT / name)
    return json.loads(frame.to_json(orient="records"))


def main() -> None:
    query_text = (OUT / "report_queries.sql").read_text()
    analysis_source = {
        "id": "energy_gap_analysis",
        "label": "Reviewed energy-gap audit evidence",
        "path": "analysis/energy_gap_report/report_queries.sql",
        "query": {
            "engine": "SQLite",
            "language": "SQL",
            "sql": query_text,
            "description": "Selects the reviewed continuity, gap-propagation, recovery-route, and validation evidence used in this report.",
            "tables_used": [
                "headline_metrics",
                "quality_by_grain",
                "recovery_routes",
                "validation_evidence",
                "continuity_summary",
                "monthly_impact",
            ],
            "filters": [
                "Dataset coverage from 2017-09-13 through 2019-10-09",
                "IHD direct validation requires at least 440 samples per source hour",
                "Circuit aggregation validation uses the first seven complete days after the opening boundary",
            ],
            "metric_definitions": [
                "Explicit blank cells count null energy measurements in the source file.",
                "Quality-affected cells include present daily/monthly totals that inherited skipped lower-grain blanks.",
                "Absolute-error metrics are expressed in Wh per reconstructed hourly value.",
            ],
        },
    }
    raw_sources = [
        {"id": "energy_hourly", "label": "energy_hourly.csv", "path": "energy_hourly.csv"},
        {"id": "energy_daily", "label": "energy_daily.csv", "path": "energy_daily.csv"},
        {"id": "energy_monthly", "label": "energy_monthly.csv", "path": "energy_monthly.csv"},
        {"id": "utility_source", "label": "utility.csv", "path": "utility.csv"},
        {"id": "ihd_source", "label": "ihd.csv", "path": "ihd.csv"},
        {"id": "power_source", "label": "power.csv", "path": "power.csv"},
        {"id": "recovered_power", "label": "Recovered 1 Hz power", "path": "recovered/power.csv"},
    ]
    sources = [analysis_source, *raw_sources]

    technical_summary = """## Technical Summary

All expected hourly, daily, and monthly period rows are present. The defect is in the measurements: **895 hourly energy cells are blank**—135 utility cells and 760 circuit cells. Of the circuit blanks, 741 belong to two internal acquisition outages and 19 are the opening coverage boundary, where the preceding hour is outside the 1 Hz dataset.

Only three daily cells and no monthly cells are explicitly blank, but that understates the damage. The daily and monthly files were built by skipping lower-grain blanks: **48 daily rows and 21 monthly rows contain at least one affected energy value**. Their existing totals cannot be used as independent constraints.

Recovery is feasible for the 741 outage-related circuit cells and all 135 utility hours, with different confidence levels. The 19 opening-boundary circuit cells should normally remain blank because any value would be a pure estimate rather than a reconstruction."""

    key_findings = """## Key Findings

- **The time axes are complete.** There are 18,168 consecutive hourly rows, 757 consecutive daily rows, and 26 consecutive monthly rows, with no duplicate timestamps at these grains.
- **Blank propagation is hidden.** Every comparable daily value exactly equals the sum of its hourly labels with blanks skipped; every comparable monthly value exactly equals the corresponding daily sum. A present aggregate therefore does not prove full coverage.
- **Circuit recovery is technically straightforward.** Aggregating clean 1 Hz power reproduced 3,192 hourly circuit cells with 0.263 Wh mean absolute error and a 1 Wh 95th-percentile error. The dominant uncertainty is the donor-based reconstruction of the missing seconds, not the hourly aggregation.
- **Utility recovery has a strong hierarchy.** Ninety gap hours have near-complete independent IHD coverage; 14 have partial IHD coverage; 31 have none. The complete `main` channel provides a strong fallback for the latter two groups.
- **Opposite-year utility copying should be only a sensitivity check.** A 364-day donor produced 220 Wh mean absolute error, versus 1.77 Wh for well-covered IHD hours and 1.18 Wh for the cross-validated, 10 Wh-rounded utility-to-main model."""

    scope = """## Scope, Data, and Definitions

The audit covers `energy_hourly.csv`, `energy_daily.csv`, and `energy_monthly.csv`, plus `utility.csv`, `ihd.csv`, `power.csv`, and the previously recovered 1 Hz power file as candidate recovery sources. The aggregate files contain one utility measure and 19 circuit measures.

A **period gap** is a missing timestamp row. A **measurement gap** is a blank energy cell in an existing row. A **quality-affected aggregate** is a present daily or monthly cell whose source period includes a lower-grain blank. Zero is treated as a valid measurement, not a gap.

The hourly label at time T corresponds to the preceding 1 Hz source hour. The first circuit row is therefore a coverage boundary. The first monthly record begins on 2017-09-13 and the final monthly record covers only the available October 2019 dates; these are partial periods by design."""

    methodology = """## Methodology

1. Checked Unix-time continuity, local-date continuity, duplicate timestamps, spans, and markers at each aggregate grain.
2. Counted blank cells and grouped consecutive hourly gaps into intervals.
3. Propagated hourly gap flags to daily and monthly labels, then reconciled every comparable aggregate cell against its lower-grain sum.
4. Tested circuit reconstruction by aggregating a deterministic seven-day clean sample from the 1 Hz power stream.
5. Tested utility reconstruction from IHD hourly means, from a month-local 10-fold `utility ~ main` regression, and from a 364-day donor benchmark.
6. Classified each target by the best available evidence and retained exact interval and affected-period tables in the report folder.

This phase is an audit and feasibility assessment only. It does not alter the three source CSV files."""

    limitations = """## Limitations, Uncertainty, and Robustness

- The recovered 1 Hz circuit samples inside the two long acquisition outages are synthetic and marked `s`. Hourly circuit energy derived from them should remain marked synthetic even though the aggregation itself is accurate.
- The IHD threshold of 440 samples per hour identifies near-complete hours relative to the normal cadence of about 450 samples. Partial-IHD hours should use the main-channel model as the primary estimate and IHD only as a check.
- The rounded utility-to-main model is highly accurate for typical held-out hours but has rare large errors (maximum 350 Wh in validation). Every filled row therefore needs method metadata and an uncertainty flag; mean error alone is not sufficient.
- Daily and monthly totals do not provide external conservation constraints because they inherited skip-null aggregation.
- The opening circuit hour cannot be reconstructed from preceding 1 Hz readings because those readings are outside the dataset. Filling it would require an explicitly labeled low-confidence estimate."""

    next_steps = """## Recommended Next Steps

1. Create separate recovered copies of the three energy files; keep the originals unchanged.
2. In the hourly copy, fill the 741 outage-related circuit cells by aggregating `recovered/power.csv` over each preceding source hour. Leave the 19 opening-boundary cells blank unless a low-confidence estimate is explicitly wanted.
3. Fill 90 utility hours from well-covered IHD means rounded to the meter's 10 Wh increment. Fill the remaining 45 with a month-local utility-to-main calibration, using partial IHD as a consistency check where available.
4. Put `s` in the hourly `marker` field for every row containing a reconstructed value and retain a sidecar method log distinguishing `ihd`, `main_model`, and `recovered_1hz`.
5. Rebuild daily and monthly values from the repaired hourly file using the dataset's existing label grouping. Do not update only the visibly blank aggregate cells: present partial totals must also be replaced. Mark an aggregate row `s` whenever it includes any reconstructed hourly input.
6. Verify unchanged row counts and timestamps, exact equality of unaffected values, complete re-aggregation, marker propagation, and no edits to raw files."""

    questions = """## Further Questions

- Should the 19 opening-boundary circuit cells remain blank, or should they receive clearly labeled low-confidence estimates?
- Do you want a compact sidecar audit CSV with the method, donor/source coverage, validation class, and uncertainty for every filled cell?
- Should the repaired daily/monthly files preserve the original label-based grouping exactly, or should a second calendar-interval version also be produced for easier downstream interpretation?"""

    manifest = {
        "version": 1,
        "surface": "report",
        "title": "Energy Aggregate Gap Recovery Feasibility",
        "description": "Technical audit of gaps and recovery options in the R1Hz hourly, daily, and monthly energy aggregates.",
        "generatedAt": "2026-08-28T00:00:00-07:00",
        "filters": [],
        "sources": sources,
        "cards": [
            {
                "id": "hourly_blanks",
                "description": "Null energy measurements in existing hourly rows.",
                "dataset": "headline_metrics",
                "sourceId": "energy_gap_analysis",
                "metrics": [{"label": "Hourly blank cells", "field": "hourly_blank_cells", "format": "number"}],
            },
            {
                "id": "circuit_recoverable",
                "description": "Circuit cells inside the two internal acquisition outages; excludes the opening boundary.",
                "dataset": "headline_metrics",
                "sourceId": "energy_gap_analysis",
                "metrics": [{"label": "Circuit cells recoverable", "field": "recoverable_circuit_cells", "format": "number"}],
            },
            {
                "id": "utility_gaps",
                "description": "Hourly utility labels requiring direct or model-based recovery.",
                "dataset": "headline_metrics",
                "sourceId": "energy_gap_analysis",
                "metrics": [{"label": "Utility gap hours", "field": "utility_gap_hours", "format": "number"}],
            },
            {
                "id": "monthly_affected",
                "description": "Monthly rows inheriting at least one lower-grain gap.",
                "dataset": "headline_metrics",
                "sourceId": "energy_gap_analysis",
                "metrics": [{"label": "Affected monthly rows", "field": "inherited_monthly_rows", "format": "number"}],
            },
        ],
        "charts": [
            {
                "id": "quality_propagation_chart",
                "title": "Quality-affected energy cells by grain",
                "subtitle": "Daily and monthly impact is larger than their visible blank counts imply.",
                "type": "bar",
                "dataset": "quality_by_grain",
                "sourceId": "energy_gap_analysis",
                "encodings": {
                    "x": {"field": "grain", "type": "ordinal", "label": "Aggregate grain"},
                    "y": {"field": "quality_affected_cells", "type": "quantitative", "label": "Affected energy cells", "unit": "cells"},
                    "tooltip": [
                        {"field": "explicit_blank_cells", "type": "quantitative", "label": "Explicit blanks"},
                        {"field": "affected_period_rows", "type": "quantitative", "label": "Affected rows"},
                        {"field": "period_rows", "type": "quantitative", "label": "Total period rows"},
                    ],
                },
                "xAxisTitle": "Aggregate grain",
                "yAxisTitle": "Quality-affected energy cells",
                "unit": "cells",
            }
        ],
        "tables": [
            {
                "id": "quality_by_grain_table",
                "title": "Visible blanks versus inherited quality impact",
                "subtitle": "Quality-affected cells include present aggregates built from incomplete lower-grain inputs.",
                "dataset": "quality_by_grain",
                "sourceId": "energy_gap_analysis",
                "density": "compact",
                "defaultSort": {"field": "quality_affected_cells", "direction": "desc"},
                "columns": [
                    {"field": "grain", "label": "Grain", "type": "text"},
                    {"field": "period_rows", "label": "Period rows", "type": "number", "format": "number"},
                    {"field": "explicit_blank_cells", "label": "Explicit blank cells", "type": "number", "format": "number"},
                    {"field": "quality_affected_cells", "label": "Quality-affected cells", "type": "number", "format": "number"},
                    {"field": "affected_period_rows", "label": "Affected period rows", "type": "number", "format": "number"},
                ],
            },
            {
                "id": "recovery_routes_table",
                "title": "Recommended recovery routes",
                "subtitle": "The opening boundary is separated from true internal gaps.",
                "dataset": "recovery_routes",
                "sourceId": "energy_gap_analysis",
                "density": "comfortable",
                "defaultSort": {"field": "affected_cells", "direction": "desc"},
                "columns": [
                    {"field": "target", "label": "Target", "type": "text"},
                    {"field": "gap_hour_labels", "label": "Gap hours", "type": "number", "format": "number"},
                    {"field": "affected_cells", "label": "Affected cells", "type": "number", "format": "number"},
                    {"field": "recommended_method", "label": "Recommended method", "type": "text"},
                    {"field": "confidence", "label": "Confidence", "type": "text"},
                    {"field": "reason", "label": "Rationale", "type": "text"},
                ],
            },
            {
                "id": "validation_table",
                "title": "Recovery-method validation",
                "subtitle": "Errors are per reconstructed hourly value; the donor benchmark is intentionally included as a caution.",
                "dataset": "validation_evidence",
                "sourceId": "energy_gap_analysis",
                "density": "compact",
                "defaultSort": {"field": "mae_wh", "direction": "asc"},
                "columns": [
                    {"field": "method", "label": "Method", "type": "text"},
                    {"field": "target", "label": "Validation target", "type": "text"},
                    {"field": "validation_n", "label": "N", "type": "number", "format": "number"},
                    {"field": "mae_wh", "label": "MAE (Wh)", "type": "number", "format": "number", "unit": "Wh"},
                    {"field": "p95_abs_error_wh", "label": "P95 abs. error (Wh)", "type": "number", "format": "number", "unit": "Wh"},
                    {"field": "max_abs_error_wh", "label": "Max abs. error (Wh)", "type": "number", "format": "number", "unit": "Wh"},
                    {"field": "exact_rate_pct", "label": "Exact rate", "type": "number", "format": "number", "unit": "%"},
                ],
            },
        ],
        "blocks": [
            {"id": "title", "type": "markdown", "body": "# Energy Aggregate Gap Recovery Feasibility"},
            {"id": "technical_summary", "type": "markdown", "body": technical_summary, "sourceId": "energy_gap_analysis"},
            {"id": "headline_metrics", "type": "metric-strip", "cardIds": ["hourly_blanks", "circuit_recoverable", "utility_gaps", "monthly_affected"]},
            {"id": "key_findings", "type": "markdown", "body": key_findings, "sourceId": "energy_gap_analysis"},
            {"id": "quality_chart", "type": "chart", "chartId": "quality_propagation_chart"},
            {"id": "quality_table", "type": "table", "tableId": "quality_by_grain_table"},
            {"id": "scope", "type": "markdown", "body": scope, "sourceId": "energy_gap_analysis"},
            {"id": "methodology", "type": "markdown", "body": methodology, "sourceId": "energy_gap_analysis"},
            {"id": "recovery_routes", "type": "table", "tableId": "recovery_routes_table"},
            {"id": "limitations", "type": "markdown", "body": limitations, "sourceId": "energy_gap_analysis"},
            {"id": "validation", "type": "table", "tableId": "validation_table"},
            {"id": "next_steps", "type": "markdown", "body": next_steps, "sourceId": "energy_gap_analysis"},
            {"id": "questions", "type": "markdown", "body": questions},
        ],
    }

    artifact = {
        "surface": "report",
        "manifest": manifest,
        "snapshot": {
            "version": 1,
            "generatedAt": "2026-08-28T00:00:00-07:00",
            "status": "ready",
            "datasets": {
                "headline_metrics": records("quality_by_grain.csv")[:0] + [json.loads((OUT / "analysis_summary.json").read_text())],
                "quality_by_grain": records("quality_by_grain.csv"),
                "recovery_routes": records("recommended_recovery_routes.csv"),
                "validation_evidence": records("method_validation.csv"),
                "continuity_summary": records("continuity_summary.csv"),
                "monthly_impact": records("monthly_quality_impact.csv"),
            },
            "accessIssues": [],
        },
        "sources": sources,
        "package_info": {"report_kind": "technical", "data_state": "reviewed_snapshot"},
    }

    # The metric-card dataset must use the exact field names expected by the
    # cards.  It is deliberately rebuilt here from the compact summary.
    summary = artifact["snapshot"]["datasets"]["headline_metrics"][0]
    artifact["snapshot"]["datasets"]["headline_metrics"] = [
        {
            "hourly_blank_cells": summary["hourly_blank_cells"],
            "recoverable_circuit_cells": summary["hourly_circuit_gap_hours"] * 19,
            "utility_gap_hours": summary["hourly_utility_blank_hours"],
            "inherited_monthly_rows": summary["affected_monthly_rows"],
            "missing_period_rows": 0,
        }
    ]

    (OUT / "artifact.json").write_text(json.dumps(artifact, indent=2) + "\n")

    markdown = "\n\n".join(
        [
            "# Energy Aggregate Gap Recovery Feasibility",
            technical_summary,
            key_findings,
            scope,
            methodology,
            limitations,
            next_steps,
            questions,
            "## Supporting Files\n\nThe report folder contains the exact gap intervals, affected daily/monthly periods, validation evidence, recovery-route classifications, analysis script outputs, and portable report source artifact.",
        ]
    )
    (OUT / "REPORT.md").write_text(markdown + "\n")


if __name__ == "__main__":
    main()
