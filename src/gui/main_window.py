from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QToolBar, 
                            QStatusBar, QMenuBar, QMenu, QMessageBox, QTabWidget,
                            QApplication, QComboBox, QHBoxLayout)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt, QTimer, QRect
from .capture_overlay import CaptureOverlay
from src.gui.widgets import ResultTextEdit
from ..services.capture_service import CaptureService
from ..services.ocr_service import OCRService
from ..services.translation_service import TranslationService
from ..services.summary_service import SummaryService
from ..services.vision_service import VisionService

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
        vision_mode_action.triggered.connect(lambda: self.mode_selector.setCurrentText("画像解説モード"))
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
        QTimer.singleShot(500, self._do_full_capture)
        
    def _do_full_capture(self):
        self.current_image = self.capture_service.capture_full_screen()
        self.show()
        
        # モードに応じて適切な処理を実行
        if self.mode_selector.currentText() == "OCRモード":
            self.perform_ocr()
        else:
            self.analyze_image()
        
    def capture_area(self):
        self.hide()
        QTimer.singleShot(100, self._show_overlay)
        
    def _show_overlay(self):
        self.overlay = QWidget()
        self.overlay.setWindowOpacity(0.3)
        self.overlay.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.overlay.setGeometry(0, 0, QApplication.primaryScreen().size().width(),
                                QApplication.primaryScreen().size().height())

        self.start_x = None
        self.start_y = None
        self.current_rect = None

        self.canvas = QWidget(self.overlay)
        self.canvas.setGeometry(0, 0, self.overlay.width(), self.overlay.height())
        self.canvas.setAutoFillBackground(True)
        self.canvas.setStyleSheet("background-color: transparent;")

        self.canvas.mousePressEvent = self.on_press
        self.canvas.mouseMoveEvent = self.on_drag
        self.canvas.mouseReleaseEvent = self.on_release

        self.overlay.show()

    def on_press(self, event):
        self.start_x = event.position().x()
        self.start_y = event.position().y()

    def on_drag(self, event):
        if not hasattr(self, 'start_x') or not hasattr(self, 'start_y'):
            return
        
        current_x = event.position().x()
        current_y = event.position().y()
        
        self.canvas.setStyleSheet("background-color: rgba(255, 0, 0, 0.3);")
        self.canvas.update()

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
        self.current_image = self.capture_service.capture_area(rect)
        self.overlay.close()
        self.overlay = None
        self.show()
        
        # モードに応じて適切な処理を実行
        if self.mode_selector.currentText() == "OCRモード":
            self.perform_ocr()
        else:
            self.analyze_image()
        
    def perform_ocr(self):
        if not hasattr(self, 'current_image'):
            return
        
        self.status_bar.showMessage("OCR処理中...")
        text = self.ocr_service.perform_ocr(self.current_image)
        self.ocr_result.setText(text)
        self.tab_widget.setCurrentWidget(self.ocr_result)
        self.status_bar.showMessage("OCR完了", 3000)
        
    def summarize_text(self):
        source_text = self.ocr_result.toPlainText()
        if not source_text:
            QMessageBox.warning(self, "警告", "要約するテキストがありません。")
            return
            
        self.status_bar.showMessage("要約処理中...")
        text = self.summary_service.summarize_text(source_text)
        self.summary_result.setText(text)
        self.tab_widget.setCurrentWidget(self.summary_result)
        self.status_bar.showMessage("要約完了", 3000)
        
    def translate_text(self, target_lang=None):
        source_text = self.ocr_result.toPlainText()
        if not source_text:
            QMessageBox.warning(self, "警告", "翻訳するテキストがありません。")
            return
            
        self.status_bar.showMessage("翻訳中...")
        text = self.translation_service.translate_text(source_text)
        self.translation_result.setText(text)
        self.tab_widget.setCurrentWidget(self.translation_result)
        self.status_bar.showMessage("翻訳完了", 3000)
        
    def analyze_image(self):
        if not hasattr(self, 'current_image'):
            return
                
        self.status_bar.showMessage("画像解析中...")
        text = self.vision_service.analyze_image(self.current_image)
        self.vision_result.setText(text)
        self.tab_widget.setCurrentWidget(self.vision_result)
        self.status_bar.showMessage("解析完了", 3000)
