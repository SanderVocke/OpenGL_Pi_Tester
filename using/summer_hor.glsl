varying vec2 tcoord;
uniform sampler2D tex;
uniform int hor_resolution;

void main(void)
{
    gl_FragColor = vec4(doThreshold(texture2D( tex, tcoord).rgb), texture2D(tex,tcoord).a);
	//gl_FragColor = vec4(colorizeSelect(texture2D( tex, tcoord).rgb), texture2D(tex,tcoord).a);
}