#!/usr/bin/python3

import pyglet
from pyglet.gl import *

class Texuture_Cube():
    def __init__(self):
            pass
            
    def draw():
        glBegin(GL_POLYGON) #// three
        glTexCoord2f(0,.5); glVertex3f(-1.0, 1.0, 1.0)
        glTexCoord2f(.5,.5); glVertex3f(-1.0,-1.0, 1.0)
        glTexCoord2f(.5,0); glVertex3f( 1.0,-1.0, 1.0)
        glTexCoord2f(0,0); glVertex3f( 1.0, 1.0, 1.0)
        glEnd()

        glBegin(GL_POLYGON) #// five
        glTexCoord2f(0,.5); glVertex3f(-1.0, 1.0,-1.0)
        glTexCoord2f(.5,.5); glVertex3f(-1.0,-1.0,-1.0)
        glTexCoord2f(.5,0); glVertex3f(-1.0,-1.0, 1.0)
        glTexCoord2f(0,0); glVertex3f(-1.0, 1.0, 1.0)
        glEnd()

        glBegin(GL_POLYGON) #// two
        glTexCoord2f(0,.5); glVertex3f( 1.0, 1.0, 1.0)
        glTexCoord2f(.5,.5); glVertex3f( 1.0,-1.0, 1.0)
        glTexCoord2f(.5,0); glVertex3f( 1.0,-1.0,-1.0)
        glTexCoord2f(0,0); glVertex3f( 1.0, 1.0,-1.0)
        glEnd()

        glBegin(GL_POLYGON) #// six
        glTexCoord2f(0,0.5); glVertex3f(-1.0, 1.0,-1.0)
        glTexCoord2f(.5,.5); glVertex3f(-1.0, 1.0, 1.0)
        glTexCoord2f(0.5,0); glVertex3f( 1.0, 1.0, 1.0)
        glTexCoord2f(0,0); glVertex3f( 1.0, 1.0,-1.0)
        glEnd()

        glBegin(GL_POLYGON) #// one
        glTexCoord2f(0,0.5); glVertex3f(-1.0, -1.0, 1.0)
        glTexCoord2f(.5,.5); glVertex3f(-1.0, -1.0,-1.0)
        glTexCoord2f(.5,0); glVertex3f( 1.0, -1.0,-1.0)
        glTexCoord2f(0,0); glVertex3f( 1.0, -1.0, 1.0)
        glEnd()

        glBegin(GL_POLYGON) #//four
        glTexCoord2f(0,.5); glVertex3f( 1.0, 1.0,-1.0)
        glTexCoord2f(.5,.5); glVertex3f( 1.0,-1.0,-1.0)
        glTexCoord2f(.5,0); glVertex3f(-1.0,-1.0,-1.0)
        glTexCoord2f(0,0); glVertex3f(-1.0, 1.0,-1.0)
        glEnd()


class Texuture_Square():
    def __init__():
        pass

    def draw():
        glBegin (GL_QUADS)
        glTexCoord2f (0.0, 0.0)
        glVertex3f (0.0, 0.0, 0.0)
        glTexCoord2f (.5, 0.0)
        glVertex3f (10.0, 0.0, 0.0)
        glTexCoord2f (.5, .5)
        glVertex3f (10.0, 10.0, 0.0)
        glTexCoord2f (0.0, .5)
        glVertex3f (0.0, 10.0, 0.0)
        glEnd ()    


class Texture_Triangle():
    def __init__():
        pass
        
    def draw():
        glBegin(GL_TRIANGLES)
        glTexCoord2f(0,0)
        glVertex2f(0,1)
        glTexCoord2f(.5,0)
        glVertex2f(-1,-1)
        glTexCoord2f(.5,.5)
        glVertex2f(1,-1)
        glEnd()
