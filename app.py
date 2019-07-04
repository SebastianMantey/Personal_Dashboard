import numpy as np
import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from plotting_functions import (
    deep_work_plot,
    gantt_chart,
    git_hub_chart,
    time_spent_plot,
    weight_plot,
    wim_hof_breathing_plot,
    youtube_kpi_plot,
)

from helper_functions import determine_current_streak

# 1.  load data
df_youtube_kpis = pd.read_csv("data/youtube_kpis.csv", index_col="date", parse_dates=["date"])
df_video_uploads_2018 = pd.read_csv("data/video_uploads_2018.csv", index_col="date", parse_dates=["date"])
df_video_uploads_2019 = pd.read_csv("data/video_uploads_2019.csv", index_col="date", parse_dates=["date"])
df_deep_work = pd.read_csv("data/deep_work.csv", parse_dates=["date"], index_col="date")
df_habits = pd.read_csv("data/habits.csv", index_col="date", parse_dates=["date"])
df_breathing = pd.read_csv("data/wim_hof_breathing.csv", index_col="date", parse_dates=["date"])

df_time_tracking = pd.read_csv("data/time_tracking.csv", parse_dates=["Start", "Finish", "Date"])
df_time_tracking.Duration = pd.to_timedelta(df_time_tracking.Duration)

df_weight = pd.read_csv("data/weight.csv", index_col="date", parse_dates=["date"])
end_date = "2019-05-31"
start_date = "2019-07-04"
df_weight_old = df_weight.loc[:end_date]
df_weight_new = df_weight.loc[start_date:]

# 2. set some variables
header_image_source = "https://raw.githubusercontent.com/SebastianMantey/Personal_Dashboard/master/header%20image.png"
header_image_height = 38
header_image_width = 0.926 * header_image_height # preserving aspect ratio of image

most_recent_date_time_tracking = df_time_tracking.Date.iloc[-1]
most_recent_date_weight_old = df_weight_old.dropna().index[-1]
most_recent_date_weight_new = df_weight_new.dropna().index[-1]

n_uploaded_videos_2018 = df_video_uploads_2018.values.sum()
n_uploaded_videos_2019 = df_video_uploads_2019.values.sum()
n_uploaded_videos_total = n_uploaded_videos_2018 + n_uploaded_videos_2019

ab_workout_streak = determine_current_streak(df_habits.ab_workout)
cold_shower_streak = determine_current_streak(df_habits.cold_shower)
self_discipline_streak = determine_current_streak(df_habits.self_discipline)
lucid_dreaming_streak = determine_current_streak(df_habits.lucid_dreaming)
omad_streak = determine_current_streak(df_habits.omad)

css_style = {
    "title": {
        "color": "white",
        "background-color": "#3182bd",
        "margin": "0",
        "padding": "5px",
        "border-bottom": "solid thin black",
        "border-radius": "4px"
    },
    
    "title-success": {
        "color": "white",
        "background-color": "#31a354",
        "margin": "0",
        "padding": "5px",
        "border-bottom": "solid thin black",
        "border-radius": "4px"
    },
    
    "title-failure": {
        "color": "white",
        "background-color": "#de2d26",
        "margin": "0",
        "padding": "5px",
        "border-bottom": "solid thin black",
        "border-radius": "4px"
    },
    
    "plotting-area": {
        "border": "solid thin lightgrey",
        "background-color": "#F5F6F9",
        "padding": "10",
        "margin-bottom": "80"
    },
    
    "heading": {
        "text-align": "center",
        "text-decoration": "underline"
    }
}


# 3. dash app
# 3.1 sub-pages
work = [
    # YouTube
    html.H2( 
        style=css_style["title"],
        children="Goal:  100,000 Subscribers on YouTube"
    ),
    dcc.Markdown(
        containerProps={"style": {"margin-bottom": 20}},
        children="""My goal is to reach 100,000 subscribers on my
            [YouTube channel](https://www.youtube.com/channel/UCCtkE-r-0Mvp7PwAvxzSdvw)
            (and [here](https://www.sebastian-mantey.com/blog/why-i-want-to-reach-10000-subscribers-on-youtube) 
            is a blog post why I want to do that). 
            In order to achieve that goal, it is important to consistently upload videos. 
            However, the number of subscribers and the number of uploaded videos are only 
            [lag measures](https://www.franklincovey.com/the-4-disciplines/discipline-2-act.html). 
            Therefore, the actual lead measure, that I am going to focus on, is the amount of 
            [deep work](http://calnewport.com/books/deep-work/)
            that I do on a daily basis. And this is what I’m trying to increase over time.
        """
    ),
    html.Div(
        className="row",
        style=css_style["plotting-area"],
        children=[
            html.Div(
                className="ten columns offset-by-one",
                style={"margin-bottom": 60},
                children=[
                    html.H3(
                        style=css_style["heading"],
                        children="Lag Measures"
                    ),
                    dcc.Graph(id="youtube-kpi-plot"),
                    dcc.RadioItems(
                        id="youtube-kpi-selection",
                        style={
                            "float": "left",
                            "padding-left": 50, 
                        },
                        options=[
                            {"label": "Subscriber Count", "value": "subscribers"},
                            {"label": "Views per Month", "value": "views"} 
                        ],
                        value="subscribers"
                    ),
                    dcc.Graph(
                        id="video-uploads-plot",
                        style={"margin-top": 80}
                    ),
                    dcc.RadioItems(
                        id="video-uploads-year-selection",
                        style={"padding-left": 60},
                        labelStyle={
                            'display': 'inline-block',
                            "padding-left": "2%"
                        },
                        options=[
                            {"label": "2018", "value": "2018"},
                            {"label": "2019", "value": "2019"} 
                        ],
                        value="2019"
                    ),
                    html.Div(
                        className="row",
                        style={"margin-top": 20},
                        children=[
                            html.Div(
                                className="three columns",
                                style={"margin-left": "11%"},
                                children=[
                                    html.P(
                                        style=css_style["heading"],
                                        children="Goal:"     
                                    ),
                                    html.P(
                                        style={"text-align": "center"},
                                        children="100 Videos"     
                                    )
                                ]
                            ),
                            html.Div(
                                className="three columns",
                                style={"margin-left": "11%"},
                                children=[
                                    html.P(
                                        style=css_style["heading"],
                                        children="Currently:"     
                                    ),
                                    html.P(
                                        style={"text-align": "center"},
                                        children="{} Videos".format(n_uploaded_videos_total)   
                                    )
                                ]
                            ),
                            html.Div(
                                className="three columns",
                                style={"margin-left": "11%", "margin-bottom": 40},
                                children=[
                                    html.P(
                                        id="video-uploads-year",
                                        style=css_style["heading"]    
                                    ),
                                    html.P(
                                        id="number-of-uploaded-videos-in-year",
                                        style={"text-align": "center"}    
                                    )
                                ]
                            )
                        ]
                    ),
                    html.H3(
                        style=css_style["heading"],
                        children="Lead Measure"
                    ),
                    dcc.Graph(
                        id="deep-work-plot"
                    ),
                    dcc.RadioItems(
                        id="rolling-average-selection",
                        style={
                            "float": "left",
                            "padding-left": 50, 
                        },
                        options=[
                            {"label": "7-Day Rolling Average", "value": 7},
                            {"label": "30-Day Rolling Average", "value": 30},
                            {"label": "90-Day Rolling Average", "value": 90}
                        ],
                        value=7
                    )
                ]
            )
        ]
    )
]

health = [
    # goal: weight loss
    html.H2(
        style=css_style["title"],
        children="Goal: Average Weight of 85kg"
    ),
    dcc.Markdown(
        containerProps={"style": {"margin-bottom": 20}},
        children="""My goal is to get down to an average weight of 85kg, i.e. there 
            should be a visible six pack.
        """     
    ),
    html.Div(
        className="row",
        style=css_style["plotting-area"],
        children=[
            dcc.Graph(
                id="weight-plot-new",
                className="nine columns",
                figure=weight_plot(df_weight_new, new_approach=True),
                hoverData={"points": [{"x": most_recent_date_weight_new}]}
            ),
            html.Img(
                id="body-image",
                className="three columns"
            )
        ]
    )
]


misc = [
    # Self-Discipline
    html.H2(
        style=css_style["title"],
        children="Self-Discipline"
    ),
    dcc.Markdown(
        containerProps={"style": {"margin-bottom": 20}},
        children=["""I define self-discipline as the ability to discipline yourself to do what you set out to do.
                    And I am going to track that in the following way: The night before, I create a to-do list 
                    with the things that I want to accomplish the next day. And if I am able to check everything 
                    off the list, then I have exercised self-discipline for that day.
        """]
    ),
    html.Div(
        className="row",
        style=css_style["plotting-area"],
        children=[
            dcc.Graph(
                id="self-discipline-plot",
                className="ten columns offset-by-one",
                figure=git_hub_chart(df_habits[["self_discipline"]],
                                     starting_date="2018-12-31",
                                     figure_title = "Habit Tracker: Self-Discipline")
            ),
            html.Div(
                className="row",
                children=[
                    html.Div(
                        className="four columns",
                        style={"margin-left": "15%"},
                        children=[
                            html.P(
                                style=css_style["heading"],
                                children="Goal:"
                            ),
                            html.P(
                                style={"text-align": "center"},
                                children="100 consecutive Days"
                            )
                        ]
                    ),
                    html.Div(
                        className="four columns",
                        style={"margin-left": "15%"},
                        children=[
                            html.P(
                                style=css_style["heading"],
                                children="Current Streak:"
                            ),
                            html.P(
                                style={"text-align": "center"},
                                children="{} Days".format(self_discipline_streak)
                            )
                        ]
                    )
                ]
            )
        ]
    )
]


archive = [
    # Wim Hof Technique
    html.H2(
        style=css_style["title-success"],
        children="Wim Hof Method - Success"
    ),
    dcc.Markdown(
        containerProps={"style": {"margin-bottom": 20}},
        children="""Wim Hof has achieved incredible [feats](https://youtu.be/TM6WKeZ43s4?t=69).
            So, I’m just curious to try out the Wim Hof Method which includes a certain 
            [breathing technique](https://www.youtube.com/watch?v=nzCaZQqAs9I) and cold exposure.
        """     
    ),
    html.Div(
        className="row",
        style=css_style["plotting-area"],
        children=[
            html.Div(
                className="ten columns offset-by-one",
                children=[
                    dcc.Graph(
                        style={"margin-bottom": "20"},
                        figure=wim_hof_breathing_plot(df_breathing)
                    ),
                    dcc.Graph(figure=git_hub_chart(df_habits[["cold_shower"]],
                                                   starting_date="2018-11-04",
                                                   figure_title = "Habit Tracker: Cold Shower")
                    ),
                    html.Div(
                        className="row",
                        children=[
                            html.Div(
                                className="four columns",
                                style={"margin-left": "15%"},
                                children=[
                                    html.P(
                                        style=css_style["heading"],
                                        children="Goal:"
                                    ),
                                    html.P(
                                        style={"text-align": "center"},
                                        children="100 consecutive Days"
                                    )
                                ]
                            ),
                            html.Div(
                                className="four columns",
                                style={"margin-left": "15%"},
                                children=[
                                    html.P(
                                        style=css_style["heading"],
                                        children="Current Streak:"
                                    ),
                                    html.P(
                                        style={"text-align": "center"},
                                        children="{} Days".format(cold_shower_streak)
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    ),
    
    # OMAD
    html.H2(
        style=css_style["title-success"],
        children="OMAD - Success"
    ),
    dcc.Markdown(
        containerProps={"style": {"margin-bottom": 20}},
        children="""OMAD is an intermittent fasting protocoll and it stands for eating just "one meal a day."
        """     
    ),
    html.Div(
        className="row",
        style=css_style["plotting-area"],
        children=[
            dcc.Graph(
                className="ten columns offset-by-one",
                figure=git_hub_chart(df_habits[["omad"]],
                                     starting_date="2018-12-31",
                                     figure_title = "Habit Tracker: OMAD")
            ),
            html.Div(
                className="row",
                children=[
                    html.Div(
                        className="four columns",
                        style={"margin-left": "15%"},
                        children=[
                            html.P(
                                style=css_style["heading"],
                                children="Goal:"
                            ),
                            html.P(
                                style={"text-align": "center"},
                                children="21 consecutive Days"
                            )
                        ]
                    ),
                    html.Div(
                        className="four columns",
                        style={"margin-left": "15%"},
                        children=[
                            html.P(
                                style=css_style["heading"],
                                children="Current Streak:"
                            ),
                            html.P(
                                style={"text-align": "center"},
                                children="{} Days".format(omad_streak)
                            )
                        ]
                    )
                ]
            )
        ]
    ),
    
    # Lucid Dreaming
    html.H2(
        style=css_style["title-success"],
        children="Lucid Dreaming - Success"
    ),
    dcc.Markdown(
        containerProps={"style": {"margin-bottom": 20}},
        children="""To improve my dream recall I want to keep a dream journal where I write down my dreams. 
                    Furthermore, I am going to do reality checks throughout the day in order to be able to
                    induce lucid dreams.
        """     
    ),
    html.Div(
        className="row",
        style=css_style["plotting-area"],
        children=[
            dcc.Graph(
                className="ten columns offset-by-one",
                figure=git_hub_chart(df_habits[["lucid_dreaming"]],
                                     starting_date="2018-12-31",
                                     figure_title = "Habit Tracker: Lucid Dreaming")
            ),
            html.Div(
                className="row",
                children=[
                    html.Div(
                        className="four columns",
                        style={"margin-left": "15%"},
                        children=[
                            html.P(
                                style=css_style["heading"],
                                children="Goal:"
                            ),
                            html.P(
                                style={"text-align": "center"},
                                children="30 consecutive Days"
                            )
                        ]
                    ),
                    html.Div(
                        className="four columns",
                        style={"margin-left": "15%"},
                        children=[
                            html.P(
                                style=css_style["heading"],
                                children="Current Streak:"
                            ),
                            html.P(
                                style={"text-align": "center"},
                                children="{} Days".format(lucid_dreaming_streak)
                            )
                        ]
                    )
                ]
            )
        ]
    ),
    
    # goal: weight loss
    html.H2(
        style=css_style["title-failure"],
        children="Goal: Average Weight of 85kg - Failure"
    ),
    dcc.Markdown(
        containerProps={"style": {"margin-bottom": 20}},
        children="""My goal is to get down to an average weight of 85kg, i.e. there 
            should be a visible six pack. Therefore, I also want to establish 
            the habit of doing a short [ab workout](https://www.youtube.com/watch?v=DHD1-2P94DI)
            right after getting up in the morning.
        """     
    ),
    html.Div(
        className="row",
        style=css_style["plotting-area"],
        children=[
            dcc.Graph(
                id="weight-plot-old",
                className="ten columns offset-by-one",
                figure=weight_plot(df_weight_old),
                hoverData={"points": [{"x": most_recent_date_weight_old}]}
            ),
            html.Div(
                className="ten columns offset-by-one",
                children=[
                    dcc.Graph(
                        style={"margin-top": "60"},
                        figure=git_hub_chart(df_habits[["ab_workout"]],
                                             starting_date="2018-11-04",
                                             figure_title = "Habit Tracker: Morning Ab Workout"),
                    ),
                    html.Div(
                        className="row",
                        children=[
                            html.Div(
                                className="four columns",
                                style={"margin-left": "15%"},
                                children=[
                                    html.P(
                                        style=css_style["heading"],
                                        children="Goal:"
                                    ),
                                    html.P(
                                        style={"text-align": "center"},
                                        children="100 consecutive Days"
                                    )
                                ]
                            ),
                            html.Div(
                                className="four columns",
                                style={"margin-left": "15%"},
                                children=[
                                    html.P(
                                        style=css_style["heading"],
                                        children="Current Streak:"
                                    ),
                                    html.P(
                                        style={"text-align": "center"},
                                        children="{} Days".format(ab_workout_streak)
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    ),
    
    # Daily Schedule
    html.H2(
        style=css_style["title-failure"],
        children="Daily Schedule - Failure"
    ),
    dcc.Markdown(
        containerProps={"style": {"margin-bottom": 20}},
        children="""As Jordan Peterson mentions in [this](https://www.youtube.com/watch?v=OoA4017M7WU)
            video, once you have a vision (in my case reaching 100,000 subscribers on YouTube), 
            you have to ask yourself: What do I have to do on a daily basis to reach that goal?
            So, I created an ideal work-day schedule where I spent 12 hours a day doing something 
            productive. And now, I want to track the percentage of how close I get to that ideal. 
            And then, obviously, I want to improve that over time.
        """     
    ),
    html.Div(
        className="row",
        style=css_style["plotting-area"],
        children=[
            dcc.Graph(
                id="time-spent-plot",
                className="ten columns offset-by-one",
                figure=time_spent_plot(df_time_tracking),
                hoverData={"points": [{"x": most_recent_date_time_tracking}]}
            ),
            html.Div(
                className="ten columns offset-by-one",
                style={"margin-top": "30"},
                children=[
                    dcc.Graph(id="gantt-chart"),
                    dcc.Checklist(
                        id="checkbox-ideal-schedule",
                        style={ "margin-top": 20},
                        options=[{"label": "Show ideal Schedule", "value": "ideal schedule"}],
                        values=[],
                    )
                ]
            )
        ]
    ),
]


# 3.2 actual app
app = dash.Dash(__name__, external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"])
server = app.server

app.layout = html.Div(
    className="container", 
    style={"max-width": "1300px"},
    children=[
        # facilitate multi-page app
        dcc.Location(id="url", refresh=True),
    
        # header
        html.Div(
            className="row",
            children=[
                html.H1(
                    style={"display": "inline-block"},
                    children="Personal Dashboard"
                ),
                html.Div(
                    className="row",
                    style={"float": "right"},
                    children=[
                        html.Img(
                            style={"margin-right": 10},
                            src=header_image_source,
                            height=header_image_height,
                            width=header_image_width
                        ),
                        html.H1(
                            style={"display": "inline-block"},
                            children="Sebastian Mantey"
                        )
                    ]
                )
            ]
        ),

        # buttons to pages
        html.Div(
            className="row",
            style={"margin-bottom": "10"},
            children=[
                dcc.Link(
                    id="work-button",
                    className="button",
                    href="/work",
                    children="work"
                ),
                dcc.Link( 
                    id="health-button",
                    className="button",
                    href="/health",
                    children="health"
                ),
                dcc.Link( 
                    id="misc-button",
                    className="button",
                    href="/misc",
                    children="misc"
                ),
                dcc.Link( 
                    id="archive-button",
                    className="button",
                    style={"margin-left": 50},
                    href="/archive",
                    children="archive"
                )
            ]
        ),

        # container for page content
        html.Div(
            id="page-content",
            className="row"
        ),

        # footer
        dcc.Markdown(
            containerProps={"style": {"text-align": "center"}},
            children="""Built with [Dash](https://plot.ly/products/dash/). 
                Code available at [GitHub](https://github.com/SebastianMantey/Personal_Dashboard).
            """
        )
    ]
)

# 3.3 interactivity of the app
# 3.3.1 navigate pages
@app.callback(Output("page-content", "children"),
             [Input("url", "pathname")])
def show_page(pathname):
    if (pathname == "/work") or (pathname == "/"):
        return work
    if pathname == "/health":
        return health
    if pathname == "/misc":
        return misc
    if pathname == "/archive":
        return archive


# 3.3.2 update style of buttons
@app.callback(Output("work-button", "style"),
             [Input("url", "pathname")])
def update_work_button(pathname):
    if (pathname == "/work") or (pathname == "/"):
        return {"margin-right": "5", "background-color": "grey", "color": "white"}
    else:
        return {"margin-right": "5"}
    

@app.callback(Output("health-button", "style"),
             [Input("url", "pathname")])
def update_health_button(pathname):
    if pathname == "/health":
        return {"margin-right": "5", "background-color": "grey", "color": "white"}
    else:
        return {"margin-right": "5"}
    
    
@app.callback(Output("misc-button", "style"),
             [Input("url", "pathname")])
def update_health_button(pathname):
    if pathname == "/misc":
        return {"margin-right": "5", "background-color": "grey", "color": "white"}
    else:
        return {"margin-right": "5"}
    
@app.callback(Output("archive-button", "style"),
             [Input("url", "pathname")])
def update_archive_button(pathname):
    if pathname == "/archive":
        return {"margin-right": "5", "background-color": "grey", "color": "white", "float": "right"}
    else:
        return {"margin-right": "5", "float": "right"}


# 3.3.3 supress exceptions (see: https://dash.plot.ly/urls)
app.config.suppress_callback_exceptions = True


# 3.3.4 interactivity of plots
@app.callback(Output("youtube-kpi-plot", "figure"),
             [Input("youtube-kpi-selection", "value")])
def update_youtube_kpi_plot(youtube_kpi):
    return youtube_kpi_plot(df_youtube_kpis, youtube_kpi)
        
        
@app.callback(Output("video-uploads-year", "children"),
             [Input("video-uploads-year-selection", "value")])
def display_video_upload_year(year):
    return "{}:".format(year)

@app.callback(Output("number-of-uploaded-videos-in-year", "children"),
             [Input("video-uploads-year-selection", "value")])
def display_n_uploaded_videos_year(year):
    if year == "2018":
        return n_uploaded_videos_2018
    if year == "2019":
        return n_uploaded_videos_2019
    
@app.callback(Output("video-uploads-plot", "figure"),
             [Input("video-uploads-year-selection", "value")])
def update_video_uploads_plot(year):
    if year == "2018":
        figure_title = "Video Uploads {}".format(year)
        return git_hub_chart(df_video_uploads_2018, starting_date="2018-01-01", figure_title=figure_title)
    
    if year == "2019":
        figure_title = "Video Uploads {}".format(year)
        return git_hub_chart(df_video_uploads_2019, starting_date="2018-12-31", figure_title=figure_title)

    
@app.callback(Output("deep-work-plot", "figure"),
             [Input("rolling-average-selection", "value")])
def update_deep_work_plot(rolling_average):
    return deep_work_plot(df_deep_work, rolling_average)

    
@app.callback(Output("body-image", "src"),
             [Input("weight-plot-new", "hoverData")])
def update_body_image(hover_data):
    date = hover_data["points"][0]["x"]
    src = "https://raw.githubusercontent.com/SebastianMantey/helper_repo/master/images/{}.jpg".format(date)
    
    return src


@app.callback(Output("gantt-chart", "figure"),
              [Input("time-spent-plot", "hoverData"),
              Input("checkbox-ideal-schedule", "values")])
def show_daily_schedule(hover_data, checkbox_ideal_schedule):
    if checkbox_ideal_schedule:
        return gantt_chart(df_time_tracking, show_ideal_schedule=True)
    else:
        date = hover_data["points"][0]["x"]
        return gantt_chart(df_time_tracking, date)


if __name__ == '__main__':
    app.run_server(debug=True)