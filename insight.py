#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
insight.py
@author: edouardm
"""
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from insight_tools import check_type

class Insight:

    def __init__(self,obs_deb,obs_vit,obs_tmp,obs_pui):
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