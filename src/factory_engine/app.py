"""Application setup and render loop."""

from pathlib import Path

import wgpu
from rendercanvas.glfw import RenderCanvas, loop


SHADER_PATH = Path(__file__).parent / "shaders" / "fullscreen.wgsl"


class GameApp:
    """Owns the window and the small amount of GPU state needed to draw."""

    def __init__(self) -> None:
        self.canvas = RenderCanvas(size=(1280, 720), title="Factory Game")

        adapter = wgpu.gpu.request_adapter_sync(power_preference="high-performance")
        self.device = adapter.request_device_sync()

        self.context = self.canvas.get_wgpu_context()
        self.texture_format = self.context.get_preferred_format(self.device.adapter)
        self.context.configure(device=self.device, format=self.texture_format)

        shader = self.device.create_shader_module(code=SHADER_PATH.read_text())
        self.pipeline = self.device.create_render_pipeline(
            layout=wgpu.AutoLayoutMode.auto,
            vertex={"module": shader},
            fragment={
                "module": shader,
                "targets": [{"format": self.texture_format}],
            },
        )

    def draw_frame(self) -> None:
        """Draw one frame of the full-screen shader."""
        encoder = self.device.create_command_encoder()
        texture_view = self.context.get_current_texture().create_view()
        render_pass = encoder.begin_render_pass(
            color_attachments=[
                {
                    "view": texture_view,
                    "clear_value": (0.0, 0.0, 0.0, 1.0),
                    "load_op": wgpu.LoadOp.clear,
                    "store_op": wgpu.StoreOp.store,
                }
            ]
        )
        render_pass.set_pipeline(self.pipeline)
        render_pass.draw(3)
        render_pass.end()

        self.device.queue.submit([encoder.finish()])

    def run(self) -> None:
        """Start the window event loop."""
        self.canvas.request_draw(self.draw_frame)
        loop.run()


def main() -> None:
    """Create and run the game application."""
    GameApp().run()
