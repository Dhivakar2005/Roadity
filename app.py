from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import io
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import google.generativeai as genai
import pandas as pd
import pickle

app = Flask(__name__)
app.secret_key = '0b156cf09f4198b95a66a9071d0231d3ebdaec504ad1035b31b252037c747c29'

# Load ML model
model = pickle.load(open('accident_model.pkl', 'rb'))

# Features expected by the model
features = [
    'driver_age', 'speed_limit', 'weather', 'road_condition',
    'road_type', 'lighting', 'vehicle_type', 'traffic_volume'
]

# ============ DATABASE SETUP ============
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("dhivakar", "test123"))
    c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("admin", "adminpass"))
    conn.commit()
    conn.close()

init_db()

# ============ AUTH ROUTES ============

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        with sqlite3.connect("users.db") as conn:
            cur = conn.cursor()
            try:
                cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                flash("Signup successful! Please log in.")
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                error = "Username already exists!"

    return render_template('signup.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        with sqlite3.connect("users.db") as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = cur.fetchone()

        if user:
            session['username'] = username
            flash("Login successful!")
            return redirect(url_for('predict'))
        else:
            error = "Invalid username or password."

    return render_template('login.html', error=error)


# ============ MAIN ROUTES ============

@app.route('/')
def home():
    return render_template('index.html')

# Configure Gemini
genai.configure(api_key="AIzaSyC4QV74nGCIRfHU8fwxGIupc4kpBCQK9YU")

def generate_safety_recommendation(driver_age, speed_limit, weather, road_condition, traffic_volume, lighting):
    """Generates a concise safety recommendation based on provided driving conditions."""

    risk_factors = []

    if driver_age < 25 or driver_age > 65:
        risk_factors.append("age")
    if weather in ["Rain", "Snow", "Fog", "Ice"]:
        risk_factors.append("weather")
    if road_condition in ["Wet", "Icy", "Slippery", "Potholes"]:
        risk_factors.append("road condition")
    if traffic_volume == "High":
        risk_factors.append("traffic")
    if lighting == "Poor" or lighting == "Dark":
        risk_factors.append("lighting")


    if len(risk_factors) > 2:  # Consider high risk if more than two factors are present. Adjust threshold as needed.
        recommendation = " Reduce speed significantly below the " + str(speed_limit) + " mph speed limit. "
        if "weather" in risk_factors:
            recommendation += "Increase following distance and use headlights. "
        if "road condition" in risk_factors:
            recommendation += "Avoid sudden braking or steering.  Be extra cautious around curves. "
        if "traffic" in risk_factors or "lighting" in risk_factors:
            recommendation += "Increase awareness of surroundings and other vehicles."


    elif len(risk_factors) > 0: # Moderate Risk
        recommendation = " Maintain a safe speed below the " + str(speed_limit) + " mph limit. "
        if "weather" in risk_factors:
            recommendation += "Ensure headlights are on and increase following distance as needed."
        if "road condition" in risk_factors:
            recommendation += "Drive smoothly and avoid sudden maneuvers."
        if "traffic" in risk_factors or "lighting" in risk_factors:
            recommendation += "Stay alert and focused on the road."

#**LOW RISK:**
    else:
        recommendation = " Maintain safe driving habits. Observe the " + str(speed_limit) + " mph speed limit, stay attentive, and keep a safe following distance."



    return recommendation




# Example Usage:
driver_age = 22
speed_limit = 65
weather = "Rain"
road_condition = "Wet"
traffic_volume = "Moderate"
lighting = "Dark"


recommendation = generate_safety_recommendation(driver_age, speed_limit, weather, road_condition, traffic_volume, lighting)
print(recommendation)


driver_age = 35
speed_limit = 30
weather = "Clear"
road_condition = "Dry"
traffic_volume = "Low"
lighting = "Daylight"


recommendation = generate_safety_recommendation(driver_age, speed_limit, weather, road_condition, traffic_volume, lighting)
print(recommendation)
features = [
    'driver_age',
    'speed_limit',
    'weather',
    'road_condition',
    'road_type',
    'lighting',
    'vehicle_type',
    'traffic_volume'
]


def fig_to_base64(plt_obj):
    img = io.BytesIO()
    plt_obj.savefig(img, format='png')
    img.seek(0)
    return base64.b64encode(img.read()).decode('utf-8')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if not file:
            return "No file uploaded", 400
        
        data = pd.read_csv(file)

        if not all(feat in data.columns for feat in features):
            return "Missing required columns", 400

        # Predict
        predictions = model.predict(data[features])
        data['Accident_Risk'] = ['Likely' if x == 1 else 'Unlikely' for x in predictions]

        # Convert DataFrame to CSV (base64 encoded for embedding in HTML)
        csv_io = io.StringIO()
        data.to_csv(csv_io, index=False)
        csv_data = csv_io.getvalue()
        b64_csv = base64.b64encode(csv_data.encode()).decode('utf-8')

        # Pie chart generation
        risk_counts = data['Accident_Risk'].value_counts()
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.pie(risk_counts, labels=risk_counts.index, autopct='%1.1f%%', startangle=140, colors=['#66c2a5', '#fc8d62'])
        ax.axis('equal')
        plt.tight_layout()
        graph = fig_to_base64(fig)
        plt.close()

        return render_template('upload.html', graph=graph, b64_csv=b64_csv, filename='predictions.csv')

    return render_template('upload.html', graph=None)


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'username' not in session:
        flash("Please log in to continue.")
        return redirect(url_for('login'))

    result = None
    suggestion = None  # ✅ Safely define this first

    if request.method == 'POST':
        data = {feat: request.form[feat] for feat in features}
        df = pd.DataFrame([data])
        prediction = model.predict(df)[0]
        result = '🚨 Accident likely' if prediction == 1 else '✅ Accident unlikely'

        driver_age = int(data['driver_age'])
        speed_limit = int(data['speed_limit'])
        weather = data['weather']
        road_condition = data['road_condition']
        traffic_volume = data['traffic_volume']
        lighting = data['lighting']

        suggestion = generate_safety_recommendation(driver_age, speed_limit, weather, road_condition, traffic_volume, lighting)

    return render_template('predict.html', result=result, suggestion=suggestion)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out. Please log in to continue.")
    return redirect(url_for('home'))  # ✅ go to home instead of predict

# ============ START APP ============
if __name__ == '__main__':
    app.run(debug=True)
