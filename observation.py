from datetime import timedelta

import numpy as np
import pandas as pd

from constants import *
from interval import Interval
from tools import sequence_to_interval


class Observation:
    """
    Observation is used to:
    1. load the data
    2. fill the missing values
    3. change the `bad` values (32767) if possible, or else remove them
    4. divide the dataframes into the cycles of the nuclear reactor
        -> most of this pipeling is problem specific. It is needed since the data doesn't come as a `clean` multivariate time series.
    Indeed there are missing values, and `bad` values (32767), but also there are periodic gaps in the data (approximately the size of a month), which would impact our analysis if left unchanged.
    We might therefore be interested in removing these periodic gaps from our study.
    This is where `low_regime_intervals` comes in, identifying these periods.
    """
    def __init__(self, path, reactor_site, suffix_list, format="%Y-%m-%dT%H:%M:%S.000Z",
                 hours_backfill=1, verbose=0, ignore_keys=[], remove_on=[deb1[0]]):
        """

        :param path: the path to the folder of the data
        :param reactor_site: the name of the reactor
        :param suffix_list: all the sensors name as a list
        :param format: the default parameter corresponds to the proper encoding format of the dates.
        :param hours_backfill: the threshold for dealing with missing values. For more, read README.md.
        :param verbose:
        :param ignore_keys:
        :param remove_on: the target sensor for missing values. If we considered all the missing values from each sensor,
         and remove all intervals where any of the values are missing, the resulting data would be very sparse.
        """
        self.verboseprint = print if verbose else lambda *a, **k: None
        self.verboseprint("Loading in memory %i observations..." % (int(len(suffix_list)),))
        self.hours_backfill = hours_backfill
        files_name = [reactor_site + "-" + suffix + ".txt" for suffix in suffix_list]
        list_df = [pd.read_csv(path + file_name, sep=";") for file_name in files_name]
        self.ignore_keys = ignore_keys
        self.remove_on = remove_on
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

        self.compute_intervals_to_remove()
        self.compute_full_concatenated_df()
        self.compute_low_regime_intervals()

    def change_isolated_wrong_values(self):
        """
        Some values of the dataframe can be singled out and replaced by the previous one, to approximate the signal.
        -> We change them into nan's in the dataframe so that we can replace them later on
        However there are a lot of successive contiguous `bad` values 32767, and these cannot be interpolated.
        -> We compute the corresponding intervals for these successive problems and store them in a dictionary.
        These intervals represent the large gap of missing values, and if too big, they will be considered to "segment" the multivariate series.
        -> We store them in bad_labels_dict
        From experience however, if we take all the signals "large gaps" and combine them,
        we are left with only 1/5 of the original data, because very often,
        there is missing data for one sensor over a long time and not for the others.
        To avoid doing this for all sensors, we can choose, when instantiating the Observation object, a target class,
        or some target classes, in the `remove_on` field.
        For instance if `remove_on=[deb1[0]]` only the first sensors' "large gaps" will be taken into account for the segmentation of the time series.
        """
        self.verboseprint("Changing isolated wrong values...")
        for column in self.df:
            bad_labels = self.df.index[((self.df[column] == MAX_VALUE) | (self.df[column] == 0))]  ## >= THRESHOLD
            bad_labels = sequence_to_interval(bad_labels, timedelta(minutes=10))  # Stricly consecutive wrong values
            to_change_index = (bad_labels[:, 1] - bad_labels[:, 0]) <= timedelta(hours=self.hours_backfill)
            for begin, end in bad_labels[to_change_index]:
                self.df[column][begin:end] = np.nan
            if column in self.remove_on:
                self.bad_labels_dict[column] = bad_labels[~to_change_index]
            else:
                for begin, end in bad_labels[~to_change_index]:
                    self.df[column][begin:end] = np.nan

    def compute_intervals_to_remove(self):
        self.intervals_to_remove = Interval([])
        for key, intervals_bad_level in self.bad_labels_dict.items():
            if (key not in self.ignore_keys):
                self.intervals_to_remove.add_intervals(intervals_bad_level)

    def compute_low_regime_intervals(self):
        '''
        This function extract the cycles of the "low regime" of the pump as intervals.
        See paragraph cycle identification in the README.md for the explanation of the pipeline.
        '''
        # time_precision = '10m'#'6H'
        low_regime_merge_time = timedelta(days=15)  # In days: The merging time for low regime
        margin_intervals_to_remove = timedelta(
            minutes=30)  # Initially 10 # In days: Be careful, a high time_precision can make this wrong !
        filter_spike = timedelta(hours=1)  # In days: below that, the interval is considered as a spike !

        # subsample = self.full_concatenated_df[deb1[0]].resample(time_precision, label='right').min()
        subsample = self.full_concatenated_df[deb1[0]]
        self.low_regime_intervals = sequence_to_interval(subsample.index[(subsample < 200)],
                                                         low_regime_merge_time)
        self.low_regime_intervals = Interval(self.low_regime_intervals)
        self.low_regime_intervals.update_conditionally(
            self.intervals_to_remove.enlarge(margin_intervals_to_remove))
        self.low_regime_intervals.filter(filter_spike)
        self.low_regime_intervals.merge_close_intervals()

    def compute_full_concatenated_df(self):
        self.full_concatenated_df = pd.concat(self.intervals_to_remove.split_between(self.df), axis=0)
