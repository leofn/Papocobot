"""Testes locais. Nenhuma mensagem real é enviada ao Telegram."""
import asyncio
import os
import runpy
import subprocess
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import papoco

EXPECTED = [
    "Fizzzzzz",
    "pra pra pra pra pra pra pra pra",
    "pra pra",
    "pra",
    "pra",
    "POOOOOWW",
]


def interaction(chat_data=None):
    message = SimpleNamespace(reply_text=AsyncMock())
    update = SimpleNamespace(effective_message=message)
    context = SimpleNamespace(chat_data={} if chat_data is None else chat_data)
    return update, context


class PapocoTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        sleeper = patch("asyncio.sleep", new_callable=AsyncMock)
        self.sleep = sleeper.start()
        self.addCleanup(sleeper.stop)

    async def test_acende_envia_sequencia_exata_em_mensagens_separadas(self):
        update, context = interaction()
        await papoco.acende(update, context)
        calls = update.effective_message.reply_text.await_args_list
        self.assertEqual([call.args[0] for call in calls], EXPECTED)
        self.assertTrue(all(call.kwargs == {"do_quote": False} for call in calls))
        self.assertEqual(self.sleep.await_count, len(EXPECTED) - 1)
        self.assertTrue(all(call.args == (1.0,) for call in self.sleep.await_args_list))

    async def test_nao_sobrepoe_sequencia_lenta_no_mesmo_chat(self):
        update, context = interaction()
        entered, release = asyncio.Event(), asyncio.Event()

        async def send(*args, **kwargs):
            if update.effective_message.reply_text.await_count == 1:
                entered.set()
                await release.wait()

        update.effective_message.reply_text.side_effect = send
        with patch("papoco.monotonic", side_effect=[0, 20]):
            task = asyncio.create_task(papoco.acende(update, context))
            try:
                await asyncio.wait_for(entered.wait(), timeout=2)
                await papoco.acende(update, context)
                self.assertEqual(update.effective_message.reply_text.await_count, 1)
            finally:
                release.set()
                await task
        self.assertEqual(update.effective_message.reply_text.await_count, len(EXPECTED))

    async def test_falha_de_envio_libera_a_conversa(self):
        update, context = interaction()
        update.effective_message.reply_text.side_effect = RuntimeError("falha simulada")
        with patch("papoco.monotonic", side_effect=[0, 11]):
            with self.assertRaises(RuntimeError):
                await papoco.acende(update, context)
            self.assertFalse(context.chat_data.get("running"))
            update.effective_message.reply_text.side_effect = None
            await papoco.acende(update, context)
        self.assertEqual(update.effective_message.reply_text.await_count, 1 + len(EXPECTED))

    async def test_log_de_erro_nao_expoe_conteudo_ou_token(self):
        self.assertTrue(callable(getattr(papoco, "on_error", None)))
        context = SimpleNamespace(error=RuntimeError("TOKEN_PRIVADO mensagem pessoal"))
        with self.assertLogs("papocobot", level="WARNING") as captured:
            await papoco.on_error(None, context)
        self.assertIn("RuntimeError", " ".join(captured.output))
        self.assertNotIn("TOKEN_PRIVADO", " ".join(captured.output))
        self.assertNotIn("mensagem pessoal", " ".join(captured.output))

    async def test_intervalo_expira_em_dez_segundos(self):
        update, context = interaction()
        with patch("papoco.monotonic", side_effect=[0, 9.9, 10]):
            await papoco.acende(update, context)
            await papoco.acende(update, context)
            await papoco.acende(update, context)
        self.assertEqual(update.effective_message.reply_text.await_count, 2 * len(EXPECTED))

    async def test_conversas_tem_intervalos_independentes(self):
        first, first_ctx = interaction()
        second, second_ctx = interaction()
        await papoco.acende(first, first_ctx)
        await papoco.acende(second, second_ctx)
        self.assertEqual(first.effective_message.reply_text.await_count, len(EXPECTED))
        self.assertEqual(second.effective_message.reply_text.await_count, len(EXPECTED))

    async def test_repeticao_no_mesmo_chat_respeita_intervalo(self):
        update, context = interaction()
        await papoco.acende(update, context)
        await papoco.acende(update, context)
        self.assertEqual(update.effective_message.reply_text.await_count, len(EXPECTED))

    def test_execucao_com_token_inicia_polling_sem_comandos_antigos(self):
        with patch.dict(os.environ, {"PAPOCO_BOT_TOKEN": "123456:TEST_TOKEN_NOT_REAL"}):
            with patch("telegram.ext.Application.builder") as builder:
                runpy.run_path(papoco.__file__, run_name="__main__")
                builder.return_value.token.assert_called_once_with("123456:TEST_TOKEN_NOT_REAL")
                app = builder.return_value.token.return_value.build.return_value
                app.run_polling.assert_called_once_with(
                    allowed_updates=["message"], drop_pending_updates=True,
                )

    def test_erro_de_inicializacao_nao_expoe_token(self):
        from telegram.error import InvalidToken
        failure = None
        with patch.dict(os.environ, {"PAPOCO_BOT_TOKEN": "123456:TEST_TOKEN_NOT_REAL"}):
            with patch("telegram.ext.Application.builder") as builder:
                app = builder.return_value.token.return_value.build.return_value
                app.run_polling.side_effect = InvalidToken("TOKEN_PRIVADO")
                try:
                    runpy.run_path(papoco.__file__, run_name="__main__")
                except BaseException as exc:
                    failure = exc
        self.assertIsInstance(failure, SystemExit)
        self.assertNotIn("TOKEN_PRIVADO", str(failure))
        self.assertIn("InvalidToken", str(failure))

    def test_execucao_sem_token_exige_credencial_propria(self):
        env = dict(os.environ)
        env.pop("PAPOCO_BOT_TOKEN", None)
        result = subprocess.run(
            [sys.executable, str(Path(papoco.__file__))],
            env=env, capture_output=True, text=True, timeout=10,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("PAPOCO_BOT_TOKEN", result.stderr)


if __name__ == "__main__":
    unittest.main()
