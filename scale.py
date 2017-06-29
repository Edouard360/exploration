from datetime import timedelta
from interval import Interval
from constants import *

class Scale:
    def __init__(self, n_units):
        self.n_units = n_units # Granularity of data.
        self.timedelta = timedelta(minutes=MAX_GRANULARITY*n_units)

    def scale(self, df):
        return df.resample(str(self.n_units*10)+"T").median() # 'T' is 'min'

    def get_intervals(self, intervals):
        return Interval(intervals).enlarge(self.timedelta)

class DayScale(Scale):
    def __init__(self, days=1):
        super(DayScale, self).__init__(n_units=24*6*days)

class HourScale(Scale):
    def __init__(self, hours=1):
        super(HourScale, self).__init__(n_units=6*hours)

class MinutesScale(Scale):
    def __init__(self, minutes=10):
        assert minutes%MAX_GRANULARITY == 0, "Max granularity is 10 minutes"
        super(MinutesScale, self).__init__(n_units=6*int(minutes/10))

class NoScale(MinutesScale):
    def __init__(self):
        super(NoScale, self).__init__(minutes=10)

    def scale(self, df):
        return df