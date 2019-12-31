from pandas.api.types import is_numeric_dtype
from pandas.api.types import is_string_dtype
import pandas as pd
import numpy as np
import datetime
from scipy import stats

def train_cats(df):
    for n,c in df.items():
        if is_string_dtype(c): df[n] = c.astype('category').cat.as_ordered()
def fix_missing_name(df,col):
    df[col].fillna(0, inplace=True)
def fix_missing(df, col):
    if is_numeric_dtype(df[col]):
        median_value = df[col].median()
        df[col].fillna(median_value, inplace=True)
def fix_missing_date(df, col):
    if df[col].dtypes=='datetime64[ns]':
        last_day_2019 = '2019-12-31'
        datetime_last_day = datetime.datetime.strptime(last_day_2019, '%Y-%m-%d')
        df[col].fillna(datetime_last_day, inplace=True)
## Cohen'd
def Cohen_d(group1, group2):
    diff = group1.mean() - group2.mean()
    n1, n2 = len(group1), len(group2)
    var1 = group1.var()
    var2 = group2.var()
    # Calculate the pooled threshold as shown earlier
    pooled_var = (n1 * var1 + n2 * var2) / (n1 + n2)   
    # Calculate Cohen's d statistic
    d = diff / np.sqrt(pooled_var) 
    return abs(d)

## Create sample distribition
def get_sample(data, n):
    sample = []
    while len(sample) != n:
        x = np.random.choice(data)
        sample.append(x) 
    return sample

def get_sample_mean(sample):
    return sum(sample) / len(sample)

def create_sample_distribution(data, dist_size=1000, n=50):
    sample_dist = []
    while len(sample_dist) != dist_size:
        sample = get_sample(data, n)
        sample_mean = get_sample_mean(sample)
        sample_dist.append(sample_mean)
    return sample_dist

def result_cohen_d_p(p, d):
    print('p value is', p,'effect size is',d)
    if d >= 0.8:
        print('It has a large effect') 
    elif (d>=0.5)&(d<0.8): 
        print('It has a medium effect') 
    else: 
        print('It has a small effect')
    print('Reject Null Hypothesis') if p < 0.025 else print('Failed to reject Null Hypothesis')
