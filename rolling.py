#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rolling.py
The series is sometimes oscillating between very few values.
Using a rolling window, we can analyse the diversity of the values.
We might want to remove periods where only two or three values occur.
Pandas built-in `rolling` function was running to slow. (cf. EOF)
@author: edouardm
"""
from tools import sequence_to_period
import numpy as np
import matplotlib.pyplot as plt


class Rolling:
    """
    The Rolling class with usage:
    rolling = Rolling(values_df.values,values_df.index)
    rolling.plot_summary()
    periods = rolling.periods()
    """

    def __init__(self, values, date_index, window_length=100):
        self.date_index = date_index
        self.window_length = window_length
        self.rolling_unique = np.array(
            [len(set(values[max(0, i + 1 - window_length):i + 1])) for i in range(len(values))])

    def periods(self, number_different_values_expected=5, contatenate_periods_threshold=15):
        indices = []
        for ind, value in enumerate(self.rolling_unique):
            if(value < number_different_values_expected):
                indices.append(ind)
        periods = sequence_to_period(
            indices, threshold=contatenate_periods_threshold)
        return periods

    def plot_diversity(self, axe=plt.subplots()[1]):
        axe.plot_date(self.date_index, self.rolling_unique, 'b-')
        axe.set_title(
            "Number of different values in a window ofsize %i" % self.window_length)

    def plot_bar(self, axe=plt.subplots()[1], n_bins=5):
        count = np.array([(np.sum(self.rolling_unique <= i))
                          for i in range(1, n_bins + 1)])
        axe.bar(range(1, n_bins + 1), count, width=0.35, color='r')
        axe.set_title("Number of windows with i or less different values")
        axe.set_xlabel("i")
        axe.set_yscale("log")

    def plot_summary(self, n_bins=5):
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(15, 5))
        self.plot_diversity(axes[0])
        self.plot_bar(axes[1], n_bins=n_bins)
        plt.tight_layout()


"""
Pandas built-in `rolling` function was running to slow.
rolling_win = self.values_df.rolling(window_length)
self.rolling_unique = rolling_win.apply(lambda x: len(np.unique(x)))
"""