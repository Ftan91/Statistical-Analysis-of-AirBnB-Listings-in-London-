from pandas.api.types import is_numeric_dtype
from pandas.api.types import is_string_dtype
import pandas as pd
import numpy as np
import datetime


def train_cats(df):
    for n,c in df.items():
        if is_string_dtype(c): df[n] = c.astype('category').cat.as_ordered()
            
def fix_missing(df, col):
    if is_numeric_dtype(df[col]):
        median_value = df[col].median()
        df[col].fillna(median_value, inplace=True)
def fix_missing_date(df, col):
    if df[col].dtypes=='datetime64[ns]':
        last_day_2019 = '2019-12-31'
        datetime_last_day = datetime.datetime.strptime(last_day_2019, '%Y-%m-%d')
        df[col].fillna(datetime_last_day, inplace=True)
    