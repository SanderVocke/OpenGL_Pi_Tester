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
from shadertester2 import *

class GShaderProgram:
	def __init__(self):
		self.ferror = True
		pass
		
	def load(self, vpath, fpath, defaultfpath):
		self.fpath = fpath
		self.defaultfpath = defaultfpath
		self.vpath = vpath
		f = open(vpath, "r")
		self.vshader_text = f.read()
		f.close()
		f = open(fpath, "r")
		self.fshader_text = f.read()
		f.close()
		f = open(defaultfpath, "r")
		self.defaultfshader_text = f.read()
		f.close()
		try:
			self.vshader = compile_vertex_shader(self.vshader_text)
		except RuntimeError as e:
			print("Vertex shader compile failed:\n\t{0}".format(e))
			exit()
		try:
			self.fshader = compile_fragment_shader(self.fshader_text)
			self.ferror = False
		except RuntimeError as e:
			print("Fragment shader compile failed:\n\t{0}".format(e))
			self.ferror = True
			self.fshader = compile_fragment_shader(self.defaultfshader_text)
		self.program = link_shader_program(self.vshader, self.fshader)
		self.modtimef = time.ctime(os.path.getmtime(self.fpath))
		self.modtimev = time.ctime(os.path.getmtime(self.fpath))
		
	def updateIfModified(self):
		ntimef = time.ctime(os.path.getmtime(self.fpath))
		ntimev = time.ctime(os.path.getmtime(self.vpath))
		if (not ntimef == self.modtimef) or (not ntimev == self.modtimev):
			self.modtimef = ntimef #update the time for next time	
			self.modtimev = ntimev #update the time for next time			
			#gl.glDeleteProgram(self.program) #delete the old program
			self.load(self.vpath,self.fpath,self.defaultfpath) #reload the image
		

class GImageTex:
	def __init__(self):
		pass
		
	def load(self, path):
		#load the image
		self.path = path
		self.img = QtGui.QImage(path)
		self.img = self.img.convertToFormat(QtGui.QImage.Format_ARGB32)
		self.width = self.img.width()
		self.height = self.img.height()
		#get the image data into an RGBA byte buffer
		self.data = np.empty(self.width*self.height*4, dtype=np.ubyte)
		for i in range (0,self.height):
			for j in range (0,self.width):
				pixel = self.img.pixel(j,i)
				self.data[((self.height-i-1)*self.width+j)*4+0] = QtGui.qRed(pixel)
				self.data[((self.height-i-1)*self.width+j)*4+1] = QtGui.qGreen(pixel)
				self.data[((self.height-i-1)*self.width+j)*4+2] = QtGui.qBlue(pixel)
				self.data[((self.height-i-1)*self.width+j)*4+3] = 255
		#store the modified time of the source file, so we can check later whether it changed
		self.modtime = time.ctime(os.path.getmtime(self.path))
		self.empty = False
		
	def make(self, width, height):
		self.width = width
		self.height = height
		self.empty = True
				
	def toTexture(self, width=None, height=None):
		if width is None:
			width = self.width
		if height is None:
			height = self.height
		self.tex = gl.glGenTextures(1)
		gl.glBindTexture(gl.GL_TEXTURE_2D, self.tex)
		if self.empty: #create empty texture
			gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width, height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, None)
		else: #use data buffer
			gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width, height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, self.data)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
		gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
		#generate a frame-buffer as well
		self.fb = gl.glGenFramebuffers(1)
		gl.glBindFramebuffer(gl.GL_FRAMEBUFFER,self.fb)
		gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER,gl.GL_COLOR_ATTACHMENT0,gl.GL_TEXTURE_2D,self.tex,0)
		gl.glBindFramebuffer(gl.GL_FRAMEBUFFER,0)
		
	def updateIfModified(self):
		ntime = time.ctime(os.path.getmtime(self.path))
		if not ntime == self.modtime:
			self.modtime = ntime #update the time for next time
			self.load(self.path) #reload the image
			#gl.glDeleteTextures(self.tex) #delete the old texture
			self.toTexture() #make a new texture
			