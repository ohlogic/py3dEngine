class MouseStateHandler(dict):
    def on_mouse_press(self, x, y, button, modifiers):
        self[button] = True
    def on_mouse_release(self, x, y, button, modifiers):
        self[button] = False
    def __getitem__(self, key):
        return self.get(key, False)