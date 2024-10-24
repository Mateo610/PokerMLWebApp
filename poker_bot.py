# poker_bot.py

import random
from player import Player
from dqn_agent import DQNAgent
import numpy as np

class PokerBot(Player):
    def __init__(self, name, chips=1000, state_size=200, action_size=3, device='cpu'):
        super().__init__(name, chips)
        self.state_size = state_size  # Size of the encoded game state vector
        self.action_size = action_size  # Number of possible actions
        self.device = device
        # Initialize the DQN agent
        self.agent = DQNAgent(
            state_size=self.state_size,
            action_size=self.action_size,
            device=self.device
        )
        # Mapping of actions
        self.action_map = {
            0: 'fold',
            1: 'call',
            2: 'raise'
        }

    def make_decision(self, game_logic):
        """
        Makes a decision based on the current game state using the DQN agent.
        """
        # Encode the current game state
        state = self.encode_game_state(game_logic)
        # Decide on an action
        action_index = self.agent.act(state)
        action = self.action_map.get(action_index, 'fold')
        return action

    def encode_game_state(self, game_logic):
        """
        Encodes the current game state into a numerical vector suitable for the DQN agent.
        """
        # Encode own cards
        own_cards = self.encode_cards(self.hand)  # 52-dimensional binary vector
        # Encode community cards
        community_cards = self.encode_cards(game_logic.community_cards)  # 52-dimensional binary vector
        # Normalize numerical features
        pot_size = game_logic.pot / 10000  # Normalize pot size
        current_bet = self.current_bet / 10000  # Normalize current bet
        chips = self.chips / 10000  # Normalize player's chips
        # Encode game phase
        phase = self.encode_phase(game_logic.game_phase)  # 5-dimensional one-hot vector
        # Combine all features into a single state vector
        state_vector = np.concatenate([
            own_cards,
            community_cards,
            [pot_size, current_bet, chips],
            phase
        ])
        # Ensure the state vector has the correct size
        state_vector = np.resize(state_vector, self.state_size)
        # Convert to NumPy array of type float32
        return state_vector.astype(np.float32)

    def encode_cards(self, cards):
        """
        Encodes a list of cards into a 52-dimensional binary vector.
        """
        card_vector = np.zeros(52)
        for card in cards:
            index = self.get_card_index(card)
            card_vector[index] = 1
        return card_vector

    def get_card_index(self, card):
        """
        Returns a unique index for a given card.
        """
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        values = [
            '2', '3', '4', '5', '6', '7', '8', '9', '10',
            'Jack', 'Queen', 'King', 'Ace'
        ]
        suit_index = suits.index(card['suit'])
        value_index = values.index(card['value'])
        card_index = suit_index * 13 + value_index
        return card_index

    def encode_phase(self, phase):
        """
        One-hot encodes the game phase.
        """
        phases = ['pre-flop', 'flop', 'turn', 'river', 'showdown']
        phase_vector = np.zeros(len(phases))
        if phase in phases:
            index = phases.index(phase)
            phase_vector[index] = 1
        return phase_vector

    def update_agent(self, state, action, reward, next_state, done):
        """
        Updates the DQN agent with the latest experience.
        """
        # Convert action to action index
        action_index = {v: k for k, v in self.action_map.items()}[action]
        # Remember the experience
        self.agent.remember(state, action_index, reward, next_state, done)
        # Replay experiences to train the agent
        self.agent.replay(batch_size=32)

    def save_agent(self, filename):
        """
        Saves the agent's model to a file.
        """
        self.agent.save(filename)

    def load_agent(self, filename):
        """
        Loads the agent's model from a file.
        """
        self.agent.load(filename)
