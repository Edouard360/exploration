import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

def check_type(start_or_end):
    return (type(start_or_end) is pd.tslib.Timestamp) or (type(start_or_end) is type(start_or_end) is datetime)

def no_values_message(axe):
    axe.text(0.5, 0.5, 'No values found',horizontalalignment='center',verticalalignment='center',fontsize=20, color='blue')

def df_ylim(df):
    mad = abs(df - df.median()).median()
    return ((df.median() - 3 * mad).min(), (df.median() + 3 * mad).max())

def plot(df, axe=None, xlim=None,auto_set_y =True):
    if axe is None:
        axe = plt.subplot()
    if xlim is None:
        df.plot(ax=axe)
    else:
        full_df = df[xlim[0]:xlim[1]]
        if (len(full_df) > 0):
            df[xlim[0]:xlim[1]].plot(ax=axe)
        else:
            no_values_message(axe);return
    if (auto_set_y):
        axe.set_ylim(df_ylim(df))