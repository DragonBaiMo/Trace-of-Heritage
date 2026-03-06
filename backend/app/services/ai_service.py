"""AI 生成服务，负责调用外部大模型或提供兜底占位实现。"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

import httpx

from app.core.config import settings
from app.utils.exceptions import BusinessException


class AIService:
    """对接大模型的服务封装，便于后续替换供应商。"""

    def __init__(self) -> None:
        self.base_url = settings.ai_base_url
        self.model = settings.ai_model
        self.api_key = settings.ai_api_key
        self.timeout = settings.ai_timeout

    def generate_synopsis_and_tags(self, text: str, expect_length: int = 100) -> Tuple[str, List[str]]:
        """
        根据剧本文本生成简介与标签。

        若未配置密钥或调用失败，则返回本地占位实现，保证流程不被阻断。
        """

        cleaned = (text or "").strip()
        if len(cleaned) < 20:
            raise BusinessException("文本内容过短，无法生成简介，请补充后重试")

        if not self.api_key:
            return self._fallback(cleaned, expect_length)

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": f"请用中文提炼以下戏曲/非遗内容，生成约{expect_length}字简介，并给出3-5个标签（用中文），以JSON返回，结构如：{{\"synopsis\":\"...\",\"tags\":[\"标签1\",\"标签2\"]}}。文本：{cleaned}",
                }
            ],
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(self.base_url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if not content:
                    raise BusinessException("AI 返回内容为空，请稍后重试")
                return self._parse_ai_content(content, cleaned, expect_length)
        except BusinessException:
            raise
        except Exception as exc:
            # 网络或解析异常时，采用本地占位结果，保证提交流程不中断
            return self._fallback(cleaned, expect_length, fallback_reason=str(exc))

    def _parse_ai_content(self, content: str, source: str, expect_length: int) -> Tuple[str, List[str]]:
        """解析大模型返回的 JSON/文本，提取简介与标签。"""

        # 尝试从 JSON 结构解析
        try:
            import json

            parsed = json.loads(content)
            synopsis = (parsed.get("synopsis") or "").strip()
            tags = [t.strip() for t in (parsed.get("tags") or []) if t]
            if synopsis:
                return synopsis[: expect_length + 60], tags[:5] if tags else self._guess_tags(source)
        except Exception:
            pass

        # 兜底：从纯文本中提取
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        synopsis_text = " ".join(lines)[: expect_length + 60] if lines else source[: expect_length + 40]
        return synopsis_text, self._guess_tags(source)

    def _fallback(self, text: str, expect_length: int, fallback_reason: str | None = None) -> Tuple[str, List[str]]:
        """无密钥或调用异常时的本地占位实现。"""

        synopsis = text[: expect_length].replace("\n", " ")
        tags = self._guess_tags(text)
        return synopsis, tags

    def _guess_tags(self, text: str) -> List[str]:
        """简单基于关键词的标签猜测，确保返回非空列表。"""

        keywords = []
        candidates = ["京剧", "豫剧", "昆曲", "评弹", "皮影", "非遗", "传承", "戏曲", "曲艺", "文化"]
        for item in candidates:
            if item in text:
                keywords.append(item)
        if not keywords:
            # 从文本提取前几个名词样式的词
            matches = re.findall(r"[\u4e00-\u9fa5]{2,4}", text[:80])
            keywords = matches[:3] if matches else ["文化", "传承"]
        return keywords[:5]
