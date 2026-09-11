struct VertexOutput {
    @builtin(position) position: vec4f,
    @location(0) local_position: vec3f,
    @location(1) normal: vec3f,
    @location(2) uv: vec2f,
};

struct Camera {
    view_projection: mat4x4f
};

struct Light {
    direction: vec3f,
    _padding: f32,
};

@group(0) @binding(0)
var<uniform> camera: Camera;

@group(0) @binding(2)
var<uniform> light: Light;

@vertex
fn vs_main(
    @location(0) vertex_position: vec3f,
    @location(1) vertex_normal: vec3f,
    @location(2) vertex_uv: vec2f,
) -> VertexOutput {
    var output: VertexOutput;

    let world_position = vec4f(vertex_position, 1.0);

    output.position = camera.view_projection * world_position;
    output.local_position = vertex_position;
    output.normal = vertex_normal;
    output.uv = vertex_uv;

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
    let base_color = vec3f(0.8, 0.8, 0.8);

    // Lambert diffuse
    let diffuse = max(dot(normal, light_direction), 0.0);
    let brightness = min(ambient + diffuse, 1.0);
    
    let color = base_color * brightness;
    
    return vec4f(color, 1.0);
}
