# ============================================================
# FLASK FULL FEATURES APP — Beginner Friendly with Comments
# ============================================================
# Features included:
# 1.  User Registration & Login (Authentication)
# 2.  Dashboard
# 3.  Profile (View & Edit)
# 4.  Image Upload (Profile Picture)
# 5.  Change Password
# 6.  Notes CRUD (Create, Read, Update, Delete)
# 7.  Search Notes
# 8.  Send Email
# 9.  Contact Form
# 10. Pagination
# 11. File Upload & Download
# 12. REST API (JSON response)
# 13. Error Handling (404, 500)
# 14. Logout
# ============================================================

import os
# os = built-in Python module to interact with operating system
# We use it for file paths, creating folders, etc.

from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify, send_from_directory
# jsonify = converts Python dictionary to JSON response (used for APIs)
# send_from_directory = sends a file from a folder to the user's browser (used for file download)

from flask_bcrypt import Bcrypt
# Bcrypt = securely hashes passwords so we never store plain text

from flask_mail import Mail, Message
# Mail = sets up email sending in Flask
# Message = creates an email message with subject, body, recipients

import pymysql
# pymysql = connects Python to MySQL database

from werkzeug.utils import secure_filename
# secure_filename = cleans uploaded file names to prevent security issues
# Example: "../../../etc/passwd" becomes "etc_passwd" (removes dangerous characters)

from ai_models import analyze_sentiment, summarize_text, detect_spam, predict_marks, predict_house_price
# These are our AI/ML functions from ai_models.py
# Each one is a trained machine learning model that makes predictions

# ============================================================
# APP CONFIGURATION
# ============================================================

# Create Flask application
app = Flask(__name__)

# Secret key for session encryption (keep this private in production)
app.secret_key = 'your_secret_key_here'

# Initialize Bcrypt for password hashing
bcrypt = Bcrypt(app)

# ---------- File Upload Configuration ----------
# Folder where uploaded files will be saved
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
# os.path.dirname(__file__) = gets the folder where this app.py file is located
# os.path.join() = joins path parts with correct separator (/ on Linux, \ on Windows)
# Result: /var/www/html/python/static/uploads

# Only allow these file types to be uploaded (for security)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt', 'doc', 'docx'}

# Tell Flask where to save uploads
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Maximum file size: 16 MB (in bytes) — prevents users from uploading huge files
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
# 16 * 1024 * 1024 = 16,777,216 bytes = 16 MB

# ---------- Email Configuration ----------
# These settings tell Flask how to connect to an email server
# Below is Gmail's SMTP server config — change to your email provider if different
app.config['MAIL_SERVER'] = 'smtp.gmail.com'       # Gmail's email server address
app.config['MAIL_PORT'] = 587                       # Port 587 is for TLS (secure email)
app.config['MAIL_USE_TLS'] = True                   # TLS = encrypts email during transmission
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'        # Your Gmail address
app.config['MAIL_PASSWORD'] = 'your_app_password_here'      # Gmail App Password (not your regular password)
# To get App Password: Google Account > Security > 2-Step Verification > App Passwords
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'  # Default "From" address

# Initialize Flask-Mail
mail = Mail(app)

# ---------- Pagination Configuration ----------
# How many items to show per page in lists
ITEMS_PER_PAGE = 5


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_db():
    """Creates and returns a new MySQL database connection"""
    return pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='python',
        cursorclass=pymysql.cursors.DictCursor
        # DictCursor makes results come as {'column': 'value'} instead of ('value',)
    )


def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    # 'photo.jpg'.rsplit('.', 1) splits from right: ['photo', 'jpg']
    # [1] gets 'jpg', .lower() makes it lowercase
    # Then checks if 'jpg' is in our ALLOWED_EXTENSIONS set
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    """Decorator that redirects to login page if user is not logged in"""
    # A decorator is a function that wraps another function to add extra behavior
    # @login_required before a route = only logged-in users can access it
    from functools import wraps
    @wraps(f)
    # @wraps(f) preserves the original function's name and docstring
    def decorated_function(*args, **kwargs):
        # *args = any positional arguments, **kwargs = any keyword arguments
        if 'user' not in session:
            # If user is not logged in, show message and redirect to login
            flash('Please log in first.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
        # If logged in, run the original function normally
    return decorated_function


# ============================================================
# 1. HOME PAGE
# ============================================================

@app.route('/')
def home():
    # If user is logged in, go to dashboard; otherwise go to login
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


# ============================================================
# 2. USER REGISTRATION
# ============================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        full_name = request.form['full_name']

        # Hash the password before storing
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')

        db = get_db()
        try:
            with db.cursor() as cursor:
                # Insert into users table (login credentials)
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (%s, %s)",
                    (username, hashed)
                )
                # Also create a profile for this user
                cursor.execute(
                    "INSERT INTO profiles (username, full_name, email) VALUES (%s, %s, %s)",
                    (username, full_name, email)
                )
            db.commit()
            flash("Registered successfully! Please log in.")
            return redirect(url_for('login'))
        except pymysql.err.IntegrityError:
            # This error means username already exists (UNIQUE constraint violation)
            db.rollback()
            # rollback() undoes any partial changes if the insert failed
            flash("Username already exists")
        finally:
            db.close()
    return render_template('register.html')


# ============================================================
# 3. USER LOGIN
# ============================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()
                # fetchone() returns one row or None if not found

            # Check: user exists AND password matches the stored hash
            if user and bcrypt.check_password_hash(user['password'], password):
                session['user'] = username
                # session stores data in encrypted browser cookie
                flash("Login successful!")
                return redirect(url_for('dashboard'))
            else:
                # Generic message for security — don't reveal if username or password is wrong
                flash("Invalid credentials")
        finally:
            db.close()
    return render_template('login.html')


# ============================================================
# 4. DASHBOARD
# ============================================================

@app.route('/dashboard')
@login_required
# @login_required = our custom decorator, redirects to login if not logged in
def dashboard():
    db = get_db()
    try:
        with db.cursor() as cursor:
            # Count total notes for this user
            cursor.execute("SELECT COUNT(*) as count FROM notes WHERE username = %s", (session['user'],))
            note_count = cursor.fetchone()['count']
            # fetchone() returns {'count': 5}, we get the number with ['count']

            # Get 5 most recent notes to show on dashboard
            cursor.execute(
                "SELECT * FROM notes WHERE username = %s ORDER BY created_at DESC LIMIT 5",
                (session['user'],)
            )
            # ORDER BY created_at DESC = newest first
            # LIMIT 5 = only get 5 rows
            recent_notes = cursor.fetchall()
            # fetchall() returns a list of all matching rows

            # Get user profile
            cursor.execute("SELECT * FROM profiles WHERE username = %s", (session['user'],))
            profile = cursor.fetchone()
    finally:
        db.close()

    return render_template('dashboard.html',
                           note_count=note_count,
                           recent_notes=recent_notes,
                           profile=profile)
    # We pass variables to the HTML template so it can display the data


# ============================================================
# 5. PROFILE — View & Edit
# ============================================================

@app.route('/profile')
@login_required
def profile():
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM profiles WHERE username = %s", (session['user'],))
            profile = cursor.fetchone()

            # If profile doesn't exist (old user), create one automatically
            if not profile:
                cursor.execute("INSERT INTO profiles (username) VALUES (%s)", (session['user'],))
                db.commit()
                cursor.execute("SELECT * FROM profiles WHERE username = %s", (session['user'],))
                profile = cursor.fetchone()
    finally:
        db.close()
    return render_template('profile.html', profile=profile)


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    db = get_db()
    try:
        if request.method == 'POST':
            full_name = request.form['full_name']
            email = request.form['email']
            phone = request.form['phone']
            bio = request.form['bio']

            with db.cursor() as cursor:
                # UPDATE modifies an existing row instead of inserting a new one
                cursor.execute(
                    "UPDATE profiles SET full_name=%s, email=%s, phone=%s, bio=%s WHERE username=%s",
                    (full_name, email, phone, bio, session['user'])
                )
            db.commit()
            flash("Profile updated successfully!")
            return redirect(url_for('profile'))

        # For GET request, load current profile data to pre-fill the form
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM profiles WHERE username = %s", (session['user'],))
            profile = cursor.fetchone()
    finally:
        db.close()
    return render_template('edit_profile.html', profile=profile)


# ============================================================
# 6. IMAGE UPLOAD — Profile Picture
# ============================================================

@app.route('/upload-image', methods=['GET', 'POST'])
@login_required
def upload_image():
    if request.method == 'POST':
        # request.files contains uploaded files
        # 'profile_image' matches the name="" attribute of the <input type="file"> in HTML
        if 'profile_image' not in request.files:
            flash('No file selected')
            return redirect(request.url)
            # request.url = the current page URL, so user stays on the same page

        file = request.files['profile_image']

        # If user clicks submit without selecting a file, browser sends empty filename
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)

        # Check if file type is allowed
        if file and allowed_file(file.filename):
            # secure_filename() removes dangerous characters from filename
            # Example: "../../hack.jpg" becomes "hack.jpg"
            filename = secure_filename(file.filename)

            # Add username prefix to avoid filename conflicts between users
            filename = session['user'] + '_' + filename

            # Save the file to our uploads folder
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # file.save() writes the uploaded file to disk

            # Update the profile_image column in database with the filename
            db = get_db()
            try:
                with db.cursor() as cursor:
                    cursor.execute(
                        "UPDATE profiles SET profile_image=%s WHERE username=%s",
                        (filename, session['user'])
                    )
                db.commit()
            finally:
                db.close()

            flash('Image uploaded successfully!')
            return redirect(url_for('profile'))
        else:
            flash('File type not allowed. Use: png, jpg, jpeg, gif')

    return render_template('upload_image.html')


# ============================================================
# 7. CHANGE PASSWORD
# ============================================================

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Check if new password and confirm password match
        if new_password != confirm_password:
            flash('New passwords do not match')
            return redirect(url_for('change_password'))

        db = get_db()
        try:
            with db.cursor() as cursor:
                # Get current stored password hash
                cursor.execute("SELECT password FROM users WHERE username = %s", (session['user'],))
                user = cursor.fetchone()

            # Verify the current password is correct before allowing change
            if user and bcrypt.check_password_hash(user['password'], current_password):
                new_hashed = bcrypt.generate_password_hash(new_password).decode('utf-8')
                with db.cursor() as cursor:
                    cursor.execute(
                        "UPDATE users SET password=%s WHERE username=%s",
                        (new_hashed, session['user'])
                    )
                db.commit()
                flash('Password changed successfully!')
                return redirect(url_for('profile'))
            else:
                flash('Current password is incorrect')
        finally:
            db.close()

    return render_template('change_password.html')


# ============================================================
# 8. NOTES — Full CRUD (Create, Read, Update, Delete)
# ============================================================

# --- LIST ALL NOTES (with Pagination) ---
@app.route('/notes')
@login_required
def notes():
    # Get current page number from URL like /notes?page=2
    # request.args.get() reads query parameters from the URL
    # default=1 means if no page parameter, use page 1
    # type=int converts the string "2" to integer 2
    page = request.args.get('page', 1, type=int)

    # Calculate offset: how many rows to skip
    # Page 1: skip 0, Page 2: skip 5, Page 3: skip 10 (if ITEMS_PER_PAGE = 5)
    offset = (page - 1) * ITEMS_PER_PAGE

    db = get_db()
    try:
        with db.cursor() as cursor:
            # Count total notes for pagination calculation
            cursor.execute("SELECT COUNT(*) as count FROM notes WHERE username = %s", (session['user'],))
            total = cursor.fetchone()['count']

            # Get notes for current page only
            cursor.execute(
                "SELECT * FROM notes WHERE username = %s ORDER BY created_at DESC LIMIT %s OFFSET %s",
                (session['user'], ITEMS_PER_PAGE, offset)
            )
            # LIMIT 5 = get only 5 rows
            # OFFSET 10 = skip the first 10 rows
            all_notes = cursor.fetchall()
    finally:
        db.close()

    # Calculate total number of pages
    # Example: 13 total notes / 5 per page = 2.6, but we need 3 pages
    # Adding (ITEMS_PER_PAGE - 1) before dividing rounds UP: (13 + 4) // 5 = 3
    total_pages = (total + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    return render_template('notes.html',
                           notes=all_notes,
                           page=page,
                           total_pages=total_pages)


# --- CREATE NOTE ---
@app.route('/notes/add', methods=['GET', 'POST'])
@login_required
def add_note():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        db = get_db()
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO notes (username, title, content) VALUES (%s, %s, %s)",
                    (session['user'], title, content)
                )
            db.commit()
            flash('Note added successfully!')
            return redirect(url_for('notes'))
        finally:
            db.close()

    return render_template('add_note.html')


# --- VIEW SINGLE NOTE ---
@app.route('/notes/<int:note_id>')
@login_required
# <int:note_id> captures the number from URL like /notes/5 and passes it as note_id=5
def view_note(note_id):
    db = get_db()
    try:
        with db.cursor() as cursor:
            # Only fetch if it belongs to the logged-in user (security check)
            cursor.execute(
                "SELECT * FROM notes WHERE id = %s AND username = %s",
                (note_id, session['user'])
            )
            note = cursor.fetchone()
    finally:
        db.close()

    if not note:
        flash('Note not found')
        return redirect(url_for('notes'))

    return render_template('view_note.html', note=note)


# --- EDIT NOTE ---
@app.route('/notes/edit/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    db = get_db()
    try:
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            with db.cursor() as cursor:
                # Update only if the note belongs to the logged-in user
                cursor.execute(
                    "UPDATE notes SET title=%s, content=%s WHERE id=%s AND username=%s",
                    (title, content, note_id, session['user'])
                )
            db.commit()
            flash('Note updated successfully!')
            return redirect(url_for('view_note', note_id=note_id))

        # GET request: load the note to pre-fill the edit form
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM notes WHERE id = %s AND username = %s",
                (note_id, session['user'])
            )
            note = cursor.fetchone()
    finally:
        db.close()

    if not note:
        flash('Note not found')
        return redirect(url_for('notes'))

    return render_template('edit_note.html', note=note)


# --- DELETE NOTE ---
@app.route('/notes/delete/<int:note_id>', methods=['POST'])
@login_required
# methods=['POST'] only — we use POST for delete to prevent accidental deletion
# A GET request (clicking a link) should never delete data
def delete_note(note_id):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "DELETE FROM notes WHERE id = %s AND username = %s",
                (note_id, session['user'])
            )
            # DELETE FROM removes a row from the table permanently
        db.commit()
        flash('Note deleted successfully!')
    finally:
        db.close()
    return redirect(url_for('notes'))


# ============================================================
# 9. SEARCH NOTES
# ============================================================

@app.route('/search')
@login_required
def search():
    # Get search term from URL like /search?q=shopping
    query = request.args.get('q', '')
    # default='' means if no search term, use empty string
    results = []

    if query:
        db = get_db()
        try:
            with db.cursor() as cursor:
                # LIKE '%word%' searches for 'word' anywhere in the text
                # % is a wildcard: %shopping% matches "go shopping today" or "shopping list"
                search_term = f'%{query}%'
                cursor.execute(
                    "SELECT * FROM notes WHERE username = %s AND (title LIKE %s OR content LIKE %s) ORDER BY created_at DESC",
                    (session['user'], search_term, search_term)
                )
                # Searches in both title AND content columns
                results = cursor.fetchall()
        finally:
            db.close()

    return render_template('search.html', results=results, query=query)


# ============================================================
# 10. SEND EMAIL
# ============================================================

@app.route('/send-email', methods=['GET', 'POST'])
@login_required
def send_email():
    if request.method == 'POST':
        recipient = request.form['recipient']
        subject = request.form['subject']
        body = request.form['body']

        try:
            # Create an email message object
            msg = Message(
                subject=subject,        # Email subject line
                recipients=[recipient], # List of email addresses to send to
                body=body               # Plain text email body
            )
            # Send the email through Flask-Mail
            mail.send(msg)
            flash('Email sent successfully!')
        except Exception as e:
            # Exception catches any error that occurs
            # str(e) converts the error to a readable string
            flash(f'Failed to send email: {str(e)}')

        return redirect(url_for('send_email'))

    return render_template('send_email.html')


# ============================================================
# 11. CONTACT FORM (stores messages in database)
# ============================================================

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    # No @login_required — anyone can submit a contact form
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        db = get_db()
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO contacts (name, email, subject, message) VALUES (%s, %s, %s, %s)",
                    (name, email, subject, message)
                )
            db.commit()
            flash('Message sent successfully! We will get back to you soon.')
        finally:
            db.close()

        return redirect(url_for('contact'))

    return render_template('contact.html')


# --- View Contact Messages (Admin Feature) ---
@app.route('/messages')
@login_required
def view_messages():
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM contacts ORDER BY created_at DESC")
            messages = cursor.fetchall()
    finally:
        db.close()
    return render_template('messages.html', messages=messages)


# ============================================================
# 12. FILE UPLOAD & DOWNLOAD
# ============================================================

@app.route('/upload-file', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add username prefix to keep files organized
            filename = session['user'] + '_' + filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash(f'File "{filename}" uploaded successfully!')
            return redirect(url_for('upload_file'))
        else:
            flash('File type not allowed')

    # List all files uploaded by this user
    user_files = []
    # os.listdir() returns a list of all files in the uploads folder
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for f in os.listdir(app.config['UPLOAD_FOLDER']):
            # Only show files that belong to this user (start with their username)
            if f.startswith(session['user'] + '_'):
                user_files.append(f)

    return render_template('upload_file.html', files=user_files)


@app.route('/download/<filename>')
@login_required
def download_file(filename):
    # Security check: only allow users to download their own files
    if not filename.startswith(session['user'] + '_'):
        flash('Access denied')
        return redirect(url_for('upload_file'))

    # send_from_directory() sends a file from the specified folder to the browser
    # as_attachment=True makes the browser download it instead of displaying it
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route('/delete-file/<filename>', methods=['POST'])
@login_required
def delete_file(filename):
    # Security check: only allow users to delete their own files
    if not filename.startswith(session['user'] + '_'):
        flash('Access denied')
        return redirect(url_for('upload_file'))

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    # os.path.exists() checks if the file is actually there before deleting
    if os.path.exists(file_path):
        os.remove(file_path)
        # os.remove() deletes the file from the server
        flash('File deleted successfully!')
    else:
        flash('File not found')

    return redirect(url_for('upload_file'))


# ============================================================
# 13. REST API — JSON Endpoints
# ============================================================
# APIs return data as JSON (not HTML) so other apps/mobile apps can use it

@app.route('/api/notes')
@login_required
def api_notes():
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, content, created_at FROM notes WHERE username = %s ORDER BY created_at DESC",
                (session['user'],)
            )
            all_notes = cursor.fetchall()
    finally:
        db.close()

    # Convert datetime objects to strings so JSON can handle them
    for note in all_notes:
        note['created_at'] = str(note['created_at'])

    # jsonify() converts Python list/dict to JSON and sets correct Content-Type header
    return jsonify({'status': 'success', 'data': all_notes, 'total': len(all_notes)})
    # Response looks like: {"status": "success", "data": [...], "total": 5}


@app.route('/api/profile')
@login_required
def api_profile():
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM profiles WHERE username = %s", (session['user'],))
            profile = cursor.fetchone()
    finally:
        db.close()

    if profile:
        profile['created_at'] = str(profile['created_at'])
        profile['updated_at'] = str(profile['updated_at'])

    return jsonify({'status': 'success', 'data': profile})


# ============================================================
# 15. AI/ML FEATURES — Machine Learning in the Browser!
# ============================================================
# These routes let you interact with AI models through the web browser.
# Each page has a form where you enter data, and the AI model returns predictions.
# ============================================================

# --- AI Dashboard (shows all AI tools in one place) ---
@app.route('/ai')
@login_required
def ai_dashboard():
    """Main page showing all available AI tools"""
    return render_template('ai_dashboard.html')


# --- Sentiment Analysis ---
@app.route('/ai/sentiment', methods=['GET', 'POST'])
@login_required
def ai_sentiment():
    """
    SENTIMENT ANALYSIS — Determines if text is positive, negative, or neutral.

    How it works:
    1. User types text in a form
    2. TextBlob analyzes the words and their emotional weight
    3. Returns a score from -1 (very negative) to +1 (very positive)

    Real-world uses:
    - Companies analyze customer reviews
    - Social media monitoring
    - Brand reputation tracking
    """
    result = None
    text = ''

    if request.method == 'POST':
        text = request.form['text']
        if text.strip():
            # .strip() removes whitespace — ensures user typed something
            result = analyze_sentiment(text)
            # Returns: {'polarity': 0.5, 'subjectivity': 0.6, 'sentiment': 'Positive 😊'}

    return render_template('ai_sentiment.html', result=result, text=text)


# --- Text Summarizer ---
@app.route('/ai/summarize', methods=['GET', 'POST'])
@login_required
def ai_summarize():
    """
    TEXT SUMMARIZER — Extracts the most important sentences from long text.

    How it works:
    1. User pastes a long article/text
    2. Algorithm scores each sentence by word importance
    3. Returns the top N most important sentences

    This is "Extractive Summarization" — it picks existing sentences.
    ChatGPT uses "Abstractive Summarization" — it writes NEW sentences.
    """
    summary = None
    text = ''
    num_sentences = 3

    if request.method == 'POST':
        text = request.form['text']
        num_sentences = int(request.form.get('num_sentences', 3))
        # .get('num_sentences', 3) = get value or default to 3
        if text.strip():
            summary = summarize_text(text, num_sentences)

    return render_template('ai_summarize.html', summary=summary, text=text, num_sentences=num_sentences)


# --- Spam Detector ---
@app.route('/ai/spam', methods=['GET', 'POST'])
@login_required
def ai_spam():
    """
    SPAM DETECTOR — Uses Logistic Regression to classify text as spam or not.

    How it works:
    1. User types an email/message
    2. System counts suspicious words (free, win, click, etc.)
    3. Logistic Regression model predicts: SPAM or NOT SPAM
    4. Also shows confidence level and which spam words were found

    This is CLASSIFICATION — the model puts data into categories.
    """
    result = None
    text = ''

    if request.method == 'POST':
        text = request.form['text']
        if text.strip():
            result = detect_spam(text)
            # Returns: {'is_spam': True, 'confidence': 95.0, 'spam_words_found': [...]}

    return render_template('ai_spam.html', result=result, text=text)


# --- Student Marks Predictor ---
@app.route('/ai/marks', methods=['GET', 'POST'])
@login_required
def ai_marks():
    """
    MARKS PREDICTOR — Uses Linear Regression to predict exam marks.

    How it works:
    1. User enters hours studied
    2. Linear Regression model uses the learned line equation (y = mx + b)
    3. Returns predicted marks and grade

    This is REGRESSION — the model predicts a continuous number.
    """
    result = None
    hours = ''

    if request.method == 'POST':
        hours = request.form['hours']
        try:
            hours_float = float(hours)
            if 0 <= hours_float <= 24:
                result = predict_marks(hours_float)
            else:
                flash('Please enter hours between 0 and 24')
        except ValueError:
            flash('Please enter a valid number')

    return render_template('ai_marks.html', result=result, hours=hours)


# --- House Price Predictor ---
@app.route('/ai/house', methods=['GET', 'POST'])
@login_required
def ai_house():
    """
    HOUSE PRICE PREDICTOR — Uses Multiple Linear Regression.

    How it works:
    1. User enters square feet and number of bedrooms
    2. Model uses MULTIPLE features (not just one) to predict
    3. Returns predicted price and shows how each feature contributes

    This is MULTIPLE REGRESSION — uses 2+ inputs for better accuracy.
    """
    result = None
    square_feet = ''
    bedrooms = ''

    if request.method == 'POST':
        square_feet = request.form['square_feet']
        bedrooms = request.form['bedrooms']
        try:
            sqft = float(square_feet)
            beds = int(bedrooms)
            if sqft > 0 and 1 <= beds <= 10:
                result = predict_house_price(sqft, beds)
            else:
                flash('Please enter valid values')
        except ValueError:
            flash('Please enter valid numbers')

    return render_template('ai_house.html', result=result, square_feet=square_feet, bedrooms=bedrooms)


# ============================================================
# 16. ERROR HANDLERS
# ============================================================
# Custom error pages instead of the default ugly ones

@app.errorhandler(404)
# 404 = Page Not Found (user visited a URL that doesn't exist)
def page_not_found(e):
    # e is the error object passed by Flask
    return render_template('404.html'), 404
    # The 404 after the comma tells the browser this is a "not found" response


@app.errorhandler(500)
# 500 = Internal Server Error (something broke in our code)
def internal_error(e):
    return render_template('500.html'), 500


# ============================================================
# 15. LOGOUT
# ============================================================

@app.route('/logout')
def logout():
    # Remove 'user' from session — forgets the login
    # None is a safety default so it doesn't crash if already logged out
    session.pop('user', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))


# ============================================================
# RUN THE APP
# ============================================================

if __name__ == '__main__':
    # Create uploads folder if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    # exist_ok=True means don't error if folder already exists

    # Start the Flask development server
    # debug=True = auto-reload on code changes + detailed error pages
    # In production, set debug=False
    app.run(debug=True)
