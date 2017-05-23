import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import timedelta
from tools import low_pass_filter, bandstop_filter, sequence_to_interval, lazyprop
from export_series import Exporter
from insight_tools import plot
from insight import Insight
from rolling import Rolling
from interval import Interval
from exploitation.exploitation import Exploitation

pd.options.mode.chained_assignment = None


class Observation:
    def __init__(self, path, files_name, files_tag, format="%d-%b-%y %H:%M:%S.0", ncol=4):
        print("Loading in memory %i observations..." % (int(len(files_name))))
        list_df = [pd.read_csv(path + file_name, sep=";") for file_name in files_name]
        self.ncol = ncol
        for df, tag in zip(list_df, files_tag):
            if self.ncol == 4:
                df.columns = ["date", "value_" + tag, "quality_" + tag, "level_" + tag]
            else:
                df.columns = ["date", "value_" + tag]
            df.drop_duplicates(subset="date", inplace=True)
            df['date'] = pd.to_datetime(df['date'], format=format)
            df.set_index('date', inplace=True)
        full_df = pd.concat(list_df, axis=1)
        full_df.fillna(method='ffill', inplace=True)
        full_df.head().fillna(method='bfill', inplace=True)
        self.full_df = full_df
        self.values_df = full_df.ix[:, ["value" in column for column in full_df.columns]]
        self.level_df = full_df.ix[:, ["level" in column for column in full_df.columns]]

    def split_valid_intervals_df(self, hours=50):
        return self.get_valid_interval(hours=hours).split_accordingly(self.values_df)

    def split_healthy_unhealthy(self):
        healthy_intervals, unhealthy_intervals = self.longest_valid_intervals.separate_intervals(healthy=(0.1, 0.3),
                                                                                                 unhealthy=(0.7, 1.0))
        healthy_ts = Interval(healthy_intervals).split_accordingly(self.values_df)
        unhealthy_ts = Interval(unhealthy_intervals).split_accordingly(self.values_df)
        return healthy_ts, unhealthy_ts

    def get_valid_interval(self, hours=50):
        valid_intervals_to_explore = self.intervals_to_remove.valid_ante_interval(self.start_bad_level, hours=hours)
        return Interval(valid_intervals_to_explore)

    @lazyprop
    def longest_valid_intervals(self):
        return self.get_valid_interval(hours=0)

    @lazyprop
    def intervals_to_remove(self):
        interval_to_remove = Interval(self.intervals_low_diversity)
        interval_to_remove.update(self.intervals_bad_level)
        interval_to_remove.update(self.intervals_low_sample)
        return interval_to_remove

    @lazyprop
    def intervals_low_sample(self, hours=1):
        print("Analysing intervals with low sampling rate")
        time_btw = self.values_df.index[1:] - self.values_df.index[:-1]
        ind_tmp = time_btw > timedelta(hours=hours)
        start_ind = np.concatenate((ind_tmp, [False]))
        end_ind = np.concatenate(([False], ind_tmp))
        return np.array(list(zip(self.values_df.index[start_ind], self.values_df.index[end_ind])))

    @lazyprop
    def intervals_low_diversity(self):
        print("Analysing intervals with low diversity")
        rolling = Rolling(self.values_df.ix[:, 0].values.ravel(), self.values_df.index)
        return rolling.intervals()

    @lazyprop
    def intervals_bad_level(self):
        print("Analysing intervals with bad level")
        bad_timestamp_value = self.values_df.index[(self.values_df == self.values_df.max()[0]).any(axis=1)]
        if self.ncol == 4:
            is_bad = np.vectorize(lambda label: label in ["Bad", "Bad/M"])
            bad_timestamp_label = self.level_df.index[(is_bad(self.level_df)).any(axis=1)]
            bad_timestamp = sorted(bad_timestamp_label.tolist() + bad_timestamp_value.tolist())
        else:
            bad_timestamp = sorted(bad_timestamp_value.tolist())
        bad_intervals = sequence_to_interval(bad_timestamp, timedelta(hours=15))
        return bad_intervals

    @lazyprop
    def start_bad_level(self):
        return self.intervals_bad_level[:, 0].reshape(-1, 1)

    @lazyprop
    def end_bad_level(self):
        return self.intervals_bad_level[:, 1].reshape(-1, 1)

    def smooth(self, cutoff=0.1):
        self.values_df = self.values_df.assign(
            smooth=low_pass_filter(self.values_df.ix[:, 0].values.ravel(), cutoff=cutoff))

    def smooth_stop(self, cutoff=[0.1, 0.9]):
        self.values_df = self.values_df.assign(
            smooth_stop=bandstop_filter(self.values_df.ix[:, 0].values.ravel(), cutoff=cutoff))

    def plot(self, xlim=None, auto_set_y=False, **kargs):
        plot(self.full_df, xlim, auto_set_y, **kargs)


PATH = "../Data/GMPP_IRSDI1/"

fnames = [
    "A1-DEB1-1.txt"]  # ,"A1-DEB1-2.txt","A1-DEB1-3.txt","A1-DEB1-4.txt","A1-DEB2-1.txt","A1-DEB2-2.txt","A1-DEB2-3.txt","A1-DEB2-4.txt"]
tags = ["deb1_1"]  # ,"deb1_2","deb1_3","deb1_4","deb2_1","deb2_2","deb2_3","deb2_4"]
obs_deb = Observation(PATH, fnames, tags, format="%Y-%m-%dT%H:%M:%S.000Z", ncol=2)

healthy_ts, unhealthy_ts = obs_deb.split_healthy_unhealthy()

exporter = Exporter()
exporter.export_ts(healthy_ts, unhealthy_ts)

'''
fnames = ["A1-TEM1-.txt","A1-TEM2-.txt","A1-TEM3-1.txt","A1-TEM3-2.txt","A1-TEM3-3.txt","A1-TEM3-4.txt"]
tags = ["tmp-inj","tmp-fuites-joint","tmp-eau1","tmp-eau2","tmp-eau3","tmp-eau4"]
obs_tmp = Observation(PATH,fnames,tags,format="%Y-%m-%dT%H:%M:%S.000Z",ncol=2)
'''

'''
fnames = ["A1-DEB3-1.txt","A1-DEB3-2.txt","A1-DEB3-3.txt","A1-DEB3-4.txt"]
tags = ["deb3_1","deb3_2","deb3_3","deb3_4"]
obs_deb_3 = Observation(PATH,fnames,tags,format="%Y-%m-%dT%H:%M:%S.000Z",ncol=2)

obs_pre = Observation(PATH,["A1-PRE-.txt"],["pre"],format="%Y-%m-%dT%H:%M:%S.000Z",ncol=2)
obs_pre.smooth()
obs_pui = Observation(PATH,["A1-PUI-.txt"],["pui"],format="%Y-%m-%dT%H:%M:%S.000Z",ncol=2)
'''

# obs_pre = Observation("./GMPP/A1-PRE-/",["A1-PRE-_5.txt"],["pre"])

# obs_pui = Observation("./GMPP/",["A1-PUI-.txt"],["pui"])
# obs_tmp = Observation("./GMPP/",["A1-TEM-.txt"],["tmp"])
# obs_vit = Observation("./GMPP/",["A1-VIT1.txt","A1-VIT2.txt"],["vit1","vit2"])
# obs_vit = Observation("./GMPP/",["A1-VIT1.txt"],["vit1"])

# obs_deb = Observation("./GMPP/",["A1-DEB1.txt","A1-DEB2.txt","A1-DEB3.txt","A1-DEB4.txt"],["deb1","deb2","deb3","deb4"])
# obs_deb = Observation("./GMPP/",["A1-DEB1.txt","A1-DEB2.txt","A1-DEB3.txt","A1-DEB4.txt"],["deb1","deb2","deb3","deb4"])

# list_values_df = obs_deb.split_valid_intervals_df()

# intervals_low_sample = np.array(obs_tmp.intervals_low_sample())
# intervals_low_sample[18] '2015-03-03 23:59:00' - '2015-03-05 00:00:00'
# intervals = Interval(intervals_low_sample)
# intervals.split_accordingly(obs_tmp)
# [plot(df.diff().var(axis=1).rolling(4).mean().ix[:-1],ax = plt.subplots()[1]) for df in list_values_df[:5]]
# list_values_df[0].rolling(100,axis=0).corr().min(axis=2).min(axis=0).plot()
# print(len(list_values_df))

# start = '2008-01-09 12:10:00'
# end = '2008-01-13 16:10:00'
# start = '2010-04-01 12:10:00'
# end = '2010-09-01 16:10:00'
# xlim = (start,end)
# obs_iter = [obs_tmp,obs_deb,obs_deb_3,obs_pre,obs_pui]
# [plot(df) for df in list_values_df]
# [plot(df) for df in list_values_df[:20]]
# insight = Insight()
# insight.plot_nine_frames(list_values_df)
# insight.plot(obs_iter,start,end)
# insight.plot("2013-05-01","2013-05-02")

# exp = [Exploitation(df) for df in list_values_df]
# exp[0].potential_plot(w_var = 200,w_auto = 200)
# exp.compute_top_discord(w_length = 40)
# exp.correlation_plot()
# exp.variation_plot()
# exp[0].plot()
