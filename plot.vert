// A3 vertex shader
// Transform position into clip coordinates
#version 150

// TODO: Define any uniforms you need here
uniform mat4 mvpTransform;

// For A3, the only vertex attribute you need is the position. If you added
// any more, they go here
in vec3 position;
in vec3 inColor;
// For A3, the only out varying we need is the gl_Position. We could generate
// the color here if desired. Out variables go here if any.
out vec4 outColor;

void main(void)
{
    // TODO: Transform your point here. You may specify color here or in the 
    // fragment shader
    gl_Position = mvpTransform * vec4(position, 1.0);
    outColor =  vec4(inColor, 1.0);
}
