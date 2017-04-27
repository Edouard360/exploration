import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import timedelta
from tools import low_pass_filter,sequence_to_period
from insight_tools import plot
from insight import Insight
from rolling import Rolling

pd.options.mode.chained_assignment = None

class Observation:
    def __init__(self,path,files_name,files_tag):
        list_df = [pd.read_csv(path+file_name,sep=";") for file_name in files_name]
        # list_df_values = []
        for df,tag in zip(list_df,files_tag):
            df.columns = ["date","value_"+tag,"quality_"+tag,"level_"+tag]
            df.drop_duplicates(subset = "date",inplace=True)
            df['date'] = pd.to_datetime(df['date'], format="%d-%b-%y %H:%M:%S.0")
            df.set_index('date', inplace=True)
            # list_df_values.append(df["value_"+tag].to_frame())

        full_df = pd.concat(list_df,axis=1)
        full_df.fillna(method='ffill',inplace=True)
        full_df.head().fillna(method='bfill', inplace=True)
        self.full_df = full_df
        self.values_df = full_df.ix[:,["value" in column for column in full_df.columns]]
        self.level_df = full_df.ix[:,["level" in column for column in full_df.columns]]

    def periods_low_sample(self,hours = 1):
        time_btw = self.values_df.index[1:]-self.values_df.index[:-1]
        ind_tmp = time_btw > timedelta(hours=hours)
        start_ind = np.concatenate((ind_tmp,[False]))
        end_ind = np.concatenate(([False],ind_tmp))
        return list(zip(self.values_df.index[start_ind],self.values_df.index[end_ind]))

    def periods_bad_level(self):
        bad_periods = self.level_df.index[(self.level_df == "Bad").any(axis=1)]
        return sequence_to_period(bad_periods,timedelta(hours=15))

    def smooth(self,cutoff = 0.1):
        self.values_df = self.values_df.assign(smooth = low_pass_filter(self.values_df.ix[:,0].values.ravel(),cutoff = cutoff))

    def plot(self,axe=None,xlim=None,auto_set_y=False):
        plot(self.full_df,axe,xlim,auto_set_y)

def get_bad_level_days(iterable_obs):
    set_bad_level_days = set(iterable_obs[0].bad_level_days())
    for obs in iterable_obs[1:]:
        set_bad_level_days = set_bad_level_days.intersection(obs.bad_level_days())
    return set_bad_level_days 


obs_deb = Observation("./GMPP/",["A1-DEB1.txt"],["deb1"])
#obs_deb = Observation("./GMPP/",["A1-DEB1.txt","A1-DEB2.txt","A1-DEB3.txt"],["deb1","deb2","deb3"])
periods = obs_deb.periods_bad_level()
print(periods)
# obs_vit = Observation("./GMPP/",["A1-VIT1.txt"],["vit1"])
# rolling = Rolling(obs_vit.values_df.values.ravel(),obs_vit.values_df.index)
# periods = rolling.periods()
# #obs_vit = Observation("./GMPP/",["A1-VIT1.txt","A1-VIT2.txt"],["vit1","vit2"])
# obs_tmp = Observation("./GMPP/",["A1-TEM-.txt"],["tmp"])
# obs_pui = Observation("./GMPP/",["A1-PUI-.txt"],["pui"])
#
# insight = Insight(obs_deb,obs_vit,obs_tmp,obs_pui)
# insight.plot("2013-05-01","2013-05-02")
# plt.show()