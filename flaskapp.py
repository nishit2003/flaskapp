
# Nishit Grover(M15329773)

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3
import os


app = Flask(__name__)

# Configuration for file upload
UPLOAD_FOLDER = '/home/ubuntu/flaskapp/uploads'  # Absolute path
# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt'}
# Set the upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check if the file extension is allowed
def allowed_file(filename):
    # Check if the file extension is in the allowed set
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize the SQLite database
def init_db():
    # Connect to the SQLite database
    conn = sqlite3.connect('/home/ubuntu/flaskapp/users.db')  # Absolute path
    # Create a cursor object
    c = conn.cursor()
    # Create a table to store user data (if not exists)
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    file_path TEXT,
                    word_count INTEGER
                )''')
    # Commit the changes
    conn.commit()
    # Close the connection
    conn.close()
# Initialize the database
init_db()

# Define the routes
@app.route('/')
# Define the home route
def home():
    # Render the welcome page
    return render_template('welcome.html')

# Define the register route
@app.route('/register', methods=['GET', 'POST'])
# Define the register function
def register():
    # Check if the request method is POST
    if request.method == 'POST':
        # Get the form data
        # Get the username
        username = request.form['username']
        # Get the password
        password = request.form['password']
        # Get the first name
        first_name = request.form['first_name']
        # Get the last name
        last_name = request.form['last_name']
        # Get the email
        email = request.form['email']

        # Check if the file is uploaded
        file = request.files['file']
        # Initialize the file path and word count
        file_path = None
        # Initialize the word count
        word_count = None

        # Save the file to the uploads folder
        if file and allowed_file(file.filename):
            # Secure the filename
            filename = secure_filename(file.filename)
            # Save the file to the uploads folder
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # Save the file
            file.save(file_path)
            # Count the number of words in the file
            with open(file_path, 'r') as f:
                # Read the file content
                file_content = f.read()
            # Count the number of words
            word_count = len(file_content.split())

        # Connect to the SQLite database
        conn = sqlite3.connect('/home/ubuntu/flaskapp/users.db')  # Absolute path
        # Create a cursor object
        c = conn.cursor()
        # Insert the user data into the database
        try:
            # Insert the user data into the database
            c.execute("INSERT INTO users (username, password, first_name, last_name, email, file_path, word_count) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                      (username, password, first_name, last_name, email, file_path, word_count))
            # Commit the changes
            conn.commit()
        # Handle the exception
        except sqlite3.IntegrityError:
            # Return an error message
            return 'Oops! User already exists in the database!'
        # Close the connection
        finally:
            # Close the connection
            conn.close()
        # Redirect to the profile page
        return redirect(url_for('profile', username=username))
    # Render the registration page
    return render_template('registration.html')

# Define the login route
@app.route('/login', methods=['GET', 'POST'])
# Define the login function
def login():
    # Check if the request method is POST
    if request.method == 'POST':
        # Get the form data
        # Get the username
        username = request.form['username']
        # Get the password
        password = request.form['password']

        # Connect to the SQLite database
        conn = sqlite3.connect('/home/ubuntu/flaskapp/users.db')  # Absolute path
        # Create a cursor object
        c = conn.cursor()
        # Fetch the user data from the database
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        # Fetch the user data
        user = c.fetchone()
        # Close the connection
        conn.close()

        # Check if the user exists
        if user:
            # Redirect to the profile page
            return redirect(url_for('profile', username=username))
        # Return an error message
        else:
            return 'Error! Invalid Login Credentials!'
    # Render the login page
    return render_template('login.html')

# Define the profile route
@app.route('/profile/<username>')
# Define the profile function
def profile(username):
    # Connect to the SQLite database
    conn = sqlite3.connect('/home/ubuntu/flaskapp/users.db')  # Absolute path
    # Create a cursor object
    c = conn.cursor()
    # Fetch the user data from the database
    c.execute("SELECT first_name, last_name, email, file_path, word_count FROM users WHERE username=?", (username,))
    # Fetch the user data
    user = c.fetchone()
    # Close the connection
    conn.close()

    # Check if the user exists
    if user:
        # Unpack the user data, i.e., first_name, last_name, email, file_path, word_count
        first_name, last_name, email, file_path, word_count = user
        # Render the profile page, passing the user data, i.e., username, first_name, last_name, email, file_path, word_count
        return render_template('profile.html', username=username, first_name=first_name, last_name=last_name, 
                               email=email, file_path=file_path, word_count=word_count)
    # Return an error message
    else:
        return 'Error! User Not Found!'
    
# Define the download route for the file to get downloaded (word count file)
@app.route('/download/<username>')
# Define the download function
def download_file(username):
    # Connect to the SQLite database
    conn = sqlite3.connect('/home/ubuntu/flaskapp/users.db')  # Absolute path
    # Create a cursor object
    c = conn.cursor()
    # Fetch the file path from the database
    c.execute("SELECT file_path FROM users WHERE username=?", (username,))
    # Fetch the file path
    file_path = c.fetchone()
    # Close the connection
    conn.close()

    # Check if the file path exists
    if file_path and file_path[0]:  # Check if file_path is not None and contains a value
        # Return the file for download
        return send_from_directory(directory=os.path.dirname(file_path[0]), 
                                   path=os.path.basename(file_path[0]), 
                                   as_attachment=True)
    # Return an error message, if the file is not found
    return 'Error! File Not Found!'

# Finally, let's run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
