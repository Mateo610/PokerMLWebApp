# test_hand_evaluator.py

import unittest
from hand_evaluator import evaluate_hand, HAND_RANKS

class TestHandEvaluator(unittest.TestCase):

    def test_royal_flush(self):
        cards = [
            {'value': 'Ace', 'suit': 'Hearts'},
            {'value': 'King', 'suit': 'Hearts'},
            {'value': 'Queen', 'suit': 'Hearts'},
            {'value': 'Jack', 'suit': 'Hearts'},
            {'value': '10', 'suit': 'Hearts'},
            {'value': '3', 'suit': 'Diamonds'},
            {'value': '2', 'suit': 'Clubs'}
        ]
        rank, high_cards = evaluate_hand(cards)
        self.assertEqual(rank, HAND_RANKS['Royal Flush'])
        self.assertEqual(high_cards, [14])

    def test_straight_flush(self):
        cards = [
            {'value': '9', 'suit': 'Spades'},
            {'value': '8', 'suit': 'Spades'},
            {'value': '7', 'suit': 'Spades'},
            {'value': '6', 'suit': 'Spades'},
            {'value': '5', 'suit': 'Spades'},
            {'value': 'King', 'suit': 'Hearts'},
            {'value': '2', 'suit': 'Clubs'}
        ]
        rank, high_cards = evaluate_hand(cards)
        self.assertEqual(rank, HAND_RANKS['Straight Flush'])
        self.assertEqual(high_cards, [9, 8, 7, 6, 5])

    def test_four_of_a_kind(self):
        cards = [
            {'value': 'Ace', 'suit': 'Clubs'},
            {'value': 'Ace', 'suit': 'Diamonds'},
            {'value': 'Ace', 'suit': 'Hearts'},
            {'value': 'Ace', 'suit': 'Spades'},
            {'value': 'King', 'suit': 'Hearts'},
            {'value': '3', 'suit': 'Diamonds'},
            {'value': '2', 'suit': 'Clubs'}
        ]
        rank, high_cards = evaluate_hand(cards)
        self.assertEqual(rank, HAND_RANKS['Four of a Kind'])
        self.assertEqual(high_cards, [14, 13])  # Four Aces with King kicker

    def test_full_house(self):
        cards = [
            {'value': 'Queen', 'suit': 'Hearts'},
            {'value': 'Queen', 'suit': 'Diamonds'},
            {'value': 'Queen', 'suit': 'Clubs'},
            {'value': 'Jack', 'suit': 'Hearts'},
            {'value': 'Jack', 'suit': 'Spades'},
            {'value': '9', 'suit': 'Clubs'},
            {'value': '2', 'suit': 'Diamonds'}
        ]
        rank, high_cards = evaluate_hand(cards)
        self.assertEqual(rank, HAND_RANKS['Full House'])
        self.assertEqual(high_cards, [12, 11])  # Queens full of Jacks

    def test_flush(self):
        cards = [
            {'value': 'King', 'suit': 'Clubs'},
            {'value': 'Jack', 'suit': 'Clubs'},
            {'value': '9', 'suit': 'Clubs'},
            {'value': '7', 'suit': 'Clubs'},
            {'value': '3', 'suit': 'Clubs'},
            {'value': 'Ace', 'suit': 'Hearts'},
            {'value': '2', 'suit': 'Spades'}
        ]
        rank, high_cards = evaluate_hand(cards)
        self.assertEqual(rank, HAND_RANKS['Flush'])
        self.assertEqual(high_cards, [13, 11, 9, 7, 3])  # Highest cards in the flush

    def test_straight(self):
        cards = [
            {'value': '9', 'suit': 'Hearts'},
            {'value': '8', 'suit': 'Diamonds'},
            {'value': '7', 'suit': 'Clubs'},
            {'value': '6', 'suit': 'Spades'},
            {'value': '5', 'suit': 'Hearts'},
            {'value': '2', 'suit': 'Clubs'},
            {'value': 'King', 'suit': 'Diamonds'}
        ]
        rank, high_cards = evaluate_hand(cards)
        self.assertEqual(rank, HAND_RANKS['Straight'])
        self.assertEqual(high_cards, [9, 8, 7, 6, 5])

    def test_ace_low_straight(self):
        cards = [
            {'value': 'Ace', 'suit': 'Clubs'},
            {'value': '2', 'suit': 'Hearts'},
            {'value': '3', 'suit': 'Diamonds'},
            {'value': '4', 'suit': 'Spades'},
            {'value': '5', 'suit': 'Hearts'},
            {'value': '9', 'suit': 'Clubs'},
            {'value': 'King', 'suit': 'Diamonds'}
        ]
        rank, high_cards = evaluate_hand(cards)
        self.assertEqual(rank, HAND_RANKS['Straight'])
        self.assertEqual(high_cards, [5, 4, 3, 2, 1])  # Ace-low straight

    def test_three_of_a_kind(self):
        cards = [
            {'value': '10', 'suit': 'Hearts'},
            {'value': '10', 'suit': 'Diamonds'},
            {'value': '10', 'suit': 'Clubs'},
            {'value': 'King', 'suit': 'Spades'},
            {'value': '5', 'suit': 'Hearts'},
            {'value': '3', 'suit': 'Clubs'},
            {'value': '2', 'suit': 'Diamonds'}
        ]
        rank, high_cards = evaluate_hand(cards)
        self.assertEqual(rank, HAND_RANKS['Three of a Kind'])
        self.assertEqual(high_cards, [10, 13, 5])  # Three Tens with King and 5 kickers

    def test_two_pair(self):
        cards = [
            {'value': 'Jack', 'suit': 'Hearts'},
            {'value': 'Jack', 'suit': 'Diamonds'},
            {'value': '9', 'suit': 'Clubs'},
            {'value': '9', 'suit': 'Spades'},
            {'value': '5', 'suit': 'Hearts'},
            {'value': '3', 'suit': 'Clubs'},
            {'value': '2', 'suit': 'Diamonds'}
        ]
        rank, high_cards = evaluate_hand(cards)
        self.assertEqual(rank, HAND_RANKS['Two Pair'])
        self.assertEqual(high_cards, [11, 9, 5])  # Jacks and Nines with 5 kicker

    def test_one_pair(self):
        cards = [
            {'value': 'Queen', 'suit': 'Hearts'},
            {'value': 'Queen', 'suit': 'Diamonds'},
            {'value': '10', 'suit': 'Clubs'},
            {'value': '8', 'suit': 'Spades'},
            {'value': '6', 'suit': 'Hearts'},
            {'value': '4', 'suit': 'Clubs'},
            {'value': '2', 'suit': 'Diamonds'}
        ]
        rank, high_cards = evaluate_hand(cards)
        self.assertEqual(rank, HAND_RANKS['One Pair'])
        self.assertEqual(high_cards, [12, 10, 8, 6])  # Pair of Queens with kickers

    def test_high_card(self):
        cards = [
            {'value': 'Ace', 'suit': 'Hearts'},
            {'value': 'King', 'suit': 'Diamonds'},
            {'value': '10', 'suit': 'Clubs'},
            {'value': '8', 'suit': 'Spades'},
            {'value': '6', 'suit': 'Hearts'},
            {'value': '4', 'suit': 'Clubs'},
            {'value': '2', 'suit': 'Diamonds'}
        ]
        rank, high_cards = evaluate_hand(cards)
        self.assertEqual(rank, HAND_RANKS['High Card'])
        self.assertEqual(high_cards, [14, 13, 10, 8, 6])  # High card Ace

    def test_tie_breaker(self):
        # Two hands with the same rank but different high cards
        hand1 = [
            {'value': 'King', 'suit': 'Hearts'},
            {'value': 'King', 'suit': 'Diamonds'},
            {'value': '10', 'suit': 'Clubs'},
            {'value': '8', 'suit': 'Spades'},
            {'value': '6', 'suit': 'Hearts'},
            {'value': '4', 'suit': 'Clubs'},
            {'value': '2', 'suit': 'Diamonds'}
        ]
        rank1, high_cards1 = evaluate_hand(hand1)

        hand2 = [
            {'value': 'King', 'suit': 'Clubs'},
            {'value': 'King', 'suit': 'Spades'},
            {'value': 'Jack', 'suit': 'Clubs'},
            {'value': '7', 'suit': 'Hearts'},
            {'value': '5', 'suit': 'Diamonds'},
            {'value': '3', 'suit': 'Spades'},
            {'value': '2', 'suit': 'Hearts'}
        ]
        rank2, high_cards2 = evaluate_hand(hand2)

        self.assertEqual(rank1, HAND_RANKS['One Pair'])
        self.assertEqual(rank2, HAND_RANKS['One Pair'])

        # Compare high cards
        self.assertTrue(high_cards1 < high_cards2)  # Hand2 should win due to higher kickers

if __name__ == '__main__':
    unittest.main()
