import pandas as pd
from datetime import datetime
import numpy as np


def check_type(start_or_end):
    return (type(start_or_end) is pd.tslib.Timestamp) or (type(start_or_end) is type(start_or_end) is datetime)


def df_ylim(df):
    ordered_values = sorted(set(df[~np.isnan(df)].values.ravel()))
    if (len(ordered_values) < 3):
        return None
    return (ordered_values[2], ordered_values[-2])


def plot(df, xlim=None, auto_set_y=True, scale_index_lag=None, y_sup=None, **kargs):
    if scale_index_lag is not None:
        if hasattr(df, "columns"):
            max_index = np.where(df.index == df.idxmax().min())[0][0]
        else:
            max_index = df[~np.isnan(df)].values.argmax()
        scale_index = max_index - scale_index_lag
        _df = df.ix[:scale_index]
    else:
        _df = df
    ylim = df_ylim(_df) if auto_set_y else None
    if "ylim" in kargs:
        ylim = kargs["ylim"]
        del kargs["ylim"]
    if ylim is not None and y_sup is not None:
        ylim = (ylim[0], min(ylim[1], y_sup))
    start_date, end_date = df.index[0].strftime("%d/%m/%y"), df.index[-1].strftime("%d/%m/%y")
    title = start_date + " to " + end_date
    if "title" in kargs:
        title = kargs["title"]
        del kargs["title"]
    if xlim is None:
        return df.plot(ylim=ylim, title=title, **kargs)
    else:
        partial_df = df[xlim[0]:xlim[1]]
        if (len(partial_df) > 0):
            return partial_df.plot(ylim=ylim, title=title, **kargs)


def annotate(ax, column, width, text):
    y = column.median()
    begin, end = column.index[0], column.index[width]
    ax.annotate(s='', xy=(begin, y), xytext=(end, y), arrowprops=dict(arrowstyle='<->'))
    ax.text(column.index[int(width / 2)], y + 10, text, horizontalalignment='center', verticalalignment='center',
            fontsize=10, color='k')
