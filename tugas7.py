import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
 
DB_NAME = "nilai_siswa.db"
 
 
# 1. DATABASE

def koneksi():
    return sqlite3.connect(DB_NAME)
 
 
def buat_tabel():
    """Membuat tabel nilai_siswa jika belum ada."""
    conn = koneksi()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS nilai_siswa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_siswa TEXT NOT NULL,
            biologi INTEGER NOT NULL,
            fisika INTEGER NOT NULL,
            inggris INTEGER NOT NULL,
            prediksi_fakultas TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
 
 
# ---------------------------------------------------------------
# 2. LOGIKA PREDIKSI
# ---------------------------------------------------------------
def hitung_prediksi(biologi, fisika, inggris):
    """
    Nilai tertinggi menentukan fakultas:
    - Biologi paling tinggi -> Kedokteran
    - Fisika paling tinggi  -> Teknik
    - Inggris paling tinggi -> Bahasa
    Jika ada nilai tertinggi yang sama, prioritas: Biologi > Fisika > Inggris.
    """
    if biologi >= fisika and biologi >= inggris:
        return "Kedokteran"
    elif fisika >= biologi and fisika >= inggris:
        return "Teknik"
    else:
        return "Bahasa"
 
 
# ---------------------------------------------------------------
# 3. FUNGSI CRUD
# ---------------------------------------------------------------
def ambil_input():
    """Validasi dan ambil data dari entry. Return None jika tidak valid."""
    nama = entry_nama.get().strip()
    if not nama:
        messagebox.showwarning("Peringatan", "Nama siswa harus diisi!")
        return None
    try:
        bio = int(entry_bio.get())
        fis = int(entry_fis.get())
        ing = int(entry_ing.get())
    except ValueError:
        messagebox.showwarning("Peringatan", "Nilai harus berupa angka!")
        return None
    for n in (bio, fis, ing):
        if not 0 <= n <= 100:
            messagebox.showwarning("Peringatan", "Nilai harus antara 0 - 100!")
            return None
    return nama, bio, fis, ing
 
 
def submit():
    """CREATE: simpan data baru."""
    data = ambil_input()
    if data is None:
        return
    nama, bio, fis, ing = data
    prediksi = hitung_prediksi(bio, fis, ing)
 
    conn = koneksi()
    conn.execute(
        "INSERT INTO nilai_siswa (nama_siswa, biologi, fisika, inggris, prediksi_fakultas) "
        "VALUES (?, ?, ?, ?, ?)",
        (nama, bio, fis, ing, prediksi),
    )
    conn.commit()
    conn.close()
 
    messagebox.showinfo("Berhasil", f"Prediksi fakultas untuk {nama}: {prediksi}")
    bersihkan()
    tampilkan_data()
 
 
def tampilkan_data():
    """READ: tampilkan semua data ke Treeview."""
    for row in tabel.get_children():
        tabel.delete(row)
    conn = koneksi()
    for row in conn.execute("SELECT * FROM nilai_siswa"):
        tabel.insert("", tk.END, values=row)
    conn.close()
 
 
def pilih_data(event):
    """Isi entry saat baris tabel diklik."""
    item = tabel.focus()
    if not item:
        return
    v = tabel.item(item)["values"]
    bersihkan(reset_id=False)
    global id_terpilih
    id_terpilih = v[0]
    entry_nama.insert(0, v[1])
    entry_bio.insert(0, v[2])
    entry_fis.insert(0, v[3])
    entry_ing.insert(0, v[4])
    lbl_hasil.config(text=f"Prediksi: {v[5]}")
 
 
def update():
    """UPDATE: ubah data terpilih."""
    if id_terpilih is None:
        messagebox.showwarning("Peringatan", "Pilih data di tabel terlebih dahulu!")
        return
    data = ambil_input()
    if data is None:
        return
    nama, bio, fis, ing = data
    prediksi = hitung_prediksi(bio, fis, ing)
 
    conn = koneksi()
    conn.execute(
        "UPDATE nilai_siswa SET nama_siswa=?, biologi=?, fisika=?, inggris=?, "
        "prediksi_fakultas=? WHERE id=?",
        (nama, bio, fis, ing, prediksi, id_terpilih),
    )
    conn.commit()
    conn.close()
    messagebox.showinfo("Berhasil", f"Data diperbarui. Prediksi: {prediksi}")
    bersihkan()
    tampilkan_data()
 
 
def hapus():
    """DELETE: hapus data terpilih."""
    if id_terpilih is None:
        messagebox.showwarning("Peringatan", "Pilih data di tabel terlebih dahulu!")
        return
    if not messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus data ini?"):
        return
    conn = koneksi()
    conn.execute("DELETE FROM nilai_siswa WHERE id=?", (id_terpilih,))
    conn.commit()
    conn.close()
    bersihkan()
    tampilkan_data()
 
 
def bersihkan(reset_id=True):
    global id_terpilih
    for e in (entry_nama, entry_bio, entry_fis, entry_ing):
        e.delete(0, tk.END)
    lbl_hasil.config(text="Prediksi: -")
    if reset_id:
        id_terpilih = None
 
 

 #4. TAMPILAN TKINTER
buat_tabel()
id_terpilih = None
 
root = tk.Tk()
root.title("Prediksi Fakultas Berdasarkan Nilai")
root.geometry("620x520")
 
frm = tk.LabelFrame(root, text="Input Nilai Siswa", padx=10, pady=10)
frm.pack(fill="x", padx=10, pady=10)
 
tk.Label(frm, text="Nama Siswa").grid(row=0, column=0, sticky="w", pady=3)
tk.Label(frm, text="Nilai Biologi").grid(row=1, column=0, sticky="w", pady=3)
tk.Label(frm, text="Nilai Fisika").grid(row=2, column=0, sticky="w", pady=3)
tk.Label(frm, text="Nilai Inggris").grid(row=3, column=0, sticky="w", pady=3)
 
entry_nama = tk.Entry(frm, width=35)
entry_bio = tk.Entry(frm, width=35)
entry_fis = tk.Entry(frm, width=35)
entry_ing = tk.Entry(frm, width=35)
entry_nama.grid(row=0, column=1, padx=10)
entry_bio.grid(row=1, column=1, padx=10)
entry_fis.grid(row=2, column=1, padx=10)
entry_ing.grid(row=3, column=1, padx=10)
 
lbl_hasil = tk.Label(frm, text="Prediksi: -", font=("Arial", 11, "bold"))
lbl_hasil.grid(row=4, column=0, columnspan=2, pady=8)
 
frm_btn = tk.Frame(root)
frm_btn.pack()
tk.Button(frm_btn, text="Submit", width=10, command=submit).grid(row=0, column=0, padx=4)
tk.Button(frm_btn, text="Update", width=10, command=update).grid(row=0, column=1, padx=4)
tk.Button(frm_btn, text="Hapus", width=10, command=hapus).grid(row=0, column=2, padx=4)
tk.Button(frm_btn, text="Bersihkan", width=10, command=bersihkan).grid(row=0, column=3, padx=4)

kolom = ("ID", "Nama", "Biologi", "Fisika", "Inggris", "Prediksi")
tabel = ttk.Treeview(root, columns=kolom, show="headings", height=10)
for k in kolom:
    tabel.heading(k, text=k)
    tabel.column(k, width=90, anchor="center")
tabel.column("ID", width=40)
tabel.pack(fill="both", expand=True, padx=10, pady=10)
tabel.bind("<ButtonRelease-1>", pilih_data)
 
tampilkan_data()
root.mainloop()