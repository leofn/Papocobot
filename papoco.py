"""Bot independente inspirado no comportamento textual do @Papocobot."""

import asyncio
import logging
import os

from html import escape
from time import monotonic

from telegram.error import TelegramError
from telegram.ext import Application, CommandHandler

INTERVALO = 10.0

ROJAO = "Fizzzzzz\n\npra pra pra pra pra pra pra pra\n\npra pra\n\npra\n\npra\n\nPOOOOOWW"


BOMBA_DE_MIL = (
    'Fiiiiiizzzzzzzzzzzzzzzzzzz',
    'Zzzzzzzzzzzz',
    'Zzzzzzzzzzzzz',
    'Zzzzzzzzzzzzz ZZZZ',
    'CATAPUUUUUMMMMMM',
)
TNT_ASCII = (
    ' ___________________    . , ; .\n'
    "(___________________|~~~~~X.;' .\n"
    '                      \' `" \' `\n'
    '            TNT'
)


async def acende(update, context):
    await _disparar(update, context, ROJAO.split("\n\n"))


async def bomba_de_mil(update, context):
    await _disparar(update, context, BOMBA_DE_MIL, TNT_ASCII)


async def _disparar(update, context, textos, arte=None):
    now = monotonic()
    last = context.chat_data.get("last_fire")
    if context.chat_data.get("running") or (last is not None and now - last < INTERVALO):
        return
    context.chat_data["last_fire"] = now
    context.chat_data["running"] = True
    try:
        for number, text in enumerate(textos):
            if number:
                await asyncio.sleep(1.0)
            await update.effective_message.reply_text(text, do_quote=False)
        if arte is not None:
            await asyncio.sleep(1.0)
            await update.effective_message.reply_text(
                "<pre>" + escape(arte) + "</pre>", do_quote=False, parse_mode="HTML",
            )
    finally:
        context.chat_data["running"] = False


async def ajuda(update, context):
    await update.effective_message.reply_text(
        "Use /acende para soltar o rojão.\n"
        "Use /bomba_de_mil para a bomba de mil com desenho TNT.\n"
        "Em grupos, acrescente @" + context.bot.username + " ao comando.\n"
        "Intervalo de 10 segundos por conversa."
    )


async def on_error(update, context):
    logging.getLogger("papocobot").warning(
        "Falha ao processar comando: %s.", type(context.error).__name__,
    )


def build_application(token, request=None):
    builder = Application.builder().token(token)
    builder.concurrent_updates(16)
    if request is not None:
        builder.request(request)
        builder.get_updates_request(request)
    app = builder.build()
    app.add_handler(CommandHandler("acende", acende))
    app.add_handler(CommandHandler("bomba_de_mil", bomba_de_mil))
    app.add_handler(CommandHandler(["start", "ajuda"], ajuda))
    app.add_error_handler(on_error)
    return app


if __name__ == "__main__":
    token = os.environ.get("PAPOCO_BOT_TOKEN")
    if not token:
        raise SystemExit("Defina PAPOCO_BOT_TOKEN com o token do novo bot criado no @BotFather.")
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
    for name in ("telegram", "httpx", "httpcore"):
        logging.getLogger(name).setLevel(logging.CRITICAL)
    try:
        build_application(token).run_polling(
            allowed_updates=["message"], drop_pending_updates=True,
        )
    except TelegramError as exc:
        raise SystemExit(
            f"Falha ao iniciar: {type(exc).__name__}. Verifique token e conexão."
        ) from None
