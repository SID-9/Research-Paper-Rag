from openai import OpenAI

from app.core.config import settings


class LLMService:

    def __init__(self):

        self.client = OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url=settings.GROQ_BASE_MODEL,
        )

        self.model = settings.GROQ_MODEL

    def generate(
        self,
        prompt: str,
    ) -> str:

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a research paper question "
                        "answering assistant. "
                        "Answer questions only using the "
                        "provided context."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0,
        )

        return response.choices[0].message.content or "" 