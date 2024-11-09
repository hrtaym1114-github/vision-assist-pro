from PIL import ImageGrab
#import numpy as np
from PyQt6.QtCore import QRect

class CaptureService:
    @staticmethod
    def capture_full_screen():
        screenshot = ImageGrab.grab()
        return screenshot
    
    @staticmethod
    def capture_area(rect: QRect):
        screenshot = ImageGrab.grab(bbox=(
            rect.x(),
            rect.y(),
            rect.x() + rect.width(),
            rect.y() + rect.height()
        ))
        return screenshot
