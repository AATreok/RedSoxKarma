import urllib.request
import urllib.error
import datetime
import time
import sys
import praw
import webbrowser
from bs4 import BeautifulSoup


def getGameStatus(team):
    team_abr = team
    usehomedata = False
    useawaydata = False
    team_home = False
    now = datetime.datetime.now()
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

    url = 'http://gd2.mlb.com/components/game/mlb/'
    url = url + urlyear + '/' + urlmonth + '/' + urlday + '/miniscoreboard.xml'
    print('Connecting to url: ' + url)

    try:
        with urllib.request.urlopen(url) as response:
            xml = response.read()
    except (urllib.error.HTTPError, urllib.error.URLError, Exception) as e:
        print("HTTPError message " + str(e))
        return -1

    soup = BeautifulSoup(xml, 'xml')
    tags = soup.findAll('game', {'away_file_code': team_abr})
    if not tags:
        print('Tags is empty for away check...')
        tags = soup.findAll('game', {'home_file_code': team_abr})
        team_home = True
        if not tags:
            print('Red Sox are not playing today ', now.month, '/', now.day, '/', now.year)
            print('Exiting with status 0')
            return 0

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
                    return 1
                else:
                    print('The ' + game_info['home_team_name'] + ' lost :( [home]...')
                    print('Final score: ' + game_info['home_team_name'] + ' ' + game_info['home_team_runs'] + ' ' +
                          game_info[
                              'away_team_name'] + ' ' +
                          game_info['away_team_runs'])
                    return 2
            else:
                print('Game is finalized!')
                if int(game_info['away_team_runs']) > int(game_info['home_team_runs']):
                    print('THE ' + game_info['away_team_name'].upper() + ' WON!')
                    print('Final score: ' + game_info['away_team_name'] + ' ' + game_info['away_team_runs'] + ' ' +
                          game_info[
                              'home_team_name'] + ' ' +
                          game_info['home_team_runs'])
                    return 1
                else:
                    print('The ' + game_info['away_team_name'] + ' lost :( [away]...')
                    print('Final score: ' + game_info['away_team_name'] + ' ' + game_info['away_team_runs'] + ' ' +
                          game_info[
                              'home_team_name'] + ' ' +
                          game_info['home_team_runs'])
                    return 2
        else:
            print("Game hasn't started or in progress (but exists).")
            return 4


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


def makePost(prawobj):
    prawobj.submit('botbottestbed', 'THE RED SOX WON UPVOTE PARTY', 'THE REDSOX WON!')
    time.sleep(28800)

def initialaccess(prawobj):
    user_client_id = 'DuOaY9FGDKSR8g'
    user_client_secret = '4unjTUjPmrpxB9ZM1cOkb1kbdDk'
    rs_redirect_uri = 'http://www.reddit.com/r/redsox'
    prawobj.set_oauth_app_info(client_id=user_client_id, client_secret=user_client_secret,
                               redirect_uri=rs_redirect_uri)
    urlauth = prawobj.get_authorize_url('uniqueKey', 'identity read submit privatemessages', True)
    webbrowser.open(urlauth)


def refreshaccess(prawobj):
    user_client_id = 'DuOaY9FGDKSR8g'
    user_client_secret = '4unjTUjPmrpxB9ZM1cOkb1kbdDk'
    rs_redirect_uri = 'http://www.reddit.com/r/redsox'
    access_key = 'EYh2n3FBEXnf5XsjKaD43eZ9atg'
    prawobj.set_oauth_app_info(client_id=user_client_id, client_secret=user_client_secret,
                               redirect_uri=rs_redirect_uri)
    access_information = prawobj.get_access_information(access_key)
    return access_information


def refreshtoken(prawobj):
    user_client_id = 'DuOaY9FGDKSR8g'
    user_client_secret = '4unjTUjPmrpxB9ZM1cOkb1kbdDk'
    rs_redirect_uri = 'http://www.reddit.com/r/redsox'
    prawobj.set_oauth_app_info(client_id=user_client_id, client_secret=user_client_secret,
                               redirect_uri=rs_redirect_uri)
    prawobj.refresh_access_information('45420599-D7uYF0c9RQ-GHdFZO1pgzB7drmk')


if __name__ == '__main__':
    # -1 --> error, check for multiple errors and send notice if problem persists for over 1>hr
    # 0 --> no game, wait until next day
    # 1 --> Red Sox won (home or away)
    # 2 --> Red Sox lost, wait until next GAME (not day, in case doublheader)
    # 4 --> continue, game in progress
    r = praw.Reddit('script:RedSoxManagment:v1.0 (by /u/andrewbenintendi)')
    # initialaccess(r)
    # print(refreshaccess(r))
    refreshtoken(r)
    authenticated_user = r.get_me()
    print(authenticated_user.name)
    netsafe = 0
    lastrefresh = datetime.datetime.now()
    # starts the bot; runs indefinitely
    while True:
        gamestatus = getGameStatus('bos')
        thistime = datetime.datetime.now()
        if((thistime - lastrefresh).seconds >= 3600):
            print("refreshing token...")
            refreshtoken(r)
        print('Gamestatus is ' + str(gamestatus))
        if gamestatus == -1:
            # URL error
            if netsafe >= 5:
                sendProbe()
                time.sleep(3600)
            netsafe += 1
            netError(thistime)
        elif gamestatus == 0:
            # no game today; wait until next day
            # believe this could cause an issue if done
            # nearly at midnight, where it skips a day
            # but I don't know if this is technically possible
            # unless the bot is started at that time
            nextDay(thistime)
        elif gamestatus == 1:
            # game won! Make post, then sleep bot.
            makePost(r)
        elif gamestatus == 2:
            # game lost; sleep bot until next game
            time.sleep(28800)
        elif gamestatus == 4:
            # 60 second pause, then recheck
            time.sleep(60)
        lastrefresh = thistime
