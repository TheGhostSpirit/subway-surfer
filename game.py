from random import *
import arcade
import pickle
import os

SPRITE_SIZE = 200
COLUMNS = 3
HEIGHT = 4

VOID = '#'
PLAYER = '.'
COIN = 'o'
TREE =  'T'

NOTHING = 'N'
LEFT = 'L'
RIGHT = 'R'
ACTIONS = [NOTHING, LEFT, RIGHT]

REWARD_OUT = -100
REWARD_TREE = -50
REWARD_COIN = 50
REWARD_NOTHING = 10

class Environment:
    def __init__(self):

        self.__states = {}
        for row in range(HEIGHT):
            for col in range(COLUMNS):
                self.__states[(row, col)] = VOID
        self.__states[(0, 1)] = PLAYER
        self.__start = (0, 1)

    @property
    def start(self):
        return self.__start

    @property
    def states(self):
        return self.__states.keys()

    def getContent(self, state):
        return self.__states[state]

    def apply(self, agent, action):
        state = agent.state
        if action == NOTHING:
            new_state = (state[0], state[1])
        elif action == LEFT:
            new_state = (state[0], state[1] - 1)
        elif action == RIGHT:
            new_state = (state[0], state[1] + 1)

        if new_state in self.__states:
            if self.__states[new_state] == TREE:
                reward = REWARD_TREE
            elif self.__states[new_state] == COIN:
                reward = REWARD_COIN
            else:
                reward = REWARD_NOTHING
            state = new_state
        else:
            reward = REWARD_OUT

        agent.update(action, state, reward)
        return reward

class Agent:
    def __init__(self, environment):
        self.__environment = environment
        self.__qtable = {}
        self.__learning_rate = 1
        self.__discount_factor = 1
        for s in environment.states:
            self.__qtable[s] = {}
            for a in ACTIONS:
                self.__qtable[s][a] = random() * 10.0
        self.reset()

    def save(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.__qtable, file)

    def load(self, filename):
        with open(filename, 'rb') as file:
            self.__qtable = pickle.load(file)            

    def reset(self):
        self.__state = self.__environment.start
        self.__score = 0
        self.__last_action = None

    def update(self, action, state, reward):
        maxQ = max(self.__qtable[state].values())
        self.__qtable[self.__state][action] += self.__learning_rate * \
                                (reward + self.__discount_factor * \
                                 maxQ - self.__qtable[self.__state][action])

        self.__state = state
        self.__score += reward
        self.__last_action = action

    def best_action(self):
        rewards = self.__qtable[self.__state]
        best = None
        for a in rewards:
            if best is None or rewards[a] > rewards[best]:
                best = a
        return best

    def do(self, action):
        self.__environment.apply(self, action)

    @property
    def state(self):
        return self.__state

    @property
    def score(self):
        return self.__score

    @property
    def qtable(self):
        return self.__qtable

    @property
    def environment(self):
        return self.__environment

class Game(arcade.Window):
    def __init__(self, agent):
        super().__init__(COLUMNS * SPRITE_SIZE, HEIGHT * SPRITE_SIZE, 'Subway Surfer')
        self.__environment = agent.environment
        self.__agent = agent
        self.__iteration = 1

    def setup(self):

        self.background = arcade.load_texture("./images/grass.jpg")
        self.player = arcade.Sprite("./images/car.png", 1)
        # self.coins = arcade.SpriteList()
        self.trees = arcade.SpriteList()
        # for state in self.__environment.states:
        #     if self.__environment.getContent(state) == WALL:
        #         sprite = arcade.Sprite(":/tiles/stone.png", 0.5)
        #         sprite.center_x = (state[1] + 0.5) * SPRITE_SIZE
        #         sprite.center_y = self.height - (state[0] + 0.5) * SPRITE_SIZE
        #         self.walls.append(sprite)
        # self.goal = arcade.Sprite(":resources:images/items/flagRed1.png", 0.5)
        # self.goal.center_x = (self.__environment.goal[1] + 0.5) * SPRITE_SIZE
        # self.goal.center_y = self.height - (self.__environment.goal[0] + 0.5) * SPRITE_SIZE

        self.update_agent()

    def get_center(self, coordinates):
        return (
            (coordinates[1] + 0.5) * SPRITE_SIZE,
            self.height - (coordinates[0] + 0.5) * SPRITE_SIZE
        )

    def update_agent(self):
        coordinates = self.get_center(self.__agent.state)
        self.player.center_x = coordinates[0]
        self.player.center_y = coordinates[1]

    def on_draw(self):
        arcade.start_render()
        arcade.draw_texture_rectangle(self.width / 2, self.height / 2, self.width, self.height, self.background)
        # self.walls.draw()
        # self.goal.draw()
        self.player.draw()
        arcade.draw_text(f"#{self.__iteration} Score : {self.__agent.score}", 10, 10, arcade.csscolor.WHITE, 20)

    def on_update(self, delta_time):
        action = self.__agent.best_action()
        reward = self.__agent.do(action)
        self.update_agent()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.R:
            self.__agent.reset()
            self.__iteration += 1

if __name__ == "__main__":
    agent_filename = 'agent.dat'

    env = Environment()
    agent = Agent(env)
    if os.path.exists(agent_filename):
        agent.load(agent_filename)
    
    window = Game(agent)
    window.setup()
    arcade.run()

    agent.save(agent_filename)
