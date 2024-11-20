from flask import Flask, render_template, request, send_file
import pandas as pd
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


def generate_pdf_for_attendance(date, day, shift, room, students, output_dir):

    print(students)
    print("\nhola")
    safe_date = date.replace("/", "_")
    day_dir = os.path.join(output_dir, safe_date)
    if not os.path.exists(day_dir):
        os.makedirs(day_dir)

    shift_dir = os.path.join(day_dir, shift)
    if not os.path.exists(shift_dir):
        os.makedirs(shift_dir)

    pdf_filename = os.path.join(shift_dir, f"attendance_{room}.pdf")

    c = canvas.Canvas(pdf_filename, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, height - 40, f"Attendance Sheet - {day} ({shift})")
    c.drawString(30, height - 60, f"Room No.: {room}")

    c.setFont("Helvetica-Bold", 10)
    c.drawString(30, height - 100, "Student Name")
    c.drawString(200, height - 100, "Roll No.")
    c.drawString(350, height - 100, "Signature of Student")

    y_position = height - 120

    for student in students:
        student_name = student['name'] if pd.notna(student['name']) else ""
        student_roll = student['rollno'] if pd.notna(student['rollno']) else ""

        c.setFont("Helvetica", 10)
        c.drawString(30, y_position, student_name)

        c.drawString(200, y_position, student_roll)

        c.drawString(350, y_position, "____________________")

        y_position -= 20

        if y_position < 100:
            c.showPage()
            y_position = height - 40

    c.setFont("Helvetica-Bold", 10)
    c.drawString(30, y_position - 30,
                 "Invigilator's Signature: ____________________")

    c.save()


@app.route('/submit', methods=['POST'])
def submit():
    buffer = int(request.form['buffer'])
    sparse_option = request.form['seating']
    sparse = sparse_option == 'sparse'

    students_file = request.files['students_file']
    schedule_file = request.files['schedule_file']
    rooms_file = request.files['rooms_file']
    student_roll_map_file = request.files['student_roll_map']  # New input file

    students_df = pd.read_csv(students_file, skiprows=1)
    schedule_df = pd.read_csv(schedule_file, skiprows=1)
    rooms_df = pd.read_csv(rooms_file)
    # Load roll-number-to-name mapping
    student_roll_map_df = pd.read_csv(student_roll_map_file)

    schedule_df['Morning Courses'] = schedule_df['Morning'].apply(
        lambda x: x.split('; ') if pd.notna(x) else [])
    schedule_df['Evening Courses'] = schedule_df['Evening'].apply(
        lambda x: x.split('; ') if pd.notna(x) else [])

    def assign_rooms(courses, rooms_df, buffer, sparse):
        assignments = []
        room_capacity_left = rooms_df[['Room No.', 'Exam Capacity']].copy()
        room_capacity_left['Remaining Capacity'] = room_capacity_left['Exam Capacity'] - buffer

        for course in courses:
            students = students_df[students_df['course_code']
                                   == course]['rollno'].tolist()
            num_students = len(students)

            for _, room in room_capacity_left.iterrows():
                if room['Remaining Capacity'] <= 0:
                    continue

                max_students_in_room = min(
                    room['Remaining Capacity'], num_students)
                if sparse:
                    max_students_in_room = min(
                        max_students_in_room, room['Exam Capacity'] // 2)

                assigned_students = max_students_in_room
                assigned_roll_numbers = students[:assigned_students]
                students = students[assigned_students:]
                num_students -= assigned_students

                room_capacity_left.loc[room_capacity_left['Room No.'] ==
                                       room['Room No.'], 'Remaining Capacity'] -= assigned_students

                existing_assignment = next(
                    (a for a in assignments if a['Room'] == room['Room No.']), None)
                if existing_assignment:
                    existing_assignment['Courses'] += f", {course}"
                    existing_assignment['Roll Numbers'] += f", {', '.join(assigned_roll_numbers)}"
                    existing_assignment['Students Assigned'] += assigned_students
                    existing_assignment['Vacant Seats'] = room_capacity_left.loc[room_capacity_left['Room No.']
                                                                                 == room['Room No.'], 'Remaining Capacity'].values[0]
                else:
                    assignments.append({
                        'Room': room['Room No.'],
                        'Block': rooms_df.loc[rooms_df['Room No.'] == room['Room No.'], 'Block'].values[0],
                        'Courses': course,
                        'Students Assigned': assigned_students,
                        'Vacant Seats': room_capacity_left.loc[room_capacity_left['Room No.'] == room['Room No.'], 'Remaining Capacity'].values[0],
                        'Roll Numbers': ', '.join(assigned_roll_numbers),
                        'Buffer Seats': buffer  # Add Buffer Seats to each room
                    })

                if num_students == 0:
                    break

            if num_students > 0:
                print(
                    f"Warning: Not enough rooms for course {course} with {num_students} students remaining.")

        return assignments

    output = []
    for _, row in schedule_df.iterrows():
        date = row['Date']
        day = row['Day']

        morning_assignments = assign_rooms(
            row['Morning Courses'], rooms_df, buffer, sparse)
        for assignment in morning_assignments:
            output.append({
                'Date': date,
                'Day': day,
                'Session': 'Morning',
                'Room': assignment['Room'],
                'Block': assignment['Block'],
                'Courses': assignment['Courses'],
                'Students Assigned': assignment['Students Assigned'],
                'Vacant Seats': assignment['Vacant Seats'],
                # Include buffer seats in output
                'Buffer Seats': assignment['Buffer Seats'],
                'Roll Numbers': assignment['Roll Numbers']

            })

        evening_assignments = assign_rooms(
            row['Evening Courses'], rooms_df, buffer, sparse)
        for assignment in evening_assignments:
            output.append({
                'Date': date,
                'Day': day,
                'Session': 'Evening',
                'Room': assignment['Room'],
                'Block': assignment['Block'],
                'Courses': assignment['Courses'],
                'Students Assigned': assignment['Students Assigned'],
                'Vacant Seats': assignment['Vacant Seats'],
                'Buffer Seats': assignment['Buffer Seats'],
                'Roll Numbers': assignment['Roll Numbers']
            })

    output_df = pd.DataFrame(output)
    output_csv = 'seating_arrangement_final.csv'
    output_df.to_csv(output_csv, index=False)

    def add_student_names(output_df, student_roll_map_df):
        expanded_rows = []
        for _, row in output_df.iterrows():
            rolls = row['Roll Numbers'].split(', ')
            for roll in rolls:
                new_row = row.copy()
                new_row['Roll No.'] = roll
                expanded_rows.append(new_row)

        expanded_df = pd.DataFrame(expanded_rows)

        final_df = pd.merge(
            expanded_df,
            student_roll_map_df,
            how='left',
            left_on='Roll No.',
            right_on='Roll'
        )
        return final_df[['Date', 'Day', 'Session', 'Room', 'Block', 'Courses', 'Roll No.', 'Name', 'Vacant Seats', 'Buffer Seats']]

    seating_with_names = add_student_names(output_df, student_roll_map_df)

    output_dir = "attendance_sheets"
    grouped_data = seating_with_names.groupby(
        ['Date', 'Day', 'Session', 'Room'])

    for (date, day, shift, room), group in grouped_data:
        students = []
        for _, student in group.iterrows():
            name = student['Name'] if pd.notna(
                student['Name']) else ""  # Handle NaN names
            rollno = student['Roll No.'] if pd.notna(
                student['Roll No.']) else ""  # Handle NaN roll numbers
            students.append({'name': name, 'rollno': rollno})
        generate_pdf_for_attendance(
            date, day, shift, room, students, output_dir)

    return "Attendance sheets have been generated successfully. You can now download them."


@app.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    return send_file(filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
