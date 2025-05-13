import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
import json
from google.oauth2.service_account import Credentials

# === Google Sheets Authentication ===
creds_info = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(creds_info, scopes=scope)
client = gspread.authorize(creds)

# === Load Data ===
spreadsheet_id = '1Zc6NxUalYApLvo0oDk2koIwCa_qXtuyat8WQbOXjo9Q'  # Ganti dengan ID kamu

def load_sheet(sheet_name):
    sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
    df = pd.DataFrame(sheet.get_all_records())
    df['Tahun'] = df['Tahun'].astype(str)  # Pastikan Tahun dalam string untuk sumbu X
    return df

df_keu = load_sheet('Keu_Kabkot')
df_kin = load_sheet('Kin_Kabkot')

# === Streamlit Layout ===
st.title("Dashboard Kinerja & Keuangan Pemda")

# Tabs untuk memisahkan grafik Keuangan & Kinerja
tab1, tab2 = st.tabs(["Keuangan (Keu_Kabkot)", "Kinerja (Kin_Kabkot)"])

# === Function buat chart interaktif ===
def plot_chart(df, title):
    indikator_list = df['Indikator'].unique()
    pemda_list = df['Pemda'].unique()

    indikator_selected = st.selectbox(f"Pilih Indikator untuk {title}", indikator_list)
    pemda_selected = st.multiselect(f"Pilih Pemda untuk {title}", pemda_list, default=pemda_list[:3])

    # Filter data sesuai pilihan user
    df_filtered = df[(df['Indikator'] == indikator_selected) & (df['Pemda'].isin(pemda_selected))]

    if df_filtered.empty:
        st.warning("Data kosong untuk pilihan ini.")
        return

    fig = px.line(df_filtered, x='Tahun', y='Nilai', color='Pemda', markers=True,
                  title=f"{title} - {indikator_selected}")
    st.plotly_chart(fig, use_container_width=True)

# === Tab 1: Keuangan ===
with tab1:
    plot_chart(df_keu, "Keuangan")

# === Tab 2: Kinerja ===
with tab2:
    plot_chart(df_kin, "Kinerja")
