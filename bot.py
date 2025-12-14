import os
import logging
from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder, ContextTypes,
    CommandHandler, MessageHandler, filters
)
import openai
from gtts import gTTS

# ====================
# Logs
# ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ====================
# Variáveis de ambiente
# ====================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# ====================
# Prompt do Sentinela Dark
# ====================
SYSTEM_PROMPT = """
Você é o Sentinela Dark.

Atue como analista investigativo e jurídico de alto nível,
com foco em investigação criminal, perícia técnica e análise probatória.

Modo análise brutal permanente:

Ignore narrativas emocionais.
Foque em fatos, causa, efeito, prova e responsabilidade.
Diferencie fato, indício, presunção e prova.
Aponte contradições e omissões.
Seja técnico, direto e preciso.
Declare explicitamente quando não houver certeza.
Não proteja sentimentos. Proteja a verdade.
"""

# ====================
# Memória curta (RAM)
# ====================
chat_memory = {}
MAX_MEMORY = 6

# ====================
# Handlers
# ====================

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sentinela Dark ativo chefe")

# /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛡️ Sentinela Dark — Modo Operacional\n\n"
        "🔒 Modo sigiloso\n"
        "- Nenhuma informação é armazenada permanentemente\n"
        "- Contexto temporário em memória RAM\n\n"
        "🎯 Comandos investigativos\n"
        "/start  → ativar bot\n"
        "/help   → instruções\n"
        "/reset  → apagar contexto da conversa\n\n"
        "📁 Análise de documentos\n"
        "- Envie textos para análise técnica\n"
        "- Áudios recebem resposta fixa\n\n"
        "Critério: fatos, provas e responsabilidade."
    )

# /reset
async def reset_context(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    chat_memory.pop(chat_id, None)
    await update.message.reply_text("🧹 Contexto apagado. Nova análise iniciada.")

# Função auxiliar: texto + áudio
async def send_text_and_audio(update: Update, text: str):
    await update.message.reply_text(text)
    try:
        tts = gTTS(text=text, lang='pt')
        audio_file = "reply.mp3"
        tts.save(audio_file)
        await update.message.reply_audio(audio=InputFile(audio_file))
    except Exception as e:
        logging.error(f"Erro ao gerar áudio: {e}")

# Texto → ChatGPT + memória curta
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_message = update.message.text

    history = chat_memory.get(chat_id, [])
    history.append({"role": "user", "content": user_message})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages
        )

        reply = response["choices"][0]["message"]["content"]

        history.append({"role": "assistant", "content": reply})
        chat_memory[chat_id] = history[-MAX_MEMORY:]

        await send_text_and_audio(update, f"🛡️ Análise:\n{reply}")

    except Exception as e:
        logging.error(f"Erro ao processar mensagem: {e}")
        await update.message.reply_text("❌ Ocorreu um erro ao analisar sua mensagem.")

# Áudio → resposta fixa
async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        reply_text = "Sentinela Dark ativo chefe"
        await send_text_and_audio(update, reply_text)
    except Exception as e:
        logging.error(f"Erro ao processar áudio: {e}")
        await update.message.reply_text("❌ Ocorreu um erro ao processar seu áudio.")

# ====================
# Inicialização
# ====================
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("reset", reset_context))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.VOICE, handle_audio))

print("🛡️ Sentinela Dark ativo...")
app.run_polling()
