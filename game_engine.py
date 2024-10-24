# game_engine.py

import random
from hand_evaluator import evaluate_hand, HAND_RANKS
from player import Player
from poker_bot import PokerBot

class GameEngine:
    def __init__(self, players_count=2, initial_chips=1000):
        self.players = []
        self.community_cards = []
        self.pot = 0
        self.deck = []
        self.current_bet = 0
        self.game_phase = 'pre-flop'
        self.small_blind = 10
        self.big_blind = 20
        self.dealer_position = 0  # Index of the dealer
        self.active_players = []
        self.initial_chips = initial_chips

        # Initialize players
        for i in range(players_count):
            if i == 0:
                # The first player is the human player
                self.players.append(Player(name="Player", chips=self.initial_chips))
            else:
                # Add AI bots
                self.players.append(PokerBot(name=f"AI Bot {i}", chips=self.initial_chips))

    def start_game(self):
        """Starts a new game of poker."""
        self.shuffle_and_deal()
        self.initialize_round()

    def shuffle_and_deal(self):
        """Shuffles the deck and deals two cards to each player."""
        self.deck = self.create_deck()
        random.shuffle(self.deck)

        # Clear previous hands
        for player in self.players:
            player.hand = []
            player.is_active = True
            player.is_all_in = False
            player.current_bet = 0

        # Deal two cards to each player
        for _ in range(2):
            for player in self.players:
                card = self.deck.pop()
                player.hand.append(card)

    def create_deck(self):
        """Creates a standard 52-card deck."""
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        values = [
            '2', '3', '4', '5', '6', '7', '8', '9', '10',
            'Jack', 'Queen', 'King', 'Ace'
        ]
        deck = [{'value': value, 'suit': suit} for suit in suits for value in values]
        return deck

    def initialize_round(self):
        """Initializes variables for a new betting round."""
        self.pot = 0
        self.community_cards = []
        self.current_bet = 0
        self.game_phase = 'pre-flop'
        self.active_players = [player for player in self.players if player.chips > 0]
        self.dealer_position = (self.dealer_position + 1) % len(self.players)
        self.post_blinds()
        self.execute_betting_round()

    def post_blinds(self):
        """Posts small and big blinds."""
        small_blind_position = (self.dealer_position + 1) % len(self.players)
        big_blind_position = (self.dealer_position + 2) % len(self.players)

        small_blind_player = self.players[small_blind_position]
        big_blind_player = self.players[big_blind_position]

        small_blind_amount = min(self.small_blind, small_blind_player.chips)
        big_blind_amount = min(self.big_blind, big_blind_player.chips)

        small_blind_player.chips -= small_blind_amount
        small_blind_player.current_bet = small_blind_amount
        big_blind_player.chips -= big_blind_amount
        big_blind_player.current_bet = big_blind_amount

        self.pot += small_blind_amount + big_blind_amount
        self.current_bet = big_blind_amount

    def execute_betting_round(self):
        """Executes a betting round."""
        print(f"Starting betting round: {self.game_phase}")
        betting_complete = False
        players_in_round = [player for player in self.players if player.is_active]

        # Reset current bet for new betting round
        for player in players_in_round:
            player.current_bet = 0

        while not betting_complete:
            betting_complete = True  # Assume betting will complete this round
            for player in players_in_round:
                if player.is_active and not player.is_all_in:
                    action = self.get_player_action(player)
                    self.process_player_action(player, action)
                    # Check if further betting is needed
                    if not self.all_bets_equal(players_in_round):
                        betting_complete = False

        # Proceed to next phase
        if self.game_phase == 'pre-flop':
            self.game_phase = 'flop'
            self.deal_community_cards(3)
        elif self.game_phase == 'flop':
            self.game_phase = 'turn'
            self.deal_community_cards(1)
        elif self.game_phase == 'turn':
            self.game_phase = 'river'
            self.deal_community_cards(1)
        elif self.game_phase == 'river':
            self.game_phase = 'showdown'
            self.showdown()
            return  # End of game

        # Start next betting round
        self.execute_betting_round()

    def get_player_action(self, player):
        """Gets the action from the player."""
        if isinstance(player, PokerBot):
            action = player.decide_action(self)
            print(f"{player.name} decides to {action}.")
        else:
            # For the human player, you can implement input or UI interaction
            action = self.get_human_player_action(player)
        return action

    def get_human_player_action(self, player):
        """Placeholder for getting action from the human player."""
        # This function should be implemented to interact with the user interface
        # For example, through input prompts or UI buttons
        # Here we'll default to 'call' for simplicity
        return 'call'

    def process_player_action(self, player, action):
        """Processes the action taken by a player."""
        if action == 'fold':
            player.is_active = False
            print(f"{player.name} folds.")
        elif action == 'call':
            call_amount = self.current_bet - player.current_bet
            bet_amount = min(call_amount, player.chips)
            player.chips -= bet_amount
            player.current_bet += bet_amount
            self.pot += bet_amount
            print(f"{player.name} calls with {bet_amount} chips.")
            if player.chips == 0:
                player.is_all_in = True
                print(f"{player.name} is all-in!")
        elif action == 'check':
            print(f"{player.name} checks.")
        elif action == 'raise':
            min_raise = self.current_bet * 2
            raise_amount = max(min_raise, player.chips)
            total_bet = raise_amount
            bet_amount = total_bet - player.current_bet
            player.chips -= bet_amount
            player.current_bet += bet_amount
            self.current_bet = total_bet
            self.pot += bet_amount
            print(f"{player.name} raises to {total_bet} chips.")
            if player.chips == 0:
                player.is_all_in = True
                print(f"{player.name} is all-in!")

    def all_bets_equal(self, players):
        """Checks if all active players have equal bets."""
        active_bets = [player.current_bet for player in players if player.is_active and not player.is_all_in]
        return len(set(active_bets)) <= 1

    def deal_community_cards(self, number):
        """Deals community cards to the table."""
        for _ in range(number):
            card = self.deck.pop()
            self.community_cards.append(card)
        print(f"Community cards: {self.format_cards(self.community_cards)}")

    def format_cards(self, cards):
        """Formats the cards for display."""
        return ', '.join(f"{card['value']} of {card['suit']}" for card in cards)

    def showdown(self):
        """Handles the showdown and determines the winner."""
        print("Showdown:")
        active_players = [player for player in self.players if player.is_active]
        best_rank = -1
        best_high_cards = []
        winners = []

        for player in active_players:
            full_hand = player.hand + self.community_cards
            hand_rank, high_cards = evaluate_hand(full_hand)
            player.hand_rank = hand_rank
            player.high_cards = high_cards
            hand_name = self.get_hand_name(hand_rank)
            print(f"{player.name} has {hand_name} with high cards {high_cards}.")

            if hand_rank > best_rank:
                best_rank = hand_rank
                best_high_cards = high_cards
                winners = [player]
            elif hand_rank == best_rank:
                if high_cards > best_high_cards:
                    best_high_cards = high_cards
                    winners = [player]
                elif high_cards == best_high_cards:
                    winners.append(player)

        if len(winners) == 1:
            winner = winners[0]
            winner.chips += self.pot
            print(f"{winner.name} wins the pot of {self.pot} chips with a {self.get_hand_name(winner.hand_rank)}!")
        else:
            # Split the pot among tied players
            pot_share = self.pot // len(winners)
            for winner in winners:
                winner.chips += pot_share
            print("The pot is split among the winners!")
        self.pot = 0

        # Reset player statuses for the next game
        for player in self.players:
            player.current_bet = 0
            player.is_active = True
            player.is_all_in = False

    def get_hand_name(self, rank):
        for name, value in HAND_RANKS.items():
            if value == rank:
                return name
        return "Unknown Hand"

    # Additional methods for training the AI agent can be added here

    # If you are integrating with the PokerEnv for reinforcement learning
    def step(self, action):
        """
        Executes one time step within the environment.
        This method is used when training the AI agent.
        """
        # Process the action taken by the AI (assuming the AI is the current player)
        player = self.players[0]  # Assuming the AI is at index 0
        self.process_player_action(player, action)

        # Proceed to next player's turn or next phase
        # You need to implement logic to handle turns and phases
        # For simplicity, we'll assume a single-player action per step here

        # Compute the reward
        reward = 0  # Define your reward function based on the game outcome

        # Check if the game is over
        done = False  # Set to True if the game ends

        # Get the next state
        next_state = player.encode_game_state(self)

        return reward, next_state, done

    def reset(self):
        """
        Resets the game to an initial state.
        This method is used when starting a new episode during training.
        """
        self.start_game()
        player = self.players[0]  # Assuming the AI is at index 0
        state = player.encode_game_state(self)
        return state
