from flask import Flask, render_template, request
import numpy as np
from keras.models import load_model 
import joblib # or joblib / pickle if sklearn

app = Flask(__name__)

# Load your trained model
model = load_model("concrete-quality.keras")  
scaler_data = joblib.load("scaler_data.pkl")
scaler_target = joblib.load("scaler_target.pkl")


@app.route('/')
def home():
    return render_template("concrete.html")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # 1️⃣ Catch data from form
        cement = float(request.form['cement'])
        slag = float(request.form['blast_furnace_slag'])
        fly_ash = float(request.form['fly_ash'])
        water = float(request.form['water'])
        superplasticizer = float(request.form['superplasticizer'])
        coarse = float(request.form['coarse_aggregate'])
        fine = float(request.form['fine_aggregate'])
        age = float(request.form['age'])

        # 2️⃣ Pass to destination data (model input format)
        input_data = np.array([[cement, slag, fly_ash, water,
                               superplasticizer, coarse, fine, age]])

        # 3️⃣ Model prediction
        input_scaled = scaler_data.transform(input_data)

        # 🔹 Predict (scaled output)
        prediction_scaled = model.predict(input_scaled)

        # 🔹 Convert back to REAL value
        prediction_real = scaler_target.inverse_transform(prediction_scaled)

        result = float(prediction_real[0][0])


        return render_template(
            "concrete.html",
            prediction_text=f"Predicted Concrete Strength: {result:.2f} MPa"
        )

    except Exception as e:
        return render_template(
            "concrete.html",
            prediction_text=f"Error: {str(e)}"
        )

if __name__ == "__main__":
    app.run(debug=True)