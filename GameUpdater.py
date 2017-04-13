import urllib.request
import urllib.error
import datetime
from bs4 import BeautifulSoup

# -1 --> error, check for multiple errors and send notice if problem persists for over 1>hr
# 0 --> no game, wait until next day
# 1 --> Red Sox won (home or away)
# 2 --> Red Sox lost, wait until next GAME (not day, in case doublheader)
# 4 --> continue, game in progress
class GameResult:
    def __init__(self, code_result='Unknown',
                 team_name='Unknown', opponent='Unknown',
                 score_rs='Unknown', score_opp='Unknown', game_date='Unknown'):
        self.code_result = code_result
        self.team_name = team_name
        self.opponent = opponent
        self.score_rs = score_rs
        self.score_opp = score_opp
        self.game_date = game_date


def cur_scoreboard_status():
    base_url = 'http://gd2.mlb.com/components/game/mlb/'
    current_time = datetime.datetime.now()
    current_url = base_url + f'year_{current_time.year}/month_' \
                             f'{current_time.month:02d}/day_{current_time.day}' \
                             f'/master_scoreboard.xml'

    # intentionally left blank- game time decided after scoreboard is checked
    gameresult = GameResult()

    print(current_url)
    try:
        with urllib.request.urlopen(current_url) as response:
            webpage = response.read()
    except (urllib.error.HTTPError, urllib.error.URLError, Exception) as e:
        print("HTTPError message " + str(e))
        gameresult.code_result = -1
        return gameresult

    team_abr = 'bos'
    soup = BeautifulSoup(webpage, 'xml')
    tags = soup.findAll('game', {'away_file_code': team_abr})
    if (tags == []):
        print("Team is home")
        #this is only looking at the 'game' filings
        tags = soup.findAll('game', {'home_file_code': team_abr})
        print(tags[0].attrs)

    else:
        print("Team is away")
    #print(tags)
    #print(soup)



if __name__ == '__main__':
    cur_scoreboard_status();