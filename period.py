#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 08:23:37 2017

@author: edouardm
"""
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import MonthLocator, YearLocator, DateFormatter
import unittest


class Period:
    """
    The Period class with usage:
    periods = np.array([period_1,period_2,period_3])
    period = Period(periods)
    period.add_period([datetime(2014,5,1),datetime(2014,7,1)])
    period.update(new_periods)
    """

    def __init__(self, periods):
        self.periods = periods

    def add_period(self, period_date):
        start, end = period_date[0], period_date[1]
        ind_low, ind_high = np.sum(start > self.periods[:, 1]), np.sum(
            end > self.periods[:, 0])
        if(ind_low == ind_high):
            self.periods = np.insert(self.periods, [ind_low], [
                                     [start, end]], axis=0)
        else:
            new_end = max(end, self.periods[ind_high - 1, 1])
            new_start = min(start, self.periods[ind_low, 0])
            self.periods = np.delete(
                self.periods, range(ind_low, ind_high), axis=0)
            self.periods = np.insert(self.periods, [ind_low], [
                                     [new_start, new_end]], axis=0)

    def update(self, list_of_periods):
        for period_date in list_of_periods:
            self.add_period(period_date)

    def plot(self, axe=None, y_pos=1):
        month = MonthLocator(bymonth=range(4, 11), interval=2)
        month_f = DateFormatter('%m')
        year = YearLocator()
        year_f = DateFormatter('%Y')
        if axe is None:
            fig, axe = plt.subplots()
        for p in self.periods:
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

    def test(self):
        period_1 = [datetime(2014, 4, 1), datetime(2014, 8, 1)]
        period_2 = [datetime(2015, 4, 1), datetime(2015, 8, 1)]
        period_3 = [datetime(2016, 4, 1), datetime(2016, 8, 1)]
        periods = np.array([period_1, period_2, period_3])
        period = Period(periods)
        self.assertEqual(len(period.periods), 3)
        fig, ax = plt.subplots()
        period.plot(ax, 1)

        period.add_period([datetime(2014, 5, 1), datetime(2014, 7, 1)])
        self.assertEqual(len(period.periods), 3)
        period.add_period([datetime(2014, 9, 1), datetime(2014, 11, 1)])
        self.assertEqual(len(period.periods), 4)
        period.plot(ax, 2)

        period.add_period([datetime(2014, 5, 1), datetime(2014, 12, 1)])
        self.assertEqual(len(period.periods), 3)
        period.add_period([datetime(2014, 3, 1), datetime(2015, 1, 1)])
        self.assertEqual(len(period.periods), 3)
        period.plot(ax, 3)

        period.add_period([datetime(2013, 4, 1), datetime(2013, 8, 1)])
        self.assertEqual(len(period.periods), 4)
        period.add_period([datetime(2017, 4, 1), datetime(2017, 8, 1)])
        self.assertEqual(len(period.periods), 5)
        period.plot(ax, 4)
        ax.set_ylim((0, 5))


if __name__ == '__main__':
    unittest.main()