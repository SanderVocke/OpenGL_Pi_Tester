varying vec2 tcoord;
uniform sampler2D tex;
uniform float ver_steps;

void main(void)
{
	float sum = 0.0f;
	float step = 1.0f/ver_steps;
	int i = 0;
	for(;i<ver_steps;i++){
		sum = sum + texture2D(tex,vec2(tcoord[0],step*i)).r;
	}
	float result = sum/ver_steps;
    //gl_FragColor = vec4(result,0.0f,0.0f,0.0f);
	gl_FragColor = vec4(result,0.0f,0.0f,0.0f);
	float found;
	if(result>0.0f) found = 1.0f;
	else discard;
	gl_FragColor = vec4(result,0.0f,found,0.0f);
}