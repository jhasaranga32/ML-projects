from flask import Flask,render_template,request
from keras.models import load_model
import numpy as np

model = load_model("plant_health_model.keras")

app =Flask(__name__)


@app.route('/')
def index():
    return render_template('home.html')

@app.route('/predict', methods=['POST'])
def getresults():
    
    
    soil_moisture = float(request.form["soil_moisture"])
    ambient_temp = float(request.form["ambient_temperature"])
    soil_temp = float(request.form["soil_temperature"])
    humidity = float(request.form["humidity"])
    light_intensity = float(request.form["light_intensity"])
    soil_ph = float(request.form["soil_ph"])
    nitrogen = float(request.form["nitrogen_level"])
    phosphorus = float(request.form["phosphorus_level"])
    potassium = float(request.form["potassium_level"])
    chlorophyll = float(request.form["chlorophyll_content"])
    electro_signal = float(request.form["electrochemical_signal"])
    
    test_data = np.array([[
    float(soil_moisture),
    float(ambient_temp),
    float(soil_temp),
    float(humidity),
    float(light_intensity),
    float(soil_ph),
    float(nitrogen),
    float(phosphorus),
    float(potassium),
    float(chlorophyll),
    float(electro_signal)
]])

    prediction = model.predict(test_data)

    # Example: classification
    class_index = np.argmax(prediction, axis=1)[0]

    # OR regression
    # result = prediction[0][0]
    class_names = {
            0: "Poor Health",
            1: "Average Health",
            2: "Healthy"
        }
    class_name = class_names[class_index]




    return render_template("result.html", prediction=class_name)

   






app.run(debug=True) 