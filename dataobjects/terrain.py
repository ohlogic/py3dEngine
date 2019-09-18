#!/usr/bin/python3

import pyglet
from pyglet.gl import *

import numpy as np
from noise import pnoise2
import math 
import numpy as np

class Ground():

    floor = None
    drawTerrain = None
    
    def __init__(self, floor):
        self.floor = floor


class Terrain_Floor():
    
    columns = 0
    rows = 0
    
    all_floors = np.empty((100, 100), dtype=object)
    
    def __init__(self, cols, rows):
        
        floor = self.create_floor(cols, rows)
        self.all_floors[0,0] = Ground(floor)
        
        
    def create_floor(self, cols, rows):
        self.columns = cols
        self.rows = rows
        
        floor_area = {}
        yoff = 0
        for y in range (0, rows):
            xoff = 0
            for x in range (0, cols):
                floor_area[x,y] = np.interp(pnoise2(xoff, yoff), [0,1], [0, 4.5])
                xoff += 0.1
            yoff += 0.1
            
        return floor_area

    # just for origin floor
    def init_load(self):
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
                    
                glVertex3f(x, y, self.all_floors[0,0].floor[x,y])
                glVertex3f(x, y+1, self.all_floors[0,0].floor[x,y+1])
            glEnd()
            
        self.all_floors[0,0].drawTerrain = DrawTerrain
        glEndList()
        
        
    def create_floor_genList(self):
    
        DrawTerrain=glGenLists(1)
        glNewList(DrawTerrain,GL_COMPILE)
        
        
        offone_y = 0
        if self.columns > 100:
            offone_y = 1
        
        offone_x = 0
        if self.rows > 100:
            offone_x = 1
        
        
        for y in range (self.rows-100-offone_x, self.rows-1):
            glBegin(GL_TRIANGLE_STRIP)
            for x in range (self.columns-100-offone_y, self.columns):
                glColor3f(0.0, 1.0, 0.0)
                glVertex3f(x, y, self.all_floors[self.icoords[0],self.icoords[1]].floor[x,y])
                glVertex3f(x, y+1, self.all_floors[self.icoords[0],self.icoords[1]].floor[x,y+1])
            glEnd()
        #self.drawTerrain = DrawTerrain
        self.all_floors[self.icoords[0],self.icoords[1]].drawTerrain = DrawTerrain
        glEndList()
        

    def coords_to_indices(self, x, z):
        
        x_f = int(math.floor(x / 100.0))
        yz_f = int(math.floor(z / 100.0))
    
        return x_f, yz_f
    
    
    def walk_on_create_floor(self, x, z):
        
        self.icoords = self.coords_to_indices(x, z)
        
        create = False
        if self.all_floors[self.icoords[0],self.icoords[1]] == None:
            create = True

        if create:
            self.all_floors[self.icoords[0],self.icoords[1]] = Ground( self.create_floor( 
                100*(self.icoords[0]+1),
                100*(self.icoords[1]+1) ) )
                
            self.create_floor_genList()
            
        
    def draw(self):
    
        icoords = self.icoords
        startx = 0
        starty = 0
        max_floor_display  = 4
        
        # a test of not loading floors that are not in range
        if icoords[0] > max_floor_display or icoords[1] > max_floor_display:
            
            if icoords[0] > max_floor_display//2:
                startx = icoords[0] - 2
            
            if icoords[1] > max_floor_display//2:
                starty = icoords[1] - 2
        #########################################
        
        for i in range(startx, 100): # otherwise 0, 100
            if self.all_floors[i,0] == None:
                break
            for j in range(starty, 100): # otherwise 0, 100
                if self.all_floors[i,j] == None:
                    continue
                else:
                    glPushMatrix()
                    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE) # add wiremesh

                    glTranslatef(0,-5,0)
                    glRotatef(-90, 1.0, .0, 0.0 )

                    glCallList(self.all_floors[i,j].drawTerrain)
                    glPolygonMode( GL_FRONT_AND_BACK, GL_FILL ) # remove wiremesh
                    glPopMatrix()    

