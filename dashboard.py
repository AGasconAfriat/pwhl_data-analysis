import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
from dash import no_update
import datetime as dt

# Create variables containing information about the teams
teams = {"BOS": {"name": "Fleet", "location": "Boston", "code": "BOS", "color":"#173f35"},
         "MIN": {"name": "Frost", "location": "Minnesota", "code": "MIN", "color":"#251161"},
         "MTL": {"name": "Victoire", "location": "Montréal", "code": "MTL", "color":"#832434"},
         "NY": {"name": "Sirens", "location": "New York", "code": "NY", "color":"#00bcb5"},
         "OTT": {"name": "Charge", "location": "Ottawa", "code": "OTT", "color":"#a3142f"},
         "TOR": {"name": "Sceptres", "location": "Toronto", "code": "TOR", "color":"#1869b7"}}
team_names = {}
team_locs = {}
team_full_names = {}
for team, team_dict in teams.items():
    team_names[team] = team_dict["name"]
    team_locs[team] = team_dict["location"]
    team_full_names[team] = f"{team_dict['location']} {team_dict['name']}"

# Create function to format lists of strings as text (ex. ["a", "b", "c"] becomes "a, b and c")
def format_list_as_text(list):
    if len(list) == 0:
        return "No result"
    elif len(list) == 1:
        return list[0]
    else:
        text = ""
        for elem in list[:-2]:
            text = text + elem + ", "
        text = text + list[-2] + " and " + list[-1]
        return text

def get_players(assists, goals, count, input_df):
    if count > 5:
        players_ls = f"{count} players"
    else:
        players_ls = input_df[(input_df["assists"]==assists) & (input_df["goals"] == goals)]["name"].to_list()
        players_ls = format_list_as_text(players_ls)
    return players_ls

# Create list of radio items
team_select_list = []
for team, details in teams.items():
    team_select_list.append({"label": details["location"], "value":team})

# Create app
app = dash.Dash(__name__)

# Set the title of the dashboard
app.title = "PWHL Player Statistics"

# Clear the layout and do not display exceptions till callback gets executed
app.config.suppress_callback_exceptions = True

# Read the data into pandas dataframe
df =  pd.read_csv('skater_stats.csv')

# Begin layout
app.layout = (
    html.Div(children=[ # Top div: season selection dropdown and dashboard title
        html.H1('PWHL Player Statistics', 
            style={'textAlign': 'center', 'color': 'black', 'font-size': 56}),
        html.Div([ # season selection div
            html.H2('Select Year:', style={'margin-right': '2em'}),
            dcc.Dropdown(["2024-2025"], value = "2024-2025" ,id='season')
        ], id="season_select", style={"width": "28%"}), # end season selection div
    ], style={"margin-bottom":"1.5em"}), # End top div
    html.Div(children=[ # Left panel div
        html.Div(children=[], id="plotL1", style={"width": "33%", "display":"inline-block"}),
        html.Div(children=[], id="plotL2", style={"width": "33%", "display":"inline-block"}),
        html.Div(children=[], id="plotL3", style={"width": "33%", "display":"inline-block"}),
        html.Div(children=[], id="dateL")
    ]), # End left panel div
    # Main panel div: interactive team dashboard
    html.Div(children=[
        # Top part: team and position selector,
        html.Div(children=[
            html.H2("Select team(s): "),
            dcc.Checklist(options=team_select_list, value=["BOS", "MIN", "MTL", "NY", "OTT", "TOR"], id="team_select", inline=True),
            html.Br(style={"line-height": "5"}),
            dcc.Checklist(options=[{"label":"Forward", "value":"forward"}, {"label":"Defense", "value":"defense"}, {"label":"Goalie", "value":"goalie"}],
                          value=["forward", "defense", "goalie"], id="position_select", inline=True),
            html.Br(style={"line-height": "5"})
        ]), # End top part
        # Bottow part: graphs and top players
        html.Div(children=[
            html.Div(children=[], id="plot1", style={"width": "25%", "display":"inline-block"}),
            html.Div(children=[], id="plot2", style={"width": "25%", "display":"inline-block"}),
            html.Div(children=[], id="plot3", style={"width": "25%", "display":"inline-block"}),
            html.Div(children=[], id="top_players", style={"width": "25%", "display":"inline-block"}))
        ], style={"display":"block"}) # End bottom part
    ]) # End main panel div
)# End layout

@app.callback([Output(component_id='plotL1', component_property='children'),
               Output(component_id='plotL2', component_property='children'),
               Output(component_id='plotL3', component_property='children'),
               Output(component_id='dateL', component_property='children')],
              [Input(component_id='season', component_property='value')])
def display_season_stats(input_season):
    current_df = df # TODO select dataframe matching selected season
    df_ag_rel = pd.DataFrame(current_df[["assists", "goals"]].value_counts()).reset_index()
    # figL1 assists and goals relationship
    # Create a column for the names of the players (or number of players is greater than 5) matching the data
    df_ag_rel["players"] = df_ag_rel.apply(lambda row: get_players(row["assists"], row["goals"], row["count"], current_df), axis=1)
    figL1 = px.scatter(df_ag_rel, x="assists", y="goals", size="count", title="Relationship between assists and goals", hover_data=["players"])
    # figL2 top 10 skaters pie chart
    skaters_only_df = current_df[current_df["position"] != "G"]
    top10 = skaters_only_df.head(10)
    team_df = top10["team"].value_counts().to_frame('counts').reset_index()
    team_df["color"] = team_df.apply(lambda row: teams[row["team"]]["color"], axis=1)
    team_df=team_df.replace(team_locs).rename(columns={'counts': 'count'})
    figL2 = px.pie(team_df, values="count", names="team", title="Distribution of top 10 skaters across teams", color_discrete_sequence=team_df["color"])
    figL2.update_layout(showlegend=False)
    # figL3 points per rookie
    rookie_df = skaters_only_df[skaters_only_df["status"] == "rookie"].groupby("team")["points"].mean().reset_index()     
    rookie_df["color"] = rookie_df.apply(lambda row: teams[row["team"]]["color"], axis=1)
    rookie_df=rookie_df.replace(team_locs).rename(columns={'points': 'points per rookie'})
    figL3 = px.bar(rookie_df, x="team", y="points per rookie", title="Average number of points per rookie skater", color="color",
                   color_discrete_sequence=rookie_df["color"], hover_data={"color":False})
    figL3.update_layout(showlegend=False)
    # TODO file date
    return [dcc.Graph(figure=figL1), dcc.Graph(figure=figL2), dcc.Graph(figure=figL3), html.P("Test file date")]

@app.callback([Output(component_id='plot1', component_property='children'),
               Output(component_id='plot2', component_property='children'),
               Output(component_id='plot3', component_property='children')],
               [Input(component_id='season', component_property='value'),
                Input(component_id='team_select', component_property='value'),
                Input(component_id='position_select', component_property='value')])
def display_stats(input_season, input_teams, input_pos):
    # create dataframe matching selected settings
    current_df = df.loc[df["team"].isin(input_teams)] #TODO take season into account
    current_df = current_df.loc[current_df["position"].isin(input_pos)]
    # fig1 age distribution
    min_age=df["age"].min()
    max_age=df["age"].max()
    fig1 = px.histogram(current_df.sort_values("age"), x="age", range_x=[min_age - 1, max_age + 1],
             title="Age distribution",
             color="age", color_discrete_sequence=px.colors.sequential.Plotly3)
    fig1.update_layout(xaxis_title="age (in years)", yaxis_title="number of players", showlegend=False)
    # fig2 points distribution
    point_data = current_df.groupby(['team', 'position'])['points'].sum().reset_index().replace(team_locs)
    fig2=px.bar(point_data,
        x='team',
        y='points',
        color='position',
        labels={'team': 'teams', 'points': 'total points'},
        title='Point distribution')
    # fig3 player origin
    # return graphs
    return [dcc.Graph(figure=fig1), dcc.Graph(figure=fig2), html.P("To add: player origin map")]

if __name__ == '__main__':
    app.run_server()