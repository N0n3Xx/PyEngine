# Changelog

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
