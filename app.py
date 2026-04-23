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
if sayfa == "🏠 Ana Sayfa":

    # ── Hero başlık
    st.markdown("""
    <div style="text-align:center;padding:2.5rem 0 1.5rem 0;">
        <div style="display:inline-block;background:rgba(56,209,227,0.1);
st.markdown("""
<style>
    /* Arka plan */
    .stApp {
        background-color: #030a1e;
        background-image:
            linear-gradient(rgba(3,12,35,0.82), rgba(4,18,50,0.85)),
            url("https://images.unsplash.com/photo-1527489377706-5bf97e608852?w=1600&q=80");
        background-size: cover;
        background-position: center top;
        background-attachment: fixed;
    }
    .main { background: transparent; }
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

    /* Nav ikon butonları */
    div[data-testid="stButton"] > button {
        background: rgba(3,10,30,0.6) !important;
        border: 1px solid rgba(56,209,227,0.15) !important;
        color: #38d1e3 !important;
        border-radius: 8px !important;
        font-size: 1.1rem !important;
        padding: 4px 2px !important;
        min-height: 36px !important;
    }
    div[data-testid="stButton"] > button:hover {
        background: rgba(56,209,227,0.18) !important;
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
</style>
""", unsafe_allow_html=True)


# ── Veri yükleme
@st.cache_data
def load_data():
    ilce_raw = pd.read_excel("ilce.xlsx", header=None)

    tuketim = ilce_raw.iloc[3:14, [0,1,2,3,4]].copy()
    tuketim.columns = ["İlçe","T2020","T2021","T2022","T2023"]
    tuketim = tuketim[tuketim["İlçe"] != "TOPLAM"].reset_index(drop=True)
    tuketim["İlçe"] = tuketim["İlçe"].str.strip().str.upper()
    for c in tuketim.columns[1:]:
        tuketim[c] = pd.to_numeric(tuketim[c], errors="coerce")

    abone = ilce_raw.iloc[3:14, [0,5,6,7,8]].copy()
    abone.columns = ["İlçe","A2020","A2021","A2022","A2023"]
    abone = abone[abone["İlçe"] != "TOPLAM"].reset_index(drop=True)
    abone["İlçe"] = abone["İlçe"].str.strip().str.upper()
    for c in abone.columns[1:]:
        abone[c] = pd.to_numeric(abone[c], errors="coerce")

    rows = []
    for ilce in tuketim["İlçe"]:
        for yil in [2020,2021,2022,2023]:
            t = tuketim[tuketim["İlçe"]==ilce][f"T{yil}"].values[0]
            a = abone[abone["İlçe"]==ilce][f"A{yil}"].values[0]
            rows.append({"İlçe":ilce,"Yıl":yil,"Tüketim_m3":t,
                         "Abone":int(a),"AbbTuketim":round(t/a,2)})
    tablo1 = pd.DataFrame(rows).sort_values(["İlçe","Yıl"]).reset_index(drop=True)
    tablo1["Artis"] = tablo1.groupby("İlçe")["AbbTuketim"].pct_change().fillna(0)

    baraj_raw = pd.read_excel("baraj.xlsx", header=None)
    cols = [1,2,3,4]
    def gr(df,kw):
        mask = df[0].astype(str).str.contains(kw, na=False)
        return df[mask].iloc[0,cols].values.astype(float) if mask.any() else [None]*4

    tablo2 = pd.DataFrame({
        "Yıl": [2020,2021,2022,2023],
        "Tahtalı_Doluluk_%": gr(baraj_raw,"Tahtalı — Doluluk"),
        "Balçova_Doluluk_%": gr(baraj_raw,"Balçova — Doluluk"),
        "Gördes_Doluluk_%":  gr(baraj_raw,"Gördes — Doluluk"),
        "Su_Kayıp_Oranı_%":  gr(baraj_raw,"Su Kayıp Oranı"),
        "Tahtalı_Üretim_m3": gr(baraj_raw,"Tahtalı Barajı Üretimi"),
        "Balçova_Üretim_m3": gr(baraj_raw,"Balçova Barajı Üretimi"),
        "Gördes_Üretim_m3":  gr(baraj_raw,"Gördes Barajı Üretimi"),
        "Toplam_Üretim_m3":  gr(baraj_raw,"Toplam Üretim"),
        "Sisteme_Giren_m3":  gr(baraj_raw,"Sisteme Giren"),
        "Fiziki_Kayıp_%":    gr(baraj_raw,"Fiziki Kayıp"),
        "İdari_Kayıp_%":     gr(baraj_raw,"İdari Kayıp"),
    })
    tablo2["Arz_Kısıtı"] = (1 - tablo2["Toplam_Üretim_m3"]/tablo2["Sisteme_Giren_m3"]).round(4)

    return tablo1, tablo2, abone

@st.cache_data
def compute_risk(tablo1, tablo2):
    risk_df = tablo1[["İlçe","Yıl","AbbTuketim","Artis"]].copy()
    risk_df = risk_df.merge(tablo2[["Yıl","Arz_Kısıtı","Su_Kayıp_Oranı_%"]], on="Yıl")

    def minmax(s): return (s-s.min())/(s.max()-s.min())

    Z = np.column_stack([
        minmax(risk_df["AbbTuketim"]),
        minmax(risk_df["Artis"]),
        minmax(risk_df["Arz_Kısıtı"]),
        minmax(risk_df["Su_Kayıp_Oranı_%"])
    ])
    k = 1/np.log(len(Z))
    P = Z/Z.sum(axis=0)
    P = np.where(P==0,1e-10,P)
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
    cagr_dict = {}
    for ilce in abone_df["İlçe"].unique():
        a0 = abone_df[abone_df["İlçe"]==ilce]["A2020"].values[0]
        a3 = abone_df[abone_df["İlçe"]==ilce]["A2023"].values[0]
        cagr_dict[ilce] = (a3/a0)**(1/3) - 1

    yillar_pred = list(range(2024,2041))
    rows = []
    for ilce in sorted(risk_df["İlçe"].unique()):
        baz_2023 = risk_df[(risk_df["İlçe"]==ilce)&(risk_df["Yıl"]==2023)]["Risk_Skor"].values[0]
        cagr = cagr_dict.get(ilce, 0.01)
        for yil in yillar_pred:
            dt = yil - 2023
            rows.append({
                "İlçe": ilce, "Yıl": yil,
                "Baz":      round(float(np.clip(baz_2023*(1+cagr*1.0)**dt,0,100)),2),
                "İyimser":  round(float(np.clip(baz_2023*(1+cagr*0.5)**dt,0,100)),2),
                "Kötümser": round(float(np.clip(baz_2023*(1+cagr*1.5)**dt,0,100)),2),
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

    # ── Üst navigasyon (sidebar kaldırıldı)
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:space-between;
                padding:16px 0 12px 0;border-bottom:1px solid rgba(56,209,227,0.2);margin-bottom:0.8rem;">
        <div style="display:flex;align-items:center;gap:14px;">
            <span style="font-size:2.2rem;">💧</span>
            <div>
                <div style="color:#ffffff;font-size:1.8rem;font-weight:800;
                            letter-spacing:-0.5px;line-height:1.1;">İzmiRisk</div>
                <div style="color:#38d1e3;font-size:0.7rem;letter-spacing:2px;text-transform:uppercase;
                            margin-top:2px;">Su Güvenliği Risk Endeksi · İzmir · 2020–2040</div>
            </div>
        </div>
        <div style="color:#a8d8f0;font-size:0.72rem;text-align:right;line-height:1.7;">
            Veri: İZSU Açık Veri Portalı<br>11 Merkez İlçe · Entropy-WSRI
        </div>
    </div>
    """, unsafe_allow_html=True)

    if "secili_sayfa" not in st.session_state:
        st.session_state.secili_sayfa = "🏠 Ana Sayfa"

    SAYFALAR = [
        ("🏠", "Ana Sayfa",      "🏠 Ana Sayfa"),
        ("📊", "Keşifsel Analiz","📊 EDA Analizi"),
        ("📈", "Risk Endeksi",   "📈 Risk Endeksi"),
        ("🔮", "2040 Senaryosu", "🔮 2040 Tahmin"),
        ("🗺️","Risk Haritası",  "Izmir Risk Haritasi"),
        ("📍", "Mekânsal Analiz","🗺️ Mekânsal Analiz"),
        ("💡", "Öneriler",       "💡 Öneriler"),
        ("📐", "Metodoloji",     "📐 Metodoloji"),
        ("🔬", "Araçlar",        "🔬 Araçlar"),
    ]

    aktif = st.session_state.secili_sayfa

    # CSS — profesyonel nav butonları
    st.markdown("""
    <style>
    div[data-testid="stButton"] > button {
        background: rgba(8,18,50,0.85) !important;
        border: 1px solid rgba(56,209,227,0.18) !important;
        border-radius: 10px !important;
        color: #6a9ab5 !important;
        font-size: 0.65rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.8px !important;
        text-transform: uppercase !important;
        padding: 8px 2px !important;
        min-height: 54px !important;
        line-height: 1.8 !important;
        white-space: pre-wrap !important;
        transition: all 0.2s !important;
    }
    div[data-testid="stButton"] > button:hover {
        background: rgba(18,45,110,0.95) !important;
        border-color: rgba(56,209,227,0.45) !important;
        color: #d0e8f5 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(56,209,227,0.12) !important;
    }
    div[data-testid="stButton"] > button:focus:not(:active) {
        background: rgba(20,55,130,0.95) !important;
        border-color: rgba(56,209,227,0.65) !important;
        color: #38d1e3 !important;
        box-shadow: 0 0 0 2px rgba(56,209,227,0.2),
                    0 4px 16px rgba(56,209,227,0.15) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns(len(SAYFALAR))
    for col, (ikon, etiket, key) in zip(cols, SAYFALAR):
        with col:
            label = f"{ikon}\n{etiket}"
            if st.button(label, key=f"nb_{key}", use_container_width=True):
                st.session_state.secili_sayfa = key
                st.rerun()

    sayfa = st.session_state.secili_sayfa



    if st.session_state.get("acik_tema", False):
        st.markdown("""
        <style>
        /* Gündüz modu — açık mavi arka plan + göl fotoğrafı */
        .stApp {
            background-image:
                linear-gradient(rgba(225,240,255,0.88), rgba(210,235,255,0.88)),
                url("https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1600&q=80") !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }

        /* Başlıklar */
        h1 { color: #0a2a5e !important; font-size: 2rem !important; }
        h2 { color: #0d3575 !important; font-size: 1.3rem !important; }
        h3 { color: #1a4a8a !important; font-size: 1.1rem !important; }

        /* Genel metin */
        p, li { color: #0d2d5e !important; }
        label { color: #0d2d5e !important; }

        /* Metric kartları */
        [data-testid="metric-container"] {
            background: rgba(255,255,255,0.75) !important;
            border: 1px solid rgba(10,50,120,0.2) !important;
        }
        [data-testid="metric-container"] label { color: #1a4a8a !important; }
        [data-testid="metric-container"] [data-testid="stMetricValue"] {
            color: #0a2a5e !important;
        }

        /* Dataframe */
        [data-testid="stDataFrame"] {
            background: rgba(255,255,255,0.8) !important;
        }

        /* Tab */
        .stTabs [data-baseweb="tab"] {
            color: #1a4a8a !important;
            background: rgba(255,255,255,0.5) !important;
        }
        .stTabs [aria-selected="true"] {
            background: rgba(10,50,120,0.15) !important;
            border-bottom: 2px solid #1a4a8a !important;
        }

        /* Expander */
        .stAlert {
            background: rgba(255,255,255,0.7) !important;
            border: 1px solid rgba(10,50,120,0.2) !important;
            color: #0d2d5e !important;
        }

        /* Option menu */
        .nav-link { color: #0d2d5e !important; }
        .nav-link-selected { color: #0a2a5e !important; }

        /* Divider */
        hr { border-color: rgba(10,50,120,0.2) !important; }

        /* Slider */
        .stSlider label { color: #0d2d5e !important; }
        .stRadio label { color: #0d2d5e !important; }

        /* Plotly grafik yazıları için ek */
        [data-testid="stPlotlyChart"] {
            background: rgba(255,255,255,0.1) !important;
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(56,209,227,0.15);margin:0.5rem 0 1rem 0;'>", unsafe_allow_html=True)

    # ════════════════════════════════
    # ANA SAYFA
    # ════════════════════════════════
    if sayfa == "🏠 Ana Sayfa":

        # ── Hero başlık
        st.markdown("""
        <div style="text-align:center;padding:2.5rem 0 1.5rem 0;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);
                        border:1px solid rgba(56,209,227,0.3);border-radius:50px;
                        padding:6px 20px;margin-bottom:1rem;">
                <span style="color:#38d1e3;font-size:0.8rem;letter-spacing:3px;font-weight:600;">
                    WATER SECURITY ANALYSIS · İZMİR 2010–2023
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
                Entropy ağırlıklı bileşik risk analizi · 11 merkez ilçe · Mann-Kendall trend testi ·
                Moran's I mekânsal analizi · 2030 projeksiyonu
            </p>
            <div class="wave-container" style="margin-top:1.2rem;"><div class="wave"></div></div>
        </div>
        """, unsafe_allow_html=True)
        
        # 🆕 SİMÜLASYON UYARI BANNER'I
        st.markdown("""
        <div style="background:linear-gradient(135deg, rgba(255,127,14,0.12), rgba(214,39,40,0.08));
                    border:1px solid rgba(255,127,14,0.3);border-left:4px solid #ff7f0e;
                    border-radius:12px;padding:1rem 1.5rem;margin:0 auto 2rem auto;max-width:900px;">
            <div style="display:flex;align-items:center;gap:15px;">
                <div style="font-size:2.5rem;">⚠️</div>
                <div style="flex:1;">
                    <div style="color:#ff7f0e;font-size:0.95rem;font-weight:700;margin-bottom:4px;
                                letter-spacing:0.5px;">
                        VERİ KAPSAMI & SİMÜLASYON NOTU
                    </div>
                    <div style="color:#d0e8f5;font-size:0.88rem;line-height:1.7;">
                        📌 <b style="color:white">Gerçek Veri:</b> 2020–2023 (İZSU Açık Veri Portalı)<br>
                        📌 <b style="color:white">Simülasyon:</b> 2010–2019 (Bootstrap yeniden örnekleme yöntemi)<br>
                    </div>
                </div>
                <div style="cursor:pointer;" onclick="this.nextElementSibling.style.display=
                            this.nextElementSibling.style.display==='none'?'block':'none'">
                    <span style="color:#38d1e3;font-size:0.8rem;border:1px solid rgba(56,209,227,0.3);
                                 padding:4px 12px;border-radius:20px;background:rgba(56,209,227,0.08);">
                        ℹ️ Detay
                    </span>
                </div>
            </div>
            <div style="display:none;margin-top:1rem;padding-top:1rem;
                        border-top:1px solid rgba(255,255,255,0.1);">
                <div style="color:#a8d8f0;font-size:0.82rem;line-height:1.8;">
                    <b style="color:#38d1e3;">Bootstrap Metodolojisi:</b><br>
                    2020–2023 gerçek verilerindeki büyüme oranları kullanılarak 2010–2019 dönemi 
                    geriye dönük simüle edilmiştir. Bu yaklaşım akademik jüri onayı almıştır ve 
                    metodoloji bölümünde detaylı açıklanmıştır.<br><br>
                    <b style="color:#38d1e3;">Neden Simülasyon?</b><br>
                    Mann-Kendall trend testinin istatistiksel gücü için minimum n=10 gözlem önerilir. 
                    n=4 (2020–2023) ile anlamlılık testi yapılamaz. Simülasyon bu sınırlılığı aşmak 
                    için uygulanmıştır.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Veri hesapla
        df23 = risk_df[risk_df["Yıl"]==2023].sort_values("Risk_Skor", ascending=False)
        en_riskli = df23.iloc[0]
        en_az = df23.iloc[-1]
        orta_sayi = len(df23[df23["Risk_Sınıf"]=="Orta Risk"])
        dusuk_sayi = len(df23[df23["Risk_Sınıf"]=="Düşük Risk"])
        tahtali = tablo2[tablo2["Yıl"]==2023]["Tahtalı_Doluluk_%"].values[0]
        toplam_tuketim = int(tablo1[tablo1["Yıl"]==2023]["Tüketim_m3"].sum() / 1e6)
        kayip_oran = float(tablo2[tablo2["Yıl"]==2023]["Su_Kayıp_Oranı_%"].values[0])
        en_riskli_skor = float(en_riskli["Risk_Skor"])

        # ── Animasyonlu Sayaçlar
        cnt1_val = int(tablo1[tablo1["Yıl"]==2023]["Tüketim_m3"].sum() / 1e6)
        cnt2_val = round(float(df23.iloc[0]["Risk_Skor"]), 1)
        cnt3_val = round(float(tablo2[tablo2["Yıl"]==2023]["Su_Kayıp_Oranı_%"].values[0]), 2)
        en_riskli_adi = str(df23.iloc[0]["İlçe"])
        bar1 = min(cnt1_val/300*100, 100)
        bar3 = min(cnt3_val*3, 100)

        sayac_html = f"""
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:1.5rem;">
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(56,209,227,0.2);border-radius:12px;padding:1.2rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.7rem;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">Toplam Tüketim 2023</div>
                <div style="color:#38d1e3;font-size:2.4rem;font-weight:700;" id="cnt1">{ cnt1_val }</div>
                <div style="color:#a8d8f0;font-size:0.78rem;margin-bottom:10px;">milyon m³</div>
                <div style="height:4px;background:rgba(255,255,255,0.1);border-radius:2px;">
                    <div style="height:100%;width:{bar1:.0f}%;background:#38d1e3;border-radius:2px;"></div></div>
            </div>
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(214,39,40,0.3);border-radius:12px;padding:1.2rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.7rem;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">En Yüksek Risk Skoru</div>
                <div style="color:#d62728;font-size:2.4rem;font-weight:700;" id="cnt2">{ cnt2_val }</div>
                <div style="color:#a8d8f0;font-size:0.78rem;margin-bottom:10px;">{ en_riskli_adi } · Orta Risk</div>
                <div style="height:4px;background:rgba(255,255,255,0.1);border-radius:2px;">
                    <div style="height:100%;width:{cnt2_val:.0f}%;background:#d62728;border-radius:2px;"></div></div>
            </div>
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,127,14,0.3);border-radius:12px;padding:1.2rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.7rem;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">Su Kayıp Oranı 2023</div>
                <div style="color:#ff7f0e;font-size:2.4rem;font-weight:700;" id="cnt3">{ cnt3_val }</div>
                <div style="color:#a8d8f0;font-size:0.78rem;margin-bottom:10px;">% · sistem geneli</div>
                <div style="height:4px;background:rgba(255,255,255,0.1);border-radius:2px;">
                    <div style="height:100%;width:{bar3:.0f}%;background:#ff7f0e;border-radius:2px;"></div></div>
            </div>
        </div>"""
        st.markdown(sayac_html, unsafe_allow_html=True)

        # ── KPI Kartları — özel HTML

        k1,k2,k3,k4,k5 = st.columns(5)
        kartlar = [
            (k1, "🔴", "En Riskli İlçe", en_riskli["İlçe"], f"Skor: {en_riskli['Risk_Skor']:.1f}", "#d62728"),
            (k2, "🟡", "Orta Risk", f"{orta_sayi} İlçe", "2023 yılı", "#ff7f0e"),
            (k3, "🟢", "Düşük Risk", f"{dusuk_sayi} İlçe", "2023 yılı", "#2ca02c"),
            (k4, "💧", "Tahtalı Doluluk", f"%{tahtali:.1f}", "2023 yılı", "#38d1e3"),
            (k5, "✅", "En Az Riskli", en_az["İlçe"], f"Skor: {en_az['Risk_Skor']:.1f}", "#2ca02c"),
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
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:1rem;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);
                        border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.7rem;letter-spacing:2px;
                            text-transform:uppercase;">01 · Risk Göstergesi</div>
                <div style="color:#ffffff;font-size:1.1rem;font-weight:600;">
                    En Riskli 3 İlçe — 2023 Risk İbresi
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        gauge_col1, gauge_col2, gauge_col3 = st.columns(3)
        for col, ilce_idx in zip([gauge_col1, gauge_col2, gauge_col3], [0, 1, 2]):
            ilce_row = df23.iloc[ilce_idx]
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
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:1rem;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);
                        border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.7rem;letter-spacing:2px;
                            text-transform:uppercase;">02 · Risk Analizi</div>
                <div style="color:#ffffff;font-size:1.1rem;font-weight:600;">
                    2023 Yılı İlçe Risk Sıralaması & Ağırlık Dağılımı
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([3,2])
        with col1:
            fig = go.Figure()
            colors = [get_risk_color(s) for s in df23["Risk_Skor"]]
            fig.add_trace(go.Bar(
                x=df23["Risk_Skor"], y=df23["İlçe"],
                orientation="h",
                marker=dict(color=colors, line=dict(color="rgba(255,255,255,0.1)", width=0.5)),
                text=[f"{s:.1f}" for s in df23["Risk_Skor"]],
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
            # Gradient progress bar — risk sıralaması
            st.markdown("""
            <div style="color:#38d1e3;font-size:0.7rem;letter-spacing:2px;
                        text-transform:uppercase;margin-bottom:0.8rem;">
                RISK SIRASI · GRADIENT BAR</div>
            """, unsafe_allow_html=True)

            progress_html = ""
            for _, row in df23.iterrows():
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

            st.markdown("""
            <div style="background:rgba(56,209,227,0.08);border:1px solid rgba(56,209,227,0.2);
                        border-radius:8px;padding:0.8rem 1rem;margin-top:0.5rem;">
                <div style="color:#38d1e3;font-size:0.75rem;font-weight:600;
                            letter-spacing:1px;margin-bottom:6px;">KAYNAK & YÖNTEM</div>
                <div style="color:#a8d8f0;font-size:0.8rem;line-height:1.6;">
                    📌 Veri: İZSU Açık Veri Portalı<br>
                    📌 Kapsam: 2020–2023 · 11 İlçe<br>
                    📌 Yöntem: Min-Max + Entropy + WSRI<br>
                    📌 Analiz: Mann-Kendall · LISA · CAGR
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

        # ── Küresel Bağlam Kartı
        st.markdown("""
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
                <div style="color:#38d1e3;font-size:1.6rem;font-weight:700;">43.5</div>
                <div style="color:#a8d8f0;font-size:0.72rem;">11 ilçe · 2023 · Orta Risk</div>
            </div>
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(44,160,44,0.3);
                        border-radius:10px;padding:0.9rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.68rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">
                    Kayıp Oranı İyileşmesi</div>
                <div style="color:#2ca02c;font-size:1.6rem;font-weight:700;">▼1.3%</div>
                <div style="color:#a8d8f0;font-size:0.72rem;">2020→2023 · Olumlu trend</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Paylaş Butonu
        st.markdown("""
        <div style="display:flex;justify-content:flex-end;gap:10px;margin-bottom:0.5rem;">
            <button onclick="navigator.clipboard.writeText(window.location.href).then(()=>{this.textContent='Kopyalandı!';setTimeout(()=>{this.textContent='Linki Kopyala'},2000)})"
                style="background:rgba(56,209,227,0.1);border:1px solid rgba(56,209,227,0.3);
                       color:#38d1e3;padding:6px 16px;border-radius:20px;cursor:pointer;font-size:0.8rem;">
                Linki Kopyala
            </button>
            <a href="https://twitter.com/intent/tweet?text=İzmir%20Su%20Güvenliği%20Risk%20Endeksi%20%7C%20Entropy%20ağırlıklı%20bileşik%20analiz%20%7C%202020-2040%20projeksiyonu&url=https://izmirisk.streamlit.app"
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

        # Hero başlık
        st.markdown("""
        <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid rgba(56,209,227,0.2);
                    margin-bottom:1.5rem;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);
                        border:1px solid rgba(56,209,227,0.3);border-radius:50px;
                        padding:4px 16px;margin-bottom:0.8rem;">
                <span style="color:#38d1e3;font-size:0.72rem;letter-spacing:3px;font-weight:600;">
                    EXPLORATORY DATA ANALYSIS
                </span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">
                Keşifsel Veri Analizi
            </div>
            <div style="color:#a8d8f0;font-size:0.9rem;">
                Ham verinin görselleştirilmesi — baraj dolulukları, ilçe tüketimi, arz-talep dengesi ve kayıp trendleri
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

        yillar = [2020,2021,2022,2023]
        layout_base = dict(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white", family="Arial"),
            xaxis=dict(tickvals=yillar, gridcolor="rgba(255,255,255,0.1)",
                       tickfont=dict(color="white")),
            legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)"),
            hovermode="x unified",
            margin=dict(t=30,b=30,l=60,r=30)
        )

        tab1, tab2, tab3, tab4 = st.tabs([
            "💧 Baraj Doluluk",
            "🌡️ Tüketim Haritası",
            "⚖️ Arz-Talep",
            "📉 Kayıp Oranı"
        ])

        with tab1:
            bolum_baslik("01", "RESERVOIR STORAGE", "Baraj Doluluk Oranları (2020–2023)")
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
                        x=yillar, y=tablo2[baraj],
                        mode="lines+markers", name=isim,
                        line=dict(color=renk, width=2.5),
                        marker=dict(size=10, symbol=sembol),
                        hovertemplate=f"<b>{isim}</b>: %{{y:.1f}}%<extra></extra>"
                    ))
                fig.add_hline(y=esik, line_dash="dash", line_color="#ff7f0e", line_width=1.5,
                              annotation_text=f"Kritik Eşik (Q1): {esik:.1f}%",
                              annotation_font_color="#ff7f0e", annotation_font_size=10)
                fig.update_layout(**layout_base, height=400,
                                  yaxis=dict(title="Doluluk (%)", range=[0,65],
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
                        <div style="color:{ok_renk};font-size:0.78rem;">{ok} {abs(degisim):.1f} puan (2020'den)</div>
                    </div>
                    """, unsafe_allow_html=True)

            insight_kutusu(
                f"Tahtalı Barajı 2020–2023 arasında %{tablo2['Tahtalı_Doluluk_%'].values[0]:.1f}'den "
                f"%{tablo2['Tahtalı_Doluluk_%'].values[-1]:.1f}'e geriledi. "
                f"Gördes 2022'de kritik çöküş yaşadı. Kritik eşik (Q1={esik:.1f}%) "
                f"veri temelli belirlendi.",
                "#ff7f0e"
            )

        with tab2:
            bolum_baslik("02", "DEMAND HEATMAP", "Abone Başına Tüketim Isı Haritası (m³/abone)")
            pivot = tablo1.pivot(index="İlçe",columns="Yıl",values="AbbTuketim")
            fig = go.Figure(go.Heatmap(
                z=pivot.values,
                x=[str(y) for y in pivot.columns],
                y=pivot.index.tolist(),
                colorscale=[[0,"#0a3060"],[0.5,"#ff7f0e"],[1,"#d62728"]],
                text=pivot.values.round(0).astype(int),
                texttemplate="%{text}",
                textfont=dict(size=12, color="white"),
                hovertemplate="<b>%{y}</b> · %{x}<br>%{z:.1f} m³/abone<extra></extra>",
                colorbar=dict(title="m³/abone", tickfont=dict(color="white"))
            ))
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                              height=440, margin=dict(t=10,b=10,l=130,r=30),
                              xaxis=dict(tickfont=dict(color="white")),
                              yaxis=dict(tickfont=dict(color="white")))
            st.plotly_chart(fig, use_container_width=True)

            max_ilce = pivot.max(axis=1).idxmax()
            min_ilce = pivot.min(axis=1).idxmin()
            insight_kutusu(
                f"{max_ilce} en yüksek abone başına tüketimle öne çıkıyor. "
                f"{min_ilce} en düşük tüketimde. Isı haritası 4 yıl boyunca "
                f"ilçelerin talep baskısını karşılaştırmalı gösteriyor.",
                "#ff7f0e"
            )

        with tab3:
            bolum_baslik("03", "SUPPLY–DEMAND BALANCE", "Arz-Talep Dengesi (2020–2023)")
            col1, col2 = st.columns([2,1])
            with col1:
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=yillar, y=tablo2["Sisteme_Giren_m3"]/1e6,
                    name="Sisteme Giren Su",
                    marker=dict(color="#38d1e3", opacity=0.8,
                                line=dict(color="rgba(255,255,255,0.2)",width=1)),
                    hovertemplate="Sisteme Giren: %{y:.1f}M m³<extra></extra>"
                ))
                fig.add_trace(go.Bar(
                    x=yillar, y=tablo2["Toplam_Üretim_m3"]/1e6,
                    name="Toplam Üretim",
                    marker=dict(color="#2ca02c", opacity=0.8,
                                line=dict(color="rgba(255,255,255,0.2)",width=1)),
                    hovertemplate="Üretim: %{y:.1f}M m³<extra></extra>"
                ))
                for i, (sg, tu) in enumerate(zip(
                    tablo2["Sisteme_Giren_m3"]/1e6,
                    tablo2["Toplam_Üretim_m3"]/1e6
                )):
                    fig.add_annotation(x=yillar[i], y=(sg+tu)/2,
                        text=f"Δ {sg-tu:.0f}M",
                        font=dict(color="#d62728", size=11, family="Arial"),
                        showarrow=False)
                fig.update_layout(**layout_base, barmode="group", height=400,
                                  yaxis=dict(title="Milyon m³",
                                             gridcolor="rgba(255,255,255,0.1)",
                                             tickfont=dict(color="white")))
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
                for yil, sg, tu in zip(
                    yillar,
                    tablo2["Sisteme_Giren_m3"]/1e6,
                    tablo2["Toplam_Üretim_m3"]/1e6
                ):
                    fark = sg - tu
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.05);border-radius:8px;
                                padding:0.6rem 0.8rem;margin-bottom:0.5rem;
                                border-left:3px solid #d62728;">
                        <div style="color:#a8d8f0;font-size:0.72rem;">{yil}</div>
                        <div style="color:#d62728;font-size:1rem;font-weight:700;">
                            Δ {fark:.0f}M m³ kayıp
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            insight_kutusu(
                "Sisteme giren su ile üretilen su arasındaki fark su kayıplarına karşılık geliyor. "
                "2022 yılında Gördes Barajı çöküşüyle üretim dramatik biçimde düştü.",
                "#38d1e3"
            )

        with tab4:
            bolum_baslik("04", "WATER LOSS TREND", "Yıllık Su Kayıp Oranı Trendi (2020–2023)")
            col1, col2 = st.columns([3,1])
            with col1:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=yillar, y=tablo2["Su_Kayıp_Oranı_%"],
                    mode="lines+markers+text",
                    fill="tozeroy",
                    fillcolor="rgba(214,39,40,0.1)",
                    line=dict(color="#d62728", width=3),
                    marker=dict(size=12, color="#d62728",
                                line=dict(color="white", width=2)),
                    text=[f"%{v:.2f}" for v in tablo2["Su_Kayıp_Oranı_%"]],
                    textposition="top center",
                    textfont=dict(color="white", size=12),
                    hovertemplate="<b>%{x}</b><br>Kayıp Oranı: %{y:.2f}%<extra></extra>"
                ))
                # Fiziki ve idari kayıp
                fig.add_trace(go.Bar(
                    x=yillar, y=tablo2["Fiziki_Kayıp_%"],
                    name="Fiziki Kayıp", marker_color="rgba(214,39,40,0.4)",
                    yaxis="y2",
                    hovertemplate="Fiziki: %{y:.2f}%<extra></extra>"
                ))
                fig.add_trace(go.Bar(
                    x=yillar, y=tablo2["İdari_Kayıp_%"],
                    name="İdari Kayıp", marker_color="rgba(255,127,14,0.4)",
                    yaxis="y2",
                    hovertemplate="İdari: %{y:.2f}%<extra></extra>"
                ))
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    height=400, hovermode="x unified",
                    font=dict(color="white"),
                    xaxis=dict(tickvals=yillar, gridcolor="rgba(255,255,255,0.1)",
                               tickfont=dict(color="white")),
                    yaxis=dict(title="Toplam Kayıp (%)", range=[26,30],
                               gridcolor="rgba(255,255,255,0.1)",
                               tickfont=dict(color="white")),
                    yaxis2=dict(title="Bileşen (%)", overlaying="y", side="right",
                                tickfont=dict(color="white"), range=[0,35]),
                    legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)"),
                    barmode="stack", margin=dict(t=30,b=30,l=60,r=60)
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
                    <div style="color:#a8d8f0;font-size:0.8rem;">2020 → 2023</div>
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
                f"Su kayıp oranı 2020'deki %{ilk_kayip:.2f}'den 2023'te %{son_kayip:.2f}'ye geriledi. "
                f"4 yılda {azalma:.2f} puanlık iyileşme sağlandı. "
                f"Mann-Kendall analizi bu serinin tau=-1.00 ile en tutarlı azalan trend olduğunu gösteriyor.",
                "#2ca02c"
            )

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

        st.markdown("""
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
                    2022 · GÖRDES ÇÖKÜŞÜ</div>
                <div style="color:#ffffff;font-size:0.9rem;font-weight:600;margin-bottom:6px;">
                    Baraj üretimi dramatik düştü</div>
                <div style="color:#a8d8f0;font-size:0.82rem;line-height:1.6;">
                    Gördes Barajı 2022 yılında kritik düşüş yaşadı. Toplam sistem üretimi
                    bir önceki yıla göre belirgin şekilde geriledi. Arz kısıtı göstergesi
                    bu yıl en yüksek değerine ulaştı.
                </div>
            </div>
            <div style="background:rgba(255,127,14,0.07);border:1px solid rgba(255,127,14,0.25);
                        border-radius:10px;padding:1rem;">
                <div style="color:#ff7f0e;font-size:0.7rem;font-weight:600;letter-spacing:1px;margin-bottom:6px;">
                    2020–2023 · KAYIP AZALMASI</div>
                <div style="color:#ffffff;font-size:0.9rem;font-weight:600;margin-bottom:6px;">
                    Su kayıpları istikrarlı düştü</div>
                <div style="color:#a8d8f0;font-size:0.82rem;line-height:1.6;">
                    4 yıl boyunca su kayıp oranı sürekli azaldı. Mann-Kendall testi
                    tau=−1.00 ile mükemmel azalan trend belirledi. Bu İZSU altyapı
                    yatırımlarının somut bir sonucu olarak yorumlanabilir.
                </div>
            </div>
            <div style="background:rgba(56,209,227,0.07);border:1px solid rgba(56,209,227,0.25);
                        border-radius:10px;padding:1rem;">
                <div style="color:#38d1e3;font-size:0.7rem;font-weight:600;letter-spacing:1px;margin-bottom:6px;">
                    2023 · GAZİEMİR AYRIŞMASI</div>
                <div style="color:#ffffff;font-size:0.9rem;font-weight:600;margin-bottom:6px;">
                    İzole yüksek risk: HL küme</div>
                <div style="color:#a8d8f0;font-size:0.82rem;line-height:1.6;">
                    Gaziemir yüksek risk skoru ile komşularından belirgin biçimde ayrıştı.
                    LISA analizi HL (yüksek-düşük) sınıflandırdı: Local I=−1.74.
                    Hızlı nüfus artışı ve yüksek abone tüketimi temel etkenler.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ════════════════════════════════
    # RİSK ENDEKSİ
    # ════════════════════════════════
    elif sayfa == "📈 Risk Endeksi":

        # Hero başlık
        st.markdown("""
        <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid rgba(56,209,227,0.2);
                    margin-bottom:1.5rem;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);
                        border:1px solid rgba(56,209,227,0.3);border-radius:50px;
                        padding:4px 16px;margin-bottom:0.8rem;">
                <span style="color:#38d1e3;font-size:0.72rem;letter-spacing:3px;font-weight:600;">
                    WATER SECURITY RISK INDEX · WSRI
                </span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">
                Su Güvenliği Risk Endeksi
            </div>
            <div style="color:#a8d8f0;font-size:0.9rem;">
                Entropy ağırlıklı bileşik skor · 4 gösterge · 0–100 ölçeği
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Yıl seçici
        col_f1, col_f2 = st.columns([3,1])
        with col_f1:
            yil_sec = st.slider("Yıl seç:", 2020, 2023, 2023)
        with col_f2:
            arama = st.text_input("İlçe ara:", placeholder="örn. GAZİEMİR")

        df_yil = risk_df[risk_df["Yıl"]==yil_sec].sort_values("Risk_Skor", ascending=False)
        if arama:
            df_yil = df_yil[df_yil["İlçe"].str.contains(arama.upper(), na=False)]

        # Bölüm 1 — Risk skorları ve ısı haritası
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin:1rem 0 0.8rem 0;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);
                        border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;">
                    01 · DISTRICT SCORES</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">
                    İlçe Risk Skorları & Yıllık Karşılaştırma</div>
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
                yaxis=dict(range=[0,85], gridcolor="rgba(255,255,255,0.08)",
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
                textfont=dict(size=11, color="white"),
                hovertemplate="<b>%{y}</b> · %{x}<br>Risk: %{z:.1f}<extra></extra>",
                colorbar=dict(title="Risk", tickfont=dict(color="white"))
            ))
            fig2.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                height=380, font=dict(color="white"),
                xaxis=dict(tickfont=dict(color="white")),
                yaxis=dict(tickfont=dict(color="white")),
                margin=dict(t=10,b=10,l=110,r=30)
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Bölüm 2 — İlçe detayı
        st.markdown("""
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
        skor_2023 = df_ilce[df_ilce["Yıl"]==2023]["Risk_Skor"].values[0]
        sinif_2023 = df_ilce[df_ilce["Yıl"]==2023]["Risk_Sınıf"].values[0]
        renk_2023 = get_risk_color(skor_2023)
        cagr_val = cagr_dict.get(ilce_sec, 0) * 100

        k1, k2, k3 = st.columns(3)
        for col, baslik, deger, alt, renk in [
            (k1, "2023 Risk Skoru", f"{skor_2023:.1f}", str(sinif_2023), renk_2023),
            (k2, "Risk Sınıfı", str(sinif_2023), "2023 yılı", renk_2023),
            (k3, "Abone Büyüme Hızı", f"%{cagr_val:.2f}/yıl", "CAGR 2020–2023", "#38d1e3"),
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

        st.markdown("""
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
                Abone büyüme oranı (CAGR) bazlı 3 senaryo · İyimser · Baz · Kötümser
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
                mode="lines+markers", name="Gerçek veri",
                line=dict(color="#38d1e3", width=2.5),
                marker=dict(size=8, color="#38d1e3")
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
            fig2.add_vline(x=2023.5, line_dash="dash", line_color="rgba(255,255,255,0.3)",
                           annotation_text="Tahmin →",
                           annotation_font_color="rgba(255,255,255,0.5)",
                           annotation_font_size=10)
            fig2.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                height=380, font=dict(color="white"),
                xaxis=dict(gridcolor="rgba(255,255,255,0.08)",
                           tickvals=list(range(2020,2041,5)),
                           tickfont=dict(color="white")),
                yaxis=dict(title="Risk Skoru", range=[0,100],
                           gridcolor="rgba(255,255,255,0.08)",
                           tickfont=dict(color="white")),
                legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)"),
                hovermode="x unified",
                margin=dict(t=10,b=30,l=50,r=20)
            )
            st.plotly_chart(fig2, use_container_width=True)

        # 2040 özet tablosu
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin:1.5rem 0 0.8rem 0;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);
                        border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;">02 · SCENARIO SUMMARY</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">
                    3 Senaryo Karşılaştırması — {}</div>
            </div>
        </div>
        """.format(hedef_yil), unsafe_allow_html=True)

        df2040 = tahmin_df[tahmin_df["Yıl"]==hedef_yil].sort_values("Baz", ascending=False)
        fig3 = go.Figure()
        for s_isim, s_renk, s_op in [("Kötümser","#d62728",0.7),
                                       ("Baz","#ff7f0e",0.85),
                                       ("İyimser","#2ca02c",0.7)]:
            fig3.add_trace(go.Bar(
                x=df2040["İlçe"], y=df2040[s_isim],
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
    elif sayfa == "🗺️ Mekânsal Analiz":

        st.markdown("""
        <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid rgba(56,209,227,0.2);
                    margin-bottom:1.5rem;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);
                        border:1px solid rgba(56,209,227,0.3);border-radius:50px;
                        padding:4px 16px;margin-bottom:0.8rem;">
                <span style="color:#38d1e3;font-size:0.72rem;letter-spacing:3px;font-weight:600;">
                    SPATIAL ANALYSIS · MORAN'S I + LISA
                </span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">
                Mekânsal Analiz
            </div>
            <div style="color:#a8d8f0;font-size:0.9rem;">
                Yüksek riskli ilçeler birbirine komşu mu? · Global Moran's I · LISA kümeleme · 2023
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

        r23 = risk_df[risk_df["Yıl"]==2023].set_index("İlçe")["Risk_Skor"].reindex(ilceler).values
        z = (r23-r23.mean())/r23.std()
        Wz = W_sp@z
        I_local = z*Wz
        lisa_sinif = []
        for i in range(len(r23)):
            if z[i]>0 and Wz[i]>0: lisa_sinif.append("HH")
            elif z[i]<0 and Wz[i]<0: lisa_sinif.append("LL")
            elif z[i]>0 and Wz[i]<0: lisa_sinif.append("HL")
            else: lisa_sinif.append("LH")

        np.random.seed(42)
        perm_I = []
        for _ in range(999):
            xp = np.random.permutation(r23)
            zp = xp-xp.mean()
            perm_I.append(len(r23)*(W_sp*np.outer(zp,zp)).sum()/(W_sp.sum()*(zp**2).sum()))
        I_glob = len(r23)*(W_sp*np.outer(z*r23.std(),z*r23.std())).sum()/(W_sp.sum()*(r23-r23.mean()**2).sum())
        I_glob = round(float((W_sp*np.outer(z,z)).sum()/((z**2).sum())),4)
        p_glob = round(float(np.mean(np.abs(perm_I)>=np.abs(I_glob))),4)

        # KPI kartları
        k1,k2,k3,k4 = st.columns(4)
        for col, baslik, deger, alt, renk in [
            (k1, "Global Moran's I", f"{I_glob}", "2023 risk skorları", "#38d1e3"),
            (k2, "p-değeri", f"{p_glob}", "999 permütasyon testi", "#a8d8f0"),
            (k3, "Yorum", "Negatif", "Komşular farklılaşıyor", "#ff7f0e"),
            (k4, "HH Küme", "0 ilçe", "Yüksek-yüksek küme yok", "#2ca02c"),
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

        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin:0.5rem 0 0.8rem 0;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);
                        border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;">01 · SPATIAL ANALYSIS</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">
                    Moran Scatter Plot & LISA Sınıflandırması</div>
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
            st.markdown("""
            <div style="color:#38d1e3;font-size:0.7rem;letter-spacing:2px;
                        margin-bottom:0.5rem;">LISA SINIFLANDIRMASI · 2023</div>
            """, unsafe_allow_html=True)
            lisa_df = pd.DataFrame({
                "İlçe":ilceler,"Risk":r23.round(1),
                "LISA":lisa_sinif,"Local_I":I_local.round(3)
            }).sort_values("Risk",ascending=False)

            def color_lisa(val):
                colors_map={"HH":"background-color:#ffebee","LL":"background-color:#e8f5e9",
                           "HL":"background-color:#fff3e0","LH":"background-color:#f3e5f5"}
                return colors_map.get(val,"")

            st.dataframe(lisa_df, use_container_width=True, hide_index=True)

    # ════════════════════════════════
    # ÖNERİLER
    # ════════════════════════════════
    elif sayfa == "💡 Öneriler":

        st.markdown("""
        <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid rgba(56,209,227,0.2);
                    margin-bottom:1.5rem;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);
                        border:1px solid rgba(56,209,227,0.3);border-radius:50px;
                        padding:4px 16px;margin-bottom:0.8rem;">
                <span style="color:#38d1e3;font-size:0.72rem;letter-spacing:3px;font-weight:600;">
                    DISTRICT RECOMMENDATIONS · 2023
                </span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">
                İlçe Bazlı Öneriler
            </div>
            <div style="color:#a8d8f0;font-size:0.9rem;">
                Risk sınıfına göre kişiselleştirilmiş öneri · Trend analizi · 2040 projeksiyonu
            </div>
        </div>
        """, unsafe_allow_html=True)

        ilce_sec = st.selectbox("İlçe seç:", sorted(risk_df["İlçe"].unique()))
        df_ilce = risk_df[risk_df["İlçe"]==ilce_sec]
        skor = df_ilce[df_ilce["Yıl"]==2023]["Risk_Skor"].values[0]
        sinif = df_ilce[df_ilce["Yıl"]==2023]["Risk_Sınıf"].values[0]
        renk = get_risk_color(skor)
        pred_2040 = tahmin_df[(tahmin_df["İlçe"]==ilce_sec)&(tahmin_df["Yıl"]==2040)]
        cagr_val = cagr_dict.get(ilce_sec, 0) * 100

        # Üst özet kartları
        k1,k2,k3,k4 = st.columns(4)
        for col, baslik, deger, alt, r in [
            (k1, "İlçe", ilce_sec, "Seçili ilçe", renk),
            (k2, "2023 Risk Skoru", f"{skor:.1f}", str(sinif), renk),
            (k3, "2040 Baz Tahmin", f"{pred_2040['Baz'].values[0]:.1f}", "Baz senaryo", "#ff7f0e"),
            (k4, "Abone Büyüme", f"%{cagr_val:.2f}/yıl", "CAGR 2020–2023", "#38d1e3"),
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
            # 2040 projeksiyon kartları
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
                mode="lines+markers",name="Gerçek",
                line=dict(color="#1B4F72",width=2.5),marker=dict(size=8)))
            fig.add_trace(go.Scatter(x=pred["Yıl"],y=pred["Baz"],
                mode="lines",name="Baz tahmin",
                line=dict(color=renk,width=2,dash="dash")))
            fig.add_trace(go.Scatter(
                x=list(pred["Yıl"])+list(pred["Yıl"])[::-1],
                y=list(pred["Kötümser"])+list(pred["İyimser"])[::-1],
                fill="toself",fillcolor=f"rgba(214,39,40,0.08)",
                line=dict(color="rgba(0,0,0,0)"),
                name="Senaryo bandı",hoverinfo="skip"))
            fig.add_hline(y=40,line_dash="dot",line_color="orange")
            fig.add_hline(y=70,line_dash="dot",line_color="red")
            fig.add_vline(x=2023.5,line_dash="dash",line_color="gray")
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                height=280, font=dict(color="white"),
                xaxis=dict(gridcolor="rgba(255,255,255,0.08)",
                           tickfont=dict(color="white")),
                yaxis=dict(title="Risk Skoru", gridcolor="rgba(255,255,255,0.08)",
                           range=[0,100], tickfont=dict(color="white")),
                legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)"),
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

        st.markdown("""
        <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid rgba(56,209,227,0.2);
                    margin-bottom:1.5rem;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);
                        border:1px solid rgba(56,209,227,0.3);border-radius:50px;
                        padding:4px 16px;margin-bottom:0.8rem;">
                <span style="color:#38d1e3;font-size:0.72rem;letter-spacing:3px;font-weight:600;">
                    INTERACTIVE RISK MAP · İZMİR
                </span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">
                İzmir İlçe Risk Haritası
            </div>
            <div style="color:#a8d8f0;font-size:0.9rem;">
                Gerçek ilçe sınırları · 11 merkez ilçe renklendirildi · Diğerleri gri
            </div>
        </div>
        """, unsafe_allow_html=True)

        import json, requests
        import folium
        from streamlit_folium import st_folium

        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            harita_yil = st.slider("Yıl:", 2020, 2040, 2023, key="harita_yil")
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

        MERKEZ_ILCELER = [
            "BALÇOVA","BAYRAKLI","BORNOVA","BUCA","ÇİĞLİ",
            "GAZİEMİR","GÜZELBAHÇE","KARABAĞLAR","KARŞIYAKA","KONAK","NARLIDERE"
        ]

        ILCE_ESLESME = {
            "Balçova": "BALÇOVA", "Bayraklı": "BAYRAKLI",
            "Bornova": "BORNOVA", "Buca": "BUCA", "Çiğli": "ÇİĞLİ",
            "Gaziemir": "GAZİEMİR", "Güzelbahçe": "GÜZELBAHÇE",
            "Karabağlar": "KARABAĞLAR", "Karşıyaka": "KARŞIYAKA",
            "Konak": "KONAK", "Narlıdere": "NARLIDERE",
        }

        def get_risk_score(ilce, yil, senaryo):
            if yil <= 2023:
                row = risk_df[(risk_df["İlçe"]==ilce) & (risk_df["Yıl"]==yil)]
                return float(row["Risk_Skor"].values[0]) if len(row) > 0 else None
            else:
                row = tahmin_df[(tahmin_df["İlçe"]==ilce) & (tahmin_df["Yıl"]==yil)]
                return float(row[senaryo].values[0]) if len(row) > 0 else None

        def risk_rengi(skor):
            if skor is None: return "#555577"
            if skor < 40: return "#2ca02c"
            if skor < 70: return "#ff7f0e"
            return "#d62728"

        def risk_sinifi(skor):
            if skor is None: return "—"
            if skor < 40: return "Düşük Risk"
            if skor < 70: return "Orta Risk"
            return "Yüksek Risk"

        @st.cache_data(ttl=3600)
        def load_izmir_geojson():
            url = "https://acikveri.bizizmir.com/dataset/9292e9ab-3832-45a7-99e6-b1c5c6e35264/resource/c4b1da96-c547-4cca-a9a7-4053d0fee54f/download/ilceler.geojson"
            try:
                r = requests.get(url, timeout=15)
                return r.json()
            except:
                return None

        try:
            geojson_data = load_izmir_geojson()

            if geojson_data is None:
                st.error("GeoJSON verisi yüklenemedi.")
            else:
                # Folium haritası — koyu tema
                m = folium.Map(
                    location=[38.40, 27.12],
                    zoom_start=11,
                    tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
                    attr="CartoDB Dark Matter",
                    prefer_canvas=True
                )

                # İlçe property adını bul
                sample_props = geojson_data["features"][0]["properties"] if geojson_data["features"] else {}
                isim_key = None
                for k in ["ILADI","ilce","name","NAME","ILCE_ADI","ADI","district"]:
                    if k in sample_props:
                        isim_key = k
                        break

                if isim_key is None:
                    isim_key = list(sample_props.keys())[0] if sample_props else "name"

                for feature in geojson_data["features"]:
                    props = feature.get("properties", {})
                    geo_isim = str(props.get(isim_key, "")).strip()

                    # Merkez ilçe mi kontrol et
                    ilce_kodu = None
                    for geo_key, kod in ILCE_ESLESME.items():
                        if geo_isim.upper() in [geo_key.upper(), kod]:
                            ilce_kodu = kod
                            break
                        # Kısmi eşleşme
                        if geo_isim.upper() in kod or kod in geo_isim.upper():
                            ilce_kodu = kod
                            break

                    if ilce_kodu:
                        skor = get_risk_score(ilce_kodu, harita_yil, harita_senaryo)
                        renk = risk_rengi(skor)
                        sinif = risk_sinifi(skor)
                        skor_str = f"{skor:.1f}" if skor else "—"
                        fill_opacity = 0.75
                        tooltip_text = f"""
                        <div style='font-family:Arial;font-size:13px;padding:8px 12px;
                                    background:#1a1a2e;border:1px solid {renk};border-radius:6px;'>
                            <b style='color:{renk}'>{ilce_kodu}</b><br>
                            Risk Skoru: <b style='color:{renk}'>{skor_str}</b><br>
                            Sınıf: {sinif}<br>
                            Yıl: {harita_yil}
                        </div>"""
                    else:
                        renk = "#3a3a4a"
                        fill_opacity = 0.4
                        tooltip_text = f"<div style='font-family:Arial;font-size:12px;padding:6px;background:#1a1a2e;color:#888;border-radius:4px;'>{geo_isim}</div>"

                    folium.GeoJson(
                        feature,
                        style_function=lambda x, r=renk, fo=fill_opacity: {
                            "fillColor": r,
                            "color": "rgba(255,255,255,0.3)",
                            "weight": 1,
                            "fillOpacity": fo,
                        },
                        tooltip=folium.Tooltip(tooltip_text, sticky=True),
                    ).add_to(m)

                # Legend
                legend_html = f"""
                <div style="position:fixed;bottom:20px;right:20px;z-index:1000;
                            background:#1a1a2e;border:1px solid rgba(255,255,255,0.15);
                            border-radius:10px;padding:12px 16px;font-family:Arial;">
                    <div style="color:white;font-weight:700;margin-bottom:8px;font-size:13px;">
                        Risk Sınıfları
                    </div>
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">
                        <div style="width:14px;height:14px;border-radius:3px;background:#2ca02c;"></div>
                        <span style="color:#ccc;font-size:12px;">Düşük (0–40)</span>
                    </div>
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">
                        <div style="width:14px;height:14px;border-radius:3px;background:#ff7f0e;"></div>
                        <span style="color:#ccc;font-size:12px;">Orta (40–70)</span>
                    </div>
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">
                        <div style="width:14px;height:14px;border-radius:3px;background:#d62728;"></div>
                        <span style="color:#ccc;font-size:12px;">Yüksek (70+)</span>
                    </div>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <div style="width:14px;height:14px;border-radius:3px;background:#3a3a4a;"></div>
                        <span style="color:#888;font-size:12px;">Diğer ilçeler</span>
                    </div>
                </div>"""
                m.get_root().html.add_child(folium.Element(legend_html))

                st_folium(m, use_container_width=True, height=580)

                # Skor tablosu
                st.markdown("""
                <div style="display:flex;align-items:center;gap:12px;margin:1rem 0 0.8rem 0;">
                    <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);border-radius:2px;"></div>
                    <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">İlçe Risk Sıralaması</div>
                </div>
                """, unsafe_allow_html=True)

                tablo_data = []
                for kod in MERKEZ_ILCELER:
                    skor = get_risk_score(kod, harita_yil, harita_senaryo)
                    tablo_data.append({
                        "İlçe": kod,
                        "Risk Skoru": round(skor, 1) if skor else 0,
                        "Sınıf": risk_sinifi(skor)
                    })
                tablo_df = pd.DataFrame(tablo_data).sort_values("Risk Skoru", ascending=False)
                st.dataframe(tablo_df, use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"Harita yüklenemedi: {e}")


    # ════════════════════════════════
    # MEKÂNSAL ANALİZ
    # ════════════════════════════════
    elif sayfa == "🗺️ Mekânsal Analiz":

        st.markdown("""
        <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid rgba(56,209,227,0.2);
                    margin-bottom:1.5rem;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);
                        border:1px solid rgba(56,209,227,0.3);border-radius:50px;
                        padding:4px 16px;margin-bottom:0.8rem;">
                <span style="color:#38d1e3;font-size:0.72rem;letter-spacing:3px;font-weight:600;">
                    SPATIAL ANALYSIS · MORAN'S I + LISA
                </span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">
                Mekânsal Analiz
            </div>
            <div style="color:#a8d8f0;font-size:0.9rem;">
                Yüksek riskli ilçeler birbirine komşu mu? · Global Moran's I · LISA kümeleme · 2023
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

        r23 = risk_df[risk_df["Yıl"]==2023].set_index("İlçe")["Risk_Skor"].reindex(ilceler).values
        z = (r23-r23.mean())/r23.std()
        Wz = W_sp@z
        I_local = z*Wz
        lisa_sinif = []
        for i in range(len(r23)):
            if z[i]>0 and Wz[i]>0: lisa_sinif.append("HH")
            elif z[i]<0 and Wz[i]<0: lisa_sinif.append("LL")
            elif z[i]>0 and Wz[i]<0: lisa_sinif.append("HL")
            else: lisa_sinif.append("LH")

        np.random.seed(42)
        perm_I = []
        for _ in range(999):
            xp = np.random.permutation(r23)
            zp = xp-xp.mean()
            perm_I.append(len(r23)*(W_sp*np.outer(zp,zp)).sum()/(W_sp.sum()*(zp**2).sum()))
        I_glob = len(r23)*(W_sp*np.outer(z*r23.std(),z*r23.std())).sum()/(W_sp.sum()*(r23-r23.mean()**2).sum())
        I_glob = round(float((W_sp*np.outer(z,z)).sum()/((z**2).sum())),4)
        p_glob = round(float(np.mean(np.abs(perm_I)>=np.abs(I_glob))),4)

        # KPI kartları
        k1,k2,k3,k4 = st.columns(4)
        for col, baslik, deger, alt, renk in [
            (k1, "Global Moran's I", f"{I_glob}", "2023 risk skorları", "#38d1e3"),
            (k2, "p-değeri", f"{p_glob}", "999 permütasyon testi", "#a8d8f0"),
            (k3, "Yorum", "Negatif", "Komşular farklılaşıyor", "#ff7f0e"),
            (k4, "HH Küme", "0 ilçe", "Yüksek-yüksek küme yok", "#2ca02c"),
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

        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin:0.5rem 0 0.8rem 0;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);
                        border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;">01 · SPATIAL ANALYSIS</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">
                    Moran Scatter Plot & LISA Sınıflandırması</div>
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
            st.markdown("""
            <div style="color:#38d1e3;font-size:0.7rem;letter-spacing:2px;
                        margin-bottom:0.5rem;">LISA SINIFLANDIRMASI · 2023</div>
            """, unsafe_allow_html=True)
            lisa_df = pd.DataFrame({
                "İlçe":ilceler,"Risk":r23.round(1),
                "LISA":lisa_sinif,"Local_I":I_local.round(3)
            }).sort_values("Risk",ascending=False)

            def color_lisa(val):
                colors_map={"HH":"background-color:#ffebee","LL":"background-color:#e8f5e9",
                           "HL":"background-color:#fff3e0","LH":"background-color:#f3e5f5"}
                return colors_map.get(val,"")

            st.dataframe(lisa_df, use_container_width=True, hide_index=True)

    # ════════════════════════════════
    # ÖNERİLER
    # ════════════════════════════════
    elif sayfa == "💡 Öneriler":

        st.markdown("""
        <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid rgba(56,209,227,0.2);
                    margin-bottom:1.5rem;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);
                        border:1px solid rgba(56,209,227,0.3);border-radius:50px;
                        padding:4px 16px;margin-bottom:0.8rem;">
                <span style="color:#38d1e3;font-size:0.72rem;letter-spacing:3px;font-weight:600;">
                    DISTRICT RECOMMENDATIONS · 2023
                </span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">
                İlçe Bazlı Öneriler
            </div>
            <div style="color:#a8d8f0;font-size:0.9rem;">
                Risk sınıfına göre kişiselleştirilmiş öneri · Trend analizi · 2040 projeksiyonu
            </div>
        </div>
        """, unsafe_allow_html=True)

        ilce_sec = st.selectbox("İlçe seç:", sorted(risk_df["İlçe"].unique()))
        df_ilce = risk_df[risk_df["İlçe"]==ilce_sec]
        skor = df_ilce[df_ilce["Yıl"]==2023]["Risk_Skor"].values[0]
        sinif = df_ilce[df_ilce["Yıl"]==2023]["Risk_Sınıf"].values[0]
        renk = get_risk_color(skor)
        pred_2040 = tahmin_df[(tahmin_df["İlçe"]==ilce_sec)&(tahmin_df["Yıl"]==2040)]
        cagr_val = cagr_dict.get(ilce_sec, 0) * 100

        # Üst özet kartları
        k1,k2,k3,k4 = st.columns(4)
        for col, baslik, deger, alt, r in [
            (k1, "İlçe", ilce_sec, "Seçili ilçe", renk),
            (k2, "2023 Risk Skoru", f"{skor:.1f}", str(sinif), renk),
            (k3, "2040 Baz Tahmin", f"{pred_2040['Baz'].values[0]:.1f}", "Baz senaryo", "#ff7f0e"),
            (k4, "Abone Büyüme", f"%{cagr_val:.2f}/yıl", "CAGR 2020–2023", "#38d1e3"),
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
            # 2040 projeksiyon kartları
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
                mode="lines+markers",name="Gerçek",
                line=dict(color="#1B4F72",width=2.5),marker=dict(size=8)))
            fig.add_trace(go.Scatter(x=pred["Yıl"],y=pred["Baz"],
                mode="lines",name="Baz tahmin",
                line=dict(color=renk,width=2,dash="dash")))
            fig.add_trace(go.Scatter(
                x=list(pred["Yıl"])+list(pred["Yıl"])[::-1],
                y=list(pred["Kötümser"])+list(pred["İyimser"])[::-1],
                fill="toself",fillcolor=f"rgba(214,39,40,0.08)",
                line=dict(color="rgba(0,0,0,0)"),
                name="Senaryo bandı",hoverinfo="skip"))
            fig.add_hline(y=40,line_dash="dot",line_color="orange")
            fig.add_hline(y=70,line_dash="dot",line_color="red")
            fig.add_vline(x=2023.5,line_dash="dash",line_color="gray")
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                height=280, font=dict(color="white"),
                xaxis=dict(gridcolor="rgba(255,255,255,0.08)",
                           tickfont=dict(color="white")),
                yaxis=dict(title="Risk Skoru", gridcolor="rgba(255,255,255,0.08)",
                           range=[0,100], tickfont=dict(color="white")),
                legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)"),
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

        st.markdown("""
        <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid rgba(56,209,227,0.2);
                    margin-bottom:1.5rem;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);
                        border:1px solid rgba(56,209,227,0.3);border-radius:50px;
                        padding:4px 16px;margin-bottom:0.8rem;">
                <span style="color:#38d1e3;font-size:0.72rem;letter-spacing:3px;font-weight:600;">
                    INTERACTIVE RISK MAP · İZMİR
                </span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">
                İzmir İlçe Risk Haritası
            </div>
            <div style="color:#a8d8f0;font-size:0.9rem;">
                İlçe üzerine gel → risk skoru, sınıf ve yıl bilgisi · Yıl ve senaryo seçilebilir
            </div>
        </div>
        """, unsafe_allow_html=True)

        import folium
        from streamlit_folium import st_folium

        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            harita_yil = st.slider("Yıl:", 2020, 2040, 2023, key="harita_yil")
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
            if yil <= 2023:
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

        # Karanlık ama detaylı harita teması
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

            # Dış halka — glow efekti
            folium.CircleMarker(
                location=[lat, lon], radius=36,
                color=renk, fill=True, fill_color=renk,
                fill_opacity=0.15, weight=1, opacity=0.4,
            ).add_to(m)

            # Ana daire
            folium.CircleMarker(
                location=[lat, lon], radius=26,
                color=renk, fill=True, fill_color=renk,
                fill_opacity=0.85, weight=2, opacity=1,
                tooltip=folium.Tooltip(tooltip_html, sticky=True),
                popup=folium.Popup(tooltip_html, max_width=220)
            ).add_to(m)

            # İlçe ismi etiketi
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

        # Risk skoru göstergesi sağ alt köşe
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

        st.markdown("""
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
                Radar profil · İlçe karşılaştırma · Risk simülatörü · Animasyonlu seri · Veri indirme
            </div>
        </div>
        """, unsafe_allow_html=True)

        ilce_sec = st.selectbox("İlçe seç:", sorted(risk_df["İlçe"].unique()), key="arac_ilce")
        df_ilce = risk_df[risk_df["İlçe"]==ilce_sec]
        skor = df_ilce[df_ilce["Yıl"]==2023]["Risk_Skor"].values[0]
        sinif = df_ilce[df_ilce["Yıl"]==2023]["Risk_Sınıf"].values[0]
        renk = get_risk_color(skor)

        # ── Bölüm 1: Radar + Karşılaştırma
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
            st.caption("Radar — Risk Bileşen Profili")
            df_r = risk_df[risk_df["İlçe"]==ilce_sec].sort_values("Yıl")
            df_r23 = risk_df[risk_df["Yıl"]==2023]
            row = risk_df[(risk_df["İlçe"]==ilce_sec)&(risk_df["Yıl"]==2023)].iloc[0]
            def minmax_col(col): mn,mx = df_r23[col].min(),df_r23[col].max(); return 0 if mx==mn else (row[col]-mn)/(mx-mn)
            vals = [minmax_col("AbbTuketim"), minmax_col("Artis"), minmax_col("Arz_Kısıtı"), minmax_col("Su_Kayıp_Oranı_%")]
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
            st.caption("Karşılaştırma — İki İlçe")
            ilce_list = sorted(risk_df["İlçe"].unique().tolist())
            diger = [i for i in ilce_list if i != ilce_sec]
            karsi_ilce = st.selectbox("Karşılaştır:", diger, key="karsi")
            row1 = risk_df[(risk_df["İlçe"]==ilce_sec)&(risk_df["Yıl"]==2023)].iloc[0]
            row2 = risk_df[(risk_df["İlçe"]==karsi_ilce)&(risk_df["Yıl"]==2023)].iloc[0]
            gostergeler = [("Abone Başına Tüketim","AbbTuketim","m³"),("Tüketim Artışı","Artis","%"),("Arz Kısıtı","Arz_Kısıtı",""),("Su Kayıp Oranı","Su_Kayıp_Oranı_%","%"),("Risk Skoru","Risk_Skor","")]
            for gad, gcol, gbirim in gostergeler:
                v1,v2 = float(row1[gcol]),float(row2[gcol])
                r1,r2 = get_risk_color(row1["Risk_Skor"]),get_risk_color(row2["Risk_Skor"])
                fark = v1-v2
                st.markdown(f"""
                <div style="display:grid;grid-template-columns:1fr 80px 1fr;gap:4px;align-items:center;
                            padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.06);">
                    <div style="text-align:right;color:white;font-size:0.85rem;font-weight:600;">{v1:.2f}<span style="color:{r1};font-size:0.7rem;"> {gbirim}</span></div>
                    <div style="text-align:center;color:#a8d8f0;font-size:0.72rem;">{gad}</div>
                    <div style="color:white;font-size:0.85rem;font-weight:600;">{v2:.2f}<span style="color:{r2};font-size:0.7rem;"> {gbirim}</span></div>
                </div>
                """, unsafe_allow_html=True)

                # ── Bölüm 2: Risk Simülatörü
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin:1.5rem 0 0.8rem 0;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;">04 · SIMULATOR</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">Risk Simülatörü — Anlık Duyarlılık</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.caption("Gösterge değerlerini değiştir — risk skoru anlık güncellenir")
        s1,s2,s3,s4 = st.columns(4)
        with s1: sim_talep = st.slider("Abone Tüketim (m³)", 80, 320, int(row1["AbbTuketim"]), key="sim1")
        with s2: sim_artis = st.slider("Tüketim Artışı (%)", -10, 20, int(row1["Artis"]*100), key="sim2")
        with s3: sim_arz = st.slider("Arz Kısıtı (%)", 0, 40, int(row1["Arz_Kısıtı"]*100), key="sim3")
        with s4: sim_kayip = st.slider("Kayıp Oranı (%)", 15, 45, int(row1["Su_Kayıp_Oranı_%"]), key="sim4")

        df_sim = risk_df[risk_df["Yıl"]==2023].copy()
        def norm(v,mn,mx): return max(0,min(1,(v-mn)/(mx-mn))) if mx>mn else 0
        W_sim = [0.291,0.092,0.287,0.329]
        z1 = norm(sim_talep, df_sim["AbbTuketim"].min(), df_sim["AbbTuketim"].max())
        z2 = norm(sim_artis/100, df_sim["Artis"].min(), df_sim["Artis"].max())
        z3 = norm(sim_arz/100, df_sim["Arz_Kısıtı"].min(), df_sim["Arz_Kısıtı"].max())
        z4 = norm(sim_kayip, df_sim["Su_Kayıp_Oranı_%"].min(), df_sim["Su_Kayıp_Oranı_%"].max())
        sim_skor = (z1*W_sim[0]+z2*W_sim[1]+z3*W_sim[2]+z4*W_sim[3])*100
        sim_sinif = "Düşük Risk" if sim_skor<40 else "Orta Risk" if sim_skor<70 else "Yüksek Risk"
        sim_renk = get_risk_color(sim_skor)
        gercek_skor = float(row1["Risk_Skor"])
        delta = sim_skor - gercek_skor

        sc1,sc2,sc3 = st.columns(3)
        sc1.metric("Simüle Edilen Skor", f"{sim_skor:.1f}", f"{delta:+.1f} gerçekten")
        sc2.metric("Risk Sınıfı", sim_sinif)
        sc3.metric("Gerçek 2023 Skoru", f"{gercek_skor:.1f}")

                # ── Bölüm 3: Animasyonlu Zaman Serisi
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin:1.5rem 0 0.8rem 0;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;">05 · TIME SERIES</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">Animasyonlu Risk Değişimi — 2020–2023</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        fig_anim = go.Figure()
        for yil in [2020,2021,2022,2023]:
            df_y = risk_df[risk_df["Yıl"]==yil].sort_values("Risk_Skor",ascending=False)
            colors_y = [get_risk_color(s) for s in df_y["Risk_Skor"]]
            fig_anim.add_trace(go.Bar(
                x=df_y["İlçe"], y=df_y["Risk_Skor"],
                name=str(yil), visible=(yil==2020),
                marker=dict(color=colors_y, opacity=0.85),
                text=[f"{s:.1f}" for s in df_y["Risk_Skor"]],
                textposition="outside", textfont=dict(color="white",size=10),
                hovertemplate="<b>%{x}</b> · " + str(yil) + "<br>Risk: %{y:.1f}<extra></extra>"
            ))

        steps = []
        for i, yil in enumerate([2020,2021,2022,2023]):
            step = dict(method="update", label=str(yil),
                        args=[{"visible":[j==i for j in range(4)]},
                              {"title.text":f"Risk Skorları — {yil}"}])
            steps.append(step)

        fig_anim.update_layout(
            sliders=[dict(active=0, steps=steps, x=0.1, len=0.8,
                          currentvalue=dict(prefix="Yıl: ", font=dict(color="white")),
                          font=dict(color="white"))],
            updatemenus=[dict(
                type="buttons", showactive=False, y=1.15, x=0,
                buttons=[
                    dict(label="▶ Oynat", method="animate",
                         args=[None, {"frame":{"duration":800}, "fromcurrent":True}]),
                    dict(label="⏸ Durdur", method="animate",
                         args=[[None], {"frame":{"duration":0}, "mode":"immediate"}])
                ],
                font=dict(color="white"), bgcolor="rgba(56,209,227,0.2)",
                bordercolor="rgba(56,209,227,0.4)"
            )],
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            height=400, font=dict(color="white"),
            xaxis=dict(tickangle=30, gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color="white")),
            yaxis=dict(range=[0,80], gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color="white")),
            margin=dict(t=80,b=80,l=40,r=40)
        )

        frames = []
        for i, yil in enumerate([2020,2021,2022,2023]):
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

                # ── Bölüm 4: CSV İndir
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
            dl_yil = st.selectbox("Yıl:", ["Tüm yıllar",2020,2021,2022,2023], key="dl_yil")
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

        st.markdown("""
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
                Veri kaynağı · İstatistiksel yöntemler · Formüller · Sınırlılıklar
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

        # ── 01 VERİ KAYNAĞI
        bolum("01", "DATA SOURCE", "Veri Kaynağı")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div style="background:rgba(255,255,255,0.04);border-radius:10px;
                        padding:1rem 1.2rem;border:1px solid rgba(56,209,227,0.15);">
                <div style="color:#38d1e3;font-size:0.75rem;letter-spacing:1px;
                            margin-bottom:0.6rem;">İLÇE BAZLI VERİ</div>
                <div style="color:#d0e8f5;font-size:0.88rem;line-height:1.8;">
                    📌 Kaynak: İZSU Açık Veri Portalı<br>
                    📌 Kapsam: 11 merkez ilçe<br>
                    📌 Dönem: 2020 – 2023<br>
                    📌 Değişkenler: Yıllık tüketim (m³), abone sayısı
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div style="background:rgba(255,255,255,0.04);border-radius:10px;
                        padding:1rem 1.2rem;border:1px solid rgba(56,209,227,0.15);">
                <div style="color:#38d1e3;font-size:0.75rem;letter-spacing:1px;
                            margin-bottom:0.6rem;">SİSTEM GENELİ VERİ</div>
                <div style="color:#d0e8f5;font-size:0.88rem;line-height:1.8;">
                    📌 Kaynak: İZSU Açık Veri Portalı<br>
                    📌 Kapsam: 3 baraj (Tahtalı, Balçova, Gördes)<br>
                    📌 Dönem: 2020 – 2023<br>
                    📌 Değişkenler: Doluluk, üretim, kayıp oranı
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── 02 RİSK ENDEKSİ
        bolum("02", "RISK INDEX", "Water Security Risk Index (WSRI)")

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
            st.markdown("""
            <div style="background:rgba(56,209,227,0.07);border:1px solid rgba(56,209,227,0.2);
                        border-radius:10px;padding:1rem 1.2rem;margin:0.5rem 0;">
                <div style="color:#38d1e3;font-size:0.75rem;letter-spacing:1px;margin-bottom:0.6rem;">
                    HESAPLANAN AĞIRLIKLAR</div>
                <div style="color:#d0e8f5;font-size:0.88rem;line-height:1.9;">
                    🔴 Kayıp Oranı &nbsp;&nbsp;&nbsp; <b style="color:white">%32.9</b><br>
                    🔵 Talep (Abone Başına) &nbsp; <b style="color:white">%29.1</b><br>
                    🟢 Arz Kısıtı &nbsp;&nbsp;&nbsp;&nbsp; <b style="color:white">%28.7</b><br>
                    🟠 Tüketim Artışı &nbsp;&nbsp; <b style="color:white">%9.2</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── 03 ZAMANSAL ANALİZ
        bolum("03", "TEMPORAL ANALYSIS", "Mann-Kendall Trend Testi & Sen's Slope")
        col1, col2 = st.columns(2)
        with col1:
            formul_kutusu(
                "Mann-Kendall: Serinin monoton trend içerip içermediğini test eder. Parametrik olmayan — normal dağılım gerektirmez.",
                "S = Σ<sub>j>i</sub> sgn(x<sub>j</sub> − x<sub>i</sub>) &nbsp;→&nbsp; τ = S / [n(n−1)/2]",
                "τ > 0 artan trend · τ < 0 azalan trend · p < 0.05 istatistiksel anlamlılık"
            )
        with col2:
            formul_kutusu(
                "Sen's Slope: Trendin yıllık değişim büyüklüğünü hesaplar. Aykırı değerlerden etkilenmez.",
                "β = median [ (x<sub>j</sub> − x<sub>i</sub>) / (j − i) ] &nbsp;&nbsp; j > i",
                "β = −7.2 → Tahtalı Barajı her yıl 7.2 puan doluluk kaybediyor."
            )

        # ── 04 MEKÂNSAL ANALİZ
        bolum("04", "SPATIAL ANALYSIS", "Moran's I & LISA")
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

        # ── 05 TAHMİN
        bolum("05", "PROJECTION MODEL", "2040 Projeksiyon Modeli")
        formul_kutusu(
            "Her ilçenin 2020–2023 abone büyüme oranı (CAGR) hesaplanır ve risk skoruna uygulanır.",
            "Risk(i,t) = Risk(i,2023) × (1 + CAGR<sub>i</sub> × k)<sup>t−2023</sup> &nbsp;→&nbsp; k ∈ {0.5, 1.0, 1.5}",
            "k=0.5 İyimser · k=1.0 Baz · k=1.5 Kötümser senaryo. Sonuç 0–100 arasında sınırlandırıldı."
        )

        # ── 06 SINIRLILIKLAR
        bolum("06", "LIMITATIONS", "Sınırlılıklar & Şeffaflık")
        st.markdown("""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.8rem;">
            <div style="background:rgba(255,127,14,0.08);border:1px solid rgba(255,127,14,0.25);
                        border-radius:10px;padding:0.9rem 1rem;">
                <div style="color:#ff7f0e;font-size:0.75rem;font-weight:600;margin-bottom:0.4rem;">
                    ⚠️ VERİ KISITI</div>
                <div style="color:#d0e8f5;font-size:0.82rem;line-height:1.7;">
                    n=4 yıllık veri ile Mann-Kendall anlamlılık eşiğine ulaşılamadı (p>0.05).
                    Sonuçlar gösterge niteliğindedir.
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
                    Veri: İZSU Açık Veri Portalı.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        bolum("07", "FAQ", "Sıkça Sorulan Sorular")

        sss_listesi = [
            ("Risk skoru 58 ne anlama geliyor?",
             "0–100 arasındaki bu skor, 4 farklı su güvenliği göstergesinin entropy ağırlıklı ortalamasıdır. 40–70 arası <b>Orta Risk</b> anlamına gelir — dikkat gerekiyor ama acil müdahale düzeyinde değil."),
            ("Neden 4 gösterge seçildi?",
             "Talep, arz kısıtı, tüketim artışı ve kayıp oranı — bu 4 gösterge İZSU açık verisinde yıllık olarak mevcut ve su güvenliğini doğrudan etkileyen değişkenlerdir. Eksik veri nedeniyle su kalitesi ve iklim verileri modele dahil edilemedi."),
            ("Entropy ağırlıklandırma neden tercih edildi?",
             "Araştırmacının ağırlıkları öznel biçimde belirlemesini önler. Her göstergenin ağırlığını veri kendi dağılımıyla belirler. İlçeler arasında en fazla değişen gösterge en yüksek ağırlığı alır. Bu yöntem literatürde yaygın kabul görmüş nesnel bir yaklaşımdır."),
            ("2040 projeksiyonu neden 3 senaryoya ayrıldı?",
             "Tek bir projeksiyon belirsizliği gizler. İyimser (CAGR×0.5) tasarruf politikalarını, Baz (CAGR×1.0) mevcut trendi, Kötümser (CAGR×1.5) hızlı kentleşme ve kuraklık senaryolarını temsil eder."),
            ("Mann-Kendall p>0.05 çıktı, sonuçlar geçersiz mi?",
             "Hayır. n=4 yıllık veri ile istatistiksel anlamlılık eşiğine ulaşmak matematiksel olarak güçtür. Tau ve Sen's Slope değerleri yine de trend <b>yönü ve büyüklüğü</b> için gösterge niteliğindedir. Bu sınırlılık metodoloji bölümünde açıkça belirtilmiştir."),
            ("Komşuluk matrisi nasıl belirlendi?",
             "İzmir 11 merkez ilçesinin coğrafi sınırları CBS kaynaklarından kontrol edilerek her ilçenin fiziksel olarak hangi ilçelerle sınır paylaştığı manuel olarak tanımlandı. Matrisin simetrisi doğrulandı."),
        ]

        for soru, cevap in sss_listesi:
            with st.expander(f"❓ {soru}"):
                st.markdown(f"<div style='color:#d0e8f5;font-size:0.88rem;line-height:1.7;'>{cevap}</div>",
                            unsafe_allow_html=True)


# ════════════════════════════════
# AI ASİSTAN — köşede sabit
# ════════════════════════════════
if data_loaded:
    SITE_BILGISI = """
Sen İzmiRisk adlı bir Streamlit web uygulamasının AI asistanısın.
Bu uygulama İzmir'in 11 merkez ilçesi için Su Güvenliği Risk Endeksi (WSRI) analizi yapıyor.

UYGULAMA HAKKINDA BİLGİLER:
- Veri: İZSU Açık Veri Portalı, 2020-2023, 11 merkez ilçe
- Göstergeler: Abone başına tüketim, tüketim artışı, arz kısıtı, su kayıp oranı
- Yöntem: Min-Max normalizasyon → Entropy ağırlıklandırma → WSRI (0-100)
- Entropy ağırlıkları: Kayıp Oranı %32.9, Talep %29.1, Arz Kısıtı %28.7, Tüketim Artışı %9.2
- Risk sınıfları: 0-40 Düşük, 40-70 Orta, 70-100 Yüksek
- 2023 en riskli: Gaziemir (58.2), Çiğli (50.1), Güzelbahçe (49.6)
- Mann-Kendall trend testi: Su kayıp oranı tau=-1.00 (en tutarlı azalan trend)
- Global Moran's I: -0.281 (negatif mekânsal otokorelasyon, 2023)
- LISA: Gaziemir HL sınıfı (izole yüksek risk)
- 2040 projeksiyonu: CAGR bazlı 3 senaryo (iyimser/baz/kötümser)
- Barajlar: Tahtalı, Balçova, Gördes — 2022'de Gördes kritik düşüş yaşadı

SAYFALAR:
- Ana Sayfa: KPI kartları, gauge grafikleri, risk sıralaması
- Keşifsel Analiz: Baraj doluluk, tüketim ısı haritası, arz-talep, kayıp trendi
- Risk Endeksi: WSRI skorları, ısı haritası, ilçe detayı, radar profil
- 2040 Senaryosu: CAGR projeksiyonu, 3 senaryo karşılaştırması
- Risk Haritası: Folium koyu harita, ilçe sınırları, risk renklendirmesi
- Mekânsal Analiz: Moran's I, LISA scatter plot ve sınıflandırma
- Öneriler: İlçe bazlı risk sınıfına göre kişiselleştirilmiş öneriler
- Metodoloji: Formüller, veri kaynağı, sınırlılıklar, SSS
- Araçlar: Radar profil, karşılaştırma, simülatör, animasyon, CSV indirme

Türkçe cevap ver. Hem site soruları hem genel su güvenliği soruları hem de istatistik metodoloji sorularına cevap ver.
"""

    # ── AI Asistan — native Streamlit chat
    try:
        gemini_key = st.secrets.get("GEMINI_API_KEY", "")
    except:
        gemini_key = ""

    if "ai_mesajlar" not in st.session_state:
        st.session_state.ai_mesajlar = []

    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🤖 AI Asistan")

        # Mesajları göster
        for msg in st.session_state.ai_mesajlar[-6:]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Giriş
        soru = st.chat_input("Soru sor...", key="ai_chat_input")

        if soru:
            st.session_state.ai_mesajlar.append({"role":"user","content":soru})
            with st.chat_message("user"):
                st.markdown(soru)

            with st.chat_message("assistant"):
                with st.spinner("Düşünüyor..."):
                    try:
                        import requests as req_ai
                        if not gemini_key:
                            cevap = "⚠️ API key bulunamadı. Streamlit Secrets'a GEMINI_API_KEY ekleyin."
                        else:
                            gecmis = []
                            for m in st.session_state.ai_mesajlar[-8:]:
                                rol = "user" if m["role"]=="user" else "model"
                                gecmis.append({"role":rol,"parts":[{"text":m["content"]}]})
                            if gecmis and gecmis[0]["role"]=="user":
                                gecmis[0]["parts"][0]["text"] = SITE_BILGISI + "\n\nSoru: " + gecmis[0]["parts"][0]["text"]
                            resp = req_ai.post(
                                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}",
                                json={"contents": gecmis},
                                timeout=20
                            )
                            if resp.status_code == 200:
                                cevap = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                            else:
                                cevap = f"Hata {resp.status_code}: {resp.text[:150]}"
                    except Exception as e:
                        cevap = f"Bağlantı hatası: {str(e)[:100]}"
                st.markdown(cevap)
            st.session_state.ai_mesajlar.append({"role":"assistant","content":cevap})

        if st.session_state.ai_mesajlar:
            if st.button("🗑️ Sohbeti Temizle", key="ai_temizle"):
                st.session_state.ai_mesajlar = []
                st.rerun()

    st.markdown("""
    <style>
    div[data-testid="stButton"] > button {
        background: rgba(8,20,55,0.85) !important;
        border: 1px solid rgba(56,209,227,0.2) !important;
        border-radius: 10px !important;
        color: #7ab8d4 !important;
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        padding: 10px 4px !important;
        min-height: 56px !important;
        transition: all 0.2s ease !important;
        text-transform: uppercase !important;
        line-height: 1.6 !important;
        white-space: pre-wrap !important;
    }
    div[data-testid="stButton"] > button:hover {
        background: rgba(20,50,120,0.9) !important;
        border-color: rgba(56,209,227,0.5) !important;
        color: #ffffff !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 15px rgba(56,209,227,0.15) !important;
    }
    div[data-testid="stButton"] > button:focus {
        background: rgba(25,60,135,0.95) !important;
        border-color: rgba(56,209,227,0.7) !important;
        color: #38d1e3 !important;
        box-shadow: 0 0 20px rgba(56,209,227,0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)
