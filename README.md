# Potluck Poker

Potluck Poker is an original, terminal-based card game. It started as a personal project to see how many original card game concepts I could come up with and implement in Python. Currently, the game features two gamemodes - **Classic** and **Round-Robin** - with the latter still being a work-in-progress.

## How to Play

### Classic

This is a strategic 1v1 game with elements of chance and betting. It is split across 5 rounds, with each round consisting of 4 Phases.

First, three cards are dealt to both players, face-down, in a row. Then, both players draw a card face-up above their center card. (This should form an upside-down T.)

The two revealed cards are called the **Goal Cards**. Their sum is the **Goal Amount** - where Jacks equal 11, Queens = 12, and Kings = 13. So for example, a 7♤ and a K♢ would form a Goal Amount of 20. The players' job is to make the sum of their three face-down cards as close to, but not exceeding, the Goal Amount.

In Phase 1, both players flip over a card. Whichever player has the larger card value may choose to swap their card for any one of the other face-up cards on the table, _including a Goal Card_. If a swap occurs with a Goal Card, the Goal Amount must be recalculated. (If the two players both reveal cards with equal value, nothing happens and they move to the next round.)

Phase 2 and Phase 3 play out exactly like the others. However, in Phase 4, _the player with the larger goal card_ gets to draw a final, **Special Card**. If that player elects to do so, the Special Card can do one of two actions:

1. Place it on top of your Base Cards to subtract this card's value from your own total
2. Place it between the Goal Cards to subtract this card's value from the goal amount

After Phase 4, whichever cards are in the center get added to the winning player's **Pot**. The value of your Pot is the sum of all card values in your Pot. Clear all cards aside and reset back to Phase 1 for the next round.

At the end of Round 5, the player with the smaller Pot must pay out the difference between the two players' Pots. (For example, if Player 1's totals out to **43** and Player 2's totals out to **29**, then Player 2 would pay $14 to Player 1.)

### Round-Robin

WIP

## How to Run

- Install Python
- Navigate to directory
- Run `python potluck_poker.py`
- Press CTRL+C to exit