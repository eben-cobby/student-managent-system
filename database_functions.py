from tkinter import Toplevel, Entry, Label, Button, messagebox
import mysql.connector as sql

# code for connecting to the database...
def connect_database(root, left_buttons, right_buttons, refresh_data):
        # Create database info input window
    database_window = Toplevel(root)
    database_window.title("Connect to Database")
    database_window.geometry("450x300+300+200")
    database_window.resizable(False, False)
    database_window.grab_set()
    database_window.attributes("-topmost", "true")

    # Function to run when the "Connect" button is clicked
    def mysql_connect():
        global cursor, conn
        try:
            conn = sql.connect(
                # host=hostname_entry.get(),
                # user=user_entry.get(),
                # password=password_entry.get(),
                host="localhost",
                user="root",
                password="Abigail@123",
            )
            cursor = conn.cursor()

        except:
            messagebox.showerror("Error", "Invalid Details", parent=database_window)
            return

        try:
            # Create the student_management_database if it doesn't exist
            database_creation_query = '''
            CREATE DATABASE IF NOT EXISTS student_management_database;
            '''
            cursor.execute(database_creation_query)

            # Set the current database to student_management_database
            conn.database = "student_management_database"

            # Create the student table if it doesn't exist
            student_table_creation_query = '''
            CREATE TABLE IF NOT EXISTS student (
                id INT PRIMARY KEY AUTO_INCREMENT,
                firstname VARCHAR(255) NOT NULL,
                surname VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                programme VARCHAR(255) NOT NULL
            );
            '''
            cursor.execute(student_table_creation_query)

            # Create the course_names table if it doesn't exist
            course_names_table_creation_query = '''
            CREATE TABLE IF NOT EXISTS course_names (
                id INT PRIMARY KEY NOT NULL,
                course_name VARCHAR(255) NOT NULL UNIQUE
            );
            '''
            cursor.execute(course_names_table_creation_query)

            # Create the course table if it doesn't exist
            course_table_creation_query = '''
            CREATE TABLE IF NOT EXISTS course (
                id INT PRIMARY KEY AUTO_INCREMENT,
                course_id INT NOT NULL,
                student_id INT NOT NULL,
                score INT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES student(id),
                FOREIGN KEY (course_id) REFERENCES course_names(id)
            );
            '''
            cursor.execute(course_table_creation_query)

            conn.commit()

            messagebox.showinfo(
                "Success", "Database Connection established", parent=database_window
            )
            database_window.destroy()

            # Enable buttons after successful database connection
            for button in left_buttons:
                button.config(state="normal")
            
            for button in right_buttons:
                button.config(state="normal")

            refresh_data()

        except sql.Error as e:
            messagebox.showerror(
                "Error",
                f"Error connecting to the database: {str(e)}",
                parent=database_window,
            )

    # connect_button.config(state=DISABLED)
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