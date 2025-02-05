from flask import Flask, render_template, request, flash
import userManagement as dbHandler


@app.route("/signin.html", methods=["GET", "POST"])
def signin():
    if request.method == "GET":
        username = request.form.get("username")
        password = request.form.get("password")

        if len(password) < 8:
            flash("Password must be at least 8 characters long", category="error")
        else:


@app.route("/signup.html", methods=["GET", "POST"])
def signup():
    return render_template("signup.html")