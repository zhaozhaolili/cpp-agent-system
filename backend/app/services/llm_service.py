import json
import httpx
from typing import AsyncGenerator, List, Dict
from app.core.config import settings

class LLMService:
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.model = settings.DEEPSEEK_MODEL

    async def stream_chat(self, messages: List[Dict]) -> AsyncGenerator[str, None]:
        if not self.api_key:
            yield "错误：未配置 DeepSeek API Key"
            return

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": True,
                        "temperature": 0.7,
                        "max_tokens": 2048
                    }
                )

                buffer = ""
                async for chunk_bytes in response.aiter_bytes():
                    try:
                        chunk_text = chunk_bytes.decode('utf-8')
                        buffer += chunk_text
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            line = line.strip()
                            if line.startswith("data: "):
                                data = line[6:]
                                if data == "[DONE]":
                                    break
                                try:
                                    chunk = json.loads(data)
                                    if "choices" in chunk:
                                        delta = chunk["choices"][0].get("delta", {})
                                        content = delta.get("content", "")
                                        if content:
                                            yield content
                                except json.JSONDecodeError:
                                    continue
                    except UnicodeDecodeError:
                        continue

            except Exception as e:
                yield f"错误: {str(e)}"

    async def chat(self, messages: List[Dict]) -> str:
        if not self.api_key:
            return "错误：未配置 DeepSeek API Key"

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                        "temperature": 0.3,
                        "max_tokens": 4096
                    }
                )
                data = response.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "")
            except Exception as e:
                return f"错误: {str(e)}"

llm_service = LLMService()