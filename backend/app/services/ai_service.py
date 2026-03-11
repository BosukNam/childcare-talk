import anthropic

from app.config import ANTHROPIC_API_KEY
from app.prompts.system_prompt import SYSTEM_PROMPT

client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)


async def get_ai_response(messages: list[dict], stream: bool = True):
    """Claude API를 호출하여 응답을 생성합니다."""
    if stream:
        async with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=messages,
        ) as response:
            async for text in response.text_stream:
                yield text
    else:
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        yield response.content[0].text


async def generate_title(first_message: str) -> str:
    """첫 번째 메시지를 기반으로 대화 제목을 생성합니다."""
    response = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=30,
        messages=[{
            "role": "user",
            "content": f"다음 메시지의 대화 주제를 10자 이내 한국어로 요약해줘. 제목만 출력해: {first_message}",
        }],
    )
    return response.content[0].text.strip()
