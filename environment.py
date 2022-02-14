from const import *

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
