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

        self.max_action = 10.0
        self.action_space = spaces.Box(-self.max_action, self.max_action, (1,))

        self.observation_space = spaces.Box(-high, high, shape=(4,), dtype=np.float32)
        
        self.steps_left = self.MAX_EPISODE
        self.state = [0, 0, math.pi/3, 0]
        self.g = 9.8
        self.length = 0.2
        self.delta_t = 0.02
        self.friction = 0.5
        self.small_theta = 0.075
        self.collision_now = 0
        self.collision_before = 0

    def step(self, action):
        action = np.float32(np.clip(action, -self.max_action, self.max_action))
        self.act = action
        collision_flag = 0
        self.act = action
        z, z_dot, theta, theta_dot = self.state

        theta_ddot = -(self.g+action[0])*math.sin(theta)/self.length - self.friction*theta_dot
        theta_dot = theta_dot + theta_ddot*self.delta_t
        theta = theta + theta_dot*self.delta_t
        z_dot = z_dot + action[0]*self.delta_t
        z = z + z_dot*self.delta_t

        if(theta<self.small_theta or theta>(math.pi-self.small_theta)):
            theta_dot = theta_dot*(-1)
            collision_flag = 1
            self.collision_before = self.collision_now
            if(theta<self.small_theta):
                theta = self.small_theta
                self.collision_now = 0
            else:
                theta = math.pi-self.small_theta
                self.collision_now = 1

        self.state = [z, z_dot, theta, theta_dot]

        
        done = bool(
            self.steps_left<0
        )    
        
        reward = 0
        if not done:
            if(collision_flag and self.collision_now!=self.collision_before):
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
        x = [pose_point[0], pose_ball_left[0]]
        y = [pose_point[1], pose_ball_left[1]]
        plt.plot(x,y,color='black')
        x = [pose_point[0], pose_ball_right[0]]
        y = [pose_point[1], pose_ball_right[1]]
        plt.plot(x,y,color='black')
        plt.scatter(pose_ball_left[0], pose_ball_left[1], color='blue', s=100)
        plt.scatter(pose_ball_right[0], pose_ball_right[1], color='blue', s=100)
        
    
    def render(self, mode='human'):
        plt.axis('equal')
        # plt.xlim([-self.length, self.length])
        # plt.ylim([-5*self.length, 5*self.length])
        pose_point = [0, self.state[0]]
        pose_ball_left = [-self.length*math.sin(self.state[2]), self.state[0]-self.length*math.cos(self.state[2])]
        pose_ball_right = [self.length*math.sin(self.state[2]), self.state[0]-self.length*math.cos(self.state[2])]
        self.draw_line(pose_point, pose_ball_left, pose_ball_right)
        plt.draw()
        plt.pause(0.001)
        plt.clf()
        print(f'State {self.state}, action: {self.act}, done: {self.cur_done}, reward: {self.cur_reward}')