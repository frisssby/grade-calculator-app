from flask import Flask, render_template, request
import pandas as pd

from grade import Grade
from exceptions import CourseNotFound
from sheets_handler import GoogleSheetsApiHandler

app = Flask(__name__)

df = pd.read_pickle('assessment_db.pkl')
google_sheets_handler = GoogleSheetsApiHandler.from_creds_file('credentials.json')


@app.route('/')
def index():
    names = list(df.index)
    return render_template('index.html', course_names=names)


@app.route('/grades', methods=['POST'])
def grades():
    if request.method == 'POST':
        try:
            course_name = request.form['course-choice']
            if not course_name in df.index:
                raise CourseNotFound(course_name)
            data = df.loc[course_name]
            mark_names = data.grade.names
            link = data.link
            return render_template(
                'grades.html',
                course_name=course_name,
                course_link=link,
                mark_names=mark_names
            )
        except CourseNotFound:
            return render_template('error.html', message="Курс не найден. \
                 Возможно, курса с таким названием не существует \
                 или информация об оценивании по нему отсутствует.")


@app.route('/result', methods=['POST'])
def result():
    values = []
    names_to_values = request.form

    for key in names_to_values:
        values.append(names_to_values[key])

    course_name = values[-1]
    marks = [float(i) for i in values[:-1]]

    grade_obj = df.loc[course_name].grade
    grade = grade_obj(marks)
    names = list(grade_obj.names)
    weights = list(grade_obj.weights)

    spreadsheet = google_sheets_handler.create_spreadsheet(course_name)
    google_sheets_handler.write_formula(spreadsheet, names, weights, marks)
    url = spreadsheet['spreadsheetUrl']

    
    return render_template('/result.html', grade=f'{grade:.3f}', sheet_link=url)
