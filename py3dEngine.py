#!/usr/bin/python3

#######################
#     Py3dEngine
#######################
# Copyright (c) 2019 Stan S., MIT License
#######################

import pyglet
from pyglet.gl import *
from pyglet.window import key, mouse

import sys
sys.setrecursionlimit(10000)
import math
import random
random.seed(7337)
import time
import sys

sys.path.insert(0, "./db")
from db import *

sys.path.append("./generate_code")
from generate import *

sys.path.append("./basicshapes")
from shapes import *

sys.path.append("./dataobjects")
from terrain import *

sys.path.append("./libs")
from objloader_dbload import *      # without database, use the objloader.py
from printfuncs import *
from algorithms import *
from easy_pyglet_addons import *    # MouseStateHandler

import numpy as np


class WorldMap(object):
    def __init__(self):
        super().__init__()

        self.objs = generate_objs_list()
        
        self.terrain = Terrain_Floor(100,100)
        
       
    def draw_objs(self, window):

        generate_obj_matrix( window )   # dynamic creation of n objects


class WinPygletGame(pyglet.window.Window):

    def __init__(self, refreshrate=240, *args, **kwargs):
        super(WinPygletGame, self).__init__(*args, **kwargs)
        
        self.icoords = [0,0]
        
        self.refreshrate = refreshrate
        self.angle = 0
        self.angleYUpDown = 0
        
        texturefile = "./textures/brick.png"
        self.texture = pyglet.image.load(texturefile).get_texture()

        
        #glClearColor(0.5, 0.69, 1.0, 1)
        glClearColor(0.902, 0.902, 1, 0.0)
        
        glLightfv(GL_LIGHT0, GL_POSITION,  (0, 50, 0, 0.0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)           # most obj files expect to be smooth-shaded
        #glLightModelf(GL_LIGHT_MODEL_LOCAL_VIEWER, GL_TRUE)
        
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
        
        #glDisable(GL_TEXTURE_2D)
        #glEnable(GL_DEPTH_TEST)
        
        # glEnable(GL_BLEND)
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        # glEnable(GL_POINT_SMOOTH)
        # glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)

        glEnable(GL_CULL_FACE)
        glCullFace(GL_FRONT)   # so that objects do not appear to rotate


        self.map = WorldMap()
        self.selected_obj = len(self.map.objs)
        
        # added just to move around the world with mouse
        self.map.objs.append( OBJworld(name='world',x='',swapyz=False,id=0, rx=0, ry=0, tx=0, ty=0) )
        
        #self.frame_times = []
        #self.start_t = time.time()

        self.storeit = None
        
        self.rotate = False
        self.move = False
        self.zpos = 5
        self.oo = self.map.objs[self.selected_obj]


        self.position = [30, 0, -65]
        self.rotation = [180, 0]
        self.angle = self.rotation[0]


        x, y = self.width // 2, self.height // 2
        n = 10
        self.reticle = pyglet.graphics.vertex_list(4,
            ('v2i', (x - n, y, x + n, y, x, y - n, x, y + n))
        )
        
        self.text = None
        

        
        self.reticle_select_mode = True
        
        if self.reticle_select_mode:
            self.set_exclusive_mouse(True)
        
        
        self.mousebuttons = MouseStateHandler()
        self.push_handlers(self.mousebuttons)
        
        self.keyboard = key.KeyStateHandler()
        self.push_handlers(self.keyboard)
        
        
        self.start_press = 0        # on_key_press code to jump strafe
        self.just_jumped = 0        # on_key_press code to jump strafe
        self.lastbutton = None      # on_key_press code to jump strafe
        
        
        self.fViewDistance_x_z = 0  # for zoom glulookat

        self.x = 0
        self.y = 0
        self.dx = 0
        self.dy = 0
        self.rapidFire = True

        pyglet.clock.schedule_interval(self.update, 1/refreshrate)
        
        
    def changeCoordinates(self, x, y):
    
        viewport     = glGetIntegerv(GL_VIEWPORT)
        matrixModelView  = glGetDoublev(GL_MODELVIEW_MATRIX)
        matrixProjection = glGetDoublev(GL_PROJECTION_MATRIX)
        print ('World coords at z=0 are', gluUnProject(x, y, 0, matrixModelView, matrixProjection, viewport))
        print ('World coords at z=1 are', gluUnProject(x, y, 1, matrixModelView, matrixProjection, viewport))
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
        
        if self.reticle_select_mode:
            viewport = self.get_viewport_size()
            x = viewport[0]//2
            y = viewport[1]//2
            
        gluPickMatrix(x, y, 1, 1, vp)
        gluPerspective(30.0, vp[2]/vp[3], 1.0, 1000.0) # if out of range, then select dont work, 1000 good
        glMatrixMode(GL_MODELVIEW)
        
        self.map.draw_objs(self)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        
        hits = glRenderMode(GL_RENDER)
        
        for n in hits:
            h = n.names[0]
            #print (', '.join(i for i in dir(n) if not i.startswith('__')))
            print ('Triangle id (select method):', h, n.near)
            #break # perform loop just once
        print ()
        glMatrixMode(GL_MODELVIEW)
        

    def on_mouse_press(self, x, y, button, modifiers):

        if button == mouse.LEFT:
            self.get_mouseclick_id(x, y)
            self.rotate = True
            
            
        elif button == mouse.MIDDLE:

            self.text = pyglet.text.HTMLLabel(
                '<font face="Times New Roman" size="4">Hello, <i>World</i></font>',
                x=x, y=y,
                anchor_x='center', anchor_y='center')
            
        elif button == mouse.RIGHT:
            self.move = True
        
            
    def on_mouse_release(self, x, y, button, modifiers):
        
        if button == mouse.LEFT:
            self.rotate = False
            update_rotate_vals(self.oo)

        elif button == mouse.MIDDLE:
            print ('middle button released')
        elif button == mouse.RIGHT:
            self.move = False
            update_move_vals(self.oo)
    
    
            self.fViewDistance_x_z = 0
            self.rapidFire = True
        
    def on_mousebutton_hold(self):
    
        if self.mousebuttons[mouse.LEFT]:
            pass
            
        if self.mousebuttons[mouse.RIGHT]:
            self.rapidFire = False
            if self.fViewDistance_x_z <= 25:
            
                self.fViewDistance_x_z += 1
                
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        
        if buttons & mouse.LEFT:
            i = x
            j = y
            if self.rotate:
                self.oo.rx = float(self.oo.rx) + float(i)/80.
                self.oo.ry = float(self.oo.ry) + float(j)/80.

        elif buttons & mouse.RIGHT:
            # if self.oo.name == 'world':
                # self.move_left(-dx) 
                # self.move_up(dy)              
                # return
            # i = dx
            # j = dy
            # if self.move:
                # self.oo.tx = float(self.oo.tx) + float(i)
                # self.oo.ty = float(self.oo.ty) + float(j)


            ###############################
            # for zoom - same code as in on_mouse_motion
            #
            if self.reticle_select_mode:
            
                self.angle += dx/15.
                self.angleYUpDown += dy/15.

                self.angle = self.angle % 360
                self.angleYUpDown = max(-90, min(90, self.angleYUpDown))
                
                self.rotation[0] = self.angle
                self.rotation[1] = self.angleYUpDown
            ###############################
            
    def on_mouse_motion(self, x, y, dx, dy):
        self.x = x  # for on_mousebutton_hold, get_mouseclick_id
        self.y = y  # for on_mousebutton_hold, get_mouseclick_id
        self.dx = dx
        self.dy = dy
        

        if self.reticle_select_mode:
        
            self.angle += dx/20.
            self.angleYUpDown += dy/20.

            self.angle = self.angle % 360
            self.angleYUpDown = max(-90, min(90, self.angleYUpDown))
            
            self.rotation[0] = self.angle
            self.rotation[1] = self.angleYUpDown
            
            
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        print ('SCROLL', x, y, scroll_x, scroll_y)

    def on_mouse_enter(self, x, y):
        pass

    def on_mouse_leave(self, x, y):
        pass

    def rotate3d(self, n):
        self.angle = n
    def move_left(self, n):
        self.position[0] -= n * math.cos(math.radians(self.angle))
        self.position[2] -= n * math.sin(math.radians(self.angle))
    def move_right(self, n):
        self.position[0] += n * math.cos(math.radians(self.angle))
        self.position[2] += n * math.sin(math.radians(self.angle))
    def move_up(self, n):
        self.position[2] -= n * math.cos(math.radians(self.angle))
        self.position[0] += n * math.sin(math.radians(self.angle))
    def move_down(self, n):
        self.position[2] += n * math.cos(math.radians(self.angle))
        self.position[0] -= n * math.sin(math.radians(self.angle))
        
        
    def on_key_release(self, symbol, modifiers):
        pass
        
    def on_key_press(self, symbol, modifiers):
        
        ###############################
        #
        # code to jump strafe
        #
        ############## variables to set
        jump_strafe = 3
        threshold = .8              # this many seconds in between clicks 
                                    #       of a double click to jump strafe 
        wait_in_between_jumps = 2   # wait at least 2 seconds before allowing another jump
        ###############################
        
        time_clock = time.time()
        jump_up = 0
        jump_down = 0
        jump_left = 0
        jump_right = 0        
        #print ('start_press:', self.start_press, '  time:', time_clock)
        
        if (self.start_press - self.just_jumped) > wait_in_between_jumps:
        
            if time_clock - self.start_press < threshold and self.lastbutton == symbol:
                
                if symbol == key.UP:
                    jump_up = jump_strafe
                    print ('jump forward')
                    self.just_jumped = time.time()
                elif symbol == key.DOWN:
                    jump_down = jump_strafe
                    print ('jump backward')
                    self.just_jumped = time.time()
                elif symbol == key.LEFT:
                    jump_left = jump_strafe
                    print ('jump to side left')
                    self.just_jumped = time.time()
                elif symbol == key.RIGHT:
                    jump_right = jump_strafe
                    print ('jump to side right')
                    self.just_jumped = time.time()
            else:
                self.start_press = time_clock
                self.lastbutton = symbol
                jump_up = 0
                jump_down = 0
                jump_left = 0
                jump_right = 0  
        else:
            self.start_press = time_clock
        ###############################
        #
        # end code to jump strafe
        #
        ###############################
            
        if symbol == key.ESCAPE:
            self.reticle_select_mode = not self.reticle_select_mode
            self.set_exclusive_mouse(self.reticle_select_mode)
        elif symbol == key.UP:
            self.move_up(.1+jump_up)
        elif symbol == key.DOWN:
            self.move_down(.1+jump_down)
        elif symbol == key.LEFT:
            self.move_left(.1+jump_left)
        elif symbol == key.RIGHT:
            self.move_right(.1+jump_right)
        elif symbol == key._1:
            self.rotate3d(10)
            self.move_right(10)
        elif symbol == key._2:
            self.rotate3d(-10)
            self.move_left(10)
        elif symbol == key._3:
            self.fullRotate('left')
        elif symbol == key._4:
            self.fullRotate('right')
            
        elif symbol == key.TAB:
            self.selected_obj +=1
            if self.selected_obj >= len(self.map.objs):
                self.selected_obj = 0
            self.oo = self.map.objs[self.selected_obj]
        
        

        
    def on_key_hold(self):
    
        # to move in diagonal directions
        if self.keyboard[key.UP] and self.keyboard[key.LEFT]:
            self.move_up(.1)
            self.move_left(.1)
        elif self.keyboard[key.UP] and self.keyboard[key.RIGHT]:
            self.move_up(.1)
            self.move_right(.1)
        elif self.keyboard[key.DOWN] and self.keyboard[key.LEFT]:
            self.move_down(.1)
            self.move_left(.1)
        elif self.keyboard[key.DOWN] and self.keyboard[key.RIGHT]:
            self.move_down(.1)
            self.move_right(.1)
        elif self.keyboard[key.UP]:
            self.move_up(.1)
        elif self.keyboard[key.DOWN]:
            self.move_down(.1)
        elif self.keyboard[key.LEFT]:
            self.move_left(.1)
        elif self.keyboard[key.RIGHT]:
            self.move_right(.1)
    
        self.icoords = self.map.terrain.coords_to_indices(self.position[0], -self.position[2])
            
    
    def fullRotate(self, direction):

        for i in range(0, 360):
            if direction == 'left':
                self.angle += 1
                self.move_left(1)
            else:
                self.angle -= 1
                self.move_right(1)
            self.on_draw()
            self.dispatch_events()
            self.flip()


    def on_draw(self):

        self.set_3d()
        

        glColor3d(1, 1, 1)
        
        #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE) # add wiremesh mode

        glBindTexture(GL_TEXTURE_2D, 0) # to reset colors one way is to bind the default texture
        
        self.map.draw_objs(self)
        
        #glPolygonMode( GL_FRONT_AND_BACK, GL_FILL ) #remove wiremesh mode
        
        glut_print(0, self.height-10, self.oo.name)
        

        glPushMatrix()
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture.id)
        Texture_Triangle.draw() 
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()
        
        
        glPushMatrix()
        glEnable(GL_TEXTURE_2D)
        glTranslatef(10, 0, 0)
        glBindTexture (GL_TEXTURE_2D, self.texture.id)
        Texuture_Square.draw()
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()
        
        
        glPushMatrix()
        glTranslatef(5, 0, 0)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture.id)
        Texuture_Cube.draw()
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()  
        

        self.map.terrain.draw()
        
        self.on_key_hold()
        
        self.set_2d()
        
        x,y,z = self.position
        infotext = '%02d (%.2f, %.2f, %.2f)' % (
            pyglet.clock.get_fps(), x, y, z)
            
            
        drawText((self.width-500, self.height-30, 0), infotext)
        glut_print(0, self.height-35, "Toggle: ESC - to show/hide mouse")
        
        glut_print(0, self.height-55, str(self.rotation))

        glut_print(0, self.height-75, ('terrain indices from coords:'+ str(self.icoords) ))


        if self.fViewDistance_x_z > 0:
            glColor3f(1,1,1)
            glBegin(GL_TRIANGLE_STRIP)
            x1 = self.width//2
            y1 = self.height//2
            radius = 49
            for angle in np.arange(1, 25, 0.2):
                x2 = x1+math.sin(angle)*radius
                y2 = y1+math.cos(angle)*radius
                glVertex2f(x2,y2)
            glEnd()
        
        if self.reticle_select_mode:
            self.draw_reticle()
            
            # type of recticle for zoom
            if self.fViewDistance_x_z > 0:
                    glColor3d(0, 1, 0)
                    x, y = self.width // 2, self.height // 2
                    n = 45
                    pyglet.graphics.vertex_list(4,
                    ('v2i', (x - n, y, x + n, y, x, y - n, x, y + n))).draw(GL_LINES)
        
        if self.text:
            self.text.draw()

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

    def set_3d(self):
        """ Configure OpenGL to draw in 3d.
        """
        self.clear()

        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        
        glLoadIdentity()
        gluPerspective(30.0, width / float(height), 1, 1000.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity() 
        
        glLoadIdentity()
        
        ###############################
        #  code for zoom 
        ###############################
        offset=0
        flip = 1
        if self.fViewDistance_x_z > 0:
            glRotatef(180, 0,0,1)
            glRotatef(180, 1,0,0)
            offset = -135
            flip = -1
            gluLookAt(self.fViewDistance_x_z, 0, self.fViewDistance_x_z, 0,0,0,0,1,0)
        ###############################

        gluLookAt(0, 0, 0, 
            math.sin(math.radians(self.angle+offset)), 
            math.sin(math.radians(self.angleYUpDown*flip)), 
            math.cos(math.radians(self.angle+offset)) * -1, 
            0, 1, 0)
        glTranslatef(-self.position[0], -self.position[1], -self.position[2])
        
        
    def draw_reticle(self):
        """ Draw the crosshairs in the center of the screen.
        """
        glColor3d(0, 0, 0)
        self.reticle.draw(GL_LINES)
        
    def on_resize(self, width, height):
        pass 

    def update(self, dt):
        self.on_mousebutton_hold()      # for rapid fire, working
        self.terrain_collision_detection()
        self.on_draw()
    
    def terrain_collision_detection(self):
        cols = self.map.terrain.columns 
        rows = self.map.terrain.rows
        
        x, y, z = self.position
        
        if self.map.terrain.all_floors[self.icoords[0],self.icoords[1]] != None:
            # adjusts height to map terrain
            self.position[1] = self.map.terrain.all_floors[self.icoords[0],self.icoords[1]].floor[int(x), -int(z)]
        else:
            self.position[1] = 0
    
        self.map.terrain.walk_on_create_floor( int(x), -int(z) )

if __name__ == '__main__':
    config = pyglet.gl.Config(double_buffer=True)
    window = WinPygletGame(width=800, height=600, resizable=True, config=config, vsync = False, refreshrate=60)
    pyglet.app.run()
