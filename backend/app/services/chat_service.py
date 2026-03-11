from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.models.message import Message


async def get_conversation_messages(db: AsyncSession, conversation_id: str, limit: int = 50) -> list[dict]:
    """대화의 최근 메시지를 Claude API 형식으로 반환합니다."""
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = result.scalars().all()
    messages.reverse()

    return [{"role": m.role, "content": m.content} for m in messages]


async def save_message(db: AsyncSession, conversation_id: str, role: str, content: str) -> Message:
    """메시지를 저장합니다."""
    message = Message(conversation_id=conversation_id, role=role, content=content)
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def get_user_conversations(db: AsyncSession, user_id: str) -> list[Conversation]:
    """사용자의 대화 목록을 반환합니다."""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    return list(result.scalars().all())


async def create_conversation(db: AsyncSession, user_id: str, title: str = "새 대화") -> Conversation:
    """새 대화를 생성합니다."""
    conversation = Conversation(user_id=user_id, title=title)
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return conversation
