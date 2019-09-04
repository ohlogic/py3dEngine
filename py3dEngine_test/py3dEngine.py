#!/usr/bin/python3

#######################
#     Py3dEngine
#######################
# Copyright (c) 2019 Stan S., MIT License
#######################

import pyglet
from pyglet.gl import *
#from OpenGL.GL import *
#from OpenGL.GLU import *

import sys
import math
import random
random.seed(7337)
import time
import sys

sys.path.insert(0, "./db")
from db import *

sys.path.append("./generate_code")
import generate
from generate import *

sys.path.append("./basicshapes")
import shapes
from shapes import *

sys.path.append("./dataobjects")
import terrian
from terrian import *

sys.path.append("./libs")
from objloader_dbload import *
from printfuncs import *
from algorithms import *

import numpy as np


class WorldMap(object):
    def __init__(self):
        super().__init__()

        exec( generate_objs() ) # for dynamic code generation of n objects

        exec( generate_objs_list() ) # for dynamic code generation of n objects
        
    def draw_objs(self, window):

        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE) # wiremesh objects

        generate_obj_matrix( window ) # dynamic creation of n objects


class WinPygletGame(pyglet.window.Window):

    def __init__(self, refreshrate=240, *args, **kwargs):
        super(WinPygletGame, self).__init__(*args, **kwargs)
        
        self.refreshrate = refreshrate
        self.angle = 0
        texturefile = "./textures/brick.png"
        self.texture = pyglet.image.load(texturefile).get_texture()
        #glClearColor(0.5, 0.69, 1.0, 1)
        glClearColor(0.902, 0.902, 1, 0.0)
        
        #glLightfv(GL_LIGHT0, GL_POSITION,  (-40, 200, 100, 0.0))
        #glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
        #glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
        #glEnable(GL_LIGHT0)
        #glEnable(GL_LIGHTING)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)           # most obj files expect to be smooth-shaded

        #glDisable(GL_TEXTURE_2D)
        #glEnable(GL_DEPTH_TEST)
        #glEnable(GL_BLEND)
        glEnable(GL_CULL_FACE)


        self.map = WorldMap()

        self.frame_times = []
        self.start_t = time.time()

        self.storeit = None
        self.selected_obj = 0
        self.rotate = False
        self.move = False
        self.zpos = 5
        self.oo = self.map.objs[self.selected_obj]


        self.position = [0, 0, -65]
        self.rotation = [0, 0]

        x, y = self.width // 2, self.height // 2
        n = 10
        self.reticle = pyglet.graphics.vertex_list(4,
            ('v2i', (x - n, y, x + n, y, x, y - n, x, y + n))
        )
        
        self.text = None
        
        
        self.terrian = Terrian_Floor(100,100)
        self.terrain_once = True
        
        
        pyglet.clock.schedule_interval(self.update, 1/refreshrate)
        
        
    def mouseLeftClick(self, x, y):
    
        viewport     = glGetIntegerv(GL_VIEWPORT)
        matrixModelView  = glGetDoublev(GL_MODELVIEW_MATRIX)
        matrixProjection = glGetDoublev(GL_PROJECTION_MATRIX)
        #print ('World coords at z=0 are', gluUnProject(x, realy, 0, matrixModelView, matrixProjection, viewport))
        #print ('World coords at z=1 are', gluUnProject(x, realy, 1, matrixModelView, matrixProjection, viewport))
        p = []
        p.append(gluUnProject(x, y, 0, matrixModelView, matrixProjection, viewport))
        p.append(gluUnProject(x, y, 1, matrixModelView, matrixProjection, viewport))
        return p
        
        
    def get_mouseclick_id(self, x, y):
    
        self.set_3d()

        selectbuffer = 30000
        glSelectBuffer(selectbuffer)
        glRenderMode(GL_SELECT)
        glInitNames()
        glPushName(0)
        glMatrixMode(GL_PROJECTION)
        
        glPushMatrix()
        glLoadIdentity()
        vp = glGetIntegerv(GL_VIEWPORT)
        gluPickMatrix(x, y, 1, 1, vp)
        gluPerspective(30.0, vp[2]/vp[3], 1.0, 1000.0) # if out of range, then select dont work, 1000 good
        glMatrixMode(GL_MODELVIEW)
        
        self.map.draw_objs(self)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        
        hits = glRenderMode(GL_RENDER)
        for n in hits:
            h = n.names[0]
            print ('Triangle id (select method):', h)

        glMatrixMode(GL_MODELVIEW)


    def on_mouse_press(self, x, y, button, modifiers):
        

        if button == pyglet.window.mouse.LEFT:
            self.get_mouseclick_id(x, y)
            self.rotate = True
            
        elif button == pyglet.window.mouse.MIDDLE:

            self.text = pyglet.text.HTMLLabel(
                '<font face="Times New Roman" size="4">Hello, <i>World</i></font>',
                x=x, y=y,
                anchor_x='center', anchor_y='center')
            
        elif button == pyglet.window.mouse.RIGHT:
            self.move = True

    def on_mouse_release(self, x, y, button, modifiers):
        
        
        if button == pyglet.window.mouse.LEFT:
            self.rotate = False
            update_rotate_vals(self.oo)

            self.set_3d()
            self.storeit = self.mouseLeftClick(x, y)
            v = ray_intersect_triangle(np.array(self.storeit[0]), np.array(self.storeit[1]), \
                np.array([[ 0.0, 1.0, 0.0], [-1.0,-1.0, 0.0],[ 1.0,-1.0, 0.0]]) )
            if v == 1:
                print ('intersect (ray intersect triangle method):', v )

        elif button == pyglet.window.mouse.MIDDLE:
            print ('middle button released')
        elif button == pyglet.window.mouse.RIGHT:
            self.move = False
            update_move_vals(self.oo)


    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):

        
        if buttons & pyglet.window.mouse.LEFT:
            i = x
            j = y
            if self.rotate:
                self.oo.rx = float(self.oo.rx) + float(i)/80.
                self.oo.ry = float(self.oo.ry) + float(j)/80.

        elif buttons & pyglet.window.mouse.RIGHT:
            i = dx
            j = dy
            if self.move:
                self.oo.tx = float(self.oo.tx) + float(i)
                self.oo.ty = float(self.oo.ty) + float(j)
        
        
    def on_mouse_motion(self, x, y, dx, dy):
        pass
        
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        print ('SCROLL', x, y, scroll_x, scroll_y)

    def on_mouse_enter(self, x, y):
        pass

    def on_mouse_leave(self, x, y):
        pass

    def rotate3d(self, n):
        self.angle = n
    def move_left(self, n):
        self.position[0] += n * math.cos(math.radians(self.angle))
        self.position[2] += n * math.sin(math.radians(self.angle))
    def move_right(self, n):
        self.position[0] -= n * math.cos(math.radians(self.angle))
        self.position[2] -= n * math.sin(math.radians(self.angle))
    def move_up(self, n):
        self.position[2] += n * math.cos(math.radians(self.angle))
        self.position[0] -= n * math.sin(math.radians(self.angle))
    def move_down(self, n):
        self.position[2] -= n * math.cos(math.radians(self.angle))
        self.position[0] += n * math.sin(math.radians(self.angle))
        
    def on_key_press(self, symbol, modifiers):

        self.clear()

        if symbol == pyglet.window.key.UP:

            self.move_up(10)
        elif symbol == pyglet.window.key.DOWN:
            self.move_down(10)
        elif symbol == pyglet.window.key.LEFT:
            self.move_left(10)
        elif symbol == pyglet.window.key.RIGHT:
            self.move_right(10)
        elif symbol == pyglet.window.key._1:
            self.rotate3d(10)
            self.move_right(10)
        elif symbol == pyglet.window.key._2:
            self.rotate3d(-10)
            self.move_left(10)
        elif symbol == pyglet.window.key._3:
            self.fullRotate('left')
        elif symbol == pyglet.window.key._4:
            self.fullRotate('right')
        elif symbol == pyglet.window.key.TAB:
            self.selected_obj +=1
            if self.selected_obj >= len(self.map.objs):
                self.selected_obj = 0
            self.oo = self.map.objs[self.selected_obj]
        
        self.terrain_once = True
        
    def fullRotate(self, direction):
        
        self.direction = direction 
        
        for i in range(0, 36):
            #self.clear()
            self.terrain_once = True

            if self.direction == 'left':
                self.angle += 1
                self.move_left(1)
            else:
                self.angle -= 1
                self.move_right(1)
            self.on_draw(clear=True)
            self.dispatch_events()
            self.flip()
            
            
    def on_draw(self, clear=False):

        self.set_3d(clear)
        glColor3d(1, 1, 1)
        
        self.map.draw_objs(self)
        
        glPolygonMode( GL_FRONT_AND_BACK, GL_FILL ) #remove wiremesh mode
        
        glut_print(0, self.height-10, self.oo.name)
        
        if self.storeit != None:  # draws line

            glPushMatrix()
            #glLineWidth(2.5)
            #glColor3f(1.0, 0.0, 0.0)
            q1, q2 = self.storeit

            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            glBegin(GL_LINES)
            glVertex3f(q1[0], q1[1], q1[2])
            glVertex3f(q2[0], q2[1], q2[2])
            glEnd()
            glPopMatrix()



        glPushMatrix()
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture.id)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE);
        Texture_Triangle.draw() 
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()
        
        
        glPushMatrix()
        glEnable(GL_TEXTURE_2D)
        glTranslatef(5, 5, 0)
        glBindTexture (GL_TEXTURE_2D, self.texture.id);
        Texuture_Square.draw()
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()
        
        
        glPushMatrix()
        glTranslatef(5, -5, 0)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture.id)
        Texuture_Cube.draw()
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()  
        

        if self.terrain_once:
            
            glPushMatrix()
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE) # add wiremesh
            glTranslatef(-5,0,0)
            glTranslatef(0,-5,0)
            glRotatef(90, 1.0, 0.0, 0.0 )
            self.terrian.draw()
            glPolygonMode( GL_FRONT_AND_BACK, GL_FILL ) # remove wiremesh
            glPopMatrix()

            self.terrain_once = False
        
        
        self.set_2d()
        
        x,y,z = self.position
        
        infotext = '%02d (%.2f, %.2f, %.2f)' % (
            pyglet.clock.get_fps(), x, y, z)
        
        drawText((self.width-500, self.height-30, 0), str(infotext))
                
        if self.text:
            self.text.draw()

        #self.draw_reticle()



    def set_2d(self):
        """ Configure OpenGL to draw in 2d.
        """
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, max(1, width), 0, max(1, height), -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def set_3d(self, clear=False):
        """ Configure OpenGL to draw in 3d.
        """
        if clear:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(30.0, width / float(height), 1, 1000.0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        gluLookAt(0, 0, 0, math.sin(math.radians(self.angle)), 0, math.cos(math.radians(self.angle)) * -1, 0, 1, 0)
        glTranslatef(self.position[0], self.position[1], self.position[2])
        
    def draw_reticle(self):
        """ Draw the crosshairs in the center of the screen.
        """
        glColor3d(0, 0, 0)
        self.reticle.draw(GL_LINES)
        
    def on_resize(self, width, height):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        pass 

    def update(self, dt):
        pass
        

if __name__ == '__main__':
    from pyglet import gl
    config = gl.Config(double_buffer=True)
    window = WinPygletGame(width=800, height=600, resizable=True, config=config, vsync = False, refreshrate=60)
    pyglet.app.run()

