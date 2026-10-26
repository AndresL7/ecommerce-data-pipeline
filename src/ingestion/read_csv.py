from pathlib import Path

import pandas as pd

EXPECTED_SCHEMAS = {
    "customers": {"customer_id", "name"},
    "orders": {"order_id", "customer_id"},
    "order_items": {
        "order_id",
        "product_id",
        "quantity",
        "unit_price",
    },
    "products": {"product_id", "name", "price"},
}

PRIMARY_KEYS = {
    "customers": ["customer_id"],
    "orders": ["order_id"],
    "products": ["product_id"],
}

def read_csv(file_path):
    schema_name = file_path.stem

    if schema_name not in EXPECTED_SCHEMAS:
        raise ValueError(f"No schema defined for file: {file_path.name}")

    try:
        df = pd.read_csv(file_path, sep=";", encoding="utf-8")

    except pd.errors.EmptyDataError:
        raise ValueError(
            f"CSV file '{file_path.name}' is empty or has no header."
        )

    if df.empty:
        raise ValueError(
            f"CSV file '{file_path.name}' contains no data rows."
        )

    missing_columns = EXPECTED_SCHEMAS[schema_name] - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns in '{file_path.name}': "
            f"{', '.join(sorted(missing_columns))}"
        )

    return df

def validate_primary_keys(dataframes):
    for table, columns in PRIMARY_KEYS.items():
        df = dataframes[table]

        if df[columns].isna().any().any():
            raise ValueError(
                f"Null primary key values found in table '{table}'."
            )

        duplicate_mask = df.duplicated(
            subset=columns,
            keep=False,
        )

        if duplicate_mask.any():
            examples = df.loc[
                duplicate_mask, columns
            ].head(5).to_dict("records")

            raise ValueError(
                f"Duplicate primary keys found in '{table}': {examples}"
            )

def validate_order_items(df):
    required_columns = [
        "order_id",
        "product_id",
        "quantity",
        "unit_price",
    ]

    if df[required_columns].isna().any().any():
        null_columns = df[required_columns].columns[
            df[required_columns].isna().any()
        ].tolist()

        raise ValueError(
            f"Null values found in order_items: {null_columns}"
        )

    duplicate_mask = df.duplicated(
        subset=["order_id", "product_id"],
        keep=False,
    )

    if duplicate_mask.any():
        examples = df.loc[
            duplicate_mask, ["order_id", "product_id"]
        ].head(5).to_dict("records")

        raise ValueError(
            f"Duplicate order-item keys found: {examples}"
        )

    quantity = pd.to_numeric(
        df["quantity"],
        errors="coerce",
    )

    invalid_quantity = (
        quantity.isna()
        | (quantity <= 0)
        | (quantity % 1 != 0)
    )

    if invalid_quantity.any():
        invalid_rows = df.index[invalid_quantity].tolist()[:5]

        raise ValueError(
            "Quantity must contain positive integers. "
            f"Invalid rows: {invalid_rows}"
        )

    unit_price = pd.to_numeric(
        df["unit_price"],
        errors="coerce",
    )

    invalid_price = unit_price.isna() | (unit_price < 0)

    if invalid_price.any():
        invalid_rows = df.index[invalid_price].tolist()[:5]

        raise ValueError(
            "Unit price must be numeric and non-negative. "
            f"Invalid rows: {invalid_rows}"
        )

    df["quantity"] = quantity.astype("int64")
    df["unit_price"] = unit_price

def validate_referential_integrity(dataframes):
    relationships = [
        ("orders", "customer_id", "customers", "customer_id"),
        ("order_items", "order_id", "orders", "order_id"),
        ("order_items", "product_id", "products", "product_id"),
    ]

    for table, column, parent_table, parent_column in relationships:
        child_values = dataframes[table][column]
        parent_values = dataframes[parent_table][parent_column]

        invalid_mask = ~child_values.isin(parent_values)

        if invalid_mask.any():
            invalid_values = (
                child_values[invalid_mask]
                .drop_duplicates()
                .head(5)
                .tolist()
            )

            raise ValueError(
                f"{table}.{column} contains references absent from "
                f"{parent_table}.{parent_column}: {invalid_values}"
            )

def main():
    data_path = (
        Path(__file__).resolve().parents[2]
        / "data"
        / "raw"
    )

    csv_files = sorted(data_path.glob("*.csv"))

    if not csv_files:
        print(f"No CSV files found in: {data_path}")
        return

    dataframes = {}
    failed_files = []

    # Read CSV files and validate their schemas.
    for file_path in csv_files:
        try:
            df = read_csv(file_path)

            dataframes[file_path.stem] = df

            print(
                f"Loaded {file_path.name}: "
                f"{len(df)} records, {len(df.columns)} columns"
            )

        except (ValueError, OSError, pd.errors.ParserError) as error:
            failed_files.append(file_path.name)

            print(f"Error processing {file_path.name}: {error}")

    # Check that all required tables were loaded.
    required_tables = set(EXPECTED_SCHEMAS)

    missing_tables = required_tables - set(dataframes)

    if missing_tables:
        print(f"Missing tables: {sorted(missing_tables)}")
        return

    try:
        # Validate order_items data.
        validate_order_items(dataframes["order_items"])

        # Validate primary keys.
        validate_primary_keys(dataframes)

        # Validate foreign key relationships.
        validate_referential_integrity(dataframes)

    except ValueError as error:
        print(f"Data validation failed: {error}")
        return

    print("\nAll data validations passed.")

    # Print a summary of the loaded tables.
    print("\nData summary:")

    for table, df in dataframes.items():
        print(f"{table}: {len(df)} records")

    if failed_files:
        print(f"\nFiles that failed to load: {failed_files}")


if __name__ == "__main__":
    main()
