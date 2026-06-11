import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor


def train_models(df):

    numeric_df = df.select_dtypes(include=["number"])

    if len(numeric_df.columns) < 2:
        raise Exception(
            "Dataset needs at least 2 numeric columns."
        )

    target = "Sales"

    if target not in df.columns:
        raise Exception(
            "Sales column not found."
        )

    X = numeric_df.drop(columns=[target])

    y = numeric_df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    models = {
        "Linear Regression": LinearRegression(),
        "Decision Tree": DecisionTreeRegressor(),
        "Random Forest": RandomForestRegressor()
    }

    results = []

    best_model = None
    best_score = -999

    for name, model in models.items():

        model.fit(X_train, y_train)

        predictions = model.predict(X_test)

        mae = mean_absolute_error(
            y_test,
            predictions
        )

        rmse = mean_squared_error(
            y_test,
            predictions
        ) ** 0.5

        r2 = r2_score(
            y_test,
            predictions
        )

        results.append({
            "Model": name,
            "MAE": round(mae, 2),
            "RMSE": round(rmse, 2),
            "R2": round(r2, 2)
        })

        if r2 > best_score:
            best_score = r2
            best_model = model

    joblib.dump(
        best_model,
        "models/best_model.pkl"
    )

    return results