import streamlit as st
import mysql.connector
import datetime as dt
import pandas as pd
from passlib.hash import pbkdf2_sha256
from st_aggrid import AgGrid


# koneksi database
db = mysql.connector.connect(host = "localhost",user = "root", password = "", database = "perpus_arsi")

# cursor
cursor = db.cursor()


def login():
    st.set_page_config(page_title="Halaman Login", page_icon="🍃", layout="centered")
    with st.form('login'):
        st.title("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button('Masuk')

    if submit:
        if username:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            if result:
                if password == "":
                    st.warning("Password Tidak Boleh Kosong")
                elif pbkdf2_sha256.verify(password, result[3]):
                    #Initialization
                    st.warning(result[4])
                    st.session_state["role"] = result[4]
                    st.session_state["nama"] = result[1]
                    st.rerun()
                else:
                    st.error('Password Salah')
            else:
                st.error("Username Belum Terdaftar")
        else:
            st.warning('Username Tidak Boleh Kosong')


def getAllDF(table):
    cursor.execute(f"SELECT * FROM {table}")
    result = cursor.fetchall()
    return pd.DataFrame(result, columns=cursor.column_names)
def getAll(table):
    cursor.execute(f"SELECT * FROM {table}")
    return cursor.fetchall()
def getWhere(table, id_dt, field='id'):
    cursor.execute(f"SELECT * FROM {table} WHERE {field} = {id_dt}")
    return cursor.fetchall()
def getUser(table):
    cursor.execute(f"SELECT * FROM {table} WHERE id != 1")
    return cursor.fetchall()

# Halaman Admin
def admin():
    st.set_page_config(page_title=f"Admin {st.session_state["nama"]}", page_icon="🍃", layout="centered")
    if st.session_state["role"] == "9":
        st.title("ADMIN PERPUSTAKAN ARSITEKTUR")
        menu = st.sidebar.selectbox("MENU ADMIN",["DATA BUKU", "TAMBAH BUKU", "EDIT BUKU", "PEMINJAMAN BUKU", "DAFTAR PEMINJAM","PENGEMBALIAN", "REGISTER"])

        if menu == "DATA BUKU":
            st.subheader("Data Buku")
            df =getAllDF('data_buku')
            AgGrid(df)
        elif menu == "TAMBAH BUKU":
            with st.form('peminjman_buku'):
                st.latex("Tambah Buku")
                judul_buku = st.text_input("Judul Buku")
                penulis = st.text_input("Penulis")
                penerbit = st.text_input("Penerbit")
                tahun_terbit = st.text_input("Tahun Terbit")
                kota_terbit = st.text_input("Kota Terbit")
                submit = st.form_submit_button("Simpan")
                
                if submit:
                    cursor.execute("INSERT INTO data_buku(judul_buku,penulis,penerbit,tahun_terbit,kota_terbit) VALUES(%s,%s,%s,%s,%s)",(judul_buku,penulis,penerbit,tahun_terbit,kota_terbit))
                    st.success("Data Buku Berhasil Di Tambahkan")
                    db.commit()
        elif menu == "EDIT BUKU":
            st.header("Edit Buku")
            id_input = st.number_input("Pilih",1)
            if id_input:
                buku = getWhere('data_buku',id_input)
                if buku:
                    for b in buku:
                        with st.form('Edit'):
                            st.latex("EDIT")
                            judul_buku = st.text_input("Judul Buku",b[1])
                            penulis = st.text_input("Penulis",b[2])
                            penerbit = st.text_input("Penerbit",b[3])
                            tahun_terbit = st.text_input("Tahun Terbit",b[4])
                            kota_terbit = st.text_input("Kota Terbit",b[5])
                            submit = st.form_submit_button("Simpan")

                            if submit:
                                # Memperbarui data
                                sql = "UPDATE data_buku SET judul_buku = %s, penulis = %s, penerbit = %s, tahun_terbit = %s, kota_terbit = %s WHERE id = %s"
                                val = (judul_buku, penulis, penerbit, tahun_terbit, kota_terbit,b[0])
                                cursor.execute(sql, val)
                                st.success("Data Buku Berhasil Di Perbarui")
                                db.commit()
                else:
                    st.warning("Data Buku Tidak Di Temukan", icon="⚠️")
        elif menu == "PEMINJAMAN BUKU":
            judul = []
            user = []
            data1= getAll('data_buku')
            data2= getUser('users')
            for d in data1:
                judul.append(d[1])
            for d in data2:
                user.append(d[1])

            with st.form('peminjaman'):
                st.latex("Peminjaman      Buku")
                user_select = st.selectbox("Nama",(user))
                judul_buku = st.selectbox("Judul Buku", (judul))
                pinjam = st.form_submit_button("Pinjam")

            if pinjam:
                cursor.execute("SELECT * FROM data_peminjam WHERE peminjam= %s", (user_select,))
                user = cursor.fetchall()
        
                if user:
                    cursor.execute("SELECT * FROM data_peminjam WHERE peminjam= %s AND is_active = 1", (user_select,))
                    cek_active = cursor.fetchall()
                    if cek_active:
                        st.warning("Maaf Peminjaman Buku Hanya Boleh 1 Buku Saja")
                        st.error("Mohon Selesikan Peminjaman Sebelum Meminjam Kembali")
                    else:
                        # Menambah data
                        sql = "INSERT INTO data_peminjam (peminjam, judul_buku, is_active) VALUES (%s, %s,%s)"
                        val = (user_select, judul_buku, 1)
                        cursor.execute(sql, val)
                        st.success("Peminjaman Berhaisl")
                        db.commit()
                else:
                    # Menambah data
                    sql = "INSERT INTO data_peminjam (peminjam, judul_buku, is_active) VALUES (%s, %s,%s)"
                    val = (user_select, judul_buku, 1)
                    cursor.execute(sql, val)
                    st.success("Peminjaman Berhaisl")
                    db.commit()
        elif menu == "DAFTAR PEMINJAM":
            dp = getWhere('data_peminjam',1,'is_active')
            if dp:
                data = {
                        "User" : [],
                        "Buku" : [],
                        "Jam" : [],
                        "Tanggal" : []
                    }
                for d in dp[0:]:
                    data["User"].append(d[1])
                    data["Buku"].append(d[2])
                    data["Jam"].append(dt.datetime.strftime(d[5], "%H:%M:%S"))
                    data["Tanggal"].append(dt.datetime.strftime(d[5], "%d, %b %Y"))
                    df = pd.DataFrame(data)
                st.subheader('Daftar Peminjaman')
                AgGrid(df)
            else:
                st.warning("Wahh Belum Ada Yang Minjem Buku Nih..")
        elif menu == "PENGEMBALIAN":
            cursor.execute("SELECT * FROM data_peminjam WHERE is_active = %s", (1,))
            data = cursor.fetchall()
            if data:
                data = data[0]
    
            with st.form('Pengembalian_Buku'):
                st.latex("Pengembalian Buku")
                nama = st.text_input("Nama")
                submit = st.form_submit_button("Kembalikan")

            if submit:
                if nama in data[1:]:
                    data_waktu = data[5]
                    waktu_sekarang = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    waktu_sekarang = dt.datetime.strptime(waktu_sekarang, '%Y-%m-%d %H:%M:%S')
                    # Menghitung selisih waktu antara dua objek datetime
                    selisih_waktu = waktu_sekarang - data_waktu
                    
                    # Menghitung selisih waktu per hari
                    selisih_hari = selisih_waktu.days
                    denda = 0
                    if selisih_hari > 7:
                        denda += (selisih_hari - 7) * 1000
                    
                    # Memperbarui data
                    sql = "UPDATE data_peminjam SET is_active = %s, denda = %s WHERE id = %s"
                    val = (0, denda, data[0])
                    cursor.execute(sql, val)
                    db.commit()
                    if denda:
                        st.warning(f"Terimakasih Telah Meminjam Buku Kami Dan Jangan lupa Membayar Denda Sebesar Rp{denda}")
                    else :
                        st.success("Terimakasih Telah Meminjam Buku Kami")

                else:
                    st.error("Nama Peminjam Tidak Terdaftar")
        elif menu == "REGISTER":
            with st.form("register"):
                st.latex("Register")
                nama = st.text_input("Nama")
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                confirm = st.text_input("Ulangi Password", type="password")
                submit = st.form_submit_button("Daftar")

            if submit:
                if password == confirm:
                    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                    result = cursor.fetchone()

                    if not result:
                        hashed_password = pbkdf2_sha256.hash(password)
                        role = 1
                        cursor.execute("INSERT INTO users (nama, username, password, role) VALUES (%s, %s, %s, %s)", (nama, username, hashed_password, role))
                        st.success("Akun berhasil dibuat.")
                        db.commit()
                    else:
                        st.warning("Username sudah ada.")
                else:
                    st.warning("Password tidak sama", icon="⚠️")

        logout = st.sidebar.button("Logout")
        if logout:
            del st.session_state['role']
            st.rerun()

    else:
        login()

def user():
    if st.session_state["role"] == "1":
        nama = st.session_state["nama"]
        st.set_page_config(page_title=f"User {nama}", page_icon="📚", layout="centered")
        menu = st.sidebar.selectbox("MENU", ["HOME","RIWAYAT"])
        if menu == "HOME":
            st.title(body=f"📚Selamat Datang {nama}")
            cursor.execute("SELECT * FROM data_peminjam WHERE peminjam = %s AND is_active = 1", (nama,))
            result = cursor.fetchone()

            if result:
                data_waktu = result[5]
                waktu_sekarang = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                waktu_sekarang = dt.datetime.strptime(waktu_sekarang, '%Y-%m-%d %H:%M:%S')

                # Menghitung selisih waktu antara dua objek datetime
                selisih_waktu = waktu_sekarang - data_waktu
                
                # Menghitung selisih waktu per hari
                selisih_hari = selisih_waktu.days
                    
                denda = 0
                st.info(f"Kamu Meminjam Buku {result[2]}",icon="ℹ️")
                if selisih_hari < 7:
                    waktu_kembali = data_waktu + dt.timedelta(days=7)
                    waktu_kembali = dt.datetime.strftime(waktu_kembali, "%d, %b %Y")
                    st.warning(f"Mohon Di Kembalikan Sebelum {waktu_kembali}", icon="⚠️")
                else :
                    denda += (selisih_hari - 7) * 1000
                    st.error(f"Kamu Terlambat {selisih_hari - 7} Hari Dan Kamu Medapat Sanksi Rp{denda}")
            else:
                st.subheader("Yahh Kamu Belum Meminjam Buku Kali ini")

        if menu == "RIWAYAT":
            st.title(body="📚Riwayat Peminjaman Buku")
            cursor.execute("SELECT * FROM data_peminjam WHERE peminjam = %s  AND is_active = 0", (nama,))
            result = cursor.fetchall()
            if result:
                dp = {
                        "Buku" : [],
                        "Denda" : [],
                        "Jam" : [],
                        "Tanggal" : []
                    }
                for r in result[0:]:
                    dp["Buku"].append(r[2])
                    dp["Denda"].append(f"Rp{r[4]}")
                    dp["Jam"].append(dt.datetime.strftime(r[5], "%H:%M:%S"))
                    dp["Tanggal"].append(dt.datetime.strftime(r[5], "%d, %b %Y"))
                df = pd.DataFrame(dp)
                AgGrid(df)
            else:
                st.warning("Riwayat Akan Tersedia Setelah Peminjaman Selesai")
        logout = st.sidebar.button("Logout")
        if logout:
            del st.session_state['role']
            st.rerun()
    else:
        login()