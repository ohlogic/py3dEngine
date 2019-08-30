#!/usr/bin/python3
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import * # only for glut_print
import time

glutInit() # only for glut_print

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

def drawTextTran(position, textString):     

    font = pygame.font.Font(None, 64)
    blue = pygame.Color('blue')

    # Render the text surface.
    txt_surf = font.render('transparent text', True, blue)
    # Create a transparent surface.
    alpha_img = pygame.Surface(txt_surf.get_size()) #.convert_alpha()
    # Fill it with white and the desired alpha value.
    alpha_img.fill((0, 0, 0, 0)) # last number is the alpha value 0 for transparent effect
    # Blit the alpha surface onto the text surface and pass BLEND_RGBA_MULT.
    #txt_surf.blit(alpha_img, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)  # transparent effect
    
    txt_surf.blit(alpha_img, (0,0))

    textData = pygame.image.tostring(txt_surf, "RGBA", True) 

    glDrawPixels(txt_surf.get_width(), txt_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)

def drawText(position, textString):     
    font = pygame.font.Font ("/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf", 32)
    textSurface = font.render(textString, True,  (255,255,255,255),(0,0,0,255))     
    textData = pygame.image.tostring(textSurface, "RGBA", True)     
    glRasterPos3d(*position)  

    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)

