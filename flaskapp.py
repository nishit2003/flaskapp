# Nishit Grover(M15329773)

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3
import os

# Create Flask application instance
app = Flask(__name__)

# Configure file upload settings
UPLOAD_FOLDER = '/home/ubuntu/flaskapp/uploads'  # Directory for file uploads
ALLOWED_EXTENSIONS = {'txt'}  # Allowed file types for upload
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Set the upload folder in app configuration

# Function to check if the uploaded file type is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to initialize the SQLite database
def init_db():
    # Connect to the SQLite database
    conn = sqlite3.connect('/home/ubuntu/flaskapp/users.db')  # Absolute path to database
    c = conn.cursor()
    # Create a table to store user data if it doesn't already exist
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
    # Commit changes and close the connection
    conn.commit()
    conn.close()

# Initialize the database when the application starts
init_db()

# Route for the home page
@app.route('/')
def home():
    return render_template('welcome.html')  # Render the welcome page

# Route for the user registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get registration form data
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']

        # Handle file upload if provided
        file = request.files['file']
        file_path = None
        word_count = None

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)  # Secure the uploaded file name
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)  # Save the file
            # Count words in the uploaded file
            with open(file_path, 'r') as f:
                file_content = f.read()
            word_count = len(file_content.split())

        # Insert user data into the database
        conn = sqlite3.connect('/home/ubuntu/flaskapp/users.db')  # Absolute path to database
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password, first_name, last_name, email, file_path, word_count) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                      (username, password, first_name, last_name, email, file_path, word_count))
            conn.commit()
        except sqlite3.IntegrityError:
            return 'Oops! User already exists in the database!'  # Handle duplicate username
        finally:
            conn.close()
        return redirect(url_for('profile', username=username))  # Redirect to profile page after successful registration
    return render_template('registration.html')  # Render registration page for GET request

# Route for the user login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get login form data
        username = request.form['username']
        password = request.form['password']

        # Check credentials against the database
        conn = sqlite3.connect('/home/ubuntu/flaskapp/users.db')  # Absolute path to database
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            return redirect(url_for('profile', username=username))  # Redirect to profile if credentials are valid
        else:
            return 'Error! Invalid Login Credentials!'  # Handle invalid login
    return render_template('login.html')  # Render login page for GET request

# Route for the user profile page
@app.route('/profile/<username>')
def profile(username):
    # Fetch user data from the database
    conn = sqlite3.connect('/home/ubuntu/flaskapp/users.db')  # Absolute path to database
    c = conn.cursor()
    c.execute("SELECT first_name, last_name, email, file_path, word_count FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()

    if user:
        # Display user profile if found
        first_name, last_name, email, file_path, word_count = user
        return render_template('profile.html', username=username, first_name=first_name, last_name=last_name, 
                               email=email, file_path=file_path, word_count=word_count)
    else:
        return 'Error! User Not Found!'  # Handle case where user is not found

# Route for downloading a file uploaded by the user
@app.route('/download/<username>')
def download_file(username):
    # Fetch the file path from the database
    conn = sqlite3.connect('/home/ubuntu/flaskapp/users.db')  # Absolute path to database
    c = conn.cursor()
    c.execute("SELECT file_path FROM users WHERE username=?", (username,))
    file_path = c.fetchone()
    conn.close()

    if file_path and file_path[0]:  # Ensure file exists
        return send_from_directory(directory=os.path.dirname(file_path[0]), 
                                   path=os.path.basename(file_path[0]), 
                                   as_attachment=True)  # Send file for download
    return 'Error! File Not Found!'  # Handle case where file is not found

# Run the Flask app in debug mode
if __name__ == '__main__':
    app.run(debug=True)
