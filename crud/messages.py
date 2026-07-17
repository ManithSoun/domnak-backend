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
    latest_by_contact = {}
    unread_by_contact = {}

    for message in res.data or []:
        sender_id = str(message["sender_id"])
        receiver_id = str(message["receiver_id"])
        contact_id = receiver_id if sender_id == user_id else sender_id
        latest_by_contact.setdefault(contact_id, message)
        if receiver_id == user_id and not message.get("is_read", False):
            unread_by_contact[contact_id] = unread_by_contact.get(contact_id, 0) + 1

    contact_ids = list(latest_by_contact)
    profiles = {}
    if contact_ids:
        profile_result = supabase.table("users").select(
            "id,full_name,role"
        ).in_("id", contact_ids).execute()
        profiles = {
            str(profile["id"]): profile
            for profile in (profile_result.data or [])
        }

    return [
        {
            "id": contact_id,
            "name": profiles.get(contact_id, {}).get("full_name") or "Unknown user",
            "role": profiles.get(contact_id, {}).get("role"),
            "last_message": message["content"],
            "last_message_at": message["created_at"],
            "unread_count": unread_by_contact.get(contact_id, 0),
        }
        for contact_id, message in latest_by_contact.items()
    ]

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

def delete_message(message_id: str, user_id: str):
    """Delete a message. Only the sender can delete their own messages."""
    res = supabase.table("messages").delete().eq("id", message_id).eq("sender_id", user_id).execute()
    return res.data

# Quote functions
def create_quote(sender_id: str, receiver_id: str, boq_data: dict, file_name: str = None, area: float = None, total: float = None):
    """Create and send a quote to a client"""
    res = supabase.table("quotes").insert({
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "boq_data": boq_data,
        "file_name": file_name,
        "area": area,
        "total": total,
        "status": "sent"
    }).execute()
    return res.data

def get_quotes(user_id: str):
    """Get all quotes for a user (sent or received)"""
    res = supabase.table("quotes").select("*").or_(
        f"sender_id.eq.{user_id},receiver_id.eq.{user_id}"
    ).order("created_at", desc=True).execute()
    return res.data

def get_quote_by_id(quote_id: str, user_id: str):
    """Get a specific quote if user has access"""
    res = supabase.table("quotes").select("*").eq("id", quote_id).or_(
        f"sender_id.eq.{user_id},receiver_id.eq.{user_id}"
    ).execute()
    return res.data

def update_quote_status(quote_id: str, status: str, user_id: str):
    """Update quote status (accept, reject)"""
    res = supabase.table("quotes").update({
        "status": status
    }).eq("id", quote_id).eq("receiver_id", user_id).execute()
    return res.data
