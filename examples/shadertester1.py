import OpenGL
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

window = 0                                             # glut window number
width, height = 500, 400                               # window size

def draw():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # ToDo draw rectangle
    
    glutSwapBuffers()
    

# initialization
glutInit() 
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
glutInitWindowSize(width, height)   
glutInitWindowPosition(0, 0)
window = glutCreateWindow(b"noobtuts.com") 
glutDisplayFunc(draw)
glutIdleFunc(draw)
glutMainLoop()

