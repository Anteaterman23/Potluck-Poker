import os
import sys
from time import sleep
from constants import BOLD, RESET, GAME_DELAY
from game_utilities import Card, Deck, Player, Interface
from typing import List

# TODO: Add computers
# TODO: Add debug logging

current_script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_script_dir, os.pardir))
sys.path.append(parent_dir)

class RoundRobinPlayer(Player):
    def __init__(self, player_num = 1):
        super().__init__(player_num)
        self.pot_card : Card = None
        self.add_pile : List[Card] = []
        self.subtract_pile : List[Card] = []
        self.face_down : Card = None
        self.face_down_visible = False
        self.alive = True

    def receive_card(self, card : Card, type : str):
        if type == "pot":
            self.pot_card = card
        elif type == "add":
            self.add_pile.append(card)
        elif type == "subtract":
            self.subtract_pile.append(card)
        elif type == "facedown":
            self.face_down = card
        else:
            raise ValueError(f"Unknown card type: {type}")
    
    def get_total(self):
        return sum(c.value for c in self.add_pile) - sum(c.value for c in self.subtract_pile)

    def eliminate(self):
        self.add_pile = []
        self.subtract_pile = []
        self.face_down = None
        self.face_down_visible = False
        self.alive = False
        
    def print_player_info(self):
        print(f"{BOLD}PLAYER {self.player_num} INFO{RESET}")
        print(f" Pot Card: {self.pot_card}")
        print(f" Add Pile: {', '.join(str(c) for c in self.add_pile) if self.add_pile else 'None'}")
        print(f" Subtract Pile: {', '.join(str(c) for c in self.subtract_pile) if self.subtract_pile else 'None'}")
        print(f" Face-Down Card: {self.face_down if self.face_down_visible else '??'}")
        print(f" Total: {BOLD}{self.get_total()}{RESET}")


class RoundRobinComputer(RoundRobinPlayer):
    def __init__(self, player_num):
        super().__init__(player_num)
        # TODO: Add computer players to game


class RoundRobinGame:
    def __init__(self, num_players = 4, num_computers = 0):
        # Game variables
        self.deck = Deck()
        self.interface = Interface()
        self.goal_amount = 0
        self.turn_index = 0
        self.players : List[RoundRobinPlayer | RoundRobinComputer] = []
        
        # Player initialization
        players, computers = 0, 0
        player_num = 1
        while players < num_players:
            self.players.append(RoundRobinPlayer(player_num))
            players += 1
            player_num += 1
        while computers < num_computers:
            self.players.append(RoundRobinComputer(player_num))
            computers += 1
            player_num += 1

    def setup_game(self):
        # Pot cards
        for p in self.players:
            self.deck.draw_card(p, "pot")
        self.goal_amount = sum(p.pot_card.value for p in self.players)

        # Add piles (two cards)
        for p in self.players:
            for _ in range(2):
                self.deck.draw_card(p, "add")
                if p.get_total() > self.goal_amount:
                    # Return last card to bottom of deck if over goal
                    self.deck.cards.insert(0, p.add_pile.pop())
                    break

        # Face-down
        for p in self.players:
            self.deck.draw_card(p, "facedown")

    def get_right_neighbor(self, idx : int) -> int:
        n = len(self.players)
        candidate = (idx - 1) % n
        while not self.players[candidate].alive:
            candidate = (candidate - 1) % n
            if candidate == idx:
                return None  # only one player alive
        return candidate

    def next_turn(self):
        n = len(self.players)
        self.turn_index = (self.turn_index + 1) % n
        while not self.players[self.turn_index].alive:
            self.turn_index = (self.turn_index + 1) % n

    def eliminate_player(self, player: RoundRobinPlayer):
        player.eliminate()

    def print_game_state(self):
        self.interface.clear_screen()
        current = self.players[self.turn_index]
        opponent = self.players[self.get_right_neighbor(self.turn_index)]
        
        for p in [current, opponent]:
            p.print_player_info()
            print("-" * 40)
            
        print(f"Goal Amount (Pot): {BOLD}{self.goal_amount}{RESET}")
        print(f"Current Turn: {BOLD}Player {current.player_num} vs. Player {opponent.player_num}{RESET}")
        print("-" * 40)
    
    def print_winner(self, winner : RoundRobinPlayer | str, reason : str):
        self.interface.clear_screen()
        if reason == "Tie":
            print(f"{BOLD}It's a tie! No players remain.{RESET}")
            self.interface.ask("\nPress Enter to exit...", [""])
            exit()
        elif reason == "Closest to goal":
            print(f"{BOLD}Player {winner.player_num} wins the game by being closest to the goal!{RESET}")
            print(f"(Total: {winner.get_total()}, Goal: {self.goal_amount})")
        elif reason == "Exact match":
            print(f"{BOLD}Player {winner.player_num} wins the game by hitting the exact goal amount!{RESET}")
        elif reason == "Last player standing":
            print(f"{BOLD}Player {winner.player_num} wins the game as the last player standing!{RESET}")
        print("")
        
        sleep(GAME_DELAY)
        total_reward = 0
        for p in self.players:
            if p != winner:
                total_reward += p.pot_card.value
                print(f"They win {BOLD}${p.pot_card.value}{RESET} from Player {p.player_num}.")
        print(f"(Total Winnings: {BOLD}${total_reward}{RESET})")
    
    def play_round(self):
        winner, reason = self.check_victory()
        if winner is not None:
            self.print_winner(winner, reason)
            self.interface.ask("\nPress Enter to exit...", [""])
            exit()
        else:
            self.print_game_state()
            sleep(GAME_DELAY)
        
        n = len(self.players)
        current = self.players[self.turn_index]
        opponent_idx = self.get_right_neighbor(self.turn_index)
        if opponent_idx is None:
            return  # only one player alive
        opponent = self.players[opponent_idx]

        # --- STEP 1: Choice of add/subtract piles ---
        question = (
            f"Player {current.player_num}, do you want your face-down card "
            f"to go into your add pile or subtract pile?\n"
            "[0] Add\n[1] Subtract\n"
        )
        choice = self.interface.ask(question, ["0", "1"])
        if choice == "0":
            current_choice = "add"
            opposite_choice = "subtract"
        else:
            current_choice = "subtract"
            opposite_choice = "add"

        # --- STEP 2: Flip both cards, reveal only suits first ---
        self.print_game_state()
        card_current = current.face_down
        card_opponent = opponent.face_down
        print(f"Player {current.player_num} reveals suit {card_current.suit}")
        print(f"Player {opponent.player_num} reveals suit {card_opponent.suit}")
        sleep(GAME_DELAY)

        # --- STEP 3: Suit match case ---
        if card_current.suit == card_opponent.suit:
            self.print_game_state()
            print("Suits match! Both players must swap with the face-down card to their left.")
            self.interface.ask("Press Enter to continue...", [""])

            # Find left neighbors
            left_of_current_idx = (self.turn_index + 1) % n
            while not self.players[left_of_current_idx].alive:
                left_of_current_idx = (left_of_current_idx + 1) % n
            
            left_of_current = self.players[left_of_current_idx]
            left_of_opponent = current

            # Swap with left neighbors
            current.face_down, left_of_current.face_down = (
                left_of_current.face_down,
                current.face_down,
            )

            opponent.face_down, left_of_opponent.face_down = (
                left_of_opponent.face_down,
                opponent.face_down,
            )

        else:
            # --- STEP 4: Reveal both card values ---
            current.face_down_visible = True
            opponent.face_down_visible = True
            self.print_game_state()
            print(f"Player {current.player_num} reveals {str(card_current)}")
            print(f"Player {opponent.player_num} reveals {str(card_opponent)}\n")
            sleep(GAME_DELAY)

            # --- STEP 5: Larger card may swap with pot ---
            if card_current.value > card_opponent.value:
                winner = current
                card_winner = card_current
            elif card_opponent.value > card_current.value:
                winner = opponent
                card_winner = card_opponent
            else:
                winner = None

            if winner:
                choice = current_choice if winner == current else opposite_choice
                
                print(f"Player {winner.player_num}, would you like to trade your {str(card_winner)} for a pot card?")
                print(f"(This will be added to your {choice} pile.)\n")
                print("[0] No")
                for i, p in enumerate(self.players, start=1):
                    print(f"[{i}] {str(p.pot_card)}")
                options = list(map(str, range(n+1)))
                answer = self.interface.ask("", options)

                if answer != "0":
                    chosen_idx = int(answer) - 1
                    chosen_pot = self.players[chosen_idx].pot_card
                    # Swap
                    self.players[chosen_idx].pot_card = card_winner
                    if winner == current:
                        card_current = chosen_pot
                    else:
                        card_opponent = chosen_pot
                    self.goal_amount = sum(p.pot_card.value for p in self.players)
            else:
                print("Card values are equal! No swaps this round.\n")
                sleep(GAME_DELAY)

        # --- STEP 6: Place cards into piles ---
        current.face_down_visible = False
        opponent.face_down_visible = False
        
        if current_choice == "add":
            current.add_pile.append(card_current)
        else:
            current.subtract_pile.append(card_current)

        if opposite_choice == "add":
            opponent.add_pile.append(card_opponent)
        else:
            opponent.subtract_pile.append(card_opponent)
            
        self.print_game_state()
        print(f"Player {current.player_num} placed {str(card_current)} into their {current_choice} pile.")
        print(f"Player {opponent.player_num} placed {str(card_opponent)} into their {opposite_choice} pile.")
        self.interface.ask("Press Enter to continue...", [""])

        # --- STEP 7: Elimination checks ---
        self.print_game_state()
        for p in [current, opponent]:
            total = p.get_total()
            if total > self.goal_amount or total < 0:
                print(f"Player {p.player_num} eliminated! (Total: {total})")
                self.eliminate_player(p)
                self.interface.ask("Press Enter to continue...", [""])

        # --- STEP 8: Replenish face-downs ---
        if current.alive:
            self.deck.draw_card(current, "facedown")
        if opponent.alive:
            self.deck.draw_card(opponent, "facedown")

        # Advance turn
        self.next_turn()
        self.play_round()

    def check_victory(self):
        # Deck runs out
        if not self.deck.cards:
            alive = [p for p in self.players if p.alive]
            if not alive:
                return "Tie", "Tie"
            elif len(alive) == 1:
                return alive[0], "Last player standing"
            return min(alive, key=lambda p: abs(self.goal_amount - p.get_total())), "Closest to goal"
        
        # Immediate win
        for p in self.players:
            if p.alive and p.get_total() == self.goal_amount:
                return p, "Exact match"
        
        return None, None