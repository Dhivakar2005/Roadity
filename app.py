from flask import Flask, render_template, request, redirect, send_file
import pandas as pd
import pickle
import io
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import google.generativeai as genai


app = Flask(__name__)

# Load the model
model = pickle.load(open('accident_model.pkl', 'rb'))


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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    suggestion = None
    result = None

    if request.method == 'POST':
        data = {feat: request.form[feat] for feat in features}
        df = pd.DataFrame([data])
        prediction = model.predict(df)[0]
        result = '🚨 Accident will be likely' if prediction == 1 else '✅ Accident is unlikely'

        # Extract relevant features
        driver_age = int(data['driver_age'])
        speed_limit = int(data['speed_limit'])
        weather = data['weather']
        road_condition = data['road_condition']
        traffic_volume = data['traffic_volume']
        lighting = data['lighting']

        # Generate suggestion using local function
        suggestion = generate_safety_recommendation(driver_age, speed_limit, weather, road_condition, traffic_volume, lighting)

    return render_template('predict.html', result=result, suggestion=suggestion)




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



@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
