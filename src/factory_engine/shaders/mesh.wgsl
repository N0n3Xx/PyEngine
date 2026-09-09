struct VertexOutput {
    @builtin(position) position: vec4f,
    @location(0) local_position: vec3f,
    @location(1) normal: vec3f
};

struct Camera {
    view_projection: mat4x4f
};

struct Model {
    matrix: mat4x4f
};

struct Light {
    direction: vec3f,
    _padding: f32,
};

@group(0) @binding(0)
var<uniform> camera: Camera;

@group(0) @binding(1)
var<uniform> model: Model;

@group(0) @binding(2)
var<uniform> light: Light;

@vertex
fn vs_main(@location(0) vertex_position: vec3f, @location(1) vertex_normal: vec3f) -> VertexOutput {
    var output: VertexOutput;
    let world_position = model.matrix * vec4f(vertex_position, 1.0);

    output.position =
        camera.view_projection
        * world_position;
    output.local_position = vertex_position;
    output.normal = (model.matrix * vec4f(vertex_normal, 0.0)).xyz;
    
    return output;
}

@fragment
fn fs_main(
    input: VertexOutput
) -> @location(0) vec4f {
    let normal = normalize(input.normal);
    let light_direction = normalize(light.direction);

    // Custom Variables
    let ambient = 0.15;
    let base_color = vec3f(0.8, 0.35, 0.05);

    // Lambert diffuse
    let diffuse = max(dot(normal, light_direction), 0.0);
    let brightness = min(ambient + diffuse, 1.0);

    // Checking for the front face
    if (all(input.normal == vec3f(0.0, 0.0, 1.0))) {
        let x = abs(input.local_position.x);
        let y = abs(input.local_position.y);
        
        let distance = max(x, y);

        let inner = smoothstep(0.2, 0.25, distance);
        let outer = smoothstep(0.3, 0.35, distance);
        let glow_mask = inner - outer;
        let circle_mask = 1.0 - smoothstep(0.2, 0.3, length(input.local_position.xy));
        
        let purple = vec3f(0.6, 0.0, 1.0);
        let white = vec3f(1.0, 1.0, 1.0);
        
        let glow_color = purple * glow_mask;

        let _final_color = base_color + glow_color + (white * circle_mask * glow_mask);
        return vec4f(_final_color, 1.0);
    }
    
    let color = base_color * brightness;
    
    return vec4f(color, 1.0);
}
