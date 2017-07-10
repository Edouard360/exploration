import matplotlib.pyplot as plt
import numpy as np
from datetime import timedelta
import pandas as pd
from collections import deque
import heapq


def lazyprop(fn):
    attr_name = '_lazy_' + fn.__name__

    @property
    def _lazyprop(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)

    return _lazyprop


def sequence_to_interval(sequence, threshold=15, plot=False):
    sequence_diff = np.array([(sequence[i + 1] - sequence[i]) for i in range(len(sequence) - 1)])
    intervals = []
    i = 0
    while (i < len(sequence_diff) + 1):  # len(sequence_diff) < len(sequence)
        start = sequence[i]
        while (i < len(sequence_diff) and sequence_diff[i] <= threshold):
            i += 1
        end = sequence[i]
        i += 1
        intervals.append((start, end))

    if (plot):
        plt.plot(sequence_diff, np.ones(len(sequence_diff)), 'ro')

    intervals = np.array([time_index for interval in intervals for time_index in interval])
    return intervals.reshape(-1, 2)


def merge_close_intervals(intervals, threshold=timedelta(days=1)):
    intervals_diff = intervals[1:, 0] - intervals[:-1, 1]
    new_intervals = []
    i = 0
    while (i < len(intervals_diff) + 1):  # len(sequence_diff) < len(sequence)
        start_i = i
        while (i < len(intervals_diff) and intervals_diff[i] <= threshold):
            i += 1
        end_i = i
        i += 1
        new_intervals.append([intervals[start_i, 0], intervals[end_i, 1]])

    return np.array(new_intervals).reshape(-1, 2)


def drop_close_extrema(df, time=timedelta(days=1)):
    # No nan values theoretically
    len(df.index)
    i_ref = df.index[0]
    to_remove = []
    for i in df.index:
        if (i_ref < i - time):
            i_ref = i
        elif (df[i] < df[i_ref]):
            to_remove += [i]
        elif (df[i] > df[i_ref]):
            to_remove += [i_ref]
            i_ref = i
    return to_remove


def combine(scores_to_update, scores_exempt, widths, multiply=None):
    scores_for_queue = [score.sort_index() for score in scores_to_update] + [score.sort_index() for score in
                                                                             scores_exempt]
    if multiply is None:
        multiply = [1] * len(scores_for_queue)

    scores_queue = [deque(zip(score.index.tolist(), score.values.ravel(), len(score) * [width],
                              len(score) * [mult], len(score) * [idx])) for
                    idx, (score, width, mult) in enumerate(zip(scores_for_queue, widths, multiply))]

    priority_queue = []
    dict_behind = {}
    # index = []
    # data = []

    index_array = [[] for i in range(len(scores_to_update))]
    data_array = [[] for i in range(len(scores_to_update))]

    for queue in scores_queue:
        if len(queue) > 0:
            timestamp, score, width, mult, idx = queue.popleft()
            heapq.heappush(priority_queue, (timestamp, score, width, mult, idx))

    while (len(priority_queue) > 0):
        (timestamp, score, width, mult, idx) = heapq.heappop(priority_queue)
        valid = True
        for timestamp_it, score_it, width_it, mult_it, idx_it in priority_queue:
            if idx_it == idx:
                continue;
            else:
                if timestamp_it - width_it < timestamp and score * mult <= score_it * mult_it:
                    valid = False
                    break

        for idx_it, (timestamp_it, score_it, width_it, mult_it) in dict_behind.items():
            if idx_it == idx:
                continue;
            else:
                if timestamp < timestamp_it + width_it and score * mult <= score_it * mult_it:
                    valid = False
                    break

        if (valid and idx < len(scores_to_update)):
            index_array[idx] += [timestamp]
            data_array[idx] += [score]

        dict_behind[idx] = (timestamp, score, width, mult)
        if len(scores_queue[idx]) > 0:
            timestamp, score, width, mult, idx = scores_queue[idx].popleft()
            heapq.heappush(priority_queue, (timestamp, score, width, mult, idx))

    return [pd.DataFrame(index=index, data=np.array(data).reshape(-1, 1), columns=["score"]) for index, data in
            zip(index_array, data_array)]


def corr(values_1, values_2):
    (values_1 - np.mean(values_1)).dot(values_2 - np.mean(values_2)) / (
        len(values_1) * np.sqrt((np.var(values_1) * np.var(values_2))))
