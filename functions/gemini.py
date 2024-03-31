import google.generativeai as gen_ai
from os import getenv


class Gemini:
    __pro_model = gen_ai.GenerativeModel(
        model_name="gemini-pro"
    )

    __generation_config: gen_ai.GenerationConfig = gen_ai.GenerationConfig(
        temperature=0.5,
        max_output_tokens=1024,
    )

    def __init__(self):
        gemini_api_key = getenv('GEMINI_API_KEY')
        gen_ai.configure(api_key=gemini_api_key)

    def generate_content(self, prompt: str):
        return self.__pro_model.generate_content(prompt, generation_config=self.__generation_config)
