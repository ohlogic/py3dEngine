#!/usr/bin/python3

import glfw
import OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *

import sys
import math
import time
import numpy as np
import random
random.seed(7337)

import sys
sys.path.append("./libs")
#sys.path.insert(0, "./db")

from db import *

from objloader import *
#from objloader_dbload import *
from printfuncs import *


#https://stackoverflow.com/a/23356273/4084546
#https://www.erikrotteveel.com/python/three-dimensional-ray-tracing-in-python/
def ray_intersect_triangle(p0, p1, triangle):
    # Tests if a ray starting at point p0, in the direction
    # p1 - p0, will intersect with the triangle.
    #
    # arguments:
    # p0, p1: numpy.ndarray, both with shape (3,) for x, y, z.
    # triangle: numpy.ndarray, shaped (3,3), with each row
    #     representing a vertex and three columns for x, y, z.
    #
    # returns: 
    #    0.0 if ray does not intersect triangle, 
    #    1.0 if it will intersect the triangle,
    #    2.0 if starting point lies in the triangle.
    v0, v1, v2 = triangle
    u = v1 - v0
    v = v2 - v0
    normal = np.cross(u, v)
    b = np.inner(normal, p1 - p0)
    a = np.inner(normal, v0 - p0)
    
    # Here is the main difference with the code in the link.
    # Instead of returning if the ray is in the plane of the 
    # triangle, we set rI, the parameter at which the ray 
    # intersects the plane of the triangle, to zero so that 
    # we can later check if the starting point of the ray
    # lies on the triangle. This is important for checking 
    # if a point is inside a polygon or not.
    
    if (b == 0.0):
        # ray is parallel to the plane
        if a != 0.0:
            # ray is outside but parallel to the plane
            return 0
        else:
            # ray is parallel and lies in the plane
            rI = 0.0
    else:
        rI = a / b
    if rI < 0.0:
        return 0
    w = p0 + rI * (p1 - p0) - v0
    denom = np.inner(u, v) * np.inner(u, v) - \
        np.inner(u, u) * np.inner(v, v)
    si = (np.inner(u, v) * np.inner(w, v) - \
        np.inner(v, v) * np.inner(w, u)) / denom
    
    if (si < 0.0) | (si > 1.0):
        return 0
    ti = (np.inner(u, v) * np.inner(w, u) - \
        np.inner(u, u) * np.inner(w, v)) / denom
    
    if (ti < 0.0) | (si + ti > 1.0):
        return 0
    if (rI == 0.0):
        # point 0 lies ON the triangle. If checking for 
        # point inside polygon, return 2 so that the loop 
        # over triangles can stop, because it is on the 
        # polygon, thus inside.
        return 2
    return 1
    
    
def generate_objs():

    cur = db.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM worldmap_objects ORDER BY id ASC;')
    #row = cur.fetchone()
        
    str1 = ""
    count = 0
    for row in cur.fetchall():
        str1 += 'self.obj%s = OBJ100("%s", swapyz=True, name="%s", id="%s", rx="%s", ry="%s", tx="%s", ty="%s");\n' % \
        (count, row['objectname'], row['objectname'].split(".")[0], row['id'], row['rx'], row['ry'], row['tx'], row['ty'])
        
        count += 1
        
    return str1
    
    
def generate_objs_list():

    cur = db.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM worldmap_objects ORDER BY id ASC;')
    
    str1 = "self.objs = ["
    count = 0
    for row in cur.fetchall():
        str1 += 'self.' + 'obj' + str(count) + ','
        count +=1
        
    if len(row) > 0:
        str1 = str1[:-1] # remove last comma
    
    str1 += ']'
    return str1
    
    
def generate_obj_matrix():
    global selected_obj, oo, objs, rand, zpos

    cur = db.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT fixobj FROM worldmap_objects;')
    str1 = ""
    count = 0
    for row in cur.fetchall():
    
        glPushMatrix()
    
        str1 = row['fixobj']
        if str1 != None:
            exec( str1 ) # e.g., glTranslate(10,0,0);glRotate(90, 1, 0, 0);glRotate(180, 0, 1, 0); 

        
        if selected_obj == count: 
            glTranslate(float(oo.tx)/20., float(oo.ty)/20., - zpos)
            glRotate(float(oo.rx), 1, 0, 0)
            glRotate(float(oo.ry), 0, 1, 0)
        else:
            glTranslate(float(map.objs[count].tx)/20., float(map.objs[count].ty)/20., - zpos)
            glRotate(float(map.objs[count].rx), 1, 0, 0)
            glRotate(float(map.objs[count].ry), 0, 1, 0)
        
        str1 = "glCallList(map.obj"+str(count)+".gl_list);"
        exec ( str1 )

        glPopMatrix()
      
        count +=1
       
def update_rotate_vals(oo):
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('UPDATE worldmap_objects SET rx = "%s" WHERE id = "%s";' % (oo.rx , oo.id ))
    cur.execute('UPDATE worldmap_objects SET ry = "%s" WHERE id = "%s";' % (oo.ry , oo.id ))
    db.commit()
     
def update_move_vals(oo):
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('UPDATE worldmap_objects SET tx = "%s" WHERE id = "%s";' % (oo.tx , oo.id ))
    cur.execute('UPDATE worldmap_objects SET ty = "%s" WHERE id = "%s";' % (oo.ty , oo.id ))
    db.commit()
     
class WorldMap(object):

    def __init__(self):
        self.angle = 0
        self.vertices = []
        self.faces = []
        self.coordinates = [0, 0, -65]  # [x,y,z]
        self.position = [0, 0, -50]
        
        #exec( generate_objs() ) # for dynamic code generation of n objects

        #manual creation of objects
        self.obj0 = OBJx("box.obj", swapyz=True, name="box", id="box", rx="0", ry="0", tx="0", ty="0")
        self.obj1 = OBJx("xmas_tree.obj", swapyz=True, name="xmas_tree", id="xmas_tree", rx="0", ry="0", tx="0", ty="0")
        self.obj2 = OBJx("teddy.obj", swapyz=True, name="teddy", id="teddy", rx="0", ry="0", tx="0", ty="0")
        
        #exec( generate_objs_list() ) # for dynamic code generation of n objects 
        
        #manual creation of list of objects
        self.objs = [self.obj0, self.obj1, self.obj2]
        
    def render_scene(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.902, 0.902, 1, 0.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0, 0, 0, math.sin(math.radians(self.angle)), 0, math.cos(math.radians(self.angle)) * -1, 0, 1, 0)
        glTranslatef(self.coordinates[0], self.coordinates[1], self.coordinates[2])

    def move_forward(self):
        self.coordinates[2] += 10 * math.cos(math.radians(self.angle))
        self.coordinates[0] -= 10 * math.sin(math.radians(self.angle))

    def move_back(self):
        self.coordinates[2] -= 10 * math.cos(math.radians(self.angle))
        self.coordinates[0] += 10 * math.sin(math.radians(self.angle))

    def move_left(self, n):
        self.coordinates[0] += n * math.cos(math.radians(self.angle))
        self.coordinates[2] += n * math.sin(math.radians(self.angle))

    def move_right(self, n):
        self.coordinates[0] -= n * math.cos(math.radians(self.angle))
        self.coordinates[2] -= n * math.sin(math.radians(self.angle))

    def rotate(self, n):
        self.angle += n

    def fullRotate(self):
        for i in range(0, 36):
            self.angle += 10
            self.move_left(10)
            self.render_scene()
            #generate_obj_matrix()
            drawit()
            
    def mouseLeftClick(self, x, y):
        
        viewport     = glGetIntegerv(GL_VIEWPORT)
        matrixModelView  = glGetDoublev(GL_MODELVIEW_MATRIX)
        matrixProjection = glGetDoublev(GL_PROJECTION_MATRIX)
        #print ('coordinates mouse are', x, y)
        #print ('Coordinates at cursor are', x, viewport[3] - float(y) - 1)
        realy = viewport[3] - float(y) - 1;
        #print ('World coords at z=0 are', gluUnProject(x, realy, 0, matrixModelView, matrixProjection, viewport))
        #print ('World coords at z=1 are', gluUnProject(x, realy, 1, matrixModelView, matrixProjection, viewport))
        p = []
        p.append(gluUnProject(x, realy, 0, matrixModelView, matrixProjection, viewport))
        p.append(gluUnProject(x, realy, 1, matrixModelView, matrixProjection, viewport))
        return p 





def drawit():

    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE) # wiremesh objects
    map.render_scene()



    # Manual creation of rending objects
    glPushMatrix()
    glTranslate(20,0,0)
    
    if selected_obj == 0:
        glTranslate(float(oo.tx)/20., float(oo.ty)/20., 0)
        glRotate(float(oo.rx), 1, 0, 0)
        glRotate(float(oo.ry), 0, 1, 0)
    else:
        glTranslate(float(map.objs[0].tx)/20., float(map.objs[0].ty)/20., 0)
        glRotate(float(map.objs[0].rx), 1, 0, 0)
        glRotate(float(map.objs[0].ry), 0, 1, 0)
        
    glCallList(map.obj0.gl_list)
    glPopMatrix()
    #############
    
    
    glPushMatrix()
    glTranslate(10,0,0)
    glRotate(90, 1, 0, 0)
    glRotate(180, 0, 1, 0)
    
    if selected_obj == 1:
        glTranslate(float(oo.tx)/20., float(oo.ty)/20., 0)
        glRotate(float(oo.rx), 1, 0, 0)
        glRotate(float(oo.ry), 0, 1, 0)
        
    else:
        glTranslate(float(map.objs[1].tx)/20., float(map.objs[1].ty)/20., 0)
        glRotate(float(map.objs[1].rx), 1, 0, 0)
        glRotate(float(map.objs[1].ry), 0, 1, 0)
        
    glCallList(map.obj1.gl_list)
    glPopMatrix()
    #############
    
    glPushMatrix()
    glTranslate(-10,0,0)
    glRotate(270, 1, 0, 0)
    glRotate(0,   0, 1, 0)
    
    if selected_obj == 2:
        glTranslate(float(oo.tx)/20., float(oo.ty)/20., 0)
        glRotate(float(oo.rx), 1, 0, 0)
        glRotate(float(oo.ry), 0, 1, 0)
    else:
        glTranslate(float(map.objs[2].tx)/20., float(map.objs[2].ty)/20., 0)
        glRotate(float(map.objs[2].rx), 1, 0, 0)
        glRotate(float(map.objs[2].ry), 0, 1, 0)
        
    glCallList(map.obj2.gl_list)
    glPopMatrix()
    #############


    # dynamic creation of n objects
    #generate_obj_matrix()



def mouse(x, y):
    selectbuffer = 10000
    glSelectBuffer(selectbuffer)
    glRenderMode(GL_SELECT)
    glInitNames()
    glPushName(0)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    vp = glGetIntegerv(GL_VIEWPORT)
    gluPickMatrix(x, vp[3] - y -1, 1, 1, vp)
    gluPerspective(30.0, vp[2]/vp[3], 1.0, 1000.0) # if out of range, then select dont work, 1000 good
    glMatrixMode(GL_MODELVIEW)
    
    
    
    
    #drawObjs(name=True)
    drawit()



    glMatrixMode(GL_PROJECTION)
    glPopMatrix()

    hits = glRenderMode(GL_RENDER)
    for n in hits:
        h = n.names[0]
        print ('Triangle id (select method):', h)
    glMatrixMode(GL_MODELVIEW)



def handle_mouse_button(window, button, act, mods):
    global rotate, move, start_x, start_y, storeit
    
    if button == glfw.MOUSE_BUTTON_LEFT and act == glfw.RELEASE:
        rotate = False
        #update_rotate_vals(oo)
        xx, yy = glfw.get_cursor_pos(window)
        storeit = map.mouseLeftClick(xx, yy)
        
        v = ray_intersect_triangle(np.array(storeit[0]), np.array(storeit[1]), \
            np.array([[ 0.0, 1.0, 0.0], [-1.0,-1.0, 0.0],[ 1.0,-1.0, 0.0]]) )
        if v == 1:
            print ('intersect (ray intersect triangle method):', v )
    
    elif button == glfw.MOUSE_BUTTON_MIDDLE and act == glfw.RELEASE:
        print ('middle mouse, release up')
    elif button == glfw.MOUSE_BUTTON_RIGHT and act == glfw.RELEASE:
        move = False
        #update_move_vals(oo)
        
        
    elif button == glfw.MOUSE_BUTTON_LEFT and glfw.PRESS:
        x, y = glfw.get_cursor_pos(window)
        mouse(x, y)
        rotate = True
    elif button == glfw.MOUSE_BUTTON_MIDDLE and glfw.PRESS:
        print ('middle mouse click down')
    elif button == glfw.MOUSE_BUTTON_RIGHT and glfw.PRESS:
        move = True
        start_x, start_y = glfw.get_cursor_pos(window)

    
    
def handle_mouse_move(window, xpos, ypos):
    global oo
    
    mouse = (xpos, glfw.get_window_size(window)[1] - ypos)
    if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT):
        print ('yes, left button held', xpos, ypos)
        i = xpos
        j = ypos
        if rotate:
            oo.rx = float(oo.rx) + float(i)/80.
            oo.ry = float(oo.ry) + float(j)/80.
        
    if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_RIGHT):
        print ('yes, right button held',xpos, ypos)
        
        end_x, end_y = glfw.get_cursor_pos(window)
        i = end_x - start_x
        j = start_y - end_y
        print ('relative coordinates',  i , j )
        if move:
            oo.tx = float(oo.tx) + float(i)/20.
            oo.ty = float(oo.ty) + float(j)/20.


def handle_scroll(window, x_offset, y_offset):
    print (x_offset, y_offset)
    
    
def key_event(win, key, scancode, action, mods):
    global map, selected_obj, oo 
    
    if action == glfw.PRESS:
        # ESC to quit
        if key == glfw.KEY_ESCAPE: 
            print ('esc')
            glfw.set_window_should_close(win, True)
            
        elif key == glfw.KEY_TAB:
            selected_obj +=1
            if selected_obj >= len(map.objs):
                selected_obj = 0
            oo = map.objs[selected_obj]
        elif key == glfw.KEY_LEFT:
            print ('left')
            map.move_left(10)
        elif key == glfw.KEY_RIGHT:
            print ('right')
            map.move_right(10)
        elif key == glfw.KEY_UP:
            print ('up')
            map.move_forward()
        elif key == glfw.KEY_DOWN:
            print ('down')
            map.move_back()
        elif key == glfw.KEY_KP_SUBTRACT:
            map.rotate(-5)
        elif key == glfw.KEY_KP_ADD:
            map.rotate(5)

def render(window):
    global map, oo, selected_obj, rotate, move
    
    
    drawit()

    glFlush()



def onSize(win, width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(30.0, width/height, 1.0, 1000.0)
    glMatrixMode(GL_MODELVIEW)
        
def main():
    global map, oo, selected_obj, zpos, storeit
    selected_obj = 0
    
    if not glfw.init():
        return

    #glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    #glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    #glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
    #glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    width, height = 800, 600
    window = glfw.create_window(width, height, "OpenGL & Python", None, None)
    
    glfw.make_context_current(window)
       
    if not window:
        return

    glfw.set_key_callback(window, key_event)
    glfw.set_cursor_pos_callback(window, handle_mouse_move)
    glfw.set_mouse_button_callback(window, handle_mouse_button)
    glfw.set_scroll_callback(window, handle_scroll)
    glfw.set_window_size_callback(window, onSize)



    glLightfv(GL_LIGHT0, GL_POSITION,  (-40, 200, 100, 0.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHTING)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)           # most obj files expect to be smooth-shaded

    # Function checker
    #glDisable(GL_TEXTURE_2D)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glEnable(GL_CULL_FACE)
    #
    

    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(30.0, width/height, 1.0, 1000.0)
    glMatrixMode(GL_MODELVIEW)
        
        
        
    map = WorldMap()
    
    frame_times = []
    start_t = time.time()


    zpos = 5
    rotate = move = False
    oo = map.objs[selected_obj]
    

    storeit = None
    
    
    while not glfw.window_should_close(window):

        render(window)
        
        
        
        
        if storeit != None:

            glPushMatrix()
            #glLineWidth(2.5)
            glColor3f(1.0, 0.0, 0.0)
            q1, q2 = storeit
            
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            
            #glClear(GL_COLOR_BUFFER_BIT)
            glBegin(GL_LINES)
            glVertex3f(q1[0], q1[1], q1[2])
            glVertex3f(q2[0], q2[1], q2[2])
            glEnd()
            glPopMatrix()


        glPushMatrix()
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_TRIANGLES)
        glVertex3f( 0.0, 1.0, 0.0)
        glVertex3f(-1.0,-1.0, 0.0)
        glVertex3f( 1.0,-1.0, 0.0)
        glEnd()
        glPopMatrix()
        
        
        
        
        
        
        end_t = time.time()
        time_taken = end_t - start_t
        start_t = end_t
        frame_times.append(time_taken)
        frame_times = frame_times[-20:]
        fps = len(frame_times) / sum(frame_times)
        
        
        glut_print(0, height-10, oo.name)
        glut_print(width-170, height-10, str(fps))
        
        
        
        glfw.swap_buffers(window)

        glfw.poll_events()

    glfw.terminate()


if __name__ == '__main__':
   main()
