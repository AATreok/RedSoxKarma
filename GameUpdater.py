import urllib.request
import urllib.error
import datetime
import time
import CSVWriter
from bs4 import BeautifulSoup


# -1 --> error, check for multiple errors and send notice if problem persists for over 1>hr
# 0 --> no game, wait until next day
# 1 --> Red Sox won, wait until next GAME (not day, in case doublheader)
# 2 --> Red Sox lost, wait until next GAME (not day, in case doublheader)
# 3 --> Game suspended, wait until next game
# 4 --> continue, game in progress
# 5 --> preview, game has not begun (long sleep)

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
    elif gameresult.code_result == 5:
        print("Game is in preview, sleep for a while")


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
def cur_scoreboard_status(team_to_check, cust_date = ""):
    game_list = []
    split_dates = cust_date.split('/')
    print("DATES ARE...")
    print(split_dates)
    if cust_date == "":
        split_dates = ("", "", "")
    testday = split_dates[1]
    testmonth = split_dates[0]
    testyear = split_dates[2]
    # Quick/dirty way of testing dates that doesn't require a lot of impl.
    testdate = 'year_' + testyear + '/month_' + testmonth + '/day_' + testday \
               + '/master_scoreboard.xml'

    base_url = 'http://gd2.mlb.com/components/game/mlb/'
    current_time = datetime.datetime.now()
    if testday != '':
        current_url = base_url + testdate
    else:
        # formats date because normally months are not prepended with 0
        current_url = '{0:s}year_{1:d}/month_{2:02d}/day_{3:d}/master_scoreboard.xml'.format(base_url,
                                                                                             current_time.year,
                                                                                             current_time.month,
                                                                                             current_time.day)
    print("The url is " + current_url)
    # intentionally left blank- game time decided after scoreboard is checked

    try:
        with urllib.request.urlopen(current_url) as response:
            webpage = response.read()
    except (urllib.error.HTTPError, urllib.error.URLError, Exception) as e:
        print("HTTPError message " + str(e))
        game_list.append(GameResult(code_result=-1))
        return game_list

    team_abr = team_to_check
    soup = BeautifulSoup(webpage, 'lxml-xml')
    # this is only looking at the 'game' filings
    tags = soup.findAll('game', {'away_file_code': team_abr})
    file_code = 'away_file_code'
    game_home = False
    if not tags:
        print("Team is home")
        # this is only looking at the 'game' filings
        tags = soup.findAll('game', {'home_file_code': team_abr})
        game_home = True
        file_code = 'home_file_code'
    else:
        print("Team is away")
    if len(tags) == 0:
        # Condition for when there is no game
        print("There is no game today, assigning code and exiting")
        game_list.append(GameResult(code_result=0))
        return game_list

    # Significant: This is what actually determines what state the game is in.
    # It checks each game, first to see if all are final. If all games are final
    # then it returns the latest game.
    for games in tags:
        gameresult = GameResult(home=game_home)
        game_status = games.find('status')['status']
        # Leaving this in for two reasons
        # 1. To understand the Beautiful Soup library and how to get info from retrieved tags
        # 2. I believe the date/ID is fundamental to the game status. In fact, eventually I
        #   would like to change it such that a preliminary function is called to generate
        #   the "essential" game data, which is then given the game code if a result is determined.
        gameresult.game_date = games['id']
        print(games['id'])
        if game_status == 'Final':
            gameresult = create_game_result(gameresult, games, file_code)
            game_list.append(gameresult)
        if game_status == 'In Progress':
            gameresult.code_result = 4
            game_list.append(gameresult)
        if game_status == "Preview":
            gameresult.code_result = 5
            game_list.append(gameresult)
        # Not sure yet if this should be treated as in progress or final yet
        # API documentation is nonexistent, so right now this will just send
        # me a message asking me to look into it
        if game_status == 'Postponed':
            gameresult.code_result = 3
            game_list.append(gameresult)
    #gameresult_printer(gameresult)
    return game_list


if __name__ == '__main__':
    team_to_check = 'mia'
    gres = cur_scoreboard_status(team_to_check)
    gresdate = CSVWriter.get_log_id(gres[0].game_date)
    print(gresdate)
    print("The day of the game is ")
    print(datetime.datetime.strptime(str(gresdate), "%Y-%m-%d %H:%M:%S").strftime('%A'))
    print("Finished successfully")