/*
COORDINATE SHADER
This is the last shader in the pipeline.
It takes two input textures: hor_sum_tex ( 1xIMAGEHEIGHT pixels ) and ver_sum_tex (IMAGEWIDTHx1 pixels).
It assumes that in these textures, the sums of all rows (hor_sum_tex) and columns (ver_sum_tex) of the THRESHOLDED image have been stored.
More specifically: in the RED component of each pixel of these "summed textures".

WHAT SHOULD IT DO:
put coordinates of objects into the output texture. The output texture of this shader will be a certain width (100), and 1 pixel high. Each
pixel will store information about 1 object.

HOW DOES IT WORK NOW:
remember that it is a shader: assuming the output texture is 100 pixels wide, this shader will be called in parallel for each of these 100 pixels!
The current operation is this: there is a function nextObject() which finds the next possible object based on the summation textures. This way we
can "iterate through" all objects by calling it repeatedly.
The shader main function first finds out which pixel it is. For example, if we are the 5th output pixel, we should store information about the
5th found object. Therefore we call nextObject() 5 times and then return the information (by setting gl_FragColor). If at any point we reach the
end of the found objects we just return 0 for everything.
The information is stored as a RGBA vec4: (x_position, y_position, x_size, y_size) of the found object.

WHAT NEEDS TO BE DONE:
As said above, we assume that sums of thresholded image are stored in RED value of the sum textures. In the future we want to have separate summation values
for the "red-thresholded" and the "blue-thresholded" image. For example, we may want in the future to store the summation results for the blue-threshold in the
BLUE component of the thresholded image.
Then this shader should be able to deal with that accordingly, and somehow return information for RED and BLUE objects!
And of course, this implementation looks incredibly inefficient - there must be different ways to do it!
*/

//VARYING AND UNIFORM VARIABLES: AUTOMATICALLY SET BEFORE STARTING (BY HOST OR VERTEX SHADER)
varying vec2 tcoord; 			//gives our own coordinate as normalized floating point (x,y)
uniform sampler2D hor_sum_tex; 	//vertical texture of summed rows
uniform sampler2D ver_sum_tex; 	//horizontal texture of summed columns
uniform float num_coords; 		//total number of output pixels
uniform float hor_sum_height; 	//total number of summed rows
uniform float ver_sum_width;	//total number of summed columns

float x = 0.0f;
float y = 0.0f;

float foundx = 0.0f;
float foundwidth = 0.0f;
float foundy = 0.0f;
float foundheight = 0.0f;

float stepx = 1.0f/ver_sum_width;
float stepy = 1.0f/hor_sum_height;

int first = 1;

//A function that can be called repeatedly to "iterate over" objects.
//The first time it is called, it finds the first object on the x axis, then the first on the y axis. Subsequent calls
//will move to the next object on the Y axis, until the end is reached - then it will go back to the top and find the next
//one on the x axis.
int nextObject(void){
	int result = 0;

	//find first object on x axis
	if(first==1){
		for(; (x<=1.0f); x+=stepx){
			if(texture2D(ver_sum_tex,vec2(x,0.0f)).r > 0.0f){
				foundx = x; //note start
				for(; (x<=1.0f); x+=stepx) {
					if(texture2D(ver_sum_tex,vec2(x,0.0f)).r == 0.0f) break;
				}
				foundwidth = x - foundx; //note end
				result = 1;
				break;
			}
		}
		if(result == 0) return 0; //there are no objects.
		first = 0;
	}
	
	//go to start of next object on y axis
	for(; (y<=1.0f); y+=stepy){
		if(texture2D(hor_sum_tex,vec2(0.0f,y)).r > 0.0f){
			foundy = y; //note start
			for(; (y<=1.0f); y+=stepx) {
				if(texture2D(hor_sum_tex,vec2(0.0f,y)).r == 0.0f) break;
			}
			foundheight = y - foundy; //note end
			return 1; //we found a new object, return success.
			break;
		}
	}
	
	//we reached the end and found no more objects on y axis: move to next x axis object then and start over!
	result = 0;
	//search for next x object
	for(; (x<=1.0f); x+=stepx){
		if(texture2D(ver_sum_tex,vec2(x,0.0f)).r > 0.0f){
			foundx = x; //note start
			for(; (x<=1.0f); x+=stepx) {
				if(texture2D(ver_sum_tex,vec2(x,0.0f)).r == 0.0f) break;
			}
			foundwidth = x - foundx; //note end
			result = 1;
			break;
		}
	}
	if(result == 0) return 0; //no more objects
	
	//go to start of first object on y axis
	for(y=0.0f; (y<=1.0f); y+=stepy){
		if(texture2D(hor_sum_tex,vec2(0.0f,y)).r > 0.0f){
			foundy = y; //note start
			for(; (y<=1.0f); y+=stepx) {
				if(texture2D(hor_sum_tex,vec2(0.0f,y)).r == 0.0f) break;
			}
			foundheight = y-foundy; //note end
			return 1; //we found a new object, return success.
			break;
		}
	}	
	
	return 0; //no more objects at all.
}


//MAIN FUNCTION
void main(void)
{
	//find out "which pixel we are" by multiplying our normalized floating point coordinate (stored in tcoord) by the total number of pixels (stored in num_coords).
	float my_num = (tcoord[0]*num_coords);
	//now iterate over objects until we reach the one "with our index" (the one we should provide information about)
	float i;
	for(i=0; i<my_num; i=i+1.0f){
		if(nextObject() == 0) return;
	}
	
	//now store the object information in our output pixel
	gl_FragColor = vec4(foundx,foundy,foundwidth,foundheight);
}