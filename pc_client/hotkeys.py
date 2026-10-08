from pynput import keyboard

def start_hotkeys(on_type, on_stop):
    hotkey = keyboard.HotKey(keyboard.HotKey.parse("<ctrl>+<shift>+t"), on_type)
    def canonical(key): return listener.canonical(key)
    def press(key):
        if key == keyboard.Key.esc: on_stop()
        hotkey.press(canonical(key))
    def release(key): hotkey.release(canonical(key))
    listener = keyboard.Listener(on_press=press, on_release=release)
    listener.start(); return listener
