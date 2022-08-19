import time
from AppKit import NSWorkspace


if __name__ == "__main__":
    active_window = NSWorkspace.sharedWorkspace().activeApplication().get("NSApplicationBundleIdentifier")
    while True:
        time.sleep(0.5)
        new_window = NSWorkspace.sharedWorkspace().activeApplication().get("NSApplicationBundleIdentifier")
        if new_window != active_window:
            print(new_window)
            active_window = new_window
