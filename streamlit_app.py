import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

@st.cache_data
def load_all_data():
    xls = pd.ExcelFile("data.xlsx")
    rasio_df = pd.read_excel(xls, "rasio")
    keu_prov_df = pd.read_excel(xls, "keu_prov")
    kin_prov_df = pd.read_excel(xls, "kin_prov")
    keu_kab_df = pd.read_excel(xls, "keu_kab")
    kin_kab_df = pd.read_excel(xls, "kin_kab")
    try:
        interpretasi_df = pd.read_excel(xls, "Interpretasi")
    except:
        interpretasi_df = pd.DataFrame(columns=["kategori", "penjelasan"])
    return rasio_df, keu_prov_df, kin_prov_df, keu_kab_df, kin_kab_df, interpretasi_df

rasio_df, keu_prov_df, kin_prov_df, keu_kab_df, kin_kab_df, interpretasi_df = load_all_data()

def get_unique_pemda(df):
    return sorted(df["Pemda"].unique())

def get_unique_indikator(df):
    return sorted(df["Indikator"].unique())

def get_interpretasi(kategori):
    interp = interpretasi_df.loc[interpretasi_df["kategori"] == kategori, "penjelasan"]
    return interp.values[0] if not interp.empty else "Belum ada interpretasi untuk kategori ini."

def filter_data(df, pemda_list, indikator):
    if pemda_list and indikator:
        return df[(df["Pemda"].isin(pemda_list)) & (df["Indikator"] == indikator)]
    else:
        return pd.DataFrame(columns=df.columns)

def plot_graph(df, title):
    if df.empty:
        st.write("Tidak ada data untuk pilihan ini.")
        return
    fig, ax = plt.subplots()
    for pemda in df["Pemda"].unique():
        sub_df = df[df["Pemda"] == pemda]
        ax.plot(sub_df["Tahun"], sub_df["Nilai"], marker='o', label=pemda)
    ax.set_title(title)
    ax.set_xlabel("Tahun")
    ax.set_ylabel("Nilai")
    ax.legend()
    st.pyplot(fig)

st.title("Dashboard Kinerja dan Keuangan Pemda")

tab1, tab2, tab3, tab4 = st.tabs([
    "Kondisi Keuangan Provinsi",
    "Kinerja Keuangan Provinsi",
    "Kondisi Keuangan Kabupaten/Kota",
    "Kinerja Keuangan Kabupaten/Kota"
])

with tab1:
    st.header("Kondisi Keuangan Provinsi")
    pemda_options = get_unique_pemda(keu_prov_df)
    indikator_options = get_unique_indikator(keu_prov_df)

    col1, col2 = st.columns([1, 3])

    with col1:
        selected_pemda = st.multiselect("Pilih Pemda", pemda_options)
        selected_indikator = st.selectbox("Pilih Rasio/Indikator", indikator_options)
        deskripsi = rasio_df.loc[rasio_df["rasio"] == selected_indikator, "penjelasan"]
        st.markdown("### Deskripsi Rasio")
        st.write(deskripsi.values[0] if not deskripsi.empty else "-")

    with col2:
        df_filtered = filter_data(keu_prov_df, selected_pemda, selected_indikator)
        plot_graph(df_filtered, "Kondisi Keuangan Provinsi")
        st.markdown("### Interpretasi")
        st.write(get_interpretasi("Keu Prov"))

with tab2:
    st.header("Kinerja Keuangan Provinsi")
    pemda_options = get_unique_pemda(kin_prov_df)
    indikator_options = get_unique_indikator(kin_prov_df)

    col1, col2 = st.columns([1, 3])

    with col1:
        selected_pemda = st.multiselect("Pilih Pemda", pemda_options)
        selected_indikator = st.selectbox("Pilih Rasio/Indikator", indikator_options)
        deskripsi = rasio_df.loc[rasio_df["rasio"] == selected_indikator, "penjelasan"]
        st.markdown("### Deskripsi Rasio")
        st.write(deskripsi.values[0] if not deskripsi.empty else "-")

    with col2:
        df_filtered = filter_data(kin_prov_df, selected_pemda, selected_indikator)
        plot_graph(df_filtered, "Kinerja Keuangan Provinsi")
        st.markdown("### Interpretasi")
        st.write(get_interpretasi("Kin Prov"))

with tab3:
    st.header("Kondisi Keuangan Kabupaten/Kota")
    pemda_options = get_unique_pemda(keu_kab_df)
    indikator_options = get_unique_indikator(keu_kab_df)

    col1, col2 = st.columns([1, 3])

    with col1:
        selected_pemda = st.multiselect("Pilih Pemda", pemda_options)
        selected_indikator = st.selectbox("Pilih Rasio/Indikator", indikator_options)
        deskripsi = rasio_df.loc[rasio_df["rasio"] == selected_indikator, "penjelasan"]
        st.markdown("### Deskripsi Rasio")
        st.write(deskripsi.values[0] if not deskripsi.empty else "-")

    with col2:
        df_filtered = filter_data(keu_kab_df, selected_pemda, selected_indikator)
        plot_graph(df_filtered, "Kondisi Keuangan Kabupaten/Kota")
        st.markdown("### Interpretasi")
        st.write(get_interpretasi("Keu Kab"))

with tab4:
    st.header("Kinerja Keuangan Kabupaten/Kota")
    pemda_options = get_unique_pemda(kin_kab_df)
    indikator_options = get_unique_indikator(kin_kab_df)

    col1, col2 = st.columns([1, 3])

    with col1:
        selected_pemda = st.multiselect("Pilih Pemda", pemda_options)
        selected_indikator = st.selectbox("Pilih Rasio/Indikator", indikator_options)
        deskripsi = rasio_df.loc[rasio_df["rasio"] == selected_indikator, "penjelasan"]
        st.markdown("### Deskripsi Rasio")
        st.write(deskripsi.values[0] if not deskripsi.empty else "-")

    with col2:
        df_filtered = filter_data(kin_kab_df, selected_pemda, selected_indikator)
        plot_graph(df_filtered, "Kinerja Keuangan Kabupaten/Kota")
        st.markdown("### Interpretasi")
        st.write(get_interpretasi("Kin Kab"))
