#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 08:23:37 2017

@author: edouardm
"""
from datetime import timedelta

import matplotlib.pyplot as plt
import numpy as np

from tools import merge_close_intervals


class Interval:
    """
    The Interval class is to deal with arrays of intervals, and have useful operations:
    add_interval, add_intervals, before, after, is_in, contains_any, select...
    All these methods and their usage are explained below
    """

    def __init__(self, intervals, enlarge_timedelta = None):
        """
        :param intervals: A list of sorted intervals - or a list of sorted timestamps.
        :param enlarge_timedelta: optional parameter, only of you want to instantiate Interval from timestamps. If so, it should be a timedelta object
        Usage:
        Either:
        intervals = np.array([interval_1,interval_2,interval_3])
        interval = Interval(intervals)
        Or:
        timestamps = np.array([timestamp_1,timestamp_2,timestamp_3])
        interval = Interval(timestamps, timedelta(days = 1))
        """
        if enlarge_timedelta is not None:
            self.intervals = np.array(intervals).reshape(-1,1)
            self.intervals = self.enlarge(enlarge_timedelta)
        else:
            self.intervals = np.array(intervals)

    def add_interval(self, interval_date):
        start, end = interval_date[0], interval_date[1]
        ind_low, ind_high = np.sum(start > self.intervals[:, 1]), np.sum(
            end > self.intervals[:, 0])
        if (ind_low == ind_high):
            self.intervals = np.insert(self.intervals, [ind_low], [
                [start, end]], axis=0)
        else:
            new_end = max(end, self.intervals[ind_high - 1, 1])
            new_start = min(start, self.intervals[ind_low, 0])
            self.intervals = np.delete(
                self.intervals, range(ind_low, ind_high), axis=0)
            self.intervals = np.insert(self.intervals, [ind_low], [
                [new_start, new_end]], axis=0)

    def add_intervals(self, list_of_intervals):
        """
        Method to merge the intervals in list_of_intervals to self.intervals.
        :param list_of_intervals: the list of intervals to add. Should be sorted.
        :return:
        intervals = np.array([interval_1,interval_2,interval_3])
        interval = Interval(intervals)
        list_of_intervals = np.array([interval_4,interval_5,interval_6])
        interval.add_intervals(list_of_intervals)
        """
        if (len(self.intervals) == 0):
            self.intervals = np.array(list_of_intervals)
        else:
            for interval_date in list_of_intervals:
                self.add_interval(interval_date)

    def plot(self, axe=None, y_pos=1, **kargs):
        """
        To visualize the intervals.
        :param axe: Optionally if you want the intervals on a specific plot.
        :param y_pos: If you want to plot different sets of intervals.
        :param kargs:
        :return:
        """
        if axe is None:
            fig, axe = plt.subplots()
        for p in self.intervals:
            axe.hlines(y_pos, p[0], p[1], **kargs)

    def intervals_in(self, period):
        """
        Return all the intervals in a given period, or that intersect with that period.
        Useful for plotting the anomalies only for a given window.
        :param period: a tuple of datetime object like (datetime(2014,1,1),datetime(2014,2,1))
        :return:
        """
        start, end = period
        return self.intervals[(self.intervals[:, 1] > start) * (self.intervals[:, 0] < end)]

    def update_conditionally(self, list_of_intervals):
        """
        Method to merge the intervals in list_of_intervals to self.intervals.
        Unlike in the add_intervals method, here, only the intervals that intersect with self.intervals will be merged.
        Useful if you want to merge `low_value_intervals` (which corresponds to cycles of the nuclear reactor) with `missing_value_intervals` (32670), only if they are close.
        :param list_of_intervals: the list of intervals to add conditionally. Should be sorted.
        :return:
        """
        to_update = []
        for i in range(len(list_of_intervals)):
            begin, end = list_of_intervals[i]
            ind_low, ind_high = np.sum(begin > self.intervals[:, 1]), np.sum(
                end > self.intervals[:, 0])
            if (ind_low != ind_high):
                # Then there is crossing
                to_update += [i]
        self.add_intervals(list_of_intervals[np.array(to_update)])

    def split_accordingly(self, df):
        """
        Split a full dataframe `df` into a list of smaller dataframes `split_df`, according to the self.intervals intervals.
        :param df: The dataframe to be split
        :return: a list of dataframes.
        """
        intervals = []
        for begin, end in self.intervals:
            intervals += [df[begin:end]]
        return intervals

    def split_between(self, df, time=timedelta(days=0), strictly=True):
        """
        Split a full dataframe `df` into a list of smaller dataframes `split_df`, according to the intervals between self.intervals.
        :param df: The dataframe to be split
        :param time: A time margin between the intervals
        :param strictly: boolean to indicate if we want the intervals extremity. For instance, to remove the 32670 value, this should be true
        :return: a list of dataframes.
        """
        split_df = Interval(self.between(time)).split_accordingly(df)
        if strictly:
            split_df[0] = split_df[0].iloc[:-1]
            for i in range(1, len(split_df) - 1):
                split_df[i] = split_df[i].iloc[1:-1]
            split_df[-1] = split_df[-1].iloc[1:]
        return split_df

    def between(self, time=timedelta(days=3)):
        """
         Return the intervals between self.intervals.
         :param time: a timedelta object like `timedelta(days=1)`
         :return:
         """
        if (type(time) is not timedelta):
            time = timedelta(days=time)
        intervals = []
        first = self.intervals[0, 0]
        last = self.intervals[-1, -1]
        intervals += [[None, first - time]]
        for begin, end in self.intervals.reshape(-1)[1:-1].reshape(-1, 2):
            begin, end = begin + time, end - time
            if (begin <= end):
                intervals += [[begin, end]]
        intervals += [[last + time, None]]
        return intervals

    def enlarge(self, time):
        """
        Method to enlarge all the intervals by a certain time duration
        :param time: a timedelta object like `timedelta(days=1)`
        :return:
        """
        begin = self.intervals[:, 0].reshape(-1, 1) - time
        end = self.intervals[:, -1].reshape(-1, 1) + time
        return np.concatenate([begin, end], axis=1)

    def before(self, time=timedelta(days=1)):
        """
        Return intervals of width `time` that end at the beginning of each the `self.intervals` intervals.
        Useful if we want to look at the series long before an anomaly. For instance, this was used for looking at increasing variance and autocovariance before the "steps anomaly".
        :param time: a timedelta object like `timedelta(days=1)`
        :return:
        """
        if (type(time) is not timedelta):
            time = timedelta(days=time)
        intervals_begin = self.intervals[:, 0].reshape(-1, 1)  # The end of **valid** intervals !
        intervals = np.concatenate((intervals_begin - time, intervals_begin), axis=1)
        return intervals

    def after(self, time=timedelta(days=1)):
        """
        Return intervals of width `time` that start at the end of each the `self.intervals` intervals.
        Useful if we want to look at the series after an anomaly.
        :param time: a timedelta object like `timedelta(days=1)`
        :return:
        """
        if (type(time) is not timedelta):
            time = timedelta(days=time)
        intervals_end = self.intervals[:, -1].reshape(-1, 1)  # The end of **valid** intervals !
        intervals = np.concatenate((intervals_end, intervals_end + time), axis=1)
        return intervals

    def merge_close_intervals(self, threshold=timedelta(days=1)):
        """
        Method to merge the intervals that are close according to a certain time threshold
        :param threshold: a timedelta object like `timedelta(days=1)`
        :return:
        """
        self.intervals = merge_close_intervals(self.intervals, threshold)

    def filter(self, time):
        """
        Method to filter the intervals according to their duration, if we want to keep only the largest.
        :param time: a timedelta object like `timedelta(days=1)`
        :return:
        """
        self.intervals = self.intervals[(self.intervals[:, 1] - self.intervals[:, 0]) >= time]

    def contains_any(self,timestamps):
        """
        Given certain timestamps, return all the intervals that contain at least one of these timestamps.
        Can be useful for finding the anomaly intervals that intersect with other anomalies.
        :param timestamps: a list of ordered timestamps
        :return: intervals in a numpy array
        """
        indices = []
        for i, timestamp in enumerate(timestamps):
            if (np.sum(timestamp >= self.intervals[:, 0]) == 1 + np.sum(timestamp > self.intervals[:, 1])):
                indices += [np.sum(timestamp >= self.intervals[:, 0])]
        indices = np.unique(indices)
        return self.intervals[indices]

    def is_in(self, timestamps):
        """
        The opposite of contains_any.
        Return the timestamps that are at least existing in one interval.
        Can be useful for finding anomalies within other anomaly intervals.
        :param timestamps: a list of ordered timestamps
        :return: timestamps satisfying the condition
        """
        is_in = []
        for i, timestamp in enumerate(timestamps):
            if (np.sum(timestamp >= self.intervals[:, 0]) == 1 + np.sum(timestamp > self.intervals[:, 1])):
                is_in += [i]
        return timestamps[np.array(is_in)]
