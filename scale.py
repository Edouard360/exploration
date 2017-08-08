from datetime import timedelta
from constants import *


class Scale:
    """
    The Scale class.
    For some feature to be computed, the dataframe needs to be resampled, according to a more suitable scale.
    For instance if we care about a 1 month increasing trend, we need only to consider a daily scale, where the value for each day is the median of all the values in that day.
    This enables faster computations for greedy and expensive algorithms such as linear regression.
    """

    def __init__(self, n_units):
        self.n_units = n_units  # Granularity of data.
        self.timedelta = timedelta(minutes=MAX_GRANULARITY * n_units)

    def scale(self, df):
        return df.resample(str(self.n_units * 10) + "T").median()  # 'T' is 'min'


class DayScale(Scale):
    def __init__(self, days=1):
        super(DayScale, self).__init__(n_units=24 * 6 * days)


class HourScale(Scale):
    def __init__(self, hours=1):
        super(HourScale, self).__init__(n_units=6 * hours)


class MinutesScale(Scale):
    def __init__(self, minutes=10):
        assert minutes % MAX_GRANULARITY == 0, "Max granularity is 10 minutes"
        super(MinutesScale, self).__init__(n_units=int(minutes / 10))
