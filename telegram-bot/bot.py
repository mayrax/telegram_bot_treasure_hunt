import os
import logging
from typing import Dict

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram import Update

# --------- Config via ENV ---------
TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
BASE  = os.environ["CLOUD_RUN_SERVICE_URL"]              # e.g. https://...run.app  (no trailing slash)
PATH  = os.environ.get("WEBHOOK_PATH", "YOUR_ENDPOINT")  # any string you chose (NOT the token)
PORT  = int(os.environ.get("PORT", "8080"))
WH_SECRET = os.environ.get("WEBHOOK_SECRET")             # optional: extra security

# --------- Logging ---------
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("bot")

# --------- Game Data ---------
QUESTIONS = [
    {"id": 1, "question": "Solve this: 5 + 3 = ?", "answer": "8",
     "location": {"latitude": 37.7749, "longitude": -122.4194}},  # SF
    {"id": 2, "question": "Solve this: 10 - 4 = ?", "answer": "6",
     "location": {"latitude": 40.7128, "longitude": -74.0060}},   # NYC
    {"id": 3, "question": "Solve this: 9 - 8 = ?", "answer": "1",
     "location": {"latitude": 48.8566, "longitude": 2.3522}},     # Paris
]
user_progress: Dict[int, int] = {}  # user_id -> current question id

# --------- Helpers ---------
def current_q_text(qid: int) -> str:
    return QUESTIONS[qid - 1]["question"]

def is_correct(qid: int, text: str) -> bool:
    # normalize: strip & lowercase; extend here for diacritics etc.
    return (text or "").strip().lower() == QUESTIONS[qid - 1]["answer"].strip().lower()

def next_location(qid: int) -> dict:
    return QUESTIONS[qid - 1]["location"]

# --------- Handlers ---------
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Start the hunt. Supports deep-link like /start question_2"""
    uid = update.effective_user.id
    args = ctx.args or []

    if args and args[0].startswith("question_"):
        try:
            qid = int(args[0].split("_", 1)[1])
        except ValueError:
            qid = 1
        if 1 <= qid <= len(QUESTIONS):
            user_progress[uid] = qid
            pre = "Welcome! Let's begin:\n" if qid == 1 else "Here's your next challenge:\n"
            await update.message.reply_text(pre + current_q_text(qid))
            return

    await update.message.reply_text(
        "Welcome to the Treasure Hunt! Scan the first QR code to start.\n"
        "Commands: /help, /reset"
    )

async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Treasure Hunt bot:\n"
        "• /start – start or continue the hunt\n"
        "• /reset – reset your progress\n"
        "Answer each challenge by sending the solution as text. "
        "When correct, I’ll send the next location."
    )

async def cmd_reset(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_progress.pop(uid, None)
    await update.message.reply_text("Your progress was reset. Send /start to begin again.")

async def handle_answer(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    # Guard: only text
    if not update.message or not update.message.text:
        await update.message.reply_text("Please send your answer as text 🙂")
        return

    text = update.message.text

    if uid not in user_progress:
        await update.message.reply_text("Please start by scanning a QR code or send /start.")
        return

    qid = user_progress[uid]
    if is_correct(qid, text):
        await update.message.reply_text("Correct!")
        next_qid = qid + 1
        if next_qid <= len(QUESTIONS):
            user_progress[uid] = next_qid
            loc = next_location(next_qid)
            await update.message.reply_location(latitude=loc["latitude"], longitude=loc["longitude"])
            await update.message.reply_text(
                "Go to this location and scan the next QR code."
            )
        else:
            await update.message.reply_text("🎉 Congratulations! You've completed the treasure hunt.")
            del user_progress[uid]
    else:
        await update.message.reply_text("Incorrect, try again.")

async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Log and attempt a polite response (don’t crash the worker)
    log.exception("Handler error", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text("Oops, something went wrong. Try again!")
        except Exception:
            pass

# --------- Main ---------
def main():
    print("BOT STARTING", flush=True)
    print("WEBHOOK =", f"{BASE}/{PATH}", flush=True)

    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("reset", cmd_reset))

    # Answers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))

    # Error logging
    app.add_error_handler(on_error)

    # One and only server: PTB webhook (no asyncio.run, no extra http.server)
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=PATH,
        webhook_url=f"{BASE}/{PATH}",
        drop_pending_updates=True,
        secret_token=WH_SECRET,  # None if not set; set WEBHOOK_SECRET for extra security
    )

if __name__ == "__main__":
    main()
