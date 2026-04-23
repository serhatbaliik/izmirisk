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

    yillar_pred = list(range(2024,2031))
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
            "gelecek": "Mevcut gidişat devam ederse 2030'da da düşük risk bekleniyor."
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
            "gelecek": "Kötümser senaryoda 2030'da yüksek riske geçme ihtimali var."
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
            "gelecek": "Önlem alınmazsa 2030'da risk skoru kritik seviyelere ulaşabilir."
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

    # ── Üst navigasyon - ORTALANMIŞ VE BÜYÜTÜLMÜŞ
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:center;
                padding:20px 0 16px 0;border-bottom:1px solid rgba(56,209,227,0.2);margin-bottom:0.8rem;">
        <div style="text-align:center;">
            <div style="display:flex;align-items:center;justify-content:center;gap:16px;margin-bottom:8px;">
                <span style="font-size:3rem;">💧</span>
                <div style="color:#ffffff;font-size:2.4rem;font-weight:800;
                            letter-spacing:-0.8px;line-height:1.1;">İzmiRisk</div>
            </div>
            <div style="color:#38d1e3;font-size:0.85rem;letter-spacing:2.5px;text-transform:uppercase;
                        font-weight:600;">
                Su Güvenliği Risk Endeksi · İzmir · 2010–2030
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if "secili_sayfa" not in st.session_state:
        st.session_state.secili_sayfa = "🏠 Ana Sayfa"

    SAYFALAR = [
        ("🏠", "Ana Sayfa",      "🏠 Ana Sayfa"),
        ("📊", "Keşifsel Analiz","📊 EDA Analizi"),
        ("📈", "Risk Endeksi",   "📈 Risk Endeksi"),
        ("🔮", "2030 Senaryosu", "🔮 2030 Tahmin"),
        ("🗺️","Risk Haritası",  "İzmir Risk Haritası"),
        ("📍", "Mekânsal Analiz","🗺️ Mekânsal Analiz"),
        ("💡", "Öneriler",       "💡 Öneriler"),
        ("📐", "Metodoloji",     "📐 Metodoloji"),
        ("🔬", "Araçlar",        "🔬 Araçlar"),
    ]

    aktif = st.session_state.secili_sayfa
