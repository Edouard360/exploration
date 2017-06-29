import pandas as pd
import numpy as np

from rule import Step
from scale import DayScale, HourScale
from score import ScoreAnalysis
from datetime import timedelta
from interval import Interval
import matplotlib.pyplot as plt

from constants import *

class Interaction:
    def __init__(self, df, intervals,split_time):
        self.rule_dict = {}
        self.df = df
        self.intervals = intervals
        self.split_time = split_time

    def add_rule(self, name, rule, scale):
        sample_df = scale.scale(self.df)
        list_df = self.intervals.split_between(sample_df, time=timedelta(days=self.split_time))
        list_scores_df = []
        for df in list_df:
            list_scores_df += [rule.score(df)]

        scores_df = pd.concat(list_scores_df, axis=0)
        scores_df = scores_df[deb1[0]].to_frame(deb1[0])
        selected_scores = ScoreAnalysis(rule.threshold, drop_time=rule.stride(scale)).analyse_and_sort(scores_df)

        self.rule_dict[name] = {
            "selected_scores": selected_scores,
            "order": len(self.rule_dict),
            "sample_df": sample_df,
            "scores_df": scores_df,
            "scale": scale,
            "rule": rule
        }

    def visualize_rule(self, name, scale=None, interval= (None,None)):
        # interval is a begin end tuple
        fig, axes = plt.subplots(2, 1, sharex=True, figsize=(12, 10))
        rule = self.rule_dict[name]

        begin, end = interval
        if(scale is not None):
            df = scale.scale(self.df)[begin:end]
        else:
            df = rule["scale"].scale(self.df)[begin:end]

        df.plot(ax=axes[0])
        if(scale is not None):
            scores, scaled_scores = scale.scale_scores(rule["scores_df"],rule["selected_scores"])
        else:
            scores, scaled_scores = rule["scores_df"], rule["selected_scores"]
        scores.plot(ax=axes[1])

        axes[1].scatter(scaled_scores.index.tolist(),scaled_scores.values)
        intervals = rule["rule"].get_intervals(scaled_scores.index.tolist(),rule["scale"])
        y = df.loc[scaled_scores.index].values.ravel()
        axes[0].hlines(xmin=intervals[:, 0], xmax=intervals[:, 1], y=y, lw=3)

    def get_intervals(self, name, scale = None):
        rule = self.rule_dict[name]
        scale = scale if scale is not None else rule["scale"]
        return rule["rule"].get_intervals(rule["selected_scores"].index.tolist(), scale)