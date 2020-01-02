"""external modules created by Shuyu and Finn"""
from pandas.api.types import is_numeric_dtype
from pandas.api.types import is_string_dtype
import pandas as pd
import numpy as np
import datetime
from scipy import stats
import itertools # for combinations
from statsmodels.stats.power import TTestIndPower, TTestPower
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.stats.multicomp import MultiComparison

#change string types to categorical types
def train_cats(df):
    for n,c in df.items():
        if is_string_dtype(c): df[n] = c.astype('category').cat.as_ordered()
            
#replace missing name with zero so later the name length can be zero
def fix_missing_name(df,col):
    df[col].fillna(0, inplace=True)
    
#general replace missing value tool
def fix_missing(df, col):
    if is_numeric_dtype(df[col]):
        median_value = df[col].median()
        df[col].fillna(median_value, inplace=True)

#replace missing date to 2019-12-31
def fix_missing_date(df, col):
    if df[col].dtypes=='datetime64[ns]':
        last_day_2019 = '2019-12-31'
        datetime_last_day = datetime.datetime.strptime(last_day_2019, '%Y-%m-%d')
        df[col].fillna(datetime_last_day, inplace=True)

#Generates x simulations of x sample size of given dataset and returns means of each simulation according to Central Limit Theorem
def central_limit_mean_sample(dataset, sample_size, num_simulations, return_mean = False):    
    random_chosen = [np.mean(np.random.choice(dataset, size = sample_size)) 
                     for i in range(num_simulations)]
    if return_mean == False:
        return random_chosen
    else:
        return random_chosen, round(np.mean(random_chosen), 2)

#Returns pooled standard deviation of both samples. Assumes sample sizes are similar for now
def pooled_stdev(sample1, sample2): 
    std_dev1 = np.var(sample1) * len(sample1)
    std_dev2 = np.var(sample2) * len(sample2)
    denom = len(sample1) + len(sample2)    
    return np.sqrt((std_dev1 + std_dev2) / denom)

#Returns effect size between two samples. Function also includes correction if sample size < 50
def effect_size(sample1, sample2):
    pooled_sd = pooled_stdev(sample1, sample2)
    mean1 = np.mean(sample1)
    mean2 = np.mean(sample2)
    size = min(len(sample1), len(sample2))
    d = (mean2 - mean1) / pooled_sd
    if size < 50:
        return np.abs((d * ((size - 3) / (size - 2.25)) * np.sqrt((size - 2) / size)))
    else:
        return np.abs(d) 
    
#welch t test
def welch_ttest(sample1, sample2):
    "Welch ttest formula"
    n1 = len(sample1)
    n2 = len(sample2)    
    var1 = np.var(sample1, ddof = 1)
    var2 = np.var(sample2, ddof = 1)    
    se1 = var1/n1
    se2 = var2/n2    
    mean1 = np.mean(sample1)
    mean2 = np.mean(sample2)   
    return abs((mean2 - mean1) / np.sqrt(se1 + se2))

#degree of freedom
def welch_degrees_of_freedom(sample1, sample2):
    s1 = np.var(sample1, ddof = 1)
    s2 = np.var(sample2, ddof = 1)
    n1 = len(sample1)
    n2 = len(sample2)    
    numerator = (s1 / n1 + s2 / n2) ** 2
    denominator = (s1 / n1) ** 2 / (n1 - 1) + (s2 / n2) ** 2 / (n2 - 1)    
    return numerator/denominator

#calculate p value
def p_value(sample1, sample2, two_sided = False):
    t = welch_ttest(sample1, sample2)
    df = welch_degrees_of_freedom(sample1, sample2)
    p = 1 - stats.t.cdf(np.abs(t), df)
    
    if two_sided == True:
        return (2*p)
    else:
        return p

def threshold(sample1, sample2):
    mean1 = np.mean(sample1)
    mean2 = np.mean(sample2)
    std1 = np.std(sample1)
    std2 = np.std(sample2)
    return (std1 * mean2 + std2 * mean1) / (std1 + std2)

#critical p value
def critical_t(alpha, df):
    return stats.t.ppf(1.0 - alpha, df)

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

def create_sample_distribution(data, dist_size=10000, n=50):
    sample_dist = []
    while len(sample_dist) != dist_size:
        sample = get_sample(data, n)
        sample_mean = get_sample_mean(sample)
        sample_dist.append(sample_mean)
    return sample_dist

#results of p value and cohen'd
def result_cohen_d_p(p, d):
    print('p value is', p,'effect size is',d)
    if d >= 0.8:
        print('It has a large effect') 
    elif (d>=0.5)&(d<0.8): 
        print('It has a medium effect') 
    else: 
        print('It has a small effect')
    print('Reject Null Hypothesis') if p < 0.025 else print('Failed to reject Null Hypothesis')

#check quantile value between 0.9-1
def check_quantile(df):
    quantiles = np.linspace(0.9,1,11)
    for i in quantiles:
        print ('{} quantile: {}'.format(round(i,2), df.quantile(i)))

#print p value and cohen'd in dataframe
def results_p_d(df):
    result_df=pd.DataFrame(columns=['group','p',"cohen'd",'hypothesis state'])
    combos = itertools.combinations(df, 2)
    for n, combo in enumerate(list(combos)):
        if (n <= 6):
            num_review1 = combo[0][1]
            num_review2 = combo[1][1]
            p = stats.ttest_ind(num_review1, num_review2, equal_var=False)[1]
            d = Cohen_d(np.array(num_review1), np.array(num_review2))
            result_df.loc[n] = ['0'+','+str(combo[1][0]*100)+'-'+str(combo[1][0]*100+100)]+[p]+[d]+['Reject Null Hypothesis' if p < 0.025 else 'Failed to reject Null Hypothesis']
        else:
            num_review1 = combo[0][1]
            num_review2 = combo[1][1]
            p = stats.ttest_ind(num_review1, num_review2, equal_var=False)[1]
            d = Cohen_d(np.array(num_review1), np.array(num_review2))
            result_df.loc[n] = [str(combo[0][0]*100-100)+'-'+str(combo[0][0]*100)+','+str(combo[1][0]*100-100)+'-'+str(combo[1][0]*100 )]+[p]+[d]+['Reject Null Hypothesis' if p < 0.025 else 'Failed to reject Null Hypothesis']
    return result_df
