#!/usr/bin/python3
import pyglet
from pyglet.gl import *

import sys
sys.path.insert(0, "./db")
from db import *

def generate_objs():
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM worldmap_objects ORDER BY id ASC;')
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

def generate_obj_matrix(winpg):
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT fixobj FROM worldmap_objects;')
    str1 = ""
    count = 0

    for row in cur.fetchall():
        glPushMatrix()
        
        str1 = row['fixobj']

        if str1 != None:
            exec( str1 ) # e.g., glTranslate(10,0,0);glRotate(90, 1, 0, 0);glRotate(180, 0, 1, 0);

        if winpg.selected_obj == count:
            glTranslatef(float(winpg.oo.tx)/20., float(winpg.oo.ty)/20., - winpg.zpos)
            glRotatef(float(winpg.oo.rx), 1, 0, 0)
            glRotatef(float(winpg.oo.ry), 0, 1, 0)
        else:
            glTranslatef(float(winpg.map.objs[count].tx)/20., float(winpg.map.objs[count].ty)/20., -  winpg.zpos)
            glRotatef(float(winpg.map.objs[count].rx), 1, 0, 0)
            glRotatef(float(winpg.map.objs[count].ry), 0, 1, 0)

        str1 = "glCallList(winpg.map.obj"+str(count)+".gl_list);"
        exec ( str1 )
        glPopMatrix()
        count +=1

def update_rotate_vals(oo):
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('UPDATE worldmap_objects SET rx = "%s" WHERE id = "%s";' % \
        (oo.rx , oo.id ))
    cur.execute('UPDATE worldmap_objects SET ry = "%s" WHERE id = "%s";' % \
        (oo.ry , oo.id ))
    db.commit()

def update_move_vals(oo):
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('UPDATE worldmap_objects SET tx = "%s" WHERE id = "%s";' % (oo.tx , oo.id ))
    cur.execute('UPDATE worldmap_objects SET ty = "%s" WHERE id = "%s";' % (oo.ty , oo.id ))
    db.commit()

