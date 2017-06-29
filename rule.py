from abc import abstractmethod
import numpy as np
from scale import Scale
from sklearn.linear_model import LinearRegression
from score import ScoreAnalysis
from datetime import timedelta
from tools import combine
import pandas as pd
from constants import *

class Rule:
    def __init__(self,types, power_scale = 1):
        self.features = []
        self.scales = []
        self.selected_scores = {}
        self.anomaly_df = None
        self.power_scale = power_scale

        self.types = types

    def process(self, obs, scales):
        for scale in scales:
            scale = self.get_subsample_scale(scale)
            df = scale.scale(obs.full_concatenated_df[deb1[0]].to_frame(deb1[0])) ## TODO
            list_df = obs.low_regime_intervals.split_between(df, time=timedelta(days=3))
            list_score_df = []
            for df in list_df:
                list_score_df += [self.score(df)]
            score_df = pd.concat(list_score_df, axis=0)
            self.features += [score_df]
            self.scales += [scale]

    def compute_anomaly_df(self):
        scores = []
        for type, (scoring, threshold, stride) in self.types.items():
            self.selected_scores[type] = [ScoreAnalysis(threshold,stride*scale.timedelta).analyse_and_sort(scoring(score)) for score,scale in zip(self.features,self.scales)]
            widths = self.anomalies_length()
            strides = len(self.scales)*[stride]
            multiply = [pow(self.power_scale,i) for i in range(len(self.scales))]
            score_combined = combine(self.selected_scores[type],widths,strides,multiply)
            score_combined["type"] = type
            scores += [score_combined]
        self.anomaly_df = pd.concat(scores, axis=0).sort_index()

    def get_anomaly_df(self,obs,scales):
        self.process(obs,scales)
        self.compute_anomaly_df()
        return self.anomaly_df

    @abstractmethod
    def anomalies_length(self):
        pass

    @abstractmethod
    def score(self, df):
        pass

    @abstractmethod
    def get_subsample_scale(self, scale_of_anomaly):
        pass


class RollingRule(Rule):
    def __init__(self, min_rolling_size, types, power_scale =1.5):
        super(RollingRule, self).__init__(types = types)
        self.min_rolling_size = min_rolling_size
        self.power_scale = power_scale

    def get_subsample_scale(self, scale_of_anomaly):
        n_units_subsample = int(scale_of_anomaly.n_units / self.min_rolling_size)
        self.rolling_size = int(scale_of_anomaly.n_units / n_units_subsample)
        return Scale(n_units=n_units_subsample)

    def anomalies_length(self):
        return [self.rolling_size * scale.timedelta for scale in self.scales]


class Trend(RollingRule):

    def __init__(self, min_rolling_size=30, threshold = 2, stride = 1, power_scale=1.5):
        types = {
            TREND_UP: (lambda score: score, threshold, stride),
            TREND_DOWN: (lambda score: -score, threshold, stride),
        }
        super(Trend, self).__init__(min_rolling_size=min_rolling_size,types = types)
        self.reg = LinearRegression()
        self.power_scale = power_scale

    def score(self, df):
        def score_df(df):
            self.reg.fit(np.arange(len(df)).reshape(len(df), -1), df)
            return self.reg.coef_[0]

        return df.rolling(self.rolling_size).apply(score_df)

class Step(RollingRule):
    def __init__(self, min_rolling_size=10,threshold=50,stride=0.5):
        types = {
            STEP: (lambda score: score, threshold, stride),
        }
        super(Step, self).__init__(min_rolling_size=min_rolling_size, types = types)

    def score(self, df):
        window_size = int(self.rolling_size / 2)

        def score_df(df):
            self.reg.fit(np.arange(len(df)).reshape(len(df), -1), df)
            return self.reg.coef_[0]


        mean_shift = lambda df: df[1:].mean()
        left = df.rolling(window_size).apply(mean_shift)
        right = df[::-1].rolling(window_size).apply(mean_shift)[::-1]
        score = (right - left).abs()
        return score.isnull()


class Oscillation(RollingRule):
    def __init__(self,
                 first_window=3,
                 second_window=20,
                 threshold=300,
                 stride = 1
                 ):
        types = {
            OSCILLATION: (lambda score: score, threshold, stride),
        }
        self.first_window = first_window
        super(Oscillation, self).__init__(min_rolling_size=second_window,types = types)

    def score(self, df):
        return df.rolling(self.first_window, center=True).var().rolling(self.rolling_size, center=True).median()

class Spike(Rule):
    def __init__(self,threshold=100,stride=20):
        types = {
            SPIKE: (lambda score: score, threshold, stride),
        }
        super(Spike, self).__init__(types = types)

    def score(self, df):
        return df.diff().abs()

    def get_subsample_scale(self, scale_of_anomaly):
        return scale_of_anomaly

    def anomalies_length(self):
        return [scale.timedelta for scale in self.scales]