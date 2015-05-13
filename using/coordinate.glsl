varying vec2 tcoord;
uniform sampler2D hor_sum_tex;
uniform sampler2D ver_sum_tex;
uniform float num_coords;
uniform float hor_sum_height;
uniform float ver_sum_width;

float x = 0.0f;
float y = 0.0f;

float foundx = 0.0f;
float foundwidth = 0.0f;
float foundy = 0.0f;
float foundheight = 0.0f;

float stepx = 1.0f/ver_sum_width;
float stepy = 1.0f/hor_sum_height;

int first = 1;

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

void main(void)
{	
	
	
	/*
	//go to first x
	for(x=0.0f; (x<1.0f); x+=stepx){
		if(texture2D(ver_sum_tex,vec2(x,0.0f)).r > 0.0f){
			foundx = x;
			found = 1.0f;
			break;
		}
	}
	for(y=0.0f; (y<1.0f); y+=stepy){
		if(texture2D(hor_sum_tex,vec2(0.0f,y)).r > 0.0f){
			foundy = y;
			found = 1.0f;
			break;
		}
	}
	*/
	
	float my_num = (tcoord[0]*num_coords);
	float i;
	for(i=0; i<my_num; i=i+1.0f){
		if(nextObject() == 0) return;
	}
	
	gl_FragColor = vec4(foundx,foundy,foundwidth,foundheight);	
	
	//gl_FragColor = texture2D(hor_sum_tex, tcoord);
	//gl_FragColor = vec4(1.0f,1.0f,1.0f,1.0f);
}