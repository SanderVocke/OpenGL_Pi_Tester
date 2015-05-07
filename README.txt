install Python (I used 3.4).

you need to use PIP (python package installer) to install PyOpenGL. With python 3.4 it's included, for lower versions google how to install it.

then go to: http://www.lfd.uci.edu/~gohlke/pythonlibs/ and download the win32 packages for:
numpy, PyQt4, PyOpenGL and PyOpenGL_accelerate.
go to where you downloaded them, open a command window and then install them:
python -m pip install wheel          <--- this is needed first
python -m pip install filename.whl   <--- do this for both .whl packages.

Good to go!