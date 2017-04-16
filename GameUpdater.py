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
    def __init__(self, code_result='Unknown', team_name='Unknown',
                 opponent='Unknown', score_rs='Unknown', score_opp='Unknown',
                 game_date='Unknown', home=False):
        self.code_result = code_result
        self.team_name = team_name
        self.opponent = opponent
        self.score_rs = score_rs
        self.score_opp = score_opp
        self.game_date = game_date
        self.home = home


def create_game_result(gameresult, game_info, team_abbr, file_code):
    if
    gameresult.team_name = game_info.

# Assumptions made:
# 1. A doubleheader on the same d
def cur_scoreboard_status():
    game_list = []
    testday = '24'
    testmonth = '07'
    testyear = '2016'
    # Quick/dirty way of testing dates that doesn't require a lot of impl.
    testdate = 'year_' + testyear + '/month_' + testmonth + '/day_' + testday \
               + '/master_scoreboard.xml'

    base_url = 'http://gd2.mlb.com/components/game/mlb/'
    current_time = datetime.datetime.now()
    if testday != '':
        current_url = base_url + testdate
    else:
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
        game_list.append(gameresult)
        return game_list

    team_abr = 'cws'
    soup = BeautifulSoup(webpage, 'xml')
    # this is only looking at the 'game' filings
    tags = soup.findAll('game', {'away_file_code': team_abr})
    file_code = 'away_file_code'
    if not tags:
        print("Team is home")
        # this is only looking at the 'game' filings
        tags = soup.findAll('game', {'home_file_code': team_abr})
        gameresult.home = True
        file_code = 'home_file_code'
    else:
        print("Team is away")
    if len(tags) == 0:
        # Condition for when there is no game
        gameresult.code_result = 0
        game_list.append(gameresult)
        return game_list
    # Significant: This is what actually determines what state the game is in.
    # It checks each game, first to see if all are final. If all games are final
    # then it returns the latest game.
    for games in tags:
        if games.find('status')['status'] == 'Final':
            away_score = games.find('r')['away']
            home_score = games.find('r')['home']
            print('Away runs: ' + str(away_score))
            print('Home runs: ' + str(home_score))
            if file_code == 'home_file_code':
                if home_score > away_score:
                    print('inputted team wins')
                    gameresult = create_game_result(gameresult, games)

    print("The status is:: " + tags[0].find('status')['status'])
    statuses = soup.find('game', {file_code: team_abr}).find('status')
    print(statuses.attrs)
    if statuses['status'] == 'Final':
        print("This game is over")

if __name__ == '__main__':
    cur_scoreboard_status();
