A short explanation of the current rendering pipeline and program structure.

Initialization
1. Input image is converted to a OpenGL Texture.


Rendering loop (paintGL() is automatically called whenever redrawn)
1. './using/thresholdshader.glsl' GLSL shader is applied to the input image texture, the result stored in the thresholded texture (black and white seen on screen).
	this shader's responsibility is to do the thresholding (as well as any preceding steps needed such as erosion, blur, although those are not currently implemented!)
	Note that right now, it only does a red threshold. To do red and blue, we could store the results in different color components of the result (red threshold results only 
	in the R component, blue only in B). That way it is not needed to work with two separate textures. Up to you!
	
2. './using/summer_hor.glsl' and './using/summer_ver.glsl' shaders are applied to the thresholded texture. They each store their result in a different output texture. 
	The summer_hor shader sums row values, the summer_ver sums column values. summer_hor stores its result in a texture which is the same height as the input, but only
	1 pixel wide. summer_ver in a texture that is the same width as input, but only 1 pixel high.
	Each pixel of the outputs contains the sum value in the R component, and the blue component is completely ON if the sum is nonzero (just nice for viewing the result onscreen!)
	you can see the result textures around the threshold texture on screen: the blue thingies. (red is also there, but hard to see).
	
3. './using/coordinate.glsl' shader is applied to the horizontal and vertical texture simultaneously.  It is supposed to take the sums, and from that derive object coordinates and sizes.
	It is crappily written at the moment! It "renders" onto an output texture of 1x100 pixels. the idea is that each "pixel" contains a centroid's information.
	R component represents X position, G component represents Y position, B component represents X size, A component represents Y size.
	The code for this shader looks very complex, but the idea is this: because it is a shader, it is executed for each output pixel (so each "found object" index of the result). That means
	the first pixel should find the first object, the second pixel the second, etc.
	Therefore, the shader first determines which output pixel it is. Then it iterates over the found objects until it reaches its own index.
	Note that right now, this all only works for finding red objects!
	
4. The host code retreives the resulting "coordinate texture" which contains object information. It is printed to the console, and also shown in the window as black bounding boxes.