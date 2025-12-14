import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import openai

# Pegando variáveis de ambiente
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Comando /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("À disposição CHEFE")

# Comando /chat para enviar pergunta à OpenAI
def chat(update: Update, context: CallbackContext):
    user_text = " ".join(context.args)
    if not user_text:
        update.message.reply_text("Digite algo após /chat")
        return
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=user_text,
            max_tokens=150
        )
        update.message.reply_text(response.choices[0].text.strip())
    except Exception as e:
        update.message.reply_text(f"Erro: {str(e)}")

# Configuração do bot
updater = Updater(TELEGRAM_BOT_TOKEN)
updater.dispatcher.add_handler(CommandHandler("start", start))
updater.dispatcher.add_handler(CommandHandler("chat", chat))

# Inicia o bot
updater.start_polling()
updater.idle()
