from ipywidgets import interact, BoundedIntText, Button, ToggleButton, Dropdown
from IPython.display import display,clear_output
from insight import *
from constants import *

class Widget:
    def __init__(self, df):
        self.df = df

    def dropdown_anomalies(self):
        idx_widget = Dropdown(
            options=[TREND_UP, TREND_DOWN],
            value=TREND_UP,
            description='Anomaly type:',
            disabled=False,
            button_style='danger'  # 'success', 'info', 'warning', 'danger' or ''
        )


    def intervals(self, intervals):
        self.intervals = intervals
        interval_widget = BoundedIntText(value=0, min=0, max=int(10) - 1, step=1,
                                         description='Interval number', disabled=False)
        btn_up = Button(description='Up', disabled=False, button_style='success')
        btn_down = Button(description='Down', disabled=False, button_style='warning')

        display_dropdown = Dropdown(
            options=['1', '2', '3', '4'],
            value='1',
            description='Display:',
            disabled=False,
            button_style='danger'  # 'success', 'info', 'warning', 'danger' or ''
        )

        def increase(t):
            interval_widget.value += 1

        def decrease(t):
            interval_widget.value -= 1

        display(btn_up)
        display(btn_down)
        btn_up.on_click(increase)
        btn_down.on_click(decrease)
        interact(self.plot, i=interval_widget, display=display_dropdown)

    def plot(self,i,display):
        begin, end = self.intervals[i]
        {'1': plot_single,
        '2':plot_deb_pre,
        '3':plot_all_stack,
        '4': plot_all_tight}[display](self.df[begin:end])