import pandas as pd
import numpy as np
from ipywidgets import interact,BoundedIntText,Button,ToggleButton,IntSlider, Dropdown
from IPython.display import display
import matplotlib.pyplot as plt
from matplotlib.dates import HourLocator, DateFormatter
from constants import *

class Interaction:
    def __init__(self, intervals):
        self.intervals = intervals
        initial = {"scores": np.zeros(len(self.intervals)),"idx": np.arange(len(self.intervals)),"order":0}
        self.idx_dict = {'Initial':initial} # mettre un index normal de base ...

    def add_idx(self, name, df_score, df_filter=lambda df: True):
        idx_filtered = [i for i in range(len(self.intervals)) if df_filter(self.intervals[i])]
        scores = [df_score(self.intervals[i]) for i in idx_filtered]
        arg_sorted_scores = np.argsort(scores)[::-1]
        idx_sorted = [idx_filtered[i] for i in arg_sorted_scores]
        scores = [scores[i] for i in arg_sorted_scores]
        self.idx_dict[name] = {"scores": scores,
                               "idx": idx_sorted,
                               "order" : len(self.idx_dict)}

    def add_filter(self,name,df_filter):
        idx_filtered = [i for i in range(len(self.intervals)) if df_filter(self.intervals[i])]
        self.idx_dict[name] = {"idx": idx_filtered}

    def interact(self):
        list_dropdown = list(self.idx_dict.keys())
        list_dropdown.sort(key=lambda k:self.idx_dict[k]["order"])
        idx_widget = Dropdown(
            options=list_dropdown,
            value='Initial',
            description='Anomaly type:',
            disabled=False,
            button_style='danger' # 'success', 'info', 'warning', 'danger' or ''
        )

        interval_widget = BoundedIntText(value=0, min=0, max=len(self.intervals) - 1, step=1,
                                         description='Interval number', disabled=False)

        def idx_widget_observe(p):
            if ('value' in p.new):
                interval_widget.max = len(self.idx_dict[p.new['value']]["idx"]) - 1

        idx_widget.observe(idx_widget_observe)
        # A voir... idx_widget  -->> len(self.idx_dict[idx_widget.value]["idx"])

        btn_up = Button(description='Up', disabled=False, button_style='success', tooltip='Increase interval number by 1')
        btn_down = Button(description='Down', disabled=False, button_style='warning', tooltip='Decrease interval number by 1')

        toggle_widget = ToggleButton(
            value=False,
            description='Tight Layout',
            disabled=False,
            button_style='',  # 'success', 'info', 'warning', 'danger' or ''
            icon='check'
        )
        display(btn_up)
        display(btn_down)

        def increase(t):
            interval_widget.value += 1

        def decrease(t):
            interval_widget.value -= 1

        btn_up.on_click(increase)
        btn_down.on_click(decrease)

        interact(self.plot_all, i=interval_widget, tight_boolean=toggle_widget, name_idx = idx_widget);

    def plot_all(self,i,tight_boolean,name_idx):
        if (type(self.intervals) is pd.DataFrame):
            df = self.intervals
        else:
            df = self.intervals[self.idx_dict[name_idx]["idx"][i]]
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
