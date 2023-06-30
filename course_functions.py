from tkinter import *
from tkinter import ttk, messagebox, filedialog

course_labels_config = ["Id", "Course", "Score", "Grade"]


# fetch student course details automatically when a student is selected
def get_course_data(course_table, cursor, student_table, event):
    global student_id

    student_id = student_table.item(student_table.focus())["values"][0]
    if not student_id:
        return

    query = """
    SELECT c.course_id, cn.course_name, c.score,
        CASE
            WHEN c.score > 80 THEN 'A'
            WHEN c.score >= 70 THEN 'B'
            WHEN c.score >= 60 THEN 'C'
            WHEN c.score >= 50 THEN 'D'
            ELSE 'F'
        END AS grade
    FROM course c
    INNER JOIN course_names cn ON c.course_id = cn.id
    WHERE c.student_id = %s
    """

    # Execute the query with the student ID as a parameter
    cursor.execute(query, (student_id,))

    course_table.delete(*course_table.get_children())
    # Fetch all the result rows
    fetched_data = cursor.fetchall()
    for data in fetched_data:
        course_table.insert("", "end", values=data)


# refresh the after running CRUD functions on course tables
def refresh_course_data(course_table, cursor):
    query = """
    SELECT c.course_id, cn.course_name, c.score,
        CASE
            WHEN c.score > 80 THEN 'A'
            WHEN c.score >= 70 THEN 'B'
            WHEN c.score >= 60 THEN 'C'
            WHEN c.score >= 50 THEN 'D'
            ELSE 'F'
        END AS grade
    FROM course c
    INNER JOIN course_names cn ON c.course_id = cn.id
    WHERE c.student_id = %s
    """

    # Execute the query with the student ID as a parameter
    cursor.execute(query, (student_id,))

    course_table.delete(*course_table.get_children())
    # Fetch all the result rows
    fetched_data = cursor.fetchall()
    for data in fetched_data:
        course_table.insert("", "end", values=data)


# create a new sub-window for adding/search/modifying course details
def fill_course(
    window_title, button_text, button_command, course_labels_config, cursor
):
    global course_fields_entries, fill_course_window, selected_course
    course_fields_entries = []

    fill_course_window = Toplevel()
    fill_course_window.title(window_title)
    fill_course_window.geometry("450x300+300+200")
    fill_course_window.resizable(False, False)
    fill_course_window.grab_set()
    fill_course_window.attributes("-topmost", "true")

    Label(fill_course_window, text="Course ID", font=("arial", 16, "bold")).grid(
        row=0, column=0, padx=20, pady=20, sticky=W
    )
    Label(fill_course_window, text="Course Name", font=("arial", 16, "bold")).grid(
        row=1, column=0, padx=20, pady=20, sticky=W
    )

    cursor.execute("SELECT id, course_name FROM course_names")
    course_names = cursor.fetchall()

    course_ids = [course[0] for course in course_names]
    course_names = [course[1] for course in course_names]

    course_id_combo = ttk.Combobox(fill_course_window, values=course_ids)
    course_id_combo.config(font=("arial", 14), width=22, height=6)
    course_id_combo.grid(row=0, column=1)
    course_fields_entries.append(course_id_combo)

    course_name_combo = ttk.Combobox(fill_course_window, values=course_names)
    course_name_combo.config(font=("arial", 14), width=22, height=6)
    course_name_combo.grid(row=1, column=1)
    course_fields_entries.append(course_name_combo)

    def on_course_id_select(event):
        selected_id = int(course_id_combo.get())
        index = course_ids.index(selected_id)
        course_name_combo.current(index)

    def on_course_name_select(event):
        selected_name = course_name_combo.get()
        index2 = course_names.index(selected_name)
        course_id_combo.current(index2)

    course_id_combo.bind("<<ComboboxSelected>>", on_course_id_select)
    course_name_combo.bind("<<ComboboxSelected>>", on_course_name_select)

    Label(fill_course_window, text="Score", font=("arial", 16, "bold")).grid(
        row=2, column=0, padx=20, pady=20, sticky=W
    )
    entry = Entry(fill_course_window, font=("arial", 16, "bold"), bd=2)
    entry.grid(row=2, column=1)
    course_fields_entries.append(entry)

    button = Button(
        fill_course_window,
        text=button_text,
        width=10,
        font=("arial", 14, "bold"),
        command=button_command,
    )
    button.grid(row=len(course_labels_config) + 1, columnspan=2, pady=10)


# add course details to the database
def add_course(cursor, conn, course_table, student_table):
    selected_student = student_table.item(student_table.focus())["values"]
    if not selected_student:
        messagebox.showerror("Error", "Please select a student first.")
        return

    def add():
        if any(entry.get() == "" for entry in course_fields_entries):
            messagebox.showerror(
                "Error", "All fields are required", parent=fill_course_window
            )
            return

        try:
            Id_value = int(course_fields_entries[0].get())
        except:
            messagebox.showerror(
                "Error", "'id' must be number", parent=fill_course_window
            )
            return  # exit if id is not a number

        course_id = Id_value
        course_name = course_fields_entries[1].get()
        score = course_fields_entries[2].get()

        # check if the course name already exists in the course_names table
        check_query = "SELECT id FROM course_names WHERE course_name = %s"
        check_data = (course_name,)
        cursor.execute(check_query, check_data)
        existing_course = cursor.fetchone()

        if existing_course:
            # Use the existing course ID
            course_id = existing_course[0]

        else:
            # Insert the new course name into the course_names table
            course_names_query = (
                "INSERT INTO course_names (id,course_name) VALUES (%s,%s)"
            )
            course_names_data = (course_id, course_name)
            cursor.execute(course_names_query, course_names_data)
            conn.commit()

        try:
            # Insert the course into the course table
            course_query = (
                "INSERT INTO course (course_id, student_id, score) VALUES (%s, %s, %s)"
            )
            course_data = (course_id, student_id, score)
            cursor.execute(course_query, course_data)
            conn.commit()
            messagebox.showinfo(
                "", "Course added successfully.", parent=fill_course_window
            )
            refresh_course_data(course_table, cursor)
        except Exception as e:
            conn.rollback()
            messagebox.showerror(
                "Error",
                f"Error occurred during entry: {str(e)}",
                parent=fill_course_window,
            )

    fill_course(
        window_title="Fill Course Details",
        button_text="Add",
        button_command=add,
        course_labels_config=course_labels_config,
        cursor=cursor,
    )


# change student score
def modify_course(cursor, conn, course_table, student_table):
    selected_course = course_table.item(course_table.focus())["values"]
    selected_student = student_table.item(student_table.focus())["values"]

    if not selected_student:
        messagebox.showerror("Error", "Please select a student first.")
        return

    if not selected_course:
        messagebox.showerror("Error", "Please select a course to update.")
        return

    def update_score():
        response = messagebox.askyesno(
            "Confirm Update",
            "Are you sure you want to update this course?",
            parent=fill_course_window,
        )

        if response:
            query = """UPDATE course
                        SET score = %s
                        WHERE (course_id = %s)
                        AND (student_id = %s)
                    """
            new_score = score.get()
            args = (
                new_score,
                selected_course[0],
                student_id,
            )

            try:
                cursor.execute(query, args)
                conn.commit()
                fill_course_window.destroy()

            except Exception as e:
                conn.rollback()
                print(str(e))
                messagebox.showerror(
                    "Error",
                    f"Error occurred during update: {str(e)}",
                    parent=fill_course_window,
                )
        refresh_course_data(course_table, cursor)

    # Create the fill_course_window
    fill_course_window = Toplevel()
    fill_course_window.title("Update Score")
    fill_course_window.geometry("400x200+300+200")
    fill_course_window.resizable(False, False)
    fill_course_window.grab_set()
    fill_course_window.attributes("-topmost", "true")

    # Create a label and entry for the score
    Label(fill_course_window, text="Score", font=("Arial", 16, "bold")).grid(
        row=0, column=0, padx=20, pady=20, sticky="W"
    )
    score = Entry(fill_course_window, font=("Arial", 16, "bold"), bd=2)
    score.grid(row=0, column=1)

    # Set the default value for the score of the selected course
    score.insert(0, str(selected_course[2]))

    # Create the update button
    button = Button(
        fill_course_window,
        text="Update",
        width=10,
        font=("Arial", 14, "bold"),
        command=update_score,
    )
    button.grid(row=1, columnspan=2, pady=10)


# delete student course details
def delete_course(cursor, conn, course_table, student_table):
    selected_course = course_table.item(course_table.focus())["values"]
    selected_student = student_table.item(student_table.focus())["values"]

    if not selected_student:
        messagebox.showerror("Error", "Please select a student first.")
        return

    if not selected_course:
        messagebox.showerror("Error", "Please select a course to delete.")
        return

    response = messagebox.askyesno(
        "Confirm Deletion", "Are you sure you want to delete this record?"
    )

    if response:
        query = """DELETE FROM course 
                    WHERE (course_id = %s)
                    AND (student_id = %s)
                """

        args = (selected_course[0], selected_student[0])

        cursor.execute(query, args)
        conn.commit()

    refresh_course_data(course_table, cursor)
