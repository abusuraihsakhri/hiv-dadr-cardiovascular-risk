#!/usr/bin/env python3
"""D:A:D input completeness checker.

This module does NOT implement the published 2016 D:A:D CVD prediction
equation. In particular it never estimates an individual's cardiovascular
risk or recommends clinical treatment. It validates the predictors needed
to use the study group's calculator independently.
"""
import argparse
import csv
import json
import math
import os
from typing import Any, Dict

# Predictors for the published D:A:D reduced model (2016).
# See https://pubmed.ncbi.nlm.nih.gov/25882821/
REQUIRED_FIELDS = (
    "age", "sex", "systolic_bp", "smoking_status", "family_history_cvd",
    "diabetes", "total_cholesterol", "hdl_cholesterol", "cd4_count",
)
NUMERIC_RANGES = {
    "age": (18, 75),                 # age range noted by the study calculator
    "systolic_bp": (50, 300),        # broad data-entry sanity limits
    "total_cholesterol": (0.1, 30),  # mmol/L
    "hdl_cholesterol": (0.1, 10),    # mmol/L
    "cd4_count": (1, 5000),          # cells/uL
}
BOOL_FIELDS = ("family_history_cvd", "diabetes")
CALCULATOR_URL = "https://chip.dk/resources/tools-standards/risk-assessment-tool/"


def _empty(value: Any) -> bool:
    return value is None or isinstance(value, str) and not value.strip()


def _validate_value(name: str, value: Any) -> str | None:
    if name in NUMERIC_RANGES:
        if isinstance(value, bool):
            return f"{name} must be a number"
        try:
            number = float(value)
        except (TypeError, ValueError):
            return f"{name} must be a number"
        low, high = NUMERIC_RANGES[name]
        if not math.isfinite(number) or not low <= number <= high or (name == "age" and not number.is_integer()):
            return f"{name} must be between {low} and {high}"
    elif name == "sex":
        if str(value).strip().lower() not in ("male", "female"):
            return "sex must be male or female (as coded by the published model)"
    elif name == "smoking_status":
        if str(value).strip().lower() not in ("never", "former", "current"):
            return "smoking_status must be never, former, or current"
    elif name in BOOL_FIELDS:
        if not (isinstance(value, bool) or str(value).strip().lower() in (
            "true", "false", "yes", "no", "1", "0"
        )):
            return f"{name} must be yes or no"
    return None


def calculate_metrics(**kwargs: Any) -> Dict[str, Any]:
    """Validate reduced-model predictors without fabricating a clinical score.

    Retains the historical entry point, but deliberately withdraws its
    arbitrary weighted-sum score and treatment recommendations.
    """
    missing = [name for name in REQUIRED_FIELDS if _empty(kwargs.get(name))]
    errors = [
        error for name in REQUIRED_FIELDS if name not in missing
        if (error := _validate_value(name, kwargs[name]))
    ]
    unknown = sorted(set(kwargs) - set(REQUIRED_FIELDS))
    if unknown:
        errors.append("Unrecognized fields: " + ", ".join(unknown))

    # Cross-field consistency helps identify data-entry mistakes.
    if (not any(k in missing for k in ("total_cholesterol", "hdl_cholesterol"))
            and not any("cholesterol" in e for e in errors)):
        if float(kwargs["hdl_cholesterol"]) > float(kwargs["total_cholesterol"]):
            errors.append("hdl_cholesterol cannot exceed total_cholesterol")

    ready = not missing and not errors
    return {
        "tool": "hiv-dadr-cardiovascular-risk",
        "status": "INPUTS_COMPLETE" if ready else "INPUTS_INCOMPLETE",
        "score": None,
        "classification": "NOT_CALCULATED",
        "risk_5y_percent": None,
        "clinical_recommendation": "No clinical recommendation is calculated.",
        "inputs_evaluated": len(kwargs),
        "missing_inputs": missing,
        "validation_errors": errors,
        "calculator_url": CALCULATOR_URL,
        "note": (
            "No D:A:D risk equation is implemented. Review the inputs and "
            "calculate risk independently with the study group's tool. "
            "The input bounds are data-entry checks, not clinical thresholds."
        ),
    }


def process_single(args: argparse.Namespace) -> None:
    fields = {name: getattr(args, name) for name in REQUIRED_FIELDS}
    print(json.dumps(calculate_metrics(**{
        key: value for key, value in fields.items() if value is not None
    }), indent=2))


def process_batch(input_csv: str, output_csv: str) -> None:
    """Annotate local CSV records with input-completeness status, never risk."""
    if not os.path.isfile(input_csv):
        raise FileNotFoundError(f"Input CSV file not found: {input_csv}")
    if os.path.abspath(input_csv) == os.path.abspath(output_csv):
        raise ValueError("Output CSV must be different from input CSV")

    with open(input_csv, newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        fields = list(reader.fieldnames or [])
        if not fields or any(not field.strip() for field in fields) or len(fields) != len(set(fields)):
            raise ValueError("Input CSV requires unique, nonempty headers")
        rows = list(reader)
    results = []
    for i, row in enumerate(rows, 2):
        if None in row:
            raise ValueError(f"CSV row {i} has more columns than headers")
        inputs = {key: row[key] for key in REQUIRED_FIELDS if key in row}
        result = calculate_metrics(**inputs)
        record = dict(row)
        # Never retain stale or previously generated risk estimates.
        record["risk_5y_percent"] = ""
        record["validation_status"] = result["status"]
        record["missing_fields"] = "; ".join(result["missing_inputs"])
        record["validation_errors"] = "; ".join(result["validation_errors"])
        results.append(record)
    output_fields = list(dict.fromkeys(
        fields + ["risk_5y_percent", "validation_status",
                  "missing_fields", "validation_errors"]
    ))
    parent = os.path.dirname(os.path.abspath(output_csv))
    os.makedirs(parent, exist_ok=True)
    with open(output_csv, "w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)
    print(f"Validated {len(results)} records -> {output_csv} (no risk scores computed)")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="D:A:D reduced-model input checker (NOT a risk calculator)"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    one = commands.add_parser("single", help="Check required inputs")
    for field in REQUIRED_FIELDS:
        if field in NUMERIC_RANGES:
            one.add_argument("--" + field.replace("_", "-"), type=float)
        else:
            one.add_argument("--" + field.replace("_", "-"))
    batch = commands.add_parser("batch", help="Validate CSV without scoring")
    batch.add_argument("-i", "--input", required=True)
    batch.add_argument("-o", "--output", default="results.csv")
    args = parser.parse_args(argv)
    if args.command == "single":
        process_single(args)
    else:
        process_batch(args.input, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
