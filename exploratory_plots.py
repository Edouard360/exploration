import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec 
import numpy as np
from datetime import timedelta, datetime, time 
from tools import sequence_to_period
import scipy.signal as signal
# Question Bad/M => bad medium

# value  quality
# 32767  24________
#    59  TRX_______
#   356  TRX_______

# quality = same over all the variables ≠ level
# there are still some moments where

class Observation:
    def __init__(self,file_path):
        self.df = pd.read_csv(file_path,sep=";")
        self.df.columns = ["date","value","quality","level"]
        self.df['date'] = pd.to_datetime(self.df['date'],format="%d-%b-%y %H:%M:%S.0") #  long process
        self.df.set_index('date',inplace=True)
        self.values_df = self.df['value']
        self.n_unique_rolling = None

    def stats(self):
        print(self.df[["value","level"]].groupby("level").count())
        print(self.df[["value", "quality"]].groupby("quality").count())

    def plot_unique_values(self,xlim = (0,1000)):
        plt.figure()
        unique_values = self.values_df.unique()
        #plt.hist(test.values,np.linspace(300,450,40))
        plt.plot(unique_values, np.ones(len(unique_values)), 'ro')
        plt.xlim(xlim)
        
    


    def plot_between_dates(self,start,end):
        self.values_df.ix[start:end].plot(ylim=(50,500))
    
#####################################################################     

        
    def periods_low_sample(self,hours = 1):
        time_btw = self.values_df.index[1:]-self.values_df.index[:-1]
        ind_tmp = time_btw > timedelta(hours=hours)
        start_ind = np.concatenate((ind_tmp,[False]))
        end_ind = np.concatenate(([False],ind_tmp))
        return list(zip(self.values_df.index[start_ind],self.values_df.index[end_ind]))
        
    def day_bad(self):
        bad_level_dates = np.unique(self.df.ix[self.df["level"] == "Bad", :].index.date)
        print("There are %i different bad level dates"%len(bad_level_dates))
        return bad_level_dates
    
    def date_max(self):
        max_value = self.values_df.max()
        nb_max = (self.values_df == max_value).sum()
        print("Max value is:%.3f, taken at %i different instants"%(max_value,nb_max))
        return self.values_df.index[(self.values_df == max_value)]
    
    def day_min(self):   
        for i in (np.where(self.values_df == self.values_df.min())[0][:30]):
            plt.figure()
            self.values_df.ix[i-20:i+20].plot()
        bad_level_dates = np.unique(self.df.ix[self.df["level"] == "Bad", :].index.date)
        print("There are %i different bad level dates"%len(bad_level_dates))
        return self.values_df.index[self.values_df == self.values_df.min()]




def get_bad_level_days(iterable_obs):
    set_bad_level_days = set(iterable_obs[0].bad_level_days())
    for obs in iterable_obs[1:]:
        set_bad_level_days = set_bad_level_days.intersection(obs.bad_level_days())
    return set_bad_level_days 


#df = obs_deb_1.df
#overflow_dates =np.unique(df.ix[df["value"]==32767,:].index.date)
#problem_dates = np.unique(df.ix[df["level"]=="Bad",:].index.date)



#df_ = df.ix[df["level"] == "Bad", :]
#df_[["value","quality"]].groupby("quality").count()

#df__ = df.ix[df["value"] == 32767, :] # 24________  is the quality (always the same)
#df__[["value","quality"]].groupby("quality").count()

#inter_pb_dates = problem_dates.intersection(semi_problem_dates) -- 13

def ylim_from_values(values):
    values = np.array(values)
    median = np.median(values)
    mad = np.median(np.abs(values - median))
    return (median-3*mad, median+3*mad)

def ylim_from_tuple(tuple_values):
    ylim = (np.inf,-np.inf)
    for values in tuple_values:
        ylim_current = ylim_from_values(values)
        ylim = (min(ylim[0],ylim_current[0]), max(ylim[1],ylim_current[1]))
    return ylim   

def plot_tuple_on_axe(tuple_values,ax):
    for values in tuple_values:
        values.plot(ax=ax)
    ylim = ylim_from_tuple(tuple_values)
    ax.set_ylim(ylim)
    
  
# ===============    
    
#from datetime import datetime

#datetime_object = datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')
#%y
obs_deb_1 = Observation("./GMPP/A1-DEB1.txt")
#obs_deb_2 = Observation("./GMPP/A1-DEB2.txt")
#obs_deb_3 = Observation("./GMPP/A1-DEB3.txt")
#obs_deb_4 = Observation("./GMPP/A1-DEB4.txt")
#obs_vit_1 = Observation("./GMPP/A1-VIT1.txt")
#obs_vit_2 = Observation("./GMPP/A1-VIT2.txt")
#obs_vit_3 = Observation("./GMPP/A1-VIT3.txt")
#obs_vit_4 = Observation("./GMPP/A1-VIT4.txt")
#
#obs_pui = Observation("./GMPP/A1-PUI-.txt")
#obs_tmp = Observation("./GMPP/A1-TEM-.txt")
#
#obs_deb_tuple = (obs_deb_1,obs_deb_2,obs_deb_3,obs_deb_4)
#obs_vit_tuple = (obs_vit_1,obs_vit_2,obs_vit_3,obs_vit_4)
#
#bad_days = list(get_bad_level_days(obs_deb_tuple))


# ===============


#end_day = bad_day + timedelta(days=1)
#time(hour=6)
#start_day = bad_day - timedelta(days=1)
#end_day = datetime.combine(start_day, time(hour=6))
#start = start_day.strftime("%Y-%m-%d %H:%M:%S")
#end = end_day.strftime("%Y-%m-%d %H:%M:%S")

# ===============

#def low_pass_filter(values,cutoff = 0.1):
#    N  = 2    # Filter order
#    B, A = signal.butter(N, cutoff, output='ba')
#    signal.butter
#    return signal.filtfilt(B,A, values)

# ===============

#for bad_day in bad_days:
#    start_day = bad_day - timedelta(days=2)
#    #end_day = datetime.combine(start_day, time(hour=6))
#    end_day = bad_day #+ timedelta(days=1)
#    start = start_day.strftime("%Y-%m-%d %H:%M:%S")
#    end = end_day.strftime("%Y-%m-%d %H:%M:%S")
#
#    fig = plt.figure(figsize=(15, 10)) # length 15 width 10
#    gs = gridspec.GridSpec(3, 2)
#    
#    ax_deb = plt.subplot(gs[0, :])
#    tuple_values = [obs.values_df.ix[start:end] for obs in obs_deb_tuple]
#    
#    try:
#        plot_tuple_on_axe(tuple_values,ax_deb)
#        ax_vit = plt.subplot(gs[1, :])
#        tuple_values = [obs.values_df.ix[start:end] for obs in obs_vit_tuple]
#        plot_tuple_on_axe(tuple_values,ax_vit)
#        
#        ax_tmp = plt.subplot(gs[2, 0])
#        tmp_df = obs_tmp.values_df.ix[start:end].to_frame()
#        tmp_smooth_df = tmp_df.assign(smooth = low_pass_filter(tmp_df.values.ravel()))
#        plot_tuple_on_axe([tmp_smooth_df[col] for col in tmp_smooth_df],ax_tmp)
#        
#        ax_pui = plt.subplot(gs[2, 1])
#        tmp_df = obs_tmp.values_df.ix[start:end].to_frame()
#        tmp_pui_df = tmp_df.assign(smooth = low_pass_filter(tmp_df.values.ravel()))
#        plot_tuple_on_axe([tmp_pui_df[col] for col in tmp_pui_df],ax_pui)
#        #plot_tuple_on_axe([obs_pui.values_df.ix[start:end]],ax_pui)
#        #plt.tight_layout()
#    except:
#        plt.close()
#        print("Plot was close since not enough values were found between :%s and %s"%(start,end))
#        continue

# ===============    


        
#ax_pui.set_ylim()






#obs_deb_1 = Observation("./GMPP/A1-VIT4.txt")

#obs_deb_1.compute_rolling_unique(100)
#plt.plot(obs_deb_1.rolling_unique)

#"./GMPP/A1-DEB2.txt"
#obs_deb_1.plot_unique_values((1,1000))
#obs_tmp = Observation("./GMPP/A1-TEM-.txt")
#obs_tmp.plot_unique_values((1,60))
#obs_pui = Observation("./GMPP/A1-PUI-.txt")
#obs_vit = Observation("./GMPP/A1-VIT1.txt")

# set_bad_level_days = set(obs_deb_1.bad_level_days()).intersection(obs_tmp.bad_level_days()).intersection(obs_pui.bad_level_days()).intersection(obs_vit.bad_level_days())
# date_one = list(set_bad_level_days)[0]
# start = date_one - timedelta(days=1)

# df = obs_deb_1.values_df
# to_remove = df[df>30000]
# locations = [df.index.get_loc(to_remove.index[i]) for i in range(len(to_remove))]
# periods = sequence_to_period(locations)


#for diff in



# plt.xlim((1,40))
# print("OK")
# start = "2015-02-27 00:00:00" # beginning
# end = "2015-02-28 00:00:00"
# obs_deb_1.plot_between_dates(start,end)
#
#
#
#
# df = obs_deb_1.values_df
# window_length = 200
# rolling_win = df.rolling(window_length)
# testing = rolling_win.apply(lambda x:len(np.unique(x)))
# testing.plot()
#
# rolling_med = df.rolling(window_length).median()
# df_minus_med = abs(df.ix[window_length-1:] - rolling_med[window_length-1:])
# date = df_minus_med.rolling(window_length).median().argmax()
# location = df.index.get_loc(date)
# #location = 477832
# #df.ix[location-20000:location-15000].plot(ylim=(50,500))
# df.ix[location-1000:location+1000].plot(ylim=(50,500))
# df.rolling(4).mean().ix[location-1000:location+1000].plot(ylim=(50,500))
#
# start_object = obs_deb_1.bad_level_days()[10]
# start = start_object.strftime("%Y-%m-%d")
# end = (start_object + timedelta(days=1)).strftime("%Y-%m-%d")
#
#
