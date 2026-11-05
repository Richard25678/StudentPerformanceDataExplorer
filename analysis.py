
"""Load and analyze the UCI Student Performance datasets with Pandas."""

import csv
import math
from pathlib import Path

import pandas as pd


UCI_COLUMNS = (
    "school", "sex", "age", "address", "famsize", "Pstatus", "Medu", "Fedu",
    "Mjob", "Fjob", "reason", "guardian", "traveltime", "studytime", "failures",
    "schoolsup", "famsup", "paid", "activities", "nursery", "higher", "internet",
    "romantic", "famrel", "freetime", "goout", "Dalc", "Walc", "health",
    "absences", "G1", "G2", "G3",
)
NUMERIC_COLUMNS = (
    "age", "Medu", "Fedu", "traveltime", "studytime", "failures", "famrel",
    "freetime", "goout", "Dalc", "Walc", "health", "absences", "G1", "G2", "G3",
)
GRADE_COLUMNS = ("G1", "G2", "G3")
RECORD_COLUMNS = ("RowNumber", "studytime", "failures", "absences", "G1", "G2", "G3")
STUDYTIME_LABELS = {
    1: "Less than 2 hours",
    2: "2 to 5 hours",
    3: "5 to 10 hours",
    4: "More than 10 hours",
}


def _read_csv_records(filename):
    """Parse comma- or semicolon-separated records, including an extra quoted row layer."""
    path = Path(filename)
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        sample = source.read(8192)
        if not sample.strip():
            raise ValueError(f"Dataset is empty: {path}")
        try:
            delimiter = csv.Sniffer().sniff(sample, delimiters=",;").delimiter
        except csv.Error as error:
            raise ValueError(f"Could not detect CSV separator in {path.name}.") from error

        source.seek(0)
        reader = csv.reader(source, delimiter=delimiter, strict=True)
        try:
            header = [column.strip().lstrip("\ufeff") for column in next(reader)]
        except (StopIteration, csv.Error) as error:
            raise ValueError(f"Could not read the header in {path.name}.") from error

        rows = []
        for line_number, row in enumerate(reader, start=2):
            if not row or all(not value.strip() for value in row):
                continue
            if len(row) == 1 and delimiter in row[0]:
                try:
                    nested_row = next(csv.reader([row[0]], delimiter=delimiter, strict=True))
                except csv.Error as error:
                    raise ValueError(
                        f"Malformed quoted row {line_number} in {path.name}."
                    ) from error
                if len(nested_row) == len(header):
                    row = nested_row
            if len(row) != len(header):
                raise ValueError(
                    f"Row {line_number} in {path.name} has {len(row)} fields; "
                    f"expected {len(header)}."
                )
            rows.append(row)

    if not rows:
        raise ValueError(f"Dataset contains a header but no student records: {path}")
    return pd.DataFrame(rows, columns=header)


def load_data(filename):
    """Load and validate a UCI subject CSV, retaining its original student records."""
    data = _read_csv_records(filename)
    missing_columns = [column for column in UCI_COLUMNS if column not in data.columns]
    if missing_columns:
        raise ValueError(
            f"{Path(filename).name} is missing expected columns: "
            f"{', '.join(missing_columns)}"
        )
    if data.columns.duplicated().any():
        raise ValueError(f"{Path(filename).name} contains duplicate column names.")

    data = data.loc[:, UCI_COLUMNS].copy()
    for column in data.columns:
        if data[column].dtype == object:
            data[column] = data[column].astype(str).str.strip()
    for column in NUMERIC_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="coerce")
        if data[column].isna().any():
            raise ValueError(f"{column} contains missing or non-numeric values.")

    for column in GRADE_COLUMNS:
        if not data[column].between(0, 20).all():
            raise ValueError(f"{column} values must be between 0 and 20.")
    if not data["studytime"].isin(STUDYTIME_LABELS).all():
        raise ValueError("studytime must use UCI's values from 1 through 4.")
    if (data["absences"] < 0).any() or (data["failures"] < 0).any():
        raise ValueError("Absences and failures cannot be negative.")

    data.insert(0, "RowNumber", range(1, len(data) + 1))
    return data


def display_summary(data):
    """Print dataset size, grade statistics, and descriptive numeric statistics."""
    print(f"\nRecords: {len(data)}")
    print(f"Schools: {data['school'].value_counts().to_dict()}")
    print("\nDescriptive statistics:")
    print(data[list(NUMERIC_COLUMNS)].describe().round(2).to_string())
    print("\nGrade summary:")
    print(data[list(GRADE_COLUMNS)].agg(["mean", "median", "min", "max"]).round(2))


def calculate_period_averages(data):
    """Calculate class means for first-period G1, second-period G2, and final G3."""
    return data[list(GRADE_COLUMNS)].mean().round(2)


def period_grade_changes(data):
    """Calculate class-average grade changes from G1 to G2 and from G2 to G3."""
    averages = calculate_period_averages(data)
    return pd.Series({"G1 to G2": averages["G2"] - averages["G1"],
                      "G2 to G3": averages["G3"] - averages["G2"]}).round(2)


def find_top_students(data, number_of_students=5):
    """Return the highest G3 records using only anonymous file row numbers."""
    if number_of_students < 1:
        raise ValueError("The number of records must be at least one.")
    return data.sort_values(["G3", "G2", "G1"], ascending=False, kind="stable").head(
        number_of_students
    )[list(RECORD_COLUMNS)]


def group_by_studytime(data):
    """Group records by UCI's weekly study-time category and average final grade."""
    grouped = data.groupby("studytime", observed=True)["G3"].agg(
        StudentCount="size", AverageG3="mean"
    )
    grouped["StudyTime"] = [STUDYTIME_LABELS[value] for value in grouped.index]
    return grouped.reset_index()[["studytime", "StudyTime", "StudentCount", "AverageG3"]].round(
        {"AverageG3": 2}
    )


def group_by_absences(data):
    """Group records by absence count and calculate each group's mean G3."""
    return data.groupby("absences", as_index=False).agg(
        StudentCount=("G3", "size"), AverageG3=("G3", "mean")
    ).sort_values("absences").round({"AverageG3": 2})


def filter_students(data, minimum_g3, sort_by="G3", descending=True):
    """Filter by a 0-20 final-grade threshold and sort by an allowed UCI field."""
    if not math.isfinite(minimum_g3) or not 0 <= minimum_g3 <= 20:
        raise ValueError("The minimum G3 grade must be between 0 and 20.")
    allowed_sort_fields = {"G1", "G2", "G3", "studytime", "absences", "failures"}
    if sort_by not in allowed_sort_fields:
        raise ValueError(f"Sort field must be one of: {', '.join(sorted(allowed_sort_fields))}.")
    filtered = data[data["G3"] >= minimum_g3]
    return filtered.sort_values(sort_by, ascending=not descending, kind="stable")[
        list(RECORD_COLUMNS)
    ].reset_index(drop=True)


def analyze_failures_and_attendance(data):
    """Summarize failure counts, G3 by past failures, and school absence statistics."""
    failure_summary = data.groupby("failures")["G3"].agg(
        StudentCount="size", AverageG3="mean"
    ).round(2)
    attendance_summary = pd.Series({
        "Average absences": round(data["absences"].mean(), 2),
        "Median absences": round(data["absences"].median(), 2),
        "Maximum absences": int(data["absences"].max()),
        "Students with no absences": int((data["absences"] == 0).sum()),
        "Students with past failures": int((data["failures"] > 0).sum()),
    })
    return failure_summary, attendance_summary


def categorize_g3(grade):
    """Assign a project-defined category to a final grade on UCI's 0-20 scale."""
    if grade < 10:
        return "Below 10"
    if grade < 14:
        return "10 to 13"
    if grade < 17:
        return "14 to 16"
    return "17 to 20"


def performance_distribution(data):
    """Count students in documented project-defined G3 score bands."""
    categories = data["G3"].apply(categorize_g3)
    order = ["Below 10", "10 to 13", "14 to 16", "17 to 20"]
    return categories.value_counts().reindex(order, fill_value=0)


def calculate_research_correlations(data):
    """Calculate Spearman rank associations with G3 without implying causation."""
    variables = ["studytime", "absences", "failures", "G1", "G2", "G3"]
    return data[variables].corr(method="spearman")["G3"].drop("G3").round(3)


def export_analysis(data, filename):
    """Export relevant UCI records and project-defined G3 categories to CSV."""
    results = data[list(RECORD_COLUMNS)].copy()
    results["G3Category"] = data["G3"].apply(categorize_g3)
    results.to_csv(filename, index=False)
    return results
