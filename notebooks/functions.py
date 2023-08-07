import pandas as pd
import polars as pl
import glob

 # station ids for 30 citi bike stations in lower Manhattan



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

    
if __name__ == '__main__':
    get_data()
    sample_data()
    sample_group_count()
    concat_dfs()
    yearly_clean_data()
    get_station_data()
