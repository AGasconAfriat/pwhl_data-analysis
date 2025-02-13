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
        # season selection div
        html.Div([
            html.H2('Select Year:', style={'margin-right': '2em'}),
            dcc.Dropdown(["2024-2025"], value = "2024-2025" ,id='season')
        ], id="season_select"), # end season selection div
        html.H1('PWHL Player Statistics', 
            style={'textAlign': 'center', 'color': 'black', 'font-size': 56})
    ]), # End top div
    #TODO html.Div for the panel on the left,
    # Main panel div: interactive team dashboard
    html.Div(children=[
        # Top part: team and position selector,
        html.Div(children=[
            html.H2("Select team: "),
            dcc.RadioItems(team_select_list, "MTL", id="team_select", inline=True),
            html.Br(style={"line-height": "5"})
            #TODO position selector
        ]), # End top part
        # Bottow part: graphs and top players
        html.Div(children=[
            html.Div(children=[], id="plot1"),
            html.Div(children=[], id="plot2"),
            html.Div(children=[], id="plot3"),
            html.Div(children=[], id="top_players")
        ]) # End bottom part
    ]) # End main panel div
)# End layout

@app.callback([Output(component_id='plot1', component_property='children'),
               Output(component_id='plot2', component_property='children'),
               Output(component_id='plot3', component_property='children')],
               [Input(component_id='season', component_property='value'),
                Input(component_id='team_select', component_property='value')])
def display_stats(input_season, input_team):
    # create dataframe matching selected settings
    current_df = df[df["team"]==input_team]
    # fig1 age distribution
    min_age=df["age"].min()
    max_age=df["age"].max()
    fig1 = px.histogram(current_df.sort_values("age"), x="age", range_x=[min_age - 1, max_age + 1],
             title="Age Distribution",
             color="age", color_discrete_sequence=px.colors.sequential.Plotly3)
    fig1.update_layout(xaxis_title="age (in years)", yaxis_title="number of players", showlegend=False)
    # fig2 points distribution
    # fig3 penalty minutes
    # return graphs
    return [dcc.Graph(figure=fig1), html.P("testB"), html.P("testC")]

if __name__ == '__main__':
    app.run_server()