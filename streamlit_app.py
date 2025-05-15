import streamlit as st
import pandas as pd
import json
from google.oauth2.service_account import Credentials
import gspread
import plotly.express as px

# --- Auth ke Google Sheets ---
scope = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
creds_info = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
creds = Credentials.from_service_account_info(creds_info, scopes=scope)
gc = gspread.authorize(creds)

# --- Load Data dari Google Sheets ---
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1Zc6NxUalYApLvo0oDk2koIwCa_qXtuyat8WQbOXjo9Q"

def load_sheet(sheet_name):
    sh = gc.open_by_url(SPREADSHEET_URL)
    worksheet = sh.worksheet(sheet_name)
    df = pd.DataFrame(worksheet.get_all_records())
    return df

rasio_df = load_sheet("rasio")
keu_prov_df = load_sheet("keu_prov")
kin_prov_df = load_sheet("kin_prov")
keu_kab_df = load_sheet("keu_kab")
kin_kab_df = load_sheet("kin_kab")
interpretasi_df = load_sheet("interpretasi")

# --- Sidebar: Pilihan Rasio ---
st.sidebar.header("Pilih Rasio")
selected_rasio = st.sidebar.selectbox("Rasio", rasio_df['rasio'])
rasio_penjelasan = rasio_df.loc[rasio_df['rasio'] == selected_rasio, 'penjelasan'].values[0]

# --- Sidebar: Pilih Pemda ---
st.sidebar.header("Cari & Pilih Pemda")
all_pemda = pd.concat([keu_prov_df['Pemda'], keu_kab_df['Pemda']]).unique()
search_pemda = st.sidebar.text_input("Cari Pemda")
filtered_pemda = [p for p in all_pemda if search_pemda.lower() in p.lower()]
selected_pemda = st.sidebar.multiselect("Daftar Pemda", filtered_pemda)

# --- Sidebar: Tombol Add (+) ---
if st.sidebar.button("Tambah Semua Hasil Cari"):
    selected_pemda = filtered_pemda

# --- Main Layout: 3 Kolom ---
col_pemda, col_graph, col_info = st.columns([2, 6, 4])

# --- Kanan: Box Deskripsi Rasio & Intepretasi ---
with col_info:
    st.markdown(f"### Deskripsi Rasio\n{rasio_penjelasan}")
    selected_graph_category = st.radio("Pilih Kategori Grafik", ["Keu Prov", "Kin Prov", "Keu Kab", "Kin Kab"])
    interp_text = interpretasi_df.loc[interpretasi_df['kategori'] == selected_graph_category, 'penjelasan'].values[0]
    st.markdown(f"### Intepretasi\n{interp_text}")

# --- Tengah: Grafik Tabs ---
with col_graph:
    tabs = st.tabs(["Kondisi Keuangan Provinsi", "Kinerja Keuangan Provinsi",
                    "Kondisi Keuangan Kab/Kota", "Kinerja Keuangan Kab/Kota"])
    
    def plot_graph(df, title):
        available_indikator = df['Indikator'].unique()
        selected_indikator = st.selectbox(f"Pilih Indikator untuk {title}", available_indikator, key=title)
        filtered_df = df[(df['Pemda'].isin(selected_pemda)) & (df['Indikator'] == selected_indikator)]
        fig = px.line(filtered_df, x="Tahun", y="Nilai", color="Pemda", markers=True, title=title)
        st.plotly_chart(fig, use_container_width=True)
    
    with tabs[0]: plot_graph(keu_prov_df, "Kondisi Keuangan Provinsi")
    with tabs[1]: plot_graph(kin_prov_df, "Kinerja Keuangan Provinsi")
    with tabs[2]: plot_graph(keu_kab_df, "Kondisi Keuangan Kabupaten/Kota")
    with tabs[3]: plot_graph(kin_kab_df, "Kinerja Keuangan Kabupaten/Kota")
