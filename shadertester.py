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
from shaderutils import *
vertexshaderpath='./resources/vertexshader.glsl'
defaultfragmentpath='./resources/inputcopy.glsl'
errorimagepath='./resources/error.png'

##################################################
##SETTINGS
##################################################
thresholdshaderpath='./using/thresholdshader.glsl'
horizontalsummerpath='./using/summer_hor.glsl'
verticalsummerpath='./using/summer_ver.glsl'
inputimagepath='./using/image.png'
#window width
DEFAULT_WIDTH = 10
NUM_STAGES = 4

#the plot widget
class GLWidget(QGLWidget):
	def initializeGL(self):
		"""Initialize OpenGL, VBOs, upload data on the GPU, etc."""
		self.width = width
		self.height = height
		# background color
		gl.glClearColor(0, 0, 0, 0)
		# create a Vertex Buffer Object with the specified data
		self.vbo = glvbo.VBO(self.data)
		
		#input shader program (to show without changes)
		self.input_program = GShaderProgram()
		self.input_program.load(vertexshaderpath,defaultfragmentpath,defaultfragmentpath)
		#threshold shader program (to create filtered, thresholded image)
		self.threshold_program = GShaderProgram()
		self.threshold_program.load(vertexshaderpath,thresholdshaderpath,defaultfragmentpath)
		#horizontal summer shader program (to make sums of rows)
		self.sumhor_program = GShaderProgram()
		self.sumhor_program.load(vertexshaderpath,horizontalsummerpath,defaultfragmentpath)
		#vertical summer shader program (to make sums of columns)
		self.sumver_program = GShaderProgram()
		self.sumver_program.load(vertexshaderpath,verticalsummerpath,defaultfragmentpath)

		
		#make textures+framebuffers
		
		#INPUT TEXTURE (RGBA IMAGE)
		input_image.toTexture()
		#ERROR TEXTURE (FOR SHOWING IF SOMETHING WENT WRONG)
		error_image.toTexture()
		#THRESHOLDED TEXTURE
		self.threshold_image = GImageTex()
		self.threshold_image.make(input_image.width, input_image.height)
		self.threshold_image.toTexture()
		#HORIZONTAL SUMMING TEXTURE
		self.sumhor_image = GImageTex()
		self.sumhor_image.make(1, input_image.height)
		self.sumhor_image.toTexture()
		#VERTICAL SUMMING TEXTURE
		self.sumver_image = GImageTex()
		self.sumver_image.make(input_image.width, 1)
		self.sumver_image.toTexture()
		
		#get initial file modification times
		self.shader_modified = time.ctime(os.path.getmtime(thresholdshaderpath))
		
		#initialize periodic timer
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.timed_out)
		self.timer.start(500)
		
	def timed_out(self):
		input_image.updateIfModified()
		error_image.updateIfModified()
		self.threshold_program.updateIfModified()
		self.sumhor_program.updateIfModified()
		self.sumver_program.updateIfModified()
		
	def doShader(self, program, sources, uniform2f=[], uniform1f=[], uniform2i=[], uniform1i=[], render_target=None, position=(0,0), size=(100,100)):
		if render_target == None:
			#resize the screen if necessary
			if position[0] + size[0] > self.width:
				self.resizefunc(50,50,position[0]+size[0],self.height+1)
			if position[1] + size[1] > self.height:
				self.resizefunc(50,50,self.width,position[1]+size[1]+1)
			#do opengl stuff
			gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
			gl.glViewport(position[0],position[1],size[0],size[1])
		else:
			gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, render_target.fb)
			gl.glViewport(0,0,render_target.width,render_target.height)
		#tell OpenGL which shader program to use for this render
		gl.glUseProgram(program.program)
		#set any uniform variables we got as arguments
		for x in uniform1i: #tuple ("name", value)
			gl.glUniform1i(gl.glGetUniformLocation(program.program, x[0]),x[1])
		for x in uniform2i: #tuple ("name", value1, value2)
			gl.glUniform2i(gl.glGetUniformLocation(program.program, x[0]),x[1],x[2])
		for x in uniform1f: #tuple ("name", value)
			gl.glUniform1f(gl.glGetUniformLocation(program.program, x[0]),x[1])
		for x in uniform2f: #tuple ("name", value1, value2)
			gl.glUniform2f(gl.glGetUniformLocation(program.program, x[0]),x[1],x[2])
		#bind vertex buffer
		self.vbo.bind()
		#bind textures
		for x in sources:
			if not program.ferror:
				gl.glBindTexture(gl.GL_TEXTURE_2D, x.tex)
			else:
				gl.glBindTexture(gl.GL_TEXTURE_2D, error_image.tex)
		#do the actual drawing
		loc = gl.glGetAttribLocation(self.input_program.program, "vertex");
		gl.glVertexAttribPointer(loc, 4, gl.GL_FLOAT, gl.GL_FALSE, 16, None)
		gl.glEnableVertexAttribArray(loc)
		gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)		

	def paintGL(self):
		"""Paint the scene."""
		#DRAW THRESHOLDED IMAGE TO TEXTURE
		self.doShader(self.threshold_program, [input_image],
			uniform2f = [("offset",-1,-1),("scale",2,2)],
			uniform1i = [("tex",0)],
			render_target = self.threshold_image
		)
		#DRAW SUMMATION TEXTURES
		self.doShader(self.sumhor_program, [self.threshold_image],
			uniform2f = [("offset",-1,-1),("scale",2,2)],
			uniform1i = [("tex",0)],
			uniform1f = [("hor_steps",input_image.width)],
			render_target = self.sumhor_image
		)
		self.doShader(self.sumver_program, [self.threshold_image],
			uniform2f = [("offset",-1,-1),("scale",2,2)],
			uniform1i = [("tex",0)],
			uniform1f = [("ver_steps",input_image.height)],
			render_target = self.sumver_image
		)
		
		#DRAW THRESHOLDED TEXTURE ON SCREEN
		self.doShader(self.input_program, [self.threshold_image],
			uniform2f = [("offset",-1,-1),("scale",2,2)],
			uniform1i = [("tex",0)],
			position = (0,0), #position from bottom left in drawing window
			size = (1000,200) #(width,height in drawing window)
		)
		#DRAW SUMMATION TEXTURES ON SCREEN
		self.doShader(self.input_program, [self.sumhor_image],
			uniform2f = [("offset",-1,-1),("scale",2,2)],
			uniform1i = [("tex",0)],
			position = (1000,0), #position from bottom left in drawing window
			size = (20,200) #(width,height in drawing window)
		)
		self.doShader(self.input_program, [self.sumver_image],
			uniform2f = [("offset",-1,-1),("scale",2,2)],
			uniform1i = [("tex",0)],
			position = (0,200), #position from bottom left in drawing window
			size = (1000,20) #(width,height in drawing window)
		)
		#DRAW INPUT IMAGE ON SCREEN
		self.doShader(self.input_program, [input_image],
			uniform2f = [("offset",-1,-1),("scale",2,2)],
			uniform1i = [("tex",0)],
			position = (0,300), #position from bottom left in drawing window
			size = (1000,200) #(width,height in drawing window)
		)

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
		self.widget.resizefunc = self.setGeometry
		# put the window at the screen position (100, 100)
		self.setGeometry(50, 50, width, height)
		self.setCentralWidget(self.widget)
		self.show()

#load the shaders
f = open(vertexshaderpath, "r")
vertexshader = f.read()
f.close()
f = open(thresholdshaderpath, "r")
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

input_image = GImageTex() #use the GImageTex class in shaderutils
input_image.load(inputimagepath)			
error_image = GImageTex()	
error_image.load(errorimagepath)

#set window width and height
width = DEFAULT_WIDTH
height = width/input_image.width*2*input_image.height	

# show the window
win = create_window(TestWindow)

