import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app import app

def test_home_page():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200

def test_customer_prediction():
    client = app.test_client()

    response = client.post("/", data={
        "age": "25",
        "gender": "Female",
        "annual_income": "50000",
        "browsing_time": "12",
        "pages_visited": "8",
        "previous_purchases": "2",
        "website_time": "6",
        "discount": "10"
    })

    assert response.status_code == 200
    assert b"Prediction:" in response.data
