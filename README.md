# Overview

## Student Performance Data Explorer

The Student Performance Data Explorer is a Python application developed to explore and analyze student academic performance using real-world educational data.

The dataset comes from the UCI Machine Learning Repository:

[UCI Student Performance Dataset](https://archive.ics.uci.edu/dataset/320/student+performance)

It contains student information from two Portuguese secondary schools. The project uses two CSV files: `student-mat.csv` for Mathematics and `student-por.csv` for Portuguese.

The dataset includes information such as students' age, gender, weekly study time, school absences, previous failures, and academic grades.

The purpose of this software is to analyze student performance and identify patterns that may be related to academic results. Users can explore statistics, filter and sort records, compare grades, generate charts, and export analysis results.

# Data Analysis Results

This project focuses on three main research questions.

### Question 1: How does weekly study time relate to students' final grades?

Answer: The analysis of 649 Portuguese student records showed that students studying less than 2 hours per week had an average final grade (G3) of 10.84/20. Students studying 2–5 hours averaged 12.09/20, while those studying 5–10 hours averaged 13.23/20. Students studying more than 10 hours averaged 13.06/20.

The highest average grade was achieved by students studying 5–10 hours per week. These results suggest a positive relationship between weekly study time and academic performance, although the group studying more than 10 hours had a slightly lower average.

### Question 2: How are school absences related to students' final grades?

Answer: The analysis of 649 Portuguese student records showed that students with no absences had an average final grade (G3) of 12.04/20. Students with 4 absences averaged 12.01/20, those with 8 absences averaged 11.62/20, and those with 12 absences averaged 10.08/20.

The results suggest that higher absence counts can be associated with lower academic performance. However, the relationship is not consistent across every absence count, and some groups contain very few students. Therefore, the results show an association rather than proving that absences cause lower grades.

### Question 3: How do average grades change across the three grading periods?

Answer: The analysis of 649 Portuguese student records showed that the average G1 grade was 11.40/20, the average G2 grade was 11.57/20, and the average G3 grade was 11.91/20. The average increased by 0.17 points from G1 to G2 and by 0.34 points from G2 to G3. Overall, the results show a gradual improvement in average grades across the three grading periods.

The application uses pandas to filter, group, sort, and calculate statistics from the student records. Matplotlib is used to create charts that help visualize the findings.

# Development Environment

I developed this project using:

- Visual Studio Code
- Python
- Windows
- Git and GitHub

The programming language used is Python.

Libraries:

- **pandas:** Used to load, organize, filter, group, and analyze student data.
- **Matplotlib:** Used to create charts and visualize analysis results.

# Useful Websites

- [UCI Machine Learning Repository – Student Performance Dataset](https://archive.ics.uci.edu/dataset/320/student+performance)
- [Python Documentation](https://docs.python.org/3/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Matplotlib Documentation](https://matplotlib.org/stable/)

# Future Work

- Add a graphical user interface.
- Create more interactive charts.
- Add additional student performance analysis.
- Improve error handling and input validation.
- Add downloadable analysis reports.

# Software Presentation

[Watch the Student Performance Data Explorer Presentation on YouTube](https://youtu.be/wz_itAPGohM)