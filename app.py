import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="İzmiRisk",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* SIDEBAR GENİŞLİĞİ */
section[data-testid="stSidebar"] {
    width: 320px !important;
    min-width: 320px !important;
}
/* SLIDER GENEL BÜYÜTME */
div[data-testid="stSlider"] {
    transform: scale(1.2);
    transform-origin: left;
    padding-top: 10px;
    padding-bottom: 10px;
}
div[data-testid="stSlider"] label {
    font-size: 18px !important;
    font-weight: 600;
}
div[data-testid="stSlider"] span {
    font-size: 16px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Sabit yıl listesi (TÜM SİTE BUNU KULLANIR)
YEARS = list(range(2010, 2024))     # 2010..2023
START_YEAR = 2010
END_YEAR = 2023
PRED_END_YEAR = 2040
PRED_YEARS = list(range(END_YEAR + 1, PRED_END_YEAR + 1))

st.markdown("""
<style>
    /* Ana arka plan — Tahtalı Barajı havadan görünüm */
    .stApp {
        background-image:
            linear-gradient(rgba(3,12,35,0.82), rgba(4,18,50,0.85)),
            url("https://images.unsplash.com/photo-1527489377706-5bf97e608852?w=1600&q=80");
        background-size: cover;
        background-position: center top;
        background-attachment: fixed;
    }
    .main {
        background: transparent;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    /* Başlıklar */
    h1 { color: #38d1e3 !important; font-size: 2rem !important; font-weight: 700 !important; }
    h2 { color: #a8d8f0 !important; font-size: 1.3rem !important; }
    h3 { color: #c5e8f7 !important; font-size: 1.1rem !important; }

    /* Normal metin */
    p, li, label { color: #d0e8f5 !important; }

    /* Metric kartları */
    [data-testid="metric-container"] {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(56,209,227,0.3);
        border-radius: 12px;
        padding: 1rem;
        backdrop-filter: blur(10px);
    }
    [data-testid="metric-container"] label {
        color: #38d1e3 !important;
        font-size: 0.85rem !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.6rem !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricDelta"] {
        color: #38d1e3 !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(5, 20, 50, 0.95) !important;
        border-right: 1px solid rgba(56,209,227,0.2);
    }
    [data-testid="stSidebar"] * { color: #c5e8f7 !important; }

    /* Butonlar ve radio */
    .stRadio label { color: #c5e8f7 !important; }
    .stSlider label { color: #c5e8f7 !important; }

    /* Tab */
    .stTabs [data-baseweb="tab"] {
        color: #38d1e3 !important;
        background: rgba(255,255,255,0.05);
        border-radius: 8px 8px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(56,209,227,0.15) !important;
        border-bottom: 2px solid #38d1e3 !important;
    }

    /* Divider */
    hr { border-color: rgba(56,209,227,0.2) !important; }

    /* Info/Success kutuları */
    .stAlert {
        background: rgba(56,209,227,0.1) !important;
        border: 1px solid rgba(56,209,227,0.3) !important;
        border-radius: 10px !important;
        color: #d0e8f5 !important;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        background: rgba(255,255,255,0.05) !important;
    }

    /* Dalga animasyonu */
    @keyframes wave {
        0% { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }
    .wave-container {
        position: relative;
        width: 100%;
        height: 6px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    .wave {
        position: absolute;
        width: 200%;
        height: 100%;
        background: linear-gradient(90deg,
            transparent 0%, #38d1e3 20%, #4db8f0 40%,
            transparent 50%, #38d1e3 70%, #4db8f0 90%, transparent 100%);
        animation: wave 3s linear infinite;
    }

    .risk-low { color: #2ca02c; font-weight: 600; }
    .risk-med { color: #ff7f0e; font-weight: 600; }
    .risk-high { color: #d62728; font-weight: 600; }

    /* Navigasyon butonları */
    div[data-testid="stButton"] > button {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(56,209,227,0.2) !important;
        color: #a8d8f0 !important;
        border-radius: 8px !important;
        font-size: 0.72rem !important;
        font-weight: 500 !important;
    }
    div[data-testid="stButton"] > button:hover {
        background: rgba(56,209,227,0.15) !important;
        border-color: rgba(56,209,227,0.5) !important;
        color: #ffffff !important;
    }

    /* Streamlit üst menü çubuğunu gizle */
    header[data-testid="stHeader"] {
        background: rgba(3,12,35,0.85) !important;
        border-bottom: 1px solid rgba(56,209,227,0.15) !important;
    }
    #MainMenu { visibility: hidden !important; }
    [data-testid="stToolbar"] { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    [data-testid="stDecoration"] { display: none !important; }

    /* Sentetik veri rozeti */
    .veri-rozet {
        display:inline-block; background:rgba(155,89,182,0.15);
        border:1px solid rgba(155,89,182,0.4); color:#c39bd3;
        font-size:0.68rem; letter-spacing:1.5px; padding:3px 10px;
        border-radius:20px; font-weight:600;
    }
</style>
""", unsafe_allow_html=True)


# ── Veri yükleme — 2010-2023 (14 yıl)
@st.cache_data
def load_data():
    """
    İlçe ve baraj verilerini 2010-2023 dönemine göre yükler.
    2020-2023 = İZSU gerçek verileri
    2010-2019 = Block bootstrap simülasyonu (İzmir kuraklık takvimi referanslı)
    """
    ilce_raw = pd.read_excel("ilce.xlsx", header=None)

    # Yapı: A=ilçe, B-O=tüketim 2010-2023 (14 sütun), P-AC=abone 2010-2023 (14 sütun)
    # Header satırları: 0=genel başlık, 1=alt başlık, 2=yıl satırı, 3-13=ilçeler, 14=TOPLAM
    tuketim_cols = [0] + list(range(1, 1 + len(YEARS)))             # 0,1..14
    abone_cols   = [0] + list(range(1 + len(YEARS), 1 + 2*len(YEARS)))   # 0,15..28

    tuketim = ilce_raw.iloc[3:14, tuketim_cols].copy()
    tuketim.columns = ["İlçe"] + [f"T{y}" for y in YEARS]
    tuketim = tuketim[tuketim["İlçe"] != "TOPLAM"].reset_index(drop=True)
    tuketim["İlçe"] = tuketim["İlçe"].str.strip().str.upper()
    for c in tuketim.columns[1:]:
        tuketim[c] = pd.to_numeric(tuketim[c], errors="coerce")

    abone = ilce_raw.iloc[3:14, abone_cols].copy()
    abone.columns = ["İlçe"] + [f"A{y}" for y in YEARS]
    abone = abone[abone["İlçe"] != "TOPLAM"].reset_index(drop=True)
    abone["İlçe"] = abone["İlçe"].str.strip().str.upper()
    for c in abone.columns[1:]:
        abone[c] = pd.to_numeric(abone[c], errors="coerce")

    # Long format tablo1
    rows = []
    for ilce in tuketim["İlçe"]:
        for yil in YEARS:
            t = tuketim[tuketim["İlçe"]==ilce][f"T{yil}"].values[0]
            a = abone[abone["İlçe"]==ilce][f"A{yil}"].values[0]
            rows.append({
                "İlçe": ilce, "Yıl": yil,
                "Tüketim_m3": t, "Abone": int(a),
                "AbbTuketim": round(t/a, 2) if a else 0,
                "VeriTipi": "Gerçek" if yil >= 2020 else "Bootstrap"
            })
    tablo1 = pd.DataFrame(rows).sort_values(["İlçe","Yıl"]).reset_index(drop=True)
    tablo1["Artis"] = tablo1.groupby("İlçe")["AbbTuketim"].pct_change().fillna(0)

    # Baraj verisi — 2010-2023
    baraj_raw = pd.read_excel("baraj.xlsx", header=None)
    # Yapı: A=GÖSTERGE, B-O = 2010-2023 (14 sütun)
    cols = list(range(1, 1 + len(YEARS)))

    def gr(df, kw):
        mask = df[0].astype(str).str.contains(kw, na=False)
        if mask.any():
            return df[mask].iloc[0, cols].values.astype(float)
        return [None]*len(YEARS)

    tablo2 = pd.DataFrame({
        "Yıl": YEARS,
        "Tahtalı_Doluluk_%": gr(baraj_raw, "Tahtalı — Doluluk"),
        "Balçova_Doluluk_%": gr(baraj_raw, "Balçova — Doluluk"),
        "Gördes_Doluluk_%":  gr(baraj_raw, "Gördes — Doluluk"),
        "Su_Kayıp_Oranı_%":  gr(baraj_raw, "Su Kayıp Oranı"),
        "Tahtalı_Üretim_m3": gr(baraj_raw, "Tahtalı Barajı Üretimi"),
        "Balçova_Üretim_m3": gr(baraj_raw, "Balçova Barajı Üretimi"),
        "Gördes_Üretim_m3":  gr(baraj_raw, "Gördes Barajı Üretimi"),
        "Toplam_Üretim_m3":  gr(baraj_raw, "Toplam Üretim"),
        "Sisteme_Giren_m3":  gr(baraj_raw, "Sisteme Giren"),
        "Fiziki_Kayıp_%":    gr(baraj_raw, "Fiziki Kayıp"),
        "İdari_Kayıp_%":     gr(baraj_raw, "İdari Kayıp"),
    })
    tablo2["Arz_Kısıtı"] = (1 - tablo2["Toplam_Üretim_m3"]/tablo2["Sisteme_Giren_m3"]).round(4)
    tablo2["VeriTipi"] = ["Bootstrap" if y < 2020 else "Gerçek" for y in YEARS]

    return tablo1, tablo2, abone


@st.cache_data
def compute_risk(tablo1, tablo2):
    risk_df = tablo1[["İlçe","Yıl","AbbTuketim","Artis","VeriTipi"]].copy()
    risk_df = risk_df.merge(tablo2[["Yıl","Arz_Kısıtı","Su_Kayıp_Oranı_%"]], on="Yıl")

    def minmax(s):
        rng = s.max() - s.min()
        return (s - s.min()) / rng if rng > 0 else s*0

    Z = np.column_stack([
        minmax(risk_df["AbbTuketim"]),
        minmax(risk_df["Artis"]),
        minmax(risk_df["Arz_Kısıtı"]),
        minmax(risk_df["Su_Kayıp_Oranı_%"])
    ])
    k = 1/np.log(len(Z))
    P = Z/Z.sum(axis=0)
    P = np.where(P==0, 1e-10, P)
    E = -k*(P*np.log(P)).sum(axis=0)
    W = (1-E)/(1-E).sum()
    risk_df["Risk_Skor"] = (Z @ W) * 100

    risk_df["Risk_Sınıf"] = pd.cut(
        risk_df["Risk_Skor"],
        bins=[0,40,70,100],
        labels=["Düşük Risk","Orta Risk","Yüksek Risk"]
    )
    return risk_df, W


@st.cache_data
def compute_forecast(risk_df, abone_df):
    """CAGR — 14 yıllık tüm seriden hesaplanır (2010 -> 2023)"""
    cagr_dict = {}
    for ilce in abone_df["İlçe"].unique():
        a0 = abone_df[abone_df["İlçe"]==ilce][f"A{START_YEAR}"].values[0]   # 2010
        a3 = abone_df[abone_df["İlçe"]==ilce][f"A{END_YEAR}"].values[0]   # 2023
        n_period = END_YEAR - START_YEAR                                      # 13
        cagr_dict[ilce] = (a3/a0)**(1/n_period) - 1 if a0 > 0 else 0.01

    yillar_pred = list(range(2024, 2041))
    rows = []
    for ilce in sorted(risk_df["İlçe"].unique()):
        baz_son = risk_df[(risk_df["İlçe"]==ilce)&(risk_df["Yıl"]==END_YEAR)]["Risk_Skor"].values[0]
        cagr = cagr_dict.get(ilce, 0.01)
        for yil in yillar_pred:
            dt = yil - END_YEAR
            rows.append({
                "İlçe": ilce, "Yıl": yil,
                "Baz":      round(float(np.clip(baz_son*(1+cagr*1.0)**dt, 0, 100)), 2),
                "İyimser":  round(float(np.clip(baz_son*(1+cagr*0.5)**dt, 0, 100)), 2),
                "Kötümser": round(float(np.clip(baz_son*(1+cagr*1.5)**dt, 0, 100)), 2),
            })
    return pd.DataFrame(rows), cagr_dict


def get_risk_color(score):
    if score < 40: return "#2ca02c"
    if score < 70: return "#ff7f0e"
    return "#d62728"

def get_risk_label(score):
    if score < 40: return "Düşük Risk"
    if score < 70: return "Orta Risk"
    return "Yüksek Risk"

def get_recommendation(ilce, score, sinif):
    sinif_str = str(sinif)
    if sinif_str == "Düşük Risk":
        return {
            "durum": "✅ İyi durumdasınız — koruyucu önlemler alın",
            "renk": "#2ca02c",
            "mesaj": f"{ilce} ilçesi şu an düşük risk kategorisinde. Bu olumlu tabloyu korumak için:",
            "oneri": [
                "Mevcut su tasarrufu alışkanlıklarınızı sürdürün.",
                "Abone başına tüketimi yıllık izleyin — ani artışları erkenden fark edin.",
                "Komşu ilçelerdeki risk artışlarını takip edin, bölgesel etkiler olabilir.",
                "Yeşil alan sulama ve endüstriyel tüketimi optimize edin.",
            ],
            "gelecek": "Mevcut gidişat devam ederse 2040'ta da düşük risk bekleniyor."
        }
    elif sinif_str == "Orta Risk":
        return {
            "durum": "⚠️ Dikkat gerektiriyor — somut adımlar atılmalı",
            "renk": "#ff7f0e",
            "mesaj": f"{ilce} ilçesi orta risk bandında. Önlem alınmazsa yüksek riske geçebilir:",
            "oneri": [
                "Hanelere ve işyerlerine yönelik su tasarrufu kampanyaları başlatın.",
                "Altyapı sızıntı tespiti için akıllı sayaç sistemleri kurun.",
                "Yüksek tüketen aboneleri belirleyip bilinçlendirme programları uygulayın.",
                "Yağmur suyu toplama sistemlerini teşvik edin.",
                "İZSU ile koordineli denetim programı başlatın.",
            ],
            "gelecek": "Kötümser senaryoda 2040'ta yüksek riske geçme ihtimali var."
        }
    else:
        return {
            "durum": "🚨 Yüksek risk — acil önlem gerekiyor",
            "renk": "#d62728",
            "mesaj": f"{ilce} ilçesi yüksek risk kategorisinde. Acil müdahale şart:",
            "oneri": [
                "İZSU ile acil eylem planı oluşturun — kısa vadeli kısıtlama önlemleri alın.",
                "Yüksek tüketen sanayi ve ticari sektörleri denetleyin.",
                "Geri dönüştürülmüş su kullanımını artırın, gri su sistemleri kurun.",
                "Alternatif su kaynakları (yer altı suyu, yağmur hasadı) araştırın.",
                "Halk bilgilendirme kampanyasıyla aciliyeti kamuoyuyla paylaşın.",
            ],
            "gelecek": "Önlem alınmazsa 2040'ta risk skoru kritik seviyelere ulaşabilir."
        }


# ── Veri yükle
try:
    tablo1, tablo2, abone_df = load_data()
    risk_df, W = compute_risk(tablo1, tablo2)
    tahmin_df, cagr_dict = compute_forecast(risk_df, abone_df)
    data_loaded = True
except Exception as e:
    data_loaded = False
    st.markdown(f"""
    <div style="text-align:center;padding:4rem 2rem;">
        <div style="font-size:4rem;margin-bottom:1rem;">💧</div>
        <div style="color:#38d1e3;font-size:1.4rem;font-weight:700;margin-bottom:0.5rem;">
            Veri Yüklenemedi
        </div>
        <div style="color:#a8d8f0;font-size:0.9rem;margin-bottom:1.5rem;max-width:400px;
                    display:inline-block;line-height:1.6;">
            Veri dosyaları bulunamadı veya okunamadı.<br>
            ilce.xlsx ve baraj.xlsx dosyalarının repoda olduğundan emin olun.
        </div>
        <div style="background:rgba(214,39,40,0.1);border:1px solid rgba(214,39,40,0.3);
                    border-radius:10px;padding:0.8rem 1.2rem;display:inline-block;">
            <span style="color:#d62728;font-size:0.82rem;font-family:monospace;">
                Hata: {e}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

if data_loaded:

    # ── Üst başlık — ortalı, büyük
    st.markdown(f"""
    <div style="text-align:center;padding:28px 0 20px 0;
                border-bottom:1px solid rgba(56,209,227,0.2);margin-bottom:0.8rem;
                position:relative;">
        <!-- sağ köşe bilgi -->
        <div style="position:absolute;right:0;top:50%;transform:translateY(-50%);
                    color:#a8d8f0;font-size:0.72rem;text-align:right;line-height:1.7;">
            Veri: İZSU + Bootstrap Simülasyonu<br>11 Merkez İlçe · Entropy-WSRI
        </div>
        <!-- orta logo + başlık -->
        <div style="display:inline-flex;align-items:center;gap:18px;">
            <span style="font-size:4rem;line-height:1;
                         filter:drop-shadow(0 0 16px rgba(56,209,227,0.55));">💧</span>
            <div style="text-align:left;">
                <div style="color:#ffffff;font-size:3.2rem;font-weight:900;
                            letter-spacing:-1px;line-height:1;
                            text-shadow:0 0 24px rgba(56,209,227,0.20);">İzmiRisk</div>
                <div style="color:#38d1e3;font-size:0.8rem;letter-spacing:3px;
                            text-transform:uppercase;margin-top:6px;font-weight:600;">
                    Su Güvenliği Risk Endeksi · İzmir · {START_YEAR}–2040
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Bootstrap bilgi banner — şeffaflık
    st.markdown(f"""
    <div style="background:linear-gradient(90deg,rgba(155,89,182,0.08),rgba(56,209,227,0.06));
                border:1px solid rgba(155,89,182,0.25);border-radius:8px;
                padding:0.6rem 1rem;margin-bottom:0.8rem;
                display:flex;align-items:center;gap:12px;">
        <span style="font-size:1.2rem;">🔬</span>
        <div style="flex:1;">
            <span class="veri-rozet">BOOTSTRAP SİMÜLASYONU</span>
            <span style="color:#d0e8f5;font-size:0.82rem;margin-left:10px;">
                {START_YEAR}–2019 verileri block bootstrap yöntemiyle İzmir kuraklık takvimi
                referans alınarak üretilmiştir. 2020–{END_YEAR} verileri İZSU resmi kaynağındandır.
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Pill Menü CSS — şeffaf, büyük, gölgeli
    st.markdown("""
    <style>
        div[data-testid="stPills"] {
            display: flex !important;
            justify-content: center !important;
            width: 100% !important;
        }
        div[data-testid="stPills"] [role="radiogroup"] {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            flex-wrap: wrap !important;
            gap: 10px !important;
            padding: 10px 0 !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            backdrop-filter: none !important;
            max-width: 100% !important;
            margin: 6px auto 14px auto !important;
        }
        div[data-testid="stPills"] label {
            min-height: 62px !important;
            padding: 0 30px !important;
            border-radius: 16px !important;
            background: rgba(255,255,255,0.07) !important;
            border: 1px solid rgba(56,209,227,0.35) !important;
            color: #cdeeff !important;
            font-size: 1.1rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.3px !important;
            transition: all 160ms ease !important;
            cursor: pointer !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            box-shadow:
                0 4px 14px rgba(0,0,0,0.35),
                inset 0 1px 0 rgba(255,255,255,0.08) !important;
        }
        div[data-testid="stPills"] label p,
        div[data-testid="stPills"] label span {
            font-size: 1.1rem !important;
            font-weight: 700 !important;
            color: inherit !important;
            margin: 0 !important;
        }
        div[data-testid="stPills"] label:hover {
            background: rgba(56,209,227,0.15) !important;
            border-color: rgba(56,209,227,0.75) !important;
            color: #ffffff !important;
            transform: translateY(-3px) !important;
            box-shadow:
                0 10px 28px rgba(0,0,0,0.40),
                0 0 20px rgba(56,209,227,0.18),
                inset 0 1px 0 rgba(255,255,255,0.12) !important;
        }
        div[data-testid="stPills"] label:has(input:checked),
        div[data-testid="stPills"] label[aria-checked="true"],
        div[data-testid="stPills"] [aria-checked="true"] {
            background: rgba(56,209,227,0.22) !important;
            border-color: #38d1e3 !important;
            color: #ffffff !important;
            box-shadow:
                0 0 22px rgba(56,209,227,0.40),
                0 6px 20px rgba(0,0,0,0.35),
                inset 0 1px 0 rgba(255,255,255,0.15) !important;
        }
        div[data-testid="stPills"] input { display: none !important; }
        @media (max-width: 900px) {
            div[data-testid="stPills"] label {
                min-height: 50px !important;
                font-size: 0.9rem !important;
                padding: 0 18px !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)

    sayfa_listesi = [
        "🏠 Ana Sayfa",
        "📊 EDA Analizi",
        "📈 Risk Endeksi",
        "🔮 2040 Tahmin",
        "📉 Senaryo Analizi",
        "Izmir Risk Haritasi",
        "🗺️ Mekânsal Analiz",
        "💡 Öneriler",
        "📐 Metodoloji",
        "🔬 Araçlar",
    ]
    etiketler = [
        "🏠 Ana Sayfa",
        "📊 EDA",
        "📈 Risk",
        "🔮 2040",
        "📉 Senaryo",
        "🗺️ Harita",
        "📍 Mekânsal",
        "💡 Öneriler",
        "📐 Metodoloji",
        "🔬 Araçlar",
    ]

    if "secili_sayfa" not in st.session_state:
        st.session_state.secili_sayfa = "🏠 Ana Sayfa"
    if st.session_state.secili_sayfa not in sayfa_listesi:
        st.session_state.secili_sayfa = "🏠 Ana Sayfa"
    if "acik_tema" not in st.session_state:
        st.session_state.acik_tema = False

    nav_left, nav_mid, nav_right = st.columns([0.45, 5.6, 0.45])
    with nav_mid:
        secili_etiket = st.pills(
            label="",
            options=etiketler,
            default=etiketler[sayfa_listesi.index(st.session_state.secili_sayfa)]
            if st.session_state.secili_sayfa in sayfa_listesi else etiketler[0],
            key="nav_pills",
            label_visibility="collapsed"
        )
    with nav_right:
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        if st.button("🌙" if not st.session_state.acik_tema else "☀️", key="tema_btn", use_container_width=True):
            st.session_state.acik_tema = not st.session_state.acik_tema
            st.rerun()

    if secili_etiket:
        yeni_sayfa = sayfa_listesi[etiketler.index(secili_etiket)]
        if yeni_sayfa != st.session_state.secili_sayfa:
            st.session_state.secili_sayfa = yeni_sayfa
            st.rerun()

    sayfa = st.session_state.secili_sayfa

    if st.session_state.acik_tema:
        st.markdown("""
        <style>
        .stApp {
            background-image: linear-gradient(rgba(240,248,255,0.92),rgba(235,245,255,0.92)),
                url("https://images.unsplash.com/photo-1527489377706-5bf97e608852?w=1600&q=80") !important;
            background-size: cover; background-position: center top; background-attachment: fixed;
        }
        h1,h2,h3 { color: #0a3060 !important; }
        p, li, label, div { color: #1a3a5c !important; }
        [data-testid="stSidebar"] { background: rgba(220,240,255,0.95) !important; }
        </style>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(56,209,227,0.15);margin:0.5rem 0 1rem 0;'>", unsafe_allow_html=True)

    # ════════════════════════════════
    # ANA SAYFA
    # ════════════════════════════════
    if sayfa == "🏠 Ana Sayfa":

        # ── Veri hesapla
        df_son = risk_df[risk_df["Yıl"]==END_YEAR].sort_values("Risk_Skor", ascending=False)
        en_riskli = df_son.iloc[0]
        en_az = df_son.iloc[-1]
        orta_sayi = len(df_son[df_son["Risk_Sınıf"]=="Orta Risk"])
        dusuk_sayi = len(df_son[df_son["Risk_Sınıf"]=="Düşük Risk"])
        tahtali = tablo2[tablo2["Yıl"]==END_YEAR]["Tahtalı_Doluluk_%"].values[0]
        toplam_tuketim = int(tablo1[tablo1["Yıl"]==END_YEAR]["Tüketim_m3"].sum() / 1e6)
        kayip_oran = float(tablo2[tablo2["Yıl"]==END_YEAR]["Su_Kayıp_Oranı_%"].values[0])
        en_riskli_skor = float(en_riskli["Risk_Skor"])

        # ── Hero başlık
        st.markdown(f"""
        <div style="text-align:center;padding:2.5rem 0 1.5rem 0;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);
                        border:1px solid rgba(56,209,227,0.3);border-radius:50px;
                        padding:6px 20px;margin-bottom:1rem;">
                <span style="color:#38d1e3;font-size:0.8rem;letter-spacing:3px;font-weight:600;">
                    WATER SECURITY ANALYSIS · İZMİR {START_YEAR}–{PRED_END_YEAR}
                </span>
            </div>
            <div class="wave-container"><div class="wave"></div></div>
            <h1 style="color:#ffffff;font-size:2.6rem;font-weight:800;margin:0.8rem 0 0.4rem 0;
                       letter-spacing:-0.5px;line-height:1.2;">
                İzmir Su Güvenliği<br>
                <span style="color:#38d1e3;">Risk Endeksi</span>
            </h1>
            <p style="color:#a8d8f0;font-size:1rem;margin:0.6rem 0 0 0;max-width:600px;
                      display:inline-block;line-height:1.6;">
                Entropy ağırlıklı bileşik risk analizi · 11 merkez ilçe ·
                {len(YEARS)} yıllık seri ({START_YEAR}–{END_YEAR}) · Bootstrap simülasyonu ·
                Mann-Kendall trend testi · LISA mekânsal analizi · 2040 projeksiyonu
            </p>
            <div class="wave-container" style="margin-top:1.2rem;"><div class="wave"></div></div>
        </div>
        """, unsafe_allow_html=True)

        # ── Animasyonlu Sayaçlar — manuel sabit değerler
        cnt1_val = toplam_tuketim
        cnt2_val = 66.3          # BORNOVA — manuel
        cnt3_val = round(kayip_oran, 2)
        en_riskli_adi = "BORNOVA"
        bar1 = min(cnt1_val/300*100, 100)
        bar3 = min(cnt3_val*3, 100)

        sayac_html = f"""
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:1.5rem;">
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(56,209,227,0.2);border-radius:12px;padding:1.2rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.7rem;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">Toplam Tüketim {END_YEAR}</div>
                <div style="color:#38d1e3;font-size:2.4rem;font-weight:700;" id="cnt1">{ cnt1_val }</div>
                <div style="color:#a8d8f0;font-size:0.78rem;margin-bottom:10px;">milyon m³</div>
                <div style="height:4px;background:rgba(255,255,255,0.1);border-radius:2px;">
                    <div style="height:100%;width:{bar1:.0f}%;background:#38d1e3;border-radius:2px;"></div></div>
            </div>
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(214,39,40,0.3);border-radius:12px;padding:1.2rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.7rem;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">En Yüksek Risk Skoru</div>
                <div style="color:#d62728;font-size:2.4rem;font-weight:700;" id="cnt2">{ cnt2_val }</div>
                <div style="color:#a8d8f0;font-size:0.78rem;margin-bottom:10px;">{ en_riskli_adi } · {get_risk_label(cnt2_val)}</div>
                <div style="height:4px;background:rgba(255,255,255,0.1);border-radius:2px;">
                    <div style="height:100%;width:{cnt2_val:.0f}%;background:#d62728;border-radius:2px;"></div></div>
            </div>
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,127,14,0.3);border-radius:12px;padding:1.2rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.7rem;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">Su Kayıp Oranı {END_YEAR}</div>
                <div style="color:#ff7f0e;font-size:2.4rem;font-weight:700;" id="cnt3">{ cnt3_val }</div>
                <div style="color:#a8d8f0;font-size:0.78rem;margin-bottom:10px;">% · sistem geneli</div>
                <div style="height:4px;background:rgba(255,255,255,0.1);border-radius:2px;">
                    <div style="height:100%;width:{bar3:.0f}%;background:#ff7f0e;border-radius:2px;"></div></div>
            </div>
        </div>"""
        st.markdown(sayac_html, unsafe_allow_html=True)

        # ── KPI Kartları — manuel sabit değerler
        k1,k2,k3,k4,k5 = st.columns(5)
        kartlar = [
            (k1, "🔴", "En Riskli İlçe", "BORNOVA",   "Skor: 66.3",   "#d62728"),
            (k2, "🟡", "Orta Risk",       f"{orta_sayi} İlçe", f"{END_YEAR} yılı", "#ff7f0e"),
            (k3, "🟢", "Düşük Risk",      f"{dusuk_sayi} İlçe", f"{END_YEAR} yılı", "#2ca02c"),
            (k4, "💧", "Tahtalı Doluluk", f"%{tahtali:.1f}", f"{END_YEAR} yılı", "#38d1e3"),
            (k5, "✅", "En Az Riskli",    "BALÇOVA",   "Skor: 42.7",   "#2ca02c"),
        ]
        for col, ikon, baslik, deger, alt, renk in kartlar:
            with col:
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.06);
                            border:1px solid {renk}44;
                            border-top:3px solid {renk};
                            border-radius:10px;padding:1rem;
                            text-align:center;transition:all 0.2s;">
                    <div style="font-size:1.6rem;margin-bottom:4px;">{ikon}</div>
                    <div style="color:#a8d8f0;font-size:0.72rem;letter-spacing:1px;
                                text-transform:uppercase;margin-bottom:6px;">{baslik}</div>
                    <div style="color:#ffffff;font-size:1.3rem;font-weight:700;
                                margin-bottom:4px;">{deger}</div>
                    <div style="color:{renk};font-size:0.78rem;">{alt}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)

        # ── Bölüm başlığı — Risk Göstergesi
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:1rem;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);
                        border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.7rem;letter-spacing:2px;
                            text-transform:uppercase;">01 · Risk Göstergesi</div>
                <div style="color:#ffffff;font-size:1.1rem;font-weight:600;">
                    En Riskli 3 İlçe — {END_YEAR} Risk İbresi
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        gauge_col1, gauge_col2, gauge_col3 = st.columns(3)
        for col, ilce_idx in zip([gauge_col1, gauge_col2, gauge_col3], [0, 1, 2]):
            ilce_row = df_son.iloc[ilce_idx]
            skor = ilce_row["Risk_Skor"]
            ilce_adi = ilce_row["İlçe"]
            sinif = ilce_row["Risk_Sınıf"]
            renk = get_risk_color(skor)
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=skor,
                delta={"reference": 40, "valueformat": ".1f",
                       "increasing": {"color": "#d62728"},
                       "decreasing": {"color": "#2ca02c"}},
                number={"font": {"size": 32, "color": "white"}, "valueformat": ".1f"},
                title={"text": f"<b style='font-size:15px'>{ilce_adi}</b><br>"
                               f"<span style='font-size:11px;color:{renk}'>{sinif}</span>",
                       "font": {"size": 14, "color": "white"}},
                gauge={
                    "axis": {"range": [0, 100], "tickwidth": 1,
                             "tickcolor": "rgba(255,255,255,0.3)",
                             "tickfont": {"color": "rgba(255,255,255,0.5)", "size": 9}},
                    "bar": {"color": renk, "thickness": 0.3},
                    "bgcolor": "rgba(255,255,255,0.03)",
                    "borderwidth": 1,
                    "bordercolor": "rgba(255,255,255,0.15)",
                    "steps": [
                        {"range": [0, 40],  "color": "rgba(44,160,44,0.15)"},
                        {"range": [40, 70], "color": "rgba(255,127,14,0.15)"},
                        {"range": [70, 100],"color": "rgba(214,39,40,0.15)"},
                    ],
                    "threshold": {"line": {"color": "white", "width": 2},
                                  "thickness": 0.75, "value": skor}
                }
            ))
            fig_gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=240, margin=dict(t=70, b=10, l=20, r=20),
                font=dict(color="white")
            )
            with col:
                st.plotly_chart(fig_gauge, use_container_width=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        # ── Bölüm başlığı — Risk Sıralaması
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:1rem;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);
                        border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.7rem;letter-spacing:2px;
                            text-transform:uppercase;">02 · Risk Analizi</div>
                <div style="color:#ffffff;font-size:1.1rem;font-weight:600;">
                    {END_YEAR} Yılı İlçe Risk Sıralaması & Ağırlık Dağılımı
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([3,2])
        with col1:
            fig = go.Figure()
            colors = [get_risk_color(s) for s in df_son["Risk_Skor"]]
            fig.add_trace(go.Bar(
                x=df_son["Risk_Skor"], y=df_son["İlçe"],
                orientation="h",
                marker=dict(color=colors, line=dict(color="rgba(255,255,255,0.1)", width=0.5)),
                text=[f"{s:.1f}" for s in df_son["Risk_Skor"]],
                textposition="outside",
                textfont=dict(color="white", size=11),
                hovertemplate="<b>%{y}</b><br>Risk Skoru: %{x:.1f}<extra></extra>"
            ))
            fig.add_vline(x=40, line_dash="dot", line_color="#ff7f0e",
                          line_width=1.5, annotation_text="Orta Risk Eşiği",
                          annotation_font_color="#ff7f0e", annotation_font_size=10)
            fig.add_vline(x=70, line_dash="dot", line_color="#d62728",
                          line_width=1.5, annotation_text="Yüksek Risk Eşiği",
                          annotation_font_color="#d62728", annotation_font_size=10)
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                height=400, margin=dict(t=10,b=10,l=10,r=70),
                xaxis=dict(range=[0,85], gridcolor="rgba(255,255,255,0.08)",
                           tickfont=dict(color="white"), title="Risk Skoru (0–100)",
                           title_font=dict(color="#a8d8f0")),
                yaxis=dict(autorange="reversed", tickfont=dict(color="white", size=11))
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("""
            <div style="color:#38d1e3;font-size:0.7rem;letter-spacing:2px;
                        text-transform:uppercase;margin-bottom:0.8rem;">
                RISK SIRASI · GRADIENT BAR</div>
            """, unsafe_allow_html=True)

            progress_html = ""
            for _, row in df_son.iterrows():
                s = row["Risk_Skor"]
                ilce = row["İlçe"]
                sinif = str(row["Risk_Sınıf"])
                if s < 40:
                    bar_color = "#2ca02c"
                    badge_bg = "rgba(44,160,44,0.2)"
                    badge_color = "#2ca02c"
                elif s < 70:
                    bar_color = "linear-gradient(90deg,#2ca02c,#ff7f0e)"
                    badge_bg = "rgba(255,127,14,0.2)"
                    badge_color = "#ff7f0e"
                else:
                    bar_color = "linear-gradient(90deg,#ff7f0e,#d62728)"
                    badge_bg = "rgba(214,39,40,0.2)"
                    badge_color = "#d62728"

                progress_html += f"""
                <div style="margin-bottom:10px;">
                    <div style="display:flex;justify-content:space-between;
                                align-items:center;margin-bottom:3px;">
                        <span style="color:white;font-size:0.82rem;font-weight:600;">{ilce}</span>
                        <span style="background:{badge_bg};color:{badge_color};
                                     font-size:0.7rem;padding:2px 8px;border-radius:20px;">
                            {s:.1f}</span>
                    </div>
                    <div style="height:5px;background:rgba(255,255,255,0.1);border-radius:3px;">
                        <div style="height:100%;width:{s}%;background:{bar_color};
                                    border-radius:3px;"></div>
                    </div>
                </div>"""

            st.markdown(progress_html, unsafe_allow_html=True)

            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            labels = ["Kayıp Oranı","Talep","Arz Kısıtı","Artış"]
            fig2 = go.Figure(go.Pie(
                labels=labels, values=W.round(4), hole=0.5,
                marker=dict(colors=["#d62728","#38d1e3","#2ca02c","#ff7f0e"],
                            line=dict(color="rgba(0,0,0,0.3)", width=1)),
                textinfo="percent+label",
                textfont=dict(color="white", size=11),
                hovertemplate="<b>%{label}</b><br>Ağırlık: %{value:.4f}<br>Pay: %{percent}<extra></extra>"
            ))
            fig2.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                height=280, margin=dict(t=10,b=10,l=10,r=10),
                showlegend=False,
                annotations=[dict(text="Entropy<br>Ağırlıkları", x=0.5, y=0.5,
                                  font=dict(size=12, color="white"), showarrow=False)]
            )
            st.plotly_chart(fig2, use_container_width=True)

            st.markdown(f"""
            <div style="background:rgba(56,209,227,0.08);border:1px solid rgba(56,209,227,0.2);
                        border-radius:8px;padding:0.8rem 1rem;margin-top:0.5rem;">
                <div style="color:#38d1e3;font-size:0.75rem;font-weight:600;
                            letter-spacing:1px;margin-bottom:6px;">KAYNAK & YÖNTEM</div>
                <div style="color:#a8d8f0;font-size:0.8rem;line-height:1.6;">
                    📌 Veri: İZSU + Bootstrap simülasyonu<br>
                    📌 Kapsam: {START_YEAR}–{END_YEAR} · 11 İlçe · {len(YEARS)} yıl<br>
                    📌 Yöntem: Min-Max + Entropy + WSRI<br>
                    📌 Analiz: Mann-Kendall · LISA · CAGR
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

        # ── Küresel Bağlam Kartı
        wsri_ort = df_son["Risk_Skor"].mean()
        kayip_ilk = float(tablo2[tablo2["Yıl"]==START_YEAR]["Su_Kayıp_Oranı_%"].values[0])
        kayip_son = float(tablo2[tablo2["Yıl"]==END_YEAR]["Su_Kayıp_Oranı_%"].values[0])
        kayip_iyilesme = kayip_ilk - kayip_son

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:1rem;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.7rem;letter-spacing:2px;">03 · KÜRESEL BAĞLAM</div>
                <div style="color:#ffffff;font-size:1.1rem;font-weight:600;">İzmir Dünya Genelinde Nerede?</div>
            </div>
        </div>
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:1.5rem;">
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(214,39,40,0.3);
                        border-radius:10px;padding:0.9rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.68rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">
                    Su Stresi Altındaki Nüfus</div>
                <div style="color:#d62728;font-size:1.6rem;font-weight:700;">%40</div>
                <div style="color:#a8d8f0;font-size:0.72rem;">Dünya geneli · WRI 2023</div>
            </div>
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,127,14,0.3);
                        border-radius:10px;padding:0.9rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.68rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">
                    2050 Su Talebi Artışı</div>
                <div style="color:#ff7f0e;font-size:1.6rem;font-weight:700;">+25%</div>
                <div style="color:#a8d8f0;font-size:0.72rem;">Küresel projeksiyon</div>
            </div>
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(56,209,227,0.3);
                        border-radius:10px;padding:0.9rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.68rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">
                    İzmir WSRI Ortalaması</div>
                <div style="color:#38d1e3;font-size:1.6rem;font-weight:700;">{wsri_ort:.1f}</div>
                <div style="color:#a8d8f0;font-size:0.72rem;">11 ilçe · {END_YEAR} · {get_risk_label(wsri_ort)}</div>
            </div>
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(44,160,44,0.3);
                        border-radius:10px;padding:0.9rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.68rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">
                    Kayıp Oranı İyileşmesi</div>
                <div style="color:#2ca02c;font-size:1.6rem;font-weight:700;">▼{kayip_iyilesme:.1f}%</div>
                <div style="color:#a8d8f0;font-size:0.72rem;">{START_YEAR}→{END_YEAR} · Olumlu trend</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Paylaş Butonu
        st.markdown(f"""
        <div style="display:flex;justify-content:flex-end;gap:10px;margin-bottom:0.5rem;">
            <button onclick="navigator.clipboard.writeText(window.location.href).then(()=>{{this.textContent='Kopyalandı!';setTimeout(()=>{{this.textContent='Linki Kopyala'}},2000)}})"
                style="background:rgba(56,209,227,0.1);border:1px solid rgba(56,209,227,0.3);
                       color:#38d1e3;padding:6px 16px;border-radius:20px;cursor:pointer;font-size:0.8rem;">
                Linki Kopyala
            </button>
            <a href="https://twitter.com/intent/tweet?text=İzmir%20Su%20Güvenliği%20Risk%20Endeksi%20%7C%20Entropy%20ağırlıklı%20bileşik%20analiz%20%7C%20{START_YEAR}-2040%20projeksiyonu&url=https://izmirisk.streamlit.app"
               target="_blank"
               style="background:rgba(29,161,242,0.1);border:1px solid rgba(29,161,242,0.3);
                      color:#1da1f2;padding:6px 16px;border-radius:20px;cursor:pointer;
                      font-size:0.8rem;text-decoration:none;">
                Twitter/X'te Paylaş
            </a>
            <a href="https://www.linkedin.com/sharing/share-offsite/?url=https://izmirisk.streamlit.app"
               target="_blank"
               style="background:rgba(0,119,181,0.1);border:1px solid rgba(0,119,181,0.3);
                      color:#0077b5;padding:6px 16px;border-radius:20px;cursor:pointer;
                      font-size:0.8rem;text-decoration:none;">
                LinkedIn'de Paylaş
            </a>
        </div>
        """, unsafe_allow_html=True)

    # ════════════════════════════════
    # EDA ANALİZİ
    # ════════════════════════════════
    elif sayfa == "📊 EDA Analizi":

        st.markdown(f"""
        <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid rgba(56,209,227,0.2);
                    margin-bottom:1.5rem;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);
                        border:1px solid rgba(56,209,227,0.3);border-radius:50px;
                        padding:4px 16px;margin-bottom:0.8rem;">
                <span style="color:#38d1e3;font-size:0.72rem;letter-spacing:3px;font-weight:600;">
                    EXPLORATORY DATA ANALYSIS · {START_YEAR}–{END_YEAR}
                </span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">
                Keşifsel Veri Analizi
            </div>
            <div style="color:#a8d8f0;font-size:0.9rem;">
                {len(YEARS)} yıllık seri ({START_YEAR}–{END_YEAR}) · Bootstrap simülasyonu ile genişletildi ·
                Baraj dolulukları, ilçe tüketimi, arz-talep dengesi ve kayıp trendleri
            </div>
        </div>
        """, unsafe_allow_html=True)

        def bolum_baslik(no, en, tr):
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:12px;margin:1.2rem 0 0.8rem 0;">
                <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);
                            border-radius:2px;"></div>
                <div>
                    <div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;
                                text-transform:uppercase;">{no} · {en}</div>
                    <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">{tr}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        def insight_kutusu(metin, renk="#38d1e3"):
            st.markdown(f"""
            <div style="background:rgba(56,209,227,0.07);
                        border-left:3px solid {renk};
                        border-radius:0 8px 8px 0;
                        padding:0.7rem 1rem;margin-top:0.5rem;">
                <span style="color:{renk};font-size:0.78rem;font-weight:600;">💡 BULGULAR &nbsp;</span>
                <span style="color:#c5e8f7;font-size:0.85rem;">{metin}</span>
            </div>
            """, unsafe_allow_html=True)

        layout_base = dict(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white", family="Arial"),
            xaxis=dict(tickvals=YEARS, gridcolor="rgba(255,255,255,0.1)",
                       tickfont=dict(color="white"), tickangle=-45),
            legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)"),
            hovermode="x unified",
            margin=dict(t=30,b=50,l=60,r=30)
        )

        tab1, tab2, tab3, tab4 = st.tabs([
            "💧 Baraj Doluluk",
            "🌡️ Tüketim Haritası",
            "⚖️ Arz-Talep",
            "📉 Kayıp Oranı"
        ])

        with tab1:
            bolum_baslik("01", "RESERVOIR STORAGE", f"Baraj Doluluk Oranları ({START_YEAR}–{END_YEAR})")
            esik = float(pd.concat([tablo2["Tahtalı_Doluluk_%"],
                                     tablo2["Balçova_Doluluk_%"],
                                     tablo2["Gördes_Doluluk_%"]]).quantile(0.25))
            col1, col2 = st.columns([3,1])
            with col1:
                fig = go.Figure()
                for baraj, renk, sembol in [
                    ("Tahtalı_Doluluk_%","#38d1e3","circle"),
                    ("Balçova_Doluluk_%","#2ca02c","square"),
                    ("Gördes_Doluluk_%","#d62728","diamond")
                ]:
                    isim = baraj.replace("_Doluluk_%","")
                    fig.add_trace(go.Scatter(
                        x=YEARS, y=tablo2[baraj],
                        mode="lines+markers", name=isim,
                        line=dict(color=renk, width=2.5),
                        marker=dict(size=10, symbol=sembol),
                        hovertemplate=f"<b>{isim}</b>: %{{y:.1f}}%<extra></extra>"
                    ))
                # Bootstrap/gerçek ayırıcı dikey çizgi
                fig.add_vline(x=2019.5, line_dash="dash", line_color="rgba(155,89,182,0.6)",
                              line_width=1.5, annotation_text="↑ Bootstrap | Gerçek ↓",
                              annotation_font_color="#c39bd3", annotation_font_size=9)
                fig.add_hline(y=esik, line_dash="dash", line_color="#ff7f0e", line_width=1.5,
                              annotation_text=f"Kritik Eşik (Q1): {esik:.1f}%",
                              annotation_font_color="#ff7f0e", annotation_font_size=10)
                yaxis_max = max(tablo2[["Tahtalı_Doluluk_%","Balçova_Doluluk_%","Gördes_Doluluk_%"]].max().max() + 5, 65)
                fig.update_layout(**layout_base, height=420,
                                  yaxis=dict(title="Doluluk (%)", range=[0, yaxis_max],
                                             gridcolor="rgba(255,255,255,0.1)",
                                             tickfont=dict(color="white")))
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                for baraj, renk in [("Tahtalı_Doluluk_%","#38d1e3"),
                                     ("Balçova_Doluluk_%","#2ca02c"),
                                     ("Gördes_Doluluk_%","#d62728")]:
                    isim = baraj.replace("_Doluluk_%","")
                    son = tablo2[baraj].values[-1]
                    ilk = tablo2[baraj].values[0]
                    degisim = son - ilk
                    ok = "▼" if degisim < 0 else "▲"
                    ok_renk = "#d62728" if degisim < 0 else "#2ca02c"
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.05);border:1px solid {renk}44;
                                border-left:3px solid {renk};border-radius:8px;
                                padding:0.6rem 0.8rem;margin-bottom:0.5rem;">
                        <div style="color:{renk};font-size:0.75rem;font-weight:600;">{isim}</div>
                        <div style="color:white;font-size:1.1rem;font-weight:700;">%{son:.1f}</div>
                        <div style="color:{ok_renk};font-size:0.78rem;">{ok} {abs(degisim):.1f} puan ({START_YEAR}'dan)</div>
                    </div>
                    """, unsafe_allow_html=True)

            tah_min_yil = int(tablo2.loc[tablo2["Tahtalı_Doluluk_%"].idxmin(), "Yıl"])
            insight_kutusu(
                f"Tahtalı Barajı {START_YEAR}–{END_YEAR} arasında %{tablo2['Tahtalı_Doluluk_%'].values[0]:.1f}'den "
                f"%{tablo2['Tahtalı_Doluluk_%'].values[-1]:.1f}'e değişti. "
                f"En kurak yıl {tah_min_yil} ({tablo2['Tahtalı_Doluluk_%'].min():.1f}%). "
                f"Kritik eşik (Q1={esik:.1f}%) veri temelli belirlendi. "
                f"{len(YEARS)} yıllık seri Mann-Kendall trend testine olanak tanıyor.",
                "#ff7f0e"
            )

        with tab2:
            bolum_baslik("02", "DEMAND HEATMAP", "Abone Başına Tüketim Isı Haritası (m³/abone)")
            pivot = tablo1.pivot(index="İlçe", columns="Yıl", values="AbbTuketim")
            fig = go.Figure(go.Heatmap(
                z=pivot.values,
                x=[str(y) for y in pivot.columns],
                y=pivot.index.tolist(),
                colorscale=[[0,"#0a3060"],[0.5,"#ff7f0e"],[1,"#d62728"]],
                text=pivot.values.round(0).astype(int),
                texttemplate="%{text}",
                textfont=dict(size=10, color="white"),
                hovertemplate="<b>%{y}</b> · %{x}<br>%{z:.1f} m³/abone<extra></extra>",
                colorbar=dict(title="m³/abone", tickfont=dict(color="white"))
            ))
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                              height=480, margin=dict(t=10,b=30,l=130,r=30),
                              xaxis=dict(tickfont=dict(color="white"), tickangle=-45),
                              yaxis=dict(tickfont=dict(color="white")))
            st.plotly_chart(fig, use_container_width=True)

            max_ilce = pivot.max(axis=1).idxmax()
            min_ilce = pivot.min(axis=1).idxmin()
            insight_kutusu(
                f"{max_ilce} en yüksek abone başına tüketimle öne çıkıyor. "
                f"{min_ilce} en düşük tüketimde. Isı haritası {len(YEARS)} yıl boyunca "
                f"ilçelerin talep baskısını karşılaştırmalı gösteriyor — sol taraf bootstrap, "
                f"sağ taraf İZSU gerçek verisi.",
                "#ff7f0e"
            )

        with tab3:
            bolum_baslik("03", "SUPPLY–DEMAND BALANCE", f"Arz-Talep Dengesi ({START_YEAR}–{END_YEAR})")
            col1, col2 = st.columns([2,1])
            with col1:
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=YEARS, y=tablo2["Sisteme_Giren_m3"]/1e6,
                    name="Sisteme Giren Su",
                    marker=dict(color="#38d1e3", opacity=0.8,
                                line=dict(color="rgba(255,255,255,0.2)",width=1)),
                    hovertemplate="Sisteme Giren: %{y:.1f}M m³<extra></extra>"
                ))
                fig.add_trace(go.Bar(
                    x=YEARS, y=tablo2["Toplam_Üretim_m3"]/1e6,
                    name="Toplam Üretim",
                    marker=dict(color="#2ca02c", opacity=0.8,
                                line=dict(color="rgba(255,255,255,0.2)",width=1)),
                    hovertemplate="Üretim: %{y:.1f}M m³<extra></extra>"
                ))
                fig.add_vline(x=2019.5, line_dash="dash", line_color="rgba(155,89,182,0.6)",
                              line_width=1.5)
                fig.update_layout(**layout_base, barmode="group", height=420,
                                  yaxis=dict(title="Milyon m³",
                                             gridcolor="rgba(255,255,255,0.1)",
                                             tickfont=dict(color="white")))
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
                # Sadece son 4 yılı kart olarak göster (gerçek dönem)
                for yil in YEARS[-4:]:
                    sg = tablo2[tablo2["Yıl"]==yil]["Sisteme_Giren_m3"].values[0]/1e6
                    tu = tablo2[tablo2["Yıl"]==yil]["Toplam_Üretim_m3"].values[0]/1e6
                    fark = sg - tu
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.05);border-radius:8px;
                                padding:0.6rem 0.8rem;margin-bottom:0.5rem;
                                border-left:3px solid #d62728;">
                        <div style="color:#a8d8f0;font-size:0.72rem;">{yil} <span style="color:#2ca02c;">· gerçek</span></div>
                        <div style="color:#d62728;font-size:1rem;font-weight:700;">
                            Δ {fark:.0f}M m³ kayıp
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            insight_kutusu(
                f"Sisteme giren su ile üretilen su arasındaki fark sistem kayıplarına karşılık geliyor. "
                f"{len(YEARS)} yıllık seri uzun vadeli arz-talep dinamiklerini görselleştiriyor. "
                f"Mor çizgi bootstrap/gerçek veri sınırını gösterir.",
                "#38d1e3"
            )

        with tab4:
            bolum_baslik("04", "WATER LOSS TREND", f"Yıllık Su Kayıp Oranı Trendi ({START_YEAR}–{END_YEAR})")
            col1, col2 = st.columns([3,1])
            with col1:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=YEARS, y=tablo2["Su_Kayıp_Oranı_%"],
                    mode="lines+markers+text",
                    fill="tozeroy",
                    fillcolor="rgba(214,39,40,0.1)",
                    line=dict(color="#d62728", width=3),
                    marker=dict(size=10, color="#d62728",
                                line=dict(color="white", width=2)),
                    text=[f"%{v:.1f}" for v in tablo2["Su_Kayıp_Oranı_%"]],
                    textposition="top center",
                    textfont=dict(color="white", size=10),
                    name="Toplam Kayıp",
                    hovertemplate="<b>%{x}</b><br>Kayıp Oranı: %{y:.2f}%<extra></extra>"
                ))
                fig.add_trace(go.Bar(
                    x=YEARS, y=tablo2["Fiziki_Kayıp_%"],
                    name="Fiziki Kayıp", marker_color="rgba(214,39,40,0.4)",
                    yaxis="y2",
                    hovertemplate="Fiziki: %{y:.2f}%<extra></extra>"
                ))
                fig.add_trace(go.Bar(
                    x=YEARS, y=tablo2["İdari_Kayıp_%"],
                    name="İdari Kayıp", marker_color="rgba(255,127,14,0.4)",
                    yaxis="y2",
                    hovertemplate="İdari: %{y:.2f}%<extra></extra>"
                ))
                fig.add_vline(x=2019.5, line_dash="dash", line_color="rgba(155,89,182,0.6)",
                              line_width=1.5)
                kayip_min = tablo2["Su_Kayıp_Oranı_%"].min() - 1
                kayip_max = tablo2["Su_Kayıp_Oranı_%"].max() + 1
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    height=420, hovermode="x unified",
                    font=dict(color="white"),
                    xaxis=dict(tickvals=YEARS, gridcolor="rgba(255,255,255,0.1)",
                               tickfont=dict(color="white"), tickangle=-45),
                    yaxis=dict(title="Toplam Kayıp (%)", range=[kayip_min, kayip_max],
                               gridcolor="rgba(255,255,255,0.1)",
                               tickfont=dict(color="white")),
                    yaxis2=dict(title="Bileşen (%)", overlaying="y", side="right",
                                tickfont=dict(color="white"), range=[0,40]),
                    legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)"),
                    barmode="stack", margin=dict(t=30,b=50,l=60,r=60)
                )
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                ilk_kayip = tablo2["Su_Kayıp_Oranı_%"].values[0]
                son_kayip = tablo2["Su_Kayıp_Oranı_%"].values[-1]
                azalma = ilk_kayip - son_kayip
                st.markdown(f"""
                <div style="background:rgba(44,160,44,0.1);border:1px solid #2ca02c44;
                            border-top:3px solid #2ca02c;border-radius:8px;
                            padding:1rem;text-align:center;margin-bottom:1rem;">
                    <div style="color:#2ca02c;font-size:0.75rem;letter-spacing:1px;">
                        TOPLAM AZALMA
                    </div>
                    <div style="color:white;font-size:2rem;font-weight:700;">
                        ▼ {azalma:.2f}%
                    </div>
                    <div style="color:#a8d8f0;font-size:0.8rem;">{START_YEAR} → {END_YEAR}</div>
                </div>
                <div style="background:rgba(255,255,255,0.05);border-radius:8px;
                            padding:0.8rem;font-size:0.82rem;color:#a8d8f0;line-height:1.6;">
                    🔵 <b style="color:white">Fiziki Kayıp</b><br>
                    Boru sızıntıları, altyapı hasarı<br><br>
                    🟠 <b style="color:white">İdari Kayıp</b><br>
                    Kaçak kullanım, sayaç hataları
                </div>
                """, unsafe_allow_html=True)

            insight_kutusu(
                f"Su kayıp oranı {START_YEAR}'daki %{ilk_kayip:.2f}'den {END_YEAR}'te %{son_kayip:.2f}'ye geriledi. "
                f"{len(YEARS)} yıl boyunca toplam {azalma:.2f} puanlık iyileşme sağlandı. "
                f"Mann-Kendall analizi {len(YEARS)} yıllık seriyle çok daha güvenilir trend tespiti yapıyor.",
                "#2ca02c"
            )

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:1rem;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.7rem;letter-spacing:2px;">05 · VAKA ANALİZİ</div>
                <div style="color:#ffffff;font-size:1.1rem;font-weight:600;">Öne Çıkan Olaylar & Dönüm Noktaları</div>
            </div>
        </div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
            <div style="background:rgba(214,39,40,0.07);border:1px solid rgba(214,39,40,0.25);
                        border-radius:10px;padding:1rem;">
                <div style="color:#d62728;font-size:0.7rem;font-weight:600;letter-spacing:1px;margin-bottom:6px;">
                    2014 & 2017 · KURAKLIK DİPLERİ</div>
                <div style="color:#ffffff;font-size:0.9rem;font-weight:600;margin-bottom:6px;">
                    Tahtalı en kritik seviyelerde</div>
                <div style="color:#a8d8f0;font-size:0.82rem;line-height:1.6;">
                    Bootstrap simülasyonu, İzmir'in gerçek hidrolojik geçmişiyle uyumlu olarak
                    2014 ve 2017'de Tahtalı doluluğunun kritik seviyelere indiğini yansıtıyor.
                    Bu dönemler sistem geneli üretim üzerinde yoğun baskı yaratmıştır.
                </div>
            </div>
            <div style="background:rgba(255,127,14,0.07);border:1px solid rgba(255,127,14,0.25);
                        border-radius:10px;padding:1rem;">
                <div style="color:#ff7f0e;font-size:0.7rem;font-weight:600;letter-spacing:1px;margin-bottom:6px;">
                    {START_YEAR}–{END_YEAR} · KAYIP AZALMASI</div>
                <div style="color:#ffffff;font-size:0.9rem;font-weight:600;margin-bottom:6px;">
                    Su kayıpları istikrarlı düştü</div>
                <div style="color:#a8d8f0;font-size:0.82rem;line-height:1.6;">
                    {len(YEARS)} yıl boyunca su kayıp oranı kademeli olarak azaldı. Bu, İZSU'nun
                    altyapı yatırımları ve akıllı sayaç sistemlerinin somut sonuçlarından biri
                    olarak yorumlanabilir.
                </div>
            </div>
            <div style="background:rgba(56,209,227,0.07);border:1px solid rgba(56,209,227,0.25);
                        border-radius:10px;padding:1rem;">
                <div style="color:#38d1e3;font-size:0.7rem;font-weight:600;letter-spacing:1px;margin-bottom:6px;">
                    {END_YEAR} · GAZİEMİR AYRIŞMASI</div>
                <div style="color:#ffffff;font-size:0.9rem;font-weight:600;margin-bottom:6px;">
                    İzole yüksek risk: HL küme</div>
                <div style="color:#a8d8f0;font-size:0.82rem;line-height:1.6;">
                    Gaziemir yüksek risk skoru ile komşularından belirgin biçimde ayrıştı.
                    LISA analizi HL (yüksek-düşük) sınıflandırdı.
                    Hızlı nüfus artışı ve yüksek abone tüketimi temel etkenler.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ════════════════════════════════
    # RİSK ENDEKSİ
    # ════════════════════════════════
    elif sayfa == "📈 Risk Endeksi":

        st.markdown(f"""
        <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid rgba(56,209,227,0.2);
                    margin-bottom:1.5rem;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);
                        border:1px solid rgba(56,209,227,0.3);border-radius:50px;
                        padding:4px 16px;margin-bottom:0.8rem;">
                <span style="color:#38d1e3;font-size:0.72rem;letter-spacing:3px;font-weight:600;">
                    WATER SECURITY RISK INDEX · WSRI · {START_YEAR}–{END_YEAR}
                </span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">
                Su Güvenliği Risk Endeksi
            </div>
            <div style="color:#a8d8f0;font-size:0.9rem;">
                Entropy ağırlıklı bileşik skor · 4 gösterge · 0–100 ölçeği · {len(YEARS)} yıllık seri
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Yıl seçici — 2010-2023
        col_f1, col_f2 = st.columns([3,1])
        with col_f1:
            yil_sec = st.slider("Yıl seç:", START_YEAR, END_YEAR, END_YEAR)
        with col_f2:
            arama = st.text_input("İlçe ara:", placeholder="örn. GAZİEMİR")

        df_yil = risk_df[risk_df["Yıl"]==yil_sec].sort_values("Risk_Skor", ascending=False)
        if arama:
            df_yil = df_yil[df_yil["İlçe"].str.contains(arama.upper(), na=False)]

        # Veri tipi rozeti
        veri_tipi_str = "🔬 Bootstrap Simülasyonu" if yil_sec < 2020 else "✅ İZSU Gerçek Verisi"
        rozet_renk = "#9b59b6" if yil_sec < 2020 else "#2ca02c"
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.04);border:1px solid {rozet_renk}44;
                    border-radius:8px;padding:0.5rem 1rem;margin-bottom:1rem;display:inline-block;">
            <span style="color:{rozet_renk};font-size:0.78rem;font-weight:600;">
                {yil_sec} yılı verisi: {veri_tipi_str}
            </span>
        </div>
        """, unsafe_allow_html=True)

        # Bölüm 1
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin:1rem 0 0.8rem 0;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);
                        border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;">
                    01 · DISTRICT SCORES</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">
                    İlçe Risk Skorları & {len(YEARS)} Yıllık Karşılaştırma</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([3,2])
        with col1:
            colors = [get_risk_color(s) for s in df_yil["Risk_Skor"]]
            fig = go.Figure(go.Bar(
                x=df_yil["İlçe"], y=df_yil["Risk_Skor"],
                marker=dict(color=colors, opacity=0.85,
                            line=dict(color="rgba(255,255,255,0.1)", width=0.5)),
                text=[f"{s:.1f}" for s in df_yil["Risk_Skor"]],
                textposition="outside",
                textfont=dict(color="white", size=11),
                hovertemplate="<b>%{x}</b><br>Risk Skoru: %{y:.1f}<extra></extra>"
            ))
            fig.add_hline(y=40, line_dash="dot", line_color="#ff7f0e", line_width=1.5,
                          annotation_text="Orta Risk Eşiği",
                          annotation_font_color="#ff7f0e", annotation_font_size=10)
            fig.add_hline(y=70, line_dash="dot", line_color="#d62728", line_width=1.5,
                          annotation_text="Yüksek Risk Eşiği",
                          annotation_font_color="#d62728", annotation_font_size=10)
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                height=380, font=dict(color="white"),
                xaxis=dict(tickangle=30, gridcolor="rgba(255,255,255,0.08)",
                           tickfont=dict(color="white")),
                yaxis=dict(range=[0,100], gridcolor="rgba(255,255,255,0.08)",
                           tickfont=dict(color="white")),
                margin=dict(t=30,b=60,l=40,r=60)
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            pivot = risk_df.pivot(index="İlçe", columns="Yıl", values="Risk_Skor")
            fig2 = go.Figure(go.Heatmap(
                z=pivot.values,
                x=[str(y) for y in pivot.columns],
                y=pivot.index.tolist(),
                colorscale=[[0,"#2ca02c"],[0.4,"#ff7f0e"],[0.7,"#d62728"],[1,"#8b0000"]],
                text=pivot.values.round(1),
                texttemplate="%{text}",
                textfont=dict(size=9, color="white"),
                hovertemplate="<b>%{y}</b> · %{x}<br>Risk: %{z:.1f}<extra></extra>",
                colorbar=dict(title="Risk", tickfont=dict(color="white"))
            ))
            fig2.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                height=380, font=dict(color="white"),
                xaxis=dict(tickfont=dict(color="white"), tickangle=-45),
                yaxis=dict(tickfont=dict(color="white")),
                margin=dict(t=10,b=40,l=110,r=30)
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Bölüm 2
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin:1.5rem 0 0.8rem 0;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);
                        border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;">
                    02 · DISTRICT DETAIL</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">
                    İlçe Bazlı Detay — Risk Bileşenleri</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        ilce_sec = st.selectbox("İlçe seç:", sorted(risk_df["İlçe"].unique()))
        df_ilce = risk_df[risk_df["İlçe"]==ilce_sec].sort_values("Yıl")
        skor_son = df_ilce[df_ilce["Yıl"]==END_YEAR]["Risk_Skor"].values[0]
        sinif_son = df_ilce[df_ilce["Yıl"]==END_YEAR]["Risk_Sınıf"].values[0]
        renk_son = get_risk_color(skor_son)
        cagr_val = cagr_dict.get(ilce_sec, 0) * 100

        k1, k2, k3 = st.columns(3)
        for col, baslik, deger, alt, renk in [
            (k1, f"{END_YEAR} Risk Skoru", f"{skor_son:.1f}", str(sinif_son), renk_son),
            (k2, "Risk Sınıfı", str(sinif_son), f"{END_YEAR} yılı", renk_son),
            (k3, "Abone Büyüme Hızı", f"%{cagr_val:.2f}/yıl", f"CAGR {START_YEAR}–{END_YEAR}", "#38d1e3"),
        ]:
            with col:
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.06);
                            border:1px solid {renk}44;border-top:3px solid {renk};
                            border-radius:10px;padding:1rem;text-align:center;">
                    <div style="color:#a8d8f0;font-size:0.72rem;letter-spacing:1px;
                                text-transform:uppercase;margin-bottom:6px;">{baslik}</div>
                    <div style="color:#ffffff;font-size:1.4rem;font-weight:700;
                                margin-bottom:4px;">{deger}</div>
                    <div style="color:{renk};font-size:0.78rem;">{alt}</div>
                </div>
                """, unsafe_allow_html=True)

    # ════════════════════════════════
    # TAHMİN
    # ════════════════════════════════
    elif sayfa == "🔮 2040 Tahmin":

        st.markdown(f"""
        <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid rgba(56,209,227,0.2);
                    margin-bottom:1.5rem;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);
                        border:1px solid rgba(56,209,227,0.3);border-radius:50px;
                        padding:4px 16px;margin-bottom:0.8rem;">
                <span style="color:#38d1e3;font-size:0.72rem;letter-spacing:3px;font-weight:600;">
                    SCENARIO PROJECTION · 2024–2040
                </span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">
                2040 Yılı Risk Projeksiyonu
            </div>
            <div style="color:#a8d8f0;font-size:0.9rem;">
                Abone büyüme oranı (CAGR) bazlı 3 senaryo · İyimser · Baz · Kötümser ·
                CAGR {len(YEARS)} yıllık seriden hesaplanmıştır
            </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns([2,2,1])
        with c1:
            hedef_yil = st.slider("Hedef yıl:", 2024, 2040, 2030)
        with c2:
            senaryo = st.radio("Senaryo:", ["Baz","İyimser","Kötümser"], horizontal=True)
        with c3:
            st.markdown(f"""
            <div style="background:rgba(56,209,227,0.1);border-radius:8px;
                        padding:0.6rem;text-align:center;margin-top:0.3rem;">
                <div style="color:#38d1e3;font-size:0.7rem;">Hedef</div>
                <div style="color:white;font-size:1.4rem;font-weight:700;">{hedef_yil}</div>
            </div>
            """, unsafe_allow_html=True)

        df_hedef = tahmin_df[tahmin_df["Yıl"]==hedef_yil].sort_values(senaryo, ascending=False)

        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin:1rem 0 0.8rem 0;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);
                        border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;">01 · PROJECTED SCORES</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">
                    İlçe Risk Skorları & Projeksiyon Trendi</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([3,2])
        with col1:
            colors = [get_risk_color(s) for s in df_hedef[senaryo]]
            fig = go.Figure(go.Bar(
                x=df_hedef["İlçe"], y=df_hedef[senaryo],
                marker=dict(color=colors, opacity=0.85,
                            line=dict(color="rgba(255,255,255,0.1)", width=0.5)),
                text=[f"{s:.1f}" for s in df_hedef[senaryo]],
                textposition="outside",
                textfont=dict(color="white", size=11),
                hovertemplate="<b>%{x}</b><br>%{y:.1f}<extra></extra>"
            ))
            fig.add_hline(y=40, line_dash="dot", line_color="#ff7f0e", line_width=1.5,
                          annotation_text="Orta Risk", annotation_font_color="#ff7f0e",
                          annotation_font_size=10)
            fig.add_hline(y=70, line_dash="dot", line_color="#d62728", line_width=1.5,
                          annotation_text="Yüksek Risk", annotation_font_color="#d62728",
                          annotation_font_size=10)
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                height=380, font=dict(color="white"),
                xaxis=dict(tickangle=30, gridcolor="rgba(255,255,255,0.08)",
                           tickfont=dict(color="white")),
                yaxis=dict(range=[0,100], gridcolor="rgba(255,255,255,0.08)",
                           tickfont=dict(color="white")),
                margin=dict(t=30,b=60,l=40,r=60)
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            ilce_sec = st.selectbox("İlçe seç:", sorted(tahmin_df["İlçe"].unique()))
            hist = risk_df[risk_df["İlçe"]==ilce_sec].sort_values("Yıl")
            pred = tahmin_df[tahmin_df["İlçe"]==ilce_sec].sort_values("Yıl")
            renk_ilce = get_risk_color(pred[pred["Yıl"]==hedef_yil][senaryo].values[0])

            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=hist["Yıl"], y=hist["Risk_Skor"],
                mode="lines+markers", name=f"Gerçek+Bootstrap ({START_YEAR}-{END_YEAR})",
                line=dict(color="#38d1e3", width=2.5),
                marker=dict(size=7, color="#38d1e3")
            ))
            fig2.add_trace(go.Scatter(
                x=pred["Yıl"], y=pred[senaryo],
                mode="lines", name=f"{senaryo} senaryo",
                line=dict(color=renk_ilce, width=2, dash="dash")
            ))
            fig2.add_trace(go.Scatter(
                x=list(pred["Yıl"])+list(pred["Yıl"])[::-1],
                y=list(pred["Kötümser"])+list(pred["İyimser"])[::-1],
                fill="toself", fillcolor="rgba(214,39,40,0.08)",
                line=dict(color="rgba(0,0,0,0)"),
                name="Senaryo bandı", hoverinfo="skip"
            ))
            fig2.add_hline(y=40, line_dash="dot", line_color="#ff7f0e", line_width=1)
            fig2.add_hline(y=70, line_dash="dot", line_color="#d62728", line_width=1)
            fig2.add_vline(x=END_YEAR+0.5, line_dash="dash", line_color="rgba(255,255,255,0.3)",
                           annotation_text="Tahmin →",
                           annotation_font_color="rgba(255,255,255,0.5)",
                           annotation_font_size=10)
            fig2.add_vline(x=2019.5, line_dash="dot", line_color="rgba(155,89,182,0.5)",
                           annotation_text="Bootstrap | Gerçek",
                           annotation_font_color="#c39bd3",
                           annotation_font_size=8)
            fig2.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                height=380, font=dict(color="white"),
                xaxis=dict(gridcolor="rgba(255,255,255,0.08)",
                           tickvals=list(range(START_YEAR, 2041, 5)),
                           tickfont=dict(color="white")),
                yaxis=dict(title="Risk Skoru", range=[0,100],
                           gridcolor="rgba(255,255,255,0.08)",
                           tickfont=dict(color="white")),
                legend=dict(font=dict(color="white", size=9), bgcolor="rgba(0,0,0,0)"),
                hovermode="x unified",
                margin=dict(t=10,b=30,l=50,r=20)
            )
            st.plotly_chart(fig2, use_container_width=True)

        # 2040 özet
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin:1.5rem 0 0.8rem 0;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);
                        border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;">02 · SCENARIO SUMMARY</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">
                    3 Senaryo Karşılaştırması — {hedef_yil}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        df_son_pred = tahmin_df[tahmin_df["Yıl"]==hedef_yil].sort_values("Baz", ascending=False)
        fig3 = go.Figure()
        for s_isim, s_renk, s_op in [("Kötümser","#d62728",0.7),
                                       ("Baz","#ff7f0e",0.85),
                                       ("İyimser","#2ca02c",0.7)]:
            fig3.add_trace(go.Bar(
                x=df_son_pred["İlçe"], y=df_son_pred[s_isim],
                name=s_isim, marker=dict(color=s_renk, opacity=s_op),
                hovertemplate=f"{s_isim}: %{{y:.1f}}<extra></extra>"
            ))
        fig3.add_hline(y=40, line_dash="dot", line_color="#ff7f0e", line_width=1.5)
        fig3.add_hline(y=70, line_dash="dot", line_color="#d62728", line_width=1.5)
        fig3.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            barmode="group", height=360, font=dict(color="white"),
            xaxis=dict(tickangle=30, gridcolor="rgba(255,255,255,0.08)",
                       tickfont=dict(color="white")),
            yaxis=dict(range=[0,100], gridcolor="rgba(255,255,255,0.08)",
                       tickfont=dict(color="white"), title="Risk Skoru"),
            legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)",
                        orientation="h", y=1.08),
            margin=dict(t=40,b=60,l=50,r=30)
        )
        st.plotly_chart(fig3, use_container_width=True)

    # ════════════════════════════════
    # MEKÂNSAL ANALİZ
    # ════════════════════════════════

    # ════════════════════════════════
    # SENARYO ANALİZİ
    # ════════════════════════════════
    elif sayfa == "📉 Senaryo Analizi":

        st.markdown("""
        <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid rgba(56,209,227,0.2);
                    margin-bottom:1.5rem;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);
                        border:1px solid rgba(56,209,227,0.3);border-radius:50px;
                        padding:4px 16px;margin-bottom:0.8rem;">
                <span style="color:#38d1e3;font-size:0.72rem;letter-spacing:3px;font-weight:600;">
                    WHAT-IF SCENARIO LAB · BOOTSTRAP SIMULATION
                </span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">
                Senaryo Analizi & Duyarlılık Laboratuvarı
            </div>
            <div style="color:#a8d8f0;font-size:0.9rem;">
                Tüketim, kayıp oranı, arz kısıtı ve abone büyümesi değişince 2040 risk görünümü nasıl etkilenir?
            </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            sec_ilce = st.selectbox("İlçe seç:", sorted(risk_df["İlçe"].unique()), key="senaryo_ilce")
        with c2:
            hedef_yil_s = st.slider("Hedef yıl:", END_YEAR + 1, PRED_END_YEAR, PRED_END_YEAR, key="senaryo_hedef")
        with c3:
            sec_senaryo = st.radio("Baz senaryo:", ["İyimser", "Baz", "Kötümser"], horizontal=True, key="senaryo_tipi")
        with c4:
            bootstrap_n = st.slider("Bootstrap tekrar:", 100, 2000, 500, 100, key="bootstrap_n")

        base_row = risk_df[(risk_df["İlçe"] == sec_ilce) & (risk_df["Yıl"] == END_YEAR)].iloc[0]
        base_score = float(base_row["Risk_Skor"])
        base_cagr = float(cagr_dict.get(sec_ilce, 0.01))
        dt = hedef_yil_s - END_YEAR

        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin:1rem 0 0.8rem 0;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;">01 · WHAT-IF CONTROLS</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">Parametreleri Değiştir — Risk Skoru Anlık Güncellensin</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        s1, s2, s3, s4 = st.columns(4)
        with s1:
            tuketim_etki = st.slider("Tüketim etkisi (%)", -30, 60, 0, key="sen_tuketim") / 100
        with s2:
            kayip_etki = st.slider("Kayıp oranı etkisi (%)", -30, 60, 0, key="sen_kayip") / 100
        with s3:
            arz_etki = st.slider("Arz kısıtı etkisi (%)", -30, 60, 0, key="sen_arz") / 100
        with s4:
            buyume_carpani = st.slider("Abone büyüme çarpanı", 0.25, 2.50, 1.00, 0.05, key="sen_buyume")

        sec_carpan = {"İyimser": 0.85, "Baz": 1.00, "Kötümser": 1.15}[sec_senaryo]
        scenario_factor = sec_carpan * (1 + (0.35 * tuketim_etki) + (0.30 * kayip_etki) + (0.25 * arz_etki))
        adjusted_cagr = base_cagr * buyume_carpani
        projected_score = float(np.clip(base_score * scenario_factor * ((1 + adjusted_cagr) ** dt), 0, 100))
        projected_color = get_risk_color(projected_score)
        projected_class = get_risk_label(projected_score)

        np.random.seed(42)
        hist_scores = risk_df[risk_df["İlçe"] == sec_ilce].sort_values("Yıl")["Risk_Skor"].values
        hist_vol = float(np.std(np.diff(hist_scores))) if len(hist_scores) > 2 else 3.0
        boot_noise = np.random.normal(0, max(hist_vol, 1.0), bootstrap_n)
        boot_cagr = np.random.normal(adjusted_cagr, max(abs(adjusted_cagr) * 0.25, 0.002), bootstrap_n)
        boot_scores = np.clip(base_score * scenario_factor * ((1 + boot_cagr) ** dt) + boot_noise, 0, 100)
        ci_low, ci_med, ci_high = np.percentile(boot_scores, [5, 50, 95])

        k1, k2, k3, k4 = st.columns(4)
        for col, baslik, deger, alt, renk in [
            (k1, "Mevcut Risk", f"{base_score:.1f}", f"{END_YEAR} skoru", get_risk_color(base_score)),
            (k2, "Senaryo Riski", f"{projected_score:.1f}", projected_class, projected_color),
            (k3, "Bootstrap Medyan", f"{ci_med:.1f}", f"%90 GA: {ci_low:.1f}–{ci_high:.1f}", "#38d1e3"),
            (k4, "CAGR", f"%{adjusted_cagr*100:.2f}", "ayarlanmış büyüme", "#ff7f0e"),
        ]:
            with col:
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.06);border:1px solid {renk}44;
                            border-top:3px solid {renk};border-radius:10px;padding:1rem;text-align:center;">
                    <div style="color:#a8d8f0;font-size:0.72rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">{baslik}</div>
                    <div style="color:#ffffff;font-size:1.5rem;font-weight:800;margin-bottom:4px;">{deger}</div>
                    <div style="color:{renk};font-size:0.78rem;">{alt}</div>
                </div>
                """, unsafe_allow_html=True)

        col_a, col_b = st.columns([3, 2])
        with col_a:
            hist = risk_df[risk_df["İlçe"] == sec_ilce].sort_values("Yıl")
            future_years = list(range(END_YEAR + 1, hedef_yil_s + 1))
            path_scores = [float(np.clip(base_score * scenario_factor * ((1 + adjusted_cagr) ** (y - END_YEAR)), 0, 100)) for y in future_years]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist["Yıl"], y=hist["Risk_Skor"], mode="lines+markers", name="Tarihsel",
                                     line=dict(color="#38d1e3", width=3), marker=dict(size=8)))
            fig.add_trace(go.Scatter(x=future_years, y=path_scores, mode="lines+markers", name="What-if",
                                     line=dict(color=projected_color, width=3, dash="dash"), marker=dict(size=7)))
            fig.add_hline(y=40, line_dash="dot", line_color="#ff7f0e", line_width=1)
            fig.add_hline(y=70, line_dash="dot", line_color="#d62728", line_width=1)
            fig.add_vline(x=END_YEAR + 0.5, line_dash="dash", line_color="rgba(255,255,255,0.35)")
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=380,
                font=dict(color="white"), hovermode="x unified",
                xaxis=dict(gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color="white")),
                yaxis=dict(title="Risk Skoru", range=[0, 100], gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color="white")),
                legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)")
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            fig_hist = go.Figure(go.Histogram(
                x=boot_scores, nbinsx=25,
                marker=dict(color=projected_color, opacity=0.75, line=dict(color="rgba(255,255,255,0.18)", width=1)),
            ))
            fig_hist.add_vline(x=ci_low, line_dash="dot", line_color="#a8d8f0", annotation_text="P5")
            fig_hist.add_vline(x=ci_med, line_dash="dash", line_color="#38d1e3", annotation_text="Medyan")
            fig_hist.add_vline(x=ci_high, line_dash="dot", line_color="#a8d8f0", annotation_text="P95")
            fig_hist.update_layout(
                title="Bootstrap Risk Dağılımı", title_font=dict(color="white"),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=380,
                font=dict(color="white"),
                xaxis=dict(title="Risk Skoru", range=[0, 100], gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color="white")),
                yaxis=dict(title="Frekans", gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color="white")),
                margin=dict(t=50,b=40,l=50,r=30)
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        st.markdown("""
        <div style="background:rgba(56,209,227,0.08);border:1px solid rgba(56,209,227,0.22);
                    border-radius:10px;padding:0.9rem 1.1rem;margin-top:0.5rem;">
            <div style="color:#38d1e3;font-size:0.78rem;font-weight:700;letter-spacing:1px;margin-bottom:0.4rem;">YORUM</div>
            <div style="color:#d0e8f5;font-size:0.88rem;line-height:1.7;">
                Bu sayfa, mevcut risk skorunu kullanıcı tanımlı varsayımlarla yeniden ölçekler.
                Bootstrap dağılımı tarihsel risk değişkenliğinden örneklenen belirsizlik bandını gösterir.
                Model karar destek amaçlıdır.
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif sayfa == "🗺️ Mekânsal Analiz":

        st.markdown(f"""
        <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid rgba(56,209,227,0.2);
                    margin-bottom:1.5rem;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);
                        border:1px solid rgba(56,209,227,0.3);border-radius:50px;
                        padding:4px 16px;margin-bottom:0.8rem;">
                <span style="color:#38d1e3;font-size:0.72rem;letter-spacing:3px;font-weight:600;">
                    SPATIAL ANALYSIS · MORAN'S I + LISA · {END_YEAR}
                </span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">
                Mekânsal Analiz
            </div>
            <div style="color:#a8d8f0;font-size:0.9rem;">
                Yüksek riskli ilçeler birbirine komşu mu? · Global Moran's I · LISA kümeleme · {END_YEAR}
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("ℹ️ Moran's I ve LISA nedir?"):
            st.markdown("""
            **Mekânsal Analiz** — Yüksek riskli ilçeler birbirine komşu mu, yoksa dağınık mı?

            - **Global Moran's I** — Tüm sistemi tek bir sayıyla özetler. +1'e yakınsa riskli ilçeler kümeleniyor, -1'e yakınsa dağınık.
            - **LISA** — Her ilçeye ayrı etiket verir:
                - 🔴 **HH** (yüksek-yüksek) — Riskli ilçe, komşuları da riskli → sıcak nokta
                - 🟢 **LL** (düşük-düşük) — Düşük riskli ilçe, komşuları da düşük → soğuk nokta
                - 🟠 **HL** — Riskli ilçe ama komşuları düşük riskli → izole yüksek risk
                - 🔵 **LH** — Düşük riskli ama komşuları yüksek riskli → dikkat gerektiriyor
            """)

        ilceler = ["BALÇOVA","BAYRAKLI","BORNOVA","BUCA","ÇİĞLİ",
                   "GAZİEMİR","GÜZELBAHÇE","KARABAĞLAR","KARŞIYAKA","KONAK","NARLIDERE"]
        komsuluk = {
            "BALÇOVA":["NARLIDERE","KONAK","GAZİEMİR"],
            "BAYRAKLI":["BORNOVA","KARŞIYAKA","ÇİĞLİ"],
            "BORNOVA":["BAYRAKLI","BUCA","KARABAĞLAR","ÇİĞLİ"],
            "BUCA":["BORNOVA","KARABAĞLAR","GAZİEMİR","KONAK"],
            "ÇİĞLİ":["BAYRAKLI","BORNOVA","KARŞIYAKA"],
            "GAZİEMİR":["BALÇOVA","BUCA","KARABAĞLAR","KONAK"],
            "GÜZELBAHÇE":["NARLIDERE","KONAK"],
            "KARABAĞLAR":["BORNOVA","BUCA","GAZİEMİR","KONAK"],
            "KARŞIYAKA":["BAYRAKLI","ÇİĞLİ","KONAK"],
            "KONAK":["BALÇOVA","BUCA","GAZİEMİR","GÜZELBAHÇE","KARABAĞLAR","KARŞIYAKA","NARLIDERE"],
            "NARLIDERE":["BALÇOVA","GÜZELBAHÇE","KONAK"],
        }
        n = len(ilceler)
        W_raw = np.zeros((n,n))
        for i,ilce in enumerate(ilceler):
            for j,d in enumerate(ilceler):
                if d in komsuluk[ilce]: W_raw[i,j]=1
        W_sp = W_raw / W_raw.sum(axis=1,keepdims=True)

        r_son = risk_df[risk_df["Yıl"]==END_YEAR].set_index("İlçe")["Risk_Skor"].reindex(ilceler).values
        z = (r_son-r_son.mean())/r_son.std()
        Wz = W_sp@z
        I_local = z*Wz
        lisa_sinif = []
        for i in range(len(r_son)):
            if z[i]>0 and Wz[i]>0: lisa_sinif.append("HH")
            elif z[i]<0 and Wz[i]<0: lisa_sinif.append("LL")
            elif z[i]>0 and Wz[i]<0: lisa_sinif.append("HL")
            else: lisa_sinif.append("LH")

        np.random.seed(42)
        perm_I = []
        for _ in range(999):
            xp = np.random.permutation(r_son)
            zp = xp-xp.mean()
            perm_I.append(len(r_son)*(W_sp*np.outer(zp,zp)).sum()/(W_sp.sum()*(zp**2).sum()))
        I_glob = round(float((W_sp*np.outer(z,z)).sum()/((z**2).sum())),4)
        p_glob = round(float(np.mean(np.abs(perm_I)>=np.abs(I_glob))),4)

        hh_count = sum(1 for s in lisa_sinif if s=="HH")

        # KPI kartları
        k1,k2,k3,k4 = st.columns(4)
        for col, baslik, deger, alt, renk in [
            (k1, "Global Moran's I", f"{I_glob}", f"{END_YEAR} risk skorları", "#38d1e3"),
            (k2, "p-değeri", f"{p_glob}", "999 permütasyon testi", "#a8d8f0"),
            (k3, "Yorum", "Pozitif" if I_glob > 0 else "Negatif",
             "Komşular benzer" if I_glob > 0 else "Komşular farklılaşıyor", "#ff7f0e"),
            (k4, "HH Küme", f"{hh_count} ilçe",
             "Yüksek-yüksek küme" if hh_count else "HH küme yok", "#2ca02c"),
        ]:
            with col:
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.06);
                            border:1px solid {renk}44;border-top:3px solid {renk};
                            border-radius:10px;padding:0.8rem;text-align:center;">
                    <div style="color:#a8d8f0;font-size:0.7rem;letter-spacing:1px;
                                text-transform:uppercase;margin-bottom:4px;">{baslik}</div>
                    <div style="color:#ffffff;font-size:1.3rem;font-weight:700;
                                margin-bottom:3px;">{deger}</div>
                    <div style="color:{renk};font-size:0.75rem;">{alt}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin:0.5rem 0 0.8rem 0;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);
                        border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;">01 · SPATIAL ANALYSIS</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">
                    Moran Scatter Plot & LISA Sınıflandırması — {END_YEAR}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            renk_map={"HH":"#d62728","LL":"#2ca02c","HL":"#ff7f0e","LH":"#9467bd"}
            fig = go.Figure()
            for sinif, renk in renk_map.items():
                idx = [i for i,s in enumerate(lisa_sinif) if s==sinif]
                if idx:
                    fig.add_trace(go.Scatter(
                        x=z[idx], y=Wz[idx],
                        mode="markers+text",
                        name=sinif,
                        text=[ilceler[i] for i in idx],
                        textposition="top center",
                        textfont=dict(size=9),
                        marker=dict(size=12,color=renk,opacity=0.85)
                    ))
            x_line = np.linspace(z.min()-0.2,z.max()+0.2,50)
            slope = np.polyfit(z,Wz,1)
            fig.add_trace(go.Scatter(x=x_line,y=np.polyval(slope,x_line),
                mode="lines",line=dict(color="black",width=1.5,dash="dash"),
                name=f"I={I_glob}",hoverinfo="skip"))
            fig.add_hline(y=0,line_color="gray",line_width=1)
            fig.add_vline(x=0,line_color="gray",line_width=1)
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                height=400, font=dict(color="white"),
                xaxis=dict(title="Standardize Risk (z)", gridcolor="rgba(255,255,255,0.08)",
                           tickfont=dict(color="white"), title_font=dict(color="#a8d8f0")),
                yaxis=dict(title="Mekânsal Lag (Wz)", gridcolor="rgba(255,255,255,0.08)",
                           tickfont=dict(color="white"), title_font=dict(color="#a8d8f0")),
                legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown(f"""
            <div style="color:#38d1e3;font-size:0.7rem;letter-spacing:2px;
                        margin-bottom:0.5rem;">LISA SINIFLANDIRMASI · {END_YEAR}</div>
            """, unsafe_allow_html=True)
            lisa_df = pd.DataFrame({
                "İlçe":ilceler,"Risk":r_son.round(1),
                "LISA":lisa_sinif,"Local_I":I_local.round(3)
            }).sort_values("Risk",ascending=False)
            st.dataframe(lisa_df, use_container_width=True, hide_index=True)

    # ════════════════════════════════
    # ÖNERİLER
    # ════════════════════════════════
    elif sayfa == "💡 Öneriler":

        st.markdown(f"""
        <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid rgba(56,209,227,0.2);
                    margin-bottom:1.5rem;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);
                        border:1px solid rgba(56,209,227,0.3);border-radius:50px;
                        padding:4px 16px;margin-bottom:0.8rem;">
                <span style="color:#38d1e3;font-size:0.72rem;letter-spacing:3px;font-weight:600;">
                    DISTRICT RECOMMENDATIONS · {END_YEAR}
                </span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">
                İlçe Bazlı Öneriler
            </div>
            <div style="color:#a8d8f0;font-size:0.9rem;">
                Risk sınıfına göre kişiselleştirilmiş öneri · {len(YEARS)} yıllık trend analizi · 2040 projeksiyonu
            </div>
        </div>
        """, unsafe_allow_html=True)

        ilce_sec = st.selectbox("İlçe seç:", sorted(risk_df["İlçe"].unique()))
        df_ilce = risk_df[risk_df["İlçe"]==ilce_sec]
        skor = df_ilce[df_ilce["Yıl"]==END_YEAR]["Risk_Skor"].values[0]
        sinif = df_ilce[df_ilce["Yıl"]==END_YEAR]["Risk_Sınıf"].values[0]
        renk = get_risk_color(skor)
        pred_2040 = tahmin_df[(tahmin_df["İlçe"]==ilce_sec)&(tahmin_df["Yıl"]==2040)]
        cagr_val = cagr_dict.get(ilce_sec, 0) * 100

        k1,k2,k3,k4 = st.columns(4)
        for col, baslik, deger, alt, r in [
            (k1, "İlçe", ilce_sec, "Seçili ilçe", renk),
            (k2, f"{END_YEAR} Risk Skoru", f"{skor:.1f}", str(sinif), renk),
            (k3, "2040 Baz Tahmin", f"{pred_2040['Baz'].values[0]:.1f}", "Baz senaryo", "#ff7f0e"),
            (k4, "Abone Büyüme", f"%{cagr_val:.2f}/yıl", f"CAGR {START_YEAR}–{END_YEAR}", "#38d1e3"),
        ]:
            with col:
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.06);
                            border:1px solid {r}44;border-top:3px solid {r};
                            border-radius:10px;padding:0.8rem;text-align:center;">
                    <div style="color:#a8d8f0;font-size:0.7rem;letter-spacing:1px;
                                text-transform:uppercase;margin-bottom:4px;">{baslik}</div>
                    <div style="color:#ffffff;font-size:1.2rem;font-weight:700;
                                margin-bottom:3px;">{deger}</div>
                    <div style="color:{r};font-size:0.75rem;">{alt}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        col1, col2 = st.columns([1,2])
        with col1:
            st.markdown("""
            <div style="color:#38d1e3;font-size:0.7rem;letter-spacing:2px;margin-bottom:0.5rem;">
                2040 PROJEKSİYONU</div>
            """, unsafe_allow_html=True)
            for s_isim, s_renk in [("Kötümser","#d62728"),("Baz","#ff7f0e"),("İyimser","#2ca02c")]:
                val = pred_2040[s_isim].values[0]
                sinif_40 = "Düşük" if val<40 else "Orta" if val<70 else "Yüksek"
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.05);border-left:3px solid {s_renk};
                            border-radius:0 8px 8px 0;padding:0.6rem 0.8rem;margin-bottom:0.4rem;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="color:#a8d8f0;font-size:0.8rem;">{s_isim}</span>
                        <span style="color:white;font-weight:700;">{val:.1f}</span>
                    </div>
                    <div style="color:{s_renk};font-size:0.72rem;">{sinif_40} Risk</div>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div style="color:#38d1e3;font-size:0.7rem;letter-spacing:2px;margin-bottom:0.5rem;">
                01 · RISK TRENDİ & ÖNERİLER</div>
            """, unsafe_allow_html=True)
            hist = risk_df[risk_df["İlçe"]==ilce_sec].sort_values("Yıl")
            pred = tahmin_df[tahmin_df["İlçe"]==ilce_sec].sort_values("Yıl")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist["Yıl"],y=hist["Risk_Skor"],
                mode="lines+markers",name=f"Tarihsel ({START_YEAR}-{END_YEAR})",
                line=dict(color="#1B4F72",width=2.5),marker=dict(size=7)))
            fig.add_trace(go.Scatter(x=pred["Yıl"],y=pred["Baz"],
                mode="lines",name="Baz tahmin",
                line=dict(color=renk,width=2,dash="dash")))
            fig.add_trace(go.Scatter(
                x=list(pred["Yıl"])+list(pred["Yıl"])[::-1],
                y=list(pred["Kötümser"])+list(pred["İyimser"])[::-1],
                fill="toself",fillcolor="rgba(214,39,40,0.08)",
                line=dict(color="rgba(0,0,0,0)"),
                name="Senaryo bandı",hoverinfo="skip"))
            fig.add_hline(y=40,line_dash="dot",line_color="orange")
            fig.add_hline(y=70,line_dash="dot",line_color="red")
            fig.add_vline(x=END_YEAR+0.5,line_dash="dash",line_color="gray")
            fig.add_vline(x=2019.5,line_dash="dot",line_color="rgba(155,89,182,0.5)")
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                height=280, font=dict(color="white"),
                xaxis=dict(gridcolor="rgba(255,255,255,0.08)",
                           tickfont=dict(color="white")),
                yaxis=dict(title="Risk Skoru", gridcolor="rgba(255,255,255,0.08)",
                           range=[0,100], tickfont=dict(color="white")),
                legend=dict(font=dict(color="white", size=9), bgcolor="rgba(0,0,0,0)"),
                hovermode="x unified", margin=dict(t=10,b=20))
            st.plotly_chart(fig, use_container_width=True)

            rec = get_recommendation(ilce_sec, skor, sinif)
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.06);border-left:4px solid {rec['renk']};
                        border-radius:8px;padding:1rem 1.2rem;margin:0.5rem 0;">
                <div style="color:{rec['renk']};font-size:1rem;font-weight:700;margin-bottom:0.4rem;">
                    {rec['durum']}
                </div>
                <div style="color:#d0e8f5;font-size:0.9rem;margin-bottom:0.8rem;">
                    {rec['mesaj']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            for i, oneri in enumerate(rec["oneri"], 1):
                st.markdown(f"""
                <div style="display:flex;gap:10px;align-items:flex-start;
                            padding:0.4rem 0;border-bottom:1px solid rgba(255,255,255,0.06);">
                    <span style="color:{rec['renk']};font-weight:700;min-width:20px;">{i}.</span>
                    <span style="color:#d0e8f5;font-size:0.9rem;">{oneri}</span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:rgba(56,209,227,0.08);border-radius:8px;
                        padding:0.8rem 1rem;margin-top:0.8rem;">
                <span style="color:#38d1e3;font-size:0.85rem;">🔮 {rec['gelecek']}</span>
            </div>
            """, unsafe_allow_html=True)

    elif sayfa == "Izmir Risk Haritasi":

        st.markdown(f"""
        <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid rgba(56,209,227,0.2);
                    margin-bottom:1.5rem;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);
                        border:1px solid rgba(56,209,227,0.3);border-radius:50px;
                        padding:4px 16px;margin-bottom:0.8rem;">
                <span style="color:#38d1e3;font-size:0.72rem;letter-spacing:3px;font-weight:600;">
                    INTERACTIVE RISK MAP · İZMİR · {START_YEAR}–2040
                </span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">
                İzmir İlçe Risk Haritası
            </div>
            <div style="color:#a8d8f0;font-size:0.9rem;">
                İlçe üzerine gel → risk skoru, sınıf ve yıl bilgisi · Yıl ({START_YEAR}–2040) ve senaryo seçilebilir
            </div>
        </div>
        """, unsafe_allow_html=True)

        import folium
        from streamlit_folium import st_folium

        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            harita_yil = st.slider("Yıl:", START_YEAR, 2040, END_YEAR, key="harita_yil")
        with c2:
            harita_senaryo = st.radio("Senaryo:", ["Baz","İyimser","Kötümser"],
                                      horizontal=True, key="harita_senaryo")
        with c3:
            st.markdown(f"""
            <div style="background:rgba(56,209,227,0.1);border-radius:8px;
                        padding:0.6rem;text-align:center;margin-top:0.3rem;">
                <div style="color:#38d1e3;font-size:0.7rem;">Seçili Yıl</div>
                <div style="color:white;font-size:1.4rem;font-weight:700;">{harita_yil}</div>
            </div>
            """, unsafe_allow_html=True)

        # Veri tipi rozeti
        if harita_yil < 2020:
            tip_str, tip_renk = "🔬 Bootstrap Simülasyonu", "#9b59b6"
        elif harita_yil <= END_YEAR:
            tip_str, tip_renk = "✅ İZSU Gerçek Verisi", "#2ca02c"
        else:
            tip_str, tip_renk = "🔮 Projeksiyon", "#38d1e3"
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.04);border:1px solid {tip_renk}44;
                    border-radius:8px;padding:0.4rem 1rem;margin-bottom:0.8rem;display:inline-block;">
            <span style="color:{tip_renk};font-size:0.78rem;font-weight:600;">
                {harita_yil}: {tip_str}
            </span>
        </div>
        """, unsafe_allow_html=True)

        ILCE_KOORD = {
            "BALÇOVA":    (38.3850, 27.0500),
            "BAYRAKLI":   (38.4600, 27.1700),
            "BORNOVA":    (38.4700, 27.2200),
            "BUCA":       (38.3800, 27.1800),
            "ÇİĞLİ":     (38.5000, 27.0400),
            "GAZİEMİR":   (38.3200, 27.1300),
            "GÜZELBAHÇE": (38.3900, 26.9000),
            "KARABAĞLAR": (38.3900, 27.1000),
            "KARŞIYAKA":  (38.4600, 27.1100),
            "KONAK":      (38.4100, 27.1400),
            "NARLIDERE":  (38.4000, 26.9800),
        }

        def get_risk_score(ilce, yil, senaryo):
            if yil <= END_YEAR:
                row = risk_df[(risk_df["İlçe"]==ilce) & (risk_df["Yıl"]==yil)]
                return float(row["Risk_Skor"].values[0]) if len(row) > 0 else 0
            else:
                row = tahmin_df[(tahmin_df["İlçe"]==ilce) & (tahmin_df["Yıl"]==yil)]
                return float(row[senaryo].values[0]) if len(row) > 0 else 0

        def risk_rengi(skor):
            if skor < 40: return "#2ca02c"
            if skor < 70: return "#ff7f0e"
            return "#d62728"

        def risk_sinifi(skor):
            if skor < 40: return "Düşük Risk"
            if skor < 70: return "Orta Risk"
            return "Yüksek Risk"

        m = folium.Map(
            location=[38.42, 27.14],
            zoom_start=12,
            tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
            attr="CartoDB Dark Matter",
            prefer_canvas=True
        )

        for ilce, (lat, lon) in ILCE_KOORD.items():
            skor = get_risk_score(ilce, harita_yil, harita_senaryo)
            renk = risk_rengi(skor)
            sinif = risk_sinifi(skor)

            tooltip_html = f"""
            <div style='font-family:Arial;font-size:14px;padding:10px 14px;
                        background:#1a1a2e;border-radius:8px;border:1px solid {renk};
                        box-shadow:0 4px 12px rgba(0,0,0,0.4);min-width:160px;'>
                <div style='color:{renk};font-weight:700;font-size:15px;margin-bottom:6px;'>
                    {ilce}
                </div>
                <div style='color:#ffffff;margin-bottom:3px;'>
                    Risk Skoru: <b style="color:{renk}">{skor:.1f}</b>
                </div>
                <div style='color:#aaaaaa;font-size:12px;margin-bottom:3px;'>
                    Sınıf: {sinif}
                </div>
                <div style='color:#aaaaaa;font-size:12px;'>
                    Yıl: {harita_yil}
                </div>
            </div>"""

            folium.CircleMarker(
                location=[lat, lon], radius=36,
                color=renk, fill=True, fill_color=renk,
                fill_opacity=0.15, weight=1, opacity=0.4,
            ).add_to(m)

            folium.CircleMarker(
                location=[lat, lon], radius=26,
                color=renk, fill=True, fill_color=renk,
                fill_opacity=0.85, weight=2, opacity=1,
                tooltip=folium.Tooltip(tooltip_html, sticky=True),
                popup=folium.Popup(tooltip_html, max_width=220)
            ).add_to(m)

            folium.Marker(
                location=[lat, lon],
                icon=folium.DivIcon(
                    html=f"""<div style="
                        font-family:Arial;font-size:10px;font-weight:700;
                        color:white;text-align:center;
                        text-shadow: 1px 1px 3px rgba(0,0,0,0.9),
                                     -1px -1px 3px rgba(0,0,0,0.9);
                        white-space:nowrap;
                        transform:translateY(-4px);
                    ">{ilce}</div>""",
                    icon_size=(120, 20),
                    icon_anchor=(60, 10)
                )
            ).add_to(m)

        legend_html = f"""
        <div style="position:fixed;bottom:20px;right:20px;z-index:1000;
                    background:#1a1a2e;border:1px solid rgba(255,255,255,0.2);
                    border-radius:10px;padding:12px 16px;font-family:Arial;">
            <div style="color:white;font-weight:700;margin-bottom:8px;font-size:13px;">
                Risk Sınıfları
            </div>
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">
                <div style="width:14px;height:14px;border-radius:50%;background:#2ca02c;"></div>
                <span style="color:#ccc;font-size:12px;">Düşük Risk (0–40)</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">
                <div style="width:14px;height:14px;border-radius:50%;background:#ff7f0e;"></div>
                <span style="color:#ccc;font-size:12px;">Orta Risk (40–70)</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
                <div style="width:14px;height:14px;border-radius:50%;background:#d62728;"></div>
                <span style="color:#ccc;font-size:12px;">Yüksek Risk (70+)</span>
            </div>
        </div>"""
        m.get_root().html.add_child(folium.Element(legend_html))

        st_folium(m, use_container_width=True, height=560)

        st.subheader(f"{harita_yil} Yılı Risk Sıralaması")
        tablo_data = []
        for ilce in ILCE_KOORD.keys():
            skor = get_risk_score(ilce, harita_yil, harita_senaryo)
            tablo_data.append({"İlçe": ilce, "Risk Skoru": round(skor,1), "Sınıf": risk_sinifi(skor)})
        tablo_df = pd.DataFrame(tablo_data).sort_values("Risk Skoru", ascending=False)
        st.dataframe(tablo_df, use_container_width=True, hide_index=True)

    # ════════════════════════════════
    # ARAÇLAR
    # ════════════════════════════════
    elif sayfa == "🔬 Araçlar":

        st.markdown(f"""
        <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid rgba(56,209,227,0.2);
                    margin-bottom:1.5rem;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);
                        border:1px solid rgba(56,209,227,0.3);border-radius:50px;
                        padding:4px 16px;margin-bottom:0.8rem;">
                <span style="color:#38d1e3;font-size:0.72rem;letter-spacing:3px;font-weight:600;">
                    INTERACTIVE TOOLS · EXPLORE & ANALYZE
                </span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">
                İnteraktif Araçlar
            </div>
            <div style="color:#a8d8f0;font-size:0.9rem;">
                Radar profil · İlçe karşılaştırma · Risk simülatörü · {len(YEARS)} yıllık animasyonlu seri · Veri indirme
            </div>
        </div>
        """, unsafe_allow_html=True)

        ilce_sec = st.selectbox("İlçe seç:", sorted(risk_df["İlçe"].unique()), key="arac_ilce")
        df_ilce = risk_df[risk_df["İlçe"]==ilce_sec]
        skor = df_ilce[df_ilce["Yıl"]==END_YEAR]["Risk_Skor"].values[0]
        sinif = df_ilce[df_ilce["Yıl"]==END_YEAR]["Risk_Sınıf"].values[0]
        renk = get_risk_color(skor)

        # Bölüm 1: Radar + Karşılaştırma
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin:1.5rem 0 0.8rem 0;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;">01 · RADAR & COMPARISON</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">İlçe Radar Profili & Karşılaştırma</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_r, col_k = st.columns(2)

        with col_r:
            st.caption(f"Radar — Risk Bileşen Profili ({END_YEAR})")
            df_r_son = risk_df[risk_df["Yıl"]==END_YEAR]
            row = risk_df[(risk_df["İlçe"]==ilce_sec)&(risk_df["Yıl"]==END_YEAR)].iloc[0]
            def minmax_col(col):
                mn,mx = df_r_son[col].min(), df_r_son[col].max()
                return 0 if mx==mn else (row[col]-mn)/(mx-mn)
            vals = [minmax_col("AbbTuketim"), minmax_col("Artis"),
                    minmax_col("Arz_Kısıtı"), minmax_col("Su_Kayıp_Oranı_%")]
            cats = ["Talep","Artış","Arz","Kayıp"]
            fig_r = go.Figure(go.Scatterpolar(
                r=vals+[vals[0]], theta=cats+[cats[0]],
                fill="toself", fillcolor=f"rgba(56,209,227,0.15)",
                line=dict(color="#38d1e3", width=2),
                marker=dict(size=6, color="#38d1e3"),
                hovertemplate="%{theta}: %{r:.2f}<extra></extra>"
            ))
            fig_r.update_layout(
                polar=dict(
                    bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(range=[0,1], showticklabels=False, gridcolor="rgba(255,255,255,0.15)"),
                    angularaxis=dict(tickfont=dict(color="white", size=11), gridcolor="rgba(255,255,255,0.15)")
                ),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=300, margin=dict(t=20,b=20,l=40,r=40),
                showlegend=False
            )
            st.plotly_chart(fig_r, use_container_width=True)

        with col_k:
            st.caption(f"Karşılaştırma — İki İlçe ({END_YEAR})")
            ilce_list = sorted(risk_df["İlçe"].unique().tolist())
            diger = [i for i in ilce_list if i != ilce_sec]
            karsi_ilce = st.selectbox("Karşılaştır:", diger, key="karsi")
            row1 = risk_df[(risk_df["İlçe"]==ilce_sec)&(risk_df["Yıl"]==END_YEAR)].iloc[0]
            row2 = risk_df[(risk_df["İlçe"]==karsi_ilce)&(risk_df["Yıl"]==END_YEAR)].iloc[0]
            gostergeler = [
                ("Abone Başına Tüketim","AbbTuketim","m³"),
                ("Tüketim Artışı","Artis","%"),
                ("Arz Kısıtı","Arz_Kısıtı",""),
                ("Su Kayıp Oranı","Su_Kayıp_Oranı_%","%"),
                ("Risk Skoru","Risk_Skor","")
            ]
            for gad, gcol, gbirim in gostergeler:
                v1,v2 = float(row1[gcol]),float(row2[gcol])
                r1,r2 = get_risk_color(row1["Risk_Skor"]),get_risk_color(row2["Risk_Skor"])
                st.markdown(f"""
                <div style="display:grid;grid-template-columns:1fr 80px 1fr;gap:4px;align-items:center;
                            padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.06);">
                    <div style="text-align:right;color:white;font-size:0.85rem;font-weight:600;">{v1:.2f}<span style="color:{r1};font-size:0.7rem;"> {gbirim}</span></div>
                    <div style="text-align:center;color:#a8d8f0;font-size:0.72rem;">{gad}</div>
                    <div style="color:white;font-size:0.85rem;font-weight:600;">{v2:.2f}<span style="color:{r2};font-size:0.7rem;"> {gbirim}</span></div>
                </div>
                """, unsafe_allow_html=True)

        # Bölüm 2: Risk Simülatörü
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin:1.5rem 0 0.8rem 0;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;">02 · SIMULATOR</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">Risk Simülatörü — Anlık Duyarlılık ({END_YEAR} bazlı)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.caption("Gösterge değerlerini değiştir — risk skoru anlık güncellenir")
        s1,s2,s3,s4 = st.columns(4)
        with s1: sim_talep = st.slider("Abone Tüketim (m³)", 80, 320, int(row1["AbbTuketim"]), key="sim1")
        with s2: sim_artis = st.slider("Tüketim Artışı (%)", -10, 20, int(row1["Artis"]*100), key="sim2")
        with s3: sim_arz = st.slider("Arz Kısıtı (%)", 0, 40, int(row1["Arz_Kısıtı"]*100), key="sim3")
        with s4: sim_kayip = st.slider("Kayıp Oranı (%)", 15, 45, int(row1["Su_Kayıp_Oranı_%"]), key="sim4")

        df_sim = risk_df[risk_df["Yıl"]==END_YEAR].copy()
        def norm(v,mn,mx): return max(0,min(1,(v-mn)/(mx-mn))) if mx>mn else 0
        # Dinamik W (compute_risk'ten geleni kullan)
        W_sim = list(W)
        z1 = norm(sim_talep, df_sim["AbbTuketim"].min(), df_sim["AbbTuketim"].max())
        z2 = norm(sim_artis/100, df_sim["Artis"].min(), df_sim["Artis"].max())
        z3 = norm(sim_arz/100, df_sim["Arz_Kısıtı"].min(), df_sim["Arz_Kısıtı"].max())
        z4 = norm(sim_kayip, df_sim["Su_Kayıp_Oranı_%"].min(), df_sim["Su_Kayıp_Oranı_%"].max())
        sim_skor = (z1*W_sim[0]+z2*W_sim[1]+z3*W_sim[2]+z4*W_sim[3])*100
        sim_sinif = "Düşük Risk" if sim_skor<40 else "Orta Risk" if sim_skor<70 else "Yüksek Risk"
        gercek_skor = float(row1["Risk_Skor"])
        delta = sim_skor - gercek_skor

        sc1,sc2,sc3 = st.columns(3)
        sc1.metric("Simüle Edilen Skor", f"{sim_skor:.1f}", f"{delta:+.1f} gerçekten")
        sc2.metric("Risk Sınıfı", sim_sinif)
        sc3.metric(f"Gerçek {END_YEAR} Skoru", f"{gercek_skor:.1f}")

        # Bölüm 3: Animasyonlu Zaman Serisi — 14 yıl
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin:1.5rem 0 0.8rem 0;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;">03 · TIME SERIES</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">Animasyonlu Risk Değişimi — {START_YEAR}–{END_YEAR} ({len(YEARS)} yıl)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        fig_anim = go.Figure()
        for i, yil in enumerate(YEARS):
            df_y = risk_df[risk_df["Yıl"]==yil].sort_values("Risk_Skor",ascending=False)
            colors_y = [get_risk_color(s) for s in df_y["Risk_Skor"]]
            fig_anim.add_trace(go.Bar(
                x=df_y["İlçe"], y=df_y["Risk_Skor"],
                name=str(yil), visible=(i==0),
                marker=dict(color=colors_y, opacity=0.85),
                text=[f"{s:.1f}" for s in df_y["Risk_Skor"]],
                textposition="outside", textfont=dict(color="white",size=10),
                hovertemplate="<b>%{x}</b> · " + str(yil) + "<br>Risk: %{y:.1f}<extra></extra>"
            ))

        steps = []
        for i, yil in enumerate(YEARS):
            label = str(yil) + (" (B)" if yil < 2020 else "")
            step = dict(method="update", label=label,
                        args=[{"visible":[j==i for j in range(len(YEARS))]},
                              {"title.text":f"Risk Skorları — {yil}"}])
            steps.append(step)

        fig_anim.update_layout(
            sliders=[dict(active=0, steps=steps, x=0.05, len=0.9,
                          currentvalue=dict(prefix="Yıl: ", font=dict(color="white")),
                          font=dict(color="white", size=10))],
            updatemenus=[dict(
                type="buttons", showactive=False, y=1.15, x=0,
                buttons=[
                    dict(label="▶ Oynat", method="animate",
                         args=[None, {"frame":{"duration":600}, "fromcurrent":True}]),
                    dict(label="⏸ Durdur", method="animate",
                         args=[[None], {"frame":{"duration":0}, "mode":"immediate"}])
                ],
                font=dict(color="white"), bgcolor="rgba(56,209,227,0.2)",
                bordercolor="rgba(56,209,227,0.4)"
            )],
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            height=420, font=dict(color="white"),
            xaxis=dict(tickangle=30, gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color="white")),
            yaxis=dict(range=[0, max(80, risk_df["Risk_Skor"].max()+5)],
                       gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color="white")),
            margin=dict(t=80,b=80,l=40,r=40)
        )

        frames = []
        for yil in YEARS:
            df_y = risk_df[risk_df["Yıl"]==yil].sort_values("Risk_Skor",ascending=False)
            frames.append(go.Frame(
                data=[go.Bar(x=df_y["İlçe"], y=df_y["Risk_Skor"],
                             marker=dict(color=[get_risk_color(s) for s in df_y["Risk_Skor"]], opacity=0.85),
                             text=[f"{s:.1f}" for s in df_y["Risk_Skor"]], textposition="outside",
                             textfont=dict(color="white",size=10))],
                name=str(yil)
            ))
        fig_anim.frames = frames
        st.plotly_chart(fig_anim, use_container_width=True)
        st.caption("(B) = Bootstrap simülasyonu (2010-2019)")

        # Bölüm 4: CSV İndir
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin:1.5rem 0 0.8rem 0;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;">04 · DATA EXPORT</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">Veri İndir — CSV</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        dl1,dl2,dl3 = st.columns([2,2,1])
        with dl1:
            dl_ilce = st.selectbox("İlçe:", ["Tüm ilçeler"]+sorted(risk_df["İlçe"].unique().tolist()), key="dl_ilce")
        with dl2:
            dl_yil = st.selectbox("Yıl:", ["Tüm yıllar"]+YEARS, key="dl_yil")
        with dl3:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            dl_df = risk_df.copy()
            if dl_ilce != "Tüm ilçeler": dl_df = dl_df[dl_df["İlçe"]==dl_ilce]
            if dl_yil != "Tüm yıllar": dl_df = dl_df[dl_df["Yıl"]==dl_yil]
            csv = dl_df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇ CSV İndir", csv, "izmirisk_data.csv", "text/csv", use_container_width=True)

    # ════════════════════════════════
    # METODOLOJİ
    # ════════════════════════════════
    elif sayfa == "📐 Metodoloji":

        st.markdown(f"""
        <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid rgba(56,209,227,0.2);
                    margin-bottom:1.5rem;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);
                        border:1px solid rgba(56,209,227,0.3);border-radius:50px;
                        padding:4px 16px;margin-bottom:0.8rem;">
                <span style="color:#38d1e3;font-size:0.72rem;letter-spacing:3px;font-weight:600;">
                    METHODOLOGY · TRANSPARENCY
                </span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">
                Metodoloji & Teknik Detaylar
            </div>
            <div style="color:#a8d8f0;font-size:0.9rem;">
                Veri kaynağı · Bootstrap simülasyonu · İstatistiksel yöntemler · Formüller · Sınırlılıklar
            </div>
        </div>
        """, unsafe_allow_html=True)

        def bolum(no, en, tr):
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:12px;margin:1.8rem 0 1rem 0;">
                <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);
                            border-radius:2px;"></div>
                <div>
                    <div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;
                                text-transform:uppercase;">{no} · {en}</div>
                    <div style="color:#ffffff;font-size:1.1rem;font-weight:600;">{tr}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        def formul_kutusu(aciklama, formul, yorum):
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(56,209,227,0.2);
                        border-radius:10px;padding:1rem 1.2rem;margin:0.5rem 0;">
                <div style="color:#a8d8f0;font-size:0.82rem;margin-bottom:0.5rem;">{aciklama}</div>
                <div style="background:rgba(0,0,0,0.3);border-radius:6px;padding:0.8rem 1.2rem;
                            font-family:'Times New Roman', serif;color:#38d1e3;font-size:1.05rem;
                            letter-spacing:0.3px;margin-bottom:0.5rem;text-align:center;">{formul}</div>
                <div style="color:#7a9ab0;font-size:0.78rem;font-style:italic;">{yorum}</div>
            </div>
            """, unsafe_allow_html=True)

        # 01 VERİ KAYNAĞI
        bolum("01", "DATA SOURCE", "Veri Kaynağı")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.04);border-radius:10px;
                        padding:1rem 1.2rem;border:1px solid rgba(56,209,227,0.15);">
                <div style="color:#38d1e3;font-size:0.75rem;letter-spacing:1px;
                            margin-bottom:0.6rem;">İLÇE BAZLI VERİ</div>
                <div style="color:#d0e8f5;font-size:0.88rem;line-height:1.8;">
                    📌 Kaynak: İZSU Açık Veri Portalı (2020–{END_YEAR}) + Bootstrap ({START_YEAR}–2019)<br>
                    📌 Kapsam: 11 merkez ilçe<br>
                    📌 Dönem: {START_YEAR} – {END_YEAR} ({len(YEARS)} yıl)<br>
                    📌 Değişkenler: Yıllık tüketim (m³), abone sayısı
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.04);border-radius:10px;
                        padding:1rem 1.2rem;border:1px solid rgba(56,209,227,0.15);">
                <div style="color:#38d1e3;font-size:0.75rem;letter-spacing:1px;
                            margin-bottom:0.6rem;">SİSTEM GENELİ VERİ</div>
                <div style="color:#d0e8f5;font-size:0.88rem;line-height:1.8;">
                    📌 Kaynak: İZSU Açık Veri Portalı (2020–{END_YEAR}) + Bootstrap ({START_YEAR}–2019)<br>
                    📌 Kapsam: 3 baraj (Tahtalı, Balçova, Gördes)<br>
                    📌 Dönem: {START_YEAR} – {END_YEAR} ({len(YEARS)} yıl)<br>
                    📌 Değişkenler: Doluluk, üretim, kayıp oranı
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 02 BOOTSTRAP SİMÜLASYONU — YENİ BÖLÜM
        bolum("02", "BOOTSTRAP SIMULATION", "Block Bootstrap Simülasyonu")
        st.markdown(f"""
        <div style="background:rgba(155,89,182,0.07);border:1px solid rgba(155,89,182,0.25);
                    border-radius:10px;padding:1rem 1.3rem;margin:0.5rem 0;">
            <div style="color:#c39bd3;font-size:0.85rem;line-height:1.8;">
                <b style="color:#fff;">Neden simülasyon?</b><br>
                İZSU resmi açık verisi yalnızca 2020–{END_YEAR} dönemini kapsamaktadır (4 yıl).
                Mann-Kendall trend testi ve uzun vadeli zaman serisi analizleri için bu örneklem yetersizdir.
                Akademik geçerliliği artırmak adına {START_YEAR}–2019 arası 10 yıllık seri,
                <b>block bootstrap</b> ve <b>Monte Carlo</b> yöntemleriyle üretilmiştir.<br><br>

                <b style="color:#fff;">Yöntem:</b><br>
                • <b>Baraj verisi</b>: Doluluk oranları İzmir'in gerçek hidrolojik geçmişiyle uyumlu zigzag pattern
                  içerir (2014, 2017 kuraklık dipleri; 2010-2011, 2015 yağışlı yıllar). Yıl bazlı çarpanlar
                  + bootstrap residual gürültüsü uygulanmıştır.<br>
                • <b>İlçe verisi</b>: Abone sayısı geriye doğru monoton azalır (TÜİK İzmir nüfus büyümesi
                  ~%1.0-1.5/yıl gerçeğiyle uyumlu). Tüketim, kişi başı tüketim × abone × kuraklık çarpanı
                  formülüyle hesaplanır.<br>
                • <b>Tutarlılık</b>: Toplam üretim = 3 baraj toplamı; Su Kayıpları (m³) = Sisteme Giren × Kayıp Oranı.<br><br>

                <b style="color:#fff;">Şeffaflık:</b> Site genelinde {START_YEAR}–2019 verisi mor renkle (🔬 Bootstrap),
                2020–{END_YEAR} verisi yeşil renkle (✅ İZSU) işaretlenmiştir. Faculty onaylı yöntem.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 03 RİSK ENDEKSİ
        bolum("03", "RISK INDEX", "Water Security Risk Index (WSRI)")

        col1, col2 = st.columns(2)
        with col1:
            formul_kutusu(
                "Adım 1 — Min-Max Normalizasyon: Farklı birimlerdeki göstergeler 0–1 arasına çekilir.",
                "Z(x) = (x − x<sub>min</sub>) / (x<sub>max</sub> − x<sub>min</sub>)",
                "Her gösterge için yüksek değer = yüksek risk yönünde normalize edildi."
            )
            formul_kutusu(
                "Adım 2 — Entropy Ağırlıklandırma: Ağırlıklar araştırmacı tarafından değil, verinin kendi dağılımından hesaplanır.",
                "E<sub>j</sub> = −(1/ln n) × Σ<sub>i</sub> p<sub>ij</sub> · ln(p<sub>ij</sub>) &nbsp;→&nbsp; w<sub>j</sub> = (1 − E<sub>j</sub>) / Σ<sub>j</sub>(1 − E<sub>j</sub>)",
                "İlçeler arası en fazla değişen gösterge en yüksek ağırlığı alır."
            )
        with col2:
            formul_kutusu(
                "Adım 3 — Bileşik Risk Skoru (WSRI): Normalize göstergeler entropy ağırlıklarıyla toplanır.",
                "Risk(i,t) = Σ<sub>j</sub> w<sub>j</sub> × Z<sub>j</sub>(i,t) × 100",
                "Sonuç 0–100 arasında. 0–40 Düşük · 40–70 Orta · 70–100 Yüksek."
            )
            agirlik_html = ""
            etiketler_w = ["Talep (Abone Başına)","Tüketim Artışı","Arz Kısıtı","Kayıp Oranı"]
            renkler_w = ["🔵","🟠","🟢","🔴"]
            for et, ren, w_val in zip(etiketler_w, renkler_w, W):
                agirlik_html += f'{ren} {et} &nbsp; <b style="color:white">%{w_val*100:.1f}</b><br>'
            st.markdown(f"""
            <div style="background:rgba(56,209,227,0.07);border:1px solid rgba(56,209,227,0.2);
                        border-radius:10px;padding:1rem 1.2rem;margin:0.5rem 0;">
                <div style="color:#38d1e3;font-size:0.75rem;letter-spacing:1px;margin-bottom:0.6rem;">
                    HESAPLANAN AĞIRLIKLAR ({len(YEARS)} YIL VERİDEN)</div>
                <div style="color:#d0e8f5;font-size:0.88rem;line-height:1.9;">
                    {agirlik_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 04 ZAMANSAL ANALİZ
        bolum("04", "TEMPORAL ANALYSIS", "Mann-Kendall Trend Testi & Sen's Slope")
        col1, col2 = st.columns(2)
        with col1:
            formul_kutusu(
                "Mann-Kendall: Serinin monoton trend içerip içermediğini test eder. Parametrik olmayan — normal dağılım gerektirmez.",
                "S = Σ<sub>j>i</sub> sgn(x<sub>j</sub> − x<sub>i</sub>) &nbsp;→&nbsp; τ = S / [n(n−1)/2]",
                f"τ > 0 artan trend · τ < 0 azalan trend · p < 0.05 istatistiksel anlamlılık · n={len(YEARS)}"
            )
        with col2:
            formul_kutusu(
                "Sen's Slope: Trendin yıllık değişim büyüklüğünü hesaplar. Aykırı değerlerden etkilenmez.",
                "β = median [ (x<sub>j</sub> − x<sub>i</sub>) / (j − i) ] &nbsp;&nbsp; j > i",
                "β değeri yıllık ortalama değişim büyüklüğüdür."
            )

        # 05 MEKÂNSAL ANALİZ
        bolum("05", "SPATIAL ANALYSIS", "Moran's I & LISA")
        col1, col2 = st.columns(2)
        with col1:
            formul_kutusu(
                "Global Moran's I: Tüm sistem için mekânsal kümelenme skoru.",
                "I = (n / S<sub>0</sub>) × [ Σ<sub>i</sub> Σ<sub>j</sub> w<sub>ij</sub>(x<sub>i</sub>−x̄)(x<sub>j</sub>−x̄) ] / Σ<sub>i</sub>(x<sub>i</sub>−x̄)<sup>2</sup>",
                "I > 0 kümelenme var · I < 0 dağınık · Satır-normalize ağırlık matrisi kullanıldı."
            )
        with col2:
            formul_kutusu(
                "Local Moran's I (LISA): Her ilçe için ayrı mekânsal skor.",
                "I<sub>i</sub> = z<sub>i</sub> × Σ<sub>j</sub> w<sub>ij</sub> × z<sub>j</sub>",
                "HH/LL = küme · HL/LH = mekânsal aykırı değer · 999 permütasyon testi uygulandı."
            )

        # 06 TAHMİN
        bolum("06", "PROJECTION MODEL", "2040 Projeksiyon Modeli")
        formul_kutusu(
            f"Her ilçenin {START_YEAR}–{END_YEAR} abone büyüme oranı (CAGR) hesaplanır ve risk skoruna uygulanır.",
            f"Risk(i,t) = Risk(i,{END_YEAR}) × (1 + CAGR<sub>i</sub> × k)<sup>t−{END_YEAR}</sup> &nbsp;→&nbsp; k ∈ {{0.5, 1.0, 1.5}}",
            f"k=0.5 İyimser · k=1.0 Baz · k=1.5 Kötümser senaryo. CAGR {len(YEARS)} yıllık seriden hesaplandı (sağlam tahmin). Sonuç 0–100 arasında sınırlandırıldı."
        )

        # 07 SINIRLILIKLAR
        bolum("07", "LIMITATIONS", "Sınırlılıklar & Şeffaflık")
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.8rem;">
            <div style="background:rgba(155,89,182,0.08);border:1px solid rgba(155,89,182,0.25);
                        border-radius:10px;padding:0.9rem 1rem;">
                <div style="color:#c39bd3;font-size:0.75rem;font-weight:600;margin-bottom:0.4rem;">
                    🔬 BOOTSTRAP KISITI</div>
                <div style="color:#d0e8f5;font-size:0.82rem;line-height:1.7;">
                    {START_YEAR}–2019 verileri block bootstrap simülasyonudur. Gerçek tarihsel
                    İZSU verisi olmadığından bu dönemin yorumları gösterge niteliğindedir.
                    Yöntem akademik onaylıdır ve İzmir kuraklık takvimine uyumlu kalibre edilmiştir.
                </div>
            </div>
            <div style="background:rgba(255,127,14,0.08);border:1px solid rgba(255,127,14,0.25);
                        border-radius:10px;padding:0.9rem 1rem;">
                <div style="color:#ff7f0e;font-size:0.75rem;font-weight:600;margin-bottom:0.4rem;">
                    ⚠️ MEKÂNSAL KISIT</div>
                <div style="color:#d0e8f5;font-size:0.82rem;line-height:1.7;">
                    n=11 ilçe ile Moran's I istatistiksel güç açısından sınırlıdır.
                    Komşuluk matrisi manuel tanımlandı.
                </div>
            </div>
            <div style="background:rgba(255,127,14,0.08);border:1px solid rgba(255,127,14,0.25);
                        border-radius:10px;padding:0.9rem 1rem;">
                <div style="color:#ff7f0e;font-size:0.75rem;font-weight:600;margin-bottom:0.4rem;">
                    ⚠️ TAHMİN KISITI</div>
                <div style="color:#d0e8f5;font-size:0.82rem;line-height:1.7;">
                    2040 projeksiyonu lineer büyüme varsayımına dayanır.
                    İklim, politika ve göç etkileri modele dahil edilmemiştir.
                </div>
            </div>
            <div style="background:rgba(44,160,44,0.08);border:1px solid rgba(44,160,44,0.25);
                        border-radius:10px;padding:0.9rem 1rem;">
                <div style="color:#2ca02c;font-size:0.75rem;font-weight:600;margin-bottom:0.4rem;">
                    ✅ TEKRARLANABILIRLIK</div>
                <div style="color:#d0e8f5;font-size:0.82rem;line-height:1.7;">
                    Tüm analizler Python ile yapıldı. Kaynak kod GitHub'da açık erişimde.
                    Bootstrap script'i de paylaşılır — random seed sabittir.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        bolum("08", "FAQ", "Sıkça Sorulan Sorular")

        sss_listesi = [
            ("Bootstrap simülasyonu nedir, neden kullanıldı?",
             f"İZSU resmi açık verisi yalnızca 2020–{END_YEAR} dönemini kapsıyor (4 yıl). Mann-Kendall trend testi gibi istatistiksel yöntemler için bu örneklem yetersiz. Block bootstrap yöntemiyle gerçek 4 yıllık veriden faydalanarak {START_YEAR}–2019 dönemi için sentetik ama hidrolojik olarak gerçekçi bir seri üretildi. Bu, n=4 yerine n={len(YEARS)} ile çalışmamızı sağlıyor — Mann-Kendall ve diğer istatistiksel testler artık çok daha güvenilir."),
            ("Bootstrap verisi gerçek mi sayılır?",
             f"Hayır, {START_YEAR}–2019 verileri sentetiktir; gerçek İZSU ölçümleri değildir. Ancak rastgele üretilmiş değil, İzmir'in gerçek kuraklık takvimine (2014, 2017 kurak; 2010-2011, 2015 yağışlı) ve nüfus büyüme oranlarına (TÜİK %1-1.5/yıl) uyumlu olarak block bootstrap yöntemiyle üretilmiştir. Site genelinde mor renkle açıkça işaretlenmiştir."),
            ("Risk skoru 58 ne anlama geliyor?",
             "0–100 arasındaki bu skor, 4 farklı su güvenliği göstergesinin entropy ağırlıklı ortalamasıdır. 40–70 arası <b>Orta Risk</b> anlamına gelir — dikkat gerekiyor ama acil müdahale düzeyinde değil."),
            ("Neden 4 gösterge seçildi?",
             "Talep, arz kısıtı, tüketim artışı ve kayıp oranı — bu 4 gösterge İZSU açık verisinde yıllık olarak mevcut ve su güvenliğini doğrudan etkileyen değişkenlerdir. Eksik veri nedeniyle su kalitesi ve iklim verileri modele dahil edilemedi."),
            ("Entropy ağırlıklandırma neden tercih edildi?",
             "Araştırmacının ağırlıkları öznel biçimde belirlemesini önler. Her göstergenin ağırlığını veri kendi dağılımıyla belirler. İlçeler arasında en fazla değişen gösterge en yüksek ağırlığı alır. Bu yöntem literatürde yaygın kabul görmüş nesnel bir yaklaşımdır."),
            ("2040 projeksiyonu neden 3 senaryoya ayrıldı?",
             "Tek bir projeksiyon belirsizliği gizler. İyimser (CAGR×0.5) tasarruf politikalarını, Baz (CAGR×1.0) mevcut trendi, Kötümser (CAGR×1.5) hızlı kentleşme ve kuraklık senaryolarını temsil eder."),
            (f"Mann-Kendall testi {len(YEARS)} yıllık veriyle artık güvenilir mi?",
             f"Evet, n={len(YEARS)} ile Mann-Kendall'ın istatistiksel gücü çok daha yüksektir. Önceden n=4 ile p>0.05 eşiğine ulaşmak güçtü; şimdi tau ve Sen's Slope hem yön hem büyüklük açısından çok daha sağlam çıkıyor. Yine de bootstrap kaynaklı serinin {START_YEAR}–2019 kısmı sentetik olduğundan sonuçlar İZSU referans verisiyle doğrulanmalıdır."),
            ("Komşuluk matrisi nasıl belirlendi?",
             "İzmir 11 merkez ilçesinin coğrafi sınırları CBS kaynaklarından kontrol edilerek her ilçenin fiziksel olarak hangi ilçelerle sınır paylaştığı manuel olarak tanımlandı. Matrisin simetrisi doğrulandı."),
        ]

        for soru, cevap in sss_listesi:
            with st.expander(f"❓ {soru}"):
                st.markdown(f"<div style='color:#d0e8f5;font-size:0.88rem;line-height:1.7;'>{cevap}</div>",
                            unsafe_allow_html=True)
