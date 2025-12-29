import re
import sys
import time
import os
import io
import json
from datetime import datetime
import ctypes

# --- CRITICAL FIX FOR WINDOWS XP / PYTHON 3.4 ---
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
# ------------------------------------------------

try:
    from PIL import Image, ImageOps, ImageGrab, ImageEnhance, ImageFilter
except ImportError:
    print("Error: Pillow library not found. Please install it using 'pip install Pillow'")
    sys.exit(1)

import pytesseract

# --- WINDOWS API SETUP ---
class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long)]

# Enable High-DPI scaling to ensure coordinates match your actual screen layout
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# --- CONFIGURATION ---

# The script will search for any window containing this text in its title.
# It works regardless of where the window is positioned on the screen.
TARGET_WINDOW_PARTIAL_NAME = "OCR Demo" 

REFRESH_RATE = 1
DEBUG_SCREENSHOTS_DIR = "debug_screenshots"

# ---------------------

def get_window_bbox_partial(partial_name):
    """Scans ALL open windows for partial title match."""
    user32 = ctypes.windll.user32
    found_rect = []

    def callback(hwnd, lParam):
        length = user32.GetWindowTextLengthW(hwnd)
        if length == 0: return True
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        title = buff.value
        if not user32.IsWindowVisible(hwnd): return True

        # Case-insensitive partial match
        if partial_name.lower() in title.lower():
            rect = RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            found_rect.append((rect.left, rect.top, rect.right, rect.bottom))
            found_rect.append(title)
            return False # Stop enumerating after finding the first match
        return True

    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    user32.EnumWindows(WNDENUMPROC(callback), 0)

    if found_rect:
        return found_rect[0], found_rect[1]
    return None, None

def extract_data(image_source):
    """Runs OCR and parses the text."""
    try:
        # --- IMPROVED PRE-PROCESSING ---
        # 1. NO RESIZING: The HTML font is already 85px (huge). 
        #    Upscaling it further confuses Tesseract.
        img = image_source 

        # 2. Enhance Contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)

        # 3. Convert to Grayscale
        img = img.convert('L') 
        
        # 4. Thicken Text (Morphological Dilation)
        #    Reduced filter size because we aren't upscaling anymore
        img = img.filter(ImageFilter.MinFilter(1)) 

        # 5. Invert if needed (Check darker background)
        if img.getpixel((0, 0)) < 128: 
            img = ImageOps.invert(img)
            
        # 6. Binarize (High threshold to isolate text)
        thresh = 150
        fn = lambda x : 255 if x > thresh else 0
        img = img.convert('L').point(fn, mode='1')
        
        # Run Tesseract
        raw_text = pytesseract.image_to_string(img, config='--psm 6')
        
        print("\n--- [DEBUG] Raw Text Content ---")
        print(raw_text.strip()[:100] + "...") # Print first 100 chars
        print("--------------------------------")
        
        data = {
            "Strike Rate": None,
            "CPU Usage": None,
            "Machine ID": None
        }

        # Regex Logic - Now filters out "0" values
        strike_match = re.search(r"Strike\s*(?:Rate)?[\s\S]{0,50}?(\d+)", raw_text, re.IGNORECASE)
        if strike_match: 
            val = int(strike_match.group(1))
            if val > 0: data["Strike Rate"] = val

        cpu_match = re.search(r"CPU\s*(?:Usage)?[\s\S]{0,50}?(\d+)", raw_text, re.IGNORECASE)
        if cpu_match: 
            val = int(cpu_match.group(1))
            if val > 0: data["CPU Usage"] = val

        id_match = re.search(r"Machine\s*ID[\s\S]{0,50}?(\d+)", raw_text, re.IGNORECASE)
        if id_match: 
            val = int(id_match.group(1))
            if val > 0: data["Machine ID"] = val

        return data

    except Exception as e:
        return {"Error": str(e)}

def capture_and_process(bbox):
    try:
        # 1. Grab screenshot to memory
        screenshot = ImageGrab.grab(bbox=bbox)

        # 2. Run OCR *before* saving
        data = extract_data(screenshot)
        
        # 3. Check for Success
        # We consider it a success if we found ANY of the target values
        success = False
        if isinstance(data, dict) and "Error" not in data:
            if data.get("Strike Rate") or data.get("CPU Usage") or data.get("Machine ID"):
                success = True

        # 4. Save screenshot ONLY if successful
        if success:
            if not os.path.exists(DEBUG_SCREENSHOTS_DIR):
                os.makedirs(DEBUG_SCREENSHOTS_DIR)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = "{}/scan_{}.png".format(DEBUG_SCREENSHOTS_DIR, timestamp)
            screenshot.save(filename)
            data["Saved Image"] = filename
        else:
            data["Saved Image"] = "Skipped (No Data Found)"
            
        return data

    except Exception as e:
        return {"Error": "Screen capture failed: " + str(e)}

def save_to_json(data, filename):
    """Appends the current data dict to a JSON list file."""
    try:
        current_data = []
        # If file exists, read it first to append
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    current_data = json.load(f)
            except ValueError:
                current_data = [] # Handle corrupted/empty JSON

        current_data.append(data)

        with open(filename, 'w') as f:
            json.dump(current_data, f, indent=4)
            
    except Exception as e:
        print("Error saving JSON: " + str(e))

if __name__ == "__main__":
    print("--- OCR Monitor Started ---")
    print("Target Window (Partial Name): '{}'".format(TARGET_WINDOW_PARTIAL_NAME))
    
    # Create a unique filename for this session
    session_json_file = "ocr_log_{}.json".format(datetime.now().strftime("%Y%m%d_%H%M%S"))
    print("Logging data to: '{}'".format(session_json_file))
    
    print("Press Ctrl + C to stop")
    time.sleep(1)

    try:
        while True:
            # Dynamically find the window location every loop
            # This allows you to move the window around without breaking the script
            bbox, title_display = get_window_bbox_partial(TARGET_WINDOW_PARTIAL_NAME)
            
            if bbox:
                print("\n" + "="*50)
                print("Capturing: '{}'".format(title_display))
                print("Coordinates: {}".format(bbox))
                
                result = capture_and_process(bbox)
                
                # Add timestamp to the result
                result["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Save to JSON
                save_to_json(result, session_json_file)
                
                found_any = False
                for key, value in result.items():
                    val_display = str(value) if value is not None else "Not Found"
                    if value is not None and key != "Saved Image": found_any = True
                    print("{:<20}: {}".format(key, val_display))
                
                if not found_any:
                     print("\n[Tip] Values missing? Check 'debug_screenshots' folder.")
            else:
                print("Scanning... Window containing '{}' not found.".format(TARGET_WINDOW_PARTIAL_NAME))
            
            time.sleep(REFRESH_RATE)

    except KeyboardInterrupt:
        print("\nStopping monitor...")