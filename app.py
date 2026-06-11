from flask import Flask, render_template, request
import pandas as pd
import os
from models.preprocessing import clean_data
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
from models.training import train_models
from models.forecasting import generate_forecast
import plotly.express as px
from models.inventory import optimize_inventory
from reports.pdf_generator import generate_pdf
import plotly.express as px

app = Flask(__name__)

# Upload folder configuration
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create uploads folder automatically
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Validation Function
def validate_dataset(df):
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "missing": df.isnull().sum().sum(),
        "duplicates": df.duplicated().sum()
    }


# Dashboard
@app.route("/")
def dashboard():

    try:

        inventory_file = "static/uploads/inventory_report.csv"

        if not os.path.exists(inventory_file):

            return render_template(
                "dashboard.html",
                total_products=0,
                low_stock=0,
                overstock=0,
                optimal=0
            )

        # Inventory Data
        df = pd.read_csv(inventory_file)

        total_products = len(df)

        low_stock = len(
            df[df["Status"] == "Low Stock"]
        )

        overstock = len(
            df[df["Status"] == "Overstock"]
        )

        optimal = len(
            df[df["Status"] == "Optimal"]
        )

        # Pie Chart
        pie_df = pd.DataFrame({
            "Status": [
                "Low Stock",
                "Overstock",
                "Optimal"
            ],
            "Count": [
                low_stock,
                overstock,
                optimal
            ]
        })

        fig_pie = px.pie(
            pie_df,
            names="Status",
            values="Count",
            title="Inventory Status"
        )

        pie_chart = fig_pie.to_html(
            full_html=False
        )

        # Forecast Charts
        forecast_file = "static/uploads/forecast.csv"

        forecast_chart = None
        products_chart = None
        revenue_chart = None
        scatter_chart = None

        if os.path.exists(forecast_file):

            forecast_df = pd.read_csv(
                forecast_file
            )

            # Forecast Trend
            fig_forecast = px.line(
                forecast_df,
                y="Predicted_Sales",
                title="Forecast Sales Trend"
            )

            forecast_chart = (
                fig_forecast.to_html(
                    full_html=False
                )
            )

            # Top Products
            top_products = (
                forecast_df.nlargest(
                    10,
                    "Predicted_Sales"
                )
            )

            fig_products = px.bar(
                top_products,
                x="Product_Name",
                y="Predicted_Sales",
                title="Top Products"
            )

            products_chart = (
                fig_products.to_html(
                    full_html=False
                )
            )

            # Revenue Chart
            forecast_df["Revenue"] = (
                forecast_df["Predicted_Sales"] *
                forecast_df["Price"]
            )

            fig_revenue = px.bar(
                forecast_df.nlargest(
                    10,
                    "Revenue"
                ),
                x="Revenue",
                y="Product_Name",
                orientation="h",
                title="Revenue Contribution"
            )

            revenue_chart = (
                fig_revenue.to_html(
                    full_html=False
                )
            )

            # Scatter Plot
            fig_scatter = px.scatter(
                forecast_df,
                x="Inventory",
                y="Predicted_Sales",
                color="Product_Name",
                title="Inventory vs Demand"
            )

            scatter_chart = (
                fig_scatter.to_html(
                    full_html=False
                )
            )

        return render_template(
            "dashboard.html",
            total_products=total_products,
            low_stock=low_stock,
            overstock=overstock,
            optimal=optimal,
            pie_chart=pie_chart,
            forecast_chart=forecast_chart,
            products_chart=products_chart,
            revenue_chart=revenue_chart,
            scatter_chart=scatter_chart
        )

    except Exception as e:

        return render_template(
            "dashboard.html",
            error=str(e)
        )
# Upload Module
@app.route("/upload", methods=["GET", "POST"])
def upload():

    preview = None
    summary = None
    message = None

    if request.method == "POST":

        if "file" not in request.files:
            message = "No file selected"
            return render_template(
                "upload.html",
                message=message
            )

        file = request.files["file"]

        if file.filename == "":
            message = "Please select a file"
            return render_template(
                "upload.html",
                message=message
            )

        filename = file.filename

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(filepath)

        try:

            # CSV File
            if filename.endswith(".csv"):
                df = pd.read_csv(filepath)

            # Excel File
            elif filename.endswith((".xlsx", ".xls")):
                df = pd.read_excel(filepath)

            else:
                message = "Only CSV and Excel files are supported"

                return render_template(
                    "upload.html",
                    message=message
                )

            summary = validate_dataset(df)

            preview = df.head(10).to_html(
                classes="table table-striped table-hover",
                index=False
            )

            message = f"{filename} uploaded successfully"

        except Exception as e:
            message = f"Error: {str(e)}"

    return render_template(
        "upload.html",
        preview=preview,
        summary=summary,
        message=message
    )


# Preprocessing
@app.route("/preprocess")
def preprocess():

    filepath = "static/uploads"

    files = os.listdir(filepath)

    if len(files) == 0:

        return render_template(
            "preprocess.html",
            message="Please upload a dataset first."
        )

    latest_file = os.path.join(
        filepath,
        files[-1]
    )

    if latest_file.endswith(".csv"):
        df = pd.read_csv(latest_file)

    else:
        df = pd.read_excel(latest_file)

    cleaned_df, report = clean_data(df)

    cleaned_path = "static/uploads/cleaned_dataset.csv"

    cleaned_df.to_csv(
        cleaned_path,
        index=False
    )

    preview = cleaned_df.head().to_html(
        classes="table table-striped",
        index=False
    )

    return render_template(
        "preprocess.html",
        report=report,
        preview=preview
    )

# EDA
@app.route("/eda")
def eda():

    upload_folder = "static/uploads"

    files = os.listdir(upload_folder)

    if len(files) == 0:

        return render_template(
            "eda.html",
            message="Please upload a dataset first."
        )

    latest_file = os.path.join(
        upload_folder,
        files[-1]
    )

    try:

        if latest_file.endswith(".csv"):
            df = pd.read_csv(latest_file)

        else:
            df = pd.read_excel(latest_file)

        # Histogram
        fig1 = px.histogram(
            df,
            x="Sales",
            title="Sales Distribution"
        )

        chart1 = fig1.to_html(
            full_html=False
        )

        # Trend
        if "Date" in df.columns:

            df["Date"] = pd.to_datetime(
                df["Date"]
            )

            fig2 = px.line(
                df,
                x="Date",
                y="Sales",
                title="Sales Trend"
            )

            chart2 = fig2.to_html(
                full_html=False
            )

        else:
            chart2 = ""

        # Correlation Heatmap

        numeric_df = df.select_dtypes(
            include="number"
        )

        corr = numeric_df.corr()

        fig3 = ff.create_annotated_heatmap(
            z=corr.values,
            x=list(corr.columns),
            y=list(corr.index),
            annotation_text=round(corr,2).values,
            showscale=True
        )

        chart3 = fig3.to_html(
            full_html=False
        )

        return render_template(
            "eda.html",
            chart1=chart1,
            chart2=chart2,
            chart3=chart3
        )

    except Exception as e:

        return render_template(
            "eda.html",
            message=str(e)
        )


# Model Training
@app.route("/training")
def training():

    upload_folder = "static/uploads"

    cleaned_file = os.path.join(
        upload_folder,
        "cleaned_dataset.csv"
    )

    try:

        if not os.path.exists(cleaned_file):

            return render_template(
                "training.html",
                message="Please preprocess data first."
            )

        df = pd.read_csv(
            cleaned_file
        )

        results = train_models(
            df
        )

        return render_template(
            "training.html",
            results=results
        )

    except Exception as e:

        return render_template(
            "training.html",
            message=str(e)
        )


# Forecasting
@app.route("/forecasting")
def forecasting():

    cleaned_file = (
        "static/uploads/cleaned_dataset.csv"
    )

    try:

        if not os.path.exists(cleaned_file):

            return render_template(
                "forecasting.html",
                message="Please preprocess data first."
            )

        df = pd.read_csv(
            cleaned_file
        )

        forecast_df = generate_forecast(
            df
        )

        forecast_df.to_csv(
            "static/uploads/forecast.csv",
            index=False
        )

        preview = forecast_df.head(
            20
        ).to_html(
            classes="table table-striped",
            index=False
        )

        fig = px.line(
            forecast_df,
            y="Predicted_Sales",
            title="Predicted Sales Trend"
        )

        chart = fig.to_html(
            full_html=False
        )

        return render_template(
            "forecasting.html",
            preview=preview,
            chart=chart
        )

    except Exception as e:

        return render_template(
            "forecasting.html",
            message=str(e)
        )


# Inventory
@app.route("/inventory")
def inventory():

    forecast_file = (
        "static/uploads/forecast.csv"
    )

    try:

        if not os.path.exists(
            forecast_file
        ):

            return render_template(
                "inventory.html",
                message="Run forecasting first."
            )

        df = pd.read_csv(
            forecast_file
        )

        inventory_df = (
            optimize_inventory(df)
        )

        inventory_df.to_csv(
            "static/uploads/inventory_report.csv",
            index=False
        )

        preview = inventory_df.head(
            20
        ).to_html(
            classes="table table-striped",
            index=False
        )

        low_stock = len(
            inventory_df[
                inventory_df["Status"]
                == "Low Stock"
            ]
        )

        overstock = len(
            inventory_df[
                inventory_df["Status"]
                == "Overstock"
            ]
        )

        optimal = len(
            inventory_df[
                inventory_df["Status"]
                == "Optimal"
            ]
        )

        return render_template(
            "inventory.html",
            preview=preview,
            low_stock=low_stock,
            overstock=overstock,
            optimal=optimal
        )

    except Exception as e:

        return render_template(
            "inventory.html",
            message=str(e)
        )


# Reports
@app.route("/reports")
def reports():

    try:

        inventory_file = "static/uploads/inventory_report.csv"

        if not os.path.exists(inventory_file):

            return render_template(
                "reports.html",
                message="Run inventory optimization first."
            )

        df = pd.read_csv(inventory_file)

        total_products = len(df)

        low_stock = len(
            df[df["Status"] == "Low Stock"]
        )

        overstock = len(
            df[df["Status"] == "Overstock"]
        )

        optimal = len(
            df[df["Status"] == "Optimal"]
        )

        report_data = [

            f"Total Products: {total_products}",

            f"Low Stock Items: {low_stock}",

            f"Overstock Items: {overstock}",

            f"Optimal Items: {optimal}"

        ]

        # Create reports folder automatically
        os.makedirs(
            "static/reports",
            exist_ok=True
        )

        pdf_path = (
            "static/reports/business_report.pdf"
        )

        generate_pdf(
            report_data,
            pdf_path
        )

        return render_template(
            "reports.html",
            report_ready=True
        )

    except Exception as e:

        return render_template(
            "reports.html",
            message=str(e)
        )

if __name__ == "__main__":
    app.run(debug=True)