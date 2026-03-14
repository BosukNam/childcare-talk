import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageResponse
from app.services.ai_service import get_ai_response, generate_title
from app.services.chat_service import get_conversation_messages, save_message

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/{conversation_id}")
async def send_message(
    conversation_id: str,
    data: MessageCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 본인의 대화인지 확인
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user.id,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다")

    # 사용자 메시지 저장
    await save_message(db, conversation_id, "user", data.content)

    # 대화 이력 로드
    messages = await get_conversation_messages(db, conversation_id)

    # 첫 번째 메시지면 제목 자동 생성
    if len(messages) == 1:
        try:
            title = await generate_title(data.content)
            conversation.title = title
            await db.commit()
        except Exception:
            pass  # 제목 생성 실패해도 대화는 계속

    async def event_stream():
        full_response = []
        sources = []
        try:
            async for event_type, data in get_ai_response(messages):
                if event_type == "chunk":
                    full_response.append(data)
                    yield f"data: {json.dumps({'type': 'chunk', 'content': data}, ensure_ascii=False)}\n\n"
                elif event_type == "sources":
                    sources = data

            # 전체 응답 저장
            assistant_content = "".join(full_response)
            await save_message(db, conversation_id, "assistant", assistant_content)

            # 대화 업데이트 시간 갱신
            conversation.updated_at = datetime.now(timezone.utc)
            await db.commit()

            # grounding sources 전송
            if sources:
                yield f"data: {json.dumps({'type': 'sources', 'sources': sources}, ensure_ascii=False)}\n\n"

            yield f"data: {json.dumps({'type': 'done', 'content': assistant_content}, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/{conversation_id}/sync", response_model=MessageResponse)
async def send_message_sync(
    conversation_id: str,
    data: MessageCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """비스트리밍 버전 (테스트용)"""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user.id,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다")

    await save_message(db, conversation_id, "user", data.content)
    messages = await get_conversation_messages(db, conversation_id)

    full_response = []
    async for event_type, data in get_ai_response(messages, stream=False):
        if event_type == "chunk":
            full_response.append(data)

    assistant_content = "".join(full_response)
    message = await save_message(db, conversation_id, "assistant", assistant_content)

    conversation.updated_at = datetime.now(timezone.utc)
    await db.commit()

    return message
