import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load data
@st.cache_data
def load_data():
    xls = pd.ExcelFile("data.xlsx")
    rasio_df = pd.read_excel(xls, "rasio")
    interpretasi_df = pd.read_excel(xls, "interpretasi")

    def load_sheet(sheet):
        return pd.read_excel(xls, sheet).rename(columns={
            "Tahun": "tahun", "Pemda": "pemda", "Kluster": "kluster",
            "Indikator": "indikator", "Nilai": "nilai"
        })

    keu_prov = load_sheet("keu_prov")
    kin_prov = load_sheet("kin_prov")
    keu_kab = load_sheet("keu_kab")
    kin_kab = load_sheet("kin_kab")

    return rasio_df, interpretasi_df, keu_prov, kin_prov, keu_kab, kin_kab

rasio_df, interpretasi_df, keu_prov_df, kin_prov_df, keu_kab_df, kin_kab_df = load_data()

# Plot helper
def plot_line(df, title):
    fig, ax = plt.subplots()
    for pemda in df["pemda"].unique():
        subset = df[df["pemda"] == pemda]
        ax.plot(subset["tahun"], subset["nilai"], marker="o", label=pemda)
    ax.set_title(title)
    ax.set_xlabel("Tahun")
    ax.set_ylabel("Nilai")
    ax.legend()
    st.pyplot(fig)

# Sidebar filter inside tabs
def tab_content(sheet_df, rasio_df, tab_title, key_prefix):
    col1, col2 = st.columns([1, 3])

    with col1:
        st.subheader("Filter Data")

        search_pemda = st.text_input("Cari Pemda", "", key=f"{key_prefix}_search")
        pemda_options = sorted(sheet_df["pemda"].unique())
        if search_pemda:
            pemda_options = [p for p in pemda_options if search_pemda.lower() in p.lower()]

        selected_pemda = st.multiselect("Pilih Pemda", pemda_options, key=f"{key_prefix}_pemda")
        indikator_options = sorted(sheet_df["indikator"].unique())
        selected_indikator = st.selectbox("Pilih Indikator", indikator_options, key=f"{key_prefix}_indikator")

        deskripsi = rasio_df.loc[rasio_df["rasio"] == selected_indikator, "penjelasan"]
        st.markdown("### Deskripsi Indikator")
        st.info(deskripsi.values[0] if not deskripsi.empty else "-")

    with col2:
        if selected_pemda and selected_indikator:
            filtered_df = sheet_df[(sheet_df["pemda"].isin(selected_pemda)) & (sheet_df["indikator"] == selected_indikator)]
            plot_line(filtered_df, tab_title)

# App layout
st.set_page_config(layout="wide", page_title="Dashboard Pemda")
st.title("Dashboard Kinerja & Keuangan Pemda")

tabs = st.tabs(["Keuangan Provinsi", "Kinerja Provinsi", "Keuangan Kab/Kota", "Kinerja Kab/Kota"])

with tabs[0]:
    tab_content(keu_prov_df, rasio_df, "Keuangan Provinsi", "keu_prov")

with tabs[1]:
    tab_content(kin_prov_df, rasio_df, "Kinerja Provinsi", "kin_prov")

with tabs[2]:
    tab_content(keu_kab_df, rasio_df, "Keuangan Kab/Kota", "keu_kab")

with tabs[3]:
    tab_content(kin_kab_df, rasio_df, "Kinerja Kab/Kota", "kin_kab")
