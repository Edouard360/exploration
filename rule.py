from abc import abstractmethod
from interval import Interval
import numpy as np


class Rule:
    def __init__(self, threshold, stride_factor):
        self.threshold = threshold
        self.stride_factor = stride_factor

    @abstractmethod
    def score(self, df):
        pass

    @abstractmethod
    def width(self, scale):
        pass

    def stride(self, scale):
        return self.width(scale) * self.stride_factor

    @abstractmethod
    def get_intervals(self, intervals, scale):
        pass


from sklearn.linear_model import LinearRegression


class IncreasingTrend(Rule):
    def __init__(self,
                 threshold=2,
                 stride_factor=0.4,
                 rolling_size=30):
        super(IncreasingTrend, self).__init__(
            threshold=threshold,
            stride_factor=stride_factor)
        self.rolling_size = rolling_size
        self.reg = LinearRegression()

    def score(self, df):
        def score_df(df):
            self.reg.fit(np.arange(len(df)).reshape(len(df), -1), df)
            return self.reg.coef_[0]

        return df.rolling(self.rolling_size).apply(score_df)

    def width(self, scale):
        return scale.length * self.rolling_size

    def get_intervals(self, intervals, scale):
        intervals = np.array(intervals).reshape(-1, 1)
        return Interval(intervals).before(self.width(scale))
