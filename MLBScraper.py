import urllib.request
import urllib.error
from bs4 import BeautifulSoup
import datetime
import time.sleep
import sys


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
            print('Game does not exist yet, or Red Sox are not playing today ', now.month, '/', now.day, '/', now.year)
            print('Exiting with status 0')
            return 0

    for game_info in tags:
        if game_info['status'] == 'Final':
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
    while (freezetime.day < datetime.datetime.now().day()):
        safeiter += 1
        time.sleep(3600)
        if safeiter >= 23:
            break


def netError(freezetime):
    time.sleep(60)


def sendProbe():
    print('There is a URL error.')


def makePost():
    print("Create karma post.")


if __name__ == '__main__':
    # -1 --> error, check for multiple errors and send notice if problem persists for over 1>hr
    # 0 --> no game, wait until next day
    # 1 --> Red Sox won (home or away)
    # 2 --> Red Sox lost, wait until next GAME (not day, in case doublheader)
    # 4 --> continue, game in progress
    thistime = datetime.datetime.now()
    # starts the bot; runs indefinitely
    netsafe = 0
    while True:
        gamestatus = getGameStatus('ana')
        while gamestatus != 1:
            if gamestatus == -1:
                if netsafe >= 5:
                    sendProbe()
                    sys.exit()
                netsafe += 1
                netError(thistime)
            if gamestatus == 0:
                nextDay(thistime)
            if gamestatus == 1:
                makePost(thistime)
            if gamestatus == 2:
                makePost(thistime)
            if gamestatus == 4:
                # 60 second pause, then recheck
                time.sleep(60)
