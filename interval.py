#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 08:23:37 2017

@author: edouardm
"""
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta
from tools import merge_close_intervals


class Interval:
    """
    The Interval class with usage:
    intervals = np.array([interval_1,interval_2,interval_3])
    interval = Interval(intervals)
    interval.add_interval([datetime(2014,5,1),datetime(2014,7,1)])
    interval.update(new_intervals)
    """

    def __init__(self, intervals):
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

    def update(self, list_of_intervals):
        if (len(self.intervals) == 0):
            self.intervals = np.array(list_of_intervals)
        else:
            for interval_date in list_of_intervals:
                self.add_interval(interval_date)

    def update_conditionally(self, list_of_intervals):
        to_update = []
        for i in range(len(list_of_intervals)):
            begin, end = list_of_intervals[i]
            ind_low, ind_high = np.sum(begin > self.intervals[:, 1]), np.sum(
                end > self.intervals[:, 0])
            if (ind_low != ind_high):
                # Then there is crossing
                to_update += [i]
        self.update(list_of_intervals[np.array(to_update)])

    def split_between(self, df, time=timedelta(days=0), strictly=True):
        split_df = Interval(self.between(time)).split_accordingly(df)
        if strictly:
            split_df[0] = split_df[0].iloc[:-1]
            for i in range(1, len(split_df) - 1):
                split_df[i] = split_df[i].iloc[1:-1]
            split_df[-1] = split_df[-1].iloc[1:]
        return split_df

    def split_accordingly(self, df):
        intervals = []
        for begin, end in self.intervals:
            intervals += [df[begin:end]]
        return intervals

    def before(self, time=timedelta(days=1)):
        if (type(time) is not timedelta):
            time = timedelta(days=time)
        intervals_begin = self.intervals[:, 0].reshape(-1, 1)  # The end of **valid** intervals !
        intervals = np.concatenate((intervals_begin - time, intervals_begin), axis=1)
        return intervals

    def after(self, time=timedelta(days=1)):
        if (type(time) is not timedelta):
            time = timedelta(days=time)
        intervals_end = self.intervals[:, -1].reshape(-1, 1)  # The end of **valid** intervals !
        intervals = np.concatenate((intervals_end, intervals_end + time), axis=1)
        return intervals

    def between(self, time=timedelta(days=3)):
        # time : the margin
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
        begin = self.intervals[:, 0].reshape(-1, 1) - time
        end = self.intervals[:, -1].reshape(-1, 1) + time
        return np.concatenate([begin, end], axis=1)

    def is_in(self, timestamps):
        is_in = []
        for i, timestamp in enumerate(timestamps):
            if (np.sum(timestamp >= self.intervals[:, 0]) == 1 + np.sum(timestamp > self.intervals[:, 1])):
                is_in += [i]
        return np.array(is_in)

    def merge_close_intervals(self, threshold=timedelta(days=1)):
        self.intervals = merge_close_intervals(self.intervals, threshold)

    def filter(self, time):
        self.intervals = self.intervals[(self.intervals[:, 1] - self.intervals[:, 0]) >= time]

    def plot(self, axe=None, y_pos=1, **kargs):
        if axe is None:
            fig, axe = plt.subplots()
        for p in self.intervals:
            axe.hlines(y_pos, p[0], p[1], **kargs)
