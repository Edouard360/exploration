#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
insight.py
@author: edouardm
"""
import matplotlib.pyplot as plt
from matplotlib.dates import HourLocator, DateFormatter
import pandas as pd
from constants import *

class Plot:
    def __init__(self,list_df):
        self.list_df = list_df

    def plot_all(self,tight_boolean, i):
        if (type(self.list_df) is pd.DataFrame):
            df = self.list_df
        else:
            df = self.list_df[i]
        # plt.figure(figsize=(width, height))
        if hasattr(df,"reactor_site"):
            print("Nuclear reactor : "+str(df.reactor_site))
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

        [t1,t2] = axes[3].plot(df[tmp2])
        axes[3].legend([t1, t2], ["injection","fuite"], loc='best')
        axes[3].set_title("Température injection aux joints / Température fuites joint 1")

        axes[4].plot(df[deb3])
        axes[4].set_title("Débit d'injection au joint")
        axes[4].set_facecolor("#d5e5e5")
        axes[5].plot(df[vit])
        axes[5].set_title("Vitesse de la pompe")
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