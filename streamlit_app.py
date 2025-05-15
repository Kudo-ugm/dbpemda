import streamlit as st
import pandas as pd

# Load data dari Excel lokal
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

all_pemda = sorted(set(keu_prov_df["Pemda"]).union(keu_kab_df["Pemda"]))

# Sidebar kanan untuk pilihan
with st.sidebar:
    st.header("Filter Pilihan")
    selected_rasio = st.selectbox("Pilih Rasio", options=rasio_df["rasio"])
    search_pemda = st.text_input("Cari Pemda")
    filtered_pemda = [p for p in all_pemda if search_pemda.lower() in p.lower()]
    selected_pemda = st.multiselect("Pilih Pemda (bisa lebih dari 1)", options=filtered_pemda)

# Tampilkan deskripsi rasio di sidebar bawah
with st.sidebar:
    st.markdown("---")
    st.subheader("Deskripsi Rasio")
    deskripsi = rasio_df.loc[rasio_df["rasio"] == selected_rasio, "penjelasan"]
    st.write(deskripsi.values[0] if not deskripsi.empty else "-")

st.title("Dashboard Kinerja dan Keuangan Pemda")

tab1, tab2, tab3, tab4 = st.tabs([
    "Kondisi Keuangan Provinsi",
    "Kinerja Keuangan Provinsi",
    "Kondisi Keuangan Kabupaten/Kota",
    "Kinerja Keuangan Kabupaten/Kota"
])

def filter_data(df, pemda_list, indikator):
    if pemda_list:
        return df[(df["Pemda"].isin(pemda_list)) & (df["Indikator"] == indikator)]
    else:
        return pd.DataFrame(columns=df.columns)

def plot_graph(df, title):
    if df.empty:
        st.write("Tidak ada data untuk pilihan ini.")
        return
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    for pemda in df["Pemda"].unique():
        sub_df = df[df["Pemda"] == pemda]
        ax.plot(sub_df["Tahun"], sub_df["Nilai"], marker='o', label=pemda)
    ax.set_title(title)
    ax.set_xlabel("Tahun")
    ax.set_ylabel("Nilai")
    ax.legend()
    st.pyplot(fig)

def get_interpretasi(kategori):
    interp = interpretasi_df.loc[interpretasi_df["kategori"] == kategori, "penjelasan"]
    return interp.values[0] if not interp.empty else "Belum ada interpretasi untuk kategori ini."

with tab1:
    st.header("Kondisi Keuangan Provinsi")
    df = filter_data(keu_prov_df, selected_pemda, selected_rasio)
    plot_graph(df, "Kondisi Keuangan Provinsi")
    st.markdown("### Interpretasi")
    st.write(get_interpretasi("Keu Prov"))

with tab2:
    st.header("Kinerja Keuangan Provinsi")
    df = filter_data(kin_prov_df, selected_pemda, selected_rasio)
    plot_graph(df, "Kinerja Keuangan Provinsi")
    st.markdown("### Interpretasi")
    st.write(get_interpretasi("Kin Prov"))

with tab3:
    st.header("Kondisi Keuangan Kabupaten/Kota")
    df = filter_data(keu_kab_df, selected_pemda, selected_rasio)
    plot_graph(df, "Kondisi Keuangan Kabupaten/Kota")
    st.markdown("### Interpretasi")
    st.write(get_interpretasi("Keu Kab"))

with tab4:
    st.header("Kinerja Keuangan Kabupaten/Kota")
    df = filter_data(kin_kab_df, selected_pemda, selected_rasio)
    plot_graph(df, "Kinerja Keuangan Kabupaten/Kota")
    st.markdown("### Interpretasi")
    st.write(get_interpretasi("Kin Kab"))
