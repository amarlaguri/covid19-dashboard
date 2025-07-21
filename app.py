import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# Load data
df = pd.read_csv('owid-covid-data.csv')

# Preprocessing
df['date'] = pd.to_datetime(df['date'], dayfirst=True)
df = df[df['continent'].notna()]  # Filter out global aggregates

# App initialization
app = dash.Dash(__name__)
server = app.server

# Metric options
metrics = {
    'new_cases': 'New Cases',
    'new_deaths': 'New Deaths',
    'total_cases': 'Total Cases',
    'total_deaths': 'Total Deaths',
    'people_vaccinated': 'People Vaccinated',
    'people_fully_vaccinated': 'Fully Vaccinated'
}

# Layout
app.layout = html.Div([
    html.H1("COVID-19 Data Visualization Dashboard", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Select Country:"),
        dcc.Dropdown(
            id='country-dropdown',
            options=[{'label': c, 'value': c} for c in sorted(df['location'].unique())],
            value='India'
        ),
    ], style={'width': '48%', 'display': 'inline-block'}),

    html.Div([
        html.Label("Select Metric:"),
        dcc.Dropdown(
            id='metric-dropdown',
            options=[{'label': v, 'value': k} for k, v in metrics.items()],
            value='new_cases'
        )
    ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'}),

    html.Div([
        html.Label("Select Date Range:"),
        dcc.DatePickerRange(
            id='date-picker',
            start_date=df['date'].min(),
            end_date=df['date'].max(),
            display_format='YYYY-MM-DD'
        ),
    ], style={'paddingTop': '20px'}),

    html.Div([
        dcc.Checklist(
            id='log-scale',
            options=[{'label': 'Log Scale', 'value': 'log'}],
            value=[]
        ),
        dcc.RadioItems(
            id='view-type',
            options=[
                {'label': 'Daily', 'value': 'daily'},
                {'label': 'Cumulative', 'value': 'cumulative'}
            ],
            value='daily',
            labelStyle={'display': 'inline-block', 'marginRight': '10px'}
        )
    ], style={'paddingTop': '10px'}),

    dcc.Graph(id='covid-graph', style={'height': '600px'})
])


# Callbacks
@app.callback(
    Output('covid-graph', 'figure'),
    Input('country-dropdown', 'value'),
    Input('metric-dropdown', 'value'),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date'),
    Input('log-scale', 'value'),
    Input('view-type', 'value')
)
def update_graph(country, metric, start_date, end_date, log_value, view_type):
    dff = df[df['location'] == country]
    dff = dff[(dff['date'] >= start_date) & (dff['date'] <= end_date)]
    title = f"{metrics[metric]} in {country}"
    y_axis_type = "log" if "log" in log_value else "linear"

    if view_type == 'daily':
        fig = px.line(dff, x='date', y=metric, title=title)
    else:
        dff = dff.sort_values('date')
        dff[metric + '_cumulative'] = dff[metric].cumsum()
        fig = px.line(dff, x='date', y=metric + '_cumulative', title=title)

    fig.update_layout(yaxis_type=y_axis_type)
    return fig


if __name__ == '__main__':
    app.run(debug=True)