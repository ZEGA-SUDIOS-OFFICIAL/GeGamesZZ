// ZEGA - MASTER BUILD SHADER SYSTEM v1.1
// Language: GLSL (OpenGL Shading Language)

#ifdef VERTEX_SHADER
layout (location = 0) in vec3 position;
void main() {
    gl_Position = vec4(position, 1.0);
}
#endif

#ifdef FRAGMENT_SHADER
uniform float u_time;
uniform vec2 u_resolution;
uniform vec2 u_mouse;
out vec4 fragColor;

// ZEGA BRAND COLOR: #58f01b
const vec3 ZEGA_GREEN = vec3(0.34, 0.94, 0.10);

void main() {
    // Normalize coordinates
    vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / u_resolution.y;
    
    // --- PERSPECTIVE GRID GENERATION ---
    float horizon = -0.2;
    float perspective = 1.0 / (uv.y - horizon);
    
    vec2 gridUv = uv;
    gridUv.y = perspective + (u_time * 0.8); // Movement speed
    gridUv.x *= perspective * 0.5;
    
    // Grid line calculation
    float lineWeight = 0.05;
    float gridLines = smoothstep(1.0 - lineWeight, 1.0, fract(gridUv.x * 8.0)) + 
                      smoothstep(1.0 - lineWeight, 1.0, fract(gridUv.y * 8.0));
    
    // Fog / Depth fade
    float depthFade = smoothstep(10.0, 0.0, perspective);
    vec3 color = mix(vec3(0.02), ZEGA_GREEN * 0.4, gridLines * depthFade);

    // --- LASER EFFECTS ---
    // Calculate laser beam based on mouse position
    vec2 mouseUv = (u_mouse * 2.0 - u_resolution.xy) / u_resolution.y;
    float laserWidth = 0.008;
    float distToLaser = abs(uv.x - (mouseUv.x * (uv.y - horizon) / (mouseUv.y - horizon)));
    
    // Only render laser above the ground and below the target height
    if (uv.y > horizon) {
        float beam = (laserWidth / distToLaser) * smoothstep(0.1, 0.0, distToLaser);
        color += beam * ZEGA_GREEN * 1.5;
    }

    // Final Post-Processing (Vignette)
    float vignette = smoothstep(1.5, 0.5, length(uv));
    fragColor = vec4(color * vignette, 1.0);
}
#endif