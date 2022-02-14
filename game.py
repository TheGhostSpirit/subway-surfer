import arcade
from sklearn.neural_network import MLPRegressor
import os
import arcade

from const import *


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
