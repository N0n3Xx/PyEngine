struct VertexOutput {
    @builtin(position) position: vec4f,
};

struct Camera {
    view_projection: mat4x4f
};

@group(0) @binding(0)
var<uniform> camera: Camera;

@vertex
fn vs_main(@location(0) vertex_position: vec3f) -> VertexOutput {
    var output: VertexOutput;

    output.position = camera.view_projection * vec4f(vertex_position, 1.0);
    
    return output;
}

@fragment
fn fs_main() -> @location(0) vec4f {
    return vec4f(1.0, 0.35, 0.05, 1.0);
}
