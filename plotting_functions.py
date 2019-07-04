import numpy as np
import pandas as pd

import plotly.graph_objs as go
import plotly.figure_factory as ff
import cufflinks as cf

from scipy.optimize import curve_fit

from helper_functions import customize_marker_colors

cf.go_offline(connected=True)




def deep_work_plot(df, rolling_average):
    
    # 1. calculate moving average
    df = df.rolling(window=rolling_average).mean()
    df = df.dropna()


    # 2. create figure
    fig = df.iplot(mode="markers+lines",
                   title="Time spent on Deep Work", 
                   xTitle="Date", 
                   yTitle="Hours",
                   asFigure=True)


    # 3. customize figure
    # 3.1 layout
    layout = fig.layout
    layout.height = 400
    layout.margin = {"l": 70, "r": 50, "t": 80, "b": 50}

    # 3.2 y-axis
    y_axis = fig.layout.yaxis
    y_axis.tickvals = np.arange(0, 600, 60)
    y_axis.ticktext = np.arange(10)

    # 3.3 scatter markers
    scatter = fig.data[0]
    scatter.marker.size = 5
    scatter.marker.line.width = 1
    scatter.marker.color = customize_marker_colors(scatter.x, "orange")

    # 3.4 hoverinfo
    hovertext_lst = []
    for date_string, total_minutes in zip(scatter.x, scatter.y):
        # determine time spent
        hours = total_minutes // 60
        minutes = total_minutes - hours * 60

        # determine workday or weekend
        date = pd.to_datetime(date_string)
        day_of_week = date.dayofweek
        if (day_of_week == 5) or (day_of_week == 6):
            day = "Weekend"
        else:
            day = "Workday"

        hovertext = "{}<br>{:.0f}h {:02.0f}min".format(day, hours, minutes)
        hovertext_lst.append(hovertext)

    scatter.hoverinfo = "text+x"
    scatter.hovertext = hovertext_lst
    
    return fig




def gantt_chart(df, date_string="", show_ideal_schedule=False):
    
    tasks_color_key = {"Deep Work": "rgb(27,158,119)", 
                   "Shallow Work": "rgb(127,201,127)",
                   "Learning": "rgb(117,112,179)",
                   "Gym": "rgb(36,78,213)"}

    # 1.  prepare data
    # 1.1 filter df 
    if show_ideal_schedule:
        df = df[df.ideal_schedule == True]
        figure_title = "Daily Schedule: ideal Work-Day"
    else:
        df = df[df.Date == date_string]
        figure_title = "Daily Schedule: " + date_string

        # add missing tasks in case there are any
        # (so that y-axis of gantt chart always shows all 4 tasks)
        start_time = pd.to_datetime(date_string + " 11:11:11")      # arbitrary time
        end_time = start_time                                       # duration of missing tasks is zero
        date = pd.to_datetime(date_string)

        tasks_available = set(tasks_color_key.keys())
        tasks_done = set(df.Task.unique())
        tasks_missing = tasks_available - tasks_done
        for task in tasks_missing:
            df_row = pd.DataFrame({"Task": [task], 
                                   "Start": [start_time], 
                                   "Finish": [end_time], 
                                   "Duration": [end_time - start_time], 
                                   "Date": [date],
                                   "ideal_schedule": [False]})
            df = df.append(df_row)

    # 1.2 making sure that tasks are always shown in the same order
    df = df.sort_values("Task")
    df = df.reset_index(drop=True)


    # 2. create figure
    fig = ff.create_gantt(df,
                          title=figure_title,
                          index_col="Task",
                          colors=tasks_color_key,
                          height=300,
                          width=None,
                          showgrid_x=True,
                          group_tasks=True,
                          bar_width=0.5)

    fig = go.Figure(fig)


    # 3. customize figure
    # 3.1 layout
    layout = fig.layout
    layout.paper_bgcolor = "#F5F6F9"
    layout.plot_bgcolor = "#F5F6F9"
    layout.margin = {"t": 75, "b": 20}

    # 3.2 hoverinfo
    hover_text = "Start - {}<br>Finish - {}<br>Duration - {:02}:{:02}"
    for bar in fig.data:
        start_time, end_time = bar.x
        duration = end_time - start_time
        mid_point = start_time + (duration / 2)

        bar.hoverinfo = "text"
        bar.text = hover_text.format(start_time.strftime("%H:%M"),
                                     end_time.strftime("%H:%M"),
                                     duration.components.hours,
                                     duration.components.minutes)
        
        # hoverinfo should only be shown when the cursor is in the middle of the bar 
        # (and not when it is at the beginning or end of the bar)
        bar.x = [mid_point]

        # make markers "invisible" (background color of plot is #F5F6F9)
        # and skip hoverinfo for missing tasks that were added above at 1.1
        if start_time == end_time:
            bar.marker.color = "#F5F6F9"
            bar.hoverinfo = "skip"

    # 3.3 axes
    n_tasks = len(df.Task.unique())
    date_today = df.Date[0]
    x_min = date_today + pd.Timedelta(hours=7)
    x_max = date_today + pd.Timedelta(hours=26)

    layout.xaxis.range = [x_min, x_max]
    layout.xaxis.rangeselector = None
    layout.yaxis.range = [-1.5, n_tasks]

    # 4.  annotations
    # 4.1 determine x- and y-positions
    x_position = date_today + pd.Timedelta(hours=25)
    y_positions = range(n_tasks, -2, -1)

    # 4.2 create text for annotations
    annotation_texts = ["Total time:"]
    total_time_per_task = df.groupby("Task").Duration.sum()
    for time in total_time_per_task:
        text = "{:02}:{:02}".format(time.components.hours, time.components.minutes)
        annotation_texts.append(text)

    total_time = total_time_per_task.sum()
    text = "{:02}:{:02}".format(total_time.components.hours, total_time.components.minutes)
    annotation_texts.append(text)

    # 4.3 create annotations
    annotations = []
    for y_position, text in zip(y_positions, annotation_texts):
        annotation_dict = {"x": x_position,
                           "y": y_position,
                           "text": text, 
                           "showarrow": False, 
                           "font":{"size": 13}}
        annotations.append(annotation_dict)

    layout.annotations = annotations

    # 4.4 draw a line above the last annotation 
    # to indicate that it is the sum of the above times
    shapes = list(layout.shapes)
    shapes.append({'type': 'line',
                   'x0': date_today + pd.Timedelta(hours=24),
                   'x1': date_today + pd.Timedelta(hours=26),
                   'y0': -0.5,
                   'y1': -0.5})

    layout.shapes = shapes

    return fig




def git_hub_chart(df, starting_date, figure_title):
    
    # 1. get df into right shape to create heatmap
    # 1.1 set variables
    n_weeks_in_year = 52
    n_days_in_week = 7
    n_days_in_year = n_weeks_in_year * n_days_in_week   # 364
    
    df = df.loc[starting_date:]
    data = df.values.flatten()
    
    # 1.2 make sure that the data starts at a monday
    # (prepend respective amount of zeros to data)
    starting_date = pd.to_datetime(starting_date)
    day_of_week = starting_date.dayofweek
    zeros = np.zeros(day_of_week)
    
    data = np.concatenate((zeros, data))
    starting_date = starting_date - pd.to_timedelta(day_of_week, unit="D")
    
    # 1.3 ensure that data contains exactly 364 elements
    # (append respective amount of zeros to data)
    n_days_left = n_days_in_year - len(data)
    if n_days_left < 0:
        print("Warning! len(data) is too big. Please delete entries from the beginning of the CSV!")
        return
    else:
        zeros = np.zeros(n_days_left)
        data = np.concatenate((data, zeros))
    
    # 1.4 create new df
    data = data.reshape(n_weeks_in_year, n_days_in_week)  # shape of heatmap
    column_headears = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    df_heatmap = pd.DataFrame(data, columns=column_headears)


    # 2. create figure
    fig = df_heatmap.iplot(kind="heatmap",
                           title=figure_title,
                           asFigure=True)


    # 3. customize figure
    # 3.1 layout
    layout = fig.layout
    layout.height = 255
    layout.margin = {"l": 80, "r": 20, "t": 80, "b": 50}
    layout.hovermode = "closest"

    # 3.2 axes
    # 3.2.1 x-axis
    x_axis = layout.xaxis
    x_axis.showgrid = False
    x_axis.tickcolor = "#F5F6F9"

    # change tick values and their text
    # (display the name of the month at the week where the month starts)
    last_day_of_week_lst = pd.date_range(starting_date, periods=n_weeks_in_year, freq="w")
    current_month = last_day_of_week_lst[0].month_name()[:3]

    tickvals = []
    month_names = []
    index = 0
    for day in last_day_of_week_lst:
        month = day.month_name()[:3]
        if index == 0:
            tickvals.append(index)
            month_names.append(month)
        elif month != current_month:
            tickvals.append(index)
            month_names.append(month)
            current_month = month

        index += 1

    x_axis.tickvals = tickvals
    x_axis.ticktext = month_names

    # 3.2.2 y-axis
    y_axis = layout.yaxis
    y_axis.showgrid = False
    y_axis.tickcolor = "#F5F6F9"
    y_axis.tickvals = [1, 3, 5]
    y_axis.autorange = "reversed"

    # 3.3 heatmap
    heatmap = fig.data[0]
    heatmap.showscale = False
    heatmap.colorscale = [[0, "#d9d9d9"], [1, "#7bc96f"]]
    heatmap.xgap = 2
    heatmap.ygap = 2

    # 3.4 hoverinfo
    days = pd.date_range(start=starting_date, periods=n_days_in_year)
    hover_text = [day.strftime("%Y-%m-%d") for day in days]
    hover_text = np.reshape(hover_text, (-1, 7))
    hover_text = hover_text.T

    heatmap.hoverinfo = "text+y"
    heatmap.text = hover_text

    return fig




def time_spent_plot(df):
    
    # 1.  prepare data
    # 1.1 filter df
    df = df[df.ideal_schedule == False]
    
    # 1.2 determine total time spent for each day as percentage of ideal
    ideal_total_duration = pd.Timedelta(hours=12)
    df = df.groupby("Date").Duration.sum()
    df = df / ideal_total_duration

    # 1.2 filling in "0" for days where I didn't do deep work
    df = df.resample("D").sum()
    df = df.fillna(0)


    # 2. create figure
    fig = df.iplot(mode="lines+markers",
                   title="Time spent on Something productive",
                   xTitle="Date",
                   yTitle="Percentage of Ideal (12h)",
                   asFigure=True)


    # 3. customize figure
    # 3.1 layout
    layout = fig.layout
    layout.height = 400
    layout.margin = {"l": 70, "r": 40, "t": 80, "b": 50}

    # 3.2 y-axis
    y_axis = fig.layout.yaxis
    y_axis.tickvals = np.arange(0, 1.2, 0.2)
    y_axis.ticktext = ['0%','20%','40%','60%','80%','100%']
    y_axis.range = [-0.05, 1.05]

    # 3.3 scatter markers
    scatter = fig.data[0]
    scatter.marker.size = 5
    scatter.marker.line.width = 1
    scatter.marker.color = customize_marker_colors(scatter.x, "orange")

    # 3.4 hoverinfo
    hovertext_lst = []
    for date_string, float_value in zip(scatter.x, scatter.y):
        # determine percentage value
        percentage = round(float_value * 100)
        percentage = "{:.0f}%".format(percentage)

        # determine time spent
        total_time_spent = float_value * ideal_total_duration.components.hours
        hours_spent = int(total_time_spent)
        minutes_spent = (total_time_spent - hours_spent) * 60
        time_spent = "{}h {:02.0f}min".format(hours_spent, minutes_spent)

        # determine workday or weekend
        date = pd.to_datetime(date_string)
        day_of_week = date.dayofweek
        if (day_of_week == 5) or (day_of_week == 6):
            day = "Weekend"
        else:
            day = "Workday"

        hovertext = "{}<br>{}: {}".format(day, percentage, time_spent)
        hovertext_lst.append(hovertext)

    scatter.hoverinfo = "text+x"
    scatter.hovertext = hovertext_lst
    
    return fig




def weight_plot(df, new_approach=False):
    
    # 1. create figure
    fig = df.iplot(mode=["lines", "lines", "lines", "lines+markers"],
                   xTitle="Date",
                   yTitle="Weight in kg",
                   colors=["rgb(177,0,38)", "rgb(44,162,95)", "rgb(177,0,38)", "rgb(0,0,0)"],
                   dash=["dash", "solid", "dash", "solid"],
                   width=2,
                   asFigure=True)


    # 2. customize figure
    # 2.1 layout
    layout = fig.layout
    layout.height = 350
    layout.margin = {"l": 70, "r": 0,  "t": 20, "b": 40}
    layout.hovermode = "closest"
    layout.hoverdistance = 3

    # 2.2 legend
    legend = layout.legend
    legend.bgcolor = "white"
    legend.bordercolor = "grey"
    legend.borderwidth = 0.5
    legend.xanchor = "left"
    legend.yanchor = "bottom"
    if new_approach:
        legend.x = 0.8
        legend.y = 0.6
    else:
        legend.x = 0.06
        legend.y = 0.15

    # 2.3 disable hover for "upper bound", "goal" and "lower bound" lines
    fig.data[0].hoverinfo = "skip"
    fig.data[1].hoverinfo = "skip"
    fig.data[2].hoverinfo = "skip"

    # 2.4  "actual" line
    # 2.4.1 markers
    scatter = fig.data[3]
    scatter.marker.size = 5
    scatter.marker.line.width = 1
    scatter.marker.color = customize_marker_colors(scatter.x, "black")

    # 2.4.2 hoverinfo
    hovertext_lst = []
    for date_string, weight in zip(scatter.x, scatter.y):
        # determine workday or weekend
        date = pd.to_datetime(date_string)
        day_of_week = date.dayofweek
        if (day_of_week == 5) or (day_of_week == 6):
            day = "Weekend"
        else:
            day = "Workday"

        hovertext = "{}<br>{}kg".format(day, weight)
        hovertext_lst.append(hovertext)

    scatter.hoverinfo = "text+x"
    scatter.hovertext = hovertext_lst

    return fig




def wim_hof_breathing_plot(df):
    # 1. create figure
    fig = df.iplot(mode="lines+markers", 
                   title="Wim Hof Breathing Method", 
                   asFigure=True)
    
    # 2. customize figure
    # 2.1 create area plot
    for scatter_trace in fig.data:
        scatter_trace.fill = "tonexty"
        scatter_trace.marker.size = 5


    # 2.2 axes
    x_axis = fig.layout.xaxis
    y_axis = fig.layout.yaxis
    
    first_date = df.index[0]
    last_date = df.index[-1]
    one_hour = pd.Timedelta(hours=1)
    x_axis.range = [first_date - one_hour, last_date + one_hour]
    x_axis.title = "Date"

    y_axis.tickvals = np.arange(0, 360, 60)
    y_axis.ticktext = np.arange(5)
    y_axis.title = "Breath held in minutes"

    
    # 2.3 hoverinfo
    for scatter_trace in fig.data:
        hovertext_lst = []
        for total_seconds in scatter_trace.y:
            minutes = total_seconds // 60
            seconds = total_seconds - minutes * 60

            hovertext = "{}min {:02}s".format(minutes, seconds)
            hovertext_lst.append(hovertext)

        scatter_trace.hoverinfo = "text+x"
        scatter_trace.hovertext = hovertext_lst
        
    return fig




def youtube_kpi_plot(df, youtube_kpi):
    
    # 1. prepare data and define required variables
    pandas_series = df[youtube_kpi]
    if youtube_kpi == "subscribers":
        pandas_series = pandas_series.cumsum()

        title_y_axis = "Subscriber Count"
        goal = 100000
    else:
        pandas_series = pandas_series.resample("M").sum()
        pandas_series = pandas_series[:-1]                    # exclude last month because it's not a full month

        title_y_axis = "Views per Month"
        goal_ad_revenue_per_month = 2000
        revenue_per_mille = 1 / 1000                          # $1 per 1,000 views
        goal = goal_ad_revenue_per_month / revenue_per_mille  # rpm * views = revenue

    # 2. create figure
    fig = pandas_series.iplot(title="YouTube KPIs",
                              xTitle="Date",
                              yTitle=title_y_axis, 
                              asFigure=True)

    
    # 3. customize figure
    # 3.1 layout
    layout = fig.layout
    layout.height = 400
    layout.margin = {"l": 70, "r": 40, "t": 80, "b": 50}

    # 3.2 legend
    legend = layout.legend
    legend.xanchor = "left"
    legend.yanchor = "bottom"
    legend.x = 0.8
    legend.y = 0.99

    # 3.3 marker
    if youtube_kpi == "views":
        trace_actual = fig.data[0]
        trace_actual.marker.size = 5
        trace_actual.mode = "lines+markers"
    
    return fig