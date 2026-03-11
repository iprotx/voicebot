from fastapi import APIRouter, Depends, HTTPException

from backend.api.deps.repositories import get_message_repo
from backend.models.schemas import MessageBatchIn, MessageIn, MessageOut
from backend.storage.repositories import MessageRepository

router = APIRouter()


@router.post("", response_model=MessageOut)
async def create_message(payload: MessageIn, repo: MessageRepository = Depends(get_message_repo)) -> MessageOut:
    return await repo.create(payload)


@router.post("/batch", response_model=list[MessageOut])
async def create_messages_batch(
    payload: MessageBatchIn, repo: MessageRepository = Depends(get_message_repo)
) -> list[MessageOut]:
    return await repo.batch_create(payload.messages)


@router.get("/{message_id}", response_model=MessageOut)
async def get_message(message_id: int, repo: MessageRepository = Depends(get_message_repo)) -> MessageOut:
    item = await repo.get(message_id)
    if not item:
        raise HTTPException(status_code=404, detail="message not found")
    return item
