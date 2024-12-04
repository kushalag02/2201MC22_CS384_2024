# Exam Room Allocation and Attendance Sheet Generator

This project automates the generation of seating plans and attendance sheets for exams. It processes student data, room details, and exam schedules to produce organized outputs.

---

## Features

1. _Seating Plan Generation_:

   - Outputs a CSV file with the seating arrangement for each exam session.

2. _Attendance Sheet Generation_:
   - Creates a directory containing Excel files for attendance sheets.
   - Room-wise attendence sheets where students will mark their attendence.
   - Each sheet includes:
     - Roll numbers
     - Student names
     - Signature columns
     - Separate rows for invigilator and TA signatures.

---

## Setup Instructions

### Step 1: Start the Backend Server

1. Open a terminal and navigate to the project directory.
2. Run the following command to start the backend server:

```bash
   python proj1.py
```

3. Run the following command to start the frontend

```bash
   streamlit run frontend_input.py
```

4. The seating_arrangement_final.csv will be ready and also the attendence sheets are generated in the same folder.
