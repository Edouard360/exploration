from abc import abstractmethod

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from constants import *


class Feature:
    """
    Abstract class that should be inherited to add new features.
    The features are independently computed, but can be combined later on.
    """

    @abstractmethod
    def score(self, df, columns):
        """
        :param df: A contiguous dataframe (no missing values), indexed with timestamps
        :param columns: The column on which we extract the feature
        :return:
        """
        pass


class Spike(Feature):
    """
    Spike is the simplest class inheriting Feature.
    It simply computes the absolute value of first order differenciation.
    """

    def score(self, df, columns):
        df = df.loc[:, columns]
        return df.diff().abs()


class RollingFeature(Feature):
    """
    Abstract class for features with rolling windows.
    """

    def __init__(self, rolling_size):
        super(RollingFeature, self).__init__()
        self.rolling_size = rolling_size


class Trend(RollingFeature):
    """
    Trend inherits RollingFeature, and compute, using linear regression, the slope of the time series for consecutive sliding windows
    """

    def __init__(self, rolling_size=30):
        super(Trend, self).__init__(rolling_size=rolling_size)
        self.reg = LinearRegression()

    def score(self, df, columns):
        df = df.loc[:, columns]

        def score_df(df):
            self.reg.fit(np.arange(len(df)).reshape(len(df), -1), df)
            return self.reg.coef_[0]  # The slope coefficient

        return df.rolling(self.rolling_size, center=True).apply(score_df)


class Step(RollingFeature):
    """
    Step inherits RollingFeature, and compute, for consecutive sliding windows, the difference between the median taken from both sides of the series (right and left).
    Median is chosen instead of mean, to damp the effect of outliers.
    """

    def __init__(self, rolling_size=10):
        super(Step, self).__init__(rolling_size=rolling_size)

    def score(self, df, columns):
        df = df.loc[:, columns]
        window_size = int(self.rolling_size / 2)
        mean_shift = lambda df: df[1:].mean()
        left = df.rolling(window_size).apply(mean_shift)
        right = df[::-1].rolling(window_size).apply(mean_shift)[::-1]
        return right - left


class Oscillation(RollingFeature):
    """
    Oscillation inherits RollingFeature, and compute, for consecutive sliding windows, the median of the variance of smaller windows.
    The first_window parameter represents the length of one oscillation, whereas the second_window parameter represents the length of the whole oscillation pattern
    """

    def __init__(self,
                 first_window=3,
                 second_window=20
                 ):
        self.first_window = first_window
        super(Oscillation, self).__init__(rolling_size=second_window)

    def score(self, df, columns):
        df = df.loc[:, columns]
        return df.rolling(self.first_window, center=True).var().rolling(self.rolling_size, center=True).median()


class Correlation(RollingFeature):
    """
    Correlation inherits RollingFeature, and computes, for consecutive sliding windows, the correlation between two given parameters.
    Temperature and Flow (Debit) have been chosen arbitrarily here, but can be modified.
    """

    def __init__(self, rolling_size=30):
        super(Correlation, self).__init__(rolling_size=rolling_size)

    def score(self, df, columns):
        def corr_np_array(np_array):
            if (np.var(np_array[:, 0]) * np.var(np_array[:, 1]) == 0):
                corrcoef = 1
            else:
                corrcoef = np.corrcoef(np_array[:, 0], np_array[:, 1])[0, 1]
            return corrcoef

        values = df.loc[:, [deb1[0], tmp[0]]].values  # Temperature and Flow (Debit).
        half_window = int(self.rolling_size / 2)
        data = [corr_np_array(values[i - half_window:i + half_window, :]) for i in
                range(half_window, len(df) - half_window)]
        index = df.index[half_window:len(df) - half_window]

        dataframe = pd.DataFrame(index=index, data=np.array(data).reshape(-1, 1), columns=["score"])
        return dataframe


class MinCorrelationDeb(RollingFeature):
    """
    Experimental:
    The minimum correlation between all the flow (deb) signals can be a good feature to find anomalies.
    """

    def __init__(self, rolling_size=30):
        super(MinCorrelationDeb, self).__init__(rolling_size=rolling_size)

    def score(self, df, columns):
        values = df[deb1].values
        half_window = int(self.rolling_size / 2)
        index = df.index[half_window:len(df) - half_window]
        data = []
        for t in range(half_window, len(df) - half_window):
            if (np.var(values[t - half_window:t + half_window], axis=0).min() == 0):
                data += [0]
            else:
                data += [np.corrcoef(values[t - half_window:t + half_window].T).min()]

        dataframe = pd.DataFrame(index=index, data=np.array(data).reshape(-1, 1), columns=["score"])
        return dataframe
