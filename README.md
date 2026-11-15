# Proyek Analisis Data: Bike Sharing Dashboard 🚲

Proyek akhir kelas analisis data. Menganalisis Bike Sharing Dataset (2011-2012) untuk menjawab tiga pertanyaan bisnis:

1. Pengaruh kondisi cuaca terhadap rata-rata penyewaan harian.
2. Jam puncak penyewaan hari kerja vs hari libur serta komposisi pengguna casual vs registered.
3. Pertumbuhan penyewaan 2012 dibandingkan 2011 (YoY) dan musim dengan pertumbuhan tertinggi.

Analisis lanjutan: manual grouping dan binning (kategori suhu, waktu dalam sehari, tingkat permintaan).

## Struktur Direktori

```
submission
├───dashboard
│   ├───main_data.csv     (data harian yang sudah bersih)
│   ├───hour_data.csv     (data per jam yang sudah bersih)
│   └───dashboard.py
├───data
│   ├───day.csv
│   └───hour.csv
├───notebook.ipynb
├───README.md
├───requirements.txt
└───url.txt
```

## Setup Environment

Menggunakan Anaconda:
```
conda create --name main-ds python=3.11
conda activate main-ds
pip install -r requirements.txt
```

Menggunakan Shell/Terminal:
```
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Menjalankan Dashboard

Dari folder utama proyek (`submission`):
```
streamlit run dashboard/dashboard.py
```

Dashboard akan terbuka di browser pada alamat `http://localhost:8501`.
