import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import timedelta
from tools import low_pass_filter,sequence_to_interval
from insight_tools import plot
from insight import Insight
from rolling import Rolling
from interval import Interval
from exploitation.exploitation import Exploitation
pd.options.mode.chained_assignment = None

class Observation:
    def __init__(self,path,files_name,files_tag):
        list_df = [pd.read_csv(path+file_name,sep=";") for file_name in files_name]
        for df,tag in zip(list_df,files_tag):
            df.columns = ["date","value_"+tag,"quality_"+tag,"level_"+tag]
            df.drop_duplicates(subset = "date",inplace=True)
            df['date'] = pd.to_datetime(df['date'], format="%d-%b-%y %H:%M:%S.0")
            df.set_index('date', inplace=True)
        full_df = pd.concat(list_df,axis=1)
        full_df.fillna(method='ffill',inplace=True)
        full_df.head().fillna(method='bfill', inplace=True)
        self.full_df = full_df
        self.values_df = full_df.ix[:,["value" in column for column in full_df.columns]]
        self.level_df = full_df.ix[:,["level" in column for column in full_df.columns]]
    
    def split_valid_periods_df(self):
        periods_bad_level = self.periods_bad_level()
        rolling = Rolling(self.values_df.ix[:,0].values.ravel(),self.values_df.index)
        period_to_remove = Interval(rolling.intervals())
        period_to_remove.update(self.periods_low_sample())
        period_to_remove.update(periods_bad_level)
        
        start_bad_periods = periods_bad_level[:,0].reshape(-1,1)
        valid_periods_to_explore = period_to_remove.valid_ante_period(start_bad_periods,hours=50)
        period_to_study = Interval(valid_periods_to_explore)
        return period_to_study.split_accordingly(self.values_df)

    def periods_low_sample(self,hours = 1):
        time_btw = self.values_df.index[1:]-self.values_df.index[:-1]
        ind_tmp = time_btw > timedelta(hours=hours)
        start_ind = np.concatenate((ind_tmp,[False]))
        end_ind = np.concatenate(([False],ind_tmp))
        return list(zip(self.values_df.index[start_ind],self.values_df.index[end_ind]))

    def periods_bad_level(self):
        is_bad = np.vectorize(lambda label: label in ["Bad","Bad/M"])
        bad_timestamp_label = self.level_df.index[(is_bad(self.level_df)).any(axis=1)]
        bad_timestamp_value = self.values_df.index[(self.values_df== self.values_df.max()[0]).any(axis=1)]
        bad_timestamp = sorted(bad_timestamp_label.tolist()+bad_timestamp_value.tolist())
        bad_periods = sequence_to_interval(bad_timestamp, timedelta(hours=15))
        return bad_periods

    def smooth(self,cutoff = 0.1):
        self.values_df = self.values_df.assign(smooth = low_pass_filter(self.values_df.ix[:,0].values.ravel(),cutoff = cutoff))

    def plot(self,xlim=None,auto_set_y=False,**kargs):
        plot(self.full_df,xlim,auto_set_y,**kargs)


#obs_pre = Observation("./GMPP/A1-PRE-/",["A1-PRE-_5.txt"],["pre"])
#obs_tmp = Observation("./GMPP/",["A1-TEM-.txt"],["tmp"])
#obs_vit = Observation("./GMPP/",["A1-VIT1.txt","A1-VIT2.txt"],["vit1","vit2"])
#obs_vit = Observation("./GMPP/",["A1-VIT1.txt"],["vit1"])
#obs_pui = Observation("./GMPP/",["A1-PUI-.txt"],["pui"])
obs_deb = Observation("./GMPP/",["A1-DEB1.txt","A1-DEB2.txt","A1-DEB3.txt","A1-DEB4.txt"],["deb1","deb2","deb3","deb4"])
list_values_df = obs_deb.split_valid_periods_df()
#[plot(df.diff().var(axis=1).rolling(4).mean().ix[:-1],ax = plt.subplots()[1]) for df in list_values_df[:5]]
#list_values_df[0].rolling(100,axis=0).corr().min(axis=2).min(axis=0).plot()
#print(len(list_values_df))

#[plot(df) for df in list_values_df]
#insight = Insight()
#insight.plot_nine_frames(list_values_df)
#insight = Insight(obs_deb,obs_vit,obs_tmp,obs_pui)
#insight.plot("2013-05-01","2013-05-02")

exp = Exploitation(list_values_df[0])
#exp.compute_top_discord(w_length = 40)
#exp.correlation_plot()
#exp.variation_plot()
exp.plot()