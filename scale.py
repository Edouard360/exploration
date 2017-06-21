from abc import abstractmethod
from datetime import timedelta


class Scale:
    def __init__(self, length):
        self.length = length

    @abstractmethod
    def scale(self, df):
        pass


class DayScale(Scale):
    def __init__(self):
        super(DayScale, self).__init__(length=timedelta(days=1))

    def scale(self, df):
        return df.resample('1D', label='right').median()  # maybe self ?
