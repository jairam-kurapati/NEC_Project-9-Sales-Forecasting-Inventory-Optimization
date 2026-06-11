import pandas as pd


def remove_outliers_iqr(df):

    numeric_cols = df.select_dtypes(include=["number"]).columns

    removed = 0

    for col in numeric_cols:

        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)

        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        before = len(df)

        df = df[
            (df[col] >= lower) &
            (df[col] <= upper)
        ]

        removed += before - len(df)

    return df, removed


def clean_data(df):

    report = {}

    # Missing values before cleaning
    report["missing_before"] = df.isnull().sum().sum()

    # Fill numeric columns
    numeric_cols = df.select_dtypes(include=["number"]).columns

    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())

    # Fill categorical columns
    categorical_cols = df.select_dtypes(include=["object"]).columns

    for col in categorical_cols:
        df[col] = df[col].fillna("Unknown")

    report["missing_after"] = df.isnull().sum().sum()

    # Duplicate removal
    report["duplicates_before"] = df.duplicated().sum()

    df = df.drop_duplicates()

    report["duplicates_after"] = df.duplicated().sum()

    # Outlier removal
    df, outliers_removed = remove_outliers_iqr(df)

    report["outliers_removed"] = outliers_removed

    return df, report