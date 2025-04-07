import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

def scrape_stats_page_gbg(url):
    # set up the WebDriver
    driver = webdriver.Edge() #EDIT THIS LINE if not using Edge <<<<<<<<<<<<<<<<<<<< IMPORTANT <<<<<<<<<<<<<<<<<<<<
    # open the webpage
    driver.get(url)
    # wait for the table to load
    try:
        table = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-head-id='player_game_by_game']//table"))
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

def get_element_attributes(element):
    attributes = {}
    for attribute in element.get_property('attributes'):
        attributes[attribute['name']] = attribute['value']
    return attributes

def scrape_name_and_seasons_played(url):
    data_dicts = []
    data = []
    # set up the WebDriver
    driver = webdriver.Edge() #EDIT THIS LINE if not using Edge <<<<<<<<<<<<<<<<<<<< IMPORTANT <<<<<<<<<<<<<<<<<<<<
    # open the webpage
    driver.get(url)
    # wait for the dropdown menu to load
    try:
        # getting season numbers
        select = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, "//select"))
        )
        select = Select(select)
        dropdown_options = select.options
        for option in dropdown_options:
            data_dicts.append(get_element_attributes(option))
        for dict in data_dicts:
            data.append(dict["value"])
        # getting player name
        str1 = "::playerInfo.firstName +' '+ playerInfo.lastName"
        str2 = f'//h1[@ng-bind="{str1}"]'
        name_h1 = driver.find_element(By.XPATH, str2).text
        # getting player position
        pos_span = driver.find_element(By.XPATH, "//span[@ng-bind='playerInfo.position']").text
    finally:
        driver.quit()
    return [name_h1, pos_span, data]

def get_season_stats(player_url, seasons):
    temp_df = pd.DataFrame()
    for s in seasons:
        season_df = scrape_stats_page_gbg(player_url + str(s))
        season_df["season"] = s
        if len(season_df) > 0:
            # ensure the webpage isn’t displaying current season statistics despite saying they are from an earlier season
            date_to_check = season_df.at[0, 1] # first row, second column (second column contains date)
            if not date_to_check in temp_df[1].values:
                temp_df = pd.concat([temp_df, season_df])
    return temp_df

def get_player_gbg(num):
    url = "https://www.thepwhl.com/en/stats/player/" + str(num) + "/"
    name, position, seasons_played = scrape_name_and_seasons_played(url)
    df = get_season_stats(url, seasons_played).dropna()
    df["name"] = name
    df["position"] = position
    return df

df = get_player_gbg(53) # currently gets stats for Ottawa Charge forward Emily Clark

df.columns = ["game", "date", "goals", "assists", "points",
              "plus-minus", "shots", "penalty minutes", "faceoffs", "faceoffs win percentage",
              "power play goals", "short handed goals", "game winning goals", "shootoutgoals", "shootout attempts",
              "time on the ice", "hits", "nothing", "season", "name",
              "position"]
del df["nothing"]

df.to_csv("emily_clark_test.csv")