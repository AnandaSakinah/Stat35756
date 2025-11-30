import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import matplotlib.pyplot as plt

# --- Custom CSS ---
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #FFA64D 25%, #FFB84D 50%, #FFCC66 75%);
        background-attachment: fixed;
        font-family: 'Poppins', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .header-container {
        display: flex;
        align-items: center; /* sejajar vertikal */
        justify-content: center;
        gap: 20px;
    }
    .header-title {
        font-size: 42px;
        font-weight: 700;
        color: #ffffff;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
        letter-spacing: 1.5px;
    }
    .subtitle {
        text-align: center;
        font-size: 22px;
        color: #1a3d7c;
        margin-bottom: 30px;
        font-weight: 500;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
    }
    .watermark {
        position: fixed;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 12px;
        color: rgba(255,255,255,0.6);
        font-family: monospace;
        z-index: 9999;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Header ---
col1, col2 = st.columns([1,4])
with col1:
    st.image("Lambang_Badan_Pusat_Statistik_(BPS)_Indonesia.svg.png", width=120)  # pastikan file ada di folder project
with col2:
    st.markdown(
        "<div class='header-title'>EconoStat Kota Mojokerto 3576</div>",
        unsafe_allow_html=True
    )

st.markdown("<div class='watermark'>output@developer_ananda_sakinah</div>", unsafe_allow_html=True)

# --- Koneksi ke Google Sheets ---
conn = st.connection("gsheets", type=GSheetsConnection)
existing_data = conn.read(worksheet="Triwulanan", usecols=list(range(9)), ttl=5)
existing_data = existing_data.dropna(how="all")

# --- Navigasi ---
if "page" not in st.session_state:
    st.session_state.page = "form"

if st.session_state.page == "form":
    st.markdown("<div class='subtitle'>Silahkan Input Data Triwulanan di Bawah Ini.</div>", unsafe_allow_html=True)

    with st.form(key="Econostat"):
        date = st.date_input("Tahun/Bulan/Tanggal", key="date")
        apbd = st.number_input("Realisasi APBD Triwulan", min_value=0, key="apbd")
        pma = st.number_input("Realisasi PMA Triwulan", min_value=0, key="pma")
        pmdn = st.number_input("Realisasi PMDN Triwulan", min_value=0, key="pmdn")
        infra = st.number_input("Realisasi Belanja Infrastruktur Triwulan", min_value=0, key="infra")
        iph = st.number_input("Data IPH Mingguan Kota Mojokerto", min_value=0.0, format="%.2f", key="iph")
        inflasi = st.number_input("Data Inflasi Bulanan Kota Kediri", min_value=0.0, format="%.2f", key="inflasi")
        ekspor = st.number_input("Data Nilai Ekspor Luar Negeri Triwulanan", min_value=0, key="ekspor")
        padi = st.number_input("Produksi Komoditas Padi Triwulanan", min_value=0, key="padi")

        submit_button = st.form_submit_button("Submit Econostat Details")
        if submit_button:
            new_row = pd.DataFrame({
                "Tanggal": [date.strftime("%d/%m/%Y")],  # format DD/MM/YYYY
                "Realisasi APBD": [apbd],
                "Realisasi PMA": [pma],
                "Realisasi PMDN": [pmdn],
                "Belanja Infrastruktur": [infra],
                "IPH Mojokerto": [iph],
                "Inflasi Kediri": [inflasi],
                "Ekspor Luar Negeri": [ekspor],
                "Produksi Padi": [padi],
            })
            existing_data = pd.concat([existing_data, new_row], ignore_index=True)
            conn.update(worksheet="Triwulanan", data=existing_data)
            st.success("Data berhasil disubmit dan disimpan!")

            # Reset nilai input ke default agar kosong kembali
            for key in ["date","apbd","pma","pmdn","infra","iph","inflasi","ekspor","padi"]:
                if key in st.session_state:
                    del st.session_state[key]

    if st.button("Next ➡️"):
        st.session_state.page = "grafik"
        st.rerun()

elif st.session_state.page == "grafik":
    st.markdown("<div class='subtitle'>Mohon dicermati baik-baik visualisasi dan tren di bawah ini.</div>", unsafe_allow_html=True)
    st.header("Dashboard Triwulanan")

    df = existing_data.copy()
    if "Tanggal" in df.columns:
        # Konversi tipe data dengan dayfirst=True
        df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce", dayfirst=True)
        df["Realisasi APBD"] = pd.to_numeric(df["Realisasi APBD"], errors="coerce").astype("Int64")
        df["Realisasi PMA"] = pd.to_numeric(df["Realisasi PMA"], errors="coerce").astype("Int64")
        df["Realisasi PMDN"] = pd.to_numeric(df["Realisasi PMDN"], errors="coerce").astype("Int64")
        df["Belanja Infrastruktur"] = pd.to_numeric(df["Belanja Infrastruktur"], errors="coerce").astype("Int64")
        df["Ekspor Luar Negeri"] = pd.to_numeric(df["Ekspor Luar Negeri"], errors="coerce").astype("Int64")
        df["Produksi Padi"] = pd.to_numeric(df["Produksi Padi"], errors="coerce").astype("Int64")
        df["IPH Mojokerto"] = pd.to_numeric(df["IPH Mojokerto"], errors="coerce").astype("float64")
        df["Inflasi Kediri"] = pd.to_numeric(df["Inflasi Kediri"], errors="coerce").astype("float64")

        df["Tahun"] = df["Tanggal"].dt.year.astype("Int64")
        df["Triwulan"] = df["Tanggal"].dt.quarter
        df = df.set_index("Tanggal")

        tahun_list = sorted(df["Tahun"].dropna().unique())
        selected_year = st.selectbox("Pilih Tahun", tahun_list)

        mode = st.radio("Pilih Mode Tampilan", ("Seluruh Tahun", "Satu Triwulan"))
        if mode == "Satu Triwulan":
            triwulan_list = [1,2,3,4]
            selected_quarter = st.selectbox("Pilih Triwulan (Q1-Q4)", triwulan_list)
            df_filtered = df[(df["Tahun"] == selected_year) & (df["Triwulan"] == selected_quarter)]
        else:
            df_filtered = df[df["Tahun"] == selected_year]

        if not df_filtered.empty:
            latest = df_filtered.iloc[-1]

            # Hitung delta dibandingkan data sebelumnya
            if len(df_filtered) > 1:
                prev = df_filtered.iloc[-2]
                delta_apbd = latest["Realisasi APBD"] - prev["Realisasi APBD"]
                delta_pma = latest["Realisasi PMA"] - prev["Realisasi PMA"]
                delta_pmdn = latest["Realisasi PMDN"] - prev["Realisasi PMDN"]
            else:
                delta_apbd = delta_pma = delta_pmdn = 0

            # Metrics dengan delta
            col1, col2, col3 = st.columns(3)
            col1.metric("APBD", f"{latest['Realisasi APBD']:,}", f"{delta_apbd:,}")
            # Metrics dengan delta
            col1, col2, col3 = st.columns(3)
            col1.metric("APBD", f"{latest['Realisasi APBD']:,}", f"{delta_apbd:,}")
            col2.metric("PMA", f"{latest['Realisasi PMA']:,}", f"{delta_pma:,}")
            col3.metric("PMDN", f"{latest['Realisasi PMDN']:,}", f"{delta_pmdn:,}")

            # Grafik tren APBD, PMA, PMDN, Infrastruktur
            st.subheader(f"Tren {mode} Tahun {selected_year}")
            st.line_chart(df_filtered[["Realisasi APBD","Realisasi PMA","Realisasi PMDN","Belanja Infrastruktur"]])

            # Grafik Ekspor
            st.subheader("Tren Ekspor Luar Negeri per Triwulan")
            fig1, ax1 = plt.subplots(figsize=(8,5))
            ax1.plot(df_filtered.index, df_filtered["Ekspor Luar Negeri"], color="tab:green", marker='o')
            ax1.set_title(f"Ekspor Luar Negeri Tahun {selected_year}", fontsize=16, fontweight="bold")
            ax1.set_xlabel("Periode")
            ax1.set_ylabel("Nilai Ekspor (Rp)")
            st.pyplot(fig1)

            # Grafik Produksi Padi
            st.subheader("Tren Produksi Padi per Triwulan")
            fig2, ax2 = plt.subplots(figsize=(8,5))
            ax2.plot(df_filtered.index, df_filtered["Produksi Padi"], color="tab:orange", marker='s')
            ax2.set_title(f"Produksi Padi Tahun {selected_year}", fontsize=16, fontweight="bold")
            ax2.set_xlabel("Periode")
            ax2.set_ylabel("Produksi Padi (Ton)")
            st.pyplot(fig2)

            # Dual axis chart IPH vs Inflasi
            st.subheader("Layered Grafik: IPH Mojokerto vs Inflasi Kediri")
            fig, ax1 = plt.subplots(figsize=(8,5))
            ax1.set_xlabel("Periode")
            ax1.set_ylabel("IPH Mojokerto", color="tab:blue")
            ax1.plot(df_filtered.index, df_filtered["IPH Mojokerto"], color="tab:blue", marker='o')
            ax1.tick_params(axis='y', labelcolor="tab:blue")

            ax2 = ax1.twinx()
            ax2.set_ylabel("Inflasi Kediri (%)", color="tab:red")
            ax2.plot(df_filtered.index, df_filtered["Inflasi Kediri"], color="tab:red", marker='s', linestyle='--')
            ax2.tick_params(axis='y', labelcolor="tab:red")

            fig.suptitle(f"Perbandingan IPH Mojokerto dan Inflasi Kediri ({selected_year})",
                        fontsize=18, fontweight="bold")
            st.pyplot(fig)

            # Tombol Back untuk kembali ke halaman form
            if st.button("⬅️ Back"):
                st.session_state.page = "form"
                st.rerun()