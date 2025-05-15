import streamlit as st
import pandas as pd
import altair as alt

# ======= Load Excel Local ========
@st.cache_data(show_spinner="Loading local Excel file...")
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
