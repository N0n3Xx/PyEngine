struct SkyboxUniforms {
	view_projection: mat4x4<f32>,
};

@group(0) @binding(0)
var<uniform> uniforms: SkyboxUniforms;

@group(0) @binding(1)
var skybox_sampler: sampler;

@group(0) @binding(2)
var skybox_texture: texture_cube<f32>;


struct VertexOutput {
	@builtin(position) position: vec4<f32>,
	@location(0) direction: vec3<f32>,
};


@vertex
fn vs_main(
	@location(0) position: vec3<f32>
) -> VertexOutput {

	var output: VertexOutput;

	output.direction = position;

	let clip_position =
		uniforms.view_projection *
		vec4<f32>(position, 1.0);

	output.position = vec4<f32>(
		clip_position.xy,
		clip_position.w,
		clip_position.w
	);

	return output;
}


@fragment
fn fs_main(
	input: VertexOutput
) -> @location(0) vec4<f32> {

	return textureSample(
		skybox_texture,
		skybox_sampler,
		normalize(input.direction)
	);
}