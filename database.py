import sqlite3
from datetime import datetime

DB_NAME = "anggotaRacana.db"

def connect():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS anggota (
        nim TEXT PRIMARY KEY,
        nama TEXT,
        waktu_daftar TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS absensi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nim TEXT,
        waktu TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jadwal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kegiatan TEXT,
        tanggal TEXT
    )
    """)

    conn.commit()
    conn.close()


# ===== ANGGOTA =====
def cek_nim(nim):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM anggota WHERE nim = ?", (nim,))
    data = cursor.fetchone()

    conn.close()
    return data


def simpan_anggota(nama, nim):
    conn = connect()
    cursor = conn.cursor()

    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO anggota (nim, nama, waktu_daftar)
    VALUES (?, ?, ?)
    """, (nim, nama, waktu))

    conn.commit()
    conn.close()


# ===== ABSENSI =====
def simpan_absensi(nim):
    conn = connect()
    cursor = conn.cursor()

    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO absensi (nim, waktu)
    VALUES (?, ?)
    """, (nim, waktu))

    conn.commit()
    conn.close()


def sudah_absen_hari_ini(nim):
    conn = connect()
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
    SELECT * FROM absensi
    WHERE nim = ? AND waktu LIKE ?
    """, (nim, f"{today}%"))

    data = cursor.fetchone()

    conn.close()
    return data


# ===== JADWAL =====
def tambah_jadwal(kegiatan, tanggal):
    conn = connect()
    cursor = conn.cursor()

    # cegah duplikat
    cursor.execute("""
    SELECT * FROM jadwal WHERE kegiatan = ? AND tanggal = ?
    """, (kegiatan, tanggal))

    if cursor.fetchone() is None:
        cursor.execute("""
        INSERT INTO jadwal (kegiatan, tanggal)
        VALUES (?, ?)
        """, (kegiatan, tanggal))

    conn.commit()
    conn.close()


def ambil_jadwal_7_hari():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT kegiatan, tanggal FROM jadwal
    WHERE tanggal >= date('now')
    ORDER BY tanggal ASC
    LIMIT 7
    """)

    data = cursor.fetchall()
    conn.close()
    return data