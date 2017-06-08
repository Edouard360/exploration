#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
insight.py
@author: edouardm
"""
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.dates import HourLocator, DateFormatter

from insight_tools import check_type, plot
import pandas as pd

deb1 = ["DEB1-1","DEB1-2","DEB1-3","DEB1-4"]
deb2 = ["DEB2-1","DEB2-2","DEB2-3","DEB2-4"]
deb3 = ["DEB3-1","DEB3-2","DEB3-3","DEB3-4"]
tmp =  ["TEM3-1","TEM3-2","TEM3-3","TEM3-4"]
tmp2 = ["TEM2-"]# Température fuite joint 1
tmp3 = ["TEM1-"] # Température ligne d'injection aux joints (en * Celsius)
deb35 = ["DEB3-5"]
pre = ["PRE-"]
pui = ["PUI-"]

class Insight:

    def __init__(self,obs_deb=None,obs_vit=None,obs_tmp=None,obs_pui=None):
        self.obs_deb = obs_deb
        self.obs_vit = obs_vit
        self.obs_tmp = obs_tmp
        self.obs_pui = obs_pui

    def plot(self,start,end):
        if (type(start) is not str) or (type(end) is not str):
            assert check_type(start) and check_type(end)
            start = start.strftime("%Y-%m-%d %H:%M:%S")
            end = end.strftime("%Y-%m-%d %H:%M:%S")
        xlim = (start, end)
        fig = plt.figure(figsize=(15, 10))  # length 15 width 10
        gs = gridspec.GridSpec(3, 2)

        ax_deb,ax_vit = plt.subplot(gs[0, :]), plt.subplot(gs[1, :])
        ax_tmp, ax_pui = plt.subplot(gs[2, 0]), plt.subplot(gs[2, 1])

        self.obs_deb.plot(ax_deb,xlim)
        self.obs_vit.plot(ax_vit, xlim)
        self.obs_tmp.plot(ax_tmp,xlim)
        self.obs_pui.plot(ax_pui, xlim)
    
    def plot_nine_frames(self,list_values_df):
        fig,axes = plt.subplots(nrows=3,ncols=3,figsize=(15, 10))
        for i, df in enumerate(list_values_df[:9]):
            ax = axes[i % 3, i // 3]
            plot(df,ax = ax);ax.legend().remove()

    def plot(self,observations,start,end):
        n_obs = len(observations)
        xlim = (start, end)
        fig, axes = plt.subplots(nrows=n_obs, ncols=1, figsize=(15, 10), sharex=True)
        for i,obs in enumerate(observations):
            ax = axes[i]
            plot(obs.df,ax = ax,xlim = xlim);ax.legend().remove()


class Plot:
    def __init__(self,list_df):
        self.list_df = list_df

    def plot_all(self,tight_boolean, i):
        if (type(self.list_df) is pd.DataFrame):
            df = self.list_df
        else:
            df = self.list_df[i]
        # plt.figure(figsize=(width, height))
        print("From : " + str(df.index[0].strftime("%d/%m/%Y"))
              + "\nTo   : " + str(df.index[-1].strftime("%d/%m/%Y")))
        if not tight_boolean:
            width = 10
            height = 20
            fig, axes = plt.subplots(nrows=8, ncols=1, figsize=(width, height), sharex=True)
        else:
            width = 12
            height = 12
            fig, axes = plt.subplots(nrows=4, ncols=2, figsize=(width, height), sharex=True)
            axes = [axes[int(i % 4), int(i / 4)] for i in range(8)]
        [d1, d2, d3, d4] = axes[0].plot(df[deb1])
        axes[0].legend([d1, d2, d3, d4], deb1, loc='best')
        axes[0].set_title("Débit de fuite au joint 1 (Gamme Large)")
        axes[1].plot(df[deb2])
        axes[1].set_title("Débit de fuite au joint 1 (Gamme Étroite)")
        axes[2].plot(df[tmp])
        axes[2].set_title("Température eau joint 1 - 051PO")

        axes[3].plot(df[tmp2])
        axes[3].set_title("Température fuites joint 1")

        axes[4].plot(df[deb3])
        axes[4].set_title("Débit d'injection au joint")
        axes[4].set_facecolor("#d5e5e5")
        axes[5].plot(df[tmp3])
        axes[5].set_title("Température ligne d'injection aux joints (en * Celsius)")
        axes[5].set_facecolor("#d5e5e5")

        axes[6].plot(df[pre], 'b')
        axes[6].set_title("Pression (BAR)")
        axes[6].set_facecolor("#d1d1d1")
        axes[7].plot(df[pui], 'k')
        axes[7].set_title("Puissance Nominale (%)")
        axes[7].set_facecolor("#d1d1d1")

        axes[0].get_xaxis().set_ticks([])
        hour_locator = HourLocator([0, 12])
        axes[0].xaxis.set_major_locator(hour_locator)
        axes[0].xaxis.set_major_formatter(DateFormatter("%H:%M"))

        plt.tight_layout()
        plt.show()