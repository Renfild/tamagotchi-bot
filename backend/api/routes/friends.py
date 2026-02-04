"""
Friends API routes.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.user import User
from models.friend import Friend, FriendStatus
from api.routes.auth import get_current_user

router = APIRouter()


class FriendRequest(BaseModel):
    """Friend request."""
    friend_id: int
    message: str = ""


@router.get("")
async def get_friends(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> List[dict]:
    """Get user's friends."""
    friends = []
    
    for f in current_user.friends_sent:
        if f.status == FriendStatus.ACCEPTED:
            friends.append({
                "id": f.friend_id,
                "username": f.friend.username if f.friend else None,
                "first_name": f.friend.first_name if f.friend else None,
                "since": f.created_at.isoformat() if f.created_at else None,
            })
    
    for f in current_user.friends_received:
        if f.status == FriendStatus.ACCEPTED:
            friends.append({
                "id": f.user_id,
                "username": f.user.username if f.user else None,
                "first_name": f.user.first_name if f.user else None,
                "since": f.created_at.isoformat() if f.created_at else None,
            })
    
    return friends


@router.get("/requests")
async def get_friend_requests(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> List[dict]:
    """Get pending friend requests."""
    requests = []
    
    for f in current_user.friends_received:
        if f.status == FriendStatus.PENDING:
            requests.append({
                "id": f.id,
                "from_id": f.user_id,
                "username": f.user.username if f.user else None,
                "first_name": f.user.first_name if f.user else None,
                "message": f.message,
                "sent_at": f.created_at.isoformat() if f.created_at else None,
            })
    
    return requests


@router.post("/request")
async def send_friend_request(
    request: FriendRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Send friend request."""
    # Check if already friends
    result = await session.execute(
        select(Friend).where(
            ((Friend.user_id == current_user.id) & (Friend.friend_id == request.friend_id)) |
            ((Friend.user_id == request.friend_id) & (Friend.friend_id == current_user.id))
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already friends or request pending")
    
    # Create friend request
    friend_request = Friend(
        user_id=current_user.id,
        friend_id=request.friend_id,
        initiated_by=current_user.id,
        message=request.message,
    )
    session.add(friend_request)
    await session.commit()
    
    return {"success": True, "request_id": friend_request.id}


@router.post("/accept/{request_id}")
async def accept_friend_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Accept friend request."""
    result = await session.execute(
        select(Friend).where(Friend.id == request_id, Friend.friend_id == current_user.id)
    )
    friend_request = result.scalar_one_or_none()
    
    if not friend_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if friend_request.status != FriendStatus.PENDING:
        raise HTTPException(status_code=400, detail="Request already processed")
    
    friend_request.accept()
    await session.commit()
    
    return {"success": True}


@router.post("/decline/{request_id}")
async def decline_friend_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Decline friend request."""
    result = await session.execute(
        select(Friend).where(Friend.id == request_id, Friend.friend_id == current_user.id)
    )
    friend_request = result.scalar_one_or_none()
    
    if not friend_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    friend_request.decline()
    await session.commit()
    
    return {"success": True}
