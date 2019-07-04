import numpy as np
import pandas as pd
import itertools

# 1. helper functions for "plotting_functions.py" 
# (for deep_work_plot, time_spent_plot and weight_plot)
def customize_marker_colors(x_values, marker_color):
    marker_colors = []
    for date_string in x_values:
        date = pd.to_datetime(date_string)
        day_of_week = date.dayofweek

        # determine weekend or workday
        if (day_of_week == 5) or (day_of_week == 6):
            # indicating weekends with "hollow" markers
            # (background color of plot is #F5F6F9)
            marker_colors.append("#F5F6F9")
        else:
            marker_colors.append(marker_color)
            
    return marker_colors


# 2. helper functions for "app.py"
def determine_current_streak(pandas_series):  
    values = pandas_series.values
    streaks = []
    for value, streak in itertools.groupby(values):
        if value == 0:
            continue
        else:
            n = 0
            for day in streak:
                n += 1
            streaks.append(n)

    if streaks:
        current_streak = streaks[-1]
    else:
        current_streak = 0
        
    return current_streak