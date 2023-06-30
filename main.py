from tkinter import *
import time
from tkinter import ttk, messagebox
import mysql.connector as sql
from student_functions import *
from course_functions import *

# global variables
student_labels_config = ["Id", "Firstname", "Surname", "Email", "Programme"]
course_labels_config = ["Id", "Course", "Score", "Grade"]


# add clock to main window
def clock():
    date = time.strftime("%d-%m-%Y")
    current_time = time.strftime("%H:%M:%S")
    date_time_label.config(text=f"Date: {date} \nCurrent Time: {current_time}")
    date_time_label.after(1000, clock)


# code for connecting to the database
def connect_database():
    # create database info input window
    database_window = Toplevel(window)
    database_window.title("Connect to Database")
    database_window.geometry("450x300+300+200")
    database_window.resizable(False, False)
    database_window.grab_set()
    database_window.attributes("-topmost", "true")

    # function to run when the "Connect" button is clicked
    def mysql_connect():
        global cursor, conn
        try:
            conn = sql.connect(
                host=hostname_entry.get(),
                user=user_entry.get(),
                password=password_entry.get(),
            )
            cursor = conn.cursor()

        except Exception as e:
            messagebox.showerror(
                "", f"Encountered error: {str(e)}", parent=database_window
            )
            return

        # create the student_management_database if it doesn't exist
        try:
            database_creation_query = """
            CREATE DATABASE IF NOT EXISTS student_management_database;
            """
            cursor.execute(database_creation_query)

            # set the current database to student_management_database
            conn.database = "student_management_database"

            # create the student table if it doesn't exist
            student_table_creation_query = """
            CREATE TABLE IF NOT EXISTS student (
                id INT PRIMARY KEY AUTO_INCREMENT,
                firstname VARCHAR(255) NOT NULL,
                surname VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                programme VARCHAR(255) NOT NULL
            );
            """
            cursor.execute(student_table_creation_query)

            # create the course_names table if it doesn't exist
            course_names_table_creation_query = """
            CREATE TABLE IF NOT EXISTS course_names (
                id INT PRIMARY KEY NOT NULL,
                course_name VARCHAR(255) NOT NULL UNIQUE
            );
            """
            cursor.execute(course_names_table_creation_query)

            # create the course table if it doesn't exist
            course_table_creation_query = """
            CREATE TABLE IF NOT EXISTS course (
                id INT PRIMARY KEY AUTO_INCREMENT,
                course_id INT NOT NULL,
                student_id INT NOT NULL,
                score INT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES student(id),
                FOREIGN KEY (course_id) REFERENCES course_names(id)
            );
            """
            cursor.execute(course_table_creation_query)

            conn.commit()

            messagebox.showinfo(
                "Success", "Database Connection established", parent=database_window
            )
            database_window.destroy()

            # enable buttons after successful database connection
            for button in left_buttons:
                button.config(state="normal")
            for button in middle_buttons:
                button.config(state="normal")

            refresh_student_data(student_table, cursor)

        except sql.Error as e:
            messagebox.showerror(
                "Error",
                f"Error connecting to the database: {str(e)}",
                parent=database_window,
            )

    hostname_label = Label(
        database_window, text="Host Name:", font=("arial", 16, "bold")
    )
    hostname_label.grid(row=0, column=0, padx=20, pady=20)
    hostname_entry = Entry(database_window, font=("arial", 16, "bold"), bd=2)
    hostname_entry.grid(row=0, column=1)

    user_label = Label(database_window, text="Username:", font=("arial", 16, "bold"))
    user_label.grid(row=1, column=0, padx=20, pady=20)
    user_entry = Entry(database_window, font=("arial", 16, "bold"), bd=2)
    user_entry.grid(row=1, column=1)

    password_label = Label(
        database_window, text="Password:", font=("arial", 16, "bold")
    )
    password_label.grid(row=2, column=0, padx=20, pady=20)
    password_entry = Entry(database_window, font=("arial", 16, "bold"), bd=2)
    password_entry.grid(row=2, column=1)

    connect_button = Button(
        database_window,
        text="Connect",
        width=10,
        font=("arial", 14, "bold"),
        command=mysql_connect,
    )
    connect_button.grid(row=3, columnspan=2, pady=10)


# create and configure the main
window = Tk()
window.geometry("1280x700")
window.title("School Management System")
window.resizable(False, False)

# create and place the date and time label
date_time_label = Label(window, font=("arial", 16, "bold"))
date_time_label.place(x=40, y=5)
clock()

# create and place the main heading label
slider_label = Label(
    window, text="Student Management System", font=("arial", 18, "bold")
)
slider_label.place(x=450, y=5)

# create and place the database window
connect_button = Button(
    window,
    text="Connect to Database",
    font=("arial", 14, "bold"),
    command=connect_database,
)
connect_button.place(x=900, y=5)

# create and place the left frame for left set of buttons (for student table)
left_frame = Frame(window)
left_frame.grid(row=1, column=0, padx=40, pady=80)

# create and place student database CRUD buttons in the left_frame
left_buttons = []

add_student_button = Button(
    left_frame,
    text="Add Student",
    width=13,
    font=("arial", 14, "bold"),
    state=DISABLED,
    command=lambda: add_student(cursor, conn, student_table),
)
add_student_button.grid(row=1, pady=20)
left_buttons.append(add_student_button)

search_student_button = Button(
    left_frame,
    text="Search Student",
    width=13,
    font=("arial", 14, "bold"),
    state=DISABLED,
    command=lambda: search_student(cursor, student_table),
)
search_student_button.grid(row=2, pady=20)
left_buttons.append(search_student_button)

delete_student_button = Button(
    left_frame,
    text="Delete Student",
    width=13,
    font=("arial", 14, "bold"),
    state=DISABLED,
    command=lambda: delete_student(cursor, conn, student_table),
)
delete_student_button.grid(row=3, pady=20)
left_buttons.append(delete_student_button)

modify_student_button = Button(
    left_frame,
    text="Modify Record",
    width=13,
    font=("arial", 14, "bold"),
    state=DISABLED,
    command=lambda: modify_student(cursor, conn, student_table),
)
modify_student_button.grid(row=4, pady=20)
left_buttons.append(modify_student_button)

refresh_data_button = Button(
    left_frame,
    text="Refresh Data",
    width=13,
    font=("arial", 14, "bold"),
    state=DISABLED,
    command=lambda: refresh_student_data(student_table, cursor),
)
refresh_data_button.grid(row=5, pady=20)
left_buttons.append(refresh_data_button)

export_data_button = Button(
    left_frame,
    text="Export Data",
    width=13,
    font=("arial", 14, "bold"),
    state=DISABLED,
    command=lambda: export_data(student_table),
)
export_data_button.grid(row=6, pady=20)
left_buttons.append(export_data_button)

exit_button = Button(
    left_frame,
    text="Exit",
    width=13,
    font=("arial", 14, "bold"),
    state=DISABLED,
    command=lambda: exit_application(window),
)
exit_button.grid(row=7, pady=20)
left_buttons.append(exit_button)

# create a frame for placing student table and scroll bars in
student_frame = Frame(window)
student_frame.place(x=240, y=80, width=500, height=600)

# create the horizontal and vertical scroll bars for the student table
scrollbar_x = Scrollbar(student_frame, orient=HORIZONTAL, width=15)
scrollbar_y = Scrollbar(student_frame, orient=VERTICAL, width=15)


student_table = ttk.Treeview(
    student_frame,
    columns=student_labels_config,
    xscrollcommand=scrollbar_x.set,
    yscrollcommand=scrollbar_y.set,
    selectmode="extended",
)

# show heading titles in table
for i in student_labels_config:
    student_table.heading(i, text=i)
student_table.config(show="headings")

# adjust treeview column width
student_table.column("Id", width=100)
student_table.column("Firstname", width=100)
student_table.column("Surname", width=100)
student_table.column("Email", width=150)

scrollbar_x.config(command=student_table.xview)
scrollbar_y.config(command=student_table.yview)
scrollbar_x.pack(side=BOTTOM, fill=X)
scrollbar_y.pack(side=RIGHT, fill=Y)

student_table.pack(fill=BOTH, expand=True)

# create and place the left frame for middle set of buttons(for course table)
third_frame = Frame(window)
third_frame.place(x=760, y=80, width=280, height=600)


# create a list of database CRUD buttons in the third frame
middle_buttons = []

add_course_button = Button(
    third_frame,
    text="Add Course",
    width=13,
    font=("arial", 14, "bold"),
    state=DISABLED,
    command=lambda: add_course(cursor, conn, course_table, student_table),
)
add_course_button.grid(row=1, pady=20)
middle_buttons.append(add_course_button)

modify_course_button = Button(
    third_frame,
    text="Modify Course",
    width=13,
    font=("arial", 14, "bold"),
    state=DISABLED,
    command=lambda: modify_course(cursor, conn, course_table, student_table),
)
modify_course_button.grid(row=2, pady=20)
middle_buttons.append(modify_course_button)

delete_course_button = Button(
    third_frame,
    text="Delete Course",
    width=13,
    font=("arial", 14, "bold"),
    state=DISABLED,
    command=lambda: delete_course(cursor, conn, course_table, student_table),
)
delete_course_button.grid(row=3, pady=20)
middle_buttons.append(delete_course_button)


# create and place the frame for course table and scroll bars
course_frame = Frame(window)
course_frame.place(x=940, y=80, width=280, height=600)

# create the horizontal and vertical scroll bars for the course table
scrollbar_x = Scrollbar(course_frame, orient=HORIZONTAL, width=15)
scrollbar_y = Scrollbar(course_frame, orient=VERTICAL, width=15)

# create the course table
course_table = ttk.Treeview(
    course_frame,
    columns=course_labels_config,
    xscrollcommand=scrollbar_x.set,
    yscrollcommand=scrollbar_y.set,
    selectmode="extended",
)
scrollbar_x.config(command=course_table.xview)
scrollbar_y.config(command=course_table.yview)
scrollbar_x.pack(side=BOTTOM, fill=X)
scrollbar_y.pack(side=RIGHT, fill=Y)
course_table.pack(fill=BOTH, expand=True)

# configure the heading titles in the course table
for i in course_labels_config:
    course_table.heading(i, text=i)
course_table.config(show="headings")
course_table.column("Id", width=20)
course_table.column("Course", width=120)
course_table.column("Score", width=30)
course_table.column("Grade", width=30)


# bind the student_table TreeviewSelect event to the get_course data function
student_table.bind(
    "<<TreeviewSelect>>",
    lambda event: get_course_data(course_table, cursor, student_table, event),
)

# configure the Treeview style
style = ttk.Style()
style.configure("Treeview", rowheight=35, font=("arial", 12, "normal"))


window.mainloop()
