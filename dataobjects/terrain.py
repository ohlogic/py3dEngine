#!/usr/bin/python3

import pyglet
from pyglet.gl import *

import numpy as np
from noise import pnoise2

class Terrain_Floor():
    
    drawTerrain = None
    floor  = {}
    columns = 0
    rows = 0
    
    def __init__(self, cols, rows):
        self.columns = cols
        self.rows = rows
        
        yoff = 0
        for y in range (0, rows):
            xoff = 0
            for x in range (0, cols):
                self.floor[x,y] = np.interp(pnoise2(xoff, yoff), [0,1], [0, 4.5])
                xoff += 0.1
            yoff += 0.1
        
    def load(self):
        DrawTerrain=glGenLists(1)
        glNewList(DrawTerrain,GL_COMPILE)
        
        for y in range (0, self.rows-1):
            glBegin(GL_TRIANGLE_STRIP)
            for x in range (0, self.columns):
                
                # testing, color coded beginning, end of map
                if y > 90 and x > 90:
                    glColor3f(1.0, 0.0, 0.0) #red
                elif y <= 3 and x <= 3:
                    glColor3f(0.0, 1.0, 0.0) #green
                else:
                    glColor3f(0.0, 1.0, 1.0) #cyan default color
                    
                glVertex3f(x, y, self.floor[x,y])
                glVertex3f(x, y+1, self.floor[x,y+1])
            glEnd()
        self.drawTerrain = DrawTerrain
        glEndList()