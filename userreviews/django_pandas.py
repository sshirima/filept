import pandas as pd

def to_django(df, DjangoModel, if_exists="fail"):
    """Uses bulk_create to insert data to Django table
    if_exists: see pd.DataFrame.to_sql API

    Ref: https://www.webforefront.com/django/multiplemodelrecords.html
    """
    import numpy as np

    if if_exists not in ["fail", "replace", "append"]:
        raise Exception("if_exists must be fail, replace or append")

    if if_exists == "replace":
        DjangoModel.objects.all().delete()
    elif if_exists == "fail":
        if DjangoModel.objects.all().count() > 0:
            raise ValueError("Data already exists in this table")
    else:
        pass

    dct = df.replace({np.nan: None}).to_dict(
        "records"
    )  # replace NaN with None since Django doesn't understand NaN

    bulk_list = []
    for x in dct:
        bulk_list.append(DjangoModel(**x))
    DjangoModel.objects.bulk_create(bulk_list)
    print("Successfully saved DataFrame to Django table.")

from django.db import models
def check_dataframe_columns(
    df: pd.DataFrame, DjangoModel: models.Model, strict: bool = False
):
    """Raises KeyError if DataFrame doesn't match a Django model

    Parameters
    ----------
    df: A pandas DataFrame object
    DjangoModel: A Django model
    strict: If strict is True, then the DataFrame must contain the exact set of columns
        as the Django mode
    """
    # todo: add column type checking
    error_list = []
    dataframe_columns = set(df.columns)
    django_columns = set(map(lambda x: x.name, DjangoModel._meta.fields))
    if not dataframe_columns.issubset(django_columns):
        unknown_columns = list(dataframe_columns - django_columns)
        unknown_columns.sort()  # to be repeatable
        error_list.append(
            f"DataFrame contains unknown column(s): {', '.join(unknown_columns)}"
        )
    if strict and not dataframe_columns == django_columns:
        missing_columns = list(django_columns - dataframe_columns)
        missing_columns.sort()  # to be repeatable
        error_list.append(
            f"With strict=True, DataFrame is missing column(s): {', '.join(missing_columns)}"
        )

    if error_list:
        raise KeyError(" | ".join(error_list))