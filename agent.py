from sklearn.neural_network import MLPRegressor
import pickle
from random import *

from const import *

class Agent:
    def __init__(self, environment):
        self.__environment = environment

        self.__learning_rate = 1
        self.__discount_factor = 1
        self.__history = []
        self.__exploration = 1.0

        self.__mlp = MLPRegressor(hidden_layer_sizes=(10,),
                                  activation='logistic',
                                  solver='sgd',
                                  max_iter=1,
                                  warm_start=True,
                                  learning_rate_init=self.__learning_rate)
        self.__mlp.fit([[0, 0]], [[0] * len(ACTIONS)])
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
            best = choice(ACTIONS)
            self.__exploration *= 0.99
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