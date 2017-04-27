import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as signal

def low_pass_filter(values,cutoff = 0.1):
   N  = 2    # Filter order
   B, A = signal.butter(N, cutoff, output='ba')
   signal.butter
   return signal.filtfilt(B,A, values)

def sequence_to_period(sequence, threshold = 15, plot=False):
    sequence_diff = np.array([(sequence[i + 1] - sequence[i]) for i in range(len(sequence) - 1)])
    periods = []
    i = 0
    while (i < len(sequence_diff)):
        start = sequence[i]
        while (i < len(sequence_diff) and sequence_diff[i] < threshold):
            i += 1
        end = sequence[i]
        i += 1
        periods.append((start, end))

    if(plot):
        plt.plot(sequence_diff, np.ones(len(sequence_diff)), 'ro')
    return periods