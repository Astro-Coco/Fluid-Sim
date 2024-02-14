from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

def draw():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(0, 0, 5, 0, 0, 0, 0, 1, 0)
    glutWireCube(2)
    glutSwapBuffers()

glutInit()
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
glutInitWindowSize(500, 500)
glutInitWindowPosition(100, 100)
glutCreateWindow(b"Simple OpenGL Example")
glutDisplayFunc(draw)
glEnable(GL_DEPTH_TEST)
glClearColor(0.0, 0.0, 0.0, 1.0)
glutMainLoop()
