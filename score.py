from datetime import timedelta

import numpy as np
import pandas as pd
from scipy.signal import argrelextrema


class ScoreAnalysis:
    """
    There is, for each anomaly type, a contiguous dataframe of scores for this anomaly, for the whole series.
    Since we are only looking for the anomalies, we extract the extrema of this dataframe.
    The timestamps corresponding to these extrema are the locations of the anomalies.
    The pipeline is as follow:
    - First we filter the score to keep only the one above a certain anomaly-specific threshold.
    - Then we extract the local maxima, since they correspond to isolated, high value scores.
    - Finally we remove the anomalies if there are too close given a certain time threshold `drop_time`.
    """
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
        """
        The pipeline is explained above.
        :param df: A series or dataframe containing one column of scores only
        :return:
        """
        if (type(df) is pd.Series):
            df = df.to_frame("score")
        elif (type(df) is pd.DataFrame):
            df.columns = ["score"]
        df = self._filter(df)
        df = self._argrelmax(df)
        df = self._drop_close_extrema(df)  # by = [deb1[0]]
        return df.sort_values(by=["score"])[::-1]
