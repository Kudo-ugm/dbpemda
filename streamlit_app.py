import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials
import plotly.express as px

# --- Google Sheets Auth ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_info = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
creds = Credentials.from_service_account_info(creds_info, scopes=scope)
gc = gspread.authorize(creds)

# --- Load Sheets ---
def load_sheet(sheet_name):
    sh = gc.open("NAMA_FILE_SHEET")  # Ganti sesuai nama file Google Sheets kamu
    return pd.DataFrame(sh.worksheet(sheet_name).get_all_records())

rasio_df = load_sheet("rasio")
keu_prov_df = load_sheet("keu_prov")
kin_prov_df = load_sheet("kin_prov")
keu_kab_df = load_sheet("keu_kab")
kin_kab_df = load_sheet("kin_kab")

try:
    interpretasi_df = load_sheet("Interpretasi")
except:
    interpretasi_df = pd.DataFrame()  # Biar blank kalo sheet kosong

# --- Sidebar Pilihan Rasio ---
st.sidebar.header("Pilih Rasio")
selected_rasio = st.sidebar.selectbox("Rasio", rasio_df['rasio'] if not rasio_df.empty else [])

# --- Deskripsi Rasio ---
if not rasio_df.empty:
    deskripsi_rasio = rasio_df.loc[rasio_df['rasio'] == selected_rasio, 'penjelasan'].values[0]
else:
    deskripsi_rasio = "Deskripsi belum tersedia."

# --- Sidebar List Pemda ---
st.sidebar.header("Pilih Daerah")
# Kumpulkan daftar provinsi/kabupaten/kota dari semua sheet
all_pemda = pd.concat([
    keu_prov_df['pemda'], kin_prov_df['pemda'],
    keu_kab_df['pemda'], kin_kab_df['pemda']
]).drop_duplicates().sort_values().tolist()

selected_pemda = st.sidebar.multiselect("Cari & Pilih Pemda", options=all_pemda, default=[])

# --- Tabs Layout ---
tab1, tab2, tab3, tab4 = st.tabs([
    "Kondisi Keuangan Provinsi", 
    "Kinerja Keuangan Provinsi", 
    "Kondisi Keuangan Kab/Kota", 
    "Kinerja Keuangan Kab/Kota"
])

# --- Function for Chart Rendering ---
def render_chart(df, title):
    if selected_pemda:
        df_filtered = df[df['pemda'].isin(selected_pemda)]
    else:
        df_filtered = df
    if df_filtered.empty:
        st.warning("Data tidak tersedia untuk pilihan Anda.")
        return
    fig = px.line(df_filtered, x="tahun", y="nilai", color="pemda", title=title)
    st.plotly_chart(fig, use_container_width=True)

# --- Function for Interpretasi Box ---
def show_interpretasi(kategori):
    if not interpretasi_df.empty and 'kategori' in interpretasi_df.columns:
        interp_data = interpretasi_df.loc[interpretasi_df['kategori'] == kategori, 'penjelasan']
        if not interp_data.empty:
            interp_text = interp_data.values[0]
        else:
            interp_text = "Interpretasi belum tersedia."
    else:
        interp_text = "Interpretasi belum tersedia."
    st.info(interp_text)

# --- Layout per Tab ---
with tab1:
    col1, col2 = st.columns([3, 1])
    with col1:
        render_chart(keu_prov_df, "Kondisi Keuangan Provinsi")
    with col2:
        st.subheader("Deskripsi Rasio")
        st.write(deskripsi_rasio)
        st.subheader("Interpretasi")
        show_interpretasi("keu_prov")

with tab2:
    col1, col2 = st.columns([3, 1])
    with col1:
        render_chart(kin_prov_df, "Kinerja Keuangan Provinsi")
    with col2:
        st.subheader("Deskripsi Rasio")
        st.write(deskripsi_rasio)
        st.subheader("Interpretasi")
        show_interpretasi("kin_prov")

with tab3:
    col1, col2 = st.columns([3, 1])
    with col1:
        render_chart(keu_kab_df, "Kondisi Keuangan Kab/Kota")
    with col2:
        st.subheader("Deskripsi Rasio")
        st.write(deskripsi_rasio)
        st.subheader("Interpretasi")
        show_interpretasi("keu_kab")

with tab4:
    col1, col2 = st.columns([3, 1])
    with col1:
        render_chart(kin_kab_df, "Kinerja Keuangan Kab/Kota")
    with col2:
        st.subheader("Deskripsi Rasio")
        st.write(deskripsi_rasio)
        st.subheader("Interpretasi")
        show_interpretasi("kin_kab")
