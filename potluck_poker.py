from constants import BOLD, UNDERLINE, RESET
from game_utilities import Interface
from gamemodes.classic import ClassicGame
from gamemodes.round_robin import RoundRobinGame

if __name__ == "__main__":
    interface = Interface()
    interface.clear_screen()

    print(f"Welcome to {BOLD}{UNDERLINE}Potluck Poker!{RESET}")
    print("Which game mode would you like to play?")
    print("[0] Classic")
    print("[1] Round-Robin")
    print("[2] ...")
    options = list(map(str, range(3)))
    gamemode = interface.ask("", options)

    if gamemode == "0":
        print(f"Would you like to play singleplayer or multiplayer?")
        print("[0] Singleplayer")
        print("[1] Multiplayer")
        options = list(map(str, range(2)))
        is_singleplayer = (interface.ask("", options) == "0")
        
        print("Starting classic game mode...")
        try:
            new_game = ClassicGame(singleplayer = is_singleplayer)
            new_game.play_round()
        except Exception as e:
            print("\nException occurred:", e)
            print("Occurred on line", e.__traceback__.tb_lineno, "of", e.__traceback__.tb_frame.f_code.co_name, sep=" ")
            interface.ask("\nPress Enter to exit...", [""])
        finally:
            interface.clear_screen()
            print(f"Thanks for playing {BOLD}{UNDERLINE}Potluck Poker!{RESET}")
            exit()
        
    elif gamemode == "1":
        min_players = 1
        max_players = 4
        
        print(f"How many players would you like? (1-4)")
        options = list(map(str, range(1, 5)))
        num_players = int(interface.ask("", options))
        
        if num_players < max_players:
            min_computers = int(num_players == min_players)
            max_computers = max_players - num_players
            
            print(f"How many computer players would you like? ({min_computers}-{max_computers})")
            options = list(map(str, range(min_computers, 1 + max_computers)))
            num_computers = int(interface.ask("", options))
        else:
            num_computers = 0
        
        print("Starting round-robin game mode...")
        try:
            new_game = RoundRobinGame(num_players, num_computers)
            new_game.setup_game()
            new_game.play_round()
        except Exception as e:
            print("\nException occurred:", e)
            print("Occurred on line", e.__traceback__.tb_lineno, "of", e.__traceback__.tb_frame.f_code.co_name, sep=" ")
            interface.ask("\nPress Enter to exit...", [""])
        finally:
            interface.clear_screen()
            print(f"Thanks for playing {BOLD}{UNDERLINE}Potluck Poker!{RESET}")
            exit()