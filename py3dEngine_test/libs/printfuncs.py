#!/usr/bin/python3
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import * # only for glut_print
import time

glutInit() # only for glut_print
pygame.font.init()
""" name: glut_print_clock
    requires: these as global, class members
        frame_times = []
        start_t = time.time()
    
    usage example:  glut_print_clock(self, self.width-170, self.height-10)
"""
def glut_print_clock(self, x, y):

    end_t = time.time()
    time_taken = end_t - self.start_t
    self.start_t = end_t
    self.frame_times.append(time_taken)
    frame_times = self.frame_times[-20:]
    fps = len(frame_times) / sum(frame_times)
    text = str(fps)
    
    glColor3f(0, 0, 0)
    glWindowPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ctypes.c_int(ord(ch)))
        

def glut_print(x, y, text):
    glColor3f(0, 0, 0)
    glWindowPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ctypes.c_int(ord(ch)))


def drawText(position, textString):
    font = pygame.font.Font ("/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf", 32)
    textSurface = font.render(textString, True,  (0,0,0,0),(255,255,255,0))
    textData = pygame.image.tostring(textSurface, "RGBA", True)
    glRasterPos3d(*position)  
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)

