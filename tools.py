import heapq
from collections import deque
from datetime import timedelta

import numpy as np
import pandas as pd


def sequence_to_interval(sequence, threshold=15):
    """
    Aggregate a sequence of points to form intervals; if sequence is an array of integer; or
    Aggregate a sequence of points in time to form time intervals; if sequence is an array of timestamps.
    :param sequence: an array - of integer or timestamps.
    :param threshold: should be a timedelta object like `timedelta(days=1)` if it is a sequence of timestamps. Otherwise, an integer
    :return:
    """
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

    intervals = np.array([time_index for interval in intervals for time_index in interval])
    return intervals.reshape(-1, 2)


def merge_close_intervals(intervals, threshold=timedelta(days=1)):
    """
    Merge an array of sorted intervals if there extremity is close enough.
    The `threshold` determines the closeness.
    :param intervals: an array of intervals.
    :param threshold: should be a timedelta object like `timedelta(days=1)`.
    :return:
    """
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
    """
    The combine function deals with the multi-scale aspect of anomaly detection.
    For instance for the trend_up anomaly there are scales:
    1d, 7d, 30d, 180d.
    We might want to remove the instances of 1d anomaly that are "included" in the instances of 7d or 30d or 180d.
    If we want to let 7d, 30d, 180d intact, we would write
    - `widths = [timedelta(days = 1),timedelta(days = 7),timedelta(days = 30),timedelta(days = 180)]`
    - `combine([score_df_1d],[score_df_7d,score_df_30d,score_df_180d], widths = widths)`
    Otherwise,if we want all dataframes to be influenced, for instance we might want a 1d trend_up to remove the trend_up at larger scales if there are less significant, we might write:
    - `combine([score_df_1d, score_df_7d,score_df_30d,score_df_180d], [], widths = widths)`
    :param scores_to_update: A list of dataframe from which we will remove false positives, that is an anomaly detected at a scale that actually belong to another scale.
    :param scores_exempt: If any, a list of dataframe of scores from which we don't remove anything.
    :param widths: An array of the different widths of influence of each dataframe.
    :param multiply: Optionnal. An array of multiplying factors, to weigh the importance of the scores.
    :return:
    """
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