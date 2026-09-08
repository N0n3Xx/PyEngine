struct VertexOutput {
    @builtin(position) position: vec4f,
    @location(0) local_position: vec3f
};

struct Camera {
    view_projection: mat4x4f
};

struct Model {
    matrix: mat4x4f
};

@group(0) @binding(0)
var<uniform> camera: Camera;

@group(0) @binding(1)
var<uniform> model: Model;

@vertex
fn vs_main(@location(0) vertex_position: vec3f) -> VertexOutput {
    var output: VertexOutput;

    output.position =
        camera.view_projection
        * model.matrix
        * vec4f(vertex_position, 1.0);
    output.local_position = vertex_position;
    
    return output;
}

@fragment
fn fs_main(
    input: VertexOutput
) -> @location(0) vec4f {
    let vpos = input.local_position;
    return vec4f(vpos.x, vpos.y, vpos.z, 1.0);
}
