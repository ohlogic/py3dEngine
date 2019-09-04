#!/usr/bin/python3

import pyglet
from pyglet.gl import *

import numpy as np
from noise import pnoise2

class Terrian_Floor():

    terrain  = {}
    columns = 0
    rows = 0
    
    def __init__(self, cols, rows):
        self.columns = cols
        self.rows = rows
        
        yoff = 0
        for y in range (0, rows):
            xoff = 0
            for x in range (0, cols):
                self.terrain[x,y] = np.interp(pnoise2(xoff, yoff), [0,1], [0, 1.5])
                xoff += 0.1
            yoff += 0.1
        
    def draw(self):
        for y in range (0, self.rows-1):
            glBegin(GL_TRIANGLE_STRIP)
            for x in range (0, self.columns):
                glColor3f(0.0, 1.0, 1.0)
                glVertex3f(x, y, self.terrain[x,y])
                glVertex3f(x, y+1, self.terrain[x,y+1])
            glEnd()