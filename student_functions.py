from tkinter import *
from tkinter import messagebox, filedialog
import csv

student_labels_config = ["Id", "Firstname", "Surname", "Email", "Programme"]


# function to get data from student table  and display once query has been run by other functions
def get_student_data(student_table, cursor):
    student_table.delete(
        *student_table.get_children()
    )  # clear table before fetching to prevent piling up
    fetched_data = cursor.fetchall()

    for data in fetched_data:
        student_table.insert("", "end", values=data)


# function to refresh data in the student table
def refresh_student_data(student_table, cursor):
    query = "select * from student"
    cursor.execute(query)
    get_student_data(student_table, cursor)


def fill_student(
    window_title,
    button_text,
    button_command,
    student_labels_config,
    student_table,
    show_default_values=False,
):
    global student_fields_entries, fill_student_window
    student_fields_entries = []

    fill_student_window = Toplevel()
    fill_student_window.title(window_title)
    fill_student_window.geometry("450x500+300+200")
    fill_student_window.resizable(False, False)
    fill_student_window.grab_set()
    fill_student_window.attributes("-topmost", "true")

    Label(fill_student_window, text="Student ID", font=("arial", 16, "bold")).grid(
        row=0, column=0, padx=20, pady=20, sticky="w"
    )

    for i, text in enumerate(student_labels_config[1:]):
        Label(fill_student_window, text=text, font=("arial", 16, "bold")).grid(
            row=i + 1, column=0, padx=20, pady=20, sticky="w"
        )

    for i, text in enumerate(student_labels_config[:-1]):
        entry = Entry(fill_student_window, font=("arial", 16, "bold"), bd=2)
        entry.grid(row=i, column=1)
        student_fields_entries.append(entry)

    button = Button(
        fill_student_window,
        text=button_text,
        width=10,
        font=("arial", 14, "bold"),
        command=button_command,
    )
    button.grid(row=len(student_labels_config) + 1, columnspan=2, pady=10)

    clicked = StringVar()  # construct a string variable selected programme list
    programme_options = [
        "Mechanical Engineering",
        "Computer Science",
        "Civil Engineering",
        "Mining Engineering",
        "Electrical Engineering",
    ]
    programme_list = OptionMenu(fill_student_window, clicked, *programme_options)
    programme_list.config(font=("arial", 14), width=20, height=1)
    programme_list.grid(row=4, column=1)
    student_fields_entries.append(clicked)

    if show_default_values:
        selected_student = student_table.item(student_table.focus())["values"]

        if not selected_student:
            fill_student_window.destroy()
            messagebox.showerror("Error", "Please select a record to update")
        else:
            for i, value in enumerate(selected_student[:-1]):
                student_fields_entries[i].insert(0, value)
            student_fields_entries[-1].set(selected_student[-1])


def add_student(cursor, conn, student_table):
    def add_student_data():
        if any(entry.get() == "" for entry in student_fields_entries):
            messagebox.showerror(
                "Error", "All fields are required", parent=fill_student_window
            )
            return

        try:
            Id_value = int(student_fields_entries[0].get())
        except ValueError:
            messagebox.showerror(
                "Error", "'id' must be a number", parent=fill_student_window
            )
            return  # exit if id is not a number

        try:
            query = "INSERT INTO student VALUES (%s, %s, %s, %s, %s)"
            args = (
                Id_value,
                student_fields_entries[1].get(),
                student_fields_entries[2].get(),
                student_fields_entries[3].get(),
                student_fields_entries[4].get(),
            )
            cursor.execute(query, args)
            conn.commit()
            question = messagebox.askyesno(
                "Confirm", "Do you want to clear the form", parent=fill_student_window
            )
        except Exception as e:
            conn.rollback()
            messagebox.showerror(
                "Error",
                f"Error occurred during update: {str(e)}",
                parent=fill_student_window,
            )

        if question:
            for entry in student_fields_entries[:-1]:
                entry.delete(0, "end")
            student_fields_entries[-1].set("")

        query = "SELECT * FROM student"
        cursor.execute(query)
        get_student_data(student_table, cursor)

    fill_student(
        window_title="Add Student",
        button_text="ADD",
        button_command=add_student_data,
        student_labels_config=student_labels_config,
        student_table=student_table,
    )


# search for student
def search_student(cursor, student_table):
    # function to run when the "SUBMIT" button on main window is clicked
    def search_student_data():
        query = """select * from student
                    WHERE (Id LIKE %s)
                    OR (Firstname LIKE %s)
                    OR (Surname LIKE %s)
                    OR (Email LIKE %s)
                    OR (Programme LIKE %s)"""

        args = (
            "%" + student_fields_entries[0].get() + "%"
            if student_fields_entries[0].get()
            else "",
            "%" + student_fields_entries[1].get() + "%"
            if student_fields_entries[1].get()
            else "",
            "%" + student_fields_entries[2].get() + "%"
            if student_fields_entries[2].get()
            else "",
            "%" + student_fields_entries[3].get() + "%"
            if student_fields_entries[3].get()
            else "",
            "%" + student_fields_entries[4].get() + "%"
            if student_fields_entries[4].get()
            else "",
        )

        cursor.execute(query, args)
        get_student_data(student_table, cursor)
        fill_student_window.destroy()

    fill_student(
        window_title="Search Records",
        button_text="SEARCH",
        button_command=search_student_data,
        student_labels_config=student_labels_config,
        student_table=student_table,
    )


# delete student record
def delete_student(cursor, conn, student_table):
    selected_student = student_table.item(student_table.selection())["values"]

    if not selected_student:
        messagebox.showerror("Error", "Please select a course to delete")
        return

    response = messagebox.askyesno(
        "Confirm Deletion", "Are you sure you want to delete this record?"
    )

    if response:
        query = """DELETE FROM student
                    WHERE (Id = %s)
                    AND (Firstname = %s)
                    AND (Surname = %s)
                    AND (Email = %s)
                    AND (Programme = %s)"""

        args = (
            selected_student[0],
            selected_student[1],
            selected_student[2],
            selected_student[3],
            selected_student[4],
        )

        cursor.execute(query, args)
        conn.commit()

        refresh_student_data(student_table, cursor)


# update/modify a student record
def modify_student(cursor, conn, student_table):
    selected_student = student_table.item(student_table.focus())["values"]
    if not selected_student:
        messagebox.showerror(
            "", "No record was selected. Please select a student to update record"
        )
        return

    def update_data():
        response = messagebox.askyesno(
            "Confirm Update",
            "Are you sure you want to update this record?",
            parent=fill_student_window,
        )

        if response:
            query = """UPDATE student
                        SET Id = %s, Firstname = %s, Surname = %s, Email = %s, Programme = %s
                        WHERE (Id = %s)
                        AND (Firstname = %s)
                        AND (Surname = %s)
                        AND (Email = %s)
                        AND (Programme = %s)"""

            args = (
                student_fields_entries[0].get() or selected_student[0],
                student_fields_entries[1].get() or selected_student[1],
                student_fields_entries[2].get() or selected_student[2],
                student_fields_entries[3].get() or selected_student[3],
                student_fields_entries[4].get() or selected_student[4],
                selected_student[0],
                selected_student[1],
                selected_student[2],
                selected_student[3],
                selected_student[4],
            )

            try:
                cursor.execute(query, args)
                conn.commit()
                fill_student_window.destroy()

            except Exception as e:
                conn.rollback()
                messagebox.showerror(
                    "Error",
                    f"Error occurred during update: {str(e)}",
                    parent=fill_student_window,
                )
        refresh_student_data(student_table, cursor)

    fill_student(
        window_title="Modify Student Record",
        button_text="UPDATE",
        button_command=update_data,
        student_labels_config=student_labels_config,
        student_table=student_table,
        show_default_values=True,
    )


# export all/selected student records as csv
def export_data(student_table):
    selected_items = student_table.selection()
    if not selected_items:
        response = messagebox.askyesno(
            "Select Record",
            "No record has been selected to export. Do you want to export all shown records?",
        )
        if not response:
            return
        selected_items = student_table.get_children()

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv")],
        title="Export Records",
    )

    if file_path:
        with open(file_path, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(student_labels_config)
            for item in selected_items:
                record = [
                    student_table.set(item, column)
                    for column in student_table["columns"]
                ]
                writer.writerow(record)
        messagebox.showinfo("Success", f"Records exported to: {file_path}")
    else:
        messagebox.showinfo("No records exported", "Export Cancelled")


# function to run when the "Exit" button on main window is clicked
def exit_application(window):
    window.destroy()
