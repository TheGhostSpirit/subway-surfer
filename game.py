from random import *
import arcade
import pickle
import os
from sklearn.neural_network import MLPRegressor

SPRITE_SIZE = 80

MAP = """
    ##.##
    MMoMM
    M#o#M
    #MMo#
    ##MM#
    #MMo#
    M#M#M
    #Mo#M
    #MM##
    ####o
"""

VOID = '#'
START = '.'
GEM = 'o'
METEOR =  'M'

NOTHING = 'N'
LEFT = 'L'
RIGHT = 'R'
ACTIONS = [NOTHING, LEFT, RIGHT]

REWARD_OUT = -100
REWARD_METEOR = -50
REWARD_GEM = 20
REWARD_NOTHING = 0

class Environment:
    def __init__(self, text):

        self.__states = {}
        lines = list(map(lambda x: x.strip(), text.strip().split('\n')))
        for row in range(len(lines)):
            for col in range(len(lines[row])):
                self.__states[(row, col)] = lines[row][col]
                if(lines[row][col] == START):
                    self.__start = (row, col)
        self.width = len(lines[0])
        self.height = len(lines)

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
            new_state = (state[0] + 1, state[1])
        elif action == LEFT:
            new_state = (state[0] + 1, state[1] - 1)
        elif action == RIGHT:
            new_state = (state[0] + 1, state[1] + 1)

        if new_state in self.__states:
            if self.__states[new_state] == METEOR:
                reward = REWARD_METEOR
            elif self.__states[new_state] == GEM:
                reward = REWARD_GEM
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
        #self.__qtable = {}

        self.__learning_rate = 1
        self.__discount_factor = 1
        #for s in environment.states:
        #    self.__qtable[s] = {}
        #    for a in ACTIONS:
        #        self.__qtable[s][a] = random() * 10.0
        self.__history = []
        self.__exploration = 1.0

        self.__mlp = MLPRegressor(hidden_layer_sizes=(10,),
                                  activation='logistic',
                                  solver='sgd',
                                  max_iter=1,
                                  warm_start=True,
                                  learning_rate_init=self.__learning_rate)
        self.__mlp.fit([[0, 0]], [[0] * len(ACTIONS)])  # initialisation du RN
        self.reset()

    def save(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.__mlp, file)

    def load(self, filename):
        with open(filename, 'rb') as file:
            self.__mlp = pickle.load(file)

    def reset(self):
        self.__state = self.__environment.start
        self.__score = 0
        self.__last_action = None

    def update_history(self):
        self.__history.append(self.__score)

    @property
    def history(self):
        return self.__history

    def update(self, action, state, reward):
        maxQ = max(self.__mlp.predict([self.state_to_vector(state)])[0])
        desired = reward + self.__discount_factor * maxQ

        qvector = self.__mlp.predict([self.state_to_vector(self.__state)])[0]
        i_action = ACTIONS.index(action)
        qvector[i_action] = desired

        self.__mlp.fit([self.state_to_vector(self.__state)], [qvector])

        self.__state = state
        self.__score += reward
        self.__last_action = action

    def state_to_vector(self, state):
        return [state[0] / self.__environment.width, \
                state[1] / self.__environment.height]

    def best_action(self):
        if random() < self.__exploration:
            best = choice(ACTIONS)  # une action au hasard
            self.__exploration *= 0.99
            # print(self.__exploration)
        else:
            qvector = self.__mlp.predict([self.state_to_vector(self.__state)])[0]
            i_best = 0
            for i in range(len(qvector)):
                if qvector[i] > qvector[i_best]:
                    i_best = i
            best = ACTIONS[i_best]

        return best

    @property
    def exploration(self):
        return self.__exploration

    def do(self, action):
        self.__environment.apply(self, action)

    @property
    def state(self):
        return self.__state

    @property
    def score(self):
        return self.__score

    @property
    def mlp(self):
        return self.__mlp

    @property
    def environment(self):
        return self.__environment

class Game(arcade.Window):
    def __init__(self, agent):
        super().__init__(
            agent.environment.width * SPRITE_SIZE,
            agent.environment.height * SPRITE_SIZE,
            'Subway Surfer'
        )
        self.__environment = agent.environment
        self.__agent = agent
        self.__iteration = 1

    def setup(self):

        self.player = arcade.Sprite(":resources:images/animated_characters/robot/robot_idle.png", 1)

        self.meteors = arcade.SpriteList()
        for state in self.__environment.states:
            if self.__environment.getContent(state) == METEOR:
                sprite = arcade.Sprite(":resources:images/space_shooter/meteorGrey_big4.png", 0.5)
                sprite.center_x = (state[1] + 0.5) * SPRITE_SIZE
                sprite.center_y = self.height - (state[0] + 0.5) * SPRITE_SIZE
                self.meteors.append(sprite)

        self.gems = arcade.SpriteList()
        for state in self.__environment.states:
            if self.__environment.getContent(state) == GEM:
                sprite = arcade.Sprite(":resources:images/items/gemYellow.png", 0.5)
                sprite.center_x = (state[1] + 0.5) * SPRITE_SIZE
                sprite.center_y = self.height - (state[0] + 0.5) * SPRITE_SIZE
                self.gems.append(sprite)
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
        self.meteors.draw()
        self.gems.draw()
        self.player.draw()
        arcade.draw_text(f"#{self.__iteration} Score : {self.__agent.score}", 10, 10, arcade.csscolor.WHITE, 20)

    def on_update(self, delta_time):
        if self.__agent.state[0] < self.__agent.environment.height - 1:
            action = self.__agent.best_action()
            reward = self.__agent.do(action)
            self.update_agent()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.R:
            self.__agent.reset()
            self.__iteration += 1

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
