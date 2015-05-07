import sys
# PyQt4 imports
from PyQt4 import QtGui, QtCore, QtOpenGL
from PyQt4.QtOpenGL import QGLWidget
# PyOpenGL imports
import OpenGL.GL as gl
import OpenGL.arrays.vbo as glvbo

# import numpy for generating random data points
import numpy as np
sys.path.insert(0, './dependencies/')
from shadertester2 import *

##################################################
##SETTINGS
##################################################
vertexshaderpath='./shaders/test/vertices.glsl'
fragmentshaderpath='./shaders/test/red.glsl'

#the plot widget
class GLWidget(QGLWidget):
	# default window size
	width, height = 600, 600

	def initializeGL(self):
		"""Initialize OpenGL, VBOs, upload data on the GPU, etc."""
		# background color
		gl.glClearColor(0, 0, 0, 0)
		# create a Vertex Buffer Object with the specified data
		self.vbo = glvbo.VBO(self.data)
		# compile the vertex shader
		vs = compile_vertex_shader(vertexshader)
		# compile the fragment shader
		fs = compile_fragment_shader(fragmentshader)
		# compile the vertex shader
		self.shaders_program = link_shader_program(vs, fs)

	def paintGL(self):
		"""Paint the scene."""
		# clear the buffer
		gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		#use the program
		gl.glUseProgram(self.shaders_program)
		#set uniforms
		gl.glUniform2f(gl.glGetUniformLocation(self.shaders_program, "offset"), 0, 0)
		gl.glUniform2f(gl.glGetUniformLocation(self.shaders_program, "scale"), 1, 1)
		# bind the VBO 
		self.vbo.bind()
		#bind texture here!
		loc = gl.glGetAttribLocation(self.shaders_program, "vertex");
		# these vertices contain 4 single precision coordinates
		gl.glVertexAttribPointer(loc, 4, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
		# tell OpenGL that the VBO contains an array of vertices
		# prepare the shader        
		gl.glEnableVertexAttribArray(loc)        
		# draw "count" points from the VBO
		gl.glDrawArrays(gl.GL_QUADS, 0, 4)

	def resizeGL(self, width, height):
		"""Called upon window resizing: reinitialize the viewport."""
		# update the window size
		self.width, self.height = width, height
		# paint within the whole window
		gl.glViewport(0, 0, width, height)

# define a Qt window with an OpenGL widget inside it
class TestWindow(QtGui.QMainWindow):
	def __init__(self):
		super(TestWindow, self).__init__()
		# initialize the GL widget
		self.widget = GLWidget()
		self.widget.data = data
		# put the window at the screen position (100, 100)
		self.setGeometry(100, 100, self.widget.width, self.widget.height)
		self.setCentralWidget(self.widget)
		self.show()

#load the shaders
f = open(vertexshaderpath, "r")
vertexshader = f.read()
f.close()
f = open(fragmentshaderpath, "r")
fragmentshader = f.read()
f.close()

#fill the vertex buffer
#data = np.zeros((10000, 2), dtype=np.float32)
#data[:,0] = np.linspace(-1., 1., len(data

#fill the vertex buffer
data = np.array([
-0.5,-0.5,1,1,
0.5,-0.5,1,1,
0.5,0.5,1,1,
-0.5,0.5,1,1
], dtype=np.float32)

# show the window
win = create_window(TestWindow)

