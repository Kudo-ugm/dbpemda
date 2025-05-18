import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="Dashboard Pemda")

@st.cache_data
def load_data():
    xls = pd.ExcelFile("data.xlsx")
    rasio = pd.read_excel(xls, "rasio")
    keu_prov = pd.read_excel(xls, "keu_prov")
    kin_prov = pd.read_excel(xls, "kin_prov")
    keu_kab = pd.read_excel(xls, "keu_kab")
    kin_kab = pd.read_excel(xls, "kin_kab")
    interpretasi = pd.read_excel(xls, "interpretasi")
    return rasio, keu_prov, kin_prov, keu_kab, kin_kab, interpretasi

rasio_df, keu_prov_df, kin_prov_df, keu_kab_df, kin_kab_df, interpretasi_df = load_data()

def plot_graph(df, judul):
    if df.empty:
        st.warning("Tidak ada data untuk ditampilkan.")
        return
    fig, ax = plt.subplots(figsize=(10, 5))
    for label, grp in df.groupby("label"):
        grp = grp.sort_values("Tahun")
        ax.plot(grp["Tahun"], grp["Nilai"], marker='o', label=label)
    ax.set_title(judul)
    ax.set_xlabel("Tahun")
    ax.set_ylabel("Nilai")
    ax.legend()
    st.pyplot(fig)

tab1, tab2, tab3, tab4 = st.tabs(["Kinerja Provinsi", "Kinerja Kab/Kota", "Keuangan Provinsi", "Keuangan Kab/Kota"])

tabs = [
    ("Kinerja Keuangan Provinsi", kin_prov_df, tab1),
    ("Kinerja Kab/Kota", kin_kab_df, tab2),
    ("Keuangan Provinsi", keu_prov_df, tab3),
    ("Keuangan Kab/Kota", keu_kab_df, tab4),
]

for judul, df, tab in tabs:
    with tab:
        st.header(judul)
        pemda_options = sorted(df["Pemda"].unique())
        indikator_options = sorted(df["Indikator"].unique())

        selected_pemda = st.sidebar.multiselect(
            f"Pilih Pemda - {judul}", pemda_options, default=pemda_options[:1], key=f"pemda_{judul}"
        )
        selected_indikator = st.sidebar.selectbox(
            f"Pilih Indikator - {judul}", indikator_options, key=f"indikator_{judul}"
        )

        filtered_df = df[
            (df["Pemda"].isin(selected_pemda)) & (df["Indikator"] == selected_indikator)
        ].copy()

        if not filtered_df.empty:
            # Tambah kolom label gabungan: "Pemda (Kluster X)"
            filtered_df["label"] = filtered_df["Pemda"] + " (Kluster " + filtered_df["Kluster"].astype(str) + ")"
        else:
            filtered_df["label"] = ""

        plot_graph(filtered_df, f"{judul} - {selected_indikator}")

        # Tempat untuk interpretasi - sementara dikosongkan
        st.subheader("Interpretasi")
        with st.container():
            st.markdown(
                """
                <div style='border:1px solid #ddd; border-radius:8px; padding:10px; min-height:100px; background-color:#f9f9f9;'>
                <!-- Isi interpretasi nanti dimasukkan di sini -->
                </div>
                """,
                unsafe_allow_html=True,
            )
