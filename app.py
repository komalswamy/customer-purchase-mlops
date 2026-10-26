
import os
import json
import joblib
import pandas as pd
import boto3

from flask import Flask, render_template_string, request

app = Flask(__name__)

MODEL_PATH = "/content/model/model.pkl"
model = joblib.load(MODEL_PATH)

ENDPOINT_NAME = os.environ.get("SAGEMAKER_ENDPOINT")
AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")

FEATURES = [
    "age", "gender", "annual_income", "browsing_time",
    "pages_visited", "previous_purchases",
    "website_time", "discount"
]

runtime = boto3.client("sagemaker-runtime", region_name=AWS_REGION)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Customer Purchase Prediction</title>
</head>
<body>
    <h1>Customer Purchase Prediction System</h1>
    <form method="POST">
        Age: <input name="age" type="number" required><br><br>
        Gender:
        <select name="gender">
            <option>Male</option>
            <option>Female</option>
        </select><br><br>
        Annual Income: <input name="annual_income" type="number" step="any" required><br><br>
        Browsing Time: <input name="browsing_time" type="number" step="any" required><br><br>
        Pages Visited: <input name="pages_visited" type="number" required><br><br>
        Previous Purchases: <input name="previous_purchases" type="number" required><br><br>
        Website Time: <input name="website_time" type="number" step="any" required><br><br>
        Discount: <input name="discount" type="number" step="any" required><br><br>
        <button type="submit">Predict Purchase</button>
    </form>
    {% if result %}
        <h2>Prediction: {{ result }}</h2>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        customer = {
            "age": int(request.form["age"]),
            "gender": request.form["gender"],
            "annual_income": float(request.form["annual_income"]),
            "browsing_time": float(request.form["browsing_time"]),
            "pages_visited": int(request.form["pages_visited"]),
            "previous_purchases": int(request.form["previous_purchases"]),
            "website_time": float(request.form["website_time"]),
            "discount": float(request.form["discount"])
        }

        data = pd.DataFrame([customer], columns=FEATURES)

        if ENDPOINT_NAME:
            response = runtime.invoke_endpoint(
                EndpointName=ENDPOINT_NAME,
                ContentType="text/csv",
                Accept="application/json",
                Body=data.to_csv(index=False, header=False).encode("utf-8")
            )
            prediction = json.loads(
                response["Body"].read().decode("utf-8")
            )
            prediction = int(prediction[0])
        else:
            prediction = int(model.predict(data)[0])

        result = (
            "Likely to Purchase" if prediction == 1
            else "Unlikely to Purchase"
        )

    return render_template_string(HTML, result=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
