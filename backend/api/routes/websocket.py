"""
WebSocket routes for real-time updates.
"""
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio

router = APIRouter()

# Store active connections
class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.battle_rooms: Dict[int, Set[int]] = {}
    
    async def connect(self, user_id: int, websocket: WebSocket):
        """Connect a user."""
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    def disconnect(self, user_id: int):
        """Disconnect a user."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        # Remove from battle rooms
        for room in self.battle_rooms.values():
            room.discard(user_id)
    
    async def send_to_user(self, user_id: int, message: dict):
        """Send message to specific user."""
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)
    
    async def broadcast_to_battle(self, battle_id: int, message: dict):
        """Broadcast message to battle room."""
        if battle_id in self.battle_rooms:
            for user_id in self.battle_rooms[battle_id]:
                await self.send_to_user(user_id, message)
    
    def join_battle(self, user_id: int, battle_id: int):
        """Join a battle room."""
        if battle_id not in self.battle_rooms:
            self.battle_rooms[battle_id] = set()
        self.battle_rooms[battle_id].add(user_id)
    
    def leave_battle(self, user_id: int, battle_id: int):
        """Leave a battle room."""
        if battle_id in self.battle_rooms:
            self.battle_rooms[battle_id].discard(user_id)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint."""
    await websocket.accept()
    
    try:
        # Wait for authentication
        auth_data = await websocket.receive_json()
        token = auth_data.get("token")
        user_id = auth_data.get("user_id")
        
        if not token or not user_id:
            await websocket.send_json({"error": "Authentication required"})
            await websocket.close()
            return
        
        # Verify token (simplified - implement proper JWT verification)
        # ...
        
        # Register connection
        await manager.connect(user_id, websocket)
        
        await websocket.send_json({"type": "connected", "user_id": user_id})
        
        # Handle messages
        while True:
            try:
                data = await websocket.receive_json()
                message_type = data.get("type")
                
                if message_type == "ping":
                    await websocket.send_json({"type": "pong"})
                
                elif message_type == "subscribe_pet":
                    # Subscribe to pet updates
                    pet_id = data.get("pet_id")
                    await websocket.send_json({
                        "type": "subscribed",
                        "channel": f"pet:{pet_id}",
                    })
                
                elif message_type == "join_battle":
                    # Join battle room
                    battle_id = data.get("battle_id")
                    manager.join_battle(user_id, battle_id)
                    await websocket.send_json({
                        "type": "joined_battle",
                        "battle_id": battle_id,
                    })
                
                elif message_type == "battle_move":
                    # Forward battle move
                    battle_id = data.get("battle_id")
                    await manager.broadcast_to_battle(battle_id, {
                        "type": "battle_move",
                        "user_id": user_id,
                        "move": data.get("move"),
                    })
                
                elif message_type == "leave_battle":
                    battle_id = data.get("battle_id")
                    manager.leave_battle(user_id, battle_id)
                
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON"})
            
    except WebSocketDisconnect:
        if user_id:
            manager.disconnect(user_id)
    except Exception as e:
        if user_id:
            manager.disconnect(user_id)
        raise


async def notify_pet_update(user_id: int, pet_data: dict):
    """Notify user about pet update."""
    await manager.send_to_user(user_id, {
        "type": "pet_update",
        "data": pet_data,
    })


async def notify_battle_update(battle_id: int, battle_data: dict):
    """Notify battle participants about update."""
    await manager.broadcast_to_battle(battle_id, {
        "type": "battle_update",
        "data": battle_data,
    })


async def notify_quest_completed(user_id: int, quest_data: dict):
    """Notify user about quest completion."""
    await manager.send_to_user(user_id, {
        "type": "quest_completed",
        "data": quest_data,
    })


async def notify_achievement_unlocked(user_id: int, achievement_data: dict):
    """Notify user about achievement unlock."""
    await manager.send_to_user(user_id, {
        "type": "achievement_unlocked",
        "data": achievement_data,
    })
