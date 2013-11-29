// A3 vertex shader
// Transform position into clip coordinates
#version 150

uniform mat4 mvpTransform;

in vec3 position;
in vec3 inColor;

out vec4 outColor;

void main(void)
{

    gl_Position = mvpTransform * vec4(position, 1.0);
    outColor =  vec4(inColor, 1.0);
}
