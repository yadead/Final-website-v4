from flask import Flask, redirect, render_template, request, flash, jsonify, session, url_for, send_file
import requests
from flask_wtf import CSRFProtect
from flask_csp.csp import csp_header
import logging
import os
import userManagement as dbHandler
from datetime import datetime
import math
import re
import csv
from io import StringIO, BytesIO

# Code snippet for logging a message
# app.logger.critical("message")

# http://127.0.0.1:5000/ or http://localhost:5000/
# pip install -r requirements.txt

app_log = logging.getLogger(__name__)
logging.basicConfig(
    filename="security_log.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
)

# Generate a unique basic 16 key: https://acte.ltd/utils/randomkeygen
app = Flask(__name__)
app.secret_key = b"_53oi3uriq9pifpff;apl"
csrf = CSRFProtect(app)

# Redirect index.html to domain root for consistent UX
@app.route("/index", methods=["GET"])
@app.route("/index.htm", methods=["GET"])
@app.route("/index.asp", methods=["GET"])
@app.route("/index.php", methods=["GET"])
@app.route("/index.html", methods=["GET"])
def root():
    return redirect("/", 302)

@app.route("/", methods=["POST", "GET"])
@csp_header(
    {
        # Server Side CSP is consistent with meta CSP in layout.html
        "base-uri": "'self'",
        "default-src": "'self'",
        "style-src": "'self'",
        "script-src": "'self'",
        "img-src": "'self' data:",
        "media-src": "'self'",
        "font-src": "'self'",
        "object-src": "'self'",
        "child-src": "'self'",
        "connect-src": "'self'",
        "worker-src": "'self'",
        "report-uri": "/csp_report",
        "frame-ancestors": "'none'",
        "form-action": "'self'",
        "frame-src": "'none'",
    }
)
def index():
    username = session.get('username')
    return render_template("index.html", username=username)

@app.route("/about.html", methods=["GET"])
def about():
    return render_template("about.html")

def validate_password(password):
    if len(password) < 8:
        flash("Password must be at least 8 characters long", 'danger')
        return False
    if not re.search(r"[A-Z]", password):
        flash("Password must contain at least one uppercase letter", 'danger')
        return False
    if not re.search(r"[a-z]", password):
        flash("Password must contain at least one lowercase letter", 'danger')
        return False
    if not re.search(r"[0-9]", password):
        flash("Password must contain at least one number", 'danger')
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        flash("Password must contain at least one special character", 'danger')
        return False
    return True

@app.route("/signup.html", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Validate the password
        if not validate_password(password):
            return render_template("signup.html")
        
        dbHandler.signup(str(username), str(password))
        flash(f"User {username} signed up successfully!", 'success')
        return redirect("/signin.html")
    return render_template("signup.html")

@app.route("/signin.html", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Validate the password
        if not validate_password(password):
            return render_template("signin.html")
        
        if dbHandler.signin(str(username), str(password)):
            session['username'] = username  # Store username in session
            flash(f"User {username} signed in successfully!", 'success')
            return redirect("/form.html")
        else:
            flash("Invalid username or password", 'danger')
            return render_template("signin.html")
    return render_template("signin.html")

@app.route("/form.html", methods=["GET", "POST"])
def form():
    if 'username' not in session:
        return redirect(url_for('sign_in'))  # Redirect to sign-in page if not signed in
    if request.method == "POST":
        Developer = session['username']
        Project = request.form.get("Project")
        time_format = "%H:%M %d/%m/%Y"
        Start_Time = request.form.get("Start_Time")
        End_Time = request.form.get("End_Time")
        start_dt = datetime.strptime(Start_Time, time_format)
        end_dt = datetime.strptime(End_Time, time_format)
        Time_Worked = end_dt - start_dt
        total_minutes = Time_Worked.total_seconds() / 60
        rounded_minutes = math.ceil(total_minutes / 15) * 15
        rounded_hours = rounded_minutes / 60
        Time_Worked = rounded_hours
        Diary_Entry = datetime.now().strftime("%H:%M %d/%m/%Y")
        Repo = request.form.get("Repo")
        Developer_Notes = request.form.get("Developer_Notes")
        dbHandler.diary_entry(Developer, Project, Start_Time, End_Time, Diary_Entry, Time_Worked, Repo, Developer_Notes)
    return render_template("form.html")

@app.route("/privacy.html", methods=["GET", "POST"])
def privacy():
    return render_template("privacy.html")

@app.route("/signout.html")
def sign_out():
    session.pop('username', None)
    flash("You have been signed out.", 'success')
    return redirect(url_for('index'))

@app.route("/formsearch.html", methods=["GET"])
def form_search():
    if 'username' not in session:
        return redirect(url_for('sign_in'))  # Redirect to sign-in page if not signed in
    
    query = request.args.get('query', '')
    entries = dbHandler.search_entries(query)
    flash(f"Search results for '{query}'", 'info')
    return render_template("formsearch.html", entries=entries)

@app.route("/delete_entry/<int:entry_id>", methods=["POST"])
def delete_entry(entry_id):
    if 'username' not in session:
        return redirect(url_for('sign_in'))  # Redirect to sign-in page if not signed in
    
    username = session['username']
    dbHandler.delete_entry(entry_id, username)
    flash("Entry deleted successfully.", 'success')
    return redirect(url_for('form_search'))

@app.route("/download_entry/<int:entry_id>", methods=["GET"])
def download_entry(entry_id):
    if 'username' not in session:
        return redirect(url_for('sign_in'))  # Redirect to sign-in page if not signed in
    
    entry = dbHandler.get_entry(entry_id)
    if not entry:
        flash("Entry not found.", 'danger')
        return redirect(url_for('form_search'))
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Developer', 'Project', 'Start Time', 'End Time', 'Diary Entry', 'Time Worked', 'Repo', 'Developer Notes'])
    writer.writerow(entry)
    
    output.seek(0)
    byte_output = BytesIO(output.getvalue().encode('utf-8'))
    return send_file(byte_output, mimetype='text/csv', download_name=f'entry_{entry_id}.csv', as_attachment=True)

# Endpoint for logging CSP violations
@app.route("/csp_report", methods=["POST"])
@csrf.exempt
def csp_report():
    app.logger.critical(request.data.decode())
    return "done"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)