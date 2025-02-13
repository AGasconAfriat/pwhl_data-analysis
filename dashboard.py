import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
from dash import no_update
import datetime as dt

teams = {"BOS": {"name": "Fleet", "location": "Boston", "code": "BOS", "color":"#173f35"},
         "MIN": {"name": "Frost", "location": "Minnesota", "code": "MIN", "color":"#251161"},
         "MTL": {"name": "Victoire", "location": "Montréal", "code": "MTL", "color":"#832434"},
         "NY": {"name": "Sirens", "location": "New York", "code": "NY", "color":"#00bcb5"},
         "OTT": {"name": "Charge", "location": "Ottawa", "code": "OTT", "color":"#a3142f"},
         "TOR": {"name": "Sceptres", "location": "Toronto", "code": "TOR", "color":"#1869b7"}}

# Create list of radio items
team_select_list = []
for team, details in teams.items():
    team_select_list.append({"label": details["location"], "value":team})

# Create app
app = dash.Dash(__name__)

# Clear the layout and do not display exceptions till callback gets executed
app.config.suppress_callback_exceptions = True

# Read the data into pandas dataframe
df =  pd.read_csv('skater_stats.csv')

# Begin layout
app.layout = (
    # Top div: season selection dropdown and dashboard title
    html.Div(children=[
        #TODO dropdown,
        html.H1('PWHL Player Statistics', 
            style={'textAlign': 'center', 'color': 'black', 'font-size': 56})
    ]), # End top div
    #TODO html.Div for the panel on the left,
    # Main panel div: interactive team dashboard
    html.Div(children=[
        # Top part: team and position selector,
        html.Div(children=[
            html.H2("Select team: "),
            dcc.RadioItems(team_select_list, "MTL", inline=True),
            html.Br(style={"line-height": "5"})
            #TODO position selector
        ]) # End top part
        #TODO bottow part: graphs and top players
    ]) # End main panel div
)# End layout

if __name__ == '__main__':
    app.run_server()