"""Shared dependencies for API routes"""
from typing import Generator
import asyncio

from app.services.notification_service import notification_service

async def get_notification_service():
    """Dependency for getting notification service"""
    return notification_service

async def get_event_loop():
    """Get current event loop"""
    return asyncio.get_event_loop()
