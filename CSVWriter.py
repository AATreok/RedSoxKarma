# Had to create a new file just for read/write CSV
import csv
import datetime
import random
filename = 'ledger.csv'

def write_to_log(new_log):
    try:
        game_log = open(filename, 'r+')
        logreader = csv.DictReader(game_log, 
            ['Game ID', 'Date', 'Opponent'], delimiter = ',')
    except IOError:
        game_log = open(filename, 'w+')
        # Basically, create an empty file so that it can read from it
        logwriter = csv.DictWriter(game_log, 
            ['Game ID', 'Date', 'Opponent'], delimiter = ',')
        game_log.close()
        game_log = open(filename, 'r+')
        logreader = csv.DictReader(game_log, 
            ['Game ID', 'Date', 'Opponent'], delimiter = ',')
    
    # Create list file will be read to
    past_games = []
    # Keeps track of size
    count = 0
    for row in logreader:
        try:
            past_games.append(
                {'Game ID':row['Game ID'],'Date':row['Date'],
                'Opponent':row['Opponent']}
            )
            count+=1
        except TypeError:
            # If there's an error, ignore it. File will be destroyed and 
            # written again regardless
            print("Caught error for row " + str(row))
            continue
    
    # Done with reading
    game_log.close()
    
    # This insures the last 10 games are kept
    if (count < 10):
        past_games.append(new_log)
    # Otherwise, it will return the oldest of the 10 games
    else:
        oldest = ''
        for games in past_games:
            if oldest == '' or oldest > games['Date']:
                oldest = games['Date']
        for games in past_games:
            if oldest == games['Date']:
                past_games.remove(games) 
                past_games.append(new_log)
                

    # Write everything back into the file    
    game_log = open(filename, 'w+')
    spamwriter = csv.DictWriter(game_log, 
        ['Game ID', 'Date', 'Opponent'], delimiter = ',')
    for log_items in past_games:
        spamwriter.writerow(log_items)
    game_log.close()

# For an inputted Game ID, this will tell you if the game already exists in
# the log (why game ID? Because it's a unique value and doesn't require
# looking at the entire row)
def game_exists(game_id):
    try:
        game_log = open(filename, 'r+')
        logreader = csv.DictReader(game_log, 
            ['Game ID', 'Date', 'Opponent'], delimiter = ',')
    except IOError:
        print("Enountered error when opening file")
        return False
    
    for row in logreader:
        print("Comparing " + row['Game ID'] + " and " + game_id)
        if row['Game ID'] == game_id:
            return True
    
    return False

# unused
def app_csv(log_entry):
    game_log = open(filename, 'a+')
    spamwriter = csv.DictWriter(game_log, ['Game ID', 'Date', 'Opponent'], delimiter = ',')
    spamwriter.writerow(log_entry)

# clears the ledger by overwriting w/ a new, blank file
def clear_Ledger():
    open(filename, 'w').close()



def backup_print(dict_list):
    # If you need to print the log stored as list, use this
    count = 1
    for things in dict_list:
        print(str(count) + ". ", end='')
        for k, v in things.items():
            print(k + ": " + str(v) + " ", end='')
        count+=1
        print()
    
def get_log_id(game_id):
    if game_id == "Unknown":
        return ""
    game_id = game_id[:10]
    return datetime.datetime.strptime(game_id, '%Y/%m/%d')

def fake_log():
    year = random.randint(2010,2017)
    month = str(random.randint(1,12)).zfill(2)
    day = str(random.randint(1,28)).zfill(2)
    end_st = str(year) + '/' + (month) + '/' + (day) + '/' + 'bosmlb-milmlb-1'
    log_entry = {'Game ID':end_st, 'Date':get_log_id(end_st), 'Opponent':'Brewers'}
    return log_entry
    
if __name__ == '__main__':
    testlog = fake_log()
    write_to_log(testlog)
    print(game_exists('2016/02/12/bosmlb-milmlb-1'))
    clear_Ledger()