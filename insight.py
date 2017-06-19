#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
insight.py
@author: edouardm
"""
import matplotlib.pyplot as plt
from matplotlib.dates import HourLocator, DateFormatter
from constants import *

def plot_all(df,axes):
    [d1, d2, d3, d4] = axes[0].plot(df[deb1])
    axes[0].legend([d1, d2, d3, d4], deb1, loc='best')
    axes[0].set_title("Débit de fuite au joint 1 (Gamme Large)")
    axes[1].plot(df[deb2])
    axes[1].set_title("Débit de fuite au joint 1 (Gamme Étroite)")
    axes[2].plot(df[tmp])
    axes[2].set_title("Température eau joint 1 - 051PO")

    [t1, t2] = axes[3].plot(df[tmp2])
    axes[3].legend([t1, t2], ["injection", "fuite"], loc='best')
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