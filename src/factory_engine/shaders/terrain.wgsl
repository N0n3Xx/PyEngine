struct VertexOutput {
    @builtin(position) position: vec4f,
    @location(0) world_position: vec3f,
    @location(1) normal: vec3f,
    @location(2) uv: vec2f,
};

struct Camera {
    view_projection: mat4x4f,
    position: vec3f,
    _padding: f32,
};

struct Light {
    direction: vec3f,
    _padding: f32,
};

struct Material {
    base_color: vec4f,
    metallic: f32,
    roughness: f32,
    _padding: vec2f,
};

@group(0) @binding(0)
var<uniform> camera: Camera;

@group(0) @binding(2)
var<uniform> light: Light;


@group(1) @binding(0)
var<uniform> material: Material;

@group(1) @binding(1)
var material_sampler: sampler;

@group(1) @binding(2)
var material_texture: texture_2d<f32>;


@group(2) @binding(0)
var environment_sampler: sampler;

@group(2) @binding(1)
var environment_texture: texture_cube<f32>;

@vertex
fn vs_main(
    @location(0) vertex_position: vec3f,
    @location(1) vertex_normal: vec3f,
    @location(2) vertex_uv: vec2f,
) -> VertexOutput {
    var output: VertexOutput;

    let world_position = vec4f(vertex_position, 1.0);

    output.position = camera.view_projection * world_position;
    output.world_position = vertex_position;
    output.normal = vertex_normal;
    output.uv = vertex_uv;

    return output;
}

@fragment
fn fs_main(
    input: VertexOutput
) -> @location(0) vec4f {
    let normal = normalize(input.normal);

    let view_direction = normalize(
        camera.position - input.world_position
    );

    let light_direction = normalize(
        light.direction
    );

    // Reflection direction for both direct specular
    // and environment reflection.
    let reflection_direction = reflect(
        -view_direction,
        normal
    );

    let ambient = 0.15;

    // Material texture
    let texture_color = textureSample(
        material_texture,
        material_sampler,
        input.uv
    );

    let base_color =
        material.base_color.rgb *
        texture_color.rgb;

    // --------------------------------------------------
    // Diffuse
    // --------------------------------------------------

    let diffuse = max(
        dot(normal, light_direction),
        0.0
    );

    let diffuse_color =
        base_color *
        diffuse *
        (1.0 - material.metallic);

    // --------------------------------------------------
    // Direct Specular
    // --------------------------------------------------

    let specular_amount = max(
        dot(view_direction, reflection_direction),
        0.0
    );

    let shininess = mix(
        128.0,
        2.0,
        material.roughness
    );

    let specular = pow(
        specular_amount,
        shininess
    );

    let specular_color = mix(
        vec3f(0.04),
        base_color,
        material.metallic
    );

    let specular_light =
        specular_color * specular;

    // --------------------------------------------------
    // Environment Reflection
    // --------------------------------------------------

    let environment_color = textureSample(
        environment_texture,
        environment_sampler,
        reflection_direction
    ).rgb;

    let reflection_strength =
        material.metallic *
        (1.0 - material.roughness);

    let environment_reflection =
        environment_color *
        reflection_strength;

    // --------------------------------------------------
    // Final Lighting
    // --------------------------------------------------

    let color =
        base_color * ambient +
        diffuse_color +
        specular_light +
        environment_reflection;

    return vec4f(color, 1.0);
}
