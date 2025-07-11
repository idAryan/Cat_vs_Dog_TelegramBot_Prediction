import logging
from typing import Final
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from bot_name import bot
BOT_USERNAME:Final=bot
with open("token.txt", "r") as f:
    TOKEN: Final = f.read().strip()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Wanna try /custom Click a photo and I will tell whether it is dog or cat")

async def custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Send me photo I will tell whether it is dog or cat")

def handle_response(text: str)->str:
    processed:str=text.lower().strip()
    if "hello" in processed:
        return "Hello! There, write /start"
    if "i love python" in processed:
        return "Python is great!"
    return "I did'nt understand"
async def handle_message(update: Update, context):
    messege_type = update.message.chat.type
    text: str = update.message.text
    print(f" User {update.message.chat.id} sent a message: {text}")
    if messege_type == "group":
        if BOT_USERNAME in text:
            new_text : str=text.replace(BOT_USERNAME, "").strip()
            response:str=handle_response(new_text)
        else:
            return
    else:
        response: str =handle_response(text)
    print(response)
    await update.message.reply_text(response)
if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    print("start")
    start_handler = CommandHandler('start', start)
    custom_handler = CommandHandler('custom', custom)
    messege_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    application.add_handler(start_handler)
    application.add_handler(custom_handler)
    application.add_handler(messege_handler)
    print("polling")
    
    application.run_polling()