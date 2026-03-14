import logging

from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY
from app.prompts.system_prompt import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

client = genai.Client(api_key=GEMINI_API_KEY)

MODEL = "gemini-2.5-flash"

# Google Search Grounding 도구
grounding_tool = types.Tool(google_search=types.GoogleSearch())


def _extract_grounding_sources(response_or_chunk) -> list[dict]:
    """응답에서 grounding metadata의 소스 URL을 추출합니다."""
    sources = []
    try:
        candidates = getattr(response_or_chunk, 'candidates', None)
        if not candidates:
            print(f"[grounding-debug] no candidates")
            return sources
        for candidate in candidates:
            metadata = getattr(candidate, 'grounding_metadata', None)
            if not metadata:
                print(f"[grounding-debug] no metadata on candidate")
                continue
            # 디버그: metadata 속성 확인
            print(f"[grounding-debug] metadata type: {type(metadata)}")
            print(f"[grounding-debug] metadata attrs: {[a for a in dir(metadata) if not a.startswith('_')]}")
            chunks = getattr(metadata, 'grounding_chunks', None)
            if not chunks:
                print(f"[grounding-debug] no grounding_chunks, trying search_entry_point...")
                sep = getattr(metadata, 'search_entry_point', None)
                print(f"[grounding-debug] search_entry_point: {bool(sep)}")
                # grounding_supports도 확인
                supports = getattr(metadata, 'grounding_supports', None)
                print(f"[grounding-debug] grounding_supports: {bool(supports)}")
                if supports:
                    print(f"[grounding-debug] supports count: {len(supports)}")
                continue
            print(f"[grounding-debug] grounding_chunks count: {len(chunks)}")
            for gc in chunks:
                web = getattr(gc, 'web', None)
                if web:
                    uri = getattr(web, 'uri', None)
                    title = getattr(web, 'title', '') or uri
                    if uri:
                        sources.append({"title": title, "url": uri})
    except Exception as e:
        print(f"[grounding-debug] 추출 실패: {e}")
    return sources


async def get_ai_response(messages: list[dict], stream: bool = True):
    """Gemini API를 호출하여 응답을 생성합니다.

    yield 형식: ("chunk", text) 또는 ("sources", [{"title": ..., "url": ...}])
    """
    # Anthropic 형식 → Gemini 형식 변환
    gemini_messages = []
    for msg in messages:
        role = "model" if msg["role"] == "assistant" else "user"
        gemini_messages.append({"role": role, "parts": [{"text": msg["content"]}]})

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        max_output_tokens=2048,
        tools=[grounding_tool],
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    )

    if stream:
        response = client.models.generate_content_stream(
            model=MODEL,
            contents=gemini_messages,
            config=config,
        )
        all_chunks = []
        for chunk in response:
            all_chunks.append(chunk)
            if chunk.text:
                yield ("chunk", chunk.text)

        # 모든 chunk에서 grounding sources 추출 (뒤에서부터 탐색)
        sources = []
        for chunk in reversed(all_chunks):
            sources = _extract_grounding_sources(chunk)
            if sources:
                break
        # 중복 제거 + 최대 5개
        seen = set()
        unique_sources = []
        for s in sources:
            if s["url"] not in seen:
                seen.add(s["url"])
                unique_sources.append(s)
            if len(unique_sources) >= 5:
                break
        print(f"[grounding] sources: {len(unique_sources)}/{len(sources)}, chunks: {len(all_chunks)}")
        if unique_sources:
            yield ("sources", unique_sources)
    else:
        response = client.models.generate_content(
            model=MODEL,
            contents=gemini_messages,
            config=config,
        )
        yield ("chunk", response.text)

        sources = _extract_grounding_sources(response)
        print(f"[grounding] sources 수 (non-stream): {len(sources)}")
        if sources:
            yield ("sources", sources)


async def generate_title(first_message: str) -> str:
    """첫 번째 메시지를 기반으로 대화 제목을 생성합니다."""
    response = client.models.generate_content(
        model=MODEL,
        contents=f"다음 메시지의 대화 주제를 10자 이내 한국어로 요약해줘. 제목만 출력해: {first_message}",
        config=genai.types.GenerateContentConfig(
            max_output_tokens=30,
            thinking_config=genai.types.ThinkingConfig(thinking_budget=0),
        ),
    )
    return response.text.strip()
