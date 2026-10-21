#!/usr/bin/env python3
"""
Hitung Krippendorff's alpha antar dua coder dari Lembar Coding (Codebook 1.0).

Contoh pemakaian:
    python hitung_alpha_krippendorff.py coder1.xlsx coder2.xlsx
    python hitung_alpha_krippendorff.py coder1.xlsx coder2.xlsx --pilot
    python hitung_alpha_krippendorff.py coder1.xlsx coder2.xlsx --boot 5000 --out hasil.xlsx

Dependensi: pandas, numpy, openpyxl  (pip install pandas numpy openpyxl)

Keluaran:
  - tabel alpha per variabel (V4 ordinal, V5-V9 nominal) + selang kepercayaan bootstrap
  - daftar perbedaan kode per unit (untuk diskusi dan adjudikasi)
  - bila --out diberikan, semuanya disimpan ke satu file .xlsx
"""
import argparse
import sys

import numpy as np
import pandas as pd

SHEET = "Lembar Coding"

# variabel yang dihitung: (awalan header, nama, tipe, urutan kategori)
VARIABEL = [
    ("V4", "Relevansi", "ordinal", ["R0", "R1", "R2"]),
    ("V5", "Tema_Utama", "nominal", None),
    ("V6", "Jenis_Pernyataan", "nominal", None),
    ("V7", "Subjek_Norma", "nominal", None),
    ("V8", "Tahap_Scraping", "nominal", None),
    ("V9", "Kebutuhan_SRS", "nominal", None),
]

# nilai sah menurut codebook (untuk validasi)
SAH = {
    "V4": {"R0", "R1", "R2"},
    "V5": {f"T{i:02d}" for i in range(1, 18)} | {"T99"},
    "V6": {f"P{i}" for i in range(1, 10)},
    "V7": {f"S{i}" for i in range(1, 10)},
    "V8": {f"F{i}" for i in range(1, 9)},
    "V9": {f"K{i}" for i in range(1, 6)},
}


# --------------------------------------------------------------------------
# Inti perhitungan alpha
# --------------------------------------------------------------------------
def matriks_koinsidensi(data, kategori):
    """data: array (coder x unit) berisi kode atau None/NaN.
    Mengembalikan matriks koinsidensi o_ck (urutan baris/kolom = kategori)."""
    idx = {c: i for i, c in enumerate(kategori)}
    k = len(kategori)
    o = np.zeros((k, k))
    for u in range(data.shape[1]):
        nilai = [v for v in data[:, u] if v is not None and not pd.isna(v)]
        m = len(nilai)
        if m < 2:  # unit dengan <2 nilai tidak berpasangan
            continue
        for a in range(m):
            for b in range(m):
                if a != b:
                    o[idx[nilai[a]], idx[nilai[b]]] += 1.0 / (m - 1)
    return o


def delta_kuadrat(n_c, tipe):
    """Matriks selisih kuadrat antar kategori."""
    k = len(n_c)
    d = np.zeros((k, k))
    if tipe == "nominal":
        d = 1.0 - np.eye(k)
    elif tipe == "ordinal":
        for c in range(k):
            for e in range(k):
                if c == e:
                    continue
                lo, hi = min(c, e), max(c, e)
                d[c, e] = (n_c[lo : hi + 1].sum() - (n_c[c] + n_c[e]) / 2.0) ** 2
    else:
        raise ValueError(f"Tipe tidak dikenal: {tipe}")
    return d


def alpha_dari_data(data, kategori, tipe):
    """Mengembalikan (alpha, D_o, D_e, n). alpha = NaN bila tidak terdefinisi."""
    o = matriks_koinsidensi(data, kategori)
    n_c = o.sum(axis=1)
    n = n_c.sum()
    if n <= 1:
        return np.nan, np.nan, np.nan, n
    d = delta_kuadrat(n_c, tipe)
    d_o = (o * d).sum() / n
    d_e = (np.outer(n_c, n_c) * d).sum() / (n * (n - 1))
    if d_e == 0:  # semua nilai satu kategori: alpha tidak terdefinisi
        return np.nan, d_o, d_e, n
    return 1.0 - d_o / d_e, d_o, d_e, n


def bootstrap_ci(data, kategori, tipe, n_boot=1000, tingkat=0.95, seed=42):
    """Bootstrap persentil dengan resampling unit (kolom)."""
    rng = np.random.default_rng(seed)
    n_unit = data.shape[1]
    hasil = []
    for _ in range(n_boot):
        pilih = rng.integers(0, n_unit, n_unit)
        a = alpha_dari_data(data[:, pilih], kategori, tipe)[0]
        if not np.isnan(a):
            hasil.append(a)
    if len(hasil) < max(20, n_boot * 0.1):
        return np.nan, np.nan, len(hasil)
    batas = (1 - tingkat) / 2 * 100
    lo, hi = np.percentile(hasil, [batas, 100 - batas])
    return lo, hi, len(hasil)


def interpretasi(a):
    if pd.isna(a):
        return "tidak terdefinisi"
    if a >= 0.800:
        return "dapat diterima (>= 0,800)"
    if a >= 0.667:
        return "tentatif (0,667-0,799)"
    return "revisi dan kode ulang (< 0,667)"


# --------------------------------------------------------------------------
# Membaca lembar coding
# --------------------------------------------------------------------------
def baca_lembar(path):
    df = pd.read_excel(path, sheet_name=SHEET, dtype=str)
    df.columns = [str(c).strip() for c in df.columns]
    kolom = {}
    for c in df.columns:
        awal = c.split()[0]
        if awal in {"V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9", "V12"}:
            kolom[awal] = c
    if "V1" not in kolom:
        sys.exit(f"[!] Kolom 'V1 ID_Unit' tidak ditemukan di {path}")
    out = pd.DataFrame({"ID_Unit": pd.to_numeric(df[kolom["V1"]], errors="coerce")})
    out["Dokumen"] = df[kolom["V3"]] if "V3" in kolom else ""
    out["Pilot"] = df["Pilot"].fillna("") if "Pilot" in df.columns else ""
    for v, *_ in VARIABEL:
        out[v] = df[kolom[v]].astype(object).where(df[kolom[v]].notna(), None)
        out[v] = out[v].map(lambda x: x.strip().upper() if isinstance(x, str) and x.strip() else None)
    out["Kode_Coder"] = df[kolom["V2"]].dropna().iloc[0] if "V2" in kolom and df[kolom["V2"]].notna().any() else ""
    out["V12"] = df[kolom["V12"]] if "V12" in kolom else ""
    out = out.dropna(subset=["ID_Unit"]).copy()
    out["ID_Unit"] = out["ID_Unit"].astype(int)
    return out.set_index("ID_Unit")


def validasi(df, nama):
    for v, *_ in VARIABEL:
        salah = df[v].dropna()[~df[v].dropna().isin(SAH[v])]
        for uid, val in salah.items():
            print(f"[!] {nama}: {v} baris {uid} berisi '{val}' (bukan kode sah)", file=sys.stderr)


# --------------------------------------------------------------------------
# Program utama
# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Krippendorff's alpha dua coder")
    ap.add_argument("coder1")
    ap.add_argument("coder2")
    ap.add_argument("--pilot", action="store_true", help="hanya unit dengan Pilot = Ya")
    ap.add_argument("--boot", type=int, default=1000, help="jumlah resampel bootstrap (default 1000)")
    ap.add_argument("--out", help="simpan hasil ke file .xlsx")
    args = ap.parse_args()

    a, b = baca_lembar(args.coder1), baca_lembar(args.coder2)
    validasi(a, args.coder1)
    validasi(b, args.coder2)

    ids = sorted(set(a.index) & set(b.index))
    if args.pilot:
        pil = {i for i in ids if str(a.loc[i, "Pilot"]).strip().lower() in {"ya", "yes"}}
        ids = sorted(pil)
    # aturan inklusi: hanya baris dengan Isi terisi, yaitu baris yang dikode (V4 terisi);
    # unit yang kosong pada kedua coder otomatis tidak berpasangan dan diabaikan.
    print(f"Coder 1: {a['Kode_Coder'].iloc[0] or args.coder1} | Coder 2: {b['Kode_Coder'].iloc[0] or args.coder2}")
    print(f"Jumlah unit dibandingkan: {len(ids)}" + (" (pilot)" if args.pilot else ""))
    if not ids:
        sys.exit("[!] Tidak ada unit untuk dibandingkan.")

    baris, beda = [], []
    for v, nama, tipe, urutan in VARIABEL:
        data = np.array([[a.loc[i, v] for i in ids], [b.loc[i, v] for i in ids]], dtype=object)
        kategori = urutan or sorted(SAH[v])
        alpha, d_o, d_e, n = alpha_dari_data(data, kategori, tipe)
        lo, hi, n_ok = bootstrap_ci(data, kategori, tipe, args.boot)
        lengkap = [(x is not None) and (y is not None) for x, y in zip(data[0], data[1])]
        sama = sum(1 for x, y, ok in zip(data[0], data[1], lengkap) if ok and x == y)
        baris.append({
            "Variabel": f"{v} {nama}", "Tipe": tipe,
            "Unit berpasangan": sum(lengkap),
            "Kesepakatan mentah (%)": round(100 * sama / max(sum(lengkap), 1), 1),
            "D_observasi": d_o, "D_harapan": d_e,
            "Alpha": alpha, "CI95 bawah": lo, "CI95 atas": hi,
            "Interpretasi": interpretasi(alpha),
        })
        for i, x, y in zip(ids, data[0], data[1]):
            if x != y:
                beda.append({
                    "ID_Unit": i, "Dokumen": a.loc[i, "Dokumen"], "Variabel": f"{v} {nama}",
                    "Coder 1": x, "Coder 2": y,
                    "Catatan C1": a.loc[i, "V12"], "Catatan C2": b.loc[i, "V12"],
                    "Keputusan adjudikasi": "",
                })

    hasil = pd.DataFrame(baris)
    daftar_beda = pd.DataFrame(beda)

    pd.set_option("display.width", 200, "display.max_columns", 20)
    tampil = hasil.copy()
    for c in ["D_observasi", "D_harapan", "Alpha", "CI95 bawah", "CI95 atas"]:
        tampil[c] = tampil[c].map(lambda x: "n/a" if pd.isna(x) else f"{x:.3f}")
    print("\n=== Krippendorff's alpha per variabel ===")
    print(tampil.to_string(index=False))
    print(f"\n=== Perbedaan kode ({len(daftar_beda)} sel) ===")
    print(daftar_beda.drop(columns=["Catatan C1", "Catatan C2"]).to_string(index=False) if len(daftar_beda) else "Tidak ada perbedaan.")
    if args.pilot or len(ids) < 30:
        print("\nCatatan: sampel kecil. Alpha pilot hanya diagnostik, bukan bukti reliabilitas (Codebook Bagian 13).")
    print("Alpha 'n/a' berarti tidak terdefinisi (mis. semua nilai satu kategori sehingga D_harapan = 0).")

    if args.out:
        with pd.ExcelWriter(args.out, engine="openpyxl") as w:
            hasil.to_excel(w, sheet_name="Alpha", index=False)
            daftar_beda.to_excel(w, sheet_name="Perbedaan", index=False)
        print(f"\nHasil disimpan ke {args.out}")


if __name__ == "__main__":
    main()
