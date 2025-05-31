import pymysql
from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import modin.pandas as pd
import pandas as mpd
import numpy as np
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta

# Load data for the feedback dashboard
data = mpd.read_excel("data.xlsx")
data['date'] = pd.to_datetime(data['date'])
data.set_index('date', inplace=True)

# Vibrant color scheme
colors = {
    'background': '#FFFFFF',
    'text': '#2C3E50',
    'primary': '#1F77B4',
    'secondary': 'rgba(248, 249, 250, 0.5)',
    'accent1': '#2ECC71',
    'accent2': '#E74C3C',
    'accent3': '#9B59B6',
    'accent4': '#F9D923',
    'accent5': '#FF6B6B'
}

# Function to calculate expected days
def get_expected_days(dataframe, column):
    completed = dataframe[column]
    average = completed.mean()
    completed_percent = completed.cumsum().iloc[-1]
    expected_days = np.round((100 - completed_percent) / average)
    plot_value_1 = np.array(completed).cumsum()
    plot_value_2 = np.array([plot_value_1[-1] + average * i for i in range(1, int(expected_days) + 1)])
    curr_day = dataframe.shape[0]
    return expected_days, plot_value_1, plot_value_2, curr_day, completed_percent

# Function to calculate streak
def calculate_streak(dataframe, column, threshold=0):
    streak = 0
    current_streak = 0
    for value in dataframe[column][::-1]:
        if value > threshold:
            current_streak += 1
            streak = max(streak, current_streak)
        else:
            current_streak = 0
    return streak

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
drop_down_unique = data.theme.unique()

# Improved layout for the Dash app
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.Img(src='/assets/logo.png', height="50px"), width=1),
        dbc.Col(html.H1("Professional Domain Dashboard", className="dashboard-title text-center"), width=11)
    ], className="header my-4"),

    dbc.Row([
        dbc.Col(
            dcc.Dropdown(
                id='topic-dropdown',
                options=[{'label': value, 'value': value} for value in drop_down_unique],
                value=drop_down_unique[0],
                clearable=False,
                className='topic-dropdown'
            ),
            width=4
        ),
        dbc.Col(
            dcc.DatePickerRange(
                id='date-range',
                start_date=data.index.min(),
                end_date=data.index.max(),
                display_format='YYYY-MM-DD'
            ),
            width=8
        )
    ], className="mb-4"),

    dbc.Row(id='kpi-container', className="mb-4"),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Project Progress Timeline"),
                dbc.CardBody([
                    dcc.Graph(id='line-chart'),
                    html.Div(id='line-chart-explanation', className="mt-2 text-muted")
                ])
            ], className="shadow")
        ], width=12, className="mb-4"),
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Overall Completion Status"),
                dbc.CardBody([
                    dcc.Graph(id='pie-chart'),
                    html.Div(id='pie-chart-explanation', className="mt-2 text-muted")
                ])
            ], className="shadow")
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Daily Completion Percentage"),
                dbc.CardBody([
                    dcc.Graph(id='bar-chart'),
                    html.Div(id='bar-chart-explanation', className="mt-2 text-muted")
                ])
            ], className="shadow")
        ], width=6),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Weekly Progress Overview"),
                dbc.CardBody([
                    dcc.Graph(id='area-chart'),
                    html.Div(id='area-chart-explanation', className="mt-2 text-muted")
                ])
            ], className="shadow")
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("User Engagement by Day of Week"),
                dbc.CardBody([
                    dcc.Graph(id='bubble-chart'),
                    html.Div(id='bubble-chart-explanation', className="mt-2 text-muted")
                ])
            ], className="shadow")
        ], width=6),
    ], className="mb-4"),

], fluid=True, style={'backgroundColor': colors['background'], 'color': colors['text'], 'padding': '20px'})


# SQL Authentication class
class MySQLAuthentication:
    def __init__(self):
        self.password = None
        self.user_name = None
        try:
            self.new_db = pymysql.connect(host='localhost', user='newuser', password='Jack(022)', database='user_db')
            self.cursor = self.new_db.cursor()
        except Exception:
            print('Error while connecting to the database')
            print('Welcome!..')

    def password_check(self, password):
        isCap = isLower = isNum = isSpecial = False
        upper = "".join([chr(i) for i in range(65, 91)])
        lower = "".join([chr(i) for i in range(97, 123)])
        special = "".join([chr(i) for i in range(33, 48)])
        numbers = "".join([chr(i) for i in range(48, 58)])

        for i in password:
            if i in upper:
                isCap = True
            elif i in lower:
                isLower = True
            elif i in special:
                isSpecial = True
            elif i in numbers:
                isNum = True
            else:
                print('Password contains invalid character')
                return False
        if not isCap:
            print('Password must contain one upper case letter')
            return False
        elif not isLower:
            print('Password must contain one lower case letter')
            return False
        elif not isNum:
            print('Password must contain one number')
            return False
        elif not isSpecial:
            print('Password must contain a special character')
            return False
        elif len(password) < 8:
            print('Password must have a length of at least 8 characters')
            return False
        else:
            print('Password created successfully')
            return True

    def sign_up(self):
        user_name = input("Please enter the username: ")
        while True:
            no_of_rows = self.cursor.execute(f"SELECT user_name FROM user_table WHERE user_name='{user_name}'")
            if no_of_rows:
                print("Username already exists")
                user_name = input("Please enter the username: ")
            else:
                self.user_name = user_name
                break
        pass_word = input("Please enter the password: ")
        while True:
            if self.password_check(pass_word):
                self.password = pass_word
                break
            else:
                pass_word = input("Please enter the password: ")
        self.cursor.execute(f"INSERT INTO user_table (user_name, password_) VALUES ('{user_name}', '{pass_word}')")
        self.new_db.commit()
        print("User registered successfully")

    def sign_in(self):
        user_name = input("Please enter the username: ")
        pass_word = input("Please enter the password: ")
        while True:
            no_of_rows = self.cursor.execute(f"SELECT * FROM user_table WHERE user_name='{user_name}' AND password_='{pass_word}'")
            if no_of_rows:
                print("You're signed in")
                break
            else:
                print("Invalid entry")
                user_name = input("Please enter the username: ")
                pass_word = input("Please enter the password: ")

    def total_recent_user(self):
        return self.cursor.execute('SELECT * FROM user_table WHERE last_sign_up > DATE_SUB(CURDATE(), INTERVAL 1 MONTH);')

    def total_user(self):
        return self.cursor.execute('SELECT * FROM user_table;')


# Create an instance of MySQLAuthentication
msa = MySQLAuthentication()

@app.callback(
    [Output('line-chart', 'figure'),
     Output('pie-chart', 'figure'),
     Output('bar-chart', 'figure'),
     Output('area-chart', 'figure'),
     Output('bubble-chart', 'figure'),
     Output('kpi-container', 'children'),
     Output('line-chart-explanation', 'children'),
     Output('pie-chart-explanation', 'children'),
     Output('bar-chart-explanation', 'children'),
     Output('area-chart-explanation', 'children'),
     Output('bubble-chart-explanation', 'children')],
    [Input('topic-dropdown', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_graphs(selected_topic, start_date, end_date):
    new_data = data[(data['theme'] == selected_topic) & 
                    (data.index >= start_date) & 
                    (data.index <= end_date)]
    expected_days, actual, predicted, curr_day, completed_percent = get_expected_days(new_data, 'percentage_completed_today')

    # Calculate streak
    streak = calculate_streak(new_data, 'percentage_completed_today', threshold=0)

    # KPI indicators
    total_users = msa.total_user()
    recent_users = msa.total_recent_user()

    kpi_cards = [
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H4("Total Users", className="card-title"),
                    html.P(f"{total_users:,}", className="card-text h2")
                ])
            ], color=colors['accent1'], inverse=True, className="shadow-lg")
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H4("Recent Users", className="card-title"),
                    html.P(f"{recent_users:,}", className="card-text h2")
                ])
            ], color=colors['accent2'], inverse=True, className="shadow-lg")
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H4("Completion Rate", className="card-title"),
                    html.P(f"{completed_percent:.1f}%", className="card-text h2")
                ])
            ], color=colors['accent4'], inverse=True, className="shadow-lg")
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H4("Current Streak 🔥", className="card-title"),
                    html.P(f"{streak} days", className="card-text h2")
                ])
            ], color=colors['accent3'], inverse=True, className="shadow-lg")
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H4("Avg. Daily Progress", className="card-title"),
                    html.P(f"{new_data['percentage_completed_today'].mean():.2f}%", className="card-text h2")
                ])
            ], color=colors['accent5'], inverse=True, className="shadow-lg")
        )
    ]

    # 1. Improved Line chart
    fig_1 = go.Figure()
    fig_1.add_trace(go.Scatter(x=list(range(1, curr_day + 1)), y=actual, mode='lines+markers', name='Actual', line=dict(color=colors['accent1'], width=3)))
    fig_1.add_trace(go.Scatter(x=list(range(curr_day+1, curr_day + len(predicted))), y=predicted, mode='lines', name='Expected', line=dict(color=colors['accent3'], width=3, dash='dot')))
    fig_1.update_layout(
        xaxis_title='Days',
        yaxis_title='Cumulative Completion (%)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor=colors['secondary'],
        paper_bgcolor=colors['background'],
        font=dict(color=colors['text']),
        margin=dict(l=40, r=40, t=40, b=40),
        hovermode="x unified"
    )
    fig_1.update_traces(hovertemplate='Day: %{x}<br>Completion: %{y:.2f}%')

    # 2. Improved Pie chart
    fig_2 = go.Figure(data=[go.Pie(
        labels=["Completed", "Remaining"], 
        values=[completed_percent, 100 - completed_percent], 
        hole=.6,
        marker=dict(colors=[colors['accent1'], colors['accent2']]),
        textinfo='label+percent',
        hoverinfo='label+value+percent',
        textfont_size=14,
        pull=[0.1, 0]
    )])
    fig_2.update_layout(
        annotations=[dict(text=f'{completed_percent:.1f}%', x=0.5, y=0.5, font_size=20, showarrow=False)],
        plot_bgcolor=colors['secondary'],
        paper_bgcolor=colors['background'],
        font=dict(color=colors['text']),
        margin=dict(l=40, r=40, t=40, b=40)
    )

    # 3. Improved Bar chart
    fig_3 = go.Figure(data=[go.Bar(
        x=new_data.index, 
        y=new_data['percentage_completed_today'], 
        marker_color=colors['accent3'],
        hovertemplate='Date: %{x}<br>Completion: %{y:.2f}%'
    )])
    fig_3.update_layout(
        xaxis_title='Date',
        yaxis_title='Completion Percentage',
        plot_bgcolor=colors['secondary'],
        paper_bgcolor=colors['background'],
        font=dict(color=colors['text']),
        margin=dict(l=40, r=40, t=40, b=40),
        bargap=0.2
    )
    fig_3.add_hline(y=new_data['percentage_completed_today'].mean(), line_dash="dash", line_color=colors['accent1'], annotation_text="Average", annotation_position="top right")

    # 4. Improved Area chart: Weekly Progress
    weekly_data = new_data.resample('W')['percentage_completed_today'].sum()
    fig_4 = go.Figure(data=[go.Scatter(
        x=weekly_data.index, 
        y=weekly_data.values, 
        fill='tozeroy',
        fillcolor=colors['accent4'] ,  # 50% opacity
        line=dict(color=colors['accent4'], width=2),
        mode='lines+markers',
        marker=dict(size=8, color=colors['accent1']),
        hovertemplate='Week: %{x}<br>Weekly Progress: %{y:.2f}%'
    )])
    fig_4.update_layout(
        xaxis_title='Week',
        yaxis_title='Weekly Progress (%)',
        plot_bgcolor=colors['secondary'],
        paper_bgcolor=colors['background'],
        font=dict(color=colors['text']),
        margin=dict(l=40, r=40, t=40, b=40)
    )

    # 5. Improved Bubble chart: User Engagement
    user_engagement = new_data.groupby(new_data.index.dayofweek)['percentage_completed_today'].agg(['mean', 'count'])
    user_engagement['day'] = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    fig_5 = go.Figure(data=[go.Scatter(
        x=user_engagement['day'],
        y=user_engagement['mean'],
        mode='markers',
        marker=dict(
            size=user_engagement['count'],
            sizemode='area',
            sizeref=2.*max(user_engagement['count'])/(40.**2),
            sizemin=4,
            color=user_engagement['mean'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Avg. Completion")
        ),
        text=user_engagement['count'],
        hovertemplate='Day: %{x}<br>Avg. Completion: %{y:.2f}%<br>Users: %{text}'
    )])
    fig_5.update_layout(
        xaxis_title='Day of Week',
        yaxis_title='Average Daily Completion (%)',
        plot_bgcolor=colors['secondary'],
        paper_bgcolor=colors['background'],
        font=dict(color=colors['text']),
        margin=dict(l=40, r=40, t=40, b=40)
    )

    # Explanations
    line_chart_explanation = html.P([
        "This chart illustrates the project's cumulative progress over time. The ",
        html.Strong("pink line with markers"), " shows actual progress, while the ",
        html.Strong("green dotted line"), " projects expected future progress based on the current rate. ",
        f"At the current pace, the project is estimated to complete in {int(expected_days)} more days."
    ])

    pie_chart_explanation = html.P([
        "This chart provides a clear overview of the overall project completion status. ",
        html.Strong(f"{completed_percent:.1f}%"), " of the project has been completed, ",
        f"with {100-completed_percent:.1f}% remaining. The pulled-out slice emphasizes the completed portion."
    ])


    bar_chart_explanation = html.P([
        "This chart displays the daily completion percentage, allowing you to identify high and low productivity days. ",
        "The ", html.Strong("red dashed line"), f" indicates the average daily progress of {new_data['percentage_completed_today'].mean():.2f}%. ",
        "Bars above this line represent days with above-average progress."
    ])

    area_chart_explanation = html.P([
        "This area chart showcases the weekly progress over time. Each point represents the total progress made in a week, ",
        "with the area under the curve filled to emphasize cumulative progress. This view helps identify trends and patterns in weekly productivity."
    ])

    bubble_chart_explanation = html.P([
        "This bubble chart visualizes user engagement patterns throughout the week. ",
        "The size of each bubble represents the number of users active on that day, while the color indicates the average completion percentage. ",
           "This chart helps identify which days of the week see the highest user activity and productivity."
    ])

    return fig_1, fig_2, fig_3, fig_4, fig_5, kpi_cards, line_chart_explanation, pie_chart_explanation, bar_chart_explanation, area_chart_explanation, bubble_chart_explanation

if __name__ == '__main__':
    app.run_server(debug=True)
