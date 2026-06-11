import pandas as pd
import joblib


def generate_forecast(df):

    model = joblib.load(
        "models/best_model.pkl"
    )

    numeric_df = df.select_dtypes(
        include=["number"]
    )

    X = numeric_df.drop(
        columns=["Sales"]
    )

    predictions = model.predict(X)

    forecast_df = df.copy()

    forecast_df["Predicted_Sales"] = predictions

    return forecast_df