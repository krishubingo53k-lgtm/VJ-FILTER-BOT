# bot.py (Custom — Krishna Movie Hub)
import os
import json
from pyrogram import Client, filters
from datetime_timestamps import datetime

# ------------ Custom Owner & Bot Names -------------
OWNER_NAME = "Krishna"
BOT_DISPLAY_NAME = "Krishna Movie Hub"
# ----------------------------------------------------

# ------------ ENV SECRETS ------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_ID = int(os.environ.get("API_ID") or 0)
API_HASH = os.environ.get("API_HASH")

ADMIN_IDS = os.environ.get("ADMIN_IDS", "")
if ADMIN_IDS.strip():
    ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS.split(",") if x.strip()]
else:
    ADMIN_IDS = []
# ---------------------------------------

DB_FILE = "files_db.json"

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump([], f, indent=2)

app = Client(
    "krishna_session",        # session file name
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

def load_db():
    with open(DB_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return []

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_file_record(filename, file_id, uploader_id):
    db = load_db()
    entry = {
        "name": filename,
        "file_id": file_id,
        "uploader": uploader_id,
        "time": datetime.utcnow().isoformat() + "Z"
    }
    db.append(entry)
    save_db(db)
    return entry

# ---------------- Commands -------------------

@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    user = message.from_user.first_name if message.from_user else "User"
    await message.reply_text(
        f"👋 **Hello {user}!**\n\n"
        f"Welcome to **{BOT_DISPLAY_NAME}** 🎬\n"
        f"Owned & Managed by **{OWNER_NAME}**.\n\n"
        f"📌 Send me any video/document/photo and I will save it.\n"
        f"📁 Use `/list` to see all saved items."
    )

@app.on_message(filters.command("help"))
async def help_cmd(client, message):
    await message.reply_text(
        f"📌 **{BOT_DISPLAY_NAME} Help**\n\n"
        "/start - Start bot\n"
        "/help - Show help\n"
        "/list - Show saved files\n"
        "/get <filename> - Admin only"
    )

@app.on_message(filters.private & (filters.document | filters.video | filters.photo))
async def save_file(client, message):
    if message.document:
        file_id = message.document.file_id
        name = message.document.file_name or "document"
    elif message.video:
        file_id = message.video.file_id
        name = message.video.file_name or f"video_{message.id}.mp4"
    elif message.photo:
        file_id = message.photo[-1].file_id
        name = f"photo_{message.id}.jpg"
    else:
        await message.reply("Unsupported file.")
        return

    uploaded_by = message.from_user.id

    entry = add_file_record(name, file_id, uploaded_by)

    await message.reply_text(
        f"✅ **Saved Successfully!**\n\n"
        f"📁 **Name:** `{entry['name']}`\n"
        f"🆔 **File ID:** `{entry['file_id']}`\n"
        f"👤 **Uploaded by:** `{entry['uploader']}`"
    )

@app.on_message(filters.command("list"))
async def list_files(client, message):
    db = load_db()
    if not db:
        await message.reply_text("No files saved yet.")
        return

    text = "📁 **Saved Files:**\n\n"
    for item in db[-50:]:  # last 50 items
        text += f"▫️ {item['name']} — `{item['file_id']}`\n"

    await message.reply_text(text)

@app.on_message(filters.command("get"))
async def get_file(client, message):
    if message.from_user.id not in ADMIN_IDS:
        await message.reply_text("❌ Only admins allowed!")
        return

    try:
        filename = message.text.split(" ", 1)[1]
    except:
        await message.reply_text("Usage: /get filename.ext")
        return

    db = load_db()
    file = None

    for item in db:
        if item["name"] == filename:
            file = item
            break

    if not file:
        await message.reply_text("❌ File not found.")
        return

    await client.send_document(
        chat_id=message.chat.id,
        document=file["file_id"],
        caption=f"🎬 **{file['name']}**"
    )

# ---------------- START BOT -------------------
if __name__ == "__main__":
    print("Krishna Movie Hub Bot Started...")
    app.run()
