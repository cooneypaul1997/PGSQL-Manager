import psycopg2
import tkinter as tk
from tkinter import messagebox, scrolledtext
from tkinter import ttk  # Import ttk for Treeview

# Declare global variables for credentials
global_host = None
global_user = None
global_password = None
global_port = None

# Function to fetch databases
def fetch_databases(host, user, password, port):
    try:
        # Connect to PostgreSQL server with provided credentials
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            port=port
        )

        # Create a cursor to execute SQL commands
        cursor = connection.cursor()

        # Execute SQL to get all databases
        cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")

        # Fetch all rows (databases)
        databases = cursor.fetchall()

        # Clear the listbox before inserting new items
        listbox.delete(0, tk.END)

        # Update the listbox with database names
        for db in databases:
            listbox.insert(tk.END, db[0])

        # Close cursor and connection
        cursor.close()
        connection.close()

    except Exception as e:
        messagebox.showerror("Error", f"Error connecting to the database:\n{e}")

# Function to open the credentials popup
def open_credentials_popup():
    # Create a new popup window
    popup = tk.Toplevel(root)
    popup.title("Enter Connection Credentials")
    
    # Labels and Entry widgets for credentials
    tk.Label(popup, text="Host:").grid(row=0, column=0)
    tk.Label(popup, text="User:").grid(row=1, column=0)
    tk.Label(popup, text="Password:").grid(row=2, column=0)
    tk.Label(popup, text="Port:").grid(row=3, column=0)

    host_entry = tk.Entry(popup)
    user_entry = tk.Entry(popup)
    password_entry = tk.Entry(popup, show="*")
    port_entry = tk.Entry(popup)

    host_entry.grid(row=0, column=1)
    user_entry.grid(row=1, column=1)
    password_entry.grid(row=2, column=1)
    port_entry.grid(row=3, column=1)

    # Prefill some values (optional)
    host_entry.insert(0, "localhost")
    port_entry.insert(0, "5432")

    # Function to handle submission
    def submit_credentials():
        global global_host, global_user, global_password, global_port
        
        global_host = host_entry.get()
        global_user = user_entry.get()
        global_password = password_entry.get()
        global_port = port_entry.get()
        popup.destroy()  # Close the popup
        fetch_databases(global_host, global_user, global_password, global_port)  # Fetch databases using the entered credentials

    # Button to submit the credentials
    submit_button = tk.Button(popup, text="Submit", command=submit_credentials)
    submit_button.grid(row=4, columnspan=2, pady=10)

# Function to open the query editor for a selected database
def open_query_editor(db_name):
    # Query window popup
    query_window = tk.Toplevel(root)
    query_window.title(f"New Query - {db_name}")

    # Text area for writing SQL queries
    query_text = scrolledtext.ScrolledText(query_window, width=80, height=15)
    query_text.pack(padx=10, pady=10)

    # Table (Treeview) for displaying query results
    result_table = ttk.Treeview(query_window, columns=(), show='headings')
    result_table.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Function to execute the query
    def execute_query():
        query = query_text.get("1.0", tk.END).strip()
        try:
            # Connect to the selected database
            connection = psycopg2.connect(
                host=global_host, user=global_user, password=global_password, port=global_port, dbname=db_name
            )
            cursor = connection.cursor()
            cursor.execute(query)

            # Fetch and display results
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]  # Get column names

            # Clear existing data in the Treeview table
            result_table.delete(*result_table.get_children())
            result_table['columns'] = columns

            # Update headings for the Treeview table
            for col in columns:
                result_table.heading(col, text=col)
                result_table.column(col, width=100)

            # Insert results into the Treeview table
            for row in results:
                result_table.insert("", tk.END, values=row)

            cursor.close()
            connection.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error executing query:\n{e}")

    # Button to execute the query
    execute_button = tk.Button(query_window, text="Execute", command=execute_query)
    execute_button.pack(pady=5)

# Function to handle right-click on the listbox
def on_right_click(event):
    # Get the index of the clicked item
    try:
        index = listbox.nearest(event.y)
        db_name = listbox.get(index)
        # Display a context menu with the "New Query" option
        context_menu = tk.Menu(root, tearoff=0)
        context_menu.add_command(label="New Query", command=lambda: open_query_editor(db_name))
        context_menu.post(event.x_root, event.y_root)
    except Exception as e:
        messagebox.showerror("Error", f"Error handling right-click:\n{e}")

# Tkinter GUI setup
root = tk.Tk()
root.title("PostgreSQL Databases")

# Frame for the listbox
frame = tk.Frame(root)
frame.pack(pady=20)

# Scrollbar for the listbox
scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Listbox to display databases
listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, width=50, height=10)
listbox.pack()

# Bind right-click event to the listbox
listbox.bind("<Button-3>", on_right_click)

# Configure the scrollbar
scrollbar.config(command=listbox.yview)

# Button to open credentials popup
fetch_button = tk.Button(root, text="Connect to PostgreSQL", command=open_credentials_popup)
fetch_button.pack(pady=10)

# Start Tkinter event loop
root.mainloop()
