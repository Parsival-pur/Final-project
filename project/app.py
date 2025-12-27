# This project was developed as a final project for CS50x.
# I used ChatGPT as a helper for debugging logic errors
# and for translating the interface and documentation into English.
# The core logic and structure were designed and implemented by me.

# IMPORTS 
from flask import Flask, render_template, request, redirect, session
import sqlite3

# APPLICATION INITIALIZATION 
app = Flask(__name__)
app.secret_key = 'your_secret_key_123'

# CONFIGURATION VARIABLES
DB_NAME = 'users.db'

# DATABASE INITIALIZATION FUNCTION
def init_db():
    try:
        conn = sqlite3.connect(DB_NAME, timeout=5)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
        print("✓ Database initialized successfully!")
    except Exception as e:
        print(f"✗ Database initialization error: {e}")


# APPLICATION ROUTES (URLS) 

# HOME PAGE
@app.route("/")
def index():
    return render_template("index.html")


# REGISTRATION PAGE 
@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        if not username or not password:
            error = "Please fill in all fields!"
        else:
            try:
                conn = sqlite3.connect(DB_NAME, timeout=5)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, password)
                )
                conn.commit()
                conn.close()
                return redirect("/login?message=Registration successful! Please enter your login details")
            except sqlite3.IntegrityError:
                error = "A user with this username already exists!"
            except Exception as e:
                error = f"Error: {str(e)}"

    return render_template("registration.html", error=error)


# LOGIN PAGE 
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    message = request.args.get("message", "")
    
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            error = "Please fill in all fields!"
        else:
            try:
                conn = sqlite3.connect(DB_NAME, timeout=5)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM users WHERE username = ? AND password = ?",
                    (username, password)
                )
                user = cursor.fetchone()
                conn.close()

                if user:
                    session['username'] = username
                    return redirect(f"/profile")
                else:
                    error = "Invalid username or password"
            except Exception as e:
                error = f"Error: {str(e)}"

    return render_template("login.html", error=error, message=message)


# PROFILE PAGE 
@app.route("/profile")
def profile():
    if 'username' not in session:
        return redirect("/login")
    
    username = session['username']
    return render_template("profile.html", username=username)


#  LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# BMI PAGE (KEEP ONLY THIS ONE) 
@app.route("/bmi")
def bmi():
    # Check if the user is logged in
    if 'username' not in session:
        return redirect("/login")
    return render_template("bmi.html")

# RESULT PAGE 
@app.route("/result", methods=["POST"])
def bmi_result():
    try:
        weight = float(request.form.get("weight", 0))
        # Attention: make sure height is entered in METERS (1.80) not in centimeters (180)
        height = float(request.form.get("height", 0))
        
        if weight <= 0 or height <= 0:
            return "Error: please enter valid weight and height values"
            
        bmi = weight / (height * height)
        bmi_rounded = round(bmi, 1)
        
        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 25:
            category = "Normal weight"
        elif bmi < 30:
            category = "Overweight"
        else:
            category = "Obesity"
            
        return render_template("result.html", bmi=bmi_rounded, category=category)
    except ValueError:
        return "Error: invalid input data (numbers required)"
    
# CALORIES PAGE
@app.route("/calories", methods=["GET", "POST"])
def calories():
    if 'username' not in session:
        return redirect("/login")

    result = None

    if request.method == "POST":
        try:
            weight = float(request.form.get("weight", 0))
            height = float(request.form.get("height", 0))
            age = int(request.form.get("age", 0))
            gender = request.form.get("gender")

            if weight <= 0 or height <= 0 or age <= 0:
                return "Error: invalid data"

            # Mifflin–St Jeor formula
            if gender == "male":
                calories = 10 * weight + 6.25 * height - 5 * age + 5
            else:
                calories = 10 * weight + 6.25 * height - 5 * age - 161

            result = round(calories)

        except ValueError:
            return "Error: please enter numbers only"

    return render_template("calories.html", result=result)


# APPLICATION START 
if __name__ == "__main__":
    init_db() 
    app.run(debug=True)
