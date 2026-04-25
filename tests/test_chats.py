"""Тест: ozon_chat_* tools."""

import json
from unittest.mock import patch

import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from mcp_server_ozon_seller.server import mcp
from mcp_server_ozon_seller.models import Chat, ChatMessage

MOCK_CHAT = {"chat_id": "chat-001", "chat_type": "Seller_Buyer", "created_at": "2026-04-20T10:00:00Z"}
MOCK_MESSAGE = {"message_id": "msg-001", "user": {"type": "seller"}, "message": "Здравствуйте!", "created_at": "2026-04-20T10:01:00Z", "is_read": False}


@pytest.mark.anyio
async def test_chat_list():
    Chat.model_validate(MOCK_CHAT)
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.chat_list.return_value = {"result": {"chats": [MOCK_CHAT]}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_chat_list", {})
            assert not result.isError


@pytest.mark.anyio
async def test_chat_history():
    ChatMessage.model_validate(MOCK_MESSAGE)
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.chat_history.return_value = {"result": {"messages": [MOCK_MESSAGE]}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_chat_history", {"chat_id": "chat-001"})
            assert not result.isError


@pytest.mark.anyio
async def test_chat_send_message():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.chat_send_message.return_value = {"result": {"message_id": "msg-002"}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_chat_send_message", {"chat_id": "chat-001", "message": "Привет!"})
            assert not result.isError
