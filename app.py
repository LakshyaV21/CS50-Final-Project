from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"  # keep this secure!

def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect("/")
        else:
            return render_template("login.html", error="Invalid username or password.")

    return render_template("login.html")

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("index.html")

from werkzeug.security import generate_password_hash

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirmation = request.form["confirmation"]

        if not username or not password or not confirmation:
            return render_template("register.html", error="All fields are required.")

        if password != confirmation:
            return render_template("register.html", error="Passwords do not match.")

        hashed_pw = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
            conn.commit()
            conn.close()
            return redirect("/login")
        except sqlite3.IntegrityError:
            return render_template("register.html", error="Username already taken.")

    return render_template("signin.html")

@app.route('/allergies', methods=['GET', 'POST'])
def allergies():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    if request.method == 'POST':
        selected_allergies = request.form.getlist('allergy')
        custom_allergy = request.form.get('customAllergy')

        if custom_allergy:
            selected_allergies.append(custom_allergy)

        conn = get_db_connection()

        # Clear previous entries
        conn.execute("DELETE FROM user_allergies WHERE user_id = ?", (user_id,))

        # Insert updated allergies
        for allergy in selected_allergies:
            conn.execute("INSERT INTO user_allergies (user_id, allergy) VALUES (?, ?)", (user_id, allergy))

        conn.commit()
        conn.close()

        return redirect(url_for('preferences'))

    return render_template('allergies.html')


@app.route('/travelguide', methods=['GET', 'POST'])
def travelguide():
    if "user_id" not in session:
        return redirect("/login")

    selected_country = None
    flagged_foods = []
    user_id = session["user_id"]

    # Example food data
    food_data = {
        "Japan": [
            {"name": "Sushi", "ingredients": ["rice", "seaweed", "fish"]},
            {"name": "Miso Soup", "ingredients": ["soy", "tofu", "miso"]}
        ],
        "Italy": [
            {"name": "Pasta Carbonara", "ingredients": ["egg", "cheese", "pork", "wheat"]},
            {"name": "Tiramisu", "ingredients": ["egg", "cream", "chocolate"]}
        ]
    }

    # Fetch user's allergies from DB
    conn = get_db_connection()
    rows = conn.execute("SELECT allergy FROM user_allergies WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    user_allergies = [row["allergy"] for row in rows]

    if request.method == 'POST':
        selected_country = request.form['country']
        foods = food_data.get(selected_country, [])

        for food in foods:
            has_allergy = any(allergy.lower() in [i.lower() for i in food['ingredients']] for allergy in user_allergies)
            flagged_foods.append({
                "name": food["name"],
                "ingredients": food["ingredients"],
                "danger": has_allergy
            })

    countries = list(food_data.keys())
    return render_template("travel.html", countries=countries, selected_country=selected_country, foods=flagged_foods)

@app.route('/mypreferences')
def preferences():
    if "user_id" not in session:
        return redirect("/login")  # Redirect if not logged in

    user_id = session["user_id"]

    # Connect to the database and fetch the user's allergies
    conn = get_db_connection()
    rows = conn.execute("SELECT allergy FROM user_allergies WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()

    # Extract allergies into a list
    allergies = [row["allergy"] for row in rows]

    return render_template('preferences.html', allergies=allergies)
