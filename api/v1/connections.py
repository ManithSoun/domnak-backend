from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from db.supabase import supabase
from config import settings
from core.auth import get_current_user
from utils.response import success, error
from typing import Optional, List
import logging

logger = logging.getLogger("domnak")
import uuid

router = APIRouter()

class InviteRequest(BaseModel):
    email: EmailStr
    message: Optional[str] = None

class InviteResponse(BaseModel):
    id: str
    inviter_id: str
    inviter_name: str
    invitee_email: str
    status: str
    created_at: str

class AcceptRequest(BaseModel):
    invite_id: str

@router.post("/invite")
def send_invite(request: InviteRequest, current_user = Depends(get_current_user)):
    """Send an invitation to connect (architect -> homeowner)"""
    try:
        inviter_id = current_user.id
        inviter_email = current_user.email
        inviter_name = current_user.full_name or inviter_email.split("@")[0]
        invitee_email = request.email.lower().strip()

        if invitee_email == inviter_email:
            return error(message="You cannot invite yourself", status_code=400)

        # Find the user by email in the users table
        user_result = supabase.table("users").select("id, email, role").eq("email", invitee_email).execute()
        invitee_user = None
        if not user_result.data:
            # Try to sync from auth if email not in users table
            import traceback
            try:
                auth_users = supabase.auth.admin.list_users()
                for u in auth_users.users:
                    if u.email.lower() == invitee_email:
                        # Update users table with email
                        supabase.table("users").update({"email": u.email}).eq("id", u.id).execute()
                        user_result = supabase.table("users").select("id, email, role").eq("email", invitee_email).execute()
                        break
            except Exception as sync_err:
                print(f"Auth sync failed: {sync_err}")
                traceback.print_exc()
        
        if user_result.data:
            invitee_user = type('obj', (object,), {
                'id': user_result.data[0]['id'],
                'email': user_result.data[0]['email'],
                'user_metadata': {'role': user_result.data[0].get('role', 'homeowner')}
            })

        if not invitee_user:
            return error(message="No user found with this email. They must sign up first.", status_code=404)

        invitee_role = invitee_user.user_metadata.get("role", "homeowner")
        if invitee_role in ["architect", "contractor"]:
            return error(message="Can only invite homeowners", status_code=400)

        # Check if already connected (now we accept directly, so check for any accepted)
        existing_connected = supabase.table("connections").select("*").eq("inviter_id", inviter_id).eq("invitee_id", invitee_user.id).eq("status", "accepted").execute()
        if existing_connected.data:
            return error(message="Already connected with this user", status_code=409)

        # Create connection directly as "accepted" - no email waiting needed
        connection_record = {
            "inviter_id": inviter_id,
            "inviter_name": inviter_name,
            "inviter_email": inviter_email,
            "invitee_id": invitee_user.id,
            "invitee_email": invitee_email,
            "status": "accepted"
        }

        result = supabase.table("connections").insert(connection_record).execute()

        # Create notification for the homeowner
        notification = {
            "user_id": invitee_user.id,
            "type": "connection_request",
            "title": "New Connection",
            "message": f"{inviter_name} ({inviter_email}) wants to connect with you",
            "data": {
                "connection_id": result.data[0]["id"] if result.data else None,
                "inviter_id": inviter_id,
                "inviter_name": inviter_name,
                "inviter_email": inviter_email
            }
        }
        try:
            supabase.table("notifications").insert(notification).execute()
        except:
            pass  # notifications table might not exist yet

        return success(data={
            "connection_id": result.data[0]["id"] if result.data else None,
            "invitee_email": invitee_email,
            "status": "accepted",
            "message": f"Connected with {invitee_email} successfully"
        })

    except Exception as e:
        import traceback; traceback.print_exc()
        return error(message=str(e), status_code=500)


@router.get("/")
def list_connections(current_user = Depends(get_current_user)):
    """List all connections and pending invites"""
    print("=== LIST_CONNECTIONS: User authenticated:", current_user.id if current_user else "NONE")
    try:
        user_id = current_user.id

        # Get accepted connections
        sent = supabase.table("connections").select("*").eq("inviter_id", user_id).eq("status", "accepted").execute()
        received = supabase.table("connections").select("*").eq("invitee_id", user_id).eq("status", "accepted").execute()

        # Get pending invites (sent by me or received by me)
        pending_sent = supabase.table("connections").select("*").eq("inviter_id", user_id).eq("status", "pending").execute()
        pending_received = supabase.table("connections").select("*").eq("invitee_id", user_id).eq("status", "pending").execute()

        contacts = []
        for conn in sent.data:
            contacts.append({
                "id": conn["id"],
                "user_id": conn["invitee_id"],
                "user_email": conn["invitee_email"],
                "user_name": conn.get("invitee_name", conn["invitee_email"].split("@")[0]),
                "connected_at": conn.get("updated_at", conn.get("created_at")),
                "direction": "sent"
            })
        for conn in received.data:
            contacts.append({
                "id": conn["id"],
                "user_id": conn["inviter_id"],
                "user_email": conn["inviter_email"],
                "user_name": conn.get("inviter_name", conn["inviter_email"].split("@")[0]),
                "connected_at": conn.get("updated_at", conn.get("created_at")),
                "direction": "received"
            })

        pending_invites = []
        for conn in pending_sent.data:
            pending_invites.append({
                "id": conn["id"],
                "invitee_email": conn["invitee_email"],
                "invitee_name": conn.get("invitee_name", conn["invitee_email"].split("@")[0]),
                "status": "pending",
                "direction": "sent",
                "created_at": conn.get("created_at")
            })
        for conn in pending_received.data:
            pending_invites.append({
                "id": conn["id"],
                "inviter_email": conn["inviter_email"],
                "inviter_name": conn.get("inviter_name", conn["inviter_email"].split("@")[0]),
                "status": "pending",
                "direction": "received",
                "created_at": conn.get("created_at")
            })

        return success(data={
            "contacts": contacts,
            "pending_invites": pending_invites
        })

    except Exception as e:
        return error(message=str(e), status_code=500)


@router.post("/accept")
def accept_invite(request: AcceptRequest, current_user = Depends(get_current_user)):
    """Accept a connection invitation"""
    try:
        user_id = current_user.id

        # Find the pending invite
        invite = supabase.table("connections").select("*").eq("id", request.invite_id).eq("invitee_id", user_id).eq("status", "pending").execute()
        if not invite.data:
            return error(message="Invite not found or already processed", status_code=404)

        supabase.table("connections").update({"status": "accepted"}).eq("id", request.invite_id).execute()

        return success(message="Connection accepted!")

    except Exception as e:
        return error(message=str(e), status_code=500)


@router.post("/reject")
def reject_invite(request: AcceptRequest, current_user = Depends(get_current_user)):
    """Reject a connection invitation"""
    try:
        user_id = current_user.id

        invite = supabase.table("connections").select("*").eq("id", request.invite_id).eq("invitee_id", user_id).eq("status", "pending").execute()
        if not invite.data:
            return error(message="Invite not found or already processed", status_code=404)

        supabase.table("connections").update({"status": "rejected"}).eq("id", request.invite_id).execute()

        return success(message="Invitation rejected")

    except Exception as e:
        return error(message=str(e), status_code=500)


@router.get("/contacts")
def list_contacts(current_user = Depends(get_current_user)):
    """List all connected contacts (people you can message)"""
    try:
        user_id = current_user.id

        sent = supabase.table("connections").select("*").eq("inviter_id", user_id).eq("status", "accepted").execute()
        received = supabase.table("connections").select("*").eq("invitee_id", user_id).eq("status", "accepted").execute()

        contacts = []
        for conn in sent.data:
            contacts.append({
                "user_id": conn["invitee_id"],
                "user_email": conn["invitee_email"],
                "user_name": conn.get("invitee_name", conn["invitee_email"].split("@")[0]),
                "connected_at": conn.get("updated_at", conn.get("created_at"))
            })
        for conn in received.data:
            contacts.append({
                "user_id": conn["inviter_id"],
                "user_email": conn["inviter_email"],
                "user_name": conn.get("inviter_name", conn["inviter_email"].split("@")[0]),
                "connected_at": conn.get("updated_at", conn.get("created_at"))
            })

        return success(data=contacts)

    except Exception as e:
        import traceback
        logger.error(f"Contacts error: {str(e)}\n{traceback.format_exc()}")
        return error(message=str(e), status_code=500)


@router.post("/accept-token")
def accept_invite_by_token(token: str, current_user = Depends(get_current_user)):
    """Accept a connection using invite token (for share link flow)"""
    try:
        user_id = current_user.id

        invite = supabase.table("connections").select("*").eq("invite_token", token).eq("invitee_id", user_id).eq("status", "pending").execute()
        if not invite.data:
            return error(message="Invalid or expired invite link", status_code=404)

        supabase.table("connections").update({"status": "accepted"}).eq("id", invite.data[0]["id"]).execute()

        inviter_name = invite.data[0].get("inviter_name", "Architect")

        return success(message=f"Connected with {inviter_name}!")

    except Exception as e:
        return error(message=str(e), status_code=500)


@router.get("/my-share-link")
def get_my_share_link(current_user = Depends(get_current_user)):
    """Get the current user's share link. Creates one if it doesn't exist."""
    try:
        user_id = current_user.id
        user_email = current_user.email
        user_name = current_user.full_name or user_email.split("@")[0]

        # Check if a share link already exists for this user (as invitee, since architect sends to homeowner)
        existing = supabase.table("connections").select("*").eq("invitee_id", user_id).execute()
        existing_pending = [c for c in (existing.data or []) if c.get("status") == "pending"]
        
        if existing_pending:
            # Return the token from any pending invite
            token = existing_pending[0].get("invite_token")
            if token:
                share_link = f"https://domnak.vercel.app/connect?token={token}"
                return success(data={"share_link": share_link, "token": token})

        # No share link exists - create one
        # For the homeowner share link flow, the homeowner is the "invitee" and the architect will be the "inviter"
        # But we need a token that the homeowner can share. Let's create a special "outgoing invite" from homeowner
        # This is a connection where homeowner is inviter and architect is invitee (reverse of normal flow)
        
        # Create a new connection record where homeowner invites architect (for share link)
        invite_token = str(uuid.uuid4())[:12]
        record = {
            "inviter_id": user_id,
            "inviter_name": user_name,
            "inviter_email": user_email,
            "invitee_email": "",  # To be filled when architect uses the link
            "status": "pending",
            "invite_token": invite_token,
            "message": "Homeowner shared their profile"
        }
        result = supabase.table("connections").insert(record).execute()
        
        share_link = f"https://domnak.vercel.app/connect?token={invite_token}"
        return success(data={"share_link": share_link, "token": invite_token})

    except Exception as e:
        return error(message=str(e), status_code=500)


@router.get("/notifications")
def get_notifications(current_user = Depends(get_current_user)):
    """Get all notifications for the current user"""
    try:
        user_id = current_user.id
        result = supabase.table("notifications").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return success(data=result.data or [])
    except Exception as e:
        return error(message=str(e), status_code=500)


@router.post("/notifications/{notification_id}/read")
def mark_notification_read(notification_id: str, current_user = Depends(get_current_user)):
    """Mark a notification as read"""
    try:
        supabase.table("notifications").update({"read": True}).eq("id", notification_id).execute()
        return success(data={"message": "Notification marked as read"})
    except Exception as e:
        return error(message=str(e), status_code=500)
