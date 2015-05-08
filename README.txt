READ THIS FIRST!

INSTALLATION:

install Python (I used 3.4). If you have multiple Pythons installed, make sure Python 3.4 is the one that is in the PATH variable (the one being started when you type "python" in CMD).

you need to use PIP (python package installer) to install PyOpenGL. With python 3.4 it's included, for lower versions google how to install it.

then go to: http://www.lfd.uci.edu/~gohlke/pythonlibs/ and download the win32 packages for:
numpy, PyQt4, PyOpenGL and PyOpenGL_accelerate. (take the win32 versions with the "34" numbering which refers to Python3.4)
go to where you downloaded them, open a command window and then install them:
python -m pip install wheel          <--- this is needed first
python -m pip install filename.whl   <--- do this for both .whl packages.

Good to go!


USAGE:

When you start the program (best to do from the command-line using "python shadertester.py", so you can see any errors being logged), it will open an OpenGL window. The top half of the window will show the input image (located in "using/image.png") and the bottom half will show the same image when passed through the shader in "using/fragmentshader.glsl". This is meant to be the same shader that is doing the final (image detection) step on the Pi. It should be possible to directly copy-paste the shader back and forth.

You don't have to restart the program while developing. If at any point you change the input image ("using/image.png"), or the shader ("using/fragmentshader.glsl"), the program should detect it and update immediately.

You can also resize the window to any shape you want.

If an error occurs while compiling your shader, the bottom half of the window will notify you of this. To see the exact error, look on your command line - it should be logged there.

Happy coding!
