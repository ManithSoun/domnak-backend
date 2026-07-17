from uuid import UUID

from fastapi import APIRouter, Depends, status
from db.supabase import supabase
from models.messages import MessageRequest
from core.auth import get_current_user
import crud.messages as message_crud
from utils.response import success, error
from core.logging import logger

router = APIRouter()

def get_user_id(current_user):
    return current_user.id if hasattr(current_user, 'id') else current_user["id"]

def are_users_connected(user_id: str, other_user_id: str) -> bool:
    """Check if two users are connected (accepted connection in either direction)"""
    result = supabase.table("connections").select("id").or_(
        f"and(inviter_id.eq.{user_id},invitee_id.eq.{other_user_id},status.eq.accepted),"
        f"and(inviter_id.eq.{other_user_id},invitee_id.eq.{user_id},status.eq.accepted)"
    ).execute()
    return len(result.data or []) > 0
  
@router.post("/", status_code=status.HTTP_201_CREATED)
def send_message(data: MessageRequest, current_user=Depends(get_current_user)):
    try:
        user_id = str(get_user_id(current_user))
        receiver_id = str(data.receiver_id)
        if receiver_id == user_id:
            return error(message="Cannot send message to yourself", status_code=400)

        # Check if users are connected
        if not are_users_connected(user_id, receiver_id):
            logger.warning(f"Users not connected. Sender: {user_id}, Receiver: {receiver_id}")
            return error(message="You can only message connected users. Please connect first.", status_code=403)

        # Note: We don't require recipients to be in the users table because
        # Supabase Auth users may not have a profile entry yet.
        # The connection check above is sufficient.

        result = message_crud.send_message(
            sender_id=user_id,
            receiver_id=receiver_id,
            content=data.content,
            quote_id=str(data.quote_id) if data.quote_id else None,
        )
        return success(data=result, status_code=status.HTTP_201_CREATED)
    except Exception as e:
        import traceback
        logger.error(f"Failed to send message: {str(e)}\n{traceback.format_exc()}")
        return error(message=str(e), status_code=500)
  
@router.get("/conversations")
def get_all_conversations(current_user = Depends(get_current_user)):
  try: 
    user_id = get_user_id(current_user)
    result = message_crud.get_all_conversations(user_id)
    # Filter to only include connected users
    connected_contacts = get_connected_contact_ids(user_id)
    filtered = [c for c in result if c["id"] in connected_contacts]
    return success(data=filtered)
  except Exception as e:
      logger.error(f"Conversations error: {str(e)}")
      return error(message=str(e), status_code=500)

def get_connected_contact_ids(user_id: str) -> set:
    """Get set of user IDs that the current user is connected with"""
    result = supabase.table("connections").select("inviter_id, invitee_id").eq("status", "accepted").execute()
    connected = set()
    for conn in (result.data or []):
        if str(conn.get("inviter_id")) == user_id:
            connected.add(str(conn.get("invitee_id")))
        elif str(conn.get("invitee_id")) == user_id:
            connected.add(str(conn.get("inviter_id")))
    return connected
  
@router.get("/unread")
def get_unread_count(current_user = Depends(get_current_user)):
  try: 
    user_id = get_user_id(current_user)
    count = message_crud.get_unread_count(user_id)
    return success(data={"unread_count": count})
  except Exception as e:
    return error(message=str(e), status_code=500)

@router.get("/{other_user_id}")
def get_conversation(other_user_id: UUID, current_user=Depends(get_current_user)):
  try:
    user_id = str(get_user_id(current_user))
    contact_id = str(other_user_id)
    if contact_id == user_id:
        return error(message="Cannot open a conversation with yourself", status_code=400)
    
    # Check if users are connected
    if not are_users_connected(user_id, contact_id):
        return error(message="You can only view conversations with connected users.", status_code=403)
    
    result = message_crud.get_conversation(user_id, contact_id)
    return success(data=result)

  except Exception as e:
    import traceback
    logger.error(f"Get conversation error: {str(e)}\n{traceback.format_exc()}")
    return error(message=str(e), status_code=500)
  
@router.patch("/{message_id}/read")
def mark_as_read(message_id: UUID, current_user=Depends(get_current_user)):
  try:
    user_id = get_user_id(current_user)
    result = message_crud.mark_as_read(str(message_id), str(user_id))
    if not result:
        return error(message="Unread message not found", status_code=404)
    return success(data=result[0], message="Message marked as read")
  except Exception as e:
    return error(message=str(e), status_code=500)

@router.delete("/{message_id}")
def delete_message(message_id: UUID, current_user=Depends(get_current_user)):
  """Delete a message (only sender can delete their own messages)"""
  try:
    user_id = get_user_id(current_user)
    result = message_crud.delete_message(str(message_id), str(user_id))
    if not result:
        return error(message="Message not found or you don't have permission to delete it", status_code=404)
    return success(data=result[0], message="Message deleted")
  except Exception as e:
    return error(message=str(e), status_code=500)
