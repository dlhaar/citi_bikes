import pandas as pd
import polars as pl
import glob
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns



def get_data(file_path:str)->list:
    """
    Reads in multiple files fitting the file_path.
    Selects two columns ('started_at' and 'start_station_id'), and
    creates three columns from 'started_at':
        'week_number': the week number of the year
        'weekday': the day of week, as an integer where monday = 1 and sunday = 7
        'hour': the hour, with the time rounded up or down to the nearest hour

    Each file read in is a dataframe and the function returns a list in which 
    each element is a dataframe

    Input
    file_path: string with the file_path to get all the files for a year eg 'data/raw/2021*.csv'

    Output
    a list of dataframes, one for each file that was read in


    """
    #scan in datasets and get the cells we need
    queries = []
    for file in glob.glob(file_path):
        q = (
            pl.scan_csv(file,
                        dtypes={'started_at':pl.Datetime,
                                'start_station_id':pl.Utf8},
                       ignore_errors=True)
            .select(['started_at', 'start_station_id'])
            .filter(pl.col('start_station_id').is_in(["4846.01","4889.06",
                                                    "4953.04","4962.01",
                                                    "4962.02","4962.08",
                                                    "4993.02","4993.13",
                                                    "5001.08","5033.01",
                                                     "5065.04","5065.12",
                                                     "5065.14","5073.07",
                                                     "5096.12","5105.01",
                                                     "5114.06","5137.11",
                                                     "5137.13","5145.02",
                                                     "5175.08","5184.08",
                                                     "5207.01","5216.04",
                                                     "5216.06","5288.08",
                                                     "5288.09","5288.12",
                                                     "5297.02","5329.08"]))
            .with_columns(
            [
            #(pl.col("started_at").dt.year().alias("year")),
            #(pl.col("started_at").dt.week().alias("week_number")),
            (pl.col("started_at").dt.round("1h").alias("started_at_rounded")),
            (pl.col("started_at").dt.weekday().alias("weekday")),
            #(pl.col("started_at").dt.round("1h").dt.hour().alias("hour"))
            ]
            )
            .drop('started_at')
            
        )
        queries.append(q)

    dataframes = pl.collect_all(queries)

    total_rows = 0
    for df in dataframes:
        total_rows += df.shape[0]
    print('The total rows in the entire df is {}'.format(total_rows))

    return dataframes


def sample_data(dataframes:list)->list:
    """
    The input is a list of dataframes. For each dataframe in the list, 
    the function returns 10% sample of the dataframe.

    Input
    a list of dataframes

    Output
    a list of dataframes

    """
    dataframes_sample=[]
    for df in dataframes:
        dataframes_sample.append(df.sample(fraction=0.1, seed=22))

    total_rows = 0
    for df in dataframes_sample:
        total_rows += df.shape[0]
    print('The total rows in the sample is {}'.format(total_rows))

    return dataframes_sample


def sample_group_count(dataframe_sample:list)->list:
    """
    The input is a list of dataframes. For each dataframe, it is grouped by week_numer,
    weekday, hour, and start_station_id, and gets the count (this is the number of rides starting
    from the station for that hour)


    """
    dataframes_grouped=[]
    for df in dataframe_sample:
        dataframes_grouped.append(df.groupby(['started_at_rounded', 'weekday', 'start_station_id'])
                                .count()
                                 .sort(by=['started_at_rounded', 'weekday', 'start_station_id'])
                    )
    total_rows = 0
    total_count = 0
    for df in dataframes_grouped:
        total_rows += df.shape[0]
        total_count += df['count'].sum()
    print('Total rows: {}, total count {}'.format(total_rows, total_count))
        
    return dataframes_grouped

#concat dfs
def concat_dfs(dataframes_agg):
    """
    Input is a list of dataframes. This function concats the dataframes and 
    """
    data_clean = pl.concat([df for df in dataframes_agg])
    data_clean = data_clean.drop_nulls()
    data_clean = data_clean.sort(by=['started_at_rounded', 'weekday', 'start_station_id'])
    
    print('total rows: {}, total count in the concated df is {}'.format(data_clean.shape[0], data_clean['count'].sum()))
    
    return data_clean


def yearly_clean_data(file_path):
    data = get_data(file_path)
    #data_sample = sample_data(data)
    #data_grouped = sample_group_count(data_sample)
    data_grouped = sample_group_count(data)
    data_concat = concat_dfs(data_grouped)
    return data_concat

def get_station_data(file_path:str)->pl.DataFrame:
    """
    Reads in multiple files fitting the file_path.
    Selects station data and then filters for the stations in the other dataset
    Selects one lat and long value for each station id

    Input
    file_path: string with path to files

    Output
    polars DataFrame
    

    """
    #scan in datasets and get the cells we need
    df = pl.read_csv(file_path,
                     dtypes={'start_station_id':pl.Utf8},
                    columns=['start_station_id', 'start_station_name', 'start_lat', 'start_lng'])
    
    #filter for the station ids in our dataset
    df = df.filter(pl.col('start_station_id').is_in(["4846.01","4889.06",
                                                    "4953.04","4962.01",
                                                    "4962.02","4962.08",
                                                    "4993.02","4993.13",
                                                    "5001.08","5033.01",
                                                     "5065.04","5065.12",
                                                     "5065.14","5073.07",
                                                     "5096.12","5105.01",
                                                     "5114.06","5137.11",
                                                     "5137.13","5145.02",
                                                     "5175.08","5184.08",
                                                     "5207.01","5216.04",
                                                     "5216.06","5288.08",
                                                     "5288.09","5288.12",
                                                     "5297.02","5329.08"]))

    #get one lat/long value for each station id --> default keep = 'any'
    df = df.unique(subset=['start_station_id', 'start_station_name']).sort(by=['start_station_id'])
    
    return df

def extract_dt_features(df, cyclic=False):
    df_temp = df.copy()

    if cyclic == False:
        df_temp['week_number'] = df_temp['started_at_rounded'].dt.isocalendar().week
        df_temp['month'] = df_temp['started_at_rounded'].dt.month
        df_temp['weekday'] = df_temp['started_at_rounded'].dt.dayofweek # Mon =0, Sun = 6
        df_temp['hour'] = df_temp['started_at_rounded'].dt.hour #0 to 23
    
    
    else:
        df_temp['week_number_sin'] = np.sin(2 * np.pi * df_temp['started_at_rounded'].dt.isocalendar().week/52.0)
        df_temp['week_number_cos'] = np.cos(2 * np.pi * df_temp['started_at_rounded'].dt.isocalendar().week/52.0)
        
        
        df_temp['month_sin'] = np.sin(2 * np.pi * df_temp['started_at_rounded'].dt.month/12.0)
        df_temp['month_cos'] = np.cos(2 * np.pi * df_temp['started_at_rounded'].dt.month/12.0)
        
        
        df_temp['weekday_sin'] = np.sin(2 * np.pi * df_temp['started_at_rounded'].dt.dayofweek/7.0)
        df_temp['weekday_cos'] = np.cos(2 * np.pi * df_temp['started_at_rounded'].dt.dayofweek/7.0) 
        
        
        df_temp['hour_sin'] = np.sin(2 * np.pi * df_temp['started_at_rounded'].dt.hour/24.0) 
        df_temp['hour_cos'] = np.cos(2 * np.pi * df_temp['started_at_rounded'].dt.hour/24.0) 

    #drop datetime col
    df_temp.drop('started_at_rounded', axis=1, inplace=True)

    return df_temp

def prep_for_eval(y_real_train, y_real_test, y_pred_train, y_pred_test):
    return y_real_train.to_list(), y_real_test.to_list(), y_pred_train.tolist(), y_pred_test.tolist()

def error_metrics_report(y_real_train: list, y_real_test: list, y_pred_train: list, y_pred_test: list) -> pd.DataFrame:
    '''
    This function takes the real values and any model predictions for the Train and Test sets and returns a Pandas
    DataFrame with a summary of error metrics for the Train and Test sets like this:

    | Metric | Train | Test |
    |--------|-------|------|
    | MAE    | value | value|
    | MSE    | value | value|
    | RMSE   | value | value|
    | R2     | value | value|

    Inputs:
    y_real_train: Python list with the real values to be predicted in the Train set
    y_real_test: Python list with the real values to be predicted in the Test set
    y_pred_train: Python list with the model's predicted values in the Train set
    y_pred_test:  Python list with the model's predicted values in the Test set
    '''
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

    MAE_train = mean_absolute_error(y_real_train, y_pred_train)
    MAE_test  = mean_absolute_error(y_real_test, y_pred_test)

    # Mean squared error
    MSE_train = mean_squared_error(y_real_train, y_pred_train)
    MSE_test  = mean_squared_error(y_real_test, y_pred_test)

    # Root mean squared error
    RMSE_train = mean_squared_error(y_real_train, y_pred_train, squared=False)
    RMSE_test  = mean_squared_error(y_real_test,  y_pred_test,  squared=False)

    # R2
    R2_train = r2_score(y_real_train, y_pred_train)
    R2_test  = r2_score(y_real_test,  y_pred_test)

    results = {"Metric": ["MAE","MSE", "RMSE", "R2"],
               "Train": [MAE_train, MSE_train, RMSE_train, R2_train],
               "Test":  [MAE_test, MSE_test, RMSE_test, R2_test]}

    results_df = pd.DataFrame(results).round(2)

    return results_df

def plot_real_predicted(test_or_train, y_real, y_pred):
    
    fig, axs = plt.subplots(3,1, figsize=(24,8))
    
    #histogram
    residual = np.array(y_real) - np.array(y_pred)
    sns.histplot(residual, ax=axs[0])
    axs[0].set_xlabel('Residuals')
    axs[0].set_ylabel('count')

    #scatter - error and y_real
    sns.scatterplot(x = y_real, y=residual, ax=axs[1])
    axs[1].set_xlabel('y_real')
    axs[1].set_ylabel('Residuals')

    #scatterplot
    sns.scatterplot(x = y_real, y = y_pred, ax=axs[2])

    if test_or_train == 'test':
        axs[2].set_xlabel('Real Values - Test')
        axs[2].set_ylabel('Predicted Values - Test')

    else:
        axs[2].set_xlabel('Real Values - Train')
        axs[2].set_ylabel('Predicted Values - Train')

    plt.tight_layout()
    
    plt.show()
    
    
if __name__ == '__main__':
    get_data()
    sample_data()
    sample_group_count()
    concat_dfs()
    yearly_clean_data()
    get_station_data()
    extract_dt_features()
    prep_for_eval()
    error_metrics_report()
    plot_real_predicted()
