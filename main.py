
"""Interactive command-line application for UCI Student Performance data."""

import csv
from pathlib import Path
import sys

# Some Python installations omit the script folder from the module search path.
PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from analysis import (
    analyze_failures_and_attendance,
    calculate_period_averages,
    calculate_research_correlations,
    display_summary,
    export_analysis,
    filter_students,
    find_top_students,
    group_by_absences,
    group_by_studytime,
    performance_distribution,
    period_grade_changes,
    load_data,
)
from visualizations import (
    plot_period_averages,
    plot_research_relationships,
    plot_student_performance,
)


DATASETS = {
    "1": ("Mathematics", PROJECT_DIR / "student-mat.csv"),
    "2": ("Portuguese", PROJECT_DIR / "student-por.csv"),
}
MENU_OPTIONS = "1 through 13"
SORT_FIELDS = ("G3", "G2", "G1", "studytime", "absences", "failures")


def display_welcome():
    """Print the program title and its UCI dataset purpose."""
    print("=" * 64)
    print("          UCI STUDENT PERFORMANCE DATA EXPLORER")
    print("=" * 64)
    print("Explore Mathematics or Portuguese grades, study time, and absences.")


def choose_dataset():
    """Ask which official UCI subject file should be analyzed."""
    while True:
        print("\nChoose a subject:")
        print("1. Mathematics (student-mat.csv)")
        print("2. Portuguese (student-por.csv)")
        try:
            choice = input("Enter 1 or 2: ").strip()
        except EOFError:
            return None
        if choice in DATASETS:
            return DATASETS[choice]
        print("Invalid selection. Enter 1 for Mathematics or 2 for Portuguese.")


def display_menu():
    """Print the existing 13 menu slots with UCI-specific analysis options."""
    print("\nMAIN MENU")
    print("-" * 54)
    print("1.  Display dataset summary and descriptive statistics")
    print("2.  Show average G1, G2, and G3 grades")
    print("3.  Show the top five anonymous student rows")
    print("4.  Group students by weekly study time")
    print("5.  Group students by school absences")
    print("6.  Filter and sort student records")
    print("7.  Analyze past failures and absences")
    print("8.  Show performance categories and correlations")
    print("9.  Chart average G1, G2, and G3")
    print("10. Chart top student G3 grades")
    print("11. Chart study time and absences against G3")
    print("12. Export analysis results to CSV")
    print("13. Exit")
    print("-" * 54)


def _show_filtered_records(data):
    """Prompt for a final-grade threshold and sorting field, then print records."""
    minimum_g3 = float(input("Minimum final grade G3 (0-20): "))
    sort_by = input(f"Sort by {', '.join(SORT_FIELDS)} [G3]: ").strip() or "G3"
    order = input("Sort descending? [Y/n]: ").strip().casefold()
    descending = order not in {"n", "no"}
    results = filter_students(data, minimum_g3, sort_by, descending)
    print(f"\n{len(results)} record(s) meet the minimum grade.")
    print(results.to_string(index=False))


def process_choice(choice, data):
    """Run one menu option and return whether the main loop should continue."""
    if choice == "1":
        display_summary(data)
    elif choice == "2":
        print("\nAVERAGE PERIOD GRADES (0-20)")
        print(calculate_period_averages(data).to_string())
        print("\nAverage changes between periods:")
        print(period_grade_changes(data).to_string())
    elif choice == "3":
        print("\nTOP FIVE RECORDS (ROW NUMBERS ARE FILE POSITIONS, NOT STUDENT IDS)")
        print(find_top_students(data).to_string(index=False))
    elif choice == "4":
        print("\nAVERAGE G3 BY WEEKLY STUDY TIME")
        print(group_by_studytime(data).to_string(index=False))
    elif choice == "5":
        print("\nAVERAGE G3 BY ABSENCE COUNT")
        print(group_by_absences(data).to_string(index=False))
    elif choice == "6":
        _show_filtered_records(data)
    elif choice == "7":
        failures, absences = analyze_failures_and_attendance(data)
        print("\nPAST FAILURES AND AVERAGE G3")
        print(failures.to_string())
        print("\nABSENCE SUMMARY")
        print(absences.to_string())
    elif choice == "8":
        print("\nPROJECT-DEFINED FINAL-GRADE CATEGORIES")
        print(performance_distribution(data).to_string())
        print("\nSPEARMAN RANK CORRELATIONS WITH G3")
        print(calculate_research_correlations(data).to_string())
        print("These are descriptive associations; correlation does not prove causation.")
    elif choice == "9":
        plot_period_averages(calculate_period_averages(data))
    elif choice == "10":
        plot_student_performance(data)
    elif choice == "11":
        plot_research_relationships(data, group_by_studytime(data))
    elif choice == "12":
        filename = input("Output CSV path [student_analysis.csv]: ").strip()
        output_path = Path(filename) if filename else PROJECT_DIR / "student_analysis.csv"
        if not output_path.is_absolute():
            output_path = PROJECT_DIR / output_path
        export_analysis(data, output_path)
        print(f"Analysis exported to: {output_path.resolve()}")
    elif choice == "13":
        print("Thank you for using the Data Explorer!")
        return False
    else:
        print(f"Invalid selection. Choose an option from {MENU_OPTIONS}.")
    return True


def main():
    """Choose a subject dataset, validate it, and run the interactive menu."""
    display_welcome()
    selected_dataset = choose_dataset()
    if selected_dataset is None:
        print("Input ended. Exiting the Data Explorer.")
        return
    subject, filename = selected_dataset
    try:
        data = load_data(filename)
    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        print(f"Could not load {subject} data: {error}")
        return

    print(f"\nLoaded {len(data)} {subject} records from {filename.name}.")
    while True:
        display_menu()
        try:
            choice = input("Enter your choice: ").strip()
            if not process_choice(choice, data):
                return
        except EOFError:
            print("\nInput ended. Exiting the Data Explorer.")
            return
        except Exception as error:
            print(f"Could not complete that option: {error}")


if __name__ == "__main__":
    main()
