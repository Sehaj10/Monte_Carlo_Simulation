import streamlit as st
import numpy as np
import pandas as pd
from collections import defaultdict

# Constants
NUM_SIMULATIONS = 100000  # Number of rounds to simulate
DECKS = 6  # Number of decks in the shoe
BLACKJACK = 21

# Possible actions
ACTIONS = ['Hit', 'Stand', 'Double', 'Split']

# Basic strategy decisions
def basic_strategy(player_hand, dealer_card):
    """Determines the basic strategy action for a given hand and dealer's card."""
    total = adjust_for_aces(player_hand)
    if total <= 11:
        return 'Hit'
    elif total >= 17:
        return 'Stand'
    elif total >= 12 and total <= 16:
        if dealer_card >= 7 or dealer_card == 1:
            return 'Hit'
        else:
            return 'Stand'
    return 'Stand'

# Simulate card drawing
def draw_card(deck, card_index):
    """Draw a card using an index and reshuffle if the deck is empty."""
    card = deck[card_index]
    return card

# Card counting function
def card_counting(deck):
    count = 0
    for card in deck:
        if card in [2, 3, 4, 5, 6]:
            count += 1
        elif card in [10, 'J', 'Q', 'K', 'A']:
            count -= 1
    return count

# Convert card face to value
def card_value(card):
    if card in ['J', 'Q', 'K']:
        return 10
    elif card == 'A':
        return 11  # Default ace to 11, adjust later if needed
    return int(card)

# Adjust ace values in the hand
def adjust_for_aces(hand):
    total = sum(card_value(card) for card in hand)
    num_aces = hand.count('A')

    while total > BLACKJACK and num_aces:
        total -= 10
        num_aces -= 1

    return total

# Run Monte Carlo Simulation
def monte_carlo_blackjack():
    results = defaultdict(lambda: defaultdict(int))

    for _ in range(NUM_SIMULATIONS):
        # Initialize deck and shuffle
        deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K', 'A'] * 4 * DECKS
        np.random.shuffle(deck)

        # Index to track current position in the deck
        current_index = 0

        # Draw initial cards
        player_hand = [draw_card(deck, current_index), draw_card(deck, current_index + 1)]
        current_index += 2
        dealer_hand = [draw_card(deck, current_index), draw_card(deck, current_index + 1)]
        current_index += 2

        # Adjust hands for aces
        player_total = adjust_for_aces(player_hand)
        dealer_card = card_value(dealer_hand[0])

        # Calculate card count
        count = card_counting(deck)

        # Determine basic strategy action
        action = basic_strategy(player_hand, dealer_card)

        # Adjust strategy with card counting
        if count > 5 and 'Double' in ACTIONS and player_total in range(9, 12):
            action = 'Double'

        # Splitting pairs logic
        if player_hand[0] == player_hand[1]:
            if player_hand[0] in [8, 'A']:
                action = 'Split'

        # Log result
        results[(player_total, dealer_card)][action] += 1

    return results

# Convert results to a strategy matrix
def create_strategy_matrix(results):
    matrix = pd.DataFrame(index=range(4, 22), columns=range(2, 12))
    for (player_total, dealer_card), actions in results.items():
        if player_total >= 4 and player_total <= 21:
            if dealer_card == 11:
                dealer_card = 'A'
            # Determine the action with the highest occurrence
            most_common_action = max(actions, key=actions.get)
            matrix.loc[player_total, dealer_card] = most_common_action
    return matrix

# Function to get user input and determine strategy
def user_input_strategy(strategy_matrix, player_hand, dealer_hand):
    # Parse player and dealer cards
    player_hand_values = [card_value(card) for card in player_hand]
    dealer_hand_values = [card_value(card) for card in dealer_hand]

    # Adjust hands for aces
    player_total = adjust_for_aces(player_hand_values)
    dealer_card = card_value(dealer_hand[0])

    # Retrieve action from strategy matrix
    if dealer_card == 11:
        dealer_card = 'A'
        
    if player_total < 4 or player_total > 21:
        return "Invalid hand total."

    action = strategy_matrix.loc[player_total, dealer_card]

    return f"Recommended action for player total {player_total} against dealer card {dealer_card}: {action}"

# Run the simulation and create the matrix
results = monte_carlo_blackjack()
strategy_matrix = create_strategy_matrix(results)

# Streamlit Interface
st.title("Blackjack using Monte Carlo Simulation")

st.write("Enter up to 4 player cards and the dealer's visible card:")

# Player cards input
player_input = st.text_input("Player Cards (e.g., '10 A 5 6'):", value='10 A')
player_hand = player_input.split()

# Dealer card input
dealer_input = st.text_input("Dealer Card (e.g., '7'):", value='7')
dealer_hand = dealer_input.split()

# Validate input and determine strategy
if len(player_hand) > 4 or len(dealer_hand) > 4:
    st.error("Error: You can enter up to 4 cards for each player and dealer.")
else:
    result = user_input_strategy(strategy_matrix, player_hand, dealer_hand)
    st.success(result)

# Display the strategy matrix
st.write(" Strategy Matrix:")
st.dataframe(strategy_matrix)

