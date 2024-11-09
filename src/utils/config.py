import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEYが設定されていません。")
        
        self.save_directory = os.getenv('SAVE_DIRECTORY', 'output')
        
        self.vision_model = os.getenv('OPENAI_VISION_MODEL', 'gpt-4o')
        
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)

def load_config() -> Config:
    return Config()
