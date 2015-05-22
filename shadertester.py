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
instructionimagepath='./resources/instruct.png'

##################################################
##SETTINGS
##################################################
thresholdshaderpath='./using/thresholdshader.glsl'
horizontalsummer1path='./using/summer_hor.glsl'
horizontalsummer2path='./using/summer_hor.glsl'
verticalsummer1path='./using/summer_ver.glsl'
verticalsummer2path='./using/summer_ver.glsl'
inputimagepath='./using/image.png'
coordinateshaderpath='./using/coordinate.glsl'
erodeshaderpath='./using/erodefragshader_ours.glsl'
dilateshaderpath='./using/dilatefragshader_ours.glsl'

#window width
DEFAULT_WIDTH = 10
MAX_COORDINATES = 100
#drawing positions
THRESHOLD_POS = (0,0)
THRESHOLD_SIZE = (1000,200)
SUMHOR1_POS = (1000,0)
SUMHOR1_SIZE = (200,200)
SUMHOR2_POS = (1205,0)
SUMHOR2_SIZE = (15,200)
SUMVER1_POS = (0,200)
SUMVER1_SIZE = (1000,100)
SUMVER2_POS = (0,405)
SUMVER2_SIZE = (1000,15)
INPUT_POS = (0,430)
INPUT_SIZE = (1000,200)
INSTRUCTION_POS = (0,650)
INSTRUCTION_SIZE = (1000,300)

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
		# erode shader program (to do morphological erode operation on the image)
		self.erode_program = GShaderProgram()
		self.erode_program.load(vertexshaderpath,erodeshaderpath,defaultfragmentpath)
		# dilate shader program (to do morphological dilate operation on the image)
		self.dilate_program = GShaderProgram()
		self.dilate_program.load(vertexshaderpath,dilateshaderpath,defaultfragmentpath)
		#horizontal summer shader program (to make sums of rows), stage 1
		self.sumhor_program1 = GShaderProgram()
		self.sumhor_program1.load(vertexshaderpath,horizontalsummer1path,defaultfragmentpath)
		#horizontal summer shader program (to make sums of rows), stage 2
		self.sumhor_program2 = GShaderProgram()
		self.sumhor_program2.load(vertexshaderpath,horizontalsummer2path,defaultfragmentpath)
		#vertical summer shader program (to make sums of columns), stage 1
		self.sumver_program1 = GShaderProgram()
		self.sumver_program1.load(vertexshaderpath,verticalsummer1path,defaultfragmentpath)
		#vertical summer shader program (to make sums of columns), stage 2
		self.sumver_program2 = GShaderProgram()
		self.sumver_program2.load(vertexshaderpath,verticalsummer2path,defaultfragmentpath)
		
		#make textures+framebuffers
		
		#INPUT TEXTURE (RGBA IMAGE)
		input_image.toTexture()
		#ERROR TEXTURE (FOR SHOWING IF SOMETHING WENT WRONG)
		error_image.toTexture()
		#INSTRUCTION TEXTURE
		instruction_image.toTexture()
		#THRESHOLDED TEXTURE
		self.threshold_image = GImageTex()
		self.threshold_image.make(input_image.width, input_image.height)
		self.threshold_image.toTexture()
		# ERODED TEXTURE
		self.erode_image = GImageTex()
		self.erode_image.make(input_image.width, input_image.height)
		self.erode_image.toTexture()
		# DILATED TEXTURE
		self.dilate_image = GImageTex()
		self.dilate_image.make(input_image.width, input_image.height)
		self.dilate_image.toTexture()
		#HORIZONTAL SUMMING TEXTURE, STAGE 1
		self.sumhor_image1 = GImageTex()
		self.sumhor_image1.make(int(input_image.width/64)+1, input_image.height)
		self.sumhor_image1.toTexture()
		#HORIZONTAL SUMMING TEXTURE, STAGE 2
		self.sumhor_image2 = GImageTex()
		self.sumhor_image2.make(1, input_image.height)
		self.sumhor_image2.toTexture()
		#VERTICAL SUMMING TEXTURE, STAGE 1
		self.sumver_image1 = GImageTex()
		self.sumver_image1.make(input_image.width, int(input_image.height/64)+1)
		self.sumver_image1.toTexture()
		#VERTICAL SUMMING TEXTURE, STAGE 2
		self.sumver_image2 = GImageTex()
		self.sumver_image2.make(input_image.width, 1)
		self.sumver_image2.toTexture()
		
		#get initial file modification times
		self.shader_modified = time.ctime(os.path.getmtime(thresholdshaderpath))
		
		#initialize periodic timer that checks for file updates
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.timed_out)
		self.timer.start(500)
		
	def timed_out(self): #check if any image or shader was changed
		input_image.updateIfModified()
		error_image.updateIfModified()
		instruction_image.updateIfModified()
		self.threshold_program.updateIfModified()
		self.erode_program.updateIfModified()
		self.dilate_program.updateIfModified()
		self.sumhor_program1.updateIfModified()
		self.sumhor_program2.updateIfModified()
		self.sumver_program1.updateIfModified()
		self.sumver_program2.updateIfModified()
		
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
		#DRAW ERODED IMAGE TO TEXTURE
		self.doShader(self.erode_program, [threshold_image],
            #uniform1f = [("stepsize_x",1/input_image.width),("stepsize_y",1/input_image.height)],
			uniform2f = [("offset",-1,-1),("scale",2,2),("texelsize",1/input_image.width,1/input_image.height)],
			uniform1i = [("tex",0)],
			render_target = self.erode_image
		)
		#DRAW DILATED IMAGE TO TEXTURE
		# self.doShader(self.dilate_program, [erode_image],
			# uniform2f = [("offset",-1,-1),("scale",2,2),("texelsize",1/input_image.width,1/input_image.height)],
			# uniform1i = [("tex",0)],
			# render_target = self.dilate_image
		# )
		#DRAW SUMMATION TEXTURES (NOTE: SET THE PIXELS OUTSIDE THE EDGES TO BLACK!!!)
		#self.doShader(self.sumhor_program1, [self.dilate_image],
		self.doShader(self.sumhor_program1, [self.erode_image],
			uniform2f = [("offset",-1,-1),("scale",2,2)],
			uniform1i = [("tex",0)],
			uniform1f = [("step",1/input_image.width)],
			render_target = self.sumhor_image1
		)
		self.doShader(self.sumhor_program2, [self.sumhor_image1],
			uniform2f = [("offset",-1,-1),("scale",2,2)],
			uniform1i = [("tex",0)],
			uniform1f = [("step",1/64)],
			render_target = self.sumhor_image2
		)
		self.doShader(self.sumver_program1, [self.threshold_image],
			uniform2f = [("offset",-1,-1),("scale",2,2)],
			uniform1i = [("tex",0)],
			uniform1f = [("step",1/input_image.height)],
			render_target = self.sumver_image1
		)
		self.doShader(self.sumver_program2, [self.sumver_image1],
			uniform2f = [("offset",-1,-1),("scale",2,2)],
			uniform1i = [("tex",0)],
			uniform1f = [("step",1/64)],
			render_target = self.sumver_image2
		)
		
		#DRAW THRESHOLDED TEXTURE ON SCREEN
		self.doShader(self.input_program, [self.threshold_image],
			uniform2f = [("offset",-1,-1),("scale",2,2)],
			uniform1i = [("tex",0)],
			position = THRESHOLD_POS, #position from bottom left in drawing window
			size = THRESHOLD_SIZE #(width,height in drawing window)
		)
		#DRAW ERODED TEXTURE ON SCREEN
		self.doShader(self.input_program, [self.erode_image],
			uniform2f = [("offset",-1,-1),("scale",2,2),("texelsize",1/input_image.width,1/input_image.height)],
			uniform1i = [("tex",0)],
			position = INPUT_POS, #position from bottom left in drawing window
			size = THRESHOLD_SIZE #(width,height in drawing window)
		)
		#DRAW DILATED TEXTURE ON SCREEN
		# self.doShader(self.input_program, [self.dilate_image],
			# uniform2f = [("offset",-1,-1),("scale",2,2),("texelsize",1/input_image.width,1/input_image.height)],
			# uniform1i = [("tex",0)],
			# position = INPUT_POS, #position from bottom left in drawing window
			# size = THRESHOLD_SIZE #(width,height in drawing window)
		# )
		#DRAW SUMMATION TEXTURES ON SCREEN
		self.doShader(self.input_program, [self.sumhor_image1],
			uniform2f = [("offset",-1,-1),("scale",2,2)],
			uniform1i = [("tex",0)],
			position = SUMHOR1_POS, #position from bottom left in drawing window
			size = SUMHOR1_SIZE #(width,height in drawing window)
		)
		self.doShader(self.input_program, [self.sumhor_image2],
			uniform2f = [("offset",-1,-1),("scale",2,2)],
			uniform1i = [("tex",0)],
			position = SUMHOR2_POS, #position from bottom left in drawing window
			size = SUMHOR2_SIZE #(width,height in drawing window)
		)
		self.doShader(self.input_program, [self.sumver_image1],
			uniform2f = [("offset",-1,-1),("scale",2,2)],
			uniform1i = [("tex",0)],
			position = SUMVER1_POS, #position from bottom left in drawing window
			size = SUMVER1_SIZE #(width,height in drawing window)
		)
		self.doShader(self.input_program, [self.sumver_image2],
			uniform2f = [("offset",-1,-1),("scale",2,2)],
			uniform1i = [("tex",0)],
			position = SUMVER2_POS, #position from bottom left in drawing window
			size = SUMVER2_SIZE #(width,height in drawing window)
		)
		#DRAW INPUT IMAGE ON SCREEN
		self.doShader(self.input_program, [input_image],
			uniform2f = [("offset",-1,-1),("scale",2,2)],
			uniform1i = [("tex",0)],
			position = INPUT_POS, #position from bottom left in drawing window
			size = INPUT_SIZE #(width,height in drawing window)
		)
		#DRAW INSTRUCTIONS IMAGE ON SCREEN
		self.doShader(self.input_program, [instruction_image],
			uniform2f = [("offset",-1,-1),("scale",2,2)],
			uniform1i = [("tex",0)],
			position = INSTRUCTION_POS, #position from bottom left in drawing window
			size = INSTRUCTION_SIZE #(width,height in drawing window)
		)
		
		
		##store and print and show coordinates found
		#objects = []
		#factx = input_image.width/255
		#facty = input_image.height/255		
		#for x in range(0,MAX_COORDINATES):
		#	if not buf[x*4+2]:
		#		break #no more objects
		#	objects.append((int(buf[x*4]*factx),int(buf[x*4+1]*facty),int(buf[x*4+2]*factx),int(buf[x*4+3]*facty)))
		#print("\n\nObjects found:\n")
		#for x in objects:
		#	print('\t{0},{1},{2},{3}'.format(x[0], x[1], x[2], x[3]))
        #
		##do opengl stuff
		#gl.glDisable(gl.GL_TEXTURE_2D)
		#gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
		#gl.glViewport(INPUT_POS[0],INPUT_POS[1],INPUT_SIZE[0],INPUT_SIZE[1])
		#for x in objects:
		#	#draw lines			
		#	gl.glColor(1,1,1)
		#	gl.glBegin(gl.GL_LINE_STRIP)
		#	gl.glVertex2f(x[0]/input_image.width, x[1]/input_image.height)
		#	gl.glVertex2f((x[0]+x[2])/input_image.width, x[1]/input_image.height)
		#	gl.glVertex2f((x[0]+x[2])/input_image.width, (x[1]+x[3])/input_image.height)
		#	gl.glVertex2f(x[0]/input_image.width, (x[1]+x[3])/input_image.height)
		#	gl.glVertex2f(x[0]/input_image.width, x[1]/input_image.height)
		#	gl.glEnd()
		#gl.glEnable(gl.GL_TEXTURE_2D)			
		
		gl.glFinish()

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
instruction_image = GImageTex()
instruction_image.load(instructionimagepath)

#set window width and height
width = DEFAULT_WIDTH
height = width/input_image.width*2*input_image.height	

# show the window
win = create_window(TestWindow)

