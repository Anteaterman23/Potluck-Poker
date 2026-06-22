import sys
import os
from datetime import datetime
from time import sleep
from typing import List
from constants import BOLD, UNDERLINE, RESET, GAME_DELAY
from general_utilities import debug
from game_utilities import Card, Deck, Player, Interface

current_script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_script_dir, os.pardir))
sys.path.append(parent_dir)

DEBUG_FILENAME = debug(datetime.now().strftime("%m/%d/%Y %H:%M:%S"))

class ClassicPlayer(Player):
    def __init__(self, player_num = 1, wins = 0, losses = 0):
        # Player info
        super().__init__(player_num, wins, losses)
        
        # Card info
        self.cards_facedown : List[Card] = []
        self.cards_faceup : List[Card] = []
        self.pot : List[Card] = []
        self.card_goal : Card = None
        self.card_special : Card = None
        self.should_subtract = False

    def receive_card(self, card : Card, type : str):
        if type == "facedown":
            self.cards_facedown.append(card)
        elif type == "goal":
            self.card_goal = card
        elif type == "special":
            self.card_special = card
        else:
            raise ValueError(f"Invalid card type: {type}. Must be 'facedown', 'goal', or 'special'.")
    
    def flip_card(self) -> Card:
        card = self.cards_facedown.pop()
        self.cards_faceup.append(card)
        return card

    def get_individual_total(self):
        total = sum(card.value for card in self.cards_faceup)
        if self.card_special and self.should_subtract:
            total -= self.card_special.value
        return total
    
    def get_pot_total(self):
        return sum(card.value for card in self.pot)

    def print_player_info(self):
        bottom_row = self.cards_faceup.copy()
        while len(bottom_row) < 3:
            bottom_row.append("??")
        
        str1 = f'{BOLD}PLAYER {self.player_num} INFO{RESET}\n'
        str2 = f'    {str(self.card_goal)}\n'
        str3 = '  '.join(str(card) for card in bottom_row) + '\n'
        str4 = f'Special Card: {str(self.card_special)}\n' if self.card_special else ''
        str5 = f'Total: {BOLD}{self.get_individual_total()}{RESET}\n'
        if self.player_num == 1:
            print(str2 + str3 + str4 + str5 + str1)
        else:
            print(str1 + str5 + str3 + str2 + str4)


class ClassicComputer(ClassicPlayer):
    def __init__(self, wins = 0, losses = 0):
        super().__init__(player_num = 2, wins = wins, losses = losses)
    
    def decide_trade(self, trade_info : dict) -> str:
        debug("TRADE OFFERED TO COMPUTER", DEBUG_FILENAME)
        best_score = float("-inf")
        best_option = "0"

        for option, info in trade_info.items():
            p1_total, p2_total, goal_amount, has_bigger_goal, has_equal_goal = info
            score = 0

            if p2_total > goal_amount:
                score -= 50
            else:
                score += 30
                score += abs(goal_amount - p2_total)
            
            if p1_total > goal_amount:
                score += 25
            else:
                score -= 15
                score -= abs(goal_amount - p1_total)
            
            if has_bigger_goal:
                score += 10
            elif has_equal_goal:
                score += 5
            
            debug(f"Option: {option}\nScore: {score}\nInfo: {info}\n", DEBUG_FILENAME)
            if score > best_score:
                best_score = score
                best_option = option

        return best_option

    def decide_if_special(self, special_info : tuple) -> str:
        debug("SPECIAL OFFERED TO COMPUTER", DEBUG_FILENAME)
        p1_total, p2_total, goal_amount = special_info

        if p2_total > goal_amount:
            debug("Taking special to avoid bust...", DEBUG_FILENAME)
            return "1"
        
        if p1_total > goal_amount - 6 and p2_total <= goal_amount - 6:
            debug("Taking special to try to gain advantage...", DEBUG_FILENAME)
            return "1"
        
        answer = str(int(abs(p2_total - goal_amount) > abs(p1_total - goal_amount)))
        if answer == "1":
            debug("Taking special because opponent is closer to goal...", DEBUG_FILENAME)
        else:
            debug("Declining special because opponent is farther from goal...", DEBUG_FILENAME)
        return answer
    
    def decide_special_effect(self, special_info : tuple, special_value : int) -> str:
        p1_total, p2_total, goal_amount = special_info

        # Option 1: subtract from self
        new_self_total = p2_total - special_value
        safe_if_self = new_self_total <= goal_amount

        # Option 2: subtract from goal
        new_goal = goal_amount - special_value
        safe_if_goal = p2_total <= new_goal
        safe_if_goal_opponent = p1_total <= new_goal

        # Case 1: If bust now, try to save myself
        if p2_total > goal_amount:
            if safe_if_self:
                debug("Subtracting from self to avoid bust...", DEBUG_FILENAME)
                return "0"
            elif safe_if_goal:
                debug("Subtracting from goal to avoid bust...", DEBUG_FILENAME)
                return "1"
            else:
                debug("Subtracting from self, but still bust no matter what...", DEBUG_FILENAME)
                return "0"

        # Case 2: If opponent is bust, don’t risk changing goal
        if p1_total > goal_amount and p2_total <= goal_amount:
            debug("Subtracting from self since opponent is bust...", DEBUG_FILENAME)
            return "0"

        dist_me = goal_amount - p2_total
        dist_them = goal_amount - p1_total

        if safe_if_goal and not safe_if_goal_opponent:
            debug("Subtracting from goal to bust opponent...", DEBUG_FILENAME)
            return "1"

        if dist_me <= 4 and safe_if_self:
            debug("Subtracting from self to stay safe...", DEBUG_FILENAME)
            return "0"

        if dist_me < dist_them and safe_if_goal:
            debug("Subtracting from goal to increase lead...", DEBUG_FILENAME)
            return "1"

        debug("Subtracting from self as fallback...", DEBUG_FILENAME)
        return "0"


class ClassicGame:
    def __init__(self, singleplayer, p1_wins = 0, p2_wins = 0):
        # Initial parameters
        self.deck = Deck()
        self.interface = Interface()
        if singleplayer:
            self.player_1 = ClassicPlayer(wins=p1_wins, losses=p2_wins)
            self.player_2 = ClassicComputer(wins=p2_wins, losses=p1_wins)
        else:
            self.player_1 = ClassicPlayer(1, wins=p1_wins, losses=p2_wins)
            self.player_2 = ClassicPlayer(2, wins=p2_wins, losses=p1_wins)
        self.players = (self.player_1, self.player_2)

        # Game variables
        self.singleplayer = singleplayer
        self.goal_amount = None
        self.phase = 0
        self.rounds = 0

    def setup_game(self):
        # Deal facedown cards
        for _ in range(3):
            self.deck.draw_card(self.player_1, "facedown")
            self.deck.draw_card(self.player_2, "facedown")
        
        # Deal goal cards
        card1 = self.deck.draw_card(self.player_1, "goal")
        card2 = self.deck.draw_card(self.player_2, "goal")
        self.goal_amount = card1.value + card2.value

    def determine_winner(self):
        p1_total = self.player_1.get_individual_total()
        p2_total = self.player_2.get_individual_total()
        goal = self.goal_amount

        if p1_total > goal and p2_total > goal:
            return None
        elif p1_total == p2_total:
            return None
        elif p1_total <= goal and p2_total > goal:
            return 1
        elif p1_total > goal and p2_total <= goal:
            return 2
        else:
            p1_dist, p2_dist = abs(p1_total - goal), abs(p2_total - goal)
            return 1 if p1_dist < p2_dist else 2

    def print_game_state(self):
        winner = self.determine_winner()
        str1 = f"{BOLD}PHASE {self.phase+1}{RESET}"
        str2 = f"{BOLD}{UNDERLINE}CURRENT WINNER:{RESET}"
        str3 = f" Player {winner}" if winner else " None"
        str4 = f"{BOLD}GOAL AMOUNT: {self.goal_amount}{RESET}"
        str5 = "-" * (len(str4) - 8)

        self.interface.clear_screen()
        print(str1, str2 + str3, "", sep='\n')
        self.player_2.print_player_info()
        print(str5, str4, str5, "", sep='\n')
        self.player_1.print_player_info()
    
    def play_phase(self):
        debug(f"PHASE {self.phase+1} START", DEBUG_FILENAME)
        self.print_game_state()
        self.interface.ask("Press enter to flip card...", options=[""])

        # Both players flip card
        card1 = self.player_1.flip_card()
        card2 = self.player_2.flip_card()
        self.print_game_state()
        
        # Card trading may occur
        if card1.value == card2.value:
            print("Cards are the same! No trades during this phase\n")
            sleep(GAME_DELAY)
        else:
            trading_player = self.players[int(card1.value < card2.value)]
            other_player = self.players[int(card1.value > card2.value)]
            offers = other_player.cards_faceup.copy()
            offers.append(self.player_2.card_goal)
            offers.append(self.player_1.card_goal)

            str1 = f"Player {trading_player.player_num} has the larger card this phase "
            str2 = f"({trading_player.cards_faceup[self.phase]})"
            print(str1 + str2)

            if self.singleplayer and trading_player == self.player_2:
                answer = self.offer_trade_to_computer(offers)
            else:
                answer = self.offer_trade_to_player(offers)
            
            self.trade_cards(trading_player, other_player, offers, answer)

        # Special card may occur at end of third phase
        if self.phase == 2:
            self.print_game_state()
            goal1 = self.player_1.card_goal
            goal2 = self.player_2.card_goal

            if goal1.value == goal2.value:
                print("Goal cards are the same! No special cards during this phase\n")
                sleep(GAME_DELAY)
            else:
                self.phase += 1
                special_player = self.players[int(goal1.value < goal2.value)]
                print(f"Player {special_player.player_num} has the larger goal card")

                if self.singleplayer and special_player == self.player_2:
                    special_card, answer = self.offer_special_to_computer(special_player)
                else:
                    special_card, answer = self.offer_special_to_player(special_player)
                
                if special_card:
                    self.use_special_card(special_player, special_card, answer)

        debug(f"PHASE END. PLAYER {self.determine_winner()} IS WINNING\n", DEBUG_FILENAME)
        # Go to next phase (but do not exceed 4; zero-indexed)
        self.phase = min(self.phase + 1, 3)
    
    def offer_trade_to_player(self, offers : list):
        debug(f"TRADE OFFERED TO PLAYER 1", DEBUG_FILENAME)
        print("Which card would they like to trade it for?")
        print("[0] None")
        for index, card in enumerate(offers, start=1):
            print(f"[{index}] {card}")

        question = ""
        options = list(str(i) for i in range(len(offers)+1))
        answer = self.interface.ask(question, options)
        return answer
    
    def offer_trade_to_computer(self, offers : list):
        print("Computer is thinking...")
        p1_total = self.player_1.get_individual_total()
        p2_total = self.player_2.get_individual_total()
        goal_amount = self.goal_amount
        has_bigger_goal = self.player_2.card_goal.value > self.player_1.card_goal.value
        has_equal_goal = self.player_2.card_goal.value == self.player_1.card_goal.value
        card_give : Card = self.player_2.cards_faceup[self.phase]
        
        trade_info = {
            "0": (p1_total, p2_total, goal_amount, has_bigger_goal, has_equal_goal)  # No trade option
        }
        
        # Simulate a trade with each offer
        for i in range(len(offers)):
            offer : Card = offers[i]
            
            if i < len(offers) - 2:
                p1_total_new = p1_total - offer.value + card_give.value
                p2_total_new = p2_total - card_give.value + offer.value
                goal_amount_new = goal_amount
            else:
                p1_total_new = p1_total
                p2_total_new = p2_total - card_give.value + offer.value
                goal_amount_new = goal_amount - offer.value + card_give.value
            
            if i == len(offers) - 2:
                has_bigger_goal = card_give.value > offer.value
                has_equal_goal = card_give.value == offer.value
            elif i == len(offers) - 1:
                has_bigger_goal = offer.value > card_give.value
                has_equal_goal = offer.value == card_give.value     

            trade_info[str(i+1)] = ( p1_total_new,
                                     p2_total_new,
                                     goal_amount_new,
                                     has_bigger_goal,
                                     has_equal_goal )

        answer = self.player_2.decide_trade(trade_info)
        
        sleep(GAME_DELAY)
        if answer == "0":
            print("Computer declined the trade.")
        else:
            print(f"Computer accepted the trade for {str(offers[int(answer)-1])}")
        self.interface.ask("\nPress enter to continue...", options=[""])
        
        return answer

    def trade_cards(self,
                    trading_player : ClassicPlayer,
                    other_player : ClassicPlayer,
                    offers : list,
                    answer : str):
        
        if answer == "0":
            # If trade offer refused, return from function
            return

        card_give = trading_player.cards_faceup[self.phase]
        card_receive = offers[int(answer)-1]

        if answer == str(len(offers)-1):
            self.player_2.card_goal = card_give
        elif answer == str(len(offers)):
            self.player_1.card_goal = card_give
        else:
            index = other_player.cards_faceup.index(card_receive)
            other_player.cards_faceup[index] = card_give
        
        self.goal_amount = trading_player.card_goal.value + other_player.card_goal.value
        trading_player.cards_faceup[self.phase] = card_receive

    def offer_special_to_player(self, special_player : ClassicPlayer):
        debug(f"SPECIAL OFFERED TO PLAYER 1", DEBUG_FILENAME)
        print("Would they like a special card?")
        question = "[0] No\n[1] Yes\n"
        options = ["0", "1"]
        answer = self.interface.ask(question, options)

        # If no special card, return from function
        if answer == "0":
            return (None, None)
        
        special_card = self.deck.draw_card(special_player, "special")
        self.print_game_state()
        print(f"What would they like to do with their special card?")
        
        question1 = f"[0] Subtract from player {special_player.player_num} total\n"
        question2 = f"[1] Subtract from goal amount\n"
        answer = self.interface.ask(question1 + question2, options)

        return (special_card, answer)

    def offer_special_to_computer(self, special_player : ClassicComputer):
        print("Computer is thinking...")
        p1_total = self.player_1.get_individual_total()
        p2_total = self.player_2.get_individual_total()
        goal_amount = self.goal_amount
        
        special_info = (p1_total, p2_total, goal_amount)
        answer = self.player_2.decide_if_special(special_info)
        sleep(GAME_DELAY)

        # If no special card, return from function
        if answer == "0":
            print("Computer declined the special card.")
            sleep(GAME_DELAY)
            return (None, None)
        
        special_card = self.deck.draw_card(special_player, "special")
        special_value = special_card.value
        self.print_game_state()
        print("Computer accepted the special card")
        print("Computer is deciding how to use it...\n")
        answer = self.player_2.decide_special_effect(special_info, special_value)
        
        sleep(GAME_DELAY)
        if answer == "0":
            print("Computer is subtracting from its total")
        else:
            print("Computer is subtracting from the goal amount")
        self.interface.ask("\nPress enter to continue...", options=[""])
        
        return (special_card, answer)
        
    def use_special_card(self,
                         special_player : ClassicPlayer,
                         special_card : Card,
                         answer : str):
        
        if answer == "0":
            special_player.should_subtract = True
        elif answer == "1":
            p1_total = self.player_1.get_individual_total()
            p2_total = self.player_2.get_individual_total()
            new_goal = self.goal_amount - special_card.value
            
            if p1_total > new_goal and p2_total > new_goal:
                print(f"{BOLD}This option cannot be used to force a tie!{RESET}")
                print("Subtracting from total instead...")
                sleep(GAME_DELAY)
                special_player.should_subtract = True
            else:
                self.goal_amount = new_goal
                
    def play_round(self):
        debug("ROUND START", DEBUG_FILENAME)
        self.setup_game()
        for _ in range(3):
            self.play_phase()
        
        winner = self.determine_winner()
        if winner == 1:
            self.player_1.win()
            self.player_2.lose()
        elif winner == 2:
            self.player_2.win()
            self.player_1.lose()

        self.print_game_state()
        if winner:
            print(f"{BOLD}PLAYER {winner} IS THE WINNER!{RESET}")
        else:
            print(f"{BOLD}THIS ROUND IS A TIE!{RESET}")
        
        sleep(GAME_DELAY)
        debug(f"ROUND END. PLAYER {winner} WINS\n", DEBUG_FILENAME)
        self.reset_game(winner)
    
    def reset_game(self, winner_num : int = None):
        self.interface.clear_screen()
        
        # Update pots if there is a winner
        if winner_num:
            winner = self.players[winner_num-1]
            winner.pot.append(self.player_1.card_goal)
            winner.pot.append(self.player_2.card_goal)
            for player in self.players:
                if player.card_special and not player.should_subtract:
                    winner.pot.append(player.card_special)
                    break
        
        # Print round summary
        self.rounds += 1
        print(f"{BOLD}Round {self.rounds} / 5 complete!{RESET}\n")
        for player in self.players:
            print(f"{BOLD}Player {player.player_num}'s pot:{RESET}", end=' ')
            print(', '.join(str(card) for card in player.pot) if player.pot else "None", end=' ')
            print(f"(Total: ${player.get_pot_total()})")
        print("")
        
        # End game after 5 rounds
        if self.rounds < 5:
            question = f"Press enter to continue to round {self.rounds+1}"
            options = [""]
            answer = self.interface.ask(question, options)
        else:
            p1_pot = self.player_1.get_pot_total()
            p2_pot = self.player_2.get_pot_total()
            if p1_pot != p2_pot:
                game_winner = int(p1_pot < p2_pot) + 1
                game_loser = int(p1_pot > p2_pot) + 1
                winnings = abs(p1_pot - p2_pot)
                print(f"{BOLD}Player {game_winner} wins the game!{RESET}")
                print(f"{BOLD}They win ${winnings} from Player {game_loser}{RESET}\n")
            else:
                print(f"The game ends in a tie with both players having a pot of {BOLD}${p1_pot}!{RESET}\n")
            
            question = f"Press enter to exit the game"
            options = [""]
            answer = self.interface.ask(question, options)
            exit()
        
        # If continuing, reset all game variables
        for player in self.players:
            player.cards_facedown = []
            player.cards_faceup = []
            player.card_goal = None
            player.card_special = None
            player.should_subtract = False

        self.goal_amount = None
        self.phase = 0
        self.play_round()