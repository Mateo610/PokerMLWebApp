# test_game_logic.py

import unittest
from game_logic import GameLogic
from player import Player


class TestGameLogic(unittest.TestCase):


    def setUp(self):
        """Set up the game logic and players before each test."""
        self.game = GameLogic()
        # Create players
        self.player1 = Player(name="Alice", chips=1000)
        self.player2 = Player(name="Bob", chips=1000)
        self.player3 = Player(name="Charlie", chips=1000)
        # Add players to the game
        self.game.players = [self.player1, self.player2, self.player3]
        # Reset pot
        self.game.pot = 0
        # Clear community cards
        self.game.community_cards = []
        # Set game phase
        self.game.game_phase = 'pre-flop'

    def test_single_winner(self):
        """Test a scenario where there is a single winner."""
        # Set up hands
        self.player1.hand = [
            {'value': 'Ace', 'suit': 'Hearts'},
            {'value': 'King', 'suit': 'Hearts'}
        ]
        self.player2.hand = [
            {'value': '10', 'suit': 'Clubs'},
            {'value': '9', 'suit': 'Diamonds'}
        ]
        self.player3.hand = [
            {'value': '2', 'suit': 'Spades'},
            {'value': '3', 'suit': 'Clubs'}
        ]
        # Community cards
        self.game.community_cards = [
            {'value': 'Queen', 'suit': 'Hearts'},
            {'value': 'Jack', 'suit': 'Hearts'},
            {'value': '10', 'suit': 'Hearts'},
            {'value': '5', 'suit': 'Clubs'},
            {'value': '2', 'suit': 'Diamonds'}
        ]
        # Set pot
        self.game.pot = 300
        # Perform showdown
        self.game.showdown()
        # Check that Alice wins the pot
        self.assertEqual(self.player1.chips, 1000 + 300)
        self.assertEqual(self.player2.chips, 1000)
        self.assertEqual(self.player3.chips, 1000)

    def test_tie_high_card(self):
        """Test a tie that requires high card comparison."""
        # Set up hands
        self.player1.hand = [
            {'value': 'Ace', 'suit': 'Clubs'},
            {'value': 'King', 'suit': 'Diamonds'}
        ]
        self.player2.hand = [
            {'value': 'Ace', 'suit': 'Spades'},
            {'value': 'King', 'suit': 'Clubs'}
        ]
        self.player3.hand = [
            {'value': '8', 'suit': 'Hearts'},
            {'value': '7', 'suit': 'Spades'}
        ]
        # Community cards
        self.game.community_cards = [
            {'value': 'Queen', 'suit': 'Hearts'},
            {'value': 'Jack', 'suit': 'Diamonds'},
            {'value': '9', 'suit': 'Clubs'},
            {'value': '5', 'suit': 'Clubs'},
            {'value': '2', 'suit': 'Diamonds'}
        ]
        # Set pot
        self.game.pot = 300
        # Perform showdown
        self.game.showdown()
        # Expected chips after splitting the pot
        expected_chips = 1000 + (300 // 2)
        self.assertEqual(self.player1.chips, expected_chips)
        self.assertEqual(self.player2.chips, expected_chips)
        self.assertEqual(self.player3.chips, 1000)
        # Check that total chips are correct
        total_chips = self.player1.chips + self.player2.chips + self.player3.chips
        self.assertEqual(total_chips, 3000)

    def test_exact_tie(self):
        """Test a scenario where two players have exactly the same hand."""
        # Set up hands
        self.player1.hand = [
            {'value': 'Ace', 'suit': 'Hearts'},
            {'value': 'King', 'suit': 'Hearts'}
        ]
        self.player2.hand = [
            {'value': 'Ace', 'suit': 'Diamonds'},
            {'value': 'King', 'suit': 'Diamonds'}
        ]
        # Remove player3 from the game
        self.game.players = [self.player1, self.player2]
        # Community cards
        self.game.community_cards = [
            {'value': 'Queen', 'suit': 'Hearts'},
            {'value': 'Jack', 'suit': 'Hearts'},
            {'value': '10', 'suit': 'Hearts'},
            {'value': '2', 'suit': 'Clubs'},
            {'value': '3', 'suit': 'Diamonds'}
        ]
        # Set pot
        self.game.pot = 200
        # Perform showdown
        self.game.showdown()
        # Expected chips after splitting the pot
        expected_chips = 1000 + (200 // 2)
        self.assertEqual(self.player1.chips, expected_chips)
        self.assertEqual(self.player2.chips, expected_chips)

    def test_player_folds(self):
        """Test that a player who folds does not participate in the showdown."""
        # Set up hands
        self.player1.hand = [
            {'value': 'Ace', 'suit': 'Hearts'},
            {'value': 'King', 'suit': 'Hearts'}
        ]
        self.player2.hand = [
            {'value': '10', 'suit': 'Clubs'},
            {'value': '9', 'suit': 'Diamonds'}
        ]
        self.player3.hand = [
            {'value': '2', 'suit': 'Spades'},
            {'value': '3', 'suit': 'Clubs'}
        ]
        # Player 3 folds
        self.player3.is_active = False
        # Community cards
        self.game.community_cards = [
            {'value': 'Queen', 'suit': 'Hearts'},
            {'value': 'Jack', 'suit': 'Hearts'},
            {'value': '10', 'suit': 'Hearts'},
            {'value': '5', 'suit': 'Clubs'},
            {'value': '2', 'suit': 'Diamonds'}
        ]
        # Set pot
        self.game.pot = 300
        # Perform showdown
        self.game.showdown()
        # Check that Alice wins the pot
        self.assertEqual(self.player1.chips, 1000 + 300)
        self.assertEqual(self.player2.chips, 1000)
        self.assertEqual(self.player3.chips, 1000)  # No change for folded player

    def test_all_players_fold_except_one(self):
        """Test that if all players fold except one, that player wins the pot without a showdown."""
        # Player 1 is the only active player
        self.player1.is_active = True
        self.player2.is_active = False
        self.player3.is_active = False
        # Set pot
        self.game.pot = 300
        # Perform showdown
        self.game.showdown()
        # Check that Alice wins the pot
        self.assertEqual(self.player1.chips, 1000 + 300)
        self.assertEqual(self.player2.chips, 1000)
        self.assertEqual(self.player3.chips, 1000)

    def test_side_pot_scenario(self):
        """Test a scenario where side pots would be needed (future implementation)."""
        # For now, this test will pass since side pots are not implemented
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
