import os
from random import shuffle

class Card:
    def __init__(self, card : str):
        self.display = card
        self.value = self.get_card_value(card)
        self.suit = self.get_suit(card)
    
    def __str__(self):
        return self.display

    def get_card_value(self, card : str):
        value = card[:-1]
        if value.isdigit():
            return int(value)
        elif value == "J":
            return 11
        elif value == "Q":
            return 12
        elif value == "K":
            return 13
        elif value == "A":
            return 1
        else:
            raise ValueError(f"Invalid card value: {card}")
    
    def get_suit(self, card : str):
        suit = card[-1]
        suits = {"♥": "Hearts", "♦": "Diamonds", "♣": "Clubs", "♠": "Spades"}
        return suits.get(suit, "Unknown")


class Player:
    def __init__(self, player_num = 1, wins = 0, losses = 0):
        self.player_num = player_num
        self.wins = wins
        self.losses = losses
    
    def receive_card(self, card : Card, type : str):
        pass
        
    def win(self):
        self.wins += 1

    def lose(self):
        self.losses += 1
 

class Deck:
    def __init__(self):
        vals = [2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K", "A"]
        suits = ["♥", "♦", "♣", "♠"]
        self.cards = [Card(f"{val}{suit}") for val in vals for suit in suits]
        self.initial_deck = self.cards.copy()  # Store initial deck state for reset
        self.shuffle_deck()
    
    def shuffle_deck(self):
        shuffle(self.cards)
    
    def reset_deck(self):
        self.cards = self.initial_deck.copy()
        self.shuffle_deck()

    def draw_card(self, player : Player, type : str) -> Card:
        if not self.cards:
            raise ValueError("No cards left in the deck")
        card = self.cards.pop()
        player.receive_card(card, type)
        return card
 

class Interface:
    def __init__(self):
        pass

    def clear_screen(self):
        if os.name == 'nt':  # For Windows
            _ = os.system('cls')
        else:  # For macOS and Linux
            _ = os.system('clear')
    
    def ask(self, question : str, options : list):
        while True:
            response = input(question).lower().strip()
            if response in options:
                print("")
                return response
            print("Invalid response. Try again")