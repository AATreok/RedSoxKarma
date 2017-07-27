import datetime
import time
import praw
import webbrowser
import configparser
import GameUpdater

def seriesText(gameresult):
    return ''

def nextDay(freezetime):
    safeiter = 0
    while (freezetime.day == datetime.datetime.now().day):
        safeiter += 1
        time.sleep(3600)
        if safeiter >= 23:
            break

def netError():
    time.sleep(60)

def sendProbe(prawobj):
    prawobj.send_message('AATroop', 'Warning',
                         'URL check has failed 5 times, please check MLB and personal server status!')

def makePost(prawobj, gammeresult):
    prawobj.submit('RedSox', 'THE RED SOX WON UPVOTE PARTY', '')
    time.sleep(28800)

def fakePost(prawobj, gameresult):
    title_text = 'THE ' + str(gameresult.team_name).upper() + ' BEAT THE ' + str(gameresult.opponent).upper() + ' UPVOTE PARTY!'
    post_text = str(gameresult.team_name).upper() + ' BEAT THE ' + str(gameresult.opponent).upper() + ': ' + gameresult.score_team + ' TO ' + gameresult.score_opp
    post_text = post_text + seriesText(gameresult)
    prawobj.subreddit('botbottestbed').submit(title=title_text,selftext=post_text,send_replies=False)
    #prawobj.submit('botbottestbed', title_text, post_text) archaic

def reinitialize():
    config = configparser.ConfigParser();
    config.read('config.ini');
    user_client_id = config['Bot Info']['ClientID']
    user_client_secret = config['Bot Info']['Secret']
    user_agent = 'RedsoxUpvoteBot:v1.1 by /u/AATroop'
    return praw.Reddit(client_id=user_client_id, client_secret=user_client_secret,
                          refresh_token=config['Bot Info']['Refresh_Token'],user_agent=user_agent)

if __name__ == '__main__':
    team_shortcode = 'bos'
    r = reinitialize()

    print(r.auth.scopes())
    games = GameUpdater.cur_scoreboard_status('bos', "07/16/2017")
    #print(games)
    GameUpdater.gameresult_printer(games[0])
    GameUpdater.gameresult_printer(games[1])
    exit()
    #r.redditor('AATroop').message('Test', 'test message from your favorite bot')
    # starts the bot; runs indefinitely
    while True:
        gamestatus = GameUpdater.cur_scoreboard_statuts(team_shortcode)
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
