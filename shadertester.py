import sys
import os.path, time
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
vertexshaderpath='./resources/vertexshader.glsl'

##################################################
##SETTINGS
##################################################
fragmentshaderpath='./using/fragmentshader.glsl'
inputimagepath='./using/image.png'
#window width
DEFAULT_WIDTH = 1600
NUM_STAGES = 4

#the plot widget
class GLWidget(QGLWidget):
	def initializeGL(self):
		"""Initialize OpenGL, VBOs, upload data on the GPU, etc."""
		self.width = width
		self.height = height
		self.ofs_error=False
		self.sumhor_error=False
		self.sumver_error=False
		# background color
		gl.glClearColor(0, 0, 0, 0)
		# create a Vertex Buffer Object with the specified data
		self.vbo = glvbo.VBO(self.data)
		# compile the vertex shader
		vs = compile_vertex_shader(vertexshader)
		# compile the fragment shader
		ifs = compile_fragment_shader(inputfragmentshader)
		try:
			ofs = compile_fragment_shader(outputfragmentshader)
		except RuntimeError as e:
			print("Compilation error on fragment shader:\n\t{0}".format(e))
			ofs = compile_fragment_shader(inputfragmentshader)
			self.ofs_error = True
		try:
			sumhor = compile_fragment_shader(summerhorizontalshader)
		except RuntimeError as e:
			print("Compilation error on horizontal summer shader:\n\t{0}".format(e))
			sumhor = compile_fragment_shader(inputfragmentshader)
			self.sumhor_error = True
		try:
			sumver = compile_fragment_shader(summerverticalshader)
		except RuntimeError as e:
			print("Compilation error on vertical summer shader:\n\t{0}".format(e))
			sumver = compile_fragment_shader(inputfragmentshader)
			self.sumver_error = True
		# lnk in the vertex shader
		self.ishaders_program = link_shader_program(vs, ifs)
		self.oshaders_program = link_shader_program(vs, ofs)
		self.sumhorshaders_program = link_shader_program(vs, sumhor)
		self.sumvershaders_program = link_shader_program(vs, sumver)
		#make textures
		
		#INPUT TEXTURE (RGBA IMAGE)
		self.inputTex = gl.glGenTextures(1)
		gl.glBindTexture(gl.GL_TEXTURE_2D, self.inputTex)
		gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, input_image.width(), input_image.height(), 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, img_data)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
		gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
		#ERROR TEXTURE (FOR SHOWING IF SOMETHING WENT WRONG)
		self.errorTex = gl.glGenTextures(1)
		gl.glBindTexture(gl.GL_TEXTURE_2D, self.errorTex)
		gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, error_image.width(), error_image.height(), 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, errimg_data)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
		gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
		#OUTPUT TEXTURE (FOR STORING THE OUTPUT)
		self.outTex = gl.glGenTextures(1)
		gl.glBindTexture(gl.GL_TEXTURE_2D, self.outTex)
		gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, input_image.width(), input_image.height(), 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, None)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
		gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
		self.outFB = gl.glGenFramebuffers(1)
		gl.glBindFramebuffer(gl.GL_FRAMEBUFFER,self.outFB)
		gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER,gl.GL_COLOR_ATTACHMENT0,gl.GL_TEXTURE_2D,self.outTex,0)
		gl.glBindFramebuffer(gl.GL_FRAMEBUFFER,0)
		#HORIZONTAL SUMMING TEXTURE
		self.sumhorTex = gl.glGenTextures(1)
		gl.glBindTexture(gl.GL_TEXTURE_2D, self.sumhorTex)
		gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, 1, input_image.height(), 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, None)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
		gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
		self.sumhorFB = gl.glGenFramebuffers(1)
		gl.glBindFramebuffer(gl.GL_FRAMEBUFFER,self.sumhorFB)
		gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER,gl.GL_COLOR_ATTACHMENT0,gl.GL_TEXTURE_2D,self.sumhorTex,0)
		gl.glBindFramebuffer(gl.GL_FRAMEBUFFER,0)
		#VERTICAL SUMMING TEXTURE
		self.sumverTex = gl.glGenTextures(1)
		gl.glBindTexture(gl.GL_TEXTURE_2D, self.sumverTex)
		gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, input_image.width(), 1, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, None)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
		gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
		self.sumverFB = gl.glGenFramebuffers(1)
		gl.glBindFramebuffer(gl.GL_FRAMEBUFFER,self.sumverFB)
		gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER,gl.GL_COLOR_ATTACHMENT0,gl.GL_TEXTURE_2D,self.sumverTex,0)
		gl.glBindFramebuffer(gl.GL_FRAMEBUFFER,0)
		
		#get initial file modification times
		self.image_modified = time.ctime(os.path.getmtime('./using/image.png'))
		self.shader_modified = time.ctime(os.path.getmtime(fragmentshaderpath))
		
		#initialize periodic timer
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.timed_out)
		self.timer.start(500)
		
	def timed_out(self):
		if os.path.isfile('./using/image.png'):
			temp = time.ctime(os.path.getmtime('./using/image.png'))
			if not temp == self.image_modified:
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
				gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, input_image.width(), input_image.height(), 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, img_data)
				self.repaint()
			self.image_modified = temp
			
		if os.path.isfile(fragmentshaderpath):
			temp = time.ctime(os.path.getmtime(fragmentshaderpath))
			if not temp == self.shader_modified:
				f = open(fragmentshaderpath, "r")
				outputfragmentshader = f.read()
				f.close()
				vs = compile_vertex_shader(vertexshader)
				try:
					ofs = compile_fragment_shader(outputfragmentshader)
					self.ofs_error = False
				except RuntimeError as e:
					print("Compilation error on fragment shader:\n\t{0}".format(e))
					ofs = compile_fragment_shader(inputfragmentshader)
					self.ofs_error = True
				self.oshaders_program = link_shader_program(vs, ofs)
				self.repaint()
			self.shader_modified = temp

	def paintGL(self):
		"""Paint the scene."""
		#DRAW PROCESSED VERSION TO OUTPUT TEXTURE
		#use the program and write to output texture
		gl.glBindFramebuffer(gl.GL_FRAMEBUFFER,self.outFB)
		gl.glViewport(0,0,input_image.width(),input_image.height())
		gl.glUseProgram(self.oshaders_program)
		#set uniforms
		gl.glUniform2f(gl.glGetUniformLocation(self.oshaders_program, "offset"), -1, -1)
		gl.glUniform2f(gl.glGetUniformLocation(self.oshaders_program, "scale"), 2, 2)
		gl.glUniform1i(gl.glGetUniformLocation(self.oshaders_program, "tex"), 0)
		# bind the VBO 
		self.vbo.bind()
		# bind the texture
		if not self.ofs_error:
			gl.glBindTexture(gl.GL_TEXTURE_2D, self.inputTex)
		else:
			gl.glBindTexture(gl.GL_TEXTURE_2D, self.errorTex)
		#bind texture here!
		loc = gl.glGetAttribLocation(self.ishaders_program, "vertex");
		# these vertices contain 4 single precision coordinates
		gl.glVertexAttribPointer(loc, 4, gl.GL_FLOAT, gl.GL_FALSE, 16, None)
		# tell OpenGL that the VBO contains an array of vertices
		# prepare the shader        
		gl.glEnableVertexAttribArray(loc)        
		# draw "count" points from the VBO
		gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)
		
		#DRAW HORIZONTAL AND VERTICAL SUMMERS
		#use the program and write to output texture
		gl.glBindFramebuffer(gl.GL_FRAMEBUFFER,self.sumhorFB)
		gl.glViewport(0,0,1,input_image.height())
		gl.glUseProgram(self.sumhorshaders_program)
		#set uniforms
		gl.glUniform2f(gl.glGetUniformLocation(self.sumhorshaders_program, "offset"), -1, -1)
		gl.glUniform2f(gl.glGetUniformLocation(self.sumhorshaders_program, "scale"), 2, 2)
		gl.glUniform1f(gl.glGetUniformLocation(self.sumhorshaders_program, "hor_steps"), input_image.width())
		gl.glUniform1i(gl.glGetUniformLocation(self.sumhorshaders_program, "tex"), 0)
		# bind the VBO 
		self.vbo.bind()
		# bind the texture
		if not self.sumhor_error:
			gl.glBindTexture(gl.GL_TEXTURE_2D, self.outTex)
		else:
			gl.glBindTexture(gl.GL_TEXTURE_2D, self.errorTex)
		loc = gl.glGetAttribLocation(self.ishaders_program, "vertex");
		# these vertices contain 4 single precision coordinates
		gl.glVertexAttribPointer(loc, 4, gl.GL_FLOAT, gl.GL_FALSE, 16, None)
		# tell OpenGL that the VBO contains an array of vertices
		# prepare the shader        
		gl.glEnableVertexAttribArray(loc)        
		# draw "count" points from the VBO
		gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)
		
		#use the program and write to output texture
		gl.glBindFramebuffer(gl.GL_FRAMEBUFFER,self.sumverFB)
		gl.glViewport(0,0,input_image.width(),1)
		gl.glUseProgram(self.sumvershaders_program)
		#set uniforms
		gl.glUniform2f(gl.glGetUniformLocation(self.sumvershaders_program, "offset"), -1, -1)
		gl.glUniform2f(gl.glGetUniformLocation(self.sumvershaders_program, "scale"), 2, 2)
		gl.glUniform1f(gl.glGetUniformLocation(self.sumvershaders_program, "ver_steps"), input_image.height())
		gl.glUniform1i(gl.glGetUniformLocation(self.sumvershaders_program, "tex"), 0)
		# bind the VBO 
		self.vbo.bind()
		# bind the texture
		if not self.sumver_error:
			gl.glBindTexture(gl.GL_TEXTURE_2D, self.outTex)
		else:
			gl.glBindTexture(gl.GL_TEXTURE_2D, self.errorTex)
		loc = gl.glGetAttribLocation(self.ishaders_program, "vertex");
		# these vertices contain 4 single precision coordinates
		gl.glVertexAttribPointer(loc, 4, gl.GL_FLOAT, gl.GL_FALSE, 16, None)
		# tell OpenGL that the VBO contains an array of vertices
		# prepare the shader        
		gl.glEnableVertexAttribArray(loc)        
		# draw "count" points from the VBO
		gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)
		
		stage = 3
		
		#DRAW INPUT TO SCREEN
		# clear the buffer
		gl.glBindFramebuffer(gl.GL_FRAMEBUFFER,0)
		gl.glViewport(0, stage*int(self.height/NUM_STAGES), self.width, int(self.height/NUM_STAGES))
		gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		#use the program
		gl.glUseProgram(self.ishaders_program)
		#set uniforms
		gl.glUniform2f(gl.glGetUniformLocation(self.ishaders_program, "offset"), -1, -1)
		gl.glUniform2f(gl.glGetUniformLocation(self.ishaders_program, "scale"), 2, 2)
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
		
		stage = 2
		
		#DRAW OUTPUT TEXTURE TO SCREEN
		# clear the buffer
		gl.glBindFramebuffer(gl.GL_FRAMEBUFFER,0)
		gl.glViewport(0, stage*int(self.height/NUM_STAGES), self.width, int(self.height/NUM_STAGES))
		#gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		#gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		#use the program
		gl.glUseProgram(self.ishaders_program)
		#set uniforms
		gl.glUniform2f(gl.glGetUniformLocation(self.ishaders_program, "offset"), -1, -1)
		gl.glUniform2f(gl.glGetUniformLocation(self.ishaders_program, "scale"), 2, 2)
		gl.glUniform1i(gl.glGetUniformLocation(self.ishaders_program, "tex"), 0)
		# bind the VBO 
		self.vbo.bind()
		# bind the texture
		gl.glBindTexture(gl.GL_TEXTURE_2D, self.outTex)
		#bind texture here!
		loc = gl.glGetAttribLocation(self.ishaders_program, "vertex");
		# these vertices contain 4 single precision coordinates
		gl.glVertexAttribPointer(loc, 4, gl.GL_FLOAT, gl.GL_FALSE, 16, None)
		# tell OpenGL that the VBO contains an array of vertices
		# prepare the shader        
		gl.glEnableVertexAttribArray(loc)        
		# draw "count" points from the VBO
		gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)
		
		stage = 1
		
		#DRAW SUMMERS TO SCREEN
		# clear the buffer
		gl.glBindFramebuffer(gl.GL_FRAMEBUFFER,0)
		gl.glViewport(0, stage*int(self.height/NUM_STAGES), self.width, int(self.height/NUM_STAGES))
		#gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		#gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		#use the program
		gl.glUseProgram(self.ishaders_program)
		#set uniforms
		gl.glUniform2f(gl.glGetUniformLocation(self.ishaders_program, "offset"), -1, -1)
		gl.glUniform2f(gl.glGetUniformLocation(self.ishaders_program, "scale"), 2, 2)
		gl.glUniform1i(gl.glGetUniformLocation(self.ishaders_program, "tex"), 0)
		# bind the VBO 
		self.vbo.bind()
		# bind the texture
		gl.glBindTexture(gl.GL_TEXTURE_2D, self.sumhorTex)
		#bind texture here!
		loc = gl.glGetAttribLocation(self.ishaders_program, "vertex");
		# these vertices contain 4 single precision coordinates
		gl.glVertexAttribPointer(loc, 4, gl.GL_FLOAT, gl.GL_FALSE, 16, None)
		# tell OpenGL that the VBO contains an array of vertices
		# prepare the shader        
		gl.glEnableVertexAttribArray(loc)        
		# draw "count" points from the VBO
		gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)
		
		stage = 0
		
		# clear the buffer
		gl.glBindFramebuffer(gl.GL_FRAMEBUFFER,0)
		gl.glViewport(0, stage*int(self.height/NUM_STAGES), self.width, int(self.height/NUM_STAGES))
		#gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		#gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		#use the program
		gl.glUseProgram(self.ishaders_program)
		#set uniforms
		gl.glUniform2f(gl.glGetUniformLocation(self.ishaders_program, "offset"), -1, -1)
		gl.glUniform2f(gl.glGetUniformLocation(self.ishaders_program, "scale"), 2, 2)
		gl.glUniform1i(gl.glGetUniformLocation(self.ishaders_program, "tex"), 0)
		# bind the VBO 
		self.vbo.bind()
		# bind the texture
		gl.glBindTexture(gl.GL_TEXTURE_2D, self.sumverTex)
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
		self.width = width
		self.height = height

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
f = open('./resources/inputcopy.glsl', "r")
inputfragmentshader = f.read()
f.close()
f = open("./using/summer_ver.glsl")
summerverticalshader = f.read()
f.close()
f = open("./using/summer_hor.glsl")
summerhorizontalshader = f.read()
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
height = width/input_image.width()*NUM_STAGES*input_image.height()
img_data = np.empty(input_image.width()*input_image.height()*4, dtype=np.ubyte)
for i in range (0,input_image.height()):
	for j in range (0,input_image.width()):
		pixel = input_image.pixel(j,i)
		img_data[((input_image.height()-i-1)*input_image.width()+j)*4+0] = QtGui.qRed(pixel)
		img_data[((input_image.height()-i-1)*input_image.width()+j)*4+1] = QtGui.qGreen(pixel)
		img_data[((input_image.height()-i-1)*input_image.width()+j)*4+2] = QtGui.qBlue(pixel)
		img_data[((input_image.height()-i-1)*input_image.width()+j)*4+3] = 255
		
error_image = QtGui.QImage('./resources/error.png')
error_image = error_image.convertToFormat(QtGui.QImage.Format_ARGB32)
width = DEFAULT_WIDTH
height = width/error_image.width()*2*error_image.height()
errimg_data = np.empty(error_image.width()*error_image.height()*4, dtype=np.ubyte)
for i in range (0,error_image.height()):
	for j in range (0,error_image.width()):
		pixel = error_image.pixel(j,i)
		errimg_data[((error_image.height()-i-1)*error_image.width()+j)*4+0] = QtGui.qRed(pixel)
		errimg_data[((error_image.height()-i-1)*error_image.width()+j)*4+1] = QtGui.qGreen(pixel)
		errimg_data[((error_image.height()-i-1)*error_image.width()+j)*4+2] = QtGui.qBlue(pixel)
		errimg_data[((error_image.height()-i-1)*error_image.width()+j)*4+3] = 255

# show the window
win = create_window(TestWindow)

