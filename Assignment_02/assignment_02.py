from selenium import webdriver
from selenium.webdriver.support.select import Select
import bs4
import pandas as pd
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import random
import time


def extract_stats_data(driver):
    normal_delay = random.normalvariate(2, 0.5)
    #     driver = webdriver.Chrome(executable_path=r'chromedriver')
    #     driver.get('http://www.mlb.com')
    #     wait = WebDriverWait(driver, 10)

    #     stats_header_bar = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'megamenu-navbar-overflow__menu-item--stats')))

    time.sleep(normal_delay)
    data_div = driver.find_element_by_id('datagrid')
    data_html = data_div.get_attribute('innerHTML')

    soup = bs4.BeautifulSoup(data_html)

    head = [t.text.replace('▲', "").replace('▼', "") for t in soup.thead.find_all('th')]

    head = [t for t in head if t != ""]
    print(len(head))

    whole = []
    for t1 in soup.tbody.find_all('tr'):
        row = []
        for t2 in t1.find_all('td'):
            row.append(t2.text.replace("\xa0", ""))

        row = row[:3] + row[5:]  # for player
        #         row = row[:2]+row[3:]
        whole.append(row)

    df = pd.DataFrame(whole, columns=head)
    return df


def click_next_page_for_stats(driver):
    try:
        pagination_div = driver.find_element_by_class_name("paginationWidget-next")
        pagination_div.click()
        return True
    except:
        return False


def get_op(row):
    if row['AwayTeam'] == 'HOU':
        return row['HomeTeam']
    else:
        return row['AwayTeam']


# ### get data from stats
# driver = webdriver.Chrome(executable_path=r'chromedriver')
# _ = True
# page = 1
# while _:
#     time.sleep(2)
#     data = extract_stats_data(driver)
#     
#     if page != 1:
#         data_pre = pd.concat([data_pre,data])
#     else:
#         data_pre = data
#     
#     page+=1
#     _ = click_next_page_for_stats(driver)

# q5_data = pd.read_csv('Question_5.csv')

# people = list(q5_data['Player'])

# home = []
# for p in people:
#     a = driver.find_element_by_link_text(p)
#     a.click()
#     time.sleep(1)
#     a = driver.find_elements_by_class_name('player-bio')[0]
#     b = a.find_elements_by_tag_name('li')    
#     home.append([t.text for t in b if 'Born' in t.text])
#     driver.back()
# home = [t[0] for t in home]


# a = driver.find_elements_by_class_name('player-bio')[0]
# b = a.find_elements_by_tag_name('li') 

# home = [t.split(' in')[1] for t in home]

# home = [t.split(', ')[1] for t in home]

############# Get game schedule data########################## 
############# ############# ############# ############# ######


# import http.client, urllib.request, urllib.parse, urllib.error, base64

# headers = {
#     # Request headers
#     'Ocp-Apim-Subscription-Key': 'd62a01e46a434ae493698f01da81fbad',
# }

# params = urllib.parse.urlencode({'format':'JSON','season':'2016'})

# try:
#     conn = http.client.HTTPSConnection('api.fantasydata.net')
#     conn.request("GET", "/v3/mlb/stats/JSON/Games/2016" , "{body}", headers)
#     response = conn.getresponse()
#     data = response.read()
#     print(data)
#     conn.close()
# except Exception as e:
#     print("[Errno {0}] {1}".format(e.errno, e.strerror))

# schedule_data = json.loads(data.decode('utf-8'))
# whole_schedule = []
# for game in schedule_data:
#     if game['AwayTeam'] == 'HOU' or game['HomeTeam'] =='HOU':
#         single_game = []
#         single_game.append(game['AwayTeam'])
#         single_game.append(game['HomeTeam'])
#         single_game.append(game['Day'])
#         single_game.append(game['StadiumID'])
#         whole_schedule.append(single_game)
# q6_data = pd.DataFrame(whole_schedule,columns=['AwayTeam','HomeTeam','Day','StadiumID'])
# q6_data.to_csv('Question_6_1.csv',index=False)

# ########## get stadium name############

# headers = {
#     # Request headers
#     'Ocp-Apim-Subscription-Key': 'd62a01e46a434ae493698f01da81fbad',
# }

# params = urllib.parse.urlencode({
# })

# try:
#     conn = http.client.HTTPSConnection('api.fantasydata.net')
#     conn.request("GET", "/v3/mlb/scores/json/Stadiums" , "{body}", headers)
#     response = conn.getresponse()
#     data = response.read()

#     conn.close()
# except Exception as e:
#     print("[Errno {0}] {1}".format(e.errno, e.strerror))
# stadium_data = json.loads(data.decode('utf-8'))
# whole_stadium = []
# for sta in stadium_data:
#     single_stadium=[]
#     single_stadium.append(sta['StadiumID'])
#     single_stadium.append(sta['City'])
#     single_stadium.append(sta['State'])
#     whole_stadium.append(single_stadium)
# sta_data = pd.DataFrame(whole_stadium,columns=['StadiumID','City','State'])
# sta_data.to_csv('Question_6_2.csv',index=False)


# 1.Which team had the most homeruns in the regular season of 2015? Print the full team name.


q1_data = pd.read_csv('Question_1.csv')

team = q1_data.sort_values(['HR'], ascending=False).iloc[0]['Team']
print('Question 1')
print(str(team), ' had the most homeruns in the regular season of 2015.')
print('\n')

# 2.Which league (AL or NL) had the greatest average number of homeruns… a) in the regular season of 2015? 
# Please give the league name and the average number of homeruns. b) in the regular season of 2015 in 
# the first inning? Please give the league name and the average number of homeruns.

q2_data = pd.read_csv('Question_2.csv')
q2b_data = pd.read_csv('Question_2b.csv')
print('Question 2')
print(q2_data.groupby('League').HR.mean().reset_index())
print('AL had the greatest average number of homeruns in the regular season of 2015.')
print('\n')
print(q2b_data.groupby('League').HR.mean().reset_index())
print('AL had the greatest average number of homeruns in the regular season of 2015 in  the first inning')
print('\n')

# 3.What is the name of the player with the best overall batting average in the 2017 regular season that
# played for the New York Yankees, who a) had at least 30 at bats? Please give his full name and position.
# b) played in the outfield (RF, CF, LF)? Please give his full name and position.
q3_data = pd.read_csv('Question_3.csv')

q3_data = q3_data[q3_data['Team'] == 'NYY']
q3_data = q3_data.sort_values('AVG', ascending=False)
print('Question 3')
print(q3_data[q3_data['AB'] > 30].iloc[0][['Player', 'Pos']],
      "is the player with the best overall batting average in the 2017 regular season that played for the New York Yankees, who had at least 30 at bats")
print('\n')
print(q3_data[q3_data['Pos'].isin(['RF', 'CF', 'LF'])][['Player', 'Pos']].iloc[0],
      "is the player with the best overall batting average in the 2017 regular season that played for the New York Yankees in the outfield.")
print('\n')
# 4 Which player in the American League had the most at bats in the 2015 regular season? Please give his
# full name, full team name, and position.
q4_data = pd.read_csv('Question_4.csv')
print('Question 4')
print(q4_data.sort_values('AB', ascending=False)[['Player', 'Pos']].iloc[0],
      "had the most at bats in the 2015 regular season in the American League")
print('\n')
# 5 Which players from the 2014 All-star game were born in Latin America (google a country list)? 
# Please give their full name and the full name of the team they play for.
q5_data = pd.read_csv('Question_5_2.csv')
latin_countries = ['Argentina', 'Bolivia', 'Bolivia', 'Chile', 'Colombia', 'Costa Rica', 'Cuba', 'Dominican Republic',
                   'Ecuador', 'El Salvador', 'French Guiana', 'Guadeloupe', 'Guatemala', 'Haiti', 'Honduras',
                   'Martinique', 'Mexico', 'Nicaragua', 'Panama', 'Paraguay', 'Peru', 'Puerto Rico', 'Saint Barthélemy',
                   'Saint Martin', 'Uruguay', 'Venezuela']

q5_data['Latin or not'] = q5_data['Home'].apply(lambda x: 1 if x in latin_countries else 0)
print('Question 5')
print(q5_data[['People', 'Team']][q5_data['Latin or not'] == 1])
print('\n')

# 6. Please print the 2016 regular season schedule for the Houston Astros in chronological order.
# Each line printed to the screen should be in the following format:
#     <opponent Team Name> <game date> <stadium name> <city>, <state>
print('Question 6')
q6_data_1 = pd.read_csv('Question_6_1.csv')

q6_data_1.head()

q6_data_2 = pd.read_csv('Question_6_2.csv')

q6_data_2.head()

q6_data = pd.merge(left=q6_data_1, right=q6_data_2, on='StadiumID')

q6_data.head()

q6_data['Opponent'] = q6_data.apply(get_op, axis=1)

q6_data = q6_data.drop(['AwayTeam', 'HomeTeam'], axis=1)

q6_data = q6_data[['Opponent', 'Day', 'StadiumID', 'City', 'State']]
print(q6_data)

