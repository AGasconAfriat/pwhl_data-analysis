# ----- SETUP ----- ----- ----- ----- ----- ----- -----
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ----- CONSTANTS ----- ----- ----- ----- ----- ----- -----
# Canada: list of province and territory codes
can_locs = ["AB", "BC", "MB", "NB", "NL", "NT", "NS", "NU", "ON", "PE", "QC", "SK", "YT"]
# United States
usa_locs = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL",
            "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME",
            "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
            "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
            "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI",
            "WY"]
number_of_seasons = 5
# ----- FUNCTIONS ----- ----- ----- ----- ----- ----- -----
def scrape_stats_page(url):
    # set up the WebDriver
    driver = webdriver.Edge() #EDIT THIS LINE if not using Edge <<<<<<<<<<<<<<<<<<<< IMPORTANT <<<<<<<<<<<<<<<<<<<<
    # open the webpage
    driver.get(url)
    # wait for the table to load
    try:
        table = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, '//table'))
        )
        rows = table.find_elements(By.TAG_NAME, 'tr')
        data = []
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, 'td')
            data.append([col.text for col in cols])
        df = pd.DataFrame(data)
    finally:
        driver.quit()
    return df
def get_country_code(code):
    if code in can_locs:
        return "CAN"
    elif code in usa_locs:
        return "USA"
    return code
def calculate_age(birthdate_str): # age in years, rounded down
    birthdate = pd.to_datetime(birthdate_str)
    today = pd.to_datetime('today')
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age
def parse_url_code(url_code, index, season=0):
    return url_code.replace("<index>", str(index)).replace("<season>", str(season))
def scrape_page_list(url_code, n, n_seasons=1): # any part of an url meant to be replaced by the index or season should be "<index>" or "<season>"
                                                # n is the number of pages to scrape
    temp_df = pd.DataFrame()
    for s in range(1, n_seasons + 1):
        for i in range(1, n + 1):
            page_df = scrape_stats_page(parse_url_code(url_code, i, s))
            if n_seasons !=1:
                page_df["season"] = s
            temp_df = pd.concat([temp_df, page_df])
    return temp_df
# ----- WEBSCRAPING ----- ----- ----- ----- ----- ----- -----
df = scrape_page_list("https://www.thepwhl.com/en/stats/player-stats/all-teams/5?sort=points&playertype=skater&position=skaters&rookie=no&statstype=expanded&page=<index>&league=1", 8, number_of_seasons)
det_df = scrape_page_list("https://www.thepwhl.com/en/stats/roster/<index>/5?league=1", 6) # details pages only list the current members of each team

# ----- DATA WRANGLING ----- ----- ----- ----- ----- ----- -----
# statistics dataframe
df.columns = ["rank", "status", "photo", "name", "position",
              "team", "games played", "goals", "assists", "points",
              "plus/minus", "penalty minutes", "power play goals", "power play assists", "short handed goals",
              "shots", "short handed assists", "game winning goals", "first goals", "insurance goals",
              "overtime goals", "unassisted goals", "empty net", "shooting percentage", "shootout goals",
              "shots in shootouts", "shootout winning goals", "shootout percentage", "nothing", "season"]
df.drop(columns=["photo", "nothing", "position"], inplace=True) #photo and nothing are just blank spaces in the table; the photos are loaded separately
                                                                #the position is covered by the details dataframe
df["name"] = df["name"].str.replace(" +", "") # Removing " +" at the end of the names of players who switched teams

# details dataframe
det_df.columns = ["jersey number", "name", "position", "shoots", "date of birth", "hometown", "nothing"]
det_df.drop(columns=["nothing"], inplace=True) #this one is just blank space in the table
det_df.dropna(inplace = True) #removing blank lines
# merged dataframe
skaters_df = df.merge(det_df, on="name", how="left")
# Drop rows that are fully blank (ignoring if the season has a value)
skaters_df = skaters_df.dropna(subset=[col for col in skaters_df.columns if col != "season"])
skaters_df[['hometown','hometown location']] = skaters_df["hometown"].str.split(", ", expand=True)
# making text values clearer
pd.options.mode.copy_on_write = True
is_rookie = (skaters_df["status"] == "*")
is_inactive = (skaters_df["status"] == "x")
skaters_df.loc[is_rookie, "status"] = "rookie"
skaters_df.loc[is_inactive, "status"] = "inactive"
forward = skaters_df["position"].isin(["F", "RW", "C", "LW"])
defense = skaters_df["position"].isin(["D", "RD", "LD"])
goalie = (skaters_df["position"] == "G")
skaters_df.loc[forward, "position"] = "forward"
skaters_df.loc[defense, "position"] = "defense"
skaters_df.loc[goalie, "position"] = "goalie"
left = (skaters_df["shoots"] == "L")
right = (skaters_df["shoots"] == "R")
skaters_df.loc[left, "shoots"] = "left"
skaters_df.loc[right, "shoots"] = "right"
# creating a row for the home country
skaters_df["home country"] = skaters_df.apply(lambda row: get_country_code(row["hometown location"]), axis = 1)
# create a row for the age in years
skaters_df["age"] = skaters_df.apply(lambda row: calculate_age(row["date of birth"]), axis = 1)
# ----- FILE ----- ----- ----- ----- ----- ----- -----
skaters_df.to_csv("full_stats.csv", index=False)

# ----- USER MESSAGE ----- ----- ----- ----- ----- ----- -----
print("Step 1 complete.")