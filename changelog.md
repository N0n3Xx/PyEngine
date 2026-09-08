# Changelog

## 0.2.0 - 2026-09-08

Initial 3D rendering foundation.

- Added `math3d.py` with `Vec3` operations plus 4x4 identity, translation,
  Y-axis rotation, scale, perspective, look-at, transform, multiplication, and
  column-major upload helpers.
- Added a fixed `Camera` with a right-handed view matrix and a `wgpu`-compatible
  0-to-1 depth-range perspective projection.
- Added a view-projection uniform buffer, bind group, and per-frame upload.
- Added `Mesh.create_cube()` with float32 position vertices and uint16 indices.
- Replaced the full-screen shader with `mesh.wgsl`, which transforms mesh
  positions by the camera view-projection matrix and renders an orange cube.
- Updated the render pipeline for position vertex input and indexed drawing.
- Added a `depth24plus` depth texture, depth testing, depth clearing, and
  physical-size resize handling for the depth attachment.
- Added `test_math3d.py` checks for vector normalization, camera basis cross
  products, identity/translation transforms, and perspective projection.

Validation completed:

- `python3 -m compileall -q main.py src/factory_engine`
- `python3 src/factory_engine/test_math3d.py`
- `git diff --check` was run and reported existing trailing whitespace in
  `src/factory_engine/app.py`; the implementation was otherwise preserved as
  authored.

## 0.1.0 - 2026-09-08

Initial project scaffold for the factory-game engine.

- Added `pyproject.toml` for Python 3.11+ with `wgpu`, `rendercanvas[glfw]`, and GLFW dependencies.
- Added the `factory_engine` package and a root `main.py` entry point.
- Added a GLFW-backed `RenderCanvas` application that configures `wgpu` and renders a full-screen triangle.
- Added a small WGSL gradient shader at `src/factory_engine/shaders/fullscreen.wgsl`.
- Added run and project notes to the README.

Validation completed:

- `python3 -m py_compile main.py src/factory_engine/app.py`
- `git diff --check`

Runtime validation was not completed in this environment because project dependencies were not installed: the sandboxed package-install attempt could not reach PyPI (DNS/network unavailable).
