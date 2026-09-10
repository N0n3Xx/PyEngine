struct VertexOutput {
    @builtin(position) position: vec4f,
    @location(0) local_position: vec3f,
    @location(1) normal: vec3f,
    @location(2) local_normal: vec3f,
    @location(3) instance_index: u32
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

    @location(2) model_0: vec4f,
	@location(3) model_1: vec4f,
	@location(4) model_2: vec4f,
	@location(5) model_3: vec4f,

	@builtin(instance_index) instance_index: u32
) -> VertexOutput {
    var output: VertexOutput;
    let model_matrix = mat4x4<f32>(
        model_0,
        model_1,
        model_2,
        model_3
    );
    let world_position = model_matrix * vec4f(vertex_position, 1.0);

    output.position =
        camera.view_projection
        * world_position;
    output.local_position = vertex_position;
    output.normal = (model_matrix * vec4f(vertex_normal, 0.0)).xyz;
    output.local_normal = vertex_normal;
    output.instance_index = instance_index;

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
    let base_color = vec3f(
        random(input.instance_index * 3u + 0u),
        random(input.instance_index * 3u + 1u),
        random(input.instance_index * 3u + 2u)
    );

    // Lambert diffuse
    let diffuse = max(dot(normal, light_direction), 0.0);
    let brightness = min(ambient + diffuse, 1.0);
    
    let color = base_color * brightness;
    
    return vec4f(color, 1.0);
}

fn random(seed: u32) -> f32 {
    var x = seed;
    x = x * 747796405u + 2891336453u;
    x = ((x >> ((x >> 28u) + 4u)) ^ x) * 277803737u;
    x = (x >> 22u) ^ x;

    return f32(x) / 4294967295.0;
}
