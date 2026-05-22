import gym
from gym import spaces
import numpy as np
import math
import matplotlib.pyplot as plt

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
        self.z_position_penalty_weight = 0.1
        self.collision_now = 0
        self.collision_before = 0
        self.fig = None
        self.ax = None

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
        
        sparse_reward = 0.0
        if not done:
            if collision_flag and self.collision_now != self.collision_before:
                sparse_reward = 1.0

        z_position_penalty = self.z_position_penalty_weight * (z ** 2)
        reward = sparse_reward - z_position_penalty

        if not done:
            self.steps_left = self.steps_left-1
        
        self.cur_sparse_reward = sparse_reward
        self.cur_z_position_penalty = z_position_penalty
        self.cur_reward = reward
        self.cur_done = done
        info = {
            "sparse_reward": sparse_reward,
            "z_position_penalty": z_position_penalty,
        }
        return np.array([self.state]), reward, done, info

    def reset(self):
        self.state = [0, 0, math.pi/3, 0]
        self.steps_left = self.MAX_EPISODE
        return np.array([self.state])

    def draw_line(self, pose_point, pose_ball_left, pose_ball_right):
        x = [pose_point[0], pose_ball_left[0]]
        y = [pose_point[1], pose_ball_left[1]]
        self.ax.plot(x, y, color='black')
        x = [pose_point[0], pose_ball_right[0]]
        y = [pose_point[1], pose_ball_right[1]]
        self.ax.plot(x, y, color='black')
        self.ax.scatter(pose_ball_left[0], pose_ball_left[1], color='blue', s=100)
        self.ax.scatter(pose_ball_right[0], pose_ball_right[1], color='blue', s=100)
        
    
    def render(self, mode='human'):
        if self.fig is None or self.ax is None or not plt.fignum_exists(self.fig.number):
            plt.ion()
            self.fig, self.ax = plt.subplots()
            plt.show(block=False)

        self.ax.clear()
        self.ax.set_aspect('equal', adjustable='box')
        self.ax.set_xlim([-1.5 * self.length, 1.5 * self.length])
        self.ax.set_ylim([-self.z_threshold - 2 * self.length, self.z_threshold + 2 * self.length])
        self.ax.set_title('Latto-Latto Animation')
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('z')

        pose_point = [0, self.state[0]]
        pose_ball_left = [-self.length*math.sin(self.state[2]), self.state[0]-self.length*math.cos(self.state[2])]
        pose_ball_right = [self.length*math.sin(self.state[2]), self.state[0]-self.length*math.cos(self.state[2])]
        self.draw_line(pose_point, pose_ball_left, pose_ball_right)
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
        plt.pause(0.02)
        print(
            "State {}, action: {}, done: {}, reward: {}, sparse_reward: {}, "
            "z_position_penalty: {}".format(
                self.state,
                self.act,
                self.cur_done,
                self.cur_reward,
                self.cur_sparse_reward,
                self.cur_z_position_penalty,
            )
        )

    def close(self):
        if self.fig is not None:
            plt.close(self.fig)
            self.fig = None
            self.ax = None
