
"""Matplotlib charts for UCI period grades, study time, and absences."""

import importlib.util
import os
import warnings
from pathlib import Path

import matplotlib

if not os.environ.get("MPLBACKEND") and importlib.util.find_spec("tkinter"):
    try:
        matplotlib.use("TkAgg")
    except (ImportError, RuntimeError):
        pass

import matplotlib.pyplot as plt


PROJECT_DIR = Path(__file__).resolve().parent


def _create_figure(figsize, **subplot_options):
    """Create a chart, switching to Agg if Tk cannot initialize its window."""
    try:
        return plt.subplots(figsize=figsize, **subplot_options)
    except Exception:
        if "tk" not in matplotlib.get_backend().lower():
            raise
        plt.switch_backend("Agg")
        return plt.subplots(figsize=figsize, **subplot_options)


def _display_or_save(figure, filename):
    """Show a chart interactively or save it when no GUI canvas is available."""
    output_path = PROJECT_DIR / filename
    interactive_framework = getattr(
        figure.canvas, "required_interactive_framework", None
    )
    if interactive_framework is None:
        _save_chart(figure, output_path, "Matplotlib is using a non-interactive backend")
        return

    try:
        with warnings.catch_warnings(record=True) as captured_warnings:
            warnings.simplefilter("always", UserWarning)
            plt.show(block=True)
        display_warning = next(
            (
                warning
                for warning in captured_warnings
                if "non-interactive" in str(warning.message).lower()
            ),
            None,
        )
        if display_warning is not None:
            _save_chart(figure, output_path, str(display_warning.message))
            return
        plt.close(figure)
    except Exception as error:
        _save_chart(figure, output_path, str(error))


def _save_chart(figure, output_path, reason):
    """Save a chart as a PNG and tell the user why interactive display failed."""
    figure.savefig(output_path, format="png", dpi=150, bbox_inches="tight")
    plt.close(figure)
    print(f"Interactive display unavailable ({reason}). Graph saved to: {output_path}")


def plot_period_averages(averages):
    """Display class-average grades for G1, G2, and final grade G3."""
    figure, axis = _create_figure(figsize=(9, 5))
    axis.bar(averages.index, averages.values, color=["#247BA0", "#70C1B3", "#F3A712"])
    axis.set(title="Average Grade Across Periods", xlabel="Grade period", ylabel="Average grade (0-20)")
    axis.set_ylim(0, 20)
    axis.grid(axis="y", linestyle="--", alpha=0.4)
    figure.tight_layout()
    _display_or_save(figure, "period_grade_averages.png")


def plot_student_performance(data):
    """Display the ten highest final grades labeled only by file row number."""
    top_students = data.sort_values(
        ["G3", "G2", "G1"], ascending=False, kind="stable"
    ).head(10)
    figure, axis = _create_figure(figsize=(11, 6))
    labels = [f"Row {number}" for number in top_students["RowNumber"]]
    axis.bar(labels, top_students["G3"], color="#247BA0")
    axis.set(title="Top Final Grades (Anonymous Rows)", xlabel="UCI file row", ylabel="Final grade G3 (0-20)")
    axis.set_ylim(0, 20)
    axis.tick_params(axis="x", labelrotation=40)
    axis.grid(axis="y", linestyle="--", alpha=0.4)
    figure.tight_layout()
    _display_or_save(figure, "top_student_g3.png")


def plot_research_relationships(data, studytime_summary):
    """Compare study-time groups and plot absences against G3 without row labels."""
    figure, axes = _create_figure(figsize=(14, 6), nrows=1, ncols=2)
    study_axis, absence_axis = axes
    study_axis.bar(
        studytime_summary["StudyTime"],
        studytime_summary["AverageG3"],
        color="#70C1B3",
    )
    study_axis.set(
        title="Weekly Study Time vs Average G3",
        xlabel="UCI study-time category",
        ylabel="Average final grade G3 (0-20)",
    )
    study_axis.set_ylim(0, 20)
    study_axis.tick_params(axis="x", labelrotation=25)
    study_axis.grid(axis="y", linestyle="--", alpha=0.4)
    absence_axis.scatter(
        data["absences"],
        data["G3"],
        color="#E4572E",
        alpha=0.8,
        edgecolors="white",
    )
    absence_axis.set(
        title="School Absences vs Final G3",
        xlabel="Number of absences",
        ylabel="Final grade G3 (0-20)",
    )
    absence_axis.set_ylim(0, 20)
    absence_axis.grid(True, linestyle="--", alpha=0.4)
    figure.tight_layout()
    _display_or_save(figure, "studytime_and_absences_vs_g3.png")
