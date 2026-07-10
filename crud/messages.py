from db.supabase import supabase

def send_message(sender_id: str, receiver_id: str, content: str, quote_id: str = None):
    res = supabase.table("messages").insert({
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "content": content,
        "quote_id": quote_id
    }).execute()
    return res.data

def get_conversation(user_id: str, other_user_id: str):
    res = supabase.table("messages").select("*").or_(
        f"and(sender_id.eq.{user_id},receiver_id.eq.{other_user_id}),"
        f"and(sender_id.eq.{other_user_id},receiver_id.eq.{user_id})"
    ).order("created_at", desc=False).execute()
    return res.data

def get_all_conversations(user_id: str):
    res = supabase.table("messages").select("*").or_(
        f"sender_id.eq.{user_id},receiver_id.eq.{user_id}"
    ).order("created_at", desc=True).execute()
    return res.data

def mark_as_read(message_id: str, user_id: str):
    res = supabase.table("messages").update({
        "is_read": True
    }).eq("id", message_id).eq("receiver_id", user_id).execute()
    return res.data

def get_unread_count(user_id: str):
    res = supabase.table("messages").select("id").eq(
        "receiver_id", user_id
    ).eq("is_read", False).execute()
    return len(res.data)