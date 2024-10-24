# dqn_agent.py

import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque

class DQNAgent:
    def __init__(self, state_size, action_size, device='cpu', learning_rate=0.001, gamma=0.99, epsilon_decay=0.995):
        self.state_size = state_size  # Size of the state vector
        self.action_size = action_size  # Number of possible actions
        self.device = torch.device(device)
        self.memory = deque(maxlen=20000)  # Experience replay buffer
        self.gamma = gamma  # Discount factor
        self.epsilon = 1.0  # Exploration rate (initially set to explore)
        self.epsilon_min = 0.01  # Minimum exploration rate
        self.epsilon_decay = epsilon_decay  # Decay rate for epsilon
        self.learning_rate = learning_rate  # Learning rate for the optimizer
        self.model = self._build_model().to(self.device)  # Neural network model
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.criterion = nn.MSELoss()  # Loss function

    def _build_model(self):
        """
        Builds the neural network model using PyTorch.
        The architecture consists of input, hidden, and output layers.
        """
        model = nn.Sequential(
            nn.Linear(self.state_size, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, self.action_size)
        )
        return model

    def remember(self, state, action, reward, next_state, done):
        """
        Stores the experience in the replay buffer.
        """
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        """
        Decides an action based on the current state.
        Uses epsilon-greedy policy for exploration and exploitation.
        """
        state = torch.tensor(state, dtype=torch.float).to(self.device)
        if np.random.rand() <= self.epsilon:
            # Explore: select a random action
            return random.randrange(self.action_size)
        self.model.eval()
        with torch.no_grad():
            # Exploit: select the action with max expected reward
            act_values = self.model(state)
        return torch.argmax(act_values).item()

    def replay(self, batch_size):
        """
        Trains the neural network using experiences sampled from the replay buffer.
        """
        if len(self.memory) < batch_size:
            return  # Not enough samples to train

        minibatch = random.sample(self.memory, batch_size)
        self.model.train()
        states = []
        targets = []
        for state, action, reward, next_state, done in minibatch:
            state_tensor = torch.tensor(state, dtype=torch.float).to(self.device)
            next_state_tensor = torch.tensor(next_state, dtype=torch.float).to(self.device)

            # Compute the target Q-value
            target = reward
            if not done:
                with torch.no_grad():
                    target = reward + self.gamma * torch.max(self.model(next_state_tensor)).item()

            # Get the current Q-values
            target_f = self.model(state_tensor)
            target_val = target_f.clone().detach()
            target_val[action] = target  # Update the Q-value for the action taken

            # Store for batch training
            states.append(state_tensor)
            targets.append(target_val)

        # Convert lists to tensors
        states_tensor = torch.stack(states)
        targets_tensor = torch.stack(targets)

        # Perform a single optimization step
        self.optimizer.zero_grad()
        outputs = self.model(states_tensor)
        loss = self.criterion(outputs, targets_tensor)
        loss.backward()
        self.optimizer.step()

        # Decay the exploration rate
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load(self, name):
        """
        Loads a saved model.
        """
        self.model.load_state_dict(torch.load(name))

    def save(self, name):
        """
        Saves the current model.
        """
        torch.save(self.model.state_dict(), name)
