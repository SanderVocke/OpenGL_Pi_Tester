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
vertexshaderpath='./using/vertexshader.glsl'
fragmentshaderpath='./using/fragmentshader.glsl'
inputimagepath='./using/image.png'
#window width
DEFAULT_WIDTH = 1600

#the plot widget
class GLWidget(QGLWidget):
	def initializeGL(self):
		"""Initialize OpenGL, VBOs, upload data on the GPU, etc."""
		# background color
		gl.glClearColor(0, 0, 0, 0)
		# create a Vertex Buffer Object with the specified data
		self.vbo = glvbo.VBO(self.data)
		# compile the vertex shader
		vs = compile_vertex_shader(vertexshader)
		# compile the fragment shader
		ifs = compile_fragment_shader(inputfragmentshader)
		ofs = compile_fragment_shader(outputfragmentshader)
		# compile the vertex shader
		self.ishaders_program = link_shader_program(vs, ifs)
		self.oshaders_program = link_shader_program(vs, ofs)
		#make textures
		self.inputTex = gl.glGenTextures(1)
		gl.glBindTexture(gl.GL_TEXTURE_2D, self.inputTex)
		gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, input_image.width(), input_image.height(), 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, img_data)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
		gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

	def paintGL(self):
		"""Paint the scene."""
		# clear the buffer
		gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		#use the program
		gl.glUseProgram(self.ishaders_program)
		#set uniforms
		gl.glUniform2f(gl.glGetUniformLocation(self.ishaders_program, "offset"), -1, 0)
		gl.glUniform2f(gl.glGetUniformLocation(self.ishaders_program, "scale"), 2, 1)
		gl.glUniform1i(gl.glGetUniformLocation(self.ishaders_program, "tex"), 0)
		# bind the VBO 
		self.vbo.bind()
		# bind the texture
		gl.glBindTexture(gl.GL_TEXTURE_2D, self.inputTex)
		#bind texture here!
		loc = gl.glGetAttribLocation(self.ishaders_program, "vertex");
		# these vertices contain 4 single precision coordinates
		gl.glVertexAttribPointer(loc, 4, gl.GL_FLOAT, gl.GL_FALSE, 16, None)
		# tell OpenGL that the VBO contains an array of vertices
		# prepare the shader        
		gl.glEnableVertexAttribArray(loc)        
		# draw "count" points from the VBO
		gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)
		
		#use the program
		gl.glUseProgram(self.oshaders_program)
		#set uniforms
		gl.glUniform2f(gl.glGetUniformLocation(self.oshaders_program, "offset"), -1, -1)
		gl.glUniform2f(gl.glGetUniformLocation(self.oshaders_program, "scale"), 2, 1)
		gl.glUniform1i(gl.glGetUniformLocation(self.oshaders_program, "tex"), 0)
		# bind the VBO 
		self.vbo.bind()
		# bind the texture
		gl.glBindTexture(gl.GL_TEXTURE_2D, self.inputTex)
		#bind texture here!
		loc = gl.glGetAttribLocation(self.ishaders_program, "vertex");
		# these vertices contain 4 single precision coordinates
		gl.glVertexAttribPointer(loc, 4, gl.GL_FLOAT, gl.GL_FALSE, 16, None)
		# tell OpenGL that the VBO contains an array of vertices
		# prepare the shader        
		gl.glEnableVertexAttribArray(loc)        
		# draw "count" points from the VBO
		gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

	def resizeGL(self, width, height):
		"""Called upon window resizing: reinitialize the viewport."""
		# update the window size
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
		self.setGeometry(50, 50, width, height)
		self.setCentralWidget(self.widget)
		self.show()

#load the shaders
f = open(vertexshaderpath, "r")
vertexshader = f.read()
f.close()
f = open(fragmentshaderpath, "r")
outputfragmentshader = f.read()
f.close()
f = open('./using/inputcopy.glsl', "r")
inputfragmentshader = f.read()
f.close()

#fill the vertex buffer
data = np.array([
0,0,1,1,
1,0,1,1,
0,1,1,1,
1,1,1,1
], dtype=np.float32)

#load the input image
input_image = QtGui.QImage(inputimagepath)
input_image = input_image.convertToFormat(QtGui.QImage.Format_ARGB32)
width = DEFAULT_WIDTH
height = width/input_image.width()*2*input_image.height()
img_data = np.empty(input_image.width()*input_image.height()*4, dtype=np.ubyte)
for i in range (0,input_image.height()):
	for j in range (0,input_image.width()):
		pixel = input_image.pixel(j,i)
		img_data[((input_image.height()-i-1)*input_image.width()+j)*4+0] = QtGui.qRed(pixel)
		img_data[((input_image.height()-i-1)*input_image.width()+j)*4+1] = QtGui.qGreen(pixel)
		img_data[((input_image.height()-i-1)*input_image.width()+j)*4+2] = QtGui.qBlue(pixel)
		img_data[((input_image.height()-i-1)*input_image.width()+j)*4+3] = 255
#ptr = input_image.bits()
#ptr.setsize(input_image.byteCount())
#img_data = np.copy(np.asarray(ptr))
#img_data.resize(len(img_data)+1)
#img_data[len(img_data)-1]=256 #move to make RGBA for OpenGL
#img_data = img_data[1:]

# show the window
win = create_window(TestWindow)

