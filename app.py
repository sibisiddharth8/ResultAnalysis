import os
from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return "No file uploaded!", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file!", 400

    try:
        # Check file type and read into DataFrame
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            return "Unsupported file type! Please upload a CSV or XLSX file.", 400

        # Normalize column headers
        df.columns = [col.strip().lower() for col in df.columns]

        # Analyze data
        total_students = len(df)
        pass_counts = df.apply(lambda row: sum(cell.strip().upper() == 'P' for cell in row[1:]), axis=1)
        fail_counts = df.apply(lambda row: sum(cell.strip().upper() == 'F' for cell in row[1:]), axis=1)

        total_passes = sum(pass_counts == df.shape[1] - 1)  # Fully passed students
        total_one_fail = sum(fail_counts == 1)  # Students with exactly one fail
        total_fails = sum(fail_counts > 0)  # Students with at least one fail
        subject_pass_counts = (df.iloc[:, 1:].applymap(lambda x: x.strip().upper() == 'P')).sum()
        subject_fail_counts = (df.iloc[:, 1:].applymap(lambda x: x.strip().upper() == 'F')).sum()

        # Additional Statistical Data
        avg_pass_count = pass_counts.mean()  # Average number of subjects passed per student
        avg_fail_count = fail_counts.mean()  # Average number of subjects failed per student
        max_passes = pass_counts.max()  # Maximum number of passes by a single student
        max_fails = fail_counts.max()  # Maximum number of fails by a single student
        min_passes = pass_counts.min()  # Minimum number of passes by a single student
        min_fails = fail_counts.min()  # Minimum number of fails by a single student
        student_with_max_fails = df.iloc[fail_counts.idxmax(), 0]  # Student with most fails
        student_with_max_passes = df.iloc[pass_counts.idxmax(), 0]  # Student with most passes

        # Prepare response data
        analysis = {
            "Total Students": total_students,
            "Total Passes": total_passes,
            "Total One Fail": total_one_fail,
            "Total Fails": total_fails,
            "Average Pass Count per Student": avg_pass_count,
            "Average Fail Count per Student": avg_fail_count,
            "Maximum Passes by a Student": max_passes,
            "Maximum Fails by a Student": max_fails,
            "Minimum Passes by a Student": min_passes,
            "Minimum Fails by a Student": min_fails,
            "Student with Most Fails": student_with_max_fails,
            "Student with Most Passes": student_with_max_passes,
            "Subject-wise Pass Counts": subject_pass_counts.to_dict(),
            "Subject-wise Fail Counts": subject_fail_counts.to_dict()
        }

        return render_template('result.html', analysis=analysis)

    except Exception as e:
        return f"An error occurred: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0')
