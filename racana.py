from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)
from dotenv import load_dotenv
import os

from database import (
    init_db, cek_nim, simpan_anggota,
    simpan_absensi, sudah_absen_hari_ini,
    ambil_jadwal_7_hari, tambah_jadwal
)

# ===== LOAD ENV =====
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# ===== INIT DB =====
init_db()

# ===== SEED JADWAL (input dari kode) =====
def seed_jadwal():
    # kalau sudah ada jadwal, tidak usah isi lagi
    if ambil_jadwal_7_hari():
        return

    tambah_jadwal("Rapat Mingguan", "2026-04-20")
    tambah_jadwal("Latihan Pramuka", "2026-04-22")
    tambah_jadwal("Bakti Sosial", "2026-04-25")

seed_jadwal()

# ===== COMMAND =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome Di Bot Racana Kariadi-Kardinah\nUniversitas Bhamada Slawi"
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "== MENU BOT RACANA ==\n"
        "/daftar - Daftar anggota\n"
        "/absensi - Absensi anggota\n"
        "/info - Info kegiatan\n"
    )

# ===== FORM DAFTAR =====
NAMA, NIM = range(2)

async def daftar(update, context):
    await update.message.reply_text("Masukkan nama kamu:")
    return NAMA

async def input_nama(update, context):
    context.user_data['nama'] = update.message.text
    await update.message.reply_text("Masukkan NIM kamu:")
    return NIM

async def input_nim(update, context):
    nama = context.user_data['nama']
    nim = update.message.text

    if not nim.isdigit():
        await update.message.reply_text("❌ NIM harus angka!")
        return NIM

    if cek_nim(nim):
        await update.message.reply_text("❌ NIM sudah terdaftar!")
        return ConversationHandler.END

    simpan_anggota(nama, nim)

    await update.message.reply_text("✅ Pendaftaran berhasil!")
    return ConversationHandler.END

# ===== ABSENSI =====
async def absensi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Masukkan NIM untuk absensi:")
    return "ABSEN_NIM"

async def proses_absensi(update, context):
    nim = update.message.text

    if not cek_nim(nim):
        await update.message.reply_text("❌ NIM belum terdaftar!")
        return ConversationHandler.END

    if sudah_absen_hari_ini(nim):
        await update.message.reply_text("⚠️ Kamu sudah absen hari ini!")
        return ConversationHandler.END

    simpan_absensi(nim)

    await update.message.reply_text("✅ Absensi berhasil!")
    return ConversationHandler.END

# ===== INFO =====
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = ambil_jadwal_7_hari()

    if not data:
        await update.message.reply_text("Belum ada jadwal kegiatan")
        return

    teks = "📅 Jadwal 7 Hari Kedepan:\n\n"

    for kegiatan, tanggal in data:
        teks += f"{tanggal} - {kegiatan}\n"

    await update.message.reply_text(teks)

# ===== CANCEL =====
async def cancel(update, context):
    await update.message.reply_text("❌ Dibatalkan")
    return ConversationHandler.END

# ===== HANDLER =====
daftar_handler = ConversationHandler(
    entry_points=[CommandHandler("daftar", daftar)],
    states={
        NAMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_nama)],
        NIM: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_nim)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)

absen_handler = ConversationHandler(
    entry_points=[CommandHandler("absensi", absensi)],
    states={
        "ABSEN_NIM": [MessageHandler(filters.TEXT & ~filters.COMMAND, proses_absensi)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)

# ===== APP =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(daftar_handler)
app.add_handler(absen_handler)

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("menu", menu))
app.add_handler(CommandHandler("info", info))

print("Bot Aktif...")
app.run_polling()