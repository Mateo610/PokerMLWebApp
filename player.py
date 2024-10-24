# player.py

class Player:
    def __init__(self, name, chips=1000):
        self.name = name
        self.chips = chips
        self.hand = []  # The player's hole cards
        self.is_active = True  # Indicates if the player is still in the current hand
        self.is_all_in = False  # Indicates if the player has gone all-in
        self.current_bet = 0  # The amount the player has bet in the current betting round
        self.hand_rank = None  # The rank of the player's hand (used at showdown)
        self.high_cards = []  # The high cards used for tie-breakers

    def reset_for_new_hand(self):
        """Resets the player's status for a new hand."""
        self.hand = []
        self.is_active = True
        self.is_all_in = False
        self.current_bet = 0
        self.hand_rank = None
        self.high_cards = []

    def make_decision(self, game_state):
        """
        Placeholder method for making a decision.
        Should be overridden by subclasses or implemented to interact with the UI.
        """
        # This method should return one of: 'fold', 'call', 'check', 'raise'
        # For human players, this would involve user input
        # For AI players, this would involve decision logic or policy
        return 'call'  # Default action

    def encode_game_state(self, game_logic):
        """
        Encodes the current game state into a format suitable for AI agents.
        """
        # Implement encoding logic here
        # This could include the player's own cards, community cards, bets, etc.
        # Returns a state representation (e.g., a vector or array)
        pass

    def __repr__(self):
        return f"Player(name={self.name}, chips={self.chips})"
