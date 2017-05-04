#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 08:23:37 2017

@author: edouardm
"""
import numpy as np
from datetime import datetime,timedelta,time
import matplotlib.pyplot as plt
from matplotlib.dates import MonthLocator, YearLocator, DateFormatter
import unittest


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
        if(ind_low == ind_high):
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
        for interval_date in list_of_intervals:
            self.add_interval(interval_date)

    def split_series(self, values_df):
        """
        :param values_df: a pandas Series
        :return: a list of pandas Series stricly comprised between intervals values
        """
        convert = lambda d: d.strftime("%Y-%m-%d %H:%M:%S")
        return [values_df[convert(self.intervals[p-1,1]):convert(self.intervals[p,0])][1:-1] for p in range(1,len(self.intervals))]

    def split_accordingly(self, values_df):
        convert = lambda d: d.strftime("%Y-%m-%d %H:%M:%S")
        return [values_df[convert(interval[0]):convert(interval[1])] for interval in self.intervals]

    def valid_ante_interval(self, intervals_end,hours = 1):
        """
        :param intervals_end: a numpy column of intervals starts
        :return: valid intervals (no intersection with self.intervals)
        """
        intervals = np.concatenate((intervals_end - timedelta(hours=hours),intervals_end),axis = 1)
        valid_intervals_index = np.array([np.sum(interval[0] > self.intervals[:, 1]) == np.sum(interval[1] > self.intervals[:, 0]) for interval in intervals])
        if hours == 0:
            index_start = np.array([np.sum(end > self.intervals[:, 1]) for end in intervals_end],dtype=np.intp) - 1
            to_change = index_start>=0
            not_to_change = np.logical_not(to_change)
            index_start = index_start[to_change]
            intervals[to_change,0] = self.intervals[index_start,1]
            intervals[not_to_change,0] = intervals[not_to_change,1] - timedelta(hours = 1)
        return intervals[valid_intervals_index]

    def plot(self, axe=None, y_pos=1):
        month = MonthLocator(bymonth=range(4, 11), interval=2)
        month_f = DateFormatter('%m')
        year = YearLocator()
        year_f = DateFormatter('%Y')
        if axe is None:
            fig, axe = plt.subplots()
        for p in self.intervals:
            axe.hlines(y_pos, p[0], p[1], lw=4, color="b")
        axe.get_yaxis().set_ticks([])
        axe.get_xaxis().set_ticks([])
        axe.xaxis.set_minor_locator(month)
        axe.xaxis.set_minor_formatter(month_f)
        axe.xaxis.set_major_locator(year)
        axe.xaxis.set_major_formatter(year_f)
        plt.setp(axe.xaxis.get_minorticklabels(), rotation=45)
        plt.setp(axe.xaxis.get_majorticklabels(), rotation=45)  # fontsize


class TestPeriod(unittest.TestCase):

    def test_update(self):
        interval_1 = [datetime(2014, 4, 1), datetime(2014, 8, 1)]
        interval_2 = [datetime(2015, 4, 1), datetime(2015, 8, 1)]
        interval_3 = [datetime(2016, 4, 1), datetime(2016, 8, 1)]
        intervals = np.array([interval_1, interval_2, interval_3])
        interval = Interval(intervals)
        self.assertEqual(len(interval.intervals), 3)
        fig, ax = plt.subplots()
        interval.plot(ax, 1)

        interval.add_interval([datetime(2014, 5, 1), datetime(2014, 7, 1)])
        self.assertEqual(len(interval.intervals), 3)
        interval.add_interval([datetime(2014, 9, 1), datetime(2014, 11, 1)])
        self.assertEqual(len(interval.intervals), 4)
        interval.plot(ax, 2)

        interval.add_interval([datetime(2014, 5, 1), datetime(2014, 12, 1)])
        self.assertEqual(len(interval.intervals), 3)
        interval.add_interval([datetime(2014, 3, 1), datetime(2015, 1, 1)])
        self.assertEqual(len(interval.intervals), 3)
        interval.plot(ax, 3)

        interval.add_interval([datetime(2013, 4, 1), datetime(2013, 8, 1)])
        self.assertEqual(len(interval.intervals), 4)
        interval.add_interval([datetime(2017, 4, 1), datetime(2017, 8, 1)])
        self.assertEqual(len(interval.intervals), 5)
        interval.plot(ax, 4)
        ax.set_ylim((0, 5))

    def test_valid_ante_interval(self):
        start_day = datetime(2014, 4, 1)
        interval_1 = [datetime.combine(start_day, time(hour=3)), datetime.combine(start_day, time(hour=4))]
        interval_2 = [datetime.combine(start_day, time(hour=6)), datetime.combine(start_day, time(hour=8))]
        intervals = np.array([interval_1, interval_2])
        interval = Interval(intervals)
        intervals_start = [
            datetime.combine(start_day, time(hour=2)),
            datetime.combine(start_day, time(hour=4, minute=30)),
            datetime.combine(start_day, time(hour=5, minute=10)),
            datetime.combine(start_day, time(hour=6, minute=10)),
            datetime.combine(start_day, time(hour=7, minute=50))]
        intervals_start = np.array(intervals_start).reshape(-1,1)
        ante_interval = interval.valid_ante_interval(intervals_start)
        self.assertEqual(len(ante_interval), 2)
        ante_interval = interval.valid_ante_interval(intervals_start,hours=0)
        self.assertEqual(len(ante_interval), 3)


if __name__ == '__main__':
    unittest.main()