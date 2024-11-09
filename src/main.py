import sys
import os
from pathlib import Path

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from PyQt6.QtWidgets import QApplication
from src.gui.main_window import EnhancedOCRTool
from src.utils.config import load_config

def main():
    # 設定の読み込み
    config = load_config()
    
    # アプリケーションの起動
    app = QApplication(sys.argv)
    
    # メインウィンドウの作成と表示
    window = EnhancedOCRTool(config)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
