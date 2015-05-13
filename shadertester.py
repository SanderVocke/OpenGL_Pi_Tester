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
coordinateshaderpath='./using/coordinate.glsl'
#window width
DEFAULT_WIDTH = 10
MAX_COORDINATES = 100

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
		#coordinate finder shader
		self.coordinate_program = GShaderProgram()
		self.coordinate_program.load(vertexshaderpath,coordinateshaderpath,defaultfragmentpath)

		
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
		#COORDINATE HOLDING TEXTURE
		self.coordinate_image = GImageTex()
		self.coordinate_image.make(MAX_COORDINATES, 1)
		self.coordinate_image.toTexture()
		
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
		self.coordinate_program.updateIfModified()
		
	def doShader(self, program, sources, uniform2f=[], uniform1f=[], uniform2i=[], uniform1i=[], render_target=None, position=(0,0), size=(100,100), readback=False):
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
		texunits = [gl.GL_TEXTURE0, gl.GL_TEXTURE1, gl.GL_TEXTURE2, gl.GL_TEXTURE3]
		for (i,x) in enumerate(sources):
			gl.glActiveTexture(texunits[i])
			if not program.ferror:
				gl.glBindTexture(gl.GL_TEXTURE_2D, x.tex)
			else:
				gl.glBindTexture(gl.GL_TEXTURE_2D, error_image.tex)
		gl.glActiveTexture(texunits[0])
		#do the actual drawing
		loc = gl.glGetAttribLocation(self.input_program.program, "vertex")
		gl.glVertexAttribPointer(loc, 4, gl.GL_FLOAT, gl.GL_FALSE, 16, None)
		gl.glEnableVertexAttribArray(loc)
		gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)		
		#readback
		if readback:
			if render_target == None:
				# Capture image from the OpenGL buffer
				buffer = ( gl.GLubyte * (4*size[0]*size[1]) )(0)
				gl.glReadPixels(0, 0, size[0], size[1], gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, buffer)
				return buffer
			else:
				# Capture image from the OpenGL buffer
				buffer = ( gl.GLubyte * (4*render_target.width*render_target.height) )(0)
				gl.glReadPixels(0, 0, render_target.width, render_target.height, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, buffer)
				return buffer
		return

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
		#"DRAW" COORDINATE TEXTURE
		buf = self.doShader(self.coordinate_program, [self.sumhor_image, self.sumver_image],
			uniform2f = [("offset",-1,-1),("scale",2,2)],
			uniform1i = [("hor_sum_tex",0),("ver_sum_tex",1)],
			uniform1f = [("num_coords",MAX_COORDINATES),("hor_sum_height",self.sumhor_image.height),("ver_sum_width",self.sumver_image.width)],
			render_target = self.coordinate_image,
			readback = True
		)
		
		#store and print coordinates found
		objects = []
		factx = input_image.width/255
		facty = input_image.height/255		
		for x in range(0,MAX_COORDINATES):
			if not buf[x*4+2]:
				break #no more objects
			objects.append((int(buf[x*4]*factx),int(buf[x*4+1]*facty),int(buf[x*4+2]*factx),int(buf[x*4+3]*facty)))
		print("\n\nObjects found:\n")
		for x in objects:
			print('\t{0},{1},{2},{3}'.format(x[0], x[1], x[2], x[3]))
		
		
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
		#DRAW COORDINATE TEXTURE ON SCREEN
		self.doShader(self.input_program, [self.coordinate_image],
			uniform2f = [("offset",-1,-1),("scale",2,2)],
			uniform1i = [("tex",0)],
			position = (0,510), #position from bottom left in drawing window
			size = (1000,20) #(width,height in drawing window)
		)
		
		#GET THE RESULT

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

