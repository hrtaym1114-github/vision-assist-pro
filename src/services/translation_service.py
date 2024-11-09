from openai import OpenAI
import base64
from PIL import Image
import io
import re

class TranslationService:
    def __init__(self, config):
        self.client = OpenAI(api_key=config.openai_api_key)
        self.vision_model = config.vision_model
        self.language_codes = {
            "日本語": "英語",
            "英語": "日本語"
        }

    def detect_language(self, text: str) -> str:
        # 日本語の文字が含まれているかチェック
        if re.search(r'[ぁ-んァ-ン一-龥]', text):
            return "日本語"
        return "英語"

    def translate_text(self, text: str, target_lang: str = None) -> str:
        source_lang = self.detect_language(text)
        target_lang = self.language_codes[source_lang]
        
        response = self.client.chat.completions.create(
            model=self.vision_model,
            messages=[
                {
                    "role": "user",
                    "content": f"以下のテキストを{target_lang}に翻訳してください:\n\n{text}"
                }
            ],
            max_tokens=1000
        )
        
        return response.choices[0].message.content
