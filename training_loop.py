# training_loop.py

import gym
import numpy as np
import torch
from poker_env import PokerEnv
from dqn_agent import DQNAgent
from collections import deque
import os

def train_agent(
    env,
    agent,
    num_episodes=1000,
    max_steps_per_episode=100,
    batch_size=32,
    save_interval=100,
    model_save_path='models/poker_dqn_agent.pth'
):
    """
    Trains the DQN agent in the PokerEnv environment.
    """
    # Create a directory for saving models if it doesn't exist
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)

    # Initialize performance tracking
    rewards_all_episodes = []
    epsilon_history = []
    max_reward = float('-inf')

    # Loop over episodes
    for episode in range(1, num_episodes + 1):
        state = env.reset()
        done = False
        total_reward = 0

        # Loop over steps within an episode
        for step in range(max_steps_per_episode):
            # Agent selects an action
            action = agent.act(state)

            # Environment processes the action
            next_state, reward, done, info = env.step(action)

            # Agent stores the experience
            agent.remember(state, action, reward, next_state, done)

            # Agent learns from experience
            agent.replay(batch_size)

            # Update state
            state = next_state

            # Accumulate reward
            total_reward += reward

            # Check if the episode is finished
            if done:
                break

        # Record total reward for this episode
        rewards_all_episodes.append(total_reward)
        epsilon_history.append(agent.epsilon)

        # Print progress every 10 episodes
        if episode % 10 == 0:
            avg_reward = np.mean(rewards_all_episodes[-10:])
            print(f"Episode {episode}/{num_episodes} - Average Reward: {avg_reward:.2f} - Epsilon: {agent.epsilon:.4f}")

        # Save the model at regular intervals
        if episode % save_interval == 0:
            agent.save(model_save_path)
            print(f"Model saved at episode {episode}")

        # Update max_reward and save the best model
        if total_reward > max_reward:
            max_reward = total_reward
            agent.save(model_save_path)
            print(f"New best model saved with reward {max_reward:.2f} at episode {episode}")

    # After training is complete, save the final model
    agent.save(model_save_path)
    print("Training complete. Final model saved.")

    # Return the performance history
    return rewards_all_episodes, epsilon_history

if __name__ == '__main__':
    # Initialize the environment
    env = PokerEnv()

    # Get state and action sizes
    state_size = env.observation_space.shape[0]
    action_size = env.action_space.n

    # Initialize the agent
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    agent = DQNAgent(state_size=state_size, action_size=action_size, device=device)

    # Train the agent
    rewards, epsilons = train_agent(
        env=env,
        agent=agent,
        num_episodes=1000,
        max_steps_per_episode=100,
        batch_size=32,
        save_interval=100,
        model_save_path='models/poker_dqn_agent.pth'
    )

    # Plotting the results (optional)
    try:
        import matplotlib.pyplot as plt
        plt.plot(rewards)
        plt.xlabel('Episode')
        plt.ylabel('Total Reward')
        plt.title('Training Progress')
        plt.show()
    except ImportError:
        print("matplotlib not installed. Skipping plotting.")
