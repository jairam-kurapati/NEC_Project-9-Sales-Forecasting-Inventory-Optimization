def validate_dataset(df):

    result = {}

    result["rows"] = len(df)

    result["columns"] = len(df.columns)

    result["missing"] = df.isnull().sum().sum()

    result["duplicates"] = df.duplicated().sum()

    return result