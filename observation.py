import pandas as pd
import numpy as np
from datetime import timedelta
from tools import sequence_to_interval, lazyprop
from interval import Interval

class Observation:
    def __init__(self, path, reactor_site, suffix_list, format="%Y-%m-%dT%H:%M:%S.000Z",
                 hours_backfill = 1, verbose=0, ignore_keys = []):
        self.verboseprint = print if verbose else lambda *a, **k: None
        self.verboseprint("Loading in memory %i observations..." % (int(len(suffix_list)),))
        self.hours_backfill = hours_backfill
        files_name = [reactor_site + "-" + suffix + ".txt" for suffix in suffix_list]
        list_df = [pd.read_csv(path + file_name, sep=";") for file_name in files_name]
        self.ignore_keys = ignore_keys
        for df, tag in zip(list_df, suffix_list):
            df.columns = ["date", tag]
            df.drop_duplicates(subset="date", inplace=True)
            df['date'] = pd.to_datetime(df['date'], format=format)
            df.set_index('date', inplace=True)
        self.verboseprint("Concatenation...")
        self.df = pd.concat(list_df, axis=1)
        self.bad_labels_dict = {}
        self.change_isolated_wrong_values()
        self.verboseprint("Forward Filling...")
        self.df.fillna(method='ffill', inplace=True)
        self.verboseprint("Backward Filling...")
        self.df.fillna(method='bfill', inplace=True)

    def change_isolated_wrong_values(self):
        self.verboseprint("Changing isolated wrong values...")
        for column in self.df:
            bad_labels = self.df.index[((self.df[column] == self.df[column].max()) | (self.df[column] == 0))]
            bad_labels = sequence_to_interval(bad_labels, timedelta(minutes=10)) # Stricly consecutive wrong values
            to_change_index = (bad_labels[:,1] - bad_labels[:,0]) <= timedelta(hours=self.hours_backfill)
            for begin, end in bad_labels[to_change_index]:
                self.df[column][begin:end] = np.nan
            self.bad_labels_dict[column] = bad_labels[~to_change_index]

    def split_between(self):
        return self.intervals_to_remove.split_between(self.df)

    def full_concatenated_df(self):
        return pd.concat(self.split_between(), axis=0)

    @lazyprop
    def intervals_to_remove(self):
        interval_to_remove= Interval([])
        for key, intervals_bad_level in self.bad_labels_dict.items():
            if(key not in self.ignore_keys):
                interval_to_remove.update(intervals_bad_level)
        return interval_to_remove