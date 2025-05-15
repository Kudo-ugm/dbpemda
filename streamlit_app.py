import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials

# ======= Konfigurasi ========
SHEET_ID = "1Zc6NxUalYApLvo0oDk2koIwCa_qXtuyat8WQbOXjo9Q"

# ======= Load Google Credentials ========
creds_info = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(creds_info, scopes=scope)
gc = gspread.authorize(credentials)

# ======= Cache Load All Sheets ========
@st.cache_data(show_spinner="Loading data from Google Sheets...")
def load_all_data():
    sh = gc.open_by_key(SHEET_ID)

    rasio_df = pd.DataFrame(sh.worksheet("rasio").get_all_records())
    keu_prov_df = pd.DataFrame(sh.worksheet("keu_prov").get_all_records())
    kin_prov_df = pd.DataFrame(sh.worksheet("kin_prov").get_all_records())
    keu_kab_df = pd.DataFrame(sh.worksheet("keu_kab").get_all_records())
    kin_kab_df = pd.DataFrame(sh.worksheet("kin_kab").get_all_records())
    
    try:
        interpretasi_df = pd.DataFrame(sh.worksheet("Interpretasi").get_all_records())
    except:
        interpretasi_df = pd.DataFrame(columns=["kategori", "penjelasan"])

    return rasio_df, keu_prov_df, kin_prov_df, keu_kab_df, kin_kab_df, interpretasi_df

# ======= Load Once ========
rasio_df, keu_prov_df, kin_prov_df, keu_kab_df, kin_kab_df, interpretasi_df = load_all_data()

# ======= Sidebar ========
st.sidebar.title("Pilihan Analisis")

selected_rasio = st.sidebar.selectbox("Pilih Rasio", rasio_df["rasio"].unique())

# Deskripsi Rasio Box
rasio_desc = rasio_df.loc[rasio_df["rasio"] == selected_rasio, "penjelasan"].values[0]
st.sidebar.markdown(f"**Deskripsi Rasio**\n\n{rasio_desc}")

# ======= Pilih Daerah ========
st.sidebar.markdown("### Pilih Provinsi/Kabupaten/Kota")

all_pemda = sorted(set(keu_prov_df["daerah"]).union(keu_kab_df["daerah"]))

search_pemda = st.sidebar.text_input("Cari Daerah", "")

filtered_pemda = [p for p in all_pemda if search_pemda.lower() in p.lower()]
selected_pemda = st.sidebar.multiselect("Daftar Daerah", filtered_pemda)

# ======= Main Tabs ========
st.title("Dashboard Kinerja & Keuangan")

tab1, tab2, tab3, tab4 = st.tabs([
    "Kondisi Keuangan Provinsi", 
    "Kinerja Keuangan Provinsi", 
    "Kondisi Keuangan Kabupaten/Kota", 
    "Kinerja Keuangan Kabupaten/Kota"
])

# ======= Plot Helper ========
import altair as alt

def plot_chart(df, title):
    if not selected_pemda:
        st.warning("Pilih minimal satu daerah terlebih dahulu.")
        return

    filtered_df = df[df["daerah"].isin(selected_pemda) & (df["rasio"] == selected_rasio)]
    
    if filtered_df.empty:
        st.info("Data tidak ditemukan untuk pilihan ini.")
        return

    chart = alt.Chart(filtered_df).mark_line(point=True).encode(
        x='tahun:O',
        y='nilai:Q',
        color='daerah:N'
    ).properties(
        title=title,
        width=700,
        height=400
    )
    
    st.altair_chart(chart, use_container_width=True)

# ======= Tab 1 ========
with tab1:
    st.header("Kondisi Keuangan Provinsi")
    plot_chart(keu_prov_df, "Kondisi Keuangan Provinsi")
    
    interp_text = interpretasi_df.loc[
        interpretasi_df['kategori'] == "Kondisi Keuangan Provinsi", 
        'penjelasan'
    ].values[0] if not interpretasi_df.empty else ""
    st.markdown(f"**Interpretasi:** {interp_text}")

# ======= Tab 2 ========
with tab2:
    st.header("Kinerja Keuangan Provinsi")
    plot_chart(kin_prov_df, "Kinerja Keuangan Provinsi")
    
    interp_text = interpretasi_df.loc[
        interpretasi_df['kategori'] == "Kinerja Keuangan Provinsi", 
        'penjelasan'
    ].values[0] if not interpretasi_df.empty else ""
    st.markdown(f"**Interpretasi:** {interp_text}")

# ======= Tab 3 ========
with tab3:
    st.header("Kondisi Keuangan Kabupaten/Kota")
    plot_chart(keu_kab_df, "Kondisi Keuangan Kabupaten/Kota")
    
    interp_text = interpretasi_df.loc[
        interpretasi_df['kategori'] == "Kondisi Keuangan Kabupaten/Kota", 
        'penjelasan'
    ].values[0] if not interpretasi_df.empty else ""
    st.markdown(f"**Interpretasi:** {interp_text}")

# ======= Tab 4 ========
with tab4:
    st.header("Kinerja Keuangan Kabupaten/Kota")
    plot_chart(kin_kab_df, "Kinerja Keuangan Kabupaten/Kota")
    
    interp_text = interpretasi_df.loc[
        interpretasi_df['kategori'] == "Kinerja Keuangan Kabupaten/Kota", 
        'penjelasan'
    ].values[0] if not interpretasi_df.empty else ""
    st.markdown(f"**Interpretasi:** {interp_text}")
