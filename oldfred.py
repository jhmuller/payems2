import os
import sys
import datetime
import inspect
import pandas as pd
import numpy as np
from plotnine import ggplot
import matplotlib as mpl
import matplotlib.pyplot as plt

#sys.path.append('../fredapi')
from fredapi import fred
import fredapi
Fred = fredapi.fred.Fred(api_key_file="fred_api_key")
print("fredapi version {0}".format(fredapi.__version__))

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
    obs_end = datetime.date.today()
    for ser in fred_ids.itertuples():
        print("series: {0}, obs_start: {1}, obs_end: {2}".format(ser.series_id,
                                                                 obs_start,
                                                                 obs_end))
        try:
            all_df = Fred.get_series_all_releases(series_id=ser.series_id,
                                                  observation_start=obs_start,
                                                  observation_end=obs_end,
                                                  verbosity=1)
            print(all_df.shape)
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

        try:
            print("error processing")
            tdf = all_df.sort_values(by="realtime_start", ascending=True).groupby(by="date").head(1)
            tdf['series_id'] = ser.series_id
            tdf['date'] = tdf['date'].dt.date
            print("rows= {0}".format(tdf.shape[0]))
            dfs.append(tdf)
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
    fred_ids = pd.read_csv('fred_ids.csv', index_col=None, sep='|')
    print(fred_ids)
    df = get_id_data(fred_ids)
