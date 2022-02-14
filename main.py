import os
import arcade

from environment import Environment
from const import *
from agent import Agent
from game import Game

if __name__ == "__main__":
    agent_filename = 'agent.dat'

    env = Environment(MAP)
    agent = Agent(env)
    if os.path.exists(agent_filename):
        agent.load(agent_filename)
    
    window = Game(agent)
    window.setup()
    arcade.run()

    agent.save(agent_filename)