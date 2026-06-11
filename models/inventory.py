import pandas as pd


def optimize_inventory(df):

    inventory_report = []

    for _, row in df.iterrows():

        sales = row["Predicted_Sales"]
        inventory = row["Inventory"]

        lead_time = 7
        service_factor = 1.65

        safety_stock = (
            service_factor *
            (sales ** 0.5)
        )

        reorder_point = (
            sales * lead_time
        ) + safety_stock

        if inventory < reorder_point:

            status = "Low Stock"

            recommendation = (
                f"Order {int(reorder_point - inventory)} units"
            )

        elif inventory > reorder_point * 2:

            status = "Overstock"

            recommendation = (
                "Reduce inventory"
            )

        else:

            status = "Optimal"

            recommendation = (
                "Maintain current stock"
            )

        inventory_report.append({

            "Product_ID":
            row["Product_ID"],

            "Product_Name":
            row["Product_Name"],

            "Inventory":
            inventory,

            "Predicted_Sales":
            round(sales, 2),

            "Safety_Stock":
            round(safety_stock, 2),

            "Reorder_Point":
            round(reorder_point, 2),

            "Status":
            status,

            "Recommendation":
            recommendation

        })

    return pd.DataFrame(
        inventory_report
    )