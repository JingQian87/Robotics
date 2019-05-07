"""
    Notice!!! Jing finished Q1 & Q2. In Q1, Jing only consider that the center 

    Take the simple_particle_pka.py from Professor Peter Allen's notes as reference.
    Note:
    1. Landmarks are squares centered in (x,y) with landmark_size.
    2. Angles are calculated in radius.
"""
from math import *
import random
import numpy as np

from visualize import *

landmark_size = 6 #If change this, should change that in visualize.py too.
filename = './world.txt'

def ccw(A,B,C):
    return (C[1]-A[1])*(B[0]-A[0]) > (B[1]-A[1])*(C[0]-A[0])

def intersect(A,B,C,D):
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

class Robot:

    def __init__(self, world_size):
        self.world_size = world_size
        self.x = random.random() * world_size[0]
        self.y = random.random() * world_size[1]
        self.theta = random.random() * 2.0 * pi

        self.forward_noise = 0.0
        self.turn_noise = 0.0
        self.range_noise = 0.0
        self.bearing_noise = 0.0

    def set_state(self, new_x, new_y, new_orientation):
        self.x = float(new_x)
        self.y = float(new_y)
        self.theta = float(new_orientation % (2.0*pi))

    def set_noise(self, new_f_noise, new_t_noise, new_r_noise, new_b_noise):
        self.forward_noise = float(new_f_noise)
        self.turn_noise = float(new_t_noise)
        self.range_noise = float(new_r_noise)#uncertainty in length
        self.bearing_noise = float(new_b_noise)#uncertainty in angle


    # Done: Moves a robot
    def move(self, angle_step = 0.1):
        """
        This function is to update the robot's state according to nonlinear transition function and return the action uk = [10cos(theta_k), 10sin(theta_k), delta_k]
        The order of move: move angle with angle_step first, then translation.
        Before retun, call sense to determine movable; if not, turn angle until safe to move forward, delta_k = total turning angle.
        """
        self.set_state(self.x, self.y, self.theta)
        forward = 10.0

        obstacles = self.sense()
        sensed_landmarks = obstacles[1:]

        niter = 0
        theta_update = self.theta + angle_step + random.gauss(0.0, self.turn_noise) #radius
        dist = 10.0 + random.gauss(0.0, self.forward_noise)
        flag = True
        while flag and niter < 10000:
            niter += 1
            x_update = self.x + cos(theta_update) * dist
            y_update = self.y + sin(theta_update) * dist
            # check wall
            if x_update > 0 and x_update < obstacles[0][0]:
                if y_update > 0 and y_update < obstacles[0][1]:
                    # check landmarks
                    for i in range(len(obstacles)-1):
                        imark = sensed_landmarks[i]
                        if imark[0] > dist or imark[0]*abs(theta_update - imark[1]) > 1.42 * landmark_size * 0.5: 
                            continue # no collision
                        else:
                            break # collision
                    else:
                        flag = False
            theta_update += angle_step
        return (x_update, y_update, theta_update)

    # Done: Returns a list of range bearing measurements
    def sense(self):
    """
    The Gaussian noise random variables are all zero-mean and have variance given by range noise for the range measurements and bearing noise for the bearing measurements, respectively (means univariate Gaussian).
    """
        world_size, landmarks = read_txt(filename)
        Z = [world_size]
        for i in range(len(landmarks)):
            dist = sqrt((self.x - landmarks[i][0]) ** 2 + (self.y - landmarks[i][1]) ** 2)
            dist += random.gauss(0.0, self.range_noise)
            angle = np.arctan2(self.y - landmarks[i][1], self.x - landmarks[i][0])
            angle += random.gauss(0.0, self.bearing_noise)
            Z.append((dist, angle))
        return Z

    # TODO: Move a particle according to the provided input vector
    def move_particle(self, dx, dy, dth):
        self.set_state(self.x, self.y, self.theta)