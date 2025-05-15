import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials

# ====== Auth ======
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_info = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
creds = Credentials.from_service_account_info(creds_info, scopes=scope)
gc = gspread.authorize(creds)

# ====== Load Sheet ======
SHEET_ID = "1Zc6NxUalYApLvo0oDk2koIwCa_qXtuyat8WQbOXjo9Q"

def load_sheet(sheet_name):
    sh = gc.open_by_key(SHEET_ID)
    worksheet = sh.worksheet(sheet_name)
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

# Load all sheets
rasio_df = load_sheet("rasio")
keu_prov_df = load_sheet("keu_prov")
kin_prov_df = load_sheet("kin_prov")
keu_kab_df = load_sheet("keu_kab")
kin_kab_df = load_sheet("kin_kab")

try:
    interpretasi_df = load_sheet("Interpretasi")
except:
    interpretasi_df = pd.DataFrame(columns=["kategori", "penjelasan"])

# ====== UI Layout ======
st.set_page_config(layout="wide", page_title="Dashboard Keuda")

st.title("Dashboard Kinerja & Keuangan")

tab1, tab2, tab3, tab4 = st.tabs(["Kondisi Keuangan Provinsi", "Kinerja Keuangan Provinsi", 
                                  "Kondisi Keuangan Kab/Kota", "Kinerja Keuangan Kab/Kota"])

# ====== Component Function ======
def display_dashboard(df, level):
    # Sidebar left: Pemda Selector
    st.sidebar.subheader(f"Daftar {level}")
    search_pemda = st.sidebar.text_input(f"Cari {level}")
    pemda_list = sorted(df["Pemda"].unique())
    filtered_pemda = [p for p in pemda_list if search_pemda.lower() in p.lower()]
    selected_pemda = st.sidebar.multiselect(f"Pilih {level}", filtered_pemda)

    # Sidebar: Rasio Selector
    selected_rasio = st.sidebar.selectbox("Pilih Rasio", rasio_df["rasio"])

    # Main: Chart
    chart_df = df[df["Indikator"] == selected_rasio]
    if selected_pemda:
        chart_df = chart_df[chart_df["Pemda"].isin(selected_pemda)]

    chart_pivot = chart_df.pivot_table(index="Tahun", columns="Pemda", values="Nilai")
    st.subheader(f"Grafik {level} - {selected_rasio}")
    st.line_chart(chart_pivot)

    # Right Column: Deskripsi Rasio + Interpretasi
    col1, col2 = st.columns(2)

    # Deskripsi Rasio
    rasio_desc = rasio_df[rasio_df["rasio"] == selected_rasio]["penjelasan"].values
    if rasio_desc:
        col1.markdown(f"### Deskripsi Rasio\n{rasio_desc[0]}")
    else:
        col1.markdown("### Deskripsi Rasio\n(Tidak tersedia)")

    # Interpretasi (optional blank)
    if not interpretasi_df.empty:
        interp_text = interpretasi_df.loc[interpretasi_df["kategori"] == selected_rasio, "penjelasan"].values
        if interp_text:
            col2.markdown(f"### Interpretasi\n{interp_text[0]}")
        else:
            col2.markdown("### Interpretasi\n(Tidak tersedia)")
    else:
        col2.markdown("### Interpretasi\n(Belum ada data)")

# ====== Tabs ======
with tab1:
    display_dashboard(keu_prov_df, "Provinsi")

with tab2:
    display_dashboard(kin_prov_df, "Provinsi")

with tab3:
    display_dashboard(keu_kab_df, "Kabupaten/Kota")

with tab4:
    display_dashboard(kin_kab_df, "Kabupaten/Kota")
