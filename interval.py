#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 08:23:37 2017

@author: edouardm
"""
import numpy as np
import matplotlib.pyplot as plt


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

    def split_between(self, df):
        intervals = []
        first = self.intervals[0, 0]
        last = self.intervals[-1, -1]
        intervals += [df[:first].iloc[:-1]]
        for begin, end in self.intervals.reshape(-1)[1:-1].reshape(-1, 2):
            intervals += [df[begin:end].iloc[1:-1]]
        intervals += [df[last:].iloc[1:]]
        return intervals

    def split_accordingly(self, df):
        intervals = []
        for begin, end in self.intervals:
            intervals += [df[begin:end]]
        return intervals

    def plot(self, axe=None, y_pos=1, **kargs):
        if axe is None:
            fig, axe = plt.subplots()
        for p in self.intervals:
            axe.hlines(y_pos, p[0], p[1], **kargs)
