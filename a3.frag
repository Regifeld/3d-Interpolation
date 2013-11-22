// A3 fragment shader
// Not much to do here other than set the color
#version 150

// Any uniforms you have go here

// Interpolated inputs. Only if you created some in your vertex program
in vec4 partColor;
// The output. Always a color
out vec4 fragColor;

void main() 
{  
    // Output the assigned color
    fragColor = partColor;
}