import gym
from gym import spaces
import numpy as np
import math
import matplotlib.pyplot as plt
import random

class LattoLatto(gym.Env):
    def __init__(self):
        super(LattoLatto, self).__init__()
        self.MAX_EPISODE = 500
        self.z_threshold = self.z_dot_threshold = 1
        self.theta_threshold = self.theta_dot_threshold = math.pi
        high = np.array([self.z_threshold, self.z_dot_threshold, self.theta_threshold, self.theta_dot_threshold],
                        dtype=np.float32)

        self.max_action = 1.0
        self.action_space = spaces.Box(-self.max_action, self.max_action, (1,))

        self.observation_space = spaces.Box(-high, high, shape=(4,), dtype=np.float32)
        
        self.steps_left = self.MAX_EPISODE
        self.state = [0, 0, math.pi/3, 0]
        self.g = 9.8
        self.length = 0.2
        self.delta_t = 0.02
        self.friction = 1.0
        self.small_theta = 0.075

    def step(self, action):
        # action = 0
        action = np.float32(np.clip(action, -self.max_action, self.max_action))
        self.act = action
        collision_flag = 0
        self.act = action
        z, z_dot, theta, theta_dot = self.state

        theta_ddot = -(self.g+action)*math.sin(theta)/self.length - self.friction*theta_dot
        theta_dot = theta_dot + theta_ddot*self.delta_t
        theta = theta + theta_dot*self.delta_t
        z_dot = z_dot + action*self.delta_t
        z = z + z_dot*self.delta_t

        if(theta<self.small_theta or theta>(math.pi-self.small_theta)):
            theta_dot = theta_dot*(-1)
            collision_flag = 1

        self.state = [z, z_dot, theta, theta_dot]

        
        done = bool(
            self.steps_left<0
        )    
        
        if not done:
            if(collision_flag):
                reward = 1
            else:
                reward = 0
        else:
            reward = 0
        if not done:
            self.steps_left = self.steps_left-1
        self.cur_reward = reward
        self.cur_done = done
        return np.array([self.state]), reward, done, {}

    def reset(self):
        self.state = [0, 0, math.pi/3, 0]
        self.steps_left = self.MAX_EPISODE
        return np.array([self.state])

    def draw_line(self, pose_point, pose_ball_left, pose_ball_right):
        point_num = 10
        delta_x_left = (pose_ball_left[0]-pose_point[0])/point_num
        delta_y_left = (pose_ball_left[1]-pose_point[1])/point_num
        delta_x_right = (pose_ball_right[0]-pose_point[0])/point_num
        delta_y_right = (pose_ball_right[1]-pose_point[1])/point_num
        for i in range(0, point_num+1):
            plt.scatter(pose_point[0]+delta_x_left*i, pose_point[1]+delta_y_left*i, color='blue')
            plt.scatter(pose_point[0]+delta_x_right*i, pose_point[1]+delta_y_right*i, color='green')
        
    
    def render(self, mode='human'):
        # plt.axis('equal')
        plt.xlim([-self.length, self.length])
        plt.ylim([-2*self.length, 2*self.length])
        pose_point = [0, self.state[0]]
        pose_ball_left = [-self.length*math.sin(self.state[2]), self.state[0]-self.length*math.cos(self.state[2])]
        pose_ball_right = [self.length*math.sin(self.state[2]), self.state[0]-self.length*math.cos(self.state[2])]
        self.draw_line(pose_point, pose_ball_left, pose_ball_right)
        plt.draw()
        plt.pause(0.001)
        plt.clf()
        print(pose_point)
        print(pose_ball_left)
        print(pose_ball_right)
        print(f'State {self.state}, action: {self.act}, done: {self.cur_done}, reward: {self.cur_reward}')