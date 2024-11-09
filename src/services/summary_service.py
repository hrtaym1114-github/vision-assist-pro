from openai import OpenAI
import base64
from PIL import Image
import io

class SummaryService:
    def __init__(self, config):
        self.client = OpenAI(api_key=config.openai_api_key)
        self.vision_model = config.vision_model

    def image_to_base64(self, image: Image.Image) -> str:
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def summarize_image(self, image: Image.Image) -> str:
        base64_image = self.image_to_base64(image)
        
        response = self.client.chat.completions.create(
            model=self.vision_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "この画像内のテキストを要約してください。"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )
        
        return response.choices[0].message.content

    def summarize_text(self, text: str) -> str:
        response = self.client.chat.completions.create(
            model=self.vision_model,
            messages=[
                {
                    "role": "user",
                    "content": f"以下のテキストを要約してください:\n\n{text}"
                }
            ],
            max_tokens=1000
        )
        
        return response.choices[0].message.content
