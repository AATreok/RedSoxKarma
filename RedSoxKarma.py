import urllib.request
import urllib.error
import datetime
import time
import praw
import webbrowser
import configparser
import GameUpdater
from bs4 import BeautifulSoup


class GameResult:
    def __init__(self, code_result, team_name, opponent, score_rs, score_opp, game_date):
        self.code_result = code_result
        self.team_name = team_name
        self.opponent = opponent
        self.score_rs = score_rs
        self.score_opp = score_opp
        self.game_date = game_date


# -1 --> error, check for multiple errors and send notice if problem persists for over 1>hr
# 0 --> no game, wait until next day
# 1 --> Red Sox won (home or away)
# 2 --> Red Sox lost, wait until next GAME (not day, in case doublheader)
# 4 --> continue, game in progress
def getgamestatus(team, gametime):
    team_abr = team
    usehomedata = False
    useawaydata = False
    team_home = False
    now = gametime
    urlyear = 'year_' + str(now.year)
    urlmonth = 'month_' + str(now.month).zfill(2)
    urlday = 'day_' + str(now.day).zfill(2)

    if usehomedata:
        urlyear = 'year_2016'
        urlmonth = 'month_06'
        urlday = 'day_04'
    elif useawaydata:
        urlyear = 'year_2016'
        urlmonth = 'month_08'
        urlday = 'day_19'

    gameresult = GameResult(None, None, None, None, None, now)
    url = 'http://gd2.mlb.com/components/game/mlb/'
    url = url + urlyear + '/' + urlmonth + '/' + urlday + '/miniscoreboard.xml'
    print('Connecting to url: ' + url)
    print('The game date is ' + str(now.day) + '/' + str(now.month) + '/' + str(now.year))
    current_time = datetime.datetime.now()
    print('The current date is ' + str(current_time.day) + '/' + str(current_time.month) + '/' + str(current_time.year))
    try:
        with urllib.request.urlopen(url) as response:
            xml = response.read()
    except (urllib.error.HTTPError, urllib.error.URLError, Exception) as e:
        print("HTTPError message " + str(e))
        gameresult.code_result = -1
        return gameresult

    soup = BeautifulSoup(xml, 'xml')
    tags = soup.findAll('game', {'away_file_code': team_abr})
    if not tags:
        print('Tags is empty for away check...')
        tags = soup.findAll('game', {'home_file_code': team_abr})
        team_home = True
        if not tags:
            print('Red Sox are not playing today ', now.month, '/', now.day, '/', now.year)
            print('Exiting with status 0')
            gameresult.code_result = 0
            return gameresult

    for game_info in tags:
        if game_info['status'] == 'Final' or game_info['status'] == 'Game Over':
            if team_home:
                print('Game is finalized!')
                if int(game_info['home_team_runs']) > int(game_info['away_team_runs']):
                    print('THE ' + game_info['home_team_name'].upper() + ' WON!')
                    print('Final score: ' + game_info['home_team_name'] + ' ' + game_info['home_team_runs'] + ' ' +
                          game_info[
                              'away_team_name'] + ' ' +
                          game_info['away_team_runs'])
                    gameresult.code_result = 1
                    gameresult.team_name = game_info['home_team_name']
                    gameresult.opponent = game_info['away_team_name']
                    gameresult.score_opp = game_info['away_team_runs']
                    gameresult.score_rs = game_info['home_team_runs']
                    return gameresult
                else:
                    print('The ' + game_info['home_team_name'] + ' lost :( [home]...')
                    print('Final score: ' + game_info['home_team_name'] + ' ' + game_info['home_team_runs'] + ' ' +
                          game_info[
                              'away_team_name'] + ' ' +
                          game_info['away_team_runs'])
                    gameresult.code_result = 2
                    return gameresult
            else:
                print('Game is finalized!')
                if int(game_info['away_team_runs']) > int(game_info['home_team_runs']):
                    print('THE ' + game_info['away_team_name'].upper() + ' WON!')
                    print('Final score: ' + game_info['away_team_name'] + ' ' + game_info['away_team_runs'] + ' ' +
                          game_info[
                              'home_team_name'] + ' ' +
                          game_info['home_team_runs'])
                    gameresult.code_result = 1
                    gameresult.team_name = game_info['away_team_name']
                    gameresult.opponent = game_info['home_team_name']
                    gameresult.score_opp = game_info['home_team_runs']
                    gameresult.score_rs = game_info['away_team_runs']
                    return gameresult
                else:
                    print('The ' + game_info['away_team_name'] + ' lost :( [away]...')
                    print('Final score: ' + game_info['away_team_name'] + ' ' + game_info['away_team_runs'] + ' ' +
                          game_info[
                              'home_team_name'] + ' ' +
                          game_info['home_team_runs'])
                    gameresult.code_result = 2
                    return gameresult
        else:
            print("Game hasn't started or in progress (but exists).")
            gameresult.code_result = 4
            return gameresult

def seriesText(gameresult):
    return ''

def nextDay(freezetime):
    safeiter = 0
    while (freezetime.day == datetime.datetime.now().day):
        safeiter += 1
        time.sleep(3600)
        if safeiter >= 23:
            break


def netError(freezetime):
    time.sleep(60)


def sendProbe(prawobj):
    prawobj.send_message('AATroop', 'Warning',
                         'URL check has failed 5 times, please check MLB and personal server status!')


def makePost(prawobj, gammeresult):
    prawobj.submit('RedSox', 'THE RED SOX WON UPVOTE PARTY', '')
    time.sleep(28800)

def fakePost(prawobj, gameresult):
    title_text = 'THE ' + str(gameresult.team_name).upper() + ' BEAT THE ' + str(gameresult.opponent).upper() + ' UPVOTE PARTY!'
    post_text = str(gameresult.team_name).upper() + ' BEAT THE ' + str(gameresult.opponent).upper() + ': ' + gameresult.score_rs + ' TO ' + gameresult.score_opp
    post_text = post_text + seriesText(gameresult)
    prawobj.subreddit('botbottestbed').submit(title=title_text,selftext=post_text,send_replies=False)
    #prawobj.submit('botbottestbed', title_text, post_text) archaic


def initialauthorization(prawobj):
    urlauth = prawobj.auth.url(['identity', 'edit', 'history', 'modconfig', 'modflair', 'modposts',
                'modwiki', 'privatemessages', 'read', 'report', 'submit', 'vote', 'wikiedit', 'wikiread'],
               duration='permanent', state=rs_redirect_uri)
    webbrowser.open(urlauth)

def reinitialize():
    return praw.Reddit(client_id=user_client_id, client_secret=user_client_secret,
                          refresh_token=config['Bot Info']['Token'],user_agent=user_agent)

def refreshaccess(prawobj):
    access_key = 'BHS9gNIxHjnD3rnvkE1OTgbNuqI'
    prawobj.set_oauth_app_info(client_id=user_client_id, client_secret=user_client_secret,
                               redirect_uri=rs_redirect_uri)
    access_information = prawobj.get_access_information(access_key)
    return access_information


def refreshtoken(prawobj):
    refresh_token = '63398004-sIFMXiIG1EWqHExsYWtGtHO7vFc'
    prawobj.set_oauth_app_info(client_id=user_client_id, client_secret=user_client_secret,
                               redirect_uri=rs_redirect_uri)
    access_information = prawobj.refresh_access_information(refresh_token)
    return access_information

if __name__ == '__main__':
    print("Hello world!");
    config = configparser.ConfigParser();
    config.read('config.ini');
    print(config['Bot Info']['ClientID'])
    print(config['Bot Info']['Secret'])

    user_client_id = config['Bot Info']['ClientID']
    user_client_secret = config['Bot Info']['Secret']
    rs_redirect_uri = 'http://localhost:8080'
    user_agent = 'RedsoxUpvoteBot:v1.1 by /u/AATroop'
    r = praw.Reddit(user_agent=user_agent, client_id=user_client_id, client_secret=user_client_secret,
                    redirect_uri=rs_redirect_uri)#'script:RedSoxUpvote:v1.0 (by /u/AATroop, /u/DatabaseCentral')
    #initialauthorization(r)
    r = reinitialize()
    print(r.auth.scopes())
    r.redditor('AATroop').message('Test', 'test message from your favorite bot')
    GameUpdater.cur_scoreboard_status('bos')
    quit()
    # starts the bot; runs indefinitely
    while True:
        gamestatus = getgamestatus('nym', thistime)
        print('Gamestatus is ' + str(gamestatus.code_result))
        if gamestatus.code_result == -1:
            # URL error
            if netsafe >= 5:
                sendProbe()
                time.sleep(3600)
            netsafe += 1
            netError(thistime)
            thistime = datetime.datetime.now()
        elif gamestatus.code_result == 0:
            # no game today; wait until next day
            # believe this could cause an issue if done
            # nearly at midnight, where it skips a day
            # but I don't know if this is technically possible
            # unless the bot is started at that time
            nextDay(thistime)
            thistime = datetime.datetime.now()
        elif gamestatus.code_result == 1:
            # game won! Make post, then sleep bot.
            fakePost(r, gamestatus)
            thistime = datetime.datetime.now()
        elif gamestatus.code_result == 2:
            # game lost; sleep bot until next game
            time.sleep(28800)
            thistime = datetime.datetime.now()
        elif gamestatus.code_result == 4:
            # 60 second pause, then recheck
            # IMPORTANT: Time is not updated so if game goes past midnight
            # it keeps on the current date
            time.sleep(60)
        #refreshes token if the (nearly current) time exeeds the last refresh by 60 minutes
        if (thistime - lastrefresh).seconds >= 3600:
            print("refreshing token...")
            refreshtoken(r)
        lastrefresh = thistime
