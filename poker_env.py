# poker_env.py

import gym
from gym import spaces
import numpy as np
from game_logic import GameLogic
from player import Player
from poker_bot import PokerBot

class PokerEnv(gym.Env):
    """
    OpenAI Gym environment for the poker game.
    """

    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(PokerEnv, self).__init__()
        # Define action and observation space
        # Actions: fold=0, call=1, raise=2
        self.action_space = spaces.Discrete(3)

        # Observation space: state vector as defined in PokerBot
        self.state_size = 112  # Adjust to match the state vector size in PokerBot
        self.observation_space = spaces.Box(
            low=0, high=1, shape=(self.state_size,), dtype=np.float32
        )

        # Initialize the game logic
        self.game_logic = GameLogic()
        # Add players: the AI agent and opponents
        self.agent_player = PokerBot(name="Agent", chips=1000)
        self.opponent = PokerBot(name="Opponent", chips=1000)
        self.game_logic.add_player(self.agent_player)
        self.game_logic.add_player(self.opponent)
        # Initialize game state
        self.current_player_index = 0  # Index of the current player

    def reset(self):
        """
        Resets the environment to an initial state and returns an initial observation.
        """
        self.game_logic.start_game()
        self.current_player_index = 0
        state = self.agent_player.encode_game_state(self.game_logic)
        return state

    def step(self, action):
        """
        Executes one time step within the environment.
        """
        # Map the action to the actual action string
        action_map = {0: 'fold', 1: 'call', 2: 'raise'}
        action_str = action_map.get(action, 'fold')

        # Save the current state
        state = self.agent_player.encode_game_state(self.game_logic)

        # Process the agent's action
        self.game_logic.process_player_action(self.agent_player, action_str)

        # Process the opponent's action (random for simplicity)
        if self.opponent.is_active and not self.opponent.is_all_in:
            opponent_action = self.opponent.make_decision(self.game_logic)
            self.game_logic.process_player_action(self.opponent, opponent_action)

        # Advance the game phase if needed
        if self.game_logic.all_bets_equal(self.game_logic.players):
            if self.game_logic.game_phase == 'pre-flop':
                self.game_logic.game_phase = 'flop'
                self.game_logic.deal_community_cards(3)
            elif self.game_logic.game_phase == 'flop':
                self.game_logic.game_phase = 'turn'
                self.game_logic.deal_community_cards(1)
            elif self.game_logic.game_phase == 'turn':
                self.game_logic.game_phase = 'river'
                self.game_logic.deal_community_cards(1)
            elif self.game_logic.game_phase == 'river':
                self.game_logic.game_phase = 'showdown'
                self.game_logic.showdown()
                done = True
                reward = self.calculate_reward()
                next_state = self.agent_player.encode_game_state(self.game_logic)
                return next_state, reward, done, {}
            else:
                pass  # Game continues

        # Get the next state
        next_state = self.agent_player.encode_game_state(self.game_logic)

        # Check if the game is over
        done = not self.agent_player.is_active or not self.opponent.is_active

        # Calculate the reward
        reward = self.calculate_reward()

        return next_state, reward, done, {}

    def calculate_reward(self):
        """
        Calculates the reward for the agent based on the game outcome.
        """
        # Reward structure:
        # Win: +1
        # Lose: -1
        # Tie: 0
        # Early fold: -0.5
        if self.game_logic.game_phase == 'showdown':
            if self.agent_player.chips > self.opponent.chips:
                return 1  # Agent wins
            elif self.agent_player.chips < self.opponent.chips:
                return -1  # Agent loses
            else:
                return 0  # Tie
        elif not self.agent_player.is_active:
            return -0.5  # Agent folded
        else:
            return 0  # Game continues

    def render(self, mode='human'):
        """
        Renders the current state of the environment.
        """
        if mode == 'human':
            print(f"Pot: {self.game_logic.pot}")
            print(f"Community Cards: {self.game_logic.format_cards(self.game_logic.community_cards)}")
            for player in self.game_logic.players:
                hand = self.game_logic.format_cards(player.hand)
                print(f"{player.name} - Chips: {player.chips} - Hand: {hand}")

    def close(self):
        """
        Performs any necessary cleanup.
        """
        pass
