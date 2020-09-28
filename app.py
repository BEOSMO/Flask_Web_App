from flask import Flask, render_template, redirect, url_for, request, make_response, jsonify
import joblib
import numpy as np
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config.from_object(os.environ["APP_SETTINGS"])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
#from models import Result

from models import Result

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=['POST'])
def predict():
    if request.method=='POST':
        
        regressor = joblib.load("linear_regression_model.pkl")
        #regressor = joblib.load("linear_regression_model.pkl")

        data = dict(request.form.items())

        yearsExperience = np.array(float(data["YearsExperience"])).reshape(-1,1)

        prediction = regressor.predict(yearsExperience)
        
    result = Result(
    YearsExperience = float(yearsExperience), 
    Prediction = float(prediction)
    )    
    db.session.add(result)
    db.session.commit()



    return render_template("predicted.html", prediction=prediction)


if __name__ == '__main__':
    app.run(debug=True)
