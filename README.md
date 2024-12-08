# VisionAssist Pro

VisionAssist Proは、OCR、テキスト要約、翻訳、画像解析機能を備えた多機能なデスクトップアプリケーションです。

## 主な機能

- スクリーンキャプチャ機能
  - フルスクリーンキャプチャ
  - エリア選択キャプチャ
- キャプチャした画像の解析機能
  - OCRによるテキスト抽出
  - 画像内容の解析と説明
- 抽出したテキストの加工機能
  - テキスト要約
  - 日英翻訳

## 必要要件

- Python 3.9以上
- Poetry
- OpenAI API キー

## セットアップ

1. リポジトリのクローン:
```bash
git clone https://github.com/hrtaym1114-github/vision-assist-pro.git
cd vision-assist-pro
```

2. Poetryを使用して依存関係をインストール:
```bash
poetry install
```

3. 環境変数の設定:
`.env`ファイルをプロジェクトのルートディレクトリに作成し、以下の内容を設定してください：

```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_VISION_MODEL=gpt-4o
SAVE_DIRECTORY=output
```

## 使用方法

1. アプリケーションの起動:
```bash
poetry run python src/main.py
```

2. 解析モードの選択:
   - 起動時はデフォルトでOCRモードが選択されています
   - 画面上部のトグルボタンで「OCR」と「画像解説」を切り替えることができます

3. キャプチャの取得と解析:
   - フルスクリーンキャプチャボタン：画面全体を撮影して解析
   - エリア選択キャプチャボタン：必要な範囲を選択して撮影・解析
   - OCRモード：テキストを抽出
   - 画像解説モード：画像の内容を説明文として取得

4. テキスト加工（OCRモード時のみ）:
   - 抽出したテキストを選択し、要約ボタンをクリックして内容を要約
   - または翻訳ボタンをクリックして日英翻訳を実行

## ライセンス

MIT License

## 作者

- GitHub: [@hrtaym1114-github](https://github.com/hrtaym1114-github)
