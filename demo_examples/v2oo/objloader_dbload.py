#!/usr/bin/python3

# not used in demos, used in dynamic object creation version, 
# shown for illustrative purposes

import pygame
from OpenGL.GL import *

import os.path
from os import path

from db import *

import io

import copy

def MTLdb(filename, x):
    contents = {}
    mtl = None
    
    if path.exists(filename):
        fpp = open(filename, "r")
    else:
        cur = db.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT mtl FROM worldmap_objects WHERE objectname = "%s";' % x)
        row = cur.fetchone()
        y =  copy.deepcopy(row['mtl'])
        fpp = io.StringIO(y)
    
    
    for line in fpp:
        if line.startswith('#'): continue
        values = line.split()
        if not values: continue
        if values[0] == 'newmtl':
            mtl = contents[values[1]] = {}
        elif mtl is None:
            raise ValueError("mtl file doesn't start with newmtl stmt")
        elif values[0] == 'map_Kd':
            # load the texture referred to by this declaration
            mtl[values[0]] = values[1]
            surf = pygame.image.load(mtl['map_Kd'])
            image = pygame.image.tostring(surf, 'RGBA', 1)
            ix, iy = surf.get_rect().size
            texid = mtl['texture_Kd'] = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texid)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,
                GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,
                GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA,
                GL_UNSIGNED_BYTE, image)
        else:
            mtl[values[0]] = list(map(float, values[1:]))
    
    if path.exists(filename):
        fpp.close
    
    
    return contents

class OBJdb:
    def __init__(self, filename, swapyz=False):
        """Loads a Wavefront OBJ file. """
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []

        material = None
        
        

        if path.exists(filename):
            fp = open(filename, "r")
        else:
            cur = db.cursor(MySQLdb.cursors.DictCursor)
            cur.execute('SELECT objectname, data FROM worldmap_objects WHERE objectname = "%s";' % filename)
            row = cur.fetchone()
            y =  copy.deepcopy(row['data'])
            fp = io.StringIO(y)
            
        for line in fp:
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'v':
                v = list(map(float, values[1:4]))
                if swapyz:
                    v = v[0], v[2], v[1]
                self.vertices.append(v)
            elif values[0] == 'vn':
                v = list(map(float, values[1:4]))
                if swapyz:
                    v = v[0], v[2], v[1]
                self.normals.append(v)
            elif values[0] == 'vt':
                self.texcoords.append(list(map(float, values[1:3])))
            elif values[0] in ('usemtl', 'usemat'):
                material = values[1]
            elif values[0] == 'mtllib':
                self.mtl = MTLdb(values[1], filename)
            elif values[0] == 'f':
                face = []
                texcoords = []
                norms = []
                for v in values[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                    if len(w) >= 2 and len(w[1]) > 0:
                        texcoords.append(int(w[1]))
                    else:
                        texcoords.append(0)
                    if len(w) >= 3 and len(w[2]) > 0:
                        norms.append(int(w[2]))
                    else:
                        norms.append(0)
                self.faces.append((face, norms, texcoords, material))
        
        if path.exists(filename):
            fp.close

        self.gl_list = glGenLists(1)
        glNewList(self.gl_list, GL_COMPILE)
        glEnable(GL_TEXTURE_2D)
        glFrontFace(GL_CCW)
        count = 1
        for face in self.faces:
            vertices, normals, texture_coords, material = face


            if "mtl" in vars(self).keys():
                mtl = self.mtl[material]
                
                if 'texture_Kd' in mtl:
                    # use diffuse texmap
                    glBindTexture(GL_TEXTURE_2D, mtl['texture_Kd'])
                else:
                    # just use diffuse colour
                    glColor(*mtl['Kd'])
            glLoadName(count)
            print ('yyy' + str(count))
            glBegin(GL_POLYGON)
            print ()
            for i in range(len(vertices)):
                if normals[i] > 0:
                    glNormal3fv(self.normals[normals[i] - 1])
                if texture_coords[i] > 0:
                    glTexCoord2fv(self.texcoords[texture_coords[i] - 1])
                glVertex3fv(self.vertices[vertices[i] - 1])
                print (self.vertices[vertices[i] - 1])
            glEnd()
            count +=1
        glDisable(GL_TEXTURE_2D)
        glEndList()
        
        
class OBJ100(OBJdb):
    def __init__(self,x,swapyz, name, id, rx, ry, tx, ty):
        super().__init__(x, swapyz) 
        self.rx = rx
        self.ry = ry
        self.tx = tx
        self.ty = ty
        self.name = name
        self.id = id