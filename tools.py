import matplotlib.pyplot as plt
import numpy as np


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
    while (i < len(sequence_diff)):
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
