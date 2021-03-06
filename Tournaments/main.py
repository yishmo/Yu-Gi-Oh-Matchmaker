'''
Created on Jan 27, 2018
made a change
@author: Yishan McNabb
'''
import prompt
import goody
import file
import random
import math
import Player

num_rounds = 0
dropped_players = [] #keeps track of dropped players

def check_if_played_before(player1, player2):
    for opponent in player1.get_opponents():
        if player2 == opponent:
            return True
    
    return False


#this is my less than perfect algorithm to try to make parings.
#It swaps seats until players play someone they havent played
def check_and_swap(seats):
    callAgain = True
    numCalls = 0
    while callAgain:
        numCalls +=1
        if numCalls == 50000:
            assert("check_and_swap failed, manually pair instead" == "")
        callAgain = False
        for i in range(len(seats) - 1):
            player1 = seats[i][0]
            player2 = seats[i][1]
            if check_if_played_before(player1, player2):
                seats[i][1], seats[i+1][0] = seats[i+1][0], seats[i][1]
                callAgain = True
                break
    
    return seats

def pair_round(players):
    seats = []
    already_paired = []
    random.shuffle(players)
    players = sorted(players, key = lambda x : -x.get_points())
    if len(players) % 2 == 0: #even
        for i in range(0, len(players), 2):
            seats.append([players[i], players[i+1]])
    else:                     #odd
        for i in range(len(players)//2):
            seats.append([players[2*i], players[(2*i) + 1]])
        seats.append([players[-1], "BYE"])

    return check_and_swap(seats)


def print_pairings(seats):
    for i in range(0, len(seats)):
        try:
            print("Table", i+1, '    ', seats[i][0].name, "("+str(seats[i][0].get_points()) + ")", 'VS.', seats[i][1].name, "("+str(seats[i][1].get_points()) + ")")
        except AttributeError:
            print("Table", i+1, '    ', seats[i][0].name, "("+str(seats[i][0].get_points()) + ")",'VS.', seats[i][1], "This match does not need to be reported.")

    
    

def check_for_same_pairs(seats):
    try:
        for x,y in seats:
            j = x.name
            k = y.name
            if x in y.get_opponents():
                return True
        return False
    except AttributeError:
        return False
        
def calculate_num_rounds(players):
    global num_rounds
    ppl = len(players)
    if ppl < 4:
        num_rounds = -1
    elif ppl in range(4,9):
        num_rounds = 3
    elif ppl in range(9,17):
        num_rounds = 4
    elif ppl in range(17,33):
        num_rounds = 5
    elif ppl in range(33,65):
        num_rounds = 6
    elif ppl in range(65,129):
        num_rounds = 7
    elif ppl in range(129,257):
        num_rounds = 8
    elif ppl in range(257, 513):
        num_rounds = 9
    elif ppl in range(513, 1025):
        num_rounds = 10
    elif ppl in range(1025, 2049):
        num_rounds = 11
    else:
        num_rounds = 12

def drop_player(players):
    global dropped_players
    while True:
        dropping = prompt.for_string("Enter the name of player who is dropping or (p)air next round"
                                    , is_legal= lambda x : x in [y.name for y in players] or x == 'p', error_message='Invalid player name or not p')
        print()
        if dropping == 'p':
            break;
        for i in range(len(players)):
            if dropping == players[i].name:
                dropped_players.append(players[i])
                del players[i]
                break
    
def get_results(pairs, players):
    still_playing = set(range(1, len(pairs) + 1))
    while len(still_playing)>0:
        print("Waiting for results from tables", still_playing)
        table = prompt.for_int("Enter a table number to report results", is_legal = lambda x : x in still_playing,
                                error_message="Enter a table that has not finished their match.")
        table -= 1
        winner = prompt.for_string("Enter a winner ("+ str(pairs[table][0].name) + ") or (" + str(pairs[table][1].name) + ") or (tie)",
                                    is_legal = (lambda x : x == pairs[table][0].name or x == pairs[table][1].name or x == "tie"),
                                    error_message="please enter the winner's full name or tie")
        if winner == 'tie':
            pairs[table][0].ties.append(pairs[table][1])
            pairs[table][1].ties.append(pairs[table][0])
        else:
            if winner == pairs[table][0].name:
                pairs[table][0].wins.append(pairs[table][1])
                pairs[table][1].losses.append(pairs[table][0])
            else:
                pairs[table][1].wins.append(pairs[table][0])
                pairs[table][0].losses.append(pairs[table][1])
        
        still_playing.remove(table + 1)
        print()

        
def calculate_standings(players):
    for player in players:
        player.tiebreaker += str(player.get_points())
    
    for player in players:
        if get_opponents_win_percentage(player) == 0:
            player.tiebreaker += "000"
        else:
            player.tiebreaker += str(int(round(get_opponents_win_percentage(player), 3)*1000))
        num_opponents = 0
        percentage = 0
        for opponent in (player.wins + player.losses + player.ties):
            if opponent != "BYE":
                percentage += get_opponents_win_percentage(opponent)
                num_opponents += 1
        
        if percentage/num_opponents == 0:
            player.tiebreaker += "000"
        else:
            player.tiebreaker+= str(int(round(percentage/num_opponents, 3)*1000))
            

def get_opponents_win_percentage(player):
    num_opponents = 0
    percentage = 0
    for opponent in (player.wins + player.losses + player.ties):
        if opponent != "BYE":
            percentage += get_win_percentage(opponent)
            num_opponents+=1
    return percentage/num_opponents

def get_win_percentage(player):
    return player.num_wins()/(player.num_wins() + player.num_losses() + player.num_ties())

def print_standings(players):
    players = sorted(players, key = lambda x : -int(x.tiebreaker))
    for i in range(len(players)):
        print(i + 1, players[i].name, 'Tie-breaker number: ' + players[i].tiebreaker)


#runs tournament normally, if pairs is called with a value, it means it was run from 
#a save file. Round number can be passed in from run_tournament_from_file function
#which is why it needs to be an argument

def run_tournament(players, roundNumber, pairs=None):
    calculate_num_rounds(players)
    if roundNumber == 1:
        print("Today we are playing", num_rounds, "rounds.")
    for i in range(roundNumber ,num_rounds + 1):
        print()
        print("--------------Round", roundNumber, "Pairings--------------")
        if pairs == None:#If we need to generate pairs(i.e. not given from a savefile) then call the pair_round function
            pairs = pair_round(players)
        print_pairings(pairs)
        write_to_file(players, roundNumber, dropped_players)
        append_pairings_to_file(f'r{roundNumber}.txt', pairs)
        print()
        if len(players)%2 != 0: #if there is a BYE
            pairs[len(pairs)-1][0].wins.append('BYE')#give the player that has a BYE a win
            del pairs[len(pairs)-1] #delete that pairing before get results is called
        get_results(pairs, players)
        drop_player(players)
        roundNumber +=1
        print("*Results up to round " + str(roundNumber - 1) + " have been saved.\n")
        pairs = None #need to reset pairs to none so that we generate a new set of pairs

    calculate_standings(players)
    print_standings(players)

#very important function that allows results to be saved into files
#in between rounds. Can also do many things to force pairings as well
#change mistakes/go back in time/add players if users understand file structure

def run_from_file(filename):

    global dropped_players
    playerdict = {"BYE" : "BYE"}# must establish the dictionary that will have the names of players along with their associated player object
    dropped_dict = {} # must be able to distinguish between a dropped player and a player that is still in the tournament
    savefile = open(filename, 'r')
    round_num = savefile.readline().rstrip()#First line in savefile is current round number
    round_num = int(round_num)
    playerNames = savefile.readline().rstrip().split(';')#second line has all player names
    droppedNames = savefile.readline().rstrip().split(';')#third line has all dropped player names
    currentplayer = ""
    entrycategory = None
    pairs = [] #this value will store pairs

    for name in playerNames:
        playerdict[name] = Player.Player(name)#create all player objects and put them in the playerdict
    for name in droppedNames:
        dropped_dict[name] = Player.Player(name)#create all player objects and put them in the playerdict
    for line in savefile:
        line = line.rstrip()
        if line == "":#there shouldn't be any empty lines (except for the last line)
            pass
        elif line[0] == '%':#the if part of the loop figures out which player and which entry category (that players wins losses or ties) it is inputting
            currentplayer = line[1:]
        elif line[0] == "$":
            entrycategory = line[1:]
        elif line[0] == "*":#this is a special case, at the end of the file there will be pairings that we need to keep track of
            people = line.split(":")[1]
            peoplelist = people.split(",")
            for i in range(0, len(peoplelist)-1, 2):
                pairs.append([playerdict[peoplelist[i]], playerdict[peoplelist[i+1]]])
        else:
        #the else part of the loop actually puts the wins losses or ties inside that players attributes
            try:
                cp_obj = playerdict[currentplayer] #cp_obj = currentplayer object
            except KeyError:                 #however the current player may be a dropped player
                cp_obj = dropped_dict[currentplayer]
            try:
                lp_obj = playerdict[line]          #lp_obj = currentline that we are proccessing's player
            except KeyError:                 #however the current line player may be a dropped player
                lp_obj = dropped_dict[line]

            if entrycategory == 'wins':
                cp_obj.wins.append(lp_obj)
            elif entrycategory == 'losses':
                cp_obj.losses.append(lp_obj)
            elif entrycategory == 'ties':
                cp_obj.ties.append(lp_obj)
                
    del playerdict["BYE"]
    players = list(playerdict.values())
    dropped_players = list(dropped_dict.values())
    savefile.close()
    run_tournament(players, round_num, pairs)

#called directly after a round is paired to save the details about that round.
#This way if someone makes a mistake, we can go back in time and fix it.

def write_to_file(players, round, dropped_players):
    savefile = open(f'r{round}.txt', "w")
    savefile.write(str(round)+"\n")

    file_str = ''
    for player in players: #first write in the remaining players
        file_str += f'{player.name};'  
    file_str = file_str[:-1]
    savefile.write(f'{file_str}\n')

    file_str = ''
    for player in dropped_players: #first write in the remaining dropped players
        file_str += f'{player.name};'  
    file_str = file_str[:-1]
    savefile.write(f'{file_str}\n')

    for player in players + dropped_players:
        savefile.write("%"+player.name+"\n")
        savefile.write("$wins\n")
        for opponent in player.wins:
            if opponent == "BYE":
                savefile.write("BYE" + "\n")
            else:
                savefile.write(opponent.name+ "\n")
        savefile.write("$losses\n")
        for opponent in player.losses:
            savefile.write(opponent.name+ "\n")
        savefile.write("$ties\n")
        for opponent in player.ties:
            savefile.write(opponent.name+"\n")
        
    
    savefile.close()

def append_pairings_to_file(filename, pairs):
    
    savefile = open(filename, "a")
    savefile.write('*pairs:')
    for pair in pairs:
        if pair[1] == "BYE":
            savefile.write(pair[0].name + ",BYE,")
        else:
            savefile.write(pair[0].name + "," + pair[1].name + ",")
        
    
    savefile.close()


def print_welcome_screen():
        print("Welcome to Yishan's Tournament Software!\n")
        print("---------------How To Use---------------\n")
        print("1. Press s or n to either load a saved tournament or start a new one.")
        print("2. Find the players.txt file and enter participans on separate lines.")
        print("3. Follow on screen prompts to run tournament, all command available are enclosed in ().\n")
        
def main():
    print_welcome_screen()
    shouldLoadFromSavefile = prompt.for_string("Load a (s)aved tournament or start a (n)ew one?"
                                                ,is_legal = (lambda x: x == 's' or x == 'n'), error_message = 'Please enter s or n.')
    if shouldLoadFromSavefile == "s":
            fileStr = prompt.for_string("Enter the name of the savefile")
            run_from_file(fileStr)
    else:
            fob = goody.safe_open("Press enter if your partipants are in players.txt, otherwise type out the name of your file.",
                                'r', 'There was an error finding/opening the file.', default='players.txt')
            players = file.get_names(fob)
            while len(players) < 4:
                    print()
                    print("You need at least 4 players to start a tournaments, please edit your file and press enter")
                    input()
                    fob.close()
                    fob = goody.safe_open("Name of file with players", 'r', 'There was an error finding/opening the file.', default='players.txt')
                    players = file.get_names(fob)
                    
            for player in players:
                    print(player.name)
            while True:
                    print("***There are currently", len(players), "players enrolled.***" )
                    start = prompt.for_string("Start tournament? Enter (y)es or (n)o", 
                                            is_legal = (lambda x: x == 'y' or x == 'n'), error_message = 'Please enter y or n.')
                    if start =='y':
                            run_tournament(players, 1)
                            break
                    else:
                            print("Edit file then hit enter.")
                            input()
                            fob = goody.safe_open("Name of file with players", 'r', 'There was an error finding/opening the file.', default='players.txt')
                            players = file.get_names(fob)
                            for player in players:
                                    print(player.name)

            fob.close()

if __name__ == "__main__":
        main()
