import urllib.request
import urllib.error
import datetime
import time
from bs4 import BeautifulSoup


# -1 --> error, check for multiple errors and send notice if problem persists for over 1>hr
# 0 --> no game, wait until next day
# 1 --> Red Sox won, wait until next GAME (not day, in case doublheader)
# 2 --> Red Sox lost, wait until next GAME (not day, in case doublheader)
# 3 --> Game suspended, wait until next game
# 4 --> continue, game in progress
class GameResult:
    def __init__(self, code_result='Unknown', team_name='Unknown',
                 opponent='Unknown', score_team='Unknown', score_opp='Unknown',
                 game_date='Unknown', home=False):
        self.code_result = code_result
        # This is your team's name
        self.team_name = team_name
        # This is the opponent's name
        self.opponent = opponent
        self.score_team = score_team
        self.score_opp = score_opp
        self.game_date = game_date
        self.home = home


def gameresult_printer(gameresult):
    print("Game Result")
    if gameresult.code_result == -1:
        print("There was an error, retry")
        return
    elif gameresult.code_result == 0:
        print("There is no game, wait until next game")
        return
    elif gameresult.code_result == 1:
        print("Our team won!")
        print("Original date of game / ID: " + str(gameresult.game_date))
        print("Winning Team: " + str(gameresult.team_name) + " w/ " +
              str(gameresult.score_team) + " runs")
        print("Losing Team: " + str(gameresult.opponent) + " w/ " +
              str(gameresult.score_opp) + " runs")
        print("Team is home? " + str(gameresult.home))
    elif gameresult.code_result == 2:
        print("Our team lost :(")
        print("Original date of game / ID: " + str(gameresult.game_date))
        print("Winning Team: " + str(gameresult.opponent) + " w/ " +
              str(gameresult.score_opp) + " runs")
        print("Losing Team: " + str(gameresult.team_name) + " w/ " +
              str(gameresult.score_team) + " runs")
        print("Team is home? " + str(gameresult.home))
    elif gameresult.code_result == 3:
        print("Game is suspended, send message and wait until message")
    elif gameresult.code_result == 4:
        print("Game still in progress, need to continue checking")


def create_game_result(gameresult, game_info, file_code):
    home_score = game_info.find('r')['home']
    away_score = game_info.find('r')['away']
    # Checking to see if home team won
    if file_code == 'home_file_code':
        # All of the below is the same regardless of win/loss for home team
        gameresult.team_name = game_info['home_team_name']
        gameresult.opponent = game_info['away_team_name']
        gameresult.score_team = home_score
        gameresult.score_opp = away_score
        # This pulls the proper date ID from the game
        # (may not match actual date)
        gameresult.game_date = game_info['id']

        if home_score > away_score:
            gameresult.code_result = 1
        else:
            gameresult.code_result = 2
    else:
        # All of the below is the same regardless of win/loss for away team
        gameresult.team_name = game_info['away_team_name']
        gameresult.opponent = game_info['home_team_name']
        gameresult.score_team = away_score
        gameresult.score_opp = home_score
        # This pulls the proper date ID from the game
        # (may not match actual date)
        gameresult.game_date = game_info['id']

        if away_score > home_score:
            gameresult.code_result = 1
        else:
            gameresult.code_result = 2
    assert isinstance(gameresult, GameResult)
    return gameresult


# Assumptions made:
# 1. A doubleheader on the same
def cur_scoreboard_status(team_to_check):
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
        current_url = base_url + \
                      f'year_{current_time.year}/month_' \
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

    team_abr = team_to_check
    soup = BeautifulSoup(webpage, 'lxml-xml')
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
        print("There is no game today, assigning code and exiting")
        gameresult.code_result = 0
        game_list.append(gameresult)
        return game_list
    # Significant: This is what actually determines what state the game is in.
    # It checks each game, first to see if all are final. If all games are final
    # then it returns the latest game.
    for games in tags:
        game_status = games.find('status')['status']
        if game_status == 'Final':
            gameresult = create_game_result(gameresult, games, file_code)
            game_list.append(gameresult)
        if game_status == 'In Progress':
            gameresult.code_result = 4
            game_list.append(gameresult)
        # Not sure yet if this should be treated as in progress or final yet
        # API documentation is nonexistent, so right now this will just send
        # me a message asking me to look into it
        if game_status == 'Postponed':
            gameresult.code_result = 3
            game_list.append(gameresult)
    gameresult_printer(gameresult)

#if __name__ == '__main__':
#    team_to_check = 'bos'
#    cur_scoreboard_status(team_to_check);
