import pandas as pd
import numpy as np
from score import ScoreAnalysis
from datetime import timedelta
from interval import Interval
import matplotlib.pyplot as plt


class Interaction:
    def __init__(self, df, intervals):
        self.rule_dict = {}
        self.df = df
        self.intervals = intervals

    def add_rule(self, name, rule, scale):
        sample_df = scale.scale(self.df)
        list_df = self.intervals.split_between(sample_df, time=timedelta(days=3))
        list_scores_df = []
        for df in list_df:
            list_scores_df += [rule.score(df)]

        scores_df = pd.concat(list_scores_df, axis=0)
        timestamps = ScoreAnalysis(rule.threshold, drop_time=rule.stride(scale)).analyse_and_sort(scores_df)
        scores = scores_df.loc[pd.Index(timestamps)]

        self.rule_dict[name] = {
            "timestamps": np.array(timestamps),
            "scores": scores.values,
            "order": len(self.rule_dict),
            "sample_df": sample_df,
            "scores_df": scores_df,
            "scale": scale,
            "rule": rule
        }

    def visualize_rule(self, name):
        fig, axes = plt.subplots(2, 1, sharex=True, figsize=(12, 10))
        rule = self.rule_dict[name]
        rule["scale"].scale(self.df).plot(ax=axes[0])
        rule["scores_df"].plot(ax=axes[1])

        axes[1].scatter(self.rule_dict[name]["timestamps"], self.rule_dict[name]["scores"])

        intervals = rule["rule"].get_intervals(rule["timestamps"], rule["scale"])
        y = self.rule_dict[name]["sample_df"].loc[self.rule_dict[name]["timestamps"]].values
        axes[0].hlines(xmin=intervals[:, 0], xmax=intervals[:, 1], y=y, lw=3)

    def get_intervals(self, name):
        rule = self.rule_dict[name]
        return rule["rule"].get_intervals(rule["timestamps"], rule["scale"])
