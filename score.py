from scipy.signal import argrelextrema
from datetime import timedelta
import pandas as pd
import numpy as np
from constants import *


class ScoreAnalysis:
    def __init__(self, threshold, drop_time=timedelta(days=30)):
        self.drop_time = drop_time
        self.threshold = threshold

    def _filter(self, df):
        df = df[(~df.isnull()).any(axis=1)]
        return df[(df > self.threshold).any(axis=1)]

    def _argrelmax(self, df):
        df = df[(~df.isnull()).any(axis=1)]
        return df.iloc[argrelextrema(df.values, np.greater)[0]]

    def _drop_close_extrema(self, df):
        # No nan values theoretically
        if len(df.index) == 0:
            return df
        i_ref = df.index[0]
        to_remove = []
        for i in df.index:
            if (i_ref < i - self.drop_time):
                i_ref = i
            elif ((df.loc[i] < df.loc[i_ref]).any()):
                to_remove += [i]
            elif ((df.loc[i] > df.loc[i_ref]).any()):
                to_remove += [i_ref]
                i_ref = i
        return df.loc[df.index.difference(pd.Index(to_remove))]

    def analyse_and_sort(self, df):
        df = self._filter(df)
        df = self._argrelmax(df)
        df = self._drop_close_extrema(df)  # by = [deb1[0]]
        return df.sort_values(by=[deb1[0]])[::-1]
