from PIL import ImageGrab
from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QPushButton, QLabel
from screeninfo import get_monitors

class MonitorSelector(QDialog):
    def __init__(self, monitors, parent=None):
        super().__init__(parent)
        self.setWindowTitle("モニター選択")
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("キャプチャするモニターを選択してください："))
        
        self.combo = QComboBox()
        for i, monitor in enumerate(monitors):
            self.combo.addItem(
                f"モニター {i+1} ({monitor.width}x{monitor.height}) - {monitor.name}", 
                monitor
            )
        layout.addWidget(self.combo)
        
        btn = QPushButton("選択")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)
        
    def get_selected_monitor(self):
        monitor = self.combo.currentData()
        return {
            'left': monitor.x,
            'top': monitor.y,
            'width': monitor.width,
            'height': monitor.height
        }

class CaptureService:
    @staticmethod
    def get_monitors():
        return list(get_monitors())
    
    @staticmethod
    def select_monitor(parent=None):
        monitors = CaptureService.get_monitors()
        if len(monitors) == 1:
            monitor = monitors[0]
            return {
                'left': monitor.x,
                'top': monitor.y,
                'width': monitor.width,
                'height': monitor.height
            }
        
        dialog = MonitorSelector(monitors, parent)
        if dialog.exec():
            return dialog.get_selected_monitor()
        return None

    @staticmethod
    def capture_full_screen(monitor=None):
        if monitor:
            bbox = (
                monitor['left'],
                monitor['top'],
                monitor['left'] + monitor['width'],
                monitor['top'] + monitor['height']
            )
            try:
                screenshot = ImageGrab.grab(bbox=bbox, all_screens=True)
            except Exception as e:
                print(f"Error capturing screen: {e}")
                screenshot = ImageGrab.grab(all_screens=True)
        else:
            screenshot = ImageGrab.grab(all_screens=True)
        return screenshot
    
    @staticmethod
    def capture_area(rect: QRect, monitor=None):
        if monitor:
            bbox = (
                monitor['left'] + rect.x(),
                monitor['top'] + rect.y(),
                monitor['left'] + rect.x() + rect.width(),
                monitor['top'] + rect.y() + rect.height()
            )
        else:
            bbox = (
                rect.x(),
                rect.y(),
                rect.x() + rect.width(),
                rect.y() + rect.height()
            )
        try:
            screenshot = ImageGrab.grab(bbox=bbox, all_screens=True)
        except Exception as e:
            print(f"Error capturing area: {e}")
            screenshot = ImageGrab.grab(bbox=bbox)
        return screenshot
