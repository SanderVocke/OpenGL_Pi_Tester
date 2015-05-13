varying vec2 tcoord;
uniform sampler2D tex;
uniform float hor_steps;

void main(void)
{
	float sum = 0.0f;
	float step = 1.0f/hor_steps;
	int i = 0;
	for(;i<hor_steps;i++){
		sum = sum + texture2D(tex,vec2(step*i,tcoord[1])).r;
	}
	float result = sum/hor_steps;
    //gl_FragColor = vec4(result,0.0f,0.0f,0.0f);
	gl_FragColor = vec4(result*5,0.0f,0.0f,0.0f);
}