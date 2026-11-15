from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")
sns.set_theme(style="whitegrid")

BASE_DIR = Path(__file__).parent
BLUE, GREY, ORANGE = "#1f77b4", "#c7c7c7", "#ff7f0e"
URUTAN_SUHU = ["Dingin (<15°C)", "Sejuk (15-25°C)", "Hangat (>25°C)"]
URUTAN_PERMINTAAN = ["Rendah", "Sedang", "Tinggi"]
URUTAN_WAKTU = ["Dini Hari (00-05)", "Pagi (06-10)", "Siang (11-15)", "Sore (16-20)", "Malam (21-23)"]
NAMA_BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
WARNA_TIPE = {"Hari Kerja": BLUE, "Hari Libur/Akhir Pekan": ORANGE}


@st.cache_data
def load_data():
    day = pd.read_csv(BASE_DIR / "main_data.csv", parse_dates=["dteday"])
    hour = pd.read_csv(BASE_DIR / "hour_data.csv", parse_dates=["dteday"])
    return day, hour


day_df, hour_df = load_data()

# ----------------------------------------------------------------- Sidebar
with st.sidebar:
    st.title("🚲 Bike Sharing")
    st.caption("Filter data yang ditampilkan")
    min_date, max_date = day_df["dteday"].min().date(), day_df["dteday"].max().date()
    rentang = st.date_input("Rentang tanggal", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    musim = st.multiselect(
        "Musim", options=["Spring", "Summer", "Fall", "Winter"], default=["Spring", "Summer", "Fall", "Winter"]
    )

if not isinstance(rentang, (tuple, list)) or len(rentang) != 2:
    st.info("Pilih tanggal awal dan tanggal akhir pada sidebar.")
    st.stop()

mulai, akhir = pd.to_datetime(rentang[0]), pd.to_datetime(rentang[1])
day_f = day_df[(day_df["dteday"] >= mulai) & (day_df["dteday"] <= akhir) & (day_df["season_label"].isin(musim))]
hour_f = hour_df[(hour_df["dteday"] >= mulai) & (hour_df["dteday"] <= akhir) & (hour_df["season_label"].isin(musim))]

if day_f.empty:
    st.warning("Tidak ada data pada filter yang dipilih.")
    st.stop()

# ----------------------------------------------------------------- Header & metrik
st.title("Dashboard Analisis Penyewaan Sepeda (2011-2012)")
st.caption("Sumber data: Bike Sharing Dataset (Capital Bikeshare, Washington D.C.)")

total = day_f["cnt"].sum()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Penyewaan", f"{total:,.0f}")
col2.metric("Rata-rata per Hari", f"{day_f['cnt'].mean():,.0f}")
col3.metric("Pengguna Registered", f"{day_f['registered'].sum() / total * 100:.1f}%")
col4.metric("Pengguna Casual", f"{day_f['casual'].sum() / total * 100:.1f}%")

tab1, tab2, tab3, tab4 = st.tabs(["☁️ Cuaca", "⏰ Pola per Jam", "📈 Tren Bulanan", "🌡️ Suhu & Permintaan"])

# ----------------------------------------------------------------- Tab 1: cuaca
with tab1:
    st.subheader("Pengaruh Cuaca terhadap Rata-rata Penyewaan Harian")
    cuaca = day_f.groupby("weather_label")["cnt"].mean().sort_values(ascending=False).reset_index()
    if "Cerah" in cuaca["weather_label"].values:
        dasar = cuaca.loc[cuaca["weather_label"] == "Cerah", "cnt"].iloc[0]
    else:
        dasar = cuaca["cnt"].max()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    warna = [BLUE if v == cuaca["cnt"].max() else GREY for v in cuaca["cnt"]]
    batang = ax.bar(cuaca["weather_label"], cuaca["cnt"], color=warna)
    for rect, nilai in zip(batang, cuaca["cnt"]):
        label = f"{nilai:,.0f}"
        if nilai != dasar:
            label += f"\n({(nilai / dasar - 1) * 100:+.1f}%)"
        ax.text(rect.get_x() + rect.get_width() / 2, rect.get_height() + 40, label, ha="center", va="bottom", fontsize=10)
    ax.set_xlabel("Kondisi Cuaca")
    ax.set_ylabel("Rata-rata Penyewaan per Hari")
    ax.set_ylim(0, cuaca["cnt"].max() * 1.25)
    sns.despine()
    st.pyplot(fig)
    st.caption("Persentase pada batang menunjukkan selisih terhadap hari cerah.")

# ----------------------------------------------------------------- Tab 2: jam
with tab2:
    st.subheader("Pola Penyewaan per Jam: Hari Kerja vs Hari Libur")
    pola = hour_f.groupby(["day_type", "hr"])["cnt"].mean().reset_index()
    kiri, kanan = st.columns([2, 1])
    with kiri:
        fig, ax = plt.subplots(figsize=(9, 4.5))
        for tipe, grup in pola.groupby("day_type"):
            ax.plot(grup["hr"], grup["cnt"], marker="o", linewidth=2, color=WARNA_TIPE[tipe], label=tipe)
            p = grup.loc[grup["cnt"].idxmax()]
            ax.annotate(f"Puncak {int(p['hr']):02d}:00", xy=(p["hr"], p["cnt"]),
                        xytext=(p["hr"] + 0.8, p["cnt"] + 8), fontsize=9, color=WARNA_TIPE[tipe])
        ax.set_xlabel("Jam")
        ax.set_ylabel("Rata-rata Penyewaan per Jam")
        ax.set_xticks(range(0, 24, 2))
        ax.legend(title="Tipe Hari")
        sns.despine()
        st.pyplot(fig)
    with kanan:
        komposisi = hour_f.groupby("day_type")[["casual", "registered"]].sum()
        persen = komposisi.div(komposisi.sum(axis=1), axis=0) * 100
        fig, ax = plt.subplots(figsize=(4.5, 4.5))
        persen.plot(kind="bar", stacked=True, ax=ax, color=[ORANGE, BLUE], width=0.6)
        for c in ax.containers:
            ax.bar_label(c, fmt="%.1f%%", label_type="center", color="white", fontsize=10)
        ax.set_xlabel("")
        ax.set_ylabel("Persentase (%)")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0, fontsize=8)
        ax.legend(["Casual", "Registered"], loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2)
        sns.despine()
        st.pyplot(fig)

# ----------------------------------------------------------------- Tab 3: tren
with tab3:
    st.subheader("Total Penyewaan Bulanan per Tahun")
    bulanan = day_f.groupby(["year", "month"])["cnt"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(10, 4.5))
    warna_tahun = {2011: GREY, 2012: BLUE}
    for tahun, grup in bulanan.groupby("year"):
        ax.plot(grup["month"], grup["cnt"], marker="o", linewidth=2, color=warna_tahun.get(tahun, BLUE), label=str(tahun))
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(NAMA_BULAN)
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Total Penyewaan")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.legend(title="Tahun")
    sns.despine()
    st.pyplot(fig)

    tahunan = day_f.groupby("year")["cnt"].sum()
    if 2011 in tahunan.index and 2012 in tahunan.index:
        st.metric("Pertumbuhan Total 2012 vs 2011", f"{(tahunan[2012] / tahunan[2011] - 1) * 100:.1f}%")
    else:
        st.caption("Pilih rentang tanggal yang mencakup 2011 dan 2012 untuk melihat pertumbuhan YoY.")

# ----------------------------------------------------------------- Tab 4: analisis lanjutan
with tab4:
    st.subheader("Analisis Lanjutan: Binning Suhu, Tingkat Permintaan, dan Waktu")
    kiri, kanan = st.columns(2)
    with kiri:
        silang = pd.crosstab(day_f["temp_category"], day_f["demand_cluster"], normalize="index") * 100
        silang = silang.reindex(index=URUTAN_SUHU, columns=URUTAN_PERMINTAAN).fillna(0)
        fig, ax = plt.subplots(figsize=(6, 4.5))
        sns.heatmap(silang, annot=True, fmt=".1f", cmap="Blues", cbar_kws={"label": "% hari"}, ax=ax)
        ax.set_xlabel("Tingkat Permintaan Harian")
        ax.set_ylabel("Kategori Suhu")
        st.pyplot(fig)
    with kanan:
        waktu = hour_f.groupby(["time_of_day", "day_type"])["cnt"].mean().unstack("day_type").reindex(URUTAN_WAKTU)
        fig, ax = plt.subplots(figsize=(6, 4.5))
        waktu.plot(kind="bar", ax=ax, color=[WARNA_TIPE[c] for c in waktu.columns], width=0.75)
        ax.set_xlabel("")
        ax.set_ylabel("Rata-rata Penyewaan per Jam")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=20)
        ax.legend(title="Tipe Hari")
        sns.despine()
        st.pyplot(fig)
    st.caption("Kategori suhu: Dingin < 15°C, Sejuk 15-25°C, Hangat > 25°C. Tingkat permintaan dibagi tiga kelompok sama besar berdasarkan kuantil jumlah penyewaan harian.")
