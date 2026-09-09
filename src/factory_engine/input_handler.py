# InputHandler.py

class InputHandler:
    def __init__(self):
        self.keys_down = set()
        self.keys_pressed = set()
        self.mouse_look_active = False
        self.last_mouse_position = None
        self.mouse_delta_x = 0.0
        self.mouse_delta_y = 0.0

    def handle_event(self, event):
        event_type = event["event_type"]

        if event_type == "key_down":
            key = event["key"].lower()

            self.keys_down.add(key)
            self.keys_pressed.add(key)
        elif event_type == "key_up":
            self.keys_down.discard(event["key"].lower())
        elif event_type == "pointer_down":
            if event["button"] == 1:
                self.mouse_look_active = True
                self.last_mouse_position = (event["x"], event["y"])
        elif event_type == "pointer_up":
            if event["button"] == 1:
                self.mouse_look_active = False
                self.last_mouse_position = None
        elif event_type == "pointer_move":
            if self.mouse_look_active and self.last_mouse_position is not None:
                previous_x, previous_y = self.last_mouse_position
                current_x = event["x"]
                current_y = event["y"]

                self.mouse_delta_x += current_x - previous_x
                self.mouse_delta_y += current_y - previous_y

                self.last_mouse_position = (current_x, current_y)

    def consume_mouse_delta(self):
        delta_x = self.mouse_delta_x
        delta_y = self.mouse_delta_y

        self.mouse_delta_x = 0.0
        self.mouse_delta_y = 0.0

        return delta_x, delta_y
        
    def is_down(self, key):
        return key.lower() in self.keys_down

    def is_pressed(self, key):
        key = key.lower()

        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
            return True

        return False