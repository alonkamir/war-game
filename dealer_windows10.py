import socket
import time
import threading
import random

# gets the array of used cards and generates an unsed card
# returns array with suit in index 0 and number in index 1
def card_gen(used_cards):
    # choose an unused card
    random_suit = random.randint(0, 3)
    random_card = random.randint(0, 12)
    while used_cards[((random_suit * 13) + random_card)] == 1:
        random_suit = random.randint(0, 3)
        random_card = random.randint(0, 12)
    random_ = []
    random_.append(random_suit)
    random_.append(random_card)
    return random_

# started by thread- handles the entire game
def new_game(clientsocket):
    # Diamons, Clubs, Hearts, Spades
    suits = ("D", "C", "H", "S")
    cards = ("2","3","4","5","6","7","8","9","10","J","Q","K","A")
    rounds_played = 0
    used_cards_counter = 0
    money_earned = 0
    keep_playing = True
    # create an array of zeros(used cards will be one)
    used_cards = []
    for i in range(0,52):
        used_cards.append(0)
    while keep_playing:
        # while the deck is not empty
        while used_cards_counter < 52 and keep_playing:
            double_tie = False
            tie = 1
            # generate card for client
            client_card = card_gen(used_cards)
            # mark card as used
            used_cards[((client_card[0] * 13) + client_card[1])] = 1
            used_cards_counter += 1
            # generate card for server
            server_card = card_gen(used_cards)
            # mark card as used
            used_cards[((server_card[0] * 13) + server_card[1])] = 1
            used_cards_counter += 1
            # send card to client
            clientsocket.send(bytes("\nYour card is " + str(cards[client_card[1]] + suits[client_card[0]] + "\nWhat is your bet? "), "utf-8"))
            client_bet = clientsocket.recv(256)
            is_int = False
            # check if input is valid (positive integer)
            while not(is_int):
                try:
                    int(client_bet.decode())
                    if int(client_bet.decode()) > 0:
                        is_int = True
                    else:
                        clientsocket.send(bytes("Invalid input. Please enter a number:", "utf-8"))
                        client_bet = clientsocket.recv(256)
                except:
                    clientsocket.send(bytes("Invalid input. Please enter a number:", "utf-8"))
                    client_bet = clientsocket.recv(256)
            rounds_played += 1
            tie_massage = False
            was_tied = False
            while tie == 1:
                # if game is not already tied
                if not(tie_massage):
                    # first tie
                    if client_card[1] == server_card[1]:
                        was_tied = True
                        result = "\nThe result of round: " + str(rounds_played) + " is a tie!\n"
                        result += "Dealer’s card: " + str(cards[server_card[1]] + suits[server_card[0]]) + "\n"
                        result += "Player’s card: " + str(cards[client_card[1]] + suits[client_card[0]]) + "\n"            
                        result += "The bet: " + client_bet.decode() + "$\n"
                        result += "Do you wish to surrender or go to war? s for surrender, w for war"
                        clientsocket.send(bytes(result, "utf-8"))
                        client_response = clientsocket.recv(256).decode()
                        # check that the input is valid
                        while client_response != "s" and client_response != "w":
                            clientsocket.send(bytes("Invalid input. type s for surrender, w for war", "utf-8"))
                            client_response = clientsocket.recv(256).decode()    
                        # war
                        if client_response == "w":
                            # not enough cards for war
                            if used_cards_counter >= 47:
                                result = "Not enough cards for war game"
                                keep_playing = False
                                tie = 0
                            # going for war
                            else:
                                # discard 3 cards
                                for i in range(1,3):
                                    discard_card = card_gen(used_cards)
                                    # mark card as used
                                    used_cards[((discard_card[0] * 13) + discard_card[1])] = 1
                                    used_cards_counter += 1
                                # generate card for client
                                client_card = card_gen(used_cards)
                                # mark card as used
                                used_cards[((client_card[0] * 13) + client_card[1])] = 1
                                used_cards_counter += 1    
                                # generate card for server
                                server_card = card_gen(used_cards)
                                # mark card as used
                                used_cards[((server_card[0] * 13) + server_card[1])] = 1
                                used_cards_counter += 1
                                # check who wins again
                                tie = 1
                                tie_massage = True

                        # surrender 
                        else:
                            money_earned -= int(client_bet.decode())/2
                            result = "\nRound: " + str(rounds_played) + " tie breaker:\n"
                            result += "Player surrendered!\nThe bet: " + client_bet.decode() + "$\n"
                            result += "Dealer won: " + str(int(client_bet.decode())/2) + "$\n"
                            result += "Player won: " + str(int(client_bet.decode())/2) + "$\n"
                            result += "Do you wish to continue? y for yes, n for no, s for status"
                            clientsocket.send(bytes(result, "utf-8"))
                            tie = 0
                    # some one won
                    else:
                        result = "\nThe result of round: " + str(rounds_played) + "\n"
                        # client won
                        if client_card[1] > server_card[1]:
                            money_earned += int(client_bet.decode())
                            result += "Player won " + client_bet.decode() + "$\n"
                        # server won
                        else:
                            money_earned -= int(client_bet.decode())
                            result += "Dealer won " + client_bet.decode() + "$\n"
                            
                        result += "Player’s card: " + str(cards[client_card[1]] + suits[client_card[0]]) + "\n"
                        result += "Dealer’s card: " + str(cards[server_card[1]] + suits[server_card[0]])+ "\n"
                        result += "Do you wish to continue? y for yes, n for no, s for status"
                        clientsocket.send(bytes(result, "utf-8"))
                        tie = 0

                # tied
                else:
                    # second tie
                    if client_card[1] == server_card[1]:                     
                        # check who wins again
                        money_earned += int(client_bet.decode())*2
                        result = "\nRound " + str(rounds_played) +" tie breaker:\n"
                        result += "Going to war!\n3 cards were discarded.\n"
                        result += "Original bet: "  + client_bet.decode() + "$\n"
                        result += "New bet: "  + str(int(client_bet.decode())*2) + "$\n"
                        result += "Dealer’s card: " + str(cards[server_card[1]] + suits[server_card[0]])+ "\n"
                        result += "Player’s card: " + str(cards[client_card[1]] + suits[client_card[0]]) + "\n"
                        result += "Player won: " + str(int(client_bet.decode())*2) + "$\n"
                        result += "Do you wish to continue? y for yes, n for no, s for status"
                        clientsocket.send(bytes(result, "utf-8")) 
                        tie = 0
                        tie_massage = False
                        double_tie = True
                    
                    # some one won tie
                    else:
                        result = "\nRound " + str(rounds_played) +" tie breaker:\n"
                        result += "Going to war!\n3 cards were discarded.\n"
                        result += "Original bet: "  + client_bet.decode() + "$\n"
                        result += "New bet: "  + str(int(client_bet.decode())*2) + "$\n"
                        result += "Dealer’s card: " + str(cards[server_card[1]] + suits[server_card[0]])+ "\n"
                        result += "Player’s card: " + str(cards[client_card[1]] + suits[client_card[0]]) + "\n"
                        # client won tie
                        if client_card[1] > server_card[1]:
                            money_earned += int(client_bet.decode())                        
                            result += "Player won: " + client_bet.decode() + "$\n"
                        # server won tie
                        else:
                            money_earned -= int(client_bet.decode())*2                           
                            result += "Dealer won: " + str(int(client_bet.decode())*2) + "$\n"   

                        result += "Do you wish to continue? y for yes, n for no, s for status"
                        clientsocket.send(bytes(result, "utf-8"))
                        tie_massage = False
                        tie = 0
            if keep_playing:      
                # player's response to "Do you wish to continue?"
                client_response = clientsocket.recv(256).decode()
                # check that input is valid
                while client_response != "n" and client_response != "s" and client_response != "y":
                    clientsocket.send(bytes("Invalid input. y for yes, n for no, s for status", "utf-8"))
                    client_response = clientsocket.recv(256).decode()
                # get status
                while str(client_response) == "s":
                    status = "\nCurrent round: " + str(rounds_played) + "\n"
                    if client_card[1] > server_card[1] or double_tie:
                        if double_tie:
                            status += "Player won: " + str(int(client_bet.decode())*2) + "$\n"
                        else:
                            status += "Player won: " + client_bet.decode() + "$\n"
                    elif client_card[1] < server_card[1]:
                        if was_tied:
                            status += "Dealer won: " + str(int(client_bet.decode())*2) + "$\n"
                        else:
                            status += "Dealer won: " + client_bet.decode() + "$\n"
                    else:
                        status += "Player surrendered and lost: " + str(int(client_bet.decode())/2) + "$\n"
                    status += "Do you wish to continue? y for yes, n for no, s for status"
                    clientsocket.send(bytes(status, "utf-8"))
                    client_response = clientsocket.recv(256).decode()
                    # check that input is valid
                    while client_response != "n" and client_response != "s" and client_response != "y":
                        clientsocket.send(bytes("Invalid input. y for yes, n for no, s for status", "utf-8"))
                        client_response = clientsocket.recv(256).decode()
                # finish
                if str(client_response) == "n":
                    end_game_msg = "\nThe game ended on round: " + str(rounds_played) + "\n"
                    end_game_msg += "The player quit.\n"
                    if money_earned < 0:
                        end_game_msg += "Player lost: " + str(money_earned * (-1)) + "$\nThanks for playing."
                    else:
                        end_game_msg += "Player won: " + str(money_earned) + "$\nThanks for playing."
                    clientsocket.send(bytes(end_game_msg, "utf-8"))
                    keep_playing = False

            
        # game finished: send score and ask player if he wants another    
        again_msg = "\nThe game has ended\n"
        if money_earned < 0:
            again_msg += "Player lost: " + str(money_earned * (-1)) + "$\n"
            again_msg += "Dealer is the winner!\n"
        else:
            again_msg += "Player won: " + str(money_earned) + "$\n"
            again_msg += "Player is the winner!\n"
        again_msg += "Would you like to play again? y for yes, n for no"
        clientsocket.send(bytes(again_msg, "utf-8"))
        client_response = clientsocket.recv(256).decode()
        while client_response != "n" and client_response != "y":
            clientsocket.send(bytes("Invalid input. y for yes, n for no", "utf-8"))
            client_response = clientsocket.recv(256).decode()
        if client_response == "n":
            keep_playing = False
            clientsocket.send(bytes("End of war game", "utf-8"))
        # reset game
        else:
            new_game(clientsocket)

###############################

# main

###############################
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 1234))

while True:
    # accept connections from outside
    s.listen(5)
    clientsocket, address = s.accept()

    # check number of active threads(clients)
    if threading.active_count() < 3:
        print(f"Connection from {address} has been established.")
        # create a new thread that handles the game for this client
        t = threading.Thread(target = new_game, args = (clientsocket,))
        # start the thread
        t.start()
    # deny client
    else:
        print(f"Connection from {address} refused due to too many players currently online.")
        clientsocket.close()