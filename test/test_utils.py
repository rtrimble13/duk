"""
Shared test utilities for duk tests.
"""


def verify_dataframe_precision(df, precision, exclude_columns=None):
    """
    Helper function to verify that all numeric columns in a DataFrame
    have values rounded to the specified precision.

    Args:
        df: pandas DataFrame to verify
        precision: Expected number of decimal places
        exclude_columns: List of column names to exclude from verification
            (default: ['date'])
    """
    if exclude_columns is None:
        exclude_columns = ["date"]

    # Check both float and int columns (consistent with cli.py implementation)
    for col in df.select_dtypes(include=["float", "int"]).columns:
        if col not in exclude_columns:
            for val in df[col].dropna():
                # Check that the value has at most the specified decimal places
                assert round(val, precision) == val, (
                    f"Column '{col}' value {val} does not match "
                    f"precision {precision}"
                )
