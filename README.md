# PyEngine

A small starting point for a Python factory-game engine. It opens a GLFW
window and draws a full-window WGSL shader with `wgpu`.

## Requirements

- Python 3.11 or newer
- A GPU supported by `wgpu` (Metal is used on macOS)

## Run

Create and activate a virtual environment, then install the project:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python main.py
```

The example shader lives in `src/factory_engine/shaders/fullscreen.wgsl`.
It uses a full-screen triangle, so no vertex buffer is required. Start the
engine with `src/factory_engine/app.py` when adding game systems.
