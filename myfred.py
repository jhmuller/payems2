import os
import sys
import datetime
import inspect
import pandas as pd
import numpy as np
from plotnine import ggplot
import matplotlib as mpl
import matplotlib.pyplot as plt

sys.path.append('../fredapi')
from fredapi.fredapi import fred
#import fredapi
Fred = fred.Fred(api_key_file="fred_api_key")
#Fred = fredapi.fred.Fred(api_key_file="fred_api_key")
#print("fredapi version {0}".format(fredapi.fredapi.__version__))

def import_versions():
    mlist = list(filter(lambda x: inspect.ismodule(x[1]), locals().items()))
    vi = sys.version_info
    print("version {0}.{1}.{2} of Python".format(vi.major, vi.minor, vi.micro))
    for name, mod in mlist:
        if name.startswith("__"):
            continue
        if hasattr(mod, "__version__"):
            print("version {1} of {0}".format(name, mod.__version__))

def get_id_data(fred_ids):
    dfs = []
    obs_start = "2010-01-01"
    obs_end = datetime.date.today().strftime("%Y-%m-%d")
    for ser in fred_ids.itertuples():
        print("series: {0}, obs_start: {1}, obs_end: {2}".format(ser.series_id,
                                                                 obs_start,
                                                                 obs_end))
        try:
            data_series= Fred.get_series(series_id=ser.series_id,
                                                  observation_start=obs_start,
                                                  observation_end=obs_end)

            print(data_series.shape)
        except AttributeError as ae:
            print("Error calling Fred")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            break
        except Exception as exc:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print('')

        try:
            print("error processing")
            all_df = pd.DataFrame(data_series)
            all_df.reset_index(inplace=True)
            all_df.columns = ['date', 'val']
            all_df['series_id'] = ser.series_id
            all_df.sort_values(by="date", ascending=True, inplace=True)
            print("rows= {0}".format(all_df.shape[0]))
            dfs.append(all_df)
        except Exception as exc:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            break
    if len(dfs) > 0:
        obs_df = pd.concat(dfs)
        obs_df = obs_df.merge(fred_ids, on='series_id')
        print(datetime.datetime.now())
    return obs_df


if __name__ == "__main__":
    fred_ids = pd.read_csv('fred_ids.csv', index_col=None, sep=',')
    print(fred_ids)
    df = get_id_data(fred_ids)
    df.sort_values(by="date", ascending=True, inplace=True)
    df.to_csv('fred_data.csv', index=False)
    print(df.shape)

