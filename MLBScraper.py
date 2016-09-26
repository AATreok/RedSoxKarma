import urllib.request
import urllib.error
from bs4 import BeautifulSoup
import datetime
import sys


def getGameStatus(team):
    team_abr = team
    usehomedata = False
    useawaydata = True
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
                    print('Final score: ' + game_info['home_team_name'] + ' ' + game_info['home_team_runs'] + ' ' + game_info[
                        'away_team_name'] + ' ' +
                          game_info['away_team_runs'])
                    return 1
                else:
                    print('The ' + game_info['home_team_name'] + ' lost :( [home]...')
                    print('Final score: ' + game_info['home_team_name'] + ' ' + game_info['home_team_runs'] + ' ' + game_info[
                        'away_team_name'] + ' ' +
                          game_info['away_team_runs'])
                    return 2
            else:
                print('Game is finalized!')
                if int(game_info['away_team_runs']) > int(game_info['home_team_runs']):
                    print('THE ' + game_info['away_team_name'].upper() + ' WON!')
                    print('Final score: ' + game_info['away_team_name'] + ' ' + game_info['away_team_runs'] + ' ' + game_info[
                        'home_team_name'] + ' ' +
                          game_info['home_team_runs'])
                    return 1
                else:
                    print('The ' + game_info['away_team_name'] + ' lost :( [away]...')
                    print('Final score: ' + game_info['away_team_name'] + ' ' + game_info['away_team_runs'] + ' ' + game_info[
                        'home_team_name'] + ' ' +
                          game_info['home_team_runs'])
                    return 2


if __name__ == '__main__':
    if getGameStatus('ana') == -1:
        print("Error getting URL")
    sys.exit()
