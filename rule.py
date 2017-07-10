from abc import abstractmethod
import numpy as np
from sklearn.linear_model import LinearRegression
from constants import *
import pandas as pd


# from IPython.core.debugger import set_trace

class Feature:
    @abstractmethod
    def score(self, df, columns):
        pass


class RollingFeature(Feature):
    def __init__(self, rolling_size):
        super(RollingFeature, self).__init__()
        self.rolling_size = rolling_size


class Trend(RollingFeature):
    def __init__(self, rolling_size=30):
        super(Trend, self).__init__(rolling_size=rolling_size)
        self.reg = LinearRegression()

    def score(self, df, columns):
        df = df.loc[:, columns]

        def score_df(df):
            self.reg.fit(np.arange(len(df)).reshape(len(df), -1), df)
            return self.reg.coef_[0]

        return df.rolling(self.rolling_size, center=True).apply(score_df)


class Step(RollingFeature):
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
    def __init__(self,
                 first_window=3,
                 second_window=20
                 ):
        self.first_window = first_window
        super(Oscillation, self).__init__(rolling_size=second_window)

    def score(self, df, columns):
        df = df.loc[:, columns]
        return df.rolling(self.first_window, center=True).var().rolling(self.rolling_size, center=True).median()


class Spike(Feature):
    def __init__(self):
        super(Spike, self).__init__()

    def score(self, df, columns):
        df = df.loc[:, columns]
        return df.diff().abs()


class Correlation(RollingFeature):
    def __init__(self, rolling_size=30):
        super(Correlation, self).__init__(rolling_size=rolling_size)

    def score(self, df, columns):
        def corr_np_array(np_array):
            if (np.var(np_array[:, 0]) * np.var(np_array[:, 1]) == 0):
                corrcoef = 1
            else:
                corrcoef = np.corrcoef(np_array[:, 0], np_array[:, 1])[0, 1]
            return corrcoef

        values = df.loc[:, [deb1[0], tmp[0]]].values
        half_window = int(self.rolling_size / 2)
        data = [corr_np_array(values[i - half_window:i + half_window, :]) for i in
                range(half_window, len(df) - half_window)]
        index = df.index[half_window:len(df) - half_window]

        dataframe = pd.DataFrame(index=index, data=np.array(data).reshape(-1, 1), columns=["score"])
        return dataframe
