import pandas as pd
import numpy as np
from datetime import timedelta, datetime
from tools import low_pass_filter, bandstop_filter, sequence_to_interval, lazyprop
from rolling import Rolling
from interval import Interval
import dateutil.parser


class Observation:
    def __init__(self, path, reactor_site, suffix_list, format="%Y-%m-%dT%H:%M:%S.000Z", ncol=2, hours_bad_level=15,
                 hours_interval=0, min_hours=5, hours_backfill = 1, verbose=0):
        self.verboseprint = print if verbose else lambda *a, **k: None
        self.verboseprint("Loading in memory %i observations..." % (int(len(suffix_list)),))
        self.hours_backfill = hours_backfill
        # 2013-2015 : format : "%d-%b-%y %H:%M:%S.0"
        files_name = [reactor_site + "-" + suffix + ".txt" for suffix in suffix_list]
        list_df = [pd.read_csv(path + file_name, sep=";") for file_name in files_name]
        self.ncol = ncol
        for df, tag in zip(list_df, suffix_list):
            if self.ncol == 4:
                df.columns = ["date", "value_" + tag, "quality_" + tag, "level_" + tag]
            else:
                df.columns = ["date", tag]
            df.drop_duplicates(subset="date", inplace=True)
            df['date'] = pd.to_datetime(df['date'], format=format)
            df.set_index('date', inplace=True)
        self.verboseprint("Concatenation...")
        self.df = pd.concat(list_df, axis=1)
        self.change_isolated_wrong_values()
        self.verboseprint("Forward Filling...")
        self.df.fillna(method='ffill', inplace=True)
        self.verboseprint("Backward Filling...")
        self.df.fillna(method='bfill', inplace=True)
        self.df.reactor_site = reactor_site
        if self.ncol == 4:
            self.df = df.ix[:, ["value" in column for column in df.columns]]
            self.level_df = df.ix[:, ["level" in column for column in df.columns]]
        self.hours_bad_level = hours_bad_level
        self.hours_interval = hours_interval  # The duration of each interval ! 0 if the max value possible is desired
        self.hours_low_sampling = 1
        self.min_hours = min_hours  # The min length to split the dataframe

    def change_isolated_wrong_values(self):
        for column in self.df:
            bad_timestamps = self.df.index[((self.df[column] == self.df[column].max()) | (self.df[column] == 0))]
            bad_timestamps = sequence_to_interval(bad_timestamps, timedelta(minutes=10)) # Stricly consecutive wrong values
            to_change_index = (bad_timestamps[:,1] - bad_timestamps[:,0]) <= timedelta(hours=self.hours_backfill)
            for begin, end in bad_timestamps[to_change_index]:
                self.df[column][begin:end] = np.nan

    def split_valid_intervals_df(self):
        return self.longest_valid_intervals.split_accordingly(self.df)

    def split_healthy_unhealthy(self, healthy=(0.1, 0.3), unhealthy=(0.7, 0.9)):
        healthy_intervals, unhealthy_intervals = self.longest_valid_intervals.separate_intervals(healthy, unhealthy)
        healthy_ts = Interval(healthy_intervals).split_accordingly(self.df)
        unhealthy_ts = Interval(unhealthy_intervals).split_accordingly(self.df)
        return healthy_ts, unhealthy_ts

    def get_valid_interval(self):
        valid_intervals_to_explore = self.intervals_to_remove.valid_ante_interval(self.start_bad_level,
                                                                                  hours=self.hours_interval,
                                                                                  min_hours=self.min_hours)
        return Interval(valid_intervals_to_explore)

    def get_interval_id(self, date):
        if (type(date) is not datetime):
            if (type(date) is str):
                date = dateutil.parser.parse(date)
        return np.sum(self.longest_valid_intervals.intervals[:, 0] < date)

    @lazyprop
    def full_concatenated_df(self):
        return pd.concat(self.split_valid_intervals_df(), axis=0)

    @lazyprop
    def longest_valid_intervals(self):
        return self.get_valid_interval()

    @lazyprop
    def intervals_to_remove(self):
        interval_to_remove = Interval(self.intervals_low_diversity)
        interval_to_remove.update(self.intervals_bad_level)
        interval_to_remove.update(self.intervals_low_sample)
        return interval_to_remove

    @lazyprop
    def intervals_low_sample(self):
        self.verboseprint("Analysing intervals with low sampling rate")
        time_btw = self.df.index[1:] - self.df.index[:-1]
        ind_tmp = time_btw > timedelta(hours=self.hours_low_sampling)
        start_ind = np.concatenate((ind_tmp, [False]))
        end_ind = np.concatenate(([False], ind_tmp))
        return np.array(list(zip(self.df.index[start_ind], self.df.index[end_ind])))

    @lazyprop
    def intervals_low_diversity(self):
        self.verboseprint("Analysing intervals with low diversity")
        rolling = Rolling(self.df.iloc[:, 0].values.ravel(), self.df.index)
        return rolling.intervals()

    @lazyprop
    def intervals_bad_level(self):
        self.verboseprint("Analysing intervals with bad level")
        bad_timestamp_value = self.df.index[((self.df == self.df.max()[0]) | (self.df == 0)).any(axis=1)]
        if self.ncol == 4:
            is_bad = np.vectorize(lambda label: label in ["Bad", "Bad/M"])
            bad_timestamp_label = self.level_df.index[(is_bad(self.level_df)).any(axis=1)]
            bad_timestamp = sorted(bad_timestamp_label.tolist() + bad_timestamp_value.tolist())
        else:
            bad_timestamp = sorted(bad_timestamp_value.tolist())
        bad_intervals = sequence_to_interval(bad_timestamp, timedelta(hours=self.hours_bad_level))
        return bad_intervals

    @lazyprop
    def start_bad_level(self):
        return self.intervals_bad_level[:, 0].reshape(-1, 1)

    @lazyprop
    def end_bad_level(self):
        return self.intervals_bad_level[:, 1].reshape(-1, 1)

    def smooth(self, cutoff=0.1):
        self.df = self.df.assign(
            smooth=low_pass_filter(self.df.ix[:, 0].values.ravel(), cutoff=cutoff))

    def smooth_stop(self, cutoff=[0.1, 0.9]):
        self.df = self.df.assign(
            smooth_stop=bandstop_filter(self.df.ix[:, 0].values.ravel(), cutoff=cutoff))
