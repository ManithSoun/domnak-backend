from fastapi import APIRouter, Depends
from db.supabase import supabase
from models.messages import MessageRequest
from core.auth import get_current_user, security
import crud.messages as message_crud
from utils.response import success, error
from core.logging import logger
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()

def get_user_id(current_user):
    return current_user.id if hasattr(current_user, 'id') else current_user["id"]
  
@router.post("/")
def send_message(data: MessageRequest, current_user = Depends(get_current_user), credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        user_id = current_user.id if hasattr(current_user, 'id') else current_user["id"]
        print(f"SEND MESSAGE DEBUG: sender={user_id}, receiver={data.receiver_id}, content={data.content}")
        if data.receiver_id == user_id:
            return error(message="Cannot send message to yourself", status_code=400)

        result = message_crud.send_message(
            sender_id=user_id,
            receiver_id=data.receiver_id,
            content=data.content,
            quote_id=data.quote_id,
        )
        return success(data=result)
    except Exception as e:
        logger.error(f"Failed to send message: {str(e)}")
        return error(message=str(e), status_code=500)
  
@router.get("/conversations")
def get_all_conversations(current_user = Depends(get_current_user)):
  try: 
    user_id = get_user_id(current_user)
    result = message_crud.get_all_conversations(user_id)
    return success(data=result)
  except Exception as e:
      logger.error(f"Conversations error: {str(e)}")
      return error(message=str(e), status_code=500)
  
@router.get("/unread")
def get_unread_count(current_user = Depends(get_current_user)):
  try: 
    user_id = get_user_id(current_user)
    count = message_crud.get_unread_count(user_id)
    return success(data={"unread_count": count})
  except Exception as e:
    return error(message=str(e), status_code=500)

@router.get("/{other_user_id}")
def get_conversation(other_user_id: str, current_user = Depends(get_current_user)):
  try:
    user_id = get_user_id(current_user)
    result = message_crud.get_conversation(user_id, other_user_id)
    return success(data=result)

  except Exception as e:
    return error(message=str(e), status_code=500)
  
@router.patch("/{message_id}/read")
def mark_as_read(message_id: str, current_user = Depends(get_current_user)):
  try:
    user_id = get_user_id(current_user)
    result = message_crud.mark_as_read(message_id, user_id)
    return success(message="Message marked as read")
  except Exception as e:
    return error(message=str(e), status_code=500)