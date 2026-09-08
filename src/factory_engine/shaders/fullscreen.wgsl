struct VertexOutput {
    @builtin(position) position: vec4f,
    @location(0) uv: vec2f,
};

@vertex
fn vertex_main(@builtin(vertex_index) index: u32) -> VertexOutput {
    var positions = array<vec2f, 3>(
        vec2(-1.0, -1.0),
        vec2(3.0, -1.0),
        vec2(-1.0, 3.0),
    );

    var output: VertexOutput;
    let position = positions[index];
    output.position = vec4(position, 0.0, 1.0);
    output.uv = position * 0.5 + vec2(0.5, 0.5);
    return output;
}

@fragment
fn fragment_main(input: VertexOutput) -> @location(0) vec4f {
    let base_color = vec3(0.06, 0.10, 0.14);
    let highlight = vec3(0.12, 0.45, 0.32);
    let color = mix(base_color, highlight, input.uv.y);
    return vec4(color, 1.0);
}
