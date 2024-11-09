from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRect, pyqtSignal
from PyQt6.QtGui import QPainter, QColor

class CaptureOverlay(QWidget):
    capture_completed = pyqtSignal(QRect)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                          Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.showFullScreen()
        
        self.start_pos = None
        self.current_pos = None
        
    def paintEvent(self, event):
        if self.start_pos and self.current_pos:
            painter = QPainter(self)
            painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
            
            x1 = min(self.start_pos.x(), self.current_pos.x())
            y1 = min(self.start_pos.y(), self.current_pos.y())
            x2 = max(self.start_pos.x(), self.current_pos.x())
            y2 = max(self.start_pos.y(), self.current_pos.y())
            
            selection = QRect(x1, y1, x2 - x1, y2 - y1)
            painter.eraseRect(selection)
            painter.drawRect(selection)
            
    def mousePressEvent(self, event):
        self.start_pos = event.pos()
        self.current_pos = event.pos()
        
    def mouseMoveEvent(self, event):
        self.current_pos = event.pos()
        self.update()
        
    def mouseReleaseEvent(self, event):
        if self.start_pos and self.current_pos:
            x1 = min(self.start_pos.x(), self.current_pos.x())
            y1 = min(self.start_pos.y(), self.current_pos.y())
            x2 = max(self.start_pos.x(), self.current_pos.x())
            y2 = max(self.start_pos.y(), self.current_pos.y())
            
            self.capture_completed.emit(QRect(x1, y1, x2 - x1, y2 - y1))
            self.close()
            
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
