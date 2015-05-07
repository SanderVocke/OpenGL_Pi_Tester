// Attribute variable that contains coordinates of the vertices.
layout(location = 0) in vec3 position;

// Main function, which needs to set `gl_Position`.
void main()
{
    // The final position is transformed from a null signal to a sinewave here.
    // We pass the position to gl_Position, by converting it into
    // a 4D vector. The last coordinate should be 0 when rendering 2D figures.
    //gl_Position = vec4(position.x, .2 * sin(20 * position.x), 0., 1.);
	
	gl_Position = vec4(position.xyz, 1.0);
}