# hand_evaluator.py

from collections import Counter
from itertools import combinations

# Define hand ranks
HAND_RANKS = {
    'High Card': 1,
    'One Pair': 2,
    'Two Pair': 3,
    'Three of a Kind': 4,
    'Straight': 5,
    'Flush': 6,
    'Full House': 7,
    'Four of a Kind': 8,
    'Straight Flush': 9,
    'Royal Flush': 10
}

# Map card values to numerical ranks
CARD_VALUE_RANKS = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
    '7': 7, '8': 8, '9': 9, '10': 10,
    'Jack': 11, 'Queen': 12, 'King': 13, 'Ace': 14
}

def evaluate_hand(cards):
    """
    Evaluates the best poker hand from the given set of cards.
    Returns a tuple (hand_rank, high_cards).
    """
    if len(cards) < 5:
        return HAND_RANKS['High Card'], get_high_cards(cards)

    possible_hands = combinations(cards, 5)
    best_rank = 0
    best_high_cards = []

    for hand in possible_hands:
        rank, high_cards = evaluate_five_card_hand(hand)
        if rank > best_rank or (rank == best_rank and high_cards > best_high_cards):
            best_rank = rank
            best_high_cards = high_cards

            # Early exit if Royal Flush is found
            if best_rank == HAND_RANKS['Royal Flush']:
                break

    return best_rank, best_high_cards

def evaluate_five_card_hand(hand):
    """Evaluates a 5-card poker hand and returns its rank and high cards."""
    values = [card['value'] for card in hand]
    suits = [card['suit'] for card in hand]
    value_counts = Counter(values)
    suit_counts = Counter(suits)

    is_flush = len(suit_counts) == 1
    sorted_values = sorted([CARD_VALUE_RANKS[v] for v in values], reverse=True)
    unique_values = sorted(set(sorted_values), reverse=True)

    # Adjust for Ace-low straight (Wheel)
    if set(sorted_values) == {14, 5, 4, 3, 2}:
        is_straight = True
        sorted_values = [5, 4, 3, 2, 1]  # Treat Ace as 1
        unique_values = sorted(set(sorted_values), reverse=True)
    else:
        is_straight = len(unique_values) == 5 and unique_values[0] - unique_values[-1] == 4

    # Check for Royal Flush
    if is_flush and is_straight and unique_values[0] == CARD_VALUE_RANKS['Ace']:
        return HAND_RANKS['Royal Flush'], [14]

    # Check for Straight Flush
    if is_flush and is_straight:
        return HAND_RANKS['Straight Flush'], unique_values

    # Check for Four of a Kind
    if 4 in value_counts.values():
        four_value = get_keys_from_value(value_counts, 4)[0]
        kicker = [v for v in sorted_values if v != CARD_VALUE_RANKS[four_value]]
        return HAND_RANKS['Four of a Kind'], [CARD_VALUE_RANKS[four_value]] + kicker

    # Check for Full House
    if 3 in value_counts.values() and 2 in value_counts.values():
        three_values = get_keys_from_value(value_counts, 3)
        pair_values = get_keys_from_value(value_counts, 2)
        high_cards = sorted([CARD_VALUE_RANKS[v] for v in three_values], reverse=True)
        high_cards += sorted([CARD_VALUE_RANKS[v] for v in pair_values], reverse=True)
        return HAND_RANKS['Full House'], high_cards

    # Check for Flush
    if is_flush:
        return HAND_RANKS['Flush'], sorted_values

    # Check for Straight
    if is_straight:
        return HAND_RANKS['Straight'], unique_values

    # Check for Three of a Kind
    if 3 in value_counts.values():
        three_value = get_keys_from_value(value_counts, 3)[0]
        kickers = [v for v in sorted_values if v != CARD_VALUE_RANKS[three_value]]
        return HAND_RANKS['Three of a Kind'], [CARD_VALUE_RANKS[three_value]] + kickers

    # Check for Two Pair
    if list(value_counts.values()).count(2) == 2:
        pair_values = get_keys_from_value(value_counts, 2)
        high_pair, low_pair = sorted([CARD_VALUE_RANKS[v] for v in pair_values], reverse=True)
        kickers = [v for v in sorted_values if v not in [high_pair, low_pair]]
        return HAND_RANKS['Two Pair'], [high_pair, low_pair] + kickers

    # Check for One Pair
    if 2 in value_counts.values():
        pair_value = get_keys_from_value(value_counts, 2)[0]
        kickers = [v for v in sorted_values if v != CARD_VALUE_RANKS[pair_value]]
        return HAND_RANKS['One Pair'], [CARD_VALUE_RANKS[pair_value]] + kickers

    # High Card
    return HAND_RANKS['High Card'], sorted_values

def get_keys_from_value(counter, target_value):
    """Returns a list of keys from the counter corresponding to the target value."""
    return [k for k, v in counter.items() if v == target_value]

def get_high_cards(cards):
    """Returns a list of card ranks in descending order."""
    values = [CARD_VALUE_RANKS[card['value']] for card in cards]
    return sorted(values, reverse=True)

def compare_hands(hand1, hand2):
    """
    Compares two hands and returns:
    - 1 if hand1 wins
    - -1 if hand2 wins
    - 0 if it's a tie
    """
    rank1, high_cards1 = evaluate_hand(hand1)
    rank2, high_cards2 = evaluate_hand(hand2)

    if rank1 > rank2:
        return 1
    elif rank1 < rank2:
        return -1
    else:
        # Compare high cards
        for hc1, hc2 in zip(high_cards1, high_cards2):
            if hc1 > hc2:
                return 1
            elif hc1 < hc2:
                return -1
        return 0  # Tie
