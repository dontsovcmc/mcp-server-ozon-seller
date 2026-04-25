"""Тест: ozon_question* tools."""

import json
from unittest.mock import patch

import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from mcp_server_ozon_seller.server import mcp
from mcp_server_ozon_seller.models import Question

MOCK_QUESTION = {"question_id": 9001, "text": "Какой размер?", "product_id": 12345, "is_answered": False}


@pytest.mark.anyio
async def test_questions_list():
    Question.model_validate(MOCK_QUESTION)
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.questions_list.return_value = {"result": {"questions": [MOCK_QUESTION]}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_questions_list", {})
            assert not result.isError


@pytest.mark.anyio
async def test_question_answer():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.question_answer.return_value = {"result": True}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_question_answer", {"question_id": 9001, "answer": "Размер M"})
            assert not result.isError
