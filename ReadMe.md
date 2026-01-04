Prerequisites

Before running this project, you need to install the following software:

1. Python 3.4.4

This exact version is required for compatibility with the included dependencies.


2. Tesseract OCR Engine

The script needs Tesseract to "read" the screen.

Download: Tesseract-OCR 3.05 

Installation Path: Install to the default location:
C:\Program Files(x86)\Tesseract-OCR

If you install it elsewhere, you must update the path inside ocr.py.

Installation & Setup

Download this project to a folder on your computer.

Open Command Prompt in that folder (click address bar, type cmd, press Enter).

Create the Virtual Environment:
Run the following command to create an isolated environment named xp_env:

C:\Python34\python.exe -m venv xp_env


Install Dependencies:
Run this command to install Pillow (5.4.1) and Pytesseract:

xp_env\Scripts\pip install -r requirements.txt

(if this does not work, install them seperately step by step)



Configuration

You can edit ocr.py to change settings:

TARGET_WINDOW_PARTIAL_NAME: Change this string to match the title of the window you want to watch.

REFRESH_RATE: How many seconds to wait between scans (Default: 1).

DEBUG_SCREENSHOTS_DIR: Where to save images (Default: debug_screenshots).

Troubleshooting

"python is not recognized": Ensure you installed Python 3.4.4 and added it to your PATH, or rely on run_ocr.bat which tries to find it automatically.

"Tesseract not found": Ensure Tesseract is installed at C:\Program Files\Tesseract-OCR\tesseract.exe.

"ImportError: No module named PIL": You forgot to run the pip install -r requirements.txt step.
