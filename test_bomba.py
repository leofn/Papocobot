"""Contrato textual e formatação da bomba de mil. Transporte simulado."""
import html
import unittest
from unittest.mock import AsyncMock, patch

import papoco
from test_papoco import interaction

EXPECTED_BOMBA = [
    "Fiiiiiizzzzzzzzzzzzzzzzzzz",
    "Zzzzzzzzzzzz",
    "Zzzzzzzzzzzzz",
    "Zzzzzzzzzzzzz ZZZZ",
    "CATAPUUUUUMMMMMM",
]
EXPECTED_ART = ' ___________________    . , ; .\n(___________________|~~~~~X.;\' .\n                      \' `" \' `\n            TNT'


class BombaTests(unittest.IsolatedAsyncioTestCase):
    async def test_comandos_compartilham_protecao_contra_repeticao(self):
        for first, second in [(papoco.acende, papoco.bomba_de_mil), (papoco.bomba_de_mil, papoco.acende)]:
            with self.subTest(first=first.__name__):
                update, context = interaction()
                with patch("asyncio.sleep", new_callable=AsyncMock):
                    with patch("papoco.monotonic", return_value=0):
                        await first(update, context)
                        count = update.effective_message.reply_text.await_count
                        await second(update, context)
                self.assertEqual(update.effective_message.reply_text.await_count, count)

    async def test_falha_na_arte_libera_o_chat(self):
        update, context = interaction()
        update.effective_message.reply_text.side_effect = [None] * len(EXPECTED_BOMBA) + [RuntimeError("falha simulada")]
        with patch("asyncio.sleep", new_callable=AsyncMock):
            with self.assertRaises(RuntimeError):
                await papoco.bomba_de_mil(update, context)
        self.assertFalse(context.chat_data.get("running"))

    async def test_falas_exatas_e_explosao_em_bloco_monoespacado(self):
        self.assertTrue(callable(getattr(papoco, "bomba_de_mil", None)), "Comando ainda não implementado")
        update, context = interaction()
        with patch("asyncio.sleep", new_callable=AsyncMock) as sleep:
            await papoco.bomba_de_mil(update, context)
        calls = update.effective_message.reply_text.await_args_list
        self.assertEqual([call.args[0] for call in calls[:-1]], EXPECTED_BOMBA)
        self.assertTrue(all(call.kwargs == {"do_quote": False} for call in calls[:-1]))
        self.assertEqual(calls[-1].args[0], "<pre>" + html.escape(EXPECTED_ART) + "</pre>")
        self.assertEqual(calls[-1].kwargs, {"do_quote": False, "parse_mode": "HTML"})
        self.assertEqual(sleep.await_count, len(EXPECTED_BOMBA))
        self.assertTrue(all(call.args == (1.0,) for call in sleep.await_args_list))
        self.assertTrue(EXPECTED_ART.isascii())
        self.assertLessEqual(max(map(len, EXPECTED_ART.splitlines())), 32)


if __name__ == "__main__":
    unittest.main()
