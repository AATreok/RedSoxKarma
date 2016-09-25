import urllib.request
from bs4 import BeautifulSoup
import datetime

rs_abr = "BOS"

now = datetime.datetime.now()
urlyear = "year_" + str(now.year)
urlmonth = "month_" + str(now.month).zfill(2)
urlday = "day_" + str(now.day - 1).zfill(2)
url = 'http://gd2.mlb.com/components/game/mlb/'
url = url + urlyear + "/" + urlmonth + "/" + urlday + "/miniscoreboard.xml"
print("Connecting to url: " + url)
with urllib.request.urlopen(url) as response:
    xml = response.read()

soup = BeautifulSoup(xml, 'xml')
tags = soup.findAll('game',{"away_file_code":"bos"})
index1 = 0
for game_info in tags:
    print(index1)
    index1+=1
    if game_info['status'] == 'Final':
        print('Game is finalized!')
        if game_info['away_team_runs'] > game_info['home_team_runs']:
            print('THE BOSTON RED SOX WON!')
            print('Final score: Red Sox ' + game_info['away_team_runs'] + ' ' + game_info['home_team_name'] + ' ' + game_info[
                'home_team_runs'])
    #for game_info in subtag:
    #    print(game_info)
    #    if game_info == "game ampm":
    #        print(game_info)

    #if subtag == 'away_name_abbrev':

    #    print(tags['home_name_abbrev'])
