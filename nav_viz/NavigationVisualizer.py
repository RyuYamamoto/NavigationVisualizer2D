# -*- coding: utf-8 -*-
import qi
import sys
import matplotlib.pyplot as plt
import math
import matplotlib.patches as patches
import numpy as np
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient

class NavigationVisualizer:
    def __init__(self, robot_ip):
        self.robot_ip = robot_ip
        self.r = 0.2
        self.pos = np.array([0,0,0])

        fig = plt.figure(figsize=(8,8))
        self.ax = plt.axes()

        self.landmarks = self.load_map()

        self.session = qi.Session()
        self.session.connect("tcp://{}:9559".format(self.robot_ip))
        self.localize = self.session.service("Localize")

    def load_map(self):
        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(self.robot_ip, port=22, username="nao", password="nao")

        with SCPClient(client.get_transport()) as scp:
            scp.get("/home/nao/naoqi/nav/map.txt", "/tmp/")
        client.close()

        with open("/tmp/map.txt", "r") as f:
            landmark = f.readlines()

        return landmark

    def conifg_screen(self):
        self.ax.cla()
        self.ax.set_aspect('equal')
        self.ax.set_xlim(-1, 14)
        self.ax.set_ylim(-2, 2)
        self.ax.set_xlabel("X", fontsize=20)
        self.ax.set_ylabel("Y", fontsize=20)

    def set_robot_pos(self, pos):
        self.pos = pos

    def move_robot(self):
        x, y, theta = self.pos

        self.draw_coordinate(self.pos)

        xn = x + self.r * math.cos(theta)
        yn = y + self.r * math.sin(theta)
        self.ax.plot([x,xn], [y,yn], color="black")
        c = patches.Circle(xy=(x, y), radius=self.r, fill=False, color="black")
        self.ax.add_patch(c)

    def draw_all_landmark(self):
        for landmark in self.landmarks:
            info = landmark.split(",")
            x,y,theta = [float(info[1]), float(info[2]), float(info[3])]
            self.ax.scatter(x, y, s=300, marker="*", color="red")
            self.ax.annotate("{}: \n({}, {}, {})".format(int(info[0]), x, y, round(theta,3)), xy=(x+0.15, y+0.15))
            self.draw_coordinate(np.array([x,y,theta]))

    def draw_coordinate(self, pose):
        x, y, theta = pose
        ux = 0.3 * math.cos(theta)
        vx = 0.3 * math.sin(theta)
        self.ax.quiver(x, y, ux, vx, angles='xy', scale_units='xy', alpha=0.3, width=0.003, scale=1)
        self.ax.annotate("x", xy=(x+ux, y+vx))

        uy = - 0.3 * math.sin(theta)
        vy =   0.3 * math.cos(theta)
        self.ax.quiver(x, y, uy, vy, angles='xy', scale_units='xy', alpha=0.3, width=0.003, scale=1)
        self.ax.annotate("y", xy=(x+uy, y+vy))

    def run(self):
        while True:
            robot_pos = self.localize.position.value()
            self.set_robot_pos(np.array([robot_pos["position"][0], robot_pos["position"][1], robot_pos["position"][2]]))
            
            self.conifg_screen()
            self.draw_all_landmark()
            self.move_robot()
            plt.pause(0.01)

