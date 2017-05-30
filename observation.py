import pandas as pd
import numpy as np
from datetime import timedelta
from tools import low_pass_filter, bandstop_filter, sequence_to_interval, lazyprop
from insight_tools import plot
from rolling import Rolling
from interval import Interval

class Observation:
    def __init__(self, path, files_name, files_tag, format="%d-%b-%y %H:%M:%S.0", ncol=4):
        print("Loading in memory %i observations..." % (int(len(files_name))))
        list_df = [pd.read_csv(path + file_name, sep=";") for file_name in files_name]
        self.ncol = ncol
        for df, tag in zip(list_df, files_tag):
            if self.ncol == 4:
                df.columns = ["date", "value_" + tag, "quality_" + tag, "level_" + tag]
            else:
                df.columns = ["date", "value_" + tag]
            df.drop_duplicates(subset="date", inplace=True)
            df['date'] = pd.to_datetime(df['date'], format=format)
            df.set_index('date', inplace=True)
        full_df = pd.concat(list_df, axis=1)
        full_df.fillna(method='ffill', inplace=True)
        full_df.head().fillna(method='bfill', inplace=True)
        self.full_df = full_df
        self.values_df = full_df.ix[:, ["value" in column for column in full_df.columns]]
        self.level_df = full_df.ix[:, ["level" in column for column in full_df.columns]]

    def split_valid_intervals_df(self, hours=50):
        return self.get_valid_interval(hours=hours).split_accordingly(self.values_df)

    def split_healthy_unhealthy(self,healthy=(0.1, 0.3),unhealthy=(0.7, 0.9)):
        healthy_intervals, unhealthy_intervals = self.longest_valid_intervals.separate_intervals(healthy,unhealthy)
        healthy_ts = Interval(healthy_intervals).split_accordingly(self.values_df)
        unhealthy_ts = Interval(unhealthy_intervals).split_accordingly(self.values_df)
        return healthy_ts, unhealthy_ts

    def get_valid_interval(self, hours=50):
        valid_intervals_to_explore = self.intervals_to_remove.valid_ante_interval(self.start_bad_level, hours=hours)
        return Interval(valid_intervals_to_explore)

    @lazyprop
    def longest_valid_intervals(self):
        return self.get_valid_interval(hours=0)

    @lazyprop
    def intervals_to_remove(self):
        interval_to_remove = Interval(self.intervals_low_diversity)
        interval_to_remove.update(self.intervals_bad_level)
        interval_to_remove.update(self.intervals_low_sample)
        return interval_to_remove

    @lazyprop
    def intervals_low_sample(self, hours=1):
        print("Analysing intervals with low sampling rate")
        time_btw = self.values_df.index[1:] - self.values_df.index[:-1]
        ind_tmp = time_btw > timedelta(hours=hours)
        start_ind = np.concatenate((ind_tmp, [False]))
        end_ind = np.concatenate(([False], ind_tmp))
        return np.array(list(zip(self.values_df.index[start_ind], self.values_df.index[end_ind])))

    @lazyprop
    def intervals_low_diversity(self):
        print("Analysing intervals with low diversity")
        rolling = Rolling(self.values_df.ix[:, 0].values.ravel(), self.values_df.index)
        return rolling.intervals()

    @lazyprop
    def intervals_bad_level(self):
        print("Analysing intervals with bad level")
        bad_timestamp_value = self.values_df.index[(self.values_df == self.values_df.max()[0]).any(axis=1)]
        if self.ncol == 4:
            is_bad = np.vectorize(lambda label: label in ["Bad", "Bad/M"])
            bad_timestamp_label = self.level_df.index[(is_bad(self.level_df)).any(axis=1)]
            bad_timestamp = sorted(bad_timestamp_label.tolist() + bad_timestamp_value.tolist())
        else:
            bad_timestamp = sorted(bad_timestamp_value.tolist())
        bad_intervals = sequence_to_interval(bad_timestamp, timedelta(hours=15))
        return bad_intervals

    @lazyprop
    def start_bad_level(self):
        return self.intervals_bad_level[:, 0].reshape(-1, 1)

    @lazyprop
    def end_bad_level(self):
        return self.intervals_bad_level[:, 1].reshape(-1, 1)

    def smooth(self, cutoff=0.1):
        self.values_df = self.values_df.assign(
            smooth=low_pass_filter(self.values_df.ix[:, 0].values.ravel(), cutoff=cutoff))

    def smooth_stop(self, cutoff=[0.1, 0.9]):
        self.values_df = self.values_df.assign(
            smooth_stop=bandstop_filter(self.values_df.ix[:, 0].values.ravel(), cutoff=cutoff))

    def plot(self, xlim=None, auto_set_y=False, **kargs):
        plot(self.full_df, xlim, auto_set_y, **kargs)
