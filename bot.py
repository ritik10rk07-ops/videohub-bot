import sqlite3
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ============ CONFIG ============
TOKEN = "8837852864:AAHN_y-tCmSA2nlcyeAInMSlTxI7xXCMvmo"
ADMIN_IDS = [5111601009, 1505746127]
CHANNEL_LINKS = {
    1: ["https://t.me/+lHPaT7RyALE1Mzhl"],
    2: [
        "https://t.me/+WogT9dN_p7RlZjJh",
        "https://t.me/+lHPaT7RyALE1Mzhl",
    ],
    3: [
        "https://t.me/+JU4AuOYF79kzMmNl",
    ],
    4: [
        "https://t.me/+dTgU7hI0PyRkY2U1",
    ],
    5: [
        "https://t.me/+lcEEi_cwv3BiNDFl",
    ],
    6: [
        "https://t.me/+lHPaT7RyALE1Mzhl",
        "https://t.me/+WogT9dN_p7RlZjJh",
        "https://t.me/+JU4AuOYF79kzMmNl",
        "https://t.me/+dTgU7hI0PyRkY2U1",
        "https://t.me/+lcEEi_cwv3BiNDFl",
        "https://t.me/+FZRrR5NTjto4NTI1",
        "https://t.me/+3Lw9kKJhJ01lZmQ1",
    ],
}

QR_IMAGE = "qr.png"

DB_FILE = "users.db"

# ===================================


# ============ DATABASE ============
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    approved INTEGER DEFAULT 0,
    plan INTEGER DEFAULT 0
)
""")

conn.commit()


# ============ FUNCTIONS ============
def add_user(user_id: int):
    cur.execute(
        "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
        (user_id,)
    )
    conn.commit()


def approve_user(user_id: int, plan: int):
    cur.execute(
        "UPDATE users SET approved = 1, plan = ? WHERE user_id = ?",
        (plan, user_id),
    )
    conn.commit()


def get_user(user_id: int):
    cur.execute("""
    SELECT approved, plan
    FROM users
    WHERE user_id = ?
    """, (user_id,))
    return cur.fetchone()


# ============ START ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id
    add_user(user_id)

    user = get_user(user_id)

    # ===== APPROVED USER =====
    if user and user[0] == 1:

        plan = user[1]
        links = CHANNEL_LINKS.get(plan)

        if not links:
            await update.message.reply_text(
                "❌ Invalid plan. Contact admin."
            )
            return

        msg = "✅ Payment Verified!\n\n🔓 Your Group Links:\n\n"

        for link in links:
            msg += f"{link}\n"

        await update.message.reply_text(msg)

        return

    # ===== NEW USER =====
    await update.message.reply_text(
        "📢 PLEASE READ CAREFULLY\n\n"

        "⚡ How it Works:\n"
        "• Select your plan and pay amount\n\n"

        "💳 Choose Your Plans:\n"
        "1• ₹35 — Collection\n"
        "2• ₹49 — Top Collection\n"
        "3• ₹100 — R+P\n"
        "4• ₹199 — Sleeping Pills\n"
        "5• ₹299 — Deshi C+P, (#Popular)\n"
        "• ₹699~ All stocks (#Best)\n\n"

"💸 Crypto (USDT) & USD($) Payments Available\n"
"📩 Contact: @Purchese02\n\n"

        "💰 Please pay using the QR code below.\n"
        "📸 After payment, send screenshot here.\n"
        "⚠️ After approval, type /start again."
    )

    try:
        await update.message.reply_photo(
            photo=open(QR_IMAGE, "rb")
        )

    except:
        await update.message.reply_text(
            "❌ QR image not found."
        )


# ============ HANDLE PHOTO ============
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user
    add_user(user.id)

    await update.message.reply_text(
        "✅ Payment screenshot received.\n"
        "⏳ Please wait for admin verification.\n\n"
        "📩 Contact for help: @ClickTo_Help"
    )

    # Forward to admin
    for admin_id in ADMIN_IDS:
          await context.bot.forward_message(
        chat_id=admin_id,
        from_chat_id=update.message.chat_id,
        message_id=update.message.message_id,
    )

    # Admin message
    for admin_id in ADMIN_IDS:
          await context.bot.send_message(
        chat_id=admin_id,
        text=(
            "💳 New Payment Proof Received\n\n"

            f"👤 USER ID: {user.id}\n"
            f"👤 USERNAME: @{user.username or 'No username'}\n\n"

            "✅ APPROVE USER:\n"
            f"/approve {user.id} 1\n"
            f"/approve {user.id} 2\n"
            f"/approve {user.id} 3\n"
            f"/approve {user.id} 4\n"
            f"/approve {user.id} 5\n"
            f"/approve {user.id} 6\n"
        )
    )


# ============ APPROVE ============
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.chat_id not in ADMIN_IDS:
          return

    if len(context.args) != 2:
        await update.message.reply_text(
            "Usage:\n/approve USER_ID PLAN"
        )
        return

    user_id = int(context.args[0])
    plan = int(context.args[1])

    if plan not in [1, 2, 3, 4, 5, 6]:
        await update.message.reply_text(
            "❌ Invalid Plan"
        )
        return

    approve_user(user_id, plan)

    await update.message.reply_text(
        f"✅ User {user_id} approved for {plan} groups."
    )

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "✅ Your payment has been approved.\n\n"
                "Type /start ←now for the l i n k."
            )
            
        )
    except:
        pass


# ============ MAIN ============
def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("approve", approve))

    app.add_handler(
        MessageHandler(filters.PHOTO, handle_photo)
    )

    print("🤖 Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()
