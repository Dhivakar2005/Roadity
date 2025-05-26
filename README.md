# 🚦 Rodity: Road Accident Predictor and Analyzer

Rodity is a web-based application that leverages machine learning to predict and analyze road accident severity based on various real-world factors. It helps users understand how different conditions affect road safety, enabling proactive measures for accident prevention.

## 🧠 Features

- 🚗 Accident severity prediction using trained machine learning models
- 📊 Interactive visual analysis of accident data
- 🧾 User-friendly web interface built with Flask
- 🔒 Login/signup system to restrict access to prediction tools
- 🤖 Gemini API integration for driving safety suggestions

## 🧾 Input Columns / Features

The model takes the following features as input:

| Column           | Description                                 |
|------------------|---------------------------------------------|
| `weather`        | Weather condition during the incident       |
| `road_condition` | Condition of the road                       |
| `road_type`      | Type of road                                |
| `lighting`       | Lighting condition                          |
| `vehicle_type`   | Type of vehicle involved                    |
| `driver_age`     | Age of the driver                           |
| `speed_limit`    | Legal speed limit of the road               |
| `traffic_volume` | Estimated traffic volume on the road        |
| `severity`       | Severity of the accident                    |

## 🛠️ Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, Flask
- **Database:** SQLite (for user authentication)
- **ML Model:** Scikit-learn model
- **Visualization:** Matplotlib, Seaborn
- **AI Suggestions:** Gemini API

## 📁 Project Structure
      
      Rodity/
      ├── static/ # CSS, JS, Images
      ├── templates/ # HTML Templates (login.html, predict.html, etc.)
      ├── app.py # Flask Application
      ├── accident_model.pkl # Trained ML Model
      ├── user.db # SQLite Database
      ├── README.md # Project Documentation
      └── requirements.txt # Python Dependencies


## 🚀 How to Run Locally


1. **Clone the repository**
   ```bash
   https://github.com/Dhivakar2005/Roadity.git
   cd rodity

2. **Install dependencies**
   ```bash
    pip install -r requirements.txt

3. **Run the Flask app**
    ```bash
    python app.py

4. **Access the app**
    ```bash
   Open your browser and go to http://127.0.0.1:5000

## 📈 Future Improvements
  - Deploy the app on cloud 

  - Add a mobile-friendly version

  - Improve accuracy with advanced ML models 

## 👨🏻‍💻Team Members
>  - Dhivakar G
>  - Santhosh S
>  - Siva E
>  - Baranidharan A
>  - Sathish B
  
## 🫱🏻‍🫲🏻 Contribution
Pull requests and feature suggestions are welcome! Feel free to fork the repo and improve Rodity.

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
