from fastapi import APIRouter, HTTPException

from backend.api.deps.repositories import message_repo
from backend.models.schemas import MessageBatchIn, MessageIn, MessageOut

router = APIRouter()


@router.post("", response_model=MessageOut)
def create_message(payload: MessageIn) -> MessageOut:
    return message_repo.create(payload)


@router.post("/batch", response_model=list[MessageOut])
def create_messages_batch(payload: MessageBatchIn) -> list[MessageOut]:
    return message_repo.batch_create(payload.messages)


@router.get("/{message_id}", response_model=MessageOut)
def get_message(message_id: int) -> MessageOut:
    item = message_repo.get(message_id)
    if not item:
        raise HTTPException(status_code=404, detail="message not found")
    return item
