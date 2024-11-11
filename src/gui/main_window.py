from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QToolBar, 
                            QStatusBar, QMenuBar, QMenu, QMessageBox, QTabWidget,
                            QApplication, QComboBox, QHBoxLayout, QLabel)
from PyQt6.QtGui import QAction, QIcon, QPainter, QPen, QColor, QPainterPath
from PyQt6.QtCore import Qt, QTimer, QRect, QRectF, QThread, pyqtSignal
from .capture_overlay import CaptureOverlay
from src.gui.widgets import ResultTextEdit
from ..services.capture_service import CaptureService
from ..services.ocr_service import OCRService
from ..services.translation_service import TranslationService
from ..services.summary_service import SummaryService
from ..services.vision_service import VisionService

class ProcessingThread(QThread):
    finished = pyqtSignal(str)
    
    def __init__(self, service_method, *args):
        super().__init__()
        self.service_method = service_method
        self.args = args
    
    def run(self):
        try:
            result = self.service_method(*self.args)
            self.finished.emit(result)
        except Exception as e:
            print(f"Error in thread: {e}")
        finally:
            self.quit()

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 150);")
        layout = QVBoxLayout(self)
        
        self.label = QLabel("処理中...")
        self.label.setStyleSheet("color: white; font-size: 24px;")
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.dots = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_dots)
        self.timer.start(500)
    
    def update_dots(self):
        self.dots = (self.dots + 1) % 4
        self.label.setText("処理中" + "." * self.dots)

class EnhancedOCRTool(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setWindowTitle("VisionAssist Pro")
        self.setGeometry(100, 100, 800, 600)
        
        # サービスの初期化
        self.ocr_service = OCRService(config)
        self.translation_service = TranslationService(config)
        self.summary_service = SummaryService(config)
        self.capture_service = CaptureService()
        self.vision_service = VisionService(config)
        
        self.setup_ui()
        
    def setup_ui(self):
        self.setup_menubar()
        self.setup_toolbar()
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.layout = QVBoxLayout(main_widget)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.setup_result_area()
        
    def setup_menubar(self):
        menubar = self.menuBar()
        
        # キャプチャメニュー
        capture_menu = menubar.addMenu("キャプチャ")
        
        full_capture_action = QAction("フルスクリーン", self)
        full_capture_action.setShortcut("Ctrl+F")
        full_capture_action.triggered.connect(self.capture_full_screen)
        capture_menu.addAction(full_capture_action)
        
        area_capture_action = QAction("エリア選択", self)
        area_capture_action.setShortcut("Ctrl+A")
        area_capture_action.triggered.connect(self.capture_area)
        capture_menu.addAction(area_capture_action)
        
        # モードメニュー
        mode_menu = menubar.addMenu("モード")
        ocr_mode_action = QAction("OCRモード", self)
        ocr_mode_action.triggered.connect(lambda: self.mode_selector.setCurrentText("OCRモード"))
        mode_menu.addAction(ocr_mode_action)
        
        vision_mode_action = QAction("画像解説モード", self)
        vision_mode_action.triggered.connect(lambda: self.mode_selector.setCurrentText("画像説モード"))
        mode_menu.addAction(vision_mode_action)
        
        # 処理メニュー
        process_menu = menubar.addMenu("処理")
        
        summarize_action = QAction("テキスト要約", self)
        summarize_action.setShortcut("Ctrl+S")
        summarize_action.triggered.connect(self.summarize_text)
        process_menu.addAction(summarize_action)
        
        translate_action = QAction("翻訳", self)
        translate_action.setShortcut("Ctrl+T")
        translate_action.triggered.connect(self.translate_text)
        process_menu.addAction(translate_action)
        
        analyze_action = QAction("画像解説", self)
        analyze_action.setShortcut("Ctrl+I")
        analyze_action.triggered.connect(self.analyze_image)
        process_menu.addAction(analyze_action)
    
    def setup_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # モード選択用コンボボックス
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["OCRモード", "画像解説モード"])
        self.mode_selector.currentTextChanged.connect(self.on_mode_changed)
        toolbar.addWidget(self.mode_selector)
        
        toolbar.addSeparator()
        toolbar.addAction(QAction("フルスクリーン", self, triggered=self.capture_full_screen))
        toolbar.addAction(QAction("エリア選択", self, triggered=self.capture_area))
        toolbar.addSeparator()
        
        # OCR関連のアクション（OCRボタンを除外）
        self.ocr_actions = []
        self.ocr_actions.append(QAction("要約", self, triggered=self.summarize_text))
        self.ocr_actions.append(QAction("翻訳", self, triggered=self.translate_text))
        
        # 画像解説アクション
        self.vision_action = QAction("画像解説", self, triggered=self.analyze_image)
        
        # 初期状態ではOCRモード
        for action in self.ocr_actions:
            toolbar.addAction(action)
            
    def on_mode_changed(self, mode):
        toolbar = self.findChild(QToolBar)
        
        # 既存のアクションをクリア（キャプチャー関連以外）
        actions = toolbar.actions()
        for action in actions[4:]:  # モード選択、セパレータ、キャプチャーボタンを除く
            toolbar.removeAction(action)
        
        if mode == "OCRモード":
            for action in self.ocr_actions:
                toolbar.addAction(action)
            self.tab_widget.setCurrentWidget(self.ocr_result)
        else:
            toolbar.addAction(self.vision_action)
            self.tab_widget.setCurrentWidget(self.vision_result)
            
    def setup_result_area(self):
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)
        
        self.ocr_result = ResultTextEdit()
        self.summary_result = ResultTextEdit()
        self.translation_result = ResultTextEdit()
        self.vision_result = ResultTextEdit()
        
        self.tab_widget.addTab(self.ocr_result, "OCR結果")
        self.tab_widget.addTab(self.summary_result, "要約結果")
        self.tab_widget.addTab(self.translation_result, "翻訳結果")
        self.tab_widget.addTab(self.vision_result, "画像解説")
        
    def capture_full_screen(self):
        self.hide()
        monitor = self.capture_service.select_monitor(self)
        if monitor is not None:
            QTimer.singleShot(500, lambda: self._do_full_capture(monitor))
        else:
            self.show()
        
    def _do_full_capture(self, monitor=None):
        self.current_image = self.capture_service.capture_full_screen(monitor)
        self.show()
        
        if self.mode_selector.currentText() == "OCRモード":
            self.perform_ocr()
        else:
            self.analyze_image()
        
    def capture_area(self):
        self.hide()
        monitor = self.capture_service.select_monitor(self)
        if monitor is not None:
            QTimer.singleShot(100, lambda: self._show_overlay(monitor))
        else:
            self.show()
        
    def _show_overlay(self, monitor=None):
        self.selected_monitor = monitor
        self.overlay = QWidget()
        self.overlay.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.overlay.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        if monitor:
            self.overlay.setGeometry(
                monitor['left'],
                monitor['top'],
                monitor['width'],
                monitor['height']
            )
        else:
            self.overlay.setGeometry(0, 0, QApplication.primaryScreen().size().width(),
                                    QApplication.primaryScreen().size().height())

        self.start_x = None
        self.start_y = None
        self.current_rect = None

        # 選択範囲を描画するためのキャンバス
        self.canvas = QWidget(self.overlay)
        self.canvas.setGeometry(0, 0, self.overlay.width(), self.overlay.height())
        self.canvas.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # イベントハンドラの設定
        self.canvas.mousePressEvent = self.on_press
        self.canvas.mouseMoveEvent = self.on_drag
        self.canvas.mouseReleaseEvent = self.on_release
        self.canvas.paintEvent = self.on_paint

        self.overlay.show()

    def on_press(self, event):
        self.start_x = event.position().x()
        self.start_y = event.position().y()
        self.current_rect = QRect(
            int(self.start_x),
            int(self.start_y),
            0, 0
        )

    def on_drag(self, event):
        if self.start_x is None or self.start_y is None:
            return
        
        current_x = int(event.position().x())
        current_y = int(event.position().y())
        
        # 選択範囲の更新
        self.current_rect = QRect(
            min(int(self.start_x), current_x),
            min(int(self.start_y), current_y),
            abs(current_x - int(self.start_x)),
            abs(current_y - int(self.start_y))
        )
        
        # 再描画を要求
        self.canvas.update()

    def on_paint(self, event):
        painter = QPainter(self.canvas)
        # 画面全体に薄い灰色の半透明オーバーレイを描画
        painter.fillRect(self.canvas.rect(), QColor(128, 128, 128, 60))

        if self.current_rect:
            # 選択範囲の外側を暗く
            painter.fillRect(0, 0, self.canvas.width(), self.current_rect.top(), QColor(0, 0, 0, 60))
            painter.fillRect(0, self.current_rect.bottom(), self.canvas.width(), self.canvas.height() - self.current_rect.bottom(), QColor(0, 0, 0, 60))
            painter.fillRect(0, self.current_rect.top(), self.current_rect.left(), self.current_rect.height(), QColor(0, 0, 0, 60))
            painter.fillRect(self.current_rect.right(), self.current_rect.top(), self.canvas.width() - self.current_rect.right(), self.current_rect.height(), QColor(0, 0, 0, 60))

            # 選択範囲の境界線を青色で表示
            pen = QPen(QColor(0, 120, 215), 2, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.drawRect(self.current_rect)

    def on_release(self, event):
        if self.start_x is None or self.start_y is None:
            return

        x1 = int(min(self.start_x, event.pos().x()))
        y1 = int(min(self.start_y, event.pos().y()))
        x2 = int(max(self.start_x, event.pos().x()))
        y2 = int(max(self.start_y, event.pos().y()))

        self.overlay.close()

        rect = QRect(x1, y1, x2-x1, y2-y1)
        self._handle_area_capture(rect)

    def _handle_area_capture(self, rect):
        self.current_image = self.capture_service.capture_area(rect, self.selected_monitor)
        self.overlay.close()
        self.overlay = None
        self.show()
        
        if self.mode_selector.currentText() == "OCRモード":
            self.perform_ocr()
        else:
            self.analyze_image()
        
    def perform_ocr(self):
        if not hasattr(self, 'current_image'):
            return
        
        self.show_loading()
        self.status_bar.showMessage("OCR処理中...")
        
        self.current_thread = ProcessingThread(self.ocr_service.perform_ocr, self.current_image)
        self.current_thread.finished.connect(self._handle_ocr_result)
        self.current_thread.start()

    def _handle_ocr_result(self, text):
        self.hide_loading()
        self.ocr_result.setText(text)
        self.tab_widget.setCurrentWidget(self.ocr_result)
        self.status_bar.showMessage("OCR完了", 3000)
        
    def summarize_text(self):
        source_text = self.ocr_result.toPlainText()
        if not source_text:
            QMessageBox.warning(self, "警告", "要約するテキストがありません。")
            return
            
        self.show_loading()
        self.status_bar.showMessage("要約処理中...")
        
        self.current_thread = ProcessingThread(self.summary_service.summarize_text, source_text)
        self.current_thread.finished.connect(self._handle_summary_result)
        self.current_thread.start()

    def _handle_summary_result(self, text):
        self.hide_loading()
        self.summary_result.setText(text)
        self.tab_widget.setCurrentWidget(self.summary_result)
        self.status_bar.showMessage("要約完了", 3000)
        
    def translate_text(self, target_lang=None):
        source_text = self.ocr_result.toPlainText()
        if not source_text:
            QMessageBox.warning(self, "警告", "翻訳するテキストがありません。")
            return
            
        self.show_loading()
        self.status_bar.showMessage("翻訳中...")
        
        self.current_thread = ProcessingThread(self.translation_service.translate_text, source_text)
        self.current_thread.finished.connect(self._handle_translation_result)
        self.current_thread.start()

    def _handle_translation_result(self, text):
        self.hide_loading()
        self.translation_result.setText(text)
        self.tab_widget.setCurrentWidget(self.translation_result)
        self.status_bar.showMessage("翻訳完了", 3000)
        
    def analyze_image(self):
        if not hasattr(self, 'current_image'):
            return
        
        self.show_loading()
        self.status_bar.showMessage("画像解析中...")
        
        self.current_thread = ProcessingThread(self.vision_service.analyze_image, self.current_image)
        self.current_thread.finished.connect(self._handle_vision_result)
        self.current_thread.start()

    def _handle_vision_result(self, text):
        self.hide_loading()
        self.vision_result.setText(text)
        self.tab_widget.setCurrentWidget(self.vision_result)
        self.status_bar.showMessage("解析完了", 3000)

    def show_loading(self):
        if not hasattr(self, 'loading_overlay'):
            self.loading_overlay = LoadingOverlay(self)
        self.loading_overlay.resize(self.size())
        self.loading_overlay.show()

    def hide_loading(self):
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.hide()

    def closeEvent(self, event):
        # アプリケーション終了時の処理
        if hasattr(self, 'current_thread'):
            self.current_thread.quit()
            self.current_thread.wait()
        event.accept()
