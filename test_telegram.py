"""Exercita o roteamento real da biblioteca com uma API Telegram simulada."""
import json
import unittest
from unittest.mock import AsyncMock, patch

from telegram import Update
from telegram.request import BaseRequest

import papoco
from test_papoco import EXPECTED


class LocalTelegram(BaseRequest):
    def __init__(self):
        self.messages = []

    @property
    def read_timeout(self):
        return 1

    async def initialize(self):
        pass

    async def shutdown(self):
        pass

    async def do_request(self, url, method, request_data=None, **kwargs):
        endpoint = url.rsplit("/", 1)[-1]
        if endpoint == "getMe":
            result = {"id": 123456, "is_bot": True, "first_name": "Rojão teste", "username": "RojaoTesteBot"}
        elif endpoint == "sendMessage":
            data = request_data.parameters
            self.messages.append(data)
            result = {"message_id": len(self.messages), "date": 1,
                      "chat": {"id": data["chat_id"], "type": "supergroup"},
                      "text": data["text"]}
        else:
            raise AssertionError(f"Chamada inesperada: {endpoint}")
        return 200, json.dumps({"ok": True, "result": result}).encode()


class TelegramTests(unittest.IsolatedAsyncioTestCase):
    async def test_roteamento_dos_comandos_em_grupo(self):
        self.assertTrue(callable(getattr(papoco, "build_application", None)), "Falta construir a aplicação Telegram")
        transport = LocalTelegram()
        app = papoco.build_application("123456:TEST_TOKEN_NOT_REAL", request=transport)
        self.assertEqual(app.update_processor.max_concurrent_updates, 16)
        async with app:
            cases = [
                ("/acende", EXPECTED),
                ("/acende@RojaoTesteBot", EXPECTED),
                ("/acende@OutroBot", None),
                ("/start", "Use /acende"),
                ("/ajuda", "Use /acende"),
            ]
            for number, (command, expected) in enumerate(cases, 1):
                with self.subTest(command=command):
                    before = len(transport.messages)
                    update = Update.de_json({
                        "update_id": number,
                        "message": {"message_id": number, "date": 1,
                            "chat": {"id": -1000000 - number, "type": "supergroup"},
                            "from": {"id": 42, "is_bot": False, "first_name": "Teste"},
                            "text": command,
                            "entities": [{"type": "bot_command", "offset": 0, "length": len(command)}]},
                    }, app.bot)
                    with patch("asyncio.sleep", new_callable=AsyncMock):
                        await app.process_update(update)
                    if expected is None:
                        self.assertEqual(len(transport.messages), before)
                    else:
                        messages = transport.messages[before:]
                        if command.startswith("/acende"):
                            self.assertEqual([message["text"] for message in messages], expected)
                        else:
                            self.assertEqual(len(messages), 1)
                            self.assertIn(expected, messages[0]["text"])


if __name__ == "__main__":
    unittest.main()
