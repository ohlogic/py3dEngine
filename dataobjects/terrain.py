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
    all_coords = []
    
    
    def __init__(self, cols, rows):
        self.walk_on_create_floor(0,0)

        
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
        
        
    def create_floor_genList(self, icoords_x, icoords_z):
    
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
            
                if (y > 90 and y <= 100) and (x > 90 and x <= 100):
                    glColor3f(1.0, 0.0, 0.0) # red
                elif y <= 3 and x <= 3:
                    glColor3f(0.0, 0.0, 1.0) # blue
                elif (y > 3 and y < 90) or (x > 3 and x < 90):
                    glColor3f(0.0, 1.0, 1.0) # cyan 
                else:
                    glColor3f(0.0, 1.0, 0.0) # green
                    
                glVertex3f(x, y, self.all_floors[ icoords_x, icoords_z ].floor[x,y])
                glVertex3f(x, y+1, self.all_floors[ icoords_x, icoords_z ].floor[x,y+1])
            glEnd()
        self.all_floors[ icoords_x, icoords_z ].drawTerrain = DrawTerrain
        glEndList()
        

    def coords_to_indices(self, x, z):
        
        x_f = int(math.floor(x / 100.0))
        yz_f = int(math.floor(z / 100.0))
    
        return x_f, yz_f
    
    
    def walk_on_create_floor(self, x, z):
        
        icoords = self.coords_to_indices(x, z)

        create = False
        if self.all_floors[icoords[0],icoords[1]] == None:
            create = True

        if create:
            self.all_floors[icoords[0],icoords[1]] = Ground( 
                self.create_floor( 100*(icoords[0]+1), 100*(icoords[1]+1) ) )
                
            self.create_floor_genList( icoords[0] , icoords[1] )
            
            self.all_coords.append( (icoords[0] , icoords[1]) )
            
    def draw(self):
        
        for i in range (0, len(self.all_coords)):
            glPushMatrix()
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE) # add wiremesh

            glTranslatef(0,-5,0)
            glRotatef(-90, 1.0, .0, 0.0 )

            glCallList(self.all_floors[ self.all_coords[i][0], self.all_coords[i][1] ].drawTerrain)
            glPolygonMode( GL_FRONT_AND_BACK, GL_FILL ) # remove wiremesh
            glPopMatrix()    

