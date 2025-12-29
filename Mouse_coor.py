import time
import sys

def run_tracker():
    print("--- Mouse Coordinate Tracker (DPI Aware) ---")
    print("Move your mouse to the corners of the area you want to scan.")
    print("Press Ctrl + C to stop.\n")

    try:
        # Method 1: Try using pyautogui (if installed)
        import pyautogui
        print("Using pyautogui...")
        print("---------------------------------------------------------")
        pyautogui.displayMousePosition()
        
    except ImportError:
        # Method 2: Fallback to ctypes (Standard Windows Library)
        import ctypes
        
        # --- CRITICAL FIX: ENABLE HIGH DPI AWARENESS ---
        # This forces the script to see the "real" physical pixels, 
        # matching what screenshot tools typically see.
        try:
            # Try setting Process DPI Awareness (Windows 8.1+)
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                # Fallback for older Windows
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass
        # -----------------------------------------------

        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

        def get_pos():
            pt = POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
            return pt.x, pt.y

        print("pyautogui not found. Using standard Windows libraries (DPI Aware).")
        print("---------------------------------------------------------")
        
        try:
            while True:
                x, y = get_pos()
                # formatting to ensure the text overwrites cleanly
                position_str = "X: {:<4} Y: {:<4}".format(x, y)
                
                # \r returns cursor to start of line to update in place
                sys.stdout.write("\r" + position_str)
                sys.stdout.flush()
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n\nDone.")

if __name__ == "__main__":
    run_tracker()