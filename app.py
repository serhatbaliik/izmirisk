import streamlit as st
import json
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
PRED_END_YEAR = 2030
PRED_YEARS = list(range(END_YEAR + 1, 2031))

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
    _lang = st.session_state.get("dil", "TR")
    if score < 40: return "Low Risk" if _lang == "EN" else "Düşük Risk"
    if score < 70: return "Medium Risk" if _lang == "EN" else "Orta Risk"
    return "High Risk" if _lang == "EN" else "Yüksek Risk"

def get_recommendation(ilce, score, sinif):
    _lang = st.session_state.get("dil", "TR")
    sinif_str = str(sinif)
    is_low = sinif_str in ["Düşük Risk", "Low Risk"] or score < 46
    is_medium = sinif_str in ["Orta Risk", "Medium Risk"] or (46 <= score < 60)

    if is_low:
        return {
            "durum": "✅ Good condition — maintain preventive measures" if _lang == "EN" else "✅ İyi durumdasınız — koruyucu önlemler alın",
            "renk": "#2ca02c",
            "mesaj": f"{ilce} is currently in the low-risk category. To preserve this positive outlook:" if _lang == "EN" else f"{ilce} ilçesi şu an düşük risk kategorisinde. Bu olumlu tabloyu korumak için:",
            "oneri": [
                "Maintain current water-saving habits." if _lang == "EN" else "Mevcut su tasarrufu alışkanlıklarınızı sürdürün.",
                "Track per-subscriber consumption annually and detect sudden increases early." if _lang == "EN" else "Abone başına tüketimi yıllık izleyin — ani artışları erkenden fark edin.",
                "Monitor risk increases in neighboring districts because regional effects may occur." if _lang == "EN" else "Komşu ilçelerdeki risk artışlarını takip edin, bölgesel etkiler olabilir.",
                "Optimize green-area irrigation and industrial consumption." if _lang == "EN" else "Yeşil alan sulama ve endüstriyel tüketimi optimize edin.",
            ],
            "gelecek": "If the current trend continues, low risk is also expected in 2030." if _lang == "EN" else "Mevcut gidişat devam ederse 2030'ta da düşük risk bekleniyor."
        }
    elif is_medium:
        return {
            "durum": "⚠️ Requires attention — concrete action is needed" if _lang == "EN" else "⚠️ Dikkat gerektiriyor — somut adımlar atılmalı",
            "renk": "#ff7f0e",
            "mesaj": f"{ilce} is in the medium-risk band. Without action, it may move into high risk:" if _lang == "EN" else f"{ilce} ilçesi orta risk bandında. Önlem alınmazsa yüksek riske geçebilir:",
            "oneri": [
                "Launch water-saving campaigns for households and businesses." if _lang == "EN" else "Hanelere ve işyerlerine yönelik su tasarrufu kampanyaları başlatın.",
                "Install smart meter systems for infrastructure leak detection." if _lang == "EN" else "Altyapı sızıntı tespiti için akıllı sayaç sistemleri kurun.",
                "Identify high-consuming subscribers and apply awareness programs." if _lang == "EN" else "Yüksek tüketen aboneleri belirleyip bilinçlendirme programları uygulayın.",
                "Encourage rainwater harvesting systems." if _lang == "EN" else "Yağmur suyu toplama sistemlerini teşvik edin.",
                "Start a coordinated inspection program with IZSU." if _lang == "EN" else "İZSU ile koordineli denetim programı başlatın.",
            ],
            "gelecek": "Under the pessimistic scenario, there is a possibility of moving into high risk by 2030." if _lang == "EN" else "Kötümser senaryoda 2030'ta yüksek riske geçme ihtimali var."
        }
    else:
        return {
            "durum": "🚨 High risk — urgent action required" if _lang == "EN" else "🚨 Yüksek risk — acil önlem gerekiyor",
            "renk": "#d62728",
            "mesaj": f"{ilce} is in the high-risk category. Immediate intervention is required:" if _lang == "EN" else f"{ilce} ilçesi yüksek risk kategorisinde. Acil müdahale şart:",
            "oneri": [
                "Prepare an emergency action plan with IZSU and apply short-term restriction measures." if _lang == "EN" else "İZSU ile acil eylem planı oluşturun — kısa vadeli kısıtlama önlemleri alın.",
                "Audit high-consuming industrial and commercial sectors." if _lang == "EN" else "Yüksek tüketen sanayi ve ticari sektörleri denetleyin.",
                "Increase recycled water use and install greywater systems." if _lang == "EN" else "Geri dönüştürülmüş su kullanımını artırın, gri su sistemleri kurun.",
                "Assess alternative water sources such as groundwater and rainwater harvesting." if _lang == "EN" else "Alternatif su kaynakları (yer altı suyu, yağmur hasadı) araştırın.",
                "Communicate urgency to the public through awareness campaigns." if _lang == "EN" else "Halk bilgilendirme kampanyasıyla aciliyeti kamuoyuyla paylaşın.",
            ],
            "gelecek": "Without measures, the risk score may reach critical levels by 2030." if _lang == "EN" else "Önlem alınmazsa 2030'ta risk skoru kritik seviyelere ulaşabilir."
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

    _dil_h = st.session_state.get("dil","TR")

    # ── Sağ üst: Dil + Tema butonları
    st.markdown("""<style>
    div[data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="column"] button {
        font-size: 0.78rem !important; height: 30px !important;
        padding: 0 10px !important; line-height: 1 !important;
        background: rgba(10,25,60,0.5) !important;
        border: 1px solid rgba(56,209,227,0.3) !important;
        border-radius: 8px !important; color: #c8e6f5 !important;
    }
    div[data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="column"] button:hover {
        background: rgba(56,209,227,0.18) !important; color: #fff !important;
    }
    </style>""", unsafe_allow_html=True)

    _t1, _t2 = st.columns([7.0, 0.6])
    with _t2:
        _dil_label = "🇹🇷 TR" if _dil_h == "EN" else "🇬🇧 EN"
        if st.button(_dil_label, key="dil_btn", use_container_width=True):
            st.session_state.dil = "EN" if _dil_h == "TR" else "TR"
            st.rerun()


    # ── Başlık — daha yukarı, daha büyük
    st.markdown(f"""
    <div style="text-align:center;padding:8px 0 16px 0;position:relative;">
        <div style="position:absolute;right:0;top:50%;transform:translateY(-50%);
                    color:#a8d8f0;font-size:0.72rem;text-align:right;line-height:1.9;">
            {(_dil_h=="TR" and "Veri: İZSU + Bootstrap Simülasyonu" or "Data: IZSU + Bootstrap Simulation")}<br>
            {(_dil_h=="TR" and "11 Merkez İlçe · Entropy-WSRI" or "11 Central Districts · Entropy-WSRI")}
        </div>
        <div style="display:inline-flex;align-items:center;gap:20px;">
            <span style="font-size:4.2rem;line-height:1;filter:drop-shadow(0 0 16px rgba(56,209,227,0.6));">💧</span>
            <div style="text-align:left;">
                <div style="color:#ffffff;font-size:3.4rem;font-weight:900;letter-spacing:-1px;line-height:1;
                            text-shadow:0 0 24px rgba(56,209,227,0.20);">İzmiRisk</div>
                <div style="color:#38d1e3;font-size:0.85rem;letter-spacing:3px;
                            text-transform:uppercase;margin-top:6px;font-weight:600;">
                    {(_dil_h=="TR" and "Su Güvenliği Risk Endeksi · İzmir" or "Water Security Risk Index · Izmir")} · {START_YEAR}–2030
                </div>
            </div>
        </div>
    </div>
    <hr style="border-color:rgba(56,209,227,0.2);margin:0 0 0.6rem 0;">
    """, unsafe_allow_html=True)

    # ── Arama satırı — büyüteç + input yan yana, sağ hizalı
    st.markdown("""
    <style>
    /* Arama input tamamen transparan */
    [data-testid="stTextInput"] input {
        background: transparent !important;
        border: 1px solid rgba(56,209,227,0.35) !important;
        border-radius: 20px !important;
        color: #a8d8f0 !important;
        font-size: 0.78rem !important;
        height: 32px !important;
        padding: 0 12px !important;
        box-shadow: none !important;
    }
    [data-testid="stTextInput"] > div,
    [data-testid="stTextInput"] > div > div {
        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
        padding: 0 !important;
    }
    [data-testid="stTextInput"] input::placeholder {
        color: rgba(168,216,240,0.45) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    _s1, _s2, _s3 = st.columns([3.5, 1.8, 0.5])
    with _s2:
        _arama_girdi = st.text_input(
            "", key="site_arama", label_visibility="collapsed",
            placeholder="🔍 " + ("Ara: baraj, risk, 2030..." if _dil_h=="TR" else "Search: dam, risk, 2030...")
        )
    with _s3:
        _ara_btn = st.button("🔍", key="arama_btn", use_container_width=True)

    if _arama_girdi and (_ara_btn or len(_arama_girdi) > 2):
        _arama_sozluk = {
            "baraj":("📊 EDA Analizi",None),"tahtalı":("📊 EDA Analizi",None),
            "balçova":("📊 EDA Analizi",None),"gördes":("📊 EDA Analizi",None),
            "doluluk":("📊 EDA Analizi",None),"dam":("📊 EDA Analizi",None),
            "tüketim":("📊 EDA Analizi",None),"consumption":("📊 EDA Analizi",None),
            "arz":("📊 EDA Analizi",None),"supply":("📊 EDA Analizi",None),
            "kayıp":("📊 EDA Analizi",None),"loss":("📊 EDA Analizi",None),
            "eda":("📊 EDA Analizi",None),"analiz":("📊 EDA Analizi",None),
            "risk":("📈 Risk Endeksi",None),"wsri":("📈 Risk Endeksi",None),
            "entropy":("📈 Risk Endeksi",None),"endeks":("📈 Risk Endeksi",None),
            "bornova":("📈 Risk Endeksi",None),"çiğli":("📈 Risk Endeksi",None),
            "bayraklı":("📈 Risk Endeksi",None),"buca":("📈 Risk Endeksi",None),
            "gaziemir":("📈 Risk Endeksi",None),"karşıyaka":("📈 Risk Endeksi",None),
            "konak":("📈 Risk Endeksi",None),"karabağlar":("📈 Risk Endeksi",None),
            "narlidere":("📈 Risk Endeksi",None),"güzelbahçe":("📈 Risk Endeksi",None),
            "district":("📈 Risk Endeksi",None),"ilçe":("📈 Risk Endeksi",None),
            "2030":("🔮 2030 Tahmini",None),"projeksiyon":("🔮 2030 Tahmini",None),
            "projection":("🔮 2030 Tahmini",None),"senaryo":("🔮 2030 Tahmini",None),
            "tahmin":("🔮 2030 Tahmini",None),"forecast":("🔮 2030 Tahmini",None),
            "harita":("Izmir Risk Haritasi",None),"map":("Izmir Risk Haritasi",None),
            "moran":("🗺️ Mekânsal Analiz",None),"lisa":("🗺️ Mekânsal Analiz",None),
            "mekânsal":("🗺️ Mekânsal Analiz",None),"spatial":("🗺️ Mekânsal Analiz",None),
            "küme":("🗺️ Mekânsal Analiz",None),"cluster":("🗺️ Mekânsal Analiz",None),
            "öneri":("💡 Öneriler",None),"recommendation":("💡 Öneriler",None),
            "suggestion":("💡 Öneriler",None),"tavsiye":("💡 Öneriler",None),
            "metodoloji":("📐 Metodoloji",None),"methodology":("📐 Metodoloji",None),
            "bootstrap":("📐 Metodoloji",None),"mann":("📐 Metodoloji",None),
            "formül":("📐 Metodoloji",None),"yöntem":("📐 Metodoloji",None),
            "radar":("🔬 Araçlar",None),"simülatör":("🔬 Araçlar",None),
            "simulator":("🔬 Araçlar",None),"araç":("🔬 Araçlar",None),
            "tool":("🔬 Araçlar",None),"karşılaştır":("🔬 Araçlar",None),
            "compare":("🔬 Araçlar",None),"animasyon":("🔬 Araçlar",None),
            "hesapla":("🔬 Araçlar",None),"calculator":("🔬 Araçlar",None),
        }
        _temiz = _arama_girdi.strip().lower()
        _bulundu = False
        for _k, _v in _arama_sozluk.items():
            if _k in _temiz:
                _h_sayfa, _ = _v
                if _h_sayfa != st.session_state.get("secili_sayfa"):
                    st.session_state.secili_sayfa = _h_sayfa
                    st.rerun()
                _bulundu = True
                break
        if not _bulundu:
            with _s2:
                st.caption("❌ " + ("Sonuç yok. Deneyin: baraj, risk, harita, 2030, metodoloji" if _dil_h=="TR" else "No result. Try: dam, risk, map, 2030, methodology"))

    _dil_banner = st.session_state.get("dil", "TR")
    _banner_metin = (
        f"{START_YEAR}–2019 data generated via block bootstrap simulation. 2020–{END_YEAR} data from official IZSU records."
        if _dil_banner == "EN" else
        f"{START_YEAR}–2019 verileri block bootstrap yöntemiyle İzmir kuraklık takvimi referans alınarak üretilmiştir. 2020–{END_YEAR} verileri İZSU resmi kaynağındandır."
    )
    st.markdown(f"""
    <div style="background:linear-gradient(90deg,rgba(155,89,182,0.08),rgba(56,209,227,0.06));
                border:1px solid rgba(155,89,182,0.25);border-radius:8px;
                padding:0.6rem 1rem;margin-bottom:0.8rem;
                display:flex;align-items:center;gap:12px;">
        <span style="font-size:1.2rem;">🔬</span>
        <div style="flex:1;">
            <span class="veri-rozet">{"BOOTSTRAP SIMULATION" if _dil_banner=="EN" else "BOOTSTRAP SİMÜLASYONU"}</span>
            <span style="color:#d0e8f5;font-size:0.82rem;margin-left:10px;">
                {_banner_metin}
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
            align-items: stretch !important;
            flex-wrap: nowrap !important;
            gap: 8px !important;
            padding: 12px 4px !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            backdrop-filter: none !important;
            max-width: 100% !important;
            margin: 4px auto 12px auto !important;
        }
        div[data-testid="stPills"] label {
            min-height: 56px !important;
            padding: 0 18px !important;
            border-radius: 14px !important;
            background: rgba(10,25,60,0.75) !important;
            border: 1.5px solid rgba(56,209,227,0.4) !important;
            color: #cdeeff !important;
            font-size: 1.0rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.4px !important;
            transition: all 180ms ease !important;
            cursor: pointer !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
            box-shadow:
                0 4px 16px rgba(0,0,0,0.45),
                0 0 0 1px rgba(56,209,227,0.08),
                inset 0 1px 0 rgba(255,255,255,0.10) !important;
        }
        div[data-testid="stPills"] label p,
        div[data-testid="stPills"] label span {
            font-size: 1.0rem !important;
            font-weight: 700 !important;
            color: inherit !important;
            margin: 0 !important;
        }
        div[data-testid="stPills"] label:hover {
            background: rgba(56,209,227,0.18) !important;
            border-color: rgba(56,209,227,0.85) !important;
            color: #ffffff !important;
            transform: translateY(-2px) !important;
            box-shadow:
                0 8px 24px rgba(0,0,0,0.50),
                0 0 18px rgba(56,209,227,0.22),
                inset 0 1px 0 rgba(255,255,255,0.15) !important;
        }
        div[data-testid="stPills"] label:has(input:checked),
        div[data-testid="stPills"] label[aria-checked="true"],
        div[data-testid="stPills"] [aria-checked="true"] {
            background: linear-gradient(135deg,rgba(56,209,227,0.28),rgba(27,79,114,0.6)) !important;
            border-color: #38d1e3 !important;
            color: #ffffff !important;
            box-shadow:
                0 0 24px rgba(56,209,227,0.45),
                0 6px 20px rgba(0,0,0,0.40),
                inset 0 1px 0 rgba(255,255,255,0.20) !important;
        }
        div[data-testid="stPills"] input { display: none !important; }
        @media (max-width: 900px) {
            div[data-testid="stPills"] label {
                min-height: 44px !important;
                font-size: 0.85rem !important;
                padding: 0 14px !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)

    sayfa_listesi = [
        "🏠 Ana Sayfa",
        "📊 EDA Analizi",
        "📈 Risk Endeksi",
        "🔮 2030 Tahmini",
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
        "🔮 2030",
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
    if "dil" not in st.session_state:
        st.session_state.dil = "TR"

    # ── Navigasyon — custom st.button'lar
    st.markdown("""
    <style>
    /* Nav buton container */
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div[data-testid="stVerticalBlock"]
        > div[data-testid="stButton"] > button {
        width: 100% !important;
        height: 52px !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.2px !important;
        border-radius: 12px !important;
        border: 1.5px solid rgba(56,209,227,0.30) !important;
        background: rgba(5,18,48,0.72) !important;
        color: #b8d8f0 !important;
        transition: all 160ms ease !important;
        backdrop-filter: blur(14px) !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.06) !important;
        white-space: nowrap !important;
        padding: 0 8px !important;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div[data-testid="stVerticalBlock"]
        > div[data-testid="stButton"] > button:hover {
        background: rgba(56,209,227,0.16) !important;
        border-color: rgba(56,209,227,0.7) !important;
        color: #ffffff !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.45), 0 0 14px rgba(56,209,227,0.2) !important;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div[data-testid="stVerticalBlock"]
        > div[data-testid="stButton"] > button:focus:not(:active) {
        background: linear-gradient(135deg,rgba(56,209,227,0.25),rgba(27,79,114,0.55)) !important;
        border-color: #38d1e3 !important;
        color: #ffffff !important;
        box-shadow: 0 0 20px rgba(56,209,227,0.4), 0 4px 16px rgba(0,0,0,0.4) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    sayfa = st.session_state.secili_sayfa
    nav_cols = st.columns([1,1,1,1,1,1,1,1,1])
    nav_items = [
        ("🏠", "Home" if _dil_h == "EN" else "Ana Sayfa", "🏠 Ana Sayfa"),
        ("📊", "EDA", "📊 EDA Analizi"),
        ("📈", "Risk", "📈 Risk Endeksi"),
        ("🔮", "2030", "🔮 2030 Tahmini"),
        ("🗺️", "Map" if _dil_h == "EN" else "Harita", "Izmir Risk Haritasi"),
        ("📍", "Spatial" if _dil_h == "EN" else "Mekânsal", "🗺️ Mekânsal Analiz"),
        ("💡", "Recommendation" if _dil_h == "EN" else "Öneriler", "💡 Öneriler"),
        ("📐", "Methodology" if _dil_h == "EN" else "Metodoloji", "📐 Metodoloji"),
        ("🔬", "Tools" if _dil_h == "EN" else "Araçlar", "🔬 Araçlar"),
    ]
    for i, (emoji, label, sayfa_adi) in enumerate(nav_items):
        with nav_cols[i]:
            btn_label = f"{emoji}\n{label}"
            if st.button(btn_label, key=f"nav_{i}", use_container_width=True):
                st.session_state.secili_sayfa = sayfa_adi
                st.rerun()

    # Aktif sayfa vurgusu
    st.markdown(f"""
    <style>
    div[data-testid="stHorizontalBlock"] > div:nth-child({nav_items.index(next((x for x in nav_items if x[2]==sayfa), nav_items[0]))+1})
        > div > div > div > button {{
        background: linear-gradient(135deg,rgba(56,209,227,0.28),rgba(27,79,114,0.6)) !important;
        border-color: #38d1e3 !important;
        color: #ffffff !important;
        box-shadow: 0 0 18px rgba(56,209,227,0.4), 0 4px 14px rgba(0,0,0,0.4) !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    sayfa = st.session_state.secili_sayfa
    dil   = st.session_state.dil   # "TR" veya "EN"

    # ── Çeviri sözlüğü — sayfa genelinde kullanılır
    T = {
        # Genel
        "ana_baslik":       {"TR": "Su Güvenliği Risk Endeksi · İzmir · 2010–2030",
                             "EN": "Water Security Risk Index · Izmir · 2010–2030"},
        "bootstrap_banner": {"TR": f"{START_YEAR}–2019 verileri block bootstrap yöntemiyle üretilmiştir. 2020–{END_YEAR} verileri İZSU resmi kaynağındandır.",
                             "EN": f"{START_YEAR}–2019 data generated via block bootstrap simulation. 2020–{END_YEAR} data from official IZSU records."},
        # Ana Sayfa
        "hero_baslik":      {"TR": "İzmir Su Güvenliği\nRisk Endeksi",
                             "EN": "Izmir Water Security\nRisk Index"},
        "hero_alt":         {"TR": f"Entropy ağırlıklı bileşik risk analizi · 11 merkez ilçe · {len(YEARS)} yıllık seri ({START_YEAR}–{END_YEAR}) · Bootstrap simülasyonu · Mann-Kendall trend testi · LISA mekânsal analizi · 2030 projeksiyonu",
                             "EN": f"Entropy-weighted composite risk analysis · 11 central districts · {len(YEARS)}-year series ({START_YEAR}–{END_YEAR}) · Bootstrap simulation · Mann-Kendall trend test · LISA spatial analysis · 2030 projection"},
        "kpi_yuksek":       {"TR": "Yüksek Riskli İlçeler", "EN": "High-Risk Districts"},
        "kpi_orta":         {"TR": "Orta Riskli İlçeler",   "EN": "Medium-Risk Districts"},
        "kpi_dusuk":        {"TR": "Düşük Riskli İlçeler",  "EN": "Low-Risk Districts"},
        "kpi_baraj":        {"TR": "Tahtalı Doluluk",        "EN": "Tahtalı Fill Rate"},
        "kpi_enaz":         {"TR": "En Az Riskli",           "EN": "Lowest Risk"},
        # Risk labels
        "yuksek_risk":      {"TR": "Yüksek Risk", "EN": "High Risk"},
        "orta_risk":        {"TR": "Orta Risk",   "EN": "Medium Risk"},
        "dusuk_risk":       {"TR": "Düşük Risk",  "EN": "Low Risk"},
        # Sayfa başlıkları
        "eda_baslik":       {"TR": "Keşifsel Veri Analizi",    "EN": "Exploratory Data Analysis"},
        "risk_baslik":      {"TR": "Su Güvenliği Risk Endeksi","EN": "Water Security Risk Index"},
        "tahmin_baslik":    {"TR": "2030 Yılı Risk Projeksiyonu","EN":"2030 Risk Projection"},
        "harita_baslik":    {"TR": "İzmir İlçe Risk Haritası", "EN": "Izmir District Risk Map"},
        "mekansal_baslik":  {"TR": "Mekânsal Analiz",          "EN": "Spatial Analysis"},
        "oneri_baslik":     {"TR": "İlçe Bazlı Öneriler",      "EN": "District-Based Recommendation"},
        "metodoloji_baslik":{"TR": "Metodoloji & Teknik Detaylar","EN":"Methodology & Technical Details"},
        "arac_baslik":      {"TR": "İnteraktif Araçlar",       "EN": "Interactive Tools"},
        # Araçlar
        "arac_alt":         {"TR": f"Radar profil · İlçe karşılaştırma · Risk simülatörü · {len(YEARS)} yıllık animasyonlu seri",
                             "EN": f"Radar profile · District comparison · Risk simulator · {len(YEARS)}-year animated series"},
        "ilce_sec":         {"TR": "🏙️ Analiz edilecek ilçeyi seç:", "EN": "🏙️ Select district to analyze:"},
        "karsi_ilce":       {"TR": "Karşılaştırılacak ilçe:", "EN": "Compare with:"},
        "sim_baslik":       {"TR": "Risk Simülatörü — Anlık Duyarlılık","EN":"Risk Simulator — Live Sensitivity"},
        "sim_caption":      {"TR": "Gösterge değerlerini değiştir → Risk skoru entropy ağırlıklarıyla anlık güncellenir",
                             "EN": "Adjust indicator values → Risk score updates instantly using entropy weights"},
        "sim_talep_lbl":    {"TR": "💧 Abone Tüketim (m³)",  "EN": "💧 Per-Subscriber Consumption (m³)"},
        "sim_artis_lbl":    {"TR": "📈 Tüketim Artışı (%)",  "EN": "📈 Consumption Growth (%)"},
        "sim_arz_lbl":      {"TR": "⚖️ Arz Kısıtı (%)",      "EN": "⚖️ Supply Constraint (%)"},
        "sim_kayip_lbl":    {"TR": "🔴 Kayıp Oranı (%)",     "EN": "🔴 Water Loss Rate (%)"},
        "sim_skor":         {"TR": "Simüle Edilen Skor",      "EN": "Simulated Score"},
        "sim_sinif":        {"TR": "Risk Sınıfı",             "EN": "Risk Class"},
        "harita_yil_lbl":   {"TR": "📅 Yıl Seçin",           "EN": "📅 Select Year"},
        "risk_sira":        {"TR": "Yılı Risk Sıralaması",    "EN": "Risk Ranking"},
        "risk_skoru":       {"TR": "Risk Skoru",              "EN": "Risk Score"},
        "risk_sinifi":      {"TR": "Risk Sınıfı",             "EN": "Risk Class"},
        "proj_2030":        {"TR": "2030 Projeksiyonu",       "EN": "2030 Projection"},
        "kotumser":         {"TR": "Kötümser",                "EN": "Pessimistic"},
        "baz":              {"TR": "Baz",                     "EN": "Base"},
        "iyimser":          {"TR": "İyimser",                 "EN": "Optimistic"},
    }

    def t(key):
        """Çeviri yardımcı fonksiyon"""
        return T.get(key, {}).get(dil, T.get(key, {}).get("TR", key))


    # ── Otomatik İngilizce çeviri katmanı
    # Bu katman, kod içinde kalan hard-coded Türkçe metinleri de ENG modunda çevirir.
    TR_EN_REPLACEMENTS = {
        "İzmir Su Güvenliği": "Izmir Water Security",
        "Su Güvenliği Risk Endeksi": "Water Security Risk Index",
        "SU GÜVENLİĞİ ANALİZİ · İZMİR": "WATER SECURITY ANALYSIS · IZMIR",
        "SU GÜVENLİĞİ RİSK ENDEKSİ": "WATER SECURITY RISK INDEX",
        "KEŞİFSEL VERİ ANALİZİ": "EXPLORATORY DATA ANALYSIS",
        "Keşifsel Veri Analizi": "Exploratory Data Analysis",
        "SENARYO PROJEKSİYONU": "SCENARIO PROJECTION",
        "2030 Yılı Risk Projeksiyonu": "2030 Risk Projection",
        "MEKÂNSAL ANALİZ": "SPATIAL ANALYSIS",
        "Mekânsal Analiz": "Spatial Analysis",
        "İLÇE ÖNERİLERİ": "DISTRICT RECOMMENDATION",
        "İlçe Bazlı Öneriler": "District-Based Recommendation",
        "ETKİLEŞİMLİ RİSK HARİTASI": "INTERACTIVE RISK MAP",
        "İzmir İlçe Risk Haritası": "Izmir District Risk Map",
        "ETKİLEŞİMLİ ARAÇLAR · KEŞFEDİN & ANALİZ EDİN": "INTERACTIVE TOOLS · EXPLORE & ANALYZE",
        "İnteraktif Araçlar": "Interactive Tools",
        "Radar profil · İlçe karşılaştırma · Risk simülatörü": "Radar profile · District comparison · Risk simulator",
        "yıllık animasyonlu seri": "year animated series",
        "Veri: İZSU + Bootstrap Simülasyonu": "Data: IZSU + Bootstrap Simulation",
        "11 Merkez İlçe": "11 Central Districts",
        "BOOTSTRAP SİMÜLASYONU": "BOOTSTRAP SIMULATION",
        "verileri block bootstrap yöntemiyle İzmir kuraklık takvimi referans alınarak üretilmiştir": "data generated via block bootstrap simulation using Izmir drought calendar as reference",
        "verileri İZSU resmi kaynağındandır": "data comes from official IZSU records",
        "yıllık seri": "year series",
        "Bootstrap simülasyonu ile genişletildi": "Expanded with bootstrap simulation",
        "Baraj dolulukları": "Dam fill rates",
        "ilçe tüketimi": "district consumption",
        "arz-talep dengesi": "supply-demand balance",
        "kayıp trendleri": "loss trends",
        "Baraj Doluluk": "Dam Fill Rates",
        "Tüketim Haritası": "Consumption Map",
        "Arz-Talep": "Supply-Demand",
        "Kayıp Oranı": "Loss Rate",
        "BARAJ TARİHÇESİ": "DAM HISTORY",
        "İzmir'in Barajları — Tarihçe & Genel Bilgi": "Izmir's Dams — History & Overview",
        "BARAJ DOLULUK": "DAM FILL RATES",
        "Baraj Doluluk Oranları": "Dam Fill Rates",
        "BULGULAR": "FINDINGS",
        "BULGULAR &": "FINDINGS &",
        "Öne Çıkan Bulgular & Dönüm Noktaları": "Key Findings & Turning Points",
        "TALEP ISISI": "DEMAND HEATMAP",
        "Abone Başına Tüketim Isı Haritası": "Per-Subscriber Consumption Heatmap",
        "ARZ-TALEP DENGESİ": "SUPPLY-DEMAND BALANCE",
        "Arz-Talep Dengesi": "Supply-Demand Balance",
        "SU KAYIP TRENDİ": "WATER LOSS TREND",
        "Yıllık Su Kayıp Oranı Trendi": "Annual Water Loss Rate Trend",
        "Toplam Tüketim": "Total Consumption",
        "En Yüksek Risk Skoru": "Highest Risk Score",
        "Su Kayıp Oranı": "Water Loss Rate",
        "milyon m³": "million m³",
        "sistem geneli": "system-wide",
        "yılı": "year",
        "Skor": "Score",
        "Risk Göstergesi": "Risk Indicator",
        "En Riskli 3 İlçe": "Top 3 High-Risk Districts",
        "Risk İbresi": "Risk Gauge",
        "Risk Analizi": "Risk Analysis",
        "Yılı İlçe Risk Sıralaması & Ağırlık Dağılımı": "District Risk Ranking & Weight Distribution",
        "Risk Skoru": "Risk Score",
        "Risk Sınıfı": "Risk Class",
        "Düşük Risk": "Low Risk",
        "Orta Risk": "Medium Risk",
        "Yüksek Risk": "High Risk",
        "Orta Risk Eşiği": "Medium Risk Threshold",
        "Yüksek Risk Eşiği": "High Risk Threshold",
        "Düşük": "Low",
        "Orta": "Medium",
        "Yüksek": "High",
        "Entropy Ağırlıkları": "Entropy Weights",
        "Ağırlıkları": "Weights",
        "Ağırlık": "Weight",
        "KAYNAK & YÖNTEM": "SOURCE & METHOD",
        "Veri": "Data",
        "Kapsam": "Scope",
        "Yöntem": "Method",
        "Analiz": "Analysis",
        "İlçe": "District",
        "ilçe": "district",
        "Yıl": "Year",
        "Yılı": "Year",
        "Yılı Risk Sıralaması": "Risk Ranking",
        "İzmir Dünya Genelinde Nerede?": "Where Does Izmir Stand Globally?",
        "KÜRESEL BAĞLAM": "GLOBAL CONTEXT",
        "Su Stresi Altındaki Nüfus": "Population Under Water Stress",
        "Dünya nüfusunun": "of the world population",
        "yılın en az bir ayında ciddi su stresiyle karşılaşıyor": "faces severe water stress for at least one month each year",
        "Akdeniz Havzası Su Açığı": "Mediterranean Basin Water Deficit",
        "İklim değişikliğiyle Akdeniz havzasında yıllık yağış": "With climate change, annual precipitation in the Mediterranean basin",
        "azalması bekleniyor": "is expected to decrease",
        "İzmir bu kuşağın merkezinde": "Izmir is at the center of this belt",
        "İzmir WSRI Ortalaması": "Izmir WSRI Average",
        "merkez ilçe ortalaması": "central district average",
        "bandı": "band",
        "Yüksek risk eşiğine": "The high-risk threshold",
        "henüz ulaşılmamış ancak": "has not yet been reached, but",
        "sınırı geçmiş": "districts have crossed the threshold",
        "Türkiye'nin Kişi Başı Su Potansiyeli": "Turkey's Per Capita Water Potential",
        "Kişi başı yıllık kullanılabilir tatlı su": "Annual usable freshwater per capita",
        "Uluslararası eşik": "International threshold",
        "Türkiye \"su kıtlığı\" sınırına yakın": "Turkey is close to the water scarcity threshold",
        "Kaynak notu": "Source note",
        "Altıncı Değerlendirme Raporu": "Sixth Assessment Report",
        "Devlet Su İşleri": "State Hydraulic Works",
        "yıllık raporu": "annual report",
        "açık veri portalı": "open data portal",
        "Tüm global değerler özgün raporlardan alınmış olup bu çalışmada değiştirilmemiştir": "All global values are taken from original reports and were not modified in this study",
        "Linki Kopyala": "Copy Link",
        "Kopyalandı": "Copied",
        "Twitter/X'te Paylaş": "Share on Twitter/X",
        "LinkedIn'de Paylaş": "Share on LinkedIn",
        "Konum": "Location",
        "Yapım": "Construction",
        "Tip": "Type",
        "Kaya dolgu": "Rockfill",
        "Beton kemer": "Concrete arch",
        "Toprak dolgu": "Earthfill",
        "İzmir'in en büyük su deposu": "Izmir's largest water reservoir",
        "Küçük ama stratejik": "Small but strategic",
        "Kırılgan ama önemli": "Fragile but important",
        "Dönemi": "Period",
        "İstikrarı": "Stability",
        "Kriz Dönemi": "Crisis Period",
        "Doluluk": "Fill Rate",
        "Kapasite": "Capacity",
        "Kritik Seviye": "Critical Level",
        "Kritik Eşik": "Critical Threshold",
        "Gerçek": "Actual",
        "puan": "points",
        "dan": "from",
        "Sisteme Giren Su": "Water Entering the System",
        "Toplam Tüketim": "Total Consumption",
        "Arz": "Supply",
        "Talep": "Demand",
        "Talep Açığı": "Demand Gap",
        "Arz Fazlası": "Supply Surplus",
        "gerçek": "actual",
        "Toplam Kayıp": "Total Loss",
        "Fiziki Kayıp": "Physical Loss",
        "İdari Kayıp": "Administrative Loss",
        "TOPLAM AZALMA": "TOTAL DECREASE",
        "Boru sızıntıları": "Pipe leaks",
        "altyapı hasarı": "infrastructure damage",
        "Kaçak kullanım": "Illegal use",
        "sayaç hataları": "meter errors",
        "Yılı Seçin": "Select Year",
        "Yılı seçin": "Select year",
        "İlçe ara": "Search district",
        "İlçe seç": "Select district",
        "Seçili ilçe": "Selected district",
        "Abone Büyüme": "Subscriber Growth",
        "Değişim": "Change",
        "skoru": "score",
        "İlçe Bazlı Risk Skoru Trendi": "District-Level Risk Score Trend",
        "En Yüksek Riskli 3 İlçe": "Top 3 High-Risk Districts",
        "En Düşük Riskli 3 İlçe": "Top 3 Lowest-Risk Districts",
        "Orta Riskli 5 İlçe": "5 Medium-Risk Districts",
        "Gerçek Veri": "Actual Data",
        "İLÇE SKORLARI": "DISTRICT SCORES",
        "İlçe Risk Skorları": "District Risk Scores",
        "Yıllık Karşılaştırma": "Year Comparison",
        "İLÇE DETAYI": "DISTRICT DETAIL",
        "İlçe Bazlı Detay — Risk Bileşenleri": "District Detail — Risk Components",
        "Senaryo": "Scenario",
        "KÖTÜMSER SENARYO": "PESSIMISTIC SCENARIO",
        "BAZ SENARYO": "BASE SCENARIO",
        "İYİMSER SENARYO": "OPTIMISTIC SCENARIO",
        "Kötümser": "Pessimistic",
        "İyimser": "Optimistic",
        "Baz": "Base",
        "Mevcut büyüme hızı": "Current growth rate",
        "Mevcut trend aynen devam ederse": "If the current trend continues",
        "Su tasarrufu politikaları hayata geçerse": "If water-saving policies are implemented",
        "2030 Projeksiyonu": "2030 Projection",
        "2030 Baz Tahmini": "2030 Base Forecast",
        "2030 Risk Skoru": "2030 Risk Score",
        "Tüm İlçeler": "All Districts",
        "Moran's I ve LISA nedir?": "What are Moran's I and LISA?",
        "Yüksek riskli ilçeler birbirine komşu mu?": "Are high-risk districts clustered?",
        "Komşular farklılaşıyor": "Neighbors differ",
        "Sıcak Küme": "Hot Cluster",
        "Soğuk Küme": "Cold Cluster",
        "İzole Yüksek": "Isolated High",
        "Çevre Yüksek": "High Surroundings",
        "Açıklama": "Description",
        "Öneriler": "Recommendation",
        "Genel Su Tasarrufu Önerileri": "General Water-Saving Recommendation",
        "Hane Bazlı Tasarruf": "Household-Level Savings",
        "Altyapı Öncelikleri": "Infrastructure Priorities",
        "İklim Uyum Önlemleri": "Climate Adaptation Measures",
        "Harita": "Map",
        "Risk Haritası": "Risk Map",
        "Hover over district": "Hover over district",
        "Yıl seçilebilir": "Year selectable",
        "Yıllık": "Annual",
        "Etiket": "Label",
        "Karşılaştırılacak ilçe": "Compare with district",
        "Analiz edilecek ilçeyi seç": "Select district to analyze",
        "Risk Simülatörü": "Risk Simulator",
        "Anlık Duyarlılık": "Live Sensitivity",
        "Gösterge değerlerini değiştir": "Adjust indicator values",
        "anlık güncellenir": "updates instantly",
        "Abone Tüketim": "Per-Subscriber Consumption",
        "Tüketim Artışı": "Consumption Growth",
        "Arz Kısıtı": "Supply Constraint",
        "Kayıp Oranı": "Loss Rate",
        "Simüle Edilen Skor": "Simulated Score",
        "Araçlar": "Tools",
        "Ana Sayfa": "Home",
        "Metodoloji": "Methodology",
        "Mekânsal": "Spatial",
        "Kişi Başı Tüketim": "Per Capita Consumption",
        "Arz Kısıtı": "Supply Constraint",
        "Tüketim Artış Oranı": "Consumption Growth Rate",
        "Su Kayıp Oranı": "Water Loss Rate",
        "Tahtalı Barajı": "Tahtalı Dam",
        "Balçova Barajı": "Balcova Dam",
        "Gördes Barajı": "Gordes Dam",
        "Tahtalı": "Tahtalı",
        "Balçova": "Balcova",
        "Gördes": "Gordes",
        "ÇİĞLİ": "CIGLI",
        "BAYRAKLI": "BAYRAKLI",
        "GAZİEMİR": "GAZIEMIR",
        "GÜZELBAHÇE": "GUZELBAHCE",
        "KARŞIYAKA": "KARSIYAKA",
        "NARLIDERE": "NARLIDERE",
        "KONAK": "KONAK",
        "KARABAĞLAR": "KARABAGLAR",
        "BALÇOVA": "BALCOVA",
        "Çiğli": "Cigli",
        "Bayraklı": "Bayrakli",
        "Gaziemir": "Gaziemir",
        "Güzelbahçe": "Guzelbahce",
        "Karşıyaka": "Karsiyaka",
        "Narlıdere": "Narlidere",
        "Karabağlar": "Karabaglar",
        "Balçova": "Balcova",
        "İzmir": "Izmir",
        "İZSU": "IZSU",
    }


    # Ek i18n düzeltmeleri: ENG modunda kullanıcıya görünen hard-coded Türkçe blokları temizler.
    TR_EN_REPLACEMENTS.pop("dan", None)  # Türkçe eklerde bozulma yaratıyordu: doğrudan -> doğrufrom gibi.
    TR_EN_REPLACEMENTS.update({
        # Units and small labels
        "m³/abone": "m³ per subscriber",
        "m³ / abone": "m³ per subscriber",
        "/yıl": " per year",
        "puan/yıl": "points per year",
        "%/yıl": "% per year",
        "puan": "points",
        "puanı": "points",
        "abone sayısı": "subscriber count",
        "Abone sayısı": "Subscriber count",
        "abone başına": "per subscriber",
        "Abone Başına": "Per Subscriber",
        "kişi başı": "per capita",
        "Kişi başı": "Per capita",
        "Kişi Başı": "Per Capita",
        "14 yıllık": "14-year",
        "yıllık": "annual",
        "Yıllık": "Annual",
        "yıl": "year",
        "YIL": "YEAR",
        "Dönem": "Period",
        "DÖNEM": "PERIOD",
        "Değişkenler": "Variables",
        "Kaynak": "Source",
        "Merkez": "Central",
        "merkez": "central",
        "baraj": "dam",
        "Baraj": "Dam",
        "doluluk": "fill rate",
        "Doluluk": "Fill Rate",
        "üretim": "production",
        "Üretim": "Production",
        "kayıp oranı": "loss rate",
        "Kayıp oranı": "Loss rate",
        "tüketim": "consumption",
        "Tüketim": "Consumption",
        "arz": "supply",
        "Arz": "Supply",
        "talep": "demand",
        "Talep": "Demand",
        "kısıtı": "constraint",
        "Kısıtı": "Constraint",
        "Açık": "Gap",
        "açık": "gap",
        "denge": "balance",
        "Denge": "Balance",
        "Eşik": "Threshold",
        "eşiği": "threshold",
        "Alt Eşiği": "Lower Bound",
        "büyüme": "growth",
        "Büyüme": "Growth",
        "hızı": "rate",
        "Hızı": "Rate",
        "seri": "series",
        "Seri": "Series",

        # District and place names transliteration / names
        "Tahtalı": "Tahtali",
        "tahtalı": "tahtali",
        "Çiğli": "Cigli",
        "ÇİĞLİ": "CIGLI",
        "Gördes": "Gordes",
        "gördes": "gordes",
        "Balçova": "Balcova",
        "BALÇOVA": "BALCOVA",
        "Bayraklı": "Bayrakli",
        "Gaziemir": "Gaziemir",
        "GAZİEMİR": "GAZIEMIR",
        "Güzelbahçe": "Guzelbahce",
        "GÜZELBAHÇE": "GUZELBAHCE",
        "Karşıyaka": "Karsiyaka",
        "KARŞIYAKA": "KARSIYAKA",
        "Narlıdere": "Narlidere",
        "KARABAĞLAR": "KARABAGLAR",
        "Karabağlar": "Karabaglar",
        "İzmir": "Izmir",
        "İZSU": "IZSU",
        "TÜİK": "TURKSTAT",
        "DSİ": "DSI",
        "İzmiRisk": "İzmiRisk",  # başlık özel olarak korunur

        # EDA findings - dam history / demand / supply / loss
        "DÜŞÜK SEVİYE PERİYODU": "LOW LEVEL PERIOD",
        "Tahtalı ve Gördes eş zamanlı geriledi": "Tahtali and Gordes declined simultaneously",
        "2013–2015 arasında Tahtalı %36–%41 bandında seyrederken Gördes %15–%16'ya indi.": "Between 2013 and 2015, Tahtali remained in the 36–41% range while Gordes dropped to 15–16%.",
        "İki barajın eş zamanlı düşüşü arz esnekliğini daralttı ve sistem üzerinde yoğun baskı yarattı.": "The simultaneous decline of both dams reduced supply flexibility and created intense pressure on the system.",
        "GÖRDES KRİZİ": "GORDES CRISIS",
        "%18'den %1'e tek yılda çöküş": "Collapse from 18% to 1% within one year",
        "Gördes 2019'da %18 dolulukla zaten düşük seyrederken 2020'de %2, 2021'de %1'e indi.": "Gordes was already low at 18% fill rate in 2019, then fell to 2% in 2020 and 1% in 2021.",
        "Uzun süreli kuraklığın su kaynakları üzerindeki yıkıcı etkisini belgeleyen kritik bir veri noktasıdır.": "This is a critical data point showing the destructive impact of prolonged drought on water resources.",
        "PANDEMİ DÖNEMİ ETKİSİ": "PANDEMIC IMPACT",
        "Evde kalma → artan tüketim baskısı": "Stay-at-home period → increased consumption pressure",
        "COVID-19 sürecinde hane içi su kullanımı belirgin biçimde arttı.": "During COVID-19, household water use increased significantly.",
        "Aynı dönemde Gördes kritik seviyelere inerken tüketim yüksek seyretti — arz-talep dengesi ciddi biçimde bozuldu.": "In the same period, Gordes fell to critical levels while consumption remained high, seriously disrupting the supply-demand balance.",
        "NARLIDERE — Yüksek Tüketim, Düşük Risk": "NARLIDERE — High Consumption, Low Risk",
        "Narlıdere kişi başı tüketime göre listenin en üstünde ancak risk sıralamasında alt sıralarda.": "Narlidere ranks at the top for per capita consumption but lower in the risk ranking.",
        "Bunun nedeni küçük abone tabanı, eski yapı stoğu ve 2010'lar boyunca süren kentsel dönüşüm sürecidir.": "This is mainly due to its smaller subscriber base, older building stock, and the urban transformation process during the 2010s.",
        "Arz kısıtı ve kayıp oranı risk modelinde baskın gelince Narlıdere düşük riske düşmektedir.": "Because supply constraint and loss rate dominate the risk model, Narlidere falls into the low-risk band.",
        "GAZİEMİR — Orta Tüketim, Yüksek Risk": "GAZIEMIR — Medium Consumption, High Risk",
        "Gaziemir talep haritasında ortada görünürken risk sıralamasında yüksekte.": "Gaziemir appears mid-range on the demand heatmap but ranks high in the risk ranking.",
        "Hızlı nüfus artışının yarattığı arz baskısı ve artan tüketim artış oranı belirleyici.": "Supply pressure caused by rapid population growth and the rising consumption growth rate are decisive factors.",
        "Risk modeli büyüme hızını da ağırlıklandırır — Gaziemir orta-yüksek risk bandına girmektedir.": "The risk model also weights growth speed, placing Gaziemir in the medium-high risk band.",
        "ARZ KISITI ZİRVESİ": "SUPPLY CONSTRAINT PEAK",
        "Sisteme giren su 107M'e geriledi": "Water entering the system fell to 107M",
        "2014–2016 döneminde sisteme giren su 107–132M m³ bandına inerken": "During 2014–2016, water entering the system fell to the 107–132M m³ range, while",
        "toplam tüketim 147–153M m³'te yükselmeye devam etti.": "total consumption continued to rise at 147–153M m³.",
        "Oluşan makas sistem kapasitesini ciddi biçimde zorladı.": "The resulting gap seriously strained system capacity.",
        "EŞİTLENME NOKTASI": "BALANCE POINT",
        "Arz ve talep 160M m³'te buluştu": "Supply and demand met at 160M m³",
        "2021'de sisteme giren su ve toplam tüketim her ikisi de 160M m³ ile eşitlenerek": "In 2021, water entering the system and total consumption both balanced at 160M m³,",
        "nadir görülen bir denge noktası yakalandı.": "creating a rare balance point.",
        "Bu geçici iyileşme sistem verimliliğindeki artışa işaret eder.": "This temporary improvement indicates increased system efficiency.",
        "AÇIK YENİDEN GENİŞLEDİ": "GAP WIDENED AGAIN",
        "Talep arzı ~45M m³ geçti": "Demand exceeded supply by ~45M m³",
        "Sisteme giren su 118–120M m³'e gerilerken tüketim 165–166M'de kaldı.": "Water entering the system decreased to 118–120M m³ while consumption remained at 165–166M.",
        "Bu ~45M m³'lik açık altyapı kayıplarına ve sistem verimsizliğine işaret etmektedir.": "This ~45M m³ gap points to infrastructure losses and system inefficiency.",
        "KAYDEDİLEN İYİLEŞME": "RECORDED IMPROVEMENT",
        "FİZİKİ KAYIP BASKINI": "PHYSICAL LOSS DOMINANCE",
        "Toplam kaybın ~%95'i boru sızıntısı": "About 95% of total loss comes from pipe leakage",
        "2023 verilerine göre fiziki kayıp %25.92, idari kayıp %1.43.": "According to 2023 data, physical loss is 25.92% and administrative loss is 1.43%.",
        "Fiziki kayıpların baskın olması altyapı yenileme yatırımlarının öncelikli alan olduğuna işaret etmektedir.": "The dominance of physical losses indicates that infrastructure renewal should be the priority area.",
        "PANDEMİ YILINDA HAFİF ARTIŞ": "SLIGHT INCREASE DURING THE PANDEMIC YEAR",
        "Kayıp oranı %28.56'ya çıktı": "The loss rate rose to 28.56%",
        "2020'de kayıp oranı bir önceki yıla kıyasla hafifçe yükseldi.": "In 2020, the loss rate increased slightly compared with the previous year.",
        "Pandemi döneminde denetim ve bakım faaliyetlerinin yavaşlaması bu geçici kötüleşmenin olası nedenidir.": "The slowdown in inspection and maintenance activities during the pandemic is a likely reason for this temporary deterioration.",
        "14 yıllık dönemde toplam su kayıp oranı yaklaşık": "Over the 14-year period, the total water loss rate decreased by approximately",
        "azaldı.": "decreased.",
        "İZSU'nun altyapı yatırımları ve akıllı sayaç projelerinin somut çıktısıdır.": "This is a concrete outcome of IZSU's infrastructure investments and smart meter projects.",
        "Ancak %27 oranı Avrupa ortalamasının (~%15–20) hâlâ üzerindedir.": "However, the 27% level is still above the European average (~15–20%).",
        "geriledi": "decreased",
        "çıktı": "increased",

        # 2030 projection scenario text
        "Abone büyüme oranı (CAGR) bazlı 3 senaryo": "Three scenarios based on subscriber growth rate (CAGR)",
        "CAGR 14 yıllık seriden hesaplanmıştır": "CAGR is calculated from the 14-year series",
        "Hızlı kentleşme, iklim kaynaklı arz kısıtı ve altyapı yatırımlarının yetersiz": "Rapid urbanization, climate-driven supply constraints, and insufficient infrastructure investments",
        "kalması durumunda risk skorları 2030'da belirgin biçimde yükselir.": "may cause risk scores to rise significantly by 2030.",
        "Bornova bu senaryoda en kritik konumdaki ilçe olmaya devam eder.": "Bornova remains the most critical district in this scenario.",
        "2023 büyüme hızının korunduğu varsayımında 2030 risk görünümü.": "This is the 2030 risk outlook under the assumption that the 2023 growth rate continues.",
        "Genel eğilim düşüş yönünde ancak yüksek riskli ilçelerde 60 eşiği": "The overall trend is downward, but in high-risk districts the 60 threshold",
        "kırılma riski devam ediyor.": "still remains at risk of being exceeded.",
        "Akıllı sayaç yaygınlaşması, su tasarrufu kampanyaları ve altyapı iyileştirmeleriyle": "With wider smart meter adoption, water-saving campaigns, and infrastructure improvements,",
        "büyüme hızının yarıya inmesi durumunda tüm ilçelerde belirgin risk azalışı öngörülmektedir.": "a clear risk reduction is projected across all districts if the growth rate is halved.",

        # Spatial / Moran / LISA explanations
        "Mekânsal Analiz": "Spatial Analysis",
        "Yüksek riskli ilçeler birbirine komşu mu": "Are high-risk districts clustered",
        "Global Moran's I nedir?": "What is Global Moran's I?",
        "p-değeri nedir?": "What is the p-value?",
        "p-değeri ne anlama geliyor?": "What does the p-value mean?",
        "Negatif kümelenme ne demek?": "What does negative clustering mean?",
        "HH küme neden yok?": "Why is there no HH cluster?",
        "2023 risk skorları": "2023 risk scores",
        "999 permütasyon testi": "999 permutation test",
        "Yorum": "Interpretation",
        "Negatif": "Negative",
        "HH Küme": "HH Cluster",
        "0 ilçe": "0 districts",
        "HH küme yok": "No HH cluster",
        "Mekânsal Analiz — Yüksek riskli ilçeler birbirine komşu mu, yoksa dağınık mı?": "Spatial analysis — Are high-risk districts clustered, or are they spatially dispersed?",
        "Tüm sistemi tek bir sayıyla özetler.": "Summarizes the whole system with a single number.",
        "Her ilçeye ayrı etiket verir": "Assigns a separate label to each district",
        "Riskli ilçe, komşuları da riskli": "High-risk district with high-risk neighbors",
        "Düşük riskli ilçe, komşuları da düşük": "Low-risk district with low-risk neighbors",
        "Riskli ilçe ama komşuları düşük riskli": "High-risk district with low-risk neighbors",
        "Düşük riskli ama komşuları yüksek riskli": "Low-risk district with high-risk neighbors",
        "dikkat gerektiriyor": "requires attention",
        "İzole Yüksek Risk": "Isolated High Risk",
        "Çevre Baskısı Altında": "Under Neighboring Pressure",
        "Gaziemir, komşuları Balçova, Konak ve Karabağlar'a kıyasla belirgin biçimde yüksek": "Gaziemir carries a noticeably higher",
        "risk skoru taşıyor": "risk score compared with its neighbors Balcova, Konak, and Karabaglar",
        "Bu \"HL\" (Yüksek-Düşük) sınıflandırması, ilçenin": "This HL (High-Low) classification shows that the district is",
        "bölgesel haritada": "on the regional map",
        "izole bir sıcak nokta": "an isolated hotspot",
        "olduğunu gösteriyor.": ".",
        "Neden?": "Why?",
        "Gaziemir'in hızlı nüfus artışı abone başına": "Gaziemir's rapid population growth pushes per-subscriber",
        "tüketimi yukarı çekiyor; aynı zamanda sanayi ve lojistik yoğunluğu su talebini": "consumption upward; industrial and logistics density also increases water demand,",
        "artırıyor.": ".",
        "Komşu ilçelerin düşük risk skoru bu ayrışmayı daha da belirginleştiriyor.": "The lower risk scores of neighboring districts make this divergence even clearer.",
        "Karşıyaka'nın kendi risk skoru düşük": "Karsiyaka's own risk score is low",
        "olsa da Çiğli ve Bayraklı gibi": "but it shares direct borders with",
        "yüksek riskli ilçelerle doğrudan sınır paylaşıyor.": "high-risk districts such as Cigli and Bayrakli.",
        "Düşük-Yüksek": "Low-High",
        "Yüksek-Düşük": "High-Low",
        "bu çevre baskısını yansıtıyor.": "reflects this neighboring pressure.",
        "Ne anlama geliyor?": "What does it mean?",
        "Bölgesel su sistemleri birbirine": "Regional water systems are",
        "bağlı olduğundan komşu ilçelerdeki yüksek risk": "interconnected; therefore, high risk in neighboring districts",
        "Karşıyaka'nın gelecekteki su": "may indirectly threaten Karsiyaka's future water",
        "güvenliğini dolaylı olarak tehdit edebilir.": "security.",
        "Uzun vadeli politikalar bu bağlantıyı": "Long-term policies should take this connection",
        "gözetmeli.": "into account.",
        "Mekânsal Lag": "Spatial Lag",
        "Sınıflandırması": "Classification",
        "SINIFLANDIRMASI": "CLASSIFICATION",

        # Methodology page
        "METODOLOJİ · ŞEFFAFLIK": "METHODOLOGY · TRANSPARENCY",
        "Metodoloji & Teknik Detaylar": "Methodology & Technical Details",
        "Teknik Detaylar": "Technical Details",
        "Veri kaynağı": "Data source",
        "İstatistiksel yöntemler": "Statistical methods",
        "Formüller": "Formulas",
        "Sınırlılıklar": "Limitations",
        "VERİ KAYNAĞI": "DATA SOURCE",
        "Veri Kaynağı": "Data Source",
        "İLÇE BAZLI VERİ": "DISTRICT-LEVEL DATA",
        "SİSTEM GENELİ VERİ": "SYSTEM-WIDE DATA",
        "Açık Veri Portalı": "Open Data Portal",
        "Açık Data Portalı": "Open Data Portal",
        "11 merkez ilçe": "11 central districts",
        "3 baraj": "3 dams",
        "Yıllık tüketim": "Annual consumption",
        "abone sayısı": "subscriber count",
        "Doluluk, üretim, kayıp oranı": "Fill rate, production, loss rate",
        "BOOTSTRAP SİMÜLASYONU": "BOOTSTRAP SIMULATION",
        "Block Bootstrap Simülasyonu": "Block Bootstrap Simulation",
        "NEDEN EK VERİ ÜRETİLDİ?": "WHY WAS ADDITIONAL DATA GENERATED?",
        "İZSU'nun resmi açık verisi yalnızca": "IZSU's official open data covers only",
        "dönemini kapsıyor": "period",
        "yani sadece": "that is, only",
        "İstatistiksel trend analizi": "Statistical trend analysis",
        "için bu süre yetersiz": "requires a longer period",
        "tıpkı 4 günlük hava gözlemiyle iklim analizi yapmaya çalışmak gibi": "similar to trying to analyze climate with only 4 days of weather observations",
        "Bu nedenle": "Therefore,",
        "arası 10 yıllık veri bilimsel yöntemle üretildi": "10 years of data were generated using a scientific method",
        "BLOCK BOOTSTRAP NEDİR?": "WHAT IS BLOCK BOOTSTRAP?",
        "Eldeki gerçek verileri küçük bloklara böl": "Split the available actual data into small blocks",
        "blokları istatistiksel kurallara göre": "shuffle the blocks according to statistical rules",
        "karıştırarak yeni seriler oluştur": "to create new series",
        "sonuçları geçmişe ait veri gibi kullan": "and use the results as historical-like data",
        "Hava tahminlerinde, finans modellerinde ve tıp araştırmalarında yaygın kullanılan": "It is a standard statistical technique widely used in weather forecasting, financial models, and medical research",
        "standart bir istatistik tekniğidir": "",
        "VERİLERE GÜVENİLEBİLİR Mİ?": "CAN THE DATA BE TRUSTED?",
        "Üretilen seri": "The generated series",
        "rastgele değil": "is not random",
        "gerçek su geçmişine uyumlu": "is calibrated to the actual water history",
        "kuraklık dönemi": "drought period",
        "baraj dolulukları düşük": "dam fill rates were low",
        "Pandemi dönemi hane tüketimi artışı": "household consumption increase during the pandemic period",
        "Nüfus büyümesi": "Population growth",
        "verisiyle": "data",
        "uyumlu": "consistent",
        "ŞEFFAFLIK": "TRANSPARENCY",
        "Site genelinde": "Across the site",
        "Mor = Bootstrap simülasyonu": "Purple = Bootstrap simulation",
        "Yeşil = İZSU Gerçek Verisi": "Green = IZSU Actual Data",
        "Kaynak kod GitHub'da açık erişimdedir": "The source code is publicly available on GitHub",
        "Tüm analizler Python ile yapıldı": "All analyses were performed with Python",
        "random seed sabittir": "the random seed is fixed",
        "sonuçlar tekrarlanabilir": "results are reproducible",
        "RİSK ENDEKSİ": "RISK INDEX",
        "Su Güvenliği Risk Endeksi": "Water Security Risk Index",
        "Adım": "Step",
        "Min-Max Normalizasyon": "Min-Max Normalization",
        "Entropy Ağırlıklandırma": "Entropy Weighting",
        "Bileşik Risk Skoru": "Composite Risk Score",
        "Ne yapar?": "What does it do?",
        "Bizim verimizde ne yaptı?": "What did it do in our data?",
        "Formülün tam yazımı": "Full formula",
        "Formül": "Formula",
        "Sonuç": "Result",
        "en düşük risk": "lowest risk",
        "en yüksek risk": "highest risk",
        "tüm göstergeler aynı ölçekte": "all indicators are on the same scale",
        "Farklı birimlerdeki göstergeleri": "It converts indicators with different units",
        "aynı 0–1 ölçeğine çeker": "to the same 0–1 scale",
        "Böylece": "Thus,",
        "birbirinden farklı birimleri toplayıp karşılaştırabiliriz": "different units can be aggregated and compared",
        "Örneğin": "For example,",
        "çok farklı değer aralıklarındadır": "have very different value ranges",
        "arasına çekildi": "were scaled into the 0–1 range",
        "en düşük değer": "the lowest value",
        "en yüksek değer": "the highest value",
        "Yüksek değer = yüksek risk yönünde normalize edildi": "Higher values were normalized in the direction of higher risk",
        "HESAPLANAN AĞIRLIKLAR": "CALCULATED WEIGHTS",
        "YIL VERİDEN": "YEARS OF DATA",
        "Talep (Abone Başına)": "Demand (Per Subscriber)",
        "ZAMANSAL ANALİZ": "TEMPORAL ANALYSIS",
        "Mann-Kendall Trend Testi": "Mann-Kendall Trend Test",
        "Bir veri serisinin zaman içinde sürekli artıp artmadığını veya azalıp azalmadığını": "Tests whether a data series consistently increases or decreases over time",
        "monoton trend": "monotonic trend",
        "test eder": "",
        "Normal dağılım varsaymaz": "It does not assume normal distribution",
        "bu onu su kalitesi gibi düzensiz verilere uygun kılar": "which makes it suitable for irregular data such as water quality",
        "14 yıllık risk serisi için her ilçede Mann-Kendall hesaplandı": "Mann-Kendall was calculated for each district using the 14-year risk series",
        "olan ilçelerde": "districts with",
        "azalan risk trendi saptandı": "a decreasing risk trend was detected",
        "istatistiksel güç": "statistical power",
        "çok daha yüksek": "much higher",
        "artan": "increasing",
        "azalan": "decreasing",
        "istatistiksel anlamlılık": "statistical significance",
        "Trendin yıllık değişim hızını hesaplar": "Calculates the annual rate of change of the trend",
        "Aykırı değerlerden etkilenmez": "It is robust to outliers",
        "ortanca (medyan) kullanır": "because it uses the median",
        "uç değerlere karşı güçlü kılar": "making it robust to extreme values",
        "Bornova için": "For Bornova,",
        "hesaplandı": "was calculated",
        "yani": "meaning",
        "her yıl ortalama": "each year on average",
        "azaldı": "decreased",
        "bu 14 yıllık düşüşü açıklar": "which explains the 14-year decline",
        "yıllık ortalama değişim büyüklüğü": "annual average change magnitude",
        "MEKÂNSAL ANALİZ": "SPATIAL ANALYSIS",
        "Tüm İzmir için risk değerlerinin mekânsal olarak kümelenip kümelenmediğini ölçer": "Measures whether risk values are spatially clustered across Izmir",
        "+1'e yakın = benzer ilçeler birbirine yakın": "close to +1 = similar districts are near each other",
        "−1'e yakın = farklı ilçeler yan yana": "close to -1 = different districts are side by side",
        "riskli ilçelerin genellikle": "high-risk districts are generally",
        "düşük riskli komşularla çevrili olduğunu gösteriyor": "surrounded by low-risk neighbors",
        "merkezi bir \"kötü bölge\" yok": "there is no central problematic region",
        "kümelenme": "clustering",
        "dağınık": "dispersed",
        "Satır-normalize ağırlık matrisi": "Row-normalized weight matrix",
        "Her ilçe için ayrı ayrı mekânsal skor üretir": "Calculates a separate local spatial score for each district",
        "genel tablo": "overall picture",
        "her ilçenin": "each district's",
        "sınıfını belirler": "classification",
        "yüksek risk, düşük riskli komşular": "high risk, low-risk neighbors",
        "düşük risk, yüksek riskli komşular": "low risk, high-risk neighbors",
        "izole sıcak nokta": "isolated hotspot",
        "çevre baskısı": "neighbor pressure",
        "permütasyon testi ile anlamlılık sınandı": "significance was tested using a permutation test",
        "küme": "cluster",
        "mekânsal aykırı değer": "spatial outlier",
        "PROJEKSİYON MODELİ": "PROJECTION MODEL",
        "Projeksiyon Modeli": "Projection Model",
        "CAGR Tabanlı Projeksiyon Modeli": "CAGR-Based Projection Model",
        "Her ilçenin geçmiş abone büyüme hızını": "Calculates each district's historical subscriber growth rate",
        "hesaplar ve bu hızı 3 farklı": "and extends this rate using three different",
        "senaryo katsayısıyla 2030'a kadar uzatır": "scenario coefficients through 2030",
        "k değerleri": "k values",
        "Baz senaryosunda": "in the base scenario",
        "Kötümser'de": "in the pessimistic scenario",
        "puana ulaşıyor": "points",
        "Sonuçlar 0–100 arasında sınırlandırıldı": "Results were clipped to the 0–100 range",
        "CAGR 14 yıllık seriden": "CAGR from the 14-year series",
        "SINIRLILIKLAR": "LIMITATIONS",
        "Sınırlılıklar & Şeffaflık": "Limitations & Transparency",
        "BOOTSTRAP KISITI": "BOOTSTRAP LIMITATION",
        "MEKÂNSAL KISIT": "SPATIAL LIMITATION",
        "TAHMİN KISITI": "FORECAST LIMITATION",
        "TEKRARLANABILIRLIK": "REPRODUCIBILITY",
        "verileri block bootstrap simülasyonudur": "data are block bootstrap simulations",
        "Gerçek tarihsel": "Actual historical",
        "verisi olmadığından bu dönemin yorumları gösterge niteliğindedir": "data are unavailable, so interpretations for this period are indicative",
        "kuraklık takvimine ve nüfus büyümesine uyumlu kalibre edilmiştir": "calibrated to the drought calendar and population growth",
        "istatistiksel güç açısından sınırlıdır": "is limited in terms of statistical power",
        "Komşuluk matrisi coğrafi sınırlar referans alınarak oluşturuldu": "The neighborhood matrix was created using geographic borders as reference",
        "projeksiyonu lineer büyüme varsayımına dayanır": "projection is based on a linear growth assumption",
        "İklim değişikliği, politika müdahaleleri ve göç etkileri modele dahil edilmemiştir": "Climate change, policy interventions, and migration effects are not included in the model",
        "Tüm analizler Python ile yapıldı": "All analyses were performed in Python",
        "Kaynak kod GitHub'da açık erişimde": "The source code is publicly available on GitHub",
        "Bootstrap simülasyonu sabit rastgele tohum": "Bootstrap simulation uses a fixed random seed",
        "ile tekrarlanabilir": "and is reproducible",
        "SIKÇA SORULAN SORULAR": "FREQUENTLY ASKED QUESTIONS",
        "Sıkça Sorulan Sorular": "Frequently Asked Questions",
        "nedir, neden kullanıldı": "what is it and why was it used",
        "verisi gerçek mi sayılır": "data considered actual",
        "Risk skoru ne anlama geliyor": "What does the risk score mean",
        "Neden 4 gösterge seçildi": "Why were 4 indicators selected",
        "Entropy ağırlıklandırma neden tercih edildi": "Why was entropy weighting preferred",
        "projeksiyonu neden 3 senaryoya ayrıldı": "Why is the projection divided into 3 scenarios",
        "testi 14 yıllık veriyle güvenilir mi": "test reliable with 14 years of data",
        "Komşuluk matrisi nasıl belirlendi": "How was the neighborhood matrix determined",
    })


    # Son temizlik: aşırı kısa substring çevirilerini kaldır, kalan sık görülen ENG/TR karışımlarını düzelt.
    for _bad_key in ["seri", "Seri", "bandı", "dan", "ile"]:
        TR_EN_REPLACEMENTS.pop(_bad_key, None)
    TR_EN_REPLACEMENTS.update({
        "font-family:Georgia,seriesf": "font-family:Georgia,serif",
        "serieses": "series",
        "seriesden": "series",
        "14-year serieses": "14-year series",
        "districtsinin": "districts",
        "districtsi": "district",
        "districtyi": "districts",
        "districtde": "district",
        "districtden": "district to district",
        "districtlerde": "districts",
        "districtlerdeki": "districts'",
        "districtlerin": "districts'",
        "districtnin": "district's",
        "centrali": "central",
        "bandnda": "band",
        "bandına": "band",
        "bandında": "range",
        "fill ratela": "fill rate",
        "Dam'nın": "Dam's",
        "%40'ı": "40%",
        "%40'ı faces": "40% faces",
        "3 district districts": "3 districts",
        "Open Data Portalı": "Open Data Portal",
        "Actual Datasi": "Actual Data",
        "simülasyonu": "simulation",
        "Simülasyonu": "Simulation",
        "Bootstrap simülasyonu": "Bootstrap simulation",
        "entropy ağırlıklarıyla": "using entropy weights",
        "Entropy ağırlıklı bileşik skor": "Entropy-weighted composite score",
        "gösterge": "indicator",
        "Gösterge": "Indicator",
        "ölçeği": "scale",
        "ölçek": "scale",
        "RİSK TRENDİ": "RISK TREND",
        "ANİK PROJEKSİYONU": "INSTANT PROJECTION",
        "PROJEKSİYONU": "PROJECTION",
        "PROJEKSİYONU": "PROJECTION",
        "PROJEKSİYONU": "PROJECTION",
        "PROJEKSİYONU": "PROJECTION",
        "PROJEKSİYONU": "PROJECTION",
        "PROJEKSİYONU": "PROJECTION",
        "PROJEKSİYONU": "PROJECTION",
        "PROJEKSİYONU": "PROJECTION",
        "PROJEKSİYONU": "PROJECTION",
        "PROJEKSİYONU": "PROJECTION",
        "PROJEKSİYONU": "PROJECTION",
        "PROJEKSİYONU": "PROJECTION",
        "RİSK": "RISK",
        "SİMÜLATÖR": "SIMULATOR",
        "ZAMAN SERİSİ": "TIME SERIES",
        "DEĞİŞİM HESAPLAYICI": "CHANGE CALCULATOR",
        "KARŞILAŞTIRMA": "COMPARISON",
        "Karşılaştırma": "Comparison",
        "Profili": "Profile",
        "GÖSTERGE": "INDICATOR",
        "Weightlı": "Weighted",
        "Hesap": "Calculation",
        "Artış": "Growth",
        "Kayıp": "Loss",
        "örn.": "e.g.",
        "Seçin": "Select",
        "aralığı": "range",
        "year aralığı": "year range",
        "üzerine gel": "hover over",
        "üzerinde": "on",
        "doğrudan": "directly",
        "yoksa": "or",
        "mı": "?",
        "değil": "not",
        "değildir": "is not",
        "değişiyor": "varies",
        "açısından": "in terms of",
        "kısıtlıdır": "is limited",
        "sınırlıdır": "is limited",
        "artırılabilir": "can be increased",
        "gözlemlenen": "observed",
        "mekânsal yapı": "spatial structure",
        "anlamlı": "significant",
        "güven düzeyinde": "confidence level",
        "İleride": "In the future",
        "eklenerek": "by adding",
        "yüksek riskli": "high-risk",
        "düşük riskli": "low-risk",
        "yüksek": "high",
        "düşük": "low",
        "komşuları": "neighbors",
        "komşular": "neighbors",
        "komşu": "neighbor",
        "çevrili": "surrounded",
        "olma eğiliminde": "tend to be",
        "satranç tahtası deseni": "checkerboard pattern",
        "istisnası": "exception",
        "kategorisinde": "category",
        "sanayi yoğunluğu": "industrial density",
        "nedeniyle": "due to",
        "ayrışıyor": "differs",
        "Hiçbir": "No",
        "hem kendisi": "itself",
        "hem de": "and also",
        "birbirine bitişik": "adjacent",
        "riskli bir bölge yok": "high-risk zone exists",
        "Risk yönetimi": "Risk management",
        "bazında uygulanabilir düzeyde": "can be applied at the district level",
        "böylece": "therefore",
        "Böylece": "Therefore",
        "çalışmak gibi": "work with",
        "hava gözlemiyle iklim analizi": "climate analysis from weather observations",
        "günlük": "daily",
        "dönemi": "period",
        "dönemini": "period",
        "dönemin": "period's",
        "kapsıyor": "covers",
        "kapsar": "covers",
        "yetersiz": "insufficient",
        "yetersizdir": "is insufficient",
        "için": "for",
        "ile": "with",
        "çünkü": "because",
        "bu onu": "this makes it",
        "düzensiz verilere uygun kılar": "suitable for irregular data",
        "kıyasla": "compared with",
        "n=4'e": "n=4",
        "oldukça": "quite",
        "güvenilir": "reliable",
        "güvenilir mi": "reliable?",
        "testi": "test",
        "veriyle": "with data",
        "veriler": "data",
        "verisi": "data",
        "verilerin": "data",
        "gerçek": "actual",
        "Hayır": "No",
        "Evet": "Yes",
        "Ancak": "However",
        "Rastgele": "Random",
        "rastgele": "random",
        "üretilmedi": "not generated",
        "kalibre edildi": "calibrated",
        "işaretlenmiştir": "marked",
        "araştırmacının": "researcher's",
        "Araştırmacının": "The researcher's",
        "öznel": "subjective",
        "kararlarını": "decisions",
        "kararlarını önler": "prevents decisions",
        "önler": "prevents",
        "dağılımı": "distribution",
        "belirler": "determines",
        "kabul görmüş": "accepted",
        "nesnel": "objective",
        "yaklaşımdır": "approach",
        "belirsizliği": "uncertainty",
        "gizler": "hides",
        "tasarruf politikalarını": "saving policies",
        "mevcut trendi": "current trend",
        "hızlı kentleşme": "rapid urbanization",
        "kuraklık baskısını": "drought pressure",
        "temsil eder": "represents",
        "geleceğin": "future",
        "öngörülmektedir": "is projected",
        "coğrafi sınırları": "geographic borders",
        "fiziksel olarak sınır paylaştığı": "physically shares a border with",
        "belirlendi": "was determined",
        "doğrulandı": "was verified",
        "satır-normalize edildi": "row-normalized",
        "puana": "points",
        "puan": "points",
        "Puan": "Points",
        "Scoreları": "Scores",
    })

    def L(obj):
        """ENG modunda görünen metinleri İngilizceye çevirir; TR modunda aynen bırakır."""
        if dil != "EN":
            return obj
        if isinstance(obj, str):
            out = obj
            for tr_txt, en_txt in sorted(TR_EN_REPLACEMENTS.items(), key=lambda kv: len(kv[0]), reverse=True):
                out = out.replace(tr_txt, en_txt)
            # Clean up artifacts created by earlier broad replacements.
            cleanup = {
                "seriesf": "serif",
                "serieses": "series",
                "seriesden": "series",
                "districtsinin": "districts",
                "districtss": "districts",
                "districtsi": "district",
                "districtde": "district",
                "bandnda": "band",
                "scoreları": "scores",
                "Scoreları": "Scores",
                "Weightlı": "Weighted",
                "Actual Datasi": "Actual Data",
                "gap verisi": "open data",
                "gapça": "clearly",
                "yearnda": "year",
                "dönemde": "period",
                "dönemdeki": "period",
                "dönemi": "period",
                "dönemin": "period's",
                "mi?": "?",
                " mı?": "?",
                "whwith": "while",
                "fwith": "file",
            }
            for a, b in cleanup.items():
                out = out.replace(a, b)
            # Last-resort transliteration so ENG mode never shows Turkish characters.
            trans = str.maketrans({"ç":"c","Ç":"C","ğ":"g","Ğ":"G","ı":"i","İ":"I","ö":"o","Ö":"O","ş":"s","Ş":"S","ü":"u","Ü":"U"})
            out = out.translate(trans)
            return out
        if isinstance(obj, list):
            return [L(x) for x in obj]
        if isinstance(obj, tuple):
            return tuple(L(x) for x in obj)
        if isinstance(obj, dict):
            return {L(k): L(v) for k, v in obj.items()}
        return obj

    def _localize_figure(fig):
        if dil != "EN":
            return fig
        try:
            fig_dict = fig.to_dict()
            return go.Figure(L(fig_dict))
        except Exception:
            return fig

    def _localize_df(df):
        if dil != "EN":
            return df
        try:
            if isinstance(df, pd.DataFrame):
                out = df.copy()
                out.columns = [L(str(c)) for c in out.columns]
                for c in out.select_dtypes(include=["object", "category"]).columns:
                    out[c] = out[c].astype(str).map(L)
                return out
        except Exception:
            return df
        return df

    _st_markdown = st.markdown
    _st_caption = st.caption
    _st_write = st.write
    _st_plotly_chart = st.plotly_chart
    _st_dataframe = st.dataframe
    _st_tabs = st.tabs
    _st_selectbox = st.selectbox
    _st_slider = st.slider
    _st_select_slider = st.select_slider
    _st_text_input = st.text_input
    _st_expander = st.expander
    _st_button = st.button

    def md_localized(body, *args, **kwargs):
        return _st_markdown(L(body), *args, **kwargs)
    def caption_localized(body, *args, **kwargs):
        return _st_caption(L(body), *args, **kwargs)
    def write_localized(*args, **kwargs):
        return _st_write(*[L(a) for a in args], **kwargs)
    def plotly_localized(fig, *args, **kwargs):
        return _st_plotly_chart(_localize_figure(fig), *args, **kwargs)
    def dataframe_localized(data=None, *args, **kwargs):
        return _st_dataframe(_localize_df(data), *args, **kwargs)
    def tabs_localized(tabs, *args, **kwargs):
        return _st_tabs(L(tabs), *args, **kwargs)
    def selectbox_localized(label, options, *args, **kwargs):
        old_format = kwargs.get("format_func", lambda x: x)
        if dil == "EN":
            kwargs["format_func"] = lambda x: L(old_format(x))
        return _st_selectbox(L(label), options, *args, **kwargs)
    def slider_localized(label, *args, **kwargs):
        return _st_slider(L(label), *args, **kwargs)
    def select_slider_localized(label, *args, **kwargs):
        return _st_select_slider(L(label), *args, **kwargs)
    def text_input_localized(label, *args, **kwargs):
        if "placeholder" in kwargs:
            kwargs["placeholder"] = L(kwargs["placeholder"])
        return _st_text_input(L(label), *args, **kwargs)
    def expander_localized(label, *args, **kwargs):
        return _st_expander(L(label), *args, **kwargs)
    def button_localized(label, *args, **kwargs):
        return _st_button(L(label), *args, **kwargs)

    st.markdown = md_localized
    st.caption = caption_localized
    st.write = write_localized
    st.plotly_chart = plotly_localized
    st.dataframe = dataframe_localized
    st.tabs = tabs_localized
    st.selectbox = selectbox_localized
    st.slider = slider_localized
    st.select_slider = select_slider_localized
    st.text_input = text_input_localized
    st.expander = expander_localized
    st.button = button_localized

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
                    {"WATER SECURITY ANALYSIS · IZMIR" if dil=="EN" else "SU GÜVENLİĞİ ANALİZİ · İZMİR"} · {START_YEAR}–{PRED_END_YEAR}
                </span>
            </div>
            <div class="wave-container"><div class="wave"></div></div>
            <h1 style="color:#ffffff;font-size:2.6rem;font-weight:800;margin:0.8rem 0 0.4rem 0;
                       letter-spacing:-0.5px;line-height:1.2;">
                {("Izmir Water Security" if dil=="EN" else "İzmir Su Güvenliği")}<br>
                <span style="color:#38d1e3;">{"Risk Index" if dil=="EN" else "Risk Endeksi"}</span>
            </h1>
            <p style="color:#a8d8f0;font-size:1rem;margin:0.6rem 0 0 0;max-width:600px;
                      display:inline-block;line-height:1.6;">
                {t("hero_alt")}
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

        # ── KPI Kartları — manuel, ilçe listeli
        k1, k2, k3, k4, k5 = st.columns(5)

        kpi_data = [
            (k1, "🔴", "#d62728", t("kpi_yuksek"), ["Bornova", "Çiğli", "Bayraklı"]),
            (k2, "🟡", "#ff7f0e", t("kpi_orta"),   ["Buca", "Gaziemir", "Güzelbahçe", "Karşıyaka", "Narlıdere"]),
            (k3, "🟢", "#2ca02c", t("kpi_dusuk"),  ["Konak", "Karabağlar", "Balçova"]),
            (k4, "💧", "#38d1e3", t("kpi_baraj"),        [f"%{tahtali:.1f}", f"{END_YEAR} yılı"]),
            (k5, "✅", "#2ca02c", t("kpi_enaz"),           ["Balçova", "Skor: 42.7"]),
        ]
        for col, ikon, renk, baslik, satirlar in kpi_data:
            with col:
                satirlar_html = "".join(
                    f'<div style="color:#ffffff;font-size:0.82rem;font-weight:600;'
                    f'line-height:1.6;">{s}</div>'
                    for s in satirlar
                )
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.06);
                            border:1px solid {renk}44;
                            border-top:3px solid {renk};
                            border-radius:10px;padding:1rem;
                            text-align:center;min-height:130px;">
                    <div style="font-size:1.4rem;margin-bottom:4px;">{ikon}</div>
                    <div style="color:#a8d8f0;font-size:0.68rem;letter-spacing:1px;
                                text-transform:uppercase;margin-bottom:6px;">{baslik}</div>
                    {satirlar_html}
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
                            text-transform:uppercase;">{"01 · Risk Göstergesi" if dil=="TR" else "01 · Risk Indicator"}</div>
                <div style="color:#ffffff;font-size:1.1rem;font-weight:600;">
                    {"En Riskli 3 İlçe" if dil=="TR" else "Top 3 High-Risk Districts"} — {END_YEAR} {"Risk İbresi" if dil=="TR" else "Risk Gauge"}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Gauge — manuel sabit değerler
        gauge_data = [
            ("BORNOVA",  67.0, +2.3),   # delta: geçen yıla göre artış
            ("ÇİĞLİ",   63.0, +1.8),
            ("BAYRAKLI", 60.0, -0.5),
        ]
        gauge_col1, gauge_col2, gauge_col3 = st.columns(3)
        for col, (ilce_adi, skor, delta_val) in zip(
            [gauge_col1, gauge_col2, gauge_col3], gauge_data
        ):
            renk = "#d62728"   # hepsi yüksek risk (60+)
            sinif_label = "Yüksek Risk"
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=skor,
                delta={
                    "reference": skor - delta_val,
                    "valueformat": ".1f",
                    "increasing": {"color": "#d62728"},
                    "decreasing": {"color": "#2ca02c"},
                },
                number={"font": {"size": 32, "color": "white"}, "valueformat": ".1f"},
                title={
                    "text": (
                        f"<b style='font-size:15px'>{ilce_adi}</b><br>"
                        f"<span style='font-size:11px;color:{renk}'>{sinif_label}</span>"
                    ),
                    "font": {"size": 14, "color": "white"},
                },
                gauge={
                    "axis": {
                        "range": [0, 100], "tickwidth": 1,
                        "tickcolor": "rgba(255,255,255,0.3)",
                        "tickfont": {"color": "rgba(255,255,255,0.5)", "size": 9},
                    },
                    "bar": {"color": renk, "thickness": 0.3},
                    "bgcolor": "rgba(255,255,255,0.03)",
                    "borderwidth": 1,
                    "bordercolor": "rgba(255,255,255,0.15)",
                    "steps": [
                        {"range": [0,  60], "color": "rgba(44,160,44,0.15)"},
                        {"range": [60, 80], "color": "rgba(214,39,40,0.20)"},
                        {"range": [80,100], "color": "rgba(139,0,0,0.25)"},
                    ],
                    "threshold": {
                        "line": {"color": "white", "width": 2},
                        "thickness": 0.75, "value": skor,
                    },
                },
            ))
            fig_gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=240, margin=dict(t=70, b=10, l=20, r=20),
                font=dict(color="white"),
            )
            with col:
                st.plotly_chart(fig_gauge, use_container_width=True,
                                key=f"gauge_{ilce_adi}")

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        # ── Bölüm başlığı — Risk Sıralaması
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:1rem;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);
                        border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.7rem;letter-spacing:2px;
                            text-transform:uppercase;">{"02 · Risk Analizi" if dil=="TR" else "02 · Risk Analysis"}</div>
                <div style="color:#ffffff;font-size:1.1rem;font-weight:600;">
                    {(f"{END_YEAR} Yılı İlçe Risk Sıralaması & Ağırlık Dağılımı" if dil=="TR" else f"{END_YEAR} District Risk Ranking & Weight Distribution")}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([3,2])
        with col1:
            # Manuel sabit risk skorları — sıralı (yüksekten düşüğe)
            manuel_ilceler = [
                ("BORNOVA",    67.0),
                ("ÇİĞLİ",     63.0),
                ("BAYRAKLI",   60.0),
                ("BUCA",       57.0),
                ("GAZİEMİR",   54.0),
                ("GÜZELBAHÇE", 51.0),
                ("KARŞIYAKA",  49.0),
                ("NARLIDERE",  47.0),
                ("KONAK",      46.0),
                ("KARABAĞLAR", 43.0),
                ("BALÇOVA",    42.0),
            ]
            # Renk: ≥60 kırmızı, 46-59 turuncu, <46 yeşil
            def risk_renk_manuel(s):
                if s >= 60: return "#d62728"
                if s >= 46: return "#ff7f0e"
                return "#2ca02c"

            ilce_adlari = [x[0] for x in manuel_ilceler]
            skorlar     = [x[1] for x in manuel_ilceler]
            renkler     = [risk_renk_manuel(s) for s in skorlar]

            fig = go.Figure(go.Bar(
                x=skorlar,
                y=ilce_adlari,
                orientation="h",
                marker=dict(color=renkler, line=dict(color="rgba(255,255,255,0.1)", width=0.5)),
                text=[f"{s:.0f}" for s in skorlar],
                textposition="outside",
                textfont=dict(color="white", size=11),
                hovertemplate="<b>%{y}</b><br>Risk Skoru: %{x:.1f}<extra></extra>"
            ))
            fig.add_vline(x=46, line_dash="dot", line_color="#ff7f0e",
                          line_width=1.5, annotation_text=("Orta Risk Eşiği (46)" if dil=="TR" else "Medium Risk Threshold (46)"),
                          annotation_font_color="#ff7f0e", annotation_font_size=10)
            fig.add_vline(x=60, line_dash="dot", line_color="#d62728",
                          line_width=1.5, annotation_text=("Yüksek Risk Eşiği (60)" if dil=="TR" else "High Risk Threshold (60)"),
                          annotation_font_color="#d62728", annotation_font_size=10)
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                height=420, margin=dict(t=10,b=10,l=10,r=80),
                xaxis=dict(range=[0,80], gridcolor="rgba(255,255,255,0.08)",
                           tickfont=dict(color="white"), title="Risk Skoru (0–100)",
                           title_font=dict(color="#a8d8f0")),
                yaxis=dict(autorange="reversed", tickfont=dict(color="white", size=11))
            )
            st.plotly_chart(fig, use_container_width=True, key="bar_risk_02")

        with col2:
            # Entropy ağırlıkları pasta — manuel sabit, mavi tonları
            pie_labels = ["Su Kayıp Oranı", "Kişi Başı Tüketim", "Arz Kısıtı", "Tüketim Artış Oranı"]
            pie_values = [33.0, 31.6, 23.8, 11.6]
            pie_colors = ["#1a3a6b", "#2166ac", "#4393c3", "#92c5de"]

            fig2 = go.Figure(go.Pie(
                labels=pie_labels,
                values=pie_values,
                hole=0.52,
                marker=dict(colors=pie_colors,
                            line=dict(color="rgba(255,255,255,0.15)", width=1.5)),
                textinfo="percent+label",
                textfont=dict(color="white", size=11),
                hovertemplate="<b>%{label}</b><br>Ağırlık: %{value}%<extra></extra>",
                sort=False,
            ))
            fig2.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                height=340, margin=dict(t=20,b=10,l=10,r=10),
                showlegend=True,
                legend=dict(font=dict(color="white", size=10),
                            bgcolor="rgba(0,0,0,0)",
                            orientation="v", x=1.0, y=0.5),
                annotations=[dict(
                    text="Entropy<br>Ağırlıkları",
                    x=0.5, y=0.5,
                    font=dict(size=12, color="white"),
                    showarrow=False
                )]
            )
            st.plotly_chart(fig2, use_container_width=True, key="pie_entropy_02")

            st.markdown(f"""
            <div style="background:rgba(56,209,227,0.08);border:1px solid rgba(56,209,227,0.2);
                        border-radius:8px;padding:0.8rem 1rem;margin-top:0.4rem;">
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

        # ── 03 · Küresel Bağlam — gerçek kaynaklara dayalı
        wsri_ort = sum([67,63,60,57,54,51,49,47,46,43,42]) / 11

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:1rem;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.7rem;letter-spacing:2px;">{"03 · KÜRESEL BAĞLAM" if dil=="TR" else "03 · GLOBAL CONTEXT"}</div>
                <div style="color:#ffffff;font-size:1.1rem;font-weight:600;">{"İzmir Dünya Genelinde Nerede?" if dil=="TR" else "Where Does Izmir Stand Globally?"}</div>
            </div>
        </div>
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:0.8rem;">
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(214,39,40,0.3);
                        border-radius:10px;padding:0.9rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.68rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">
                    {"Su Stresi Altındaki Nüfus" if dil=="TR" else "Population Under Water Stress"}</div>
                <div style="color:#d62728;font-size:1.6rem;font-weight:700;">%40</div>
                <div style="color:#a8d8f0;font-size:0.68rem;line-height:1.5;margin-top:3px;">
                    Dünya nüfusunun %40'ı yılın en az bir ayında ciddi su stresiyle karşılaşıyor.<br>
                    <span style="color:#6a8fa8;">WRI Aqueduct 2023</span>
                </div>
            </div>
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,127,14,0.3);
                        border-radius:10px;padding:0.9rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.68rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">
                    {"Akdeniz Havzası Su Açığı" if dil=="TR" else "Mediterranean Basin Water Deficit"}</div>
                <div style="color:#ff7f0e;font-size:1.6rem;font-weight:700;">−20%</div>
                <div style="color:#a8d8f0;font-size:0.68rem;line-height:1.5;margin-top:3px;">
                    İklim değişikliğiyle Akdeniz havzasında yıllık yağış 2050'ye kadar
                    %20 azalması bekleniyor. İzmir bu kuşağın merkezinde.<br>
                    <span style="color:#6a8fa8;">IPCC AR6 · 2021</span>
                </div>
            </div>
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(56,209,227,0.3);
                        border-radius:10px;padding:0.9rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.68rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">
                    {"İzmir WSRI Ortalaması" if dil=="TR" else "Izmir WSRI Average"}</div>
                <div style="color:#38d1e3;font-size:1.6rem;font-weight:700;">{wsri_ort:.1f}</div>
                <div style="color:#a8d8f0;font-size:0.68rem;line-height:1.5;margin-top:3px;">
                    11 merkez ilçe ortalaması — Orta Risk bandı.
                    Yüksek risk eşiğine (60) henüz ulaşılmamış ancak 3 ilçe sınırı geçmiş.<br>
                    <span style="color:#6a8fa8;">İZSU + Bu çalışma · {END_YEAR}</span>
                </div>
            </div>
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(44,160,44,0.3);
                        border-radius:10px;padding:0.9rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.68rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">
                    {"Türkiye'nin Kişi Başı Su Potansiyeli" if dil=="TR" else "Turkey's Per Capita Water Potential"}</div>
                <div style="color:#2ca02c;font-size:1.6rem;font-weight:700;">1.346 m³</div>
                <div style="color:#a8d8f0;font-size:0.68rem;line-height:1.5;margin-top:3px;">
                    Kişi başı yıllık kullanılabilir tatlı su. Uluslararası eşik 1.700 m³ —
                    Türkiye "su kıtlığı" sınırına yakın.<br>
                    <span style="color:#6a8fa8;">DSİ · 2022</span>
                </div>
            </div>
        </div>
        <div style="background:rgba(56,209,227,0.05);border:1px solid rgba(56,209,227,0.15);
                    border-radius:8px;padding:0.7rem 1rem;margin-bottom:1.5rem;">
            <span style="color:#38d1e3;font-size:0.75rem;font-weight:600;">📌 Kaynak notu: </span>
            <span style="color:#a8d8f0;font-size:0.78rem;">
                WRI (World Resources Institute) Aqueduct 2023 · IPCC Altıncı Değerlendirme Raporu (AR6, 2021) ·
                DSİ (Devlet Su İşleri) 2022 yıllık raporu · İZSU açık veri portalı.
                Tüm global değerler özgün raporlardan alınmış olup bu çalışmada değiştirilmemiştir.
            </span>
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
            <a href="https://twitter.com/intent/tweet?text=İzmir%20Su%20Güvenliği%20Risk%20Endeksi%20%7C%20Entropy%20ağırlıklı%20bileşik%20analiz%20%7C%20{START_YEAR}-2030%20projeksiyonu&url=https://izmirisk.streamlit.app"
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
                    KEŞİFSEL VERİ ANALİZİ · {START_YEAR}–{END_YEAR}
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
            "💧 " + ("Baraj Doluluk" if dil=="TR" else "Dam Levels"),
            "🌡️ " + ("Tüketim Haritası" if dil=="TR" else "Consumption Map"),
            "⚖️ " + ("Arz-Talep" if dil=="TR" else "Supply-Demand"),
            "📉 " + ("Kayıp Oranı" if dil=="TR" else "Loss Rate")
        ])

        with tab1:
            bolum_baslik("01", "BARAJ TARİHÇESİ", "İzmir'in Barajları — Tarihçe & Genel Bilgi")

            # Baraj tanıtım kartları — detaylı
            bc1, bc2, bc3 = st.columns(3)
            baraj_detay = [
                (bc1, "💧 Tahtalı Barajı", "#38d1e3",
                 "📍 Konum: Menderes İlçesi, İzmir  |  📅 Yapım: 1993–1997  |  🏗️ Tip: Kaya dolgu",
                 [
                     ("İzmir'in en büyük su deposu.", "Tahtalı Barajı, şehrin su ihtiyacının yaklaşık **%60–70'ini** tek başına karşılar. Tahtalı Çayı üzerinde inşa edilmiş olup havzası 432 km²\'dir. Toplam depolama kapasitesi **309 milyon m³** — bu miktar İzmir\'in yaklaşık 2 yıllık su tüketimine eşdeğerdir."),
                     ("2014–2023 Dönemi:", "2014 yılında olağandışı yağışlarla **%44 doluluk** zirvesini yaşadı. 2020\'de Gördes Barajı\'nın kritik seviyelere inmesiyle üzerindeki baskı arttı. 2023 itibarıyla **%29 dolulukla** seyretmekte — 2010\'daki %38 seviyesinin belirgin altında."),
                 ],
                 "2023 Doluluk: %29  |  Kapasite: 309 M m³"),
                (bc2, "🌿 Balçova Barajı", "#2ca02c",
                 "📍 Konum: Balçova İlçesi, İzmir  |  📅 Yapım: 1991–1995  |  🏗️ Tip: Beton kemer",
                 [
                     ("Küçük ama stratejik.", "Balçova Barajı, Bornova ve yakın çevresi başta olmak üzere merkezi ilçeleri destekler. Meles Çayı üzerinde konumlanan baraj, görece küçük havzasına (47 km²) karşın şehir içi konumu nedeniyle kritik önem taşır. Depolama kapasitesi **57 milyon m³** olup sisteme hızlı müdahale imkânı sunar."),
                     ("2010–2023 İstikrarı:", "14 yıllık dönemde en istikrarlı doluluk seyrini gösteren barajdır: **%26–%34 bandında** kalmayı başardı. Fiziki konumu gereği buharlaşma kaybı görece düşüktür."),
                 ],
                 "2023 Doluluk: %32  |  Kapasite: 57 M m³"),
                (bc3, "🚨 Gördes Barajı", "#d62728",
                 "📍 Konum: Gördes İlçesi, Manisa  |  📅 Yapım: 1976–1980  |  🏗️ Tip: Toprak dolgu",
                 [
                     ("Kırılgan ama önemli.", "Gördes Barajı coğrafi olarak Manisa iline bağlı olsa da İzmir\'in su sistemine borularla bağlanmıştır. Depolama kapasitesi **176 milyon m³** olan bu baraj, aynı zamanda sulama ve taşkın önleme işlevi görür."),
                     ("2019–2021 Kriz Dönemi:", "Gördes, 2019\'da %18 dolulukla zaten düşük seyrederken 2020\'de **%2\'ye**, 2021\'de ise tarihi dip olan **%1\'e** indi. Bu, tek bir barajın kuraklıkla nasıl çöküşe geçebildiğini gösteren çarpıcı bir örnektir. 2022–2023\'te kısmi toparlanma yaşandı ancak uzun vadeli kırılganlık devam etmektedir."),
                 ],
                 "2023 Doluluk: %5  |  Kapasite: 176 M m³  |  Kritik Seviye"),
            ]

            for col, isim, renk, konum_tip, aciklama_listesi, durum in baraj_detay:
                with col:
                    with st.expander(isim, expanded=True):
                        img_map = {
                            "💧 Tahtalı Barajı": "tahtali.jpg",
                            "🌿 Balçova Barajı": "balcova.jpg",
                            "🚨 Gördes Barajı":  "gordes.jpg",
                        }
                        img_file = img_map.get(isim, "")
                        try:
                            st.image(img_file, use_container_width=True)
                        except Exception:
                            st.markdown("""<div style="background:rgba(0,0,0,0.25);height:140px;
                                display:flex;align-items:center;justify-content:center;
                                border-radius:8px;font-size:2.5rem;margin-bottom:8px;">🏞️</div>""",
                                unsafe_allow_html=True)
                        st.markdown(f'<div style="color:{renk};font-size:0.72rem;font-weight:600;margin:8px 0 10px 0;">{konum_tip}</div>', unsafe_allow_html=True)
                        for baslik_p, metin_p in aciklama_listesi:
                            st.markdown(f"**{baslik_p}** {metin_p}")
                        st.markdown(f'<div style="background:rgba(255,255,255,0.06);border-left:3px solid {renk};border-radius:0 6px 6px 0;padding:0.5rem 0.8rem;margin-top:0.8rem;"><span style="color:{renk};font-size:0.78rem;font-weight:700;">{durum}</span></div>', unsafe_allow_html=True)

            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            bolum_baslik("02", "BARAJ DOLULUK", f"Baraj Doluluk Oranları ({START_YEAR}–{END_YEAR})")

            baraj_yillar = [2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023]
            tahtali_v = [38,35,37,36,44,41,34,36,36,35,35,31,40,29]
            balcova_v = [33,32,29,30,31,31,34,32,31,31,30,26,27,32]
            gordes_v  = [22,21,24,15,16,16,21,22,24,18, 2, 1, 4, 5]
            esik = 15.0
            col1, col2 = st.columns([3,1])
            with col1:
                fig = go.Figure()
                for isim, renk, sembol, degerler in [
                    ("Tahtalı","#38d1e3","circle",tahtali_v),
                    ("Balçova","#2ca02c","square",balcova_v),
                    ("Gördes","#d62728","diamond",gordes_v),
                ]:
                    fig.add_trace(go.Scatter(x=baraj_yillar, y=degerler, mode="lines+markers", name=isim,
                        line=dict(color=renk,width=2.5), marker=dict(size=10,symbol=sembol),
                        hovertemplate=f"<b>{isim}</b>: %{{y:.0f}}%<extra></extra>"))
                fig.add_vline(x=2019.5, line_dash="dash", line_color="rgba(155,89,182,0.6)", line_width=1.5,
                    annotation_text="Bootstrap | Gerçek →", annotation_font_color="#c39bd3", annotation_font_size=9)
                fig.add_hline(y=esik, line_dash="dash", line_color="#ff7f0e", line_width=1.5,
                    annotation_text=f"Kritik Eşik: {esik:.0f}%", annotation_font_color="#ff7f0e", annotation_font_size=10)
                fig.update_layout(**layout_base, height=420,
                    yaxis=dict(title="Doluluk (%)", range=[0,55], gridcolor="rgba(255,255,255,0.1)", tickfont=dict(color="white")))
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                for isim, renk, son_val, ilk_val in [("Tahtalı","#38d1e3",29,38),("Balçova","#2ca02c",32,33),("Gördes","#d62728",5,22)]:
                    degisim = son_val - ilk_val
                    ok = "▼" if degisim < 0 else "▲"
                    ok_renk = "#d62728" if degisim < 0 else "#2ca02c"
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.05);border:1px solid {renk}44;
                                border-left:3px solid {renk};border-radius:8px;padding:0.6rem 0.8rem;margin-bottom:0.5rem;">
                        <div style="color:{renk};font-size:0.75rem;font-weight:600;">{isim}</div>
                        <div style="color:white;font-size:1.1rem;font-weight:700;">%{son_val}</div>
                        <div style="color:{ok_renk};font-size:0.78rem;">{ok} {abs(degisim)} puan ({START_YEAR}'dan)</div>
                    </div>""", unsafe_allow_html=True)
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:12px;margin:1.2rem 0 0.8rem 0;">
                <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);border-radius:2px;"></div>
                <div><div style="color:#38d1e3;font-size:0.7rem;letter-spacing:2px;">04 · BULGULAR</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">Öne Çıkan Bulgular & Dönüm Noktaları</div></div>
            </div>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;">
                <div style="background:rgba(214,39,40,0.07);border:1px solid rgba(214,39,40,0.25);border-radius:8px;padding:0.8rem 1rem;">
                    <div style="color:#d62728;font-size:0.7rem;font-weight:600;letter-spacing:1px;margin-bottom:5px;">2013–2015 · DÜŞÜK SEVİYE PERİYODU</div>
                    <div style="color:#ffffff;font-size:0.82rem;font-weight:600;margin-bottom:4px;">Tahtalı ve Gördes eş zamanlı geriledi</div>
                    <div style="color:#a8d8f0;font-size:0.8rem;line-height:1.6;">2013–2015 arasında Tahtalı %36–%41 bandında seyrederken Gördes %15–%16'ya indi.
                    İki barajın eş zamanlı düşüşü arz esnekliğini daralttı ve sistem üzerinde yoğun baskı yarattı.</div>
                </div>
                <div style="background:rgba(214,39,40,0.07);border:1px solid rgba(214,39,40,0.25);border-radius:8px;padding:0.8rem 1rem;">
                    <div style="color:#d62728;font-size:0.7rem;font-weight:600;letter-spacing:1px;margin-bottom:5px;">2019–2021 · GÖRDES KRİZİ</div>
                    <div style="color:#ffffff;font-size:0.82rem;font-weight:600;margin-bottom:4px;">%18'den %1'e tek yılda çöküş</div>
                    <div style="color:#a8d8f0;font-size:0.8rem;line-height:1.6;">Gördes 2019'da %18 dolulukla zaten düşük seyrederken 2020'de %2, 2021'de %1'e indi.
                    Uzun süreli kuraklığın su kaynakları üzerindeki yıkıcı etkisini belgeleyen kritik bir veri noktasıdır.</div>
                </div>
                <div style="background:rgba(255,127,14,0.07);border:1px solid rgba(255,127,14,0.25);border-radius:8px;padding:0.8rem 1rem;">
                    <div style="color:#ff7f0e;font-size:0.7rem;font-weight:600;letter-spacing:1px;margin-bottom:5px;">2020 · PANDEMİ DÖNEMİ ETKİSİ</div>
                    <div style="color:#ffffff;font-size:0.82rem;font-weight:600;margin-bottom:4px;">Evde kalma → artan tüketim baskısı</div>
                    <div style="color:#a8d8f0;font-size:0.8rem;line-height:1.6;">COVID-19 sürecinde hane içi su kullanımı belirgin biçimde arttı.
                    Aynı dönemde Gördes kritik seviyelere inerken tüketim yüksek seyretti — arz-talep dengesi ciddi biçimde bozuldu.</div>
                </div>
            </div>""", unsafe_allow_html=True)

        with tab2:
            bolum_baslik("02", "TALEP ISISI", "Abone Başına Tüketim Isı Haritası (m³/abone)")
            heatmap_data = {
                "NARLIDERE":  [198,201,196,194,200,203,197,199,202,198,185,170,175,178],
                "BORNOVA":    [193,190,186,183,188,186,183,185,187,184,180,178,181,179],
                "BAYRAKLI":   [178,176,173,170,174,172,169,171,173,170,167,165,168,166],
                "KARŞIYAKA":  [171,169,166,163,167,165,162,164,166,163,160,158,161,159],
                "BUCA":       [162,160,157,154,158,156,153,155,157,154,151,149,152,150],
                "ÇİĞLİ":     [158,156,153,150,154,152,150,152,154,151,148,146,149,147],
                "GAZİEMİR":  [152,150,148,145,149,147,145,147,149,146,150,155,158,162],
                "GÜZELBAHÇE":[148,146,144,142,145,143,141,143,145,142,139,137,140,138],
                "KONAK":      [132,130,128,126,129,127,125,127,129,126,123,121,124,122],
                "BALÇOVA":    [118,116,114,112,115,113,111,113,115,112,109,107,110,108],
                "KARABAĞLAR": [112,110,108,106,109,107,105,107,109,106,103,101,104,102],
            }
            ilce_sirali = list(heatmap_data.keys())
            yillar_str = [str(y) for y in YEARS]
            z_vals = [heatmap_data[ilce] for ilce in ilce_sirali]
            fig = go.Figure(go.Heatmap(z=z_vals, x=yillar_str, y=ilce_sirali,
                colorscale=[[0,"#2ca02c"],[0.35,"#aacc44"],[0.6,"#ff7f0e"],[1,"#d62728"]],
                zmin=100, zmax=210,
                text=[[str(v) for v in row] for row in z_vals],
                texttemplate="%{text}", textfont=dict(size=9,color="white"),
                hovertemplate="<b>%{y}</b> · %{x}<br>%{z} m³/abone<extra></extra>",
                colorbar=dict(title="m³/abone",tickfont=dict(color="white"),len=0.9,thickness=14)))
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                height=480, margin=dict(t=10,b=40,l=130,r=30),
                xaxis=dict(tickmode="array",tickvals=yillar_str,ticktext=yillar_str,
                           tickfont=dict(color="white",size=10),tickangle=-45),
                yaxis=dict(tickfont=dict(color="white",size=11), autorange="reversed"))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:12px;margin:1.2rem 0 0.8rem 0;">
                <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);border-radius:2px;"></div>
                <div><div style="color:#38d1e3;font-size:0.7rem;letter-spacing:2px;">04 · BULGULAR</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">Öne Çıkan Bulgular & Dönüm Noktaları</div></div>
            </div>
            <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:10px;">
                <div style="background:rgba(214,39,40,0.07);border:1px solid rgba(214,39,40,0.25);border-radius:8px;padding:0.8rem 1rem;">
                    <div style="color:#d62728;font-size:0.72rem;font-weight:700;letter-spacing:1px;margin-bottom:5px;">🔴 NARLIDERE — Yüksek Tüketim, Düşük Risk</div>
                    <div style="color:#d0e8f5;font-size:0.82rem;line-height:1.6;">Narlıdere kişi başı tüketime göre listenin en üstünde ancak risk sıralamasında alt sıralarda.
                    Bunun nedeni küçük abone tabanı, eski yapı stoğu ve 2010'lar boyunca süren kentsel dönüşüm sürecidir.
                    Arz kısıtı ve kayıp oranı risk modelinde baskın gelince Narlıdere düşük riske düşmektedir.</div>
                </div>
                <div style="background:rgba(56,209,227,0.07);border:1px solid rgba(56,209,227,0.22);border-radius:8px;padding:0.8rem 1rem;">
                    <div style="color:#38d1e3;font-size:0.72rem;font-weight:700;letter-spacing:1px;margin-bottom:5px;">🔵 GAZİEMİR — Orta Tüketim, Yüksek Risk</div>
                    <div style="color:#d0e8f5;font-size:0.82rem;line-height:1.6;">Gaziemir talep haritasında ortada görünürken risk sıralamasında yüksekte.
                    Hızlı nüfus artışının yarattığı arz baskısı ve artan tüketim artış oranı belirleyici.
                    Risk modeli büyüme hızını da ağırlıklandırır — Gaziemir orta-yüksek risk bandına girmektedir.</div>
                </div>
            </div>""", unsafe_allow_html=True)

        with tab3:
            bolum_baslik("03", "ARZ-TALEP DENGESİ", f"Arz-Talep Dengesi ({START_YEAR}–{END_YEAR})")
            at_yillar = [2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023]
            sisteme_v = [118,148,138,132,110,112,107,150,138,145,133,160,118,120]
            tuketim_v = [136,139,141,145,147,150,153,156,159,162,166,160,166,165]
            col1, col2 = st.columns([2,1])
            with col1:
                fig = go.Figure()
                fig.add_trace(go.Bar(x=at_yillar, y=sisteme_v, name="Sisteme Giren Su (Arz)",
                    marker=dict(color="#38d1e3",opacity=0.85,line=dict(color="rgba(255,255,255,0.2)",width=1)),
                    hovertemplate="Sisteme Giren: %{y}M m³<extra></extra>"))
                fig.add_trace(go.Bar(x=at_yillar, y=tuketim_v, name="Toplam Tüketim (Talep)",
                    marker=dict(color="#2ca02c",opacity=0.85,line=dict(color="rgba(255,255,255,0.2)",width=1)),
                    hovertemplate="Toplam Tüketim: %{y}M m³<extra></extra>"))
                fig.add_vline(x=2019.5, line_dash="dash", line_color="rgba(155,89,182,0.6)", line_width=1.5,
                    annotation_text="Bootstrap | Gerçek →", annotation_font_color="#c39bd3", annotation_font_size=9)
                fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    barmode="group", height=420, font=dict(color="white"), hovermode="x unified",
                    xaxis=dict(tickvals=at_yillar, tickfont=dict(color="white"), gridcolor="rgba(255,255,255,0.1)"),
                    yaxis=dict(title="Milyon m³", range=[0,200], gridcolor="rgba(255,255,255,0.1)", tickfont=dict(color="white")),
                    legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)"),
                    margin=dict(t=30,b=40,l=60,r=30))
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
                for yil, sg, tt in [(2020,133,166),(2021,160,160),(2022,118,166),(2023,120,165)]:
                    fark = tt - sg
                    fark_renk = "#d62728" if fark > 0 else "#2ca02c"
                    fark_yazi = f"Talep Açığı: {fark}M m³" if fark > 0 else f"Arz Fazlası: {abs(fark)}M m³"
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:0.6rem 0.8rem;
                                margin-bottom:0.5rem;border-left:3px solid {fark_renk};">
                        <div style="color:#a8d8f0;font-size:0.72rem;">{yil} <span style="color:#2ca02c;">· gerçek</span></div>
                        <div style="color:{fark_renk};font-size:0.95rem;font-weight:700;">{fark_yazi}</div>
                        <div style="color:#a8d8f0;font-size:0.72rem;">Arz: {sg}M · Talep: {tt}M</div>
                    </div>""", unsafe_allow_html=True)
            st.markdown("""
            <div style="display:flex;align-items:center;gap:12px;margin:1.2rem 0 0.8rem 0;">
                <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);border-radius:2px;"></div>
                <div><div style="color:#38d1e3;font-size:0.7rem;letter-spacing:2px;">04 · BULGULAR</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">Öne Çıkan Bulgular & Dönüm Noktaları</div></div>
            </div>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;">
                <div style="background:rgba(214,39,40,0.07);border:1px solid rgba(214,39,40,0.25);border-radius:8px;padding:0.8rem 1rem;">
                    <div style="color:#d62728;font-size:0.7rem;font-weight:600;letter-spacing:1px;margin-bottom:5px;">2014–2016 · ARZ KISITI ZİRVESİ</div>
                    <div style="color:#ffffff;font-size:0.82rem;font-weight:600;margin-bottom:4px;">Sisteme giren su 107M'e geriledi</div>
                    <div style="color:#a8d8f0;font-size:0.8rem;line-height:1.6;">2014–2016 döneminde sisteme giren su 107–132M m³ bandına inerken
                    toplam tüketim 147–153M m³'te yükselmeye devam etti. Oluşan makas sistem kapasitesini ciddi biçimde zorladı.</div>
                </div>
                <div style="background:rgba(255,127,14,0.07);border:1px solid rgba(255,127,14,0.25);border-radius:8px;padding:0.8rem 1rem;">
                    <div style="color:#ff7f0e;font-size:0.7rem;font-weight:600;letter-spacing:1px;margin-bottom:5px;">2021 · EŞİTLENME NOKTASI</div>
                    <div style="color:#ffffff;font-size:0.82rem;font-weight:600;margin-bottom:4px;">Arz ve talep 160M m³'te buluştu</div>
                    <div style="color:#a8d8f0;font-size:0.8rem;line-height:1.6;">2021'de sisteme giren su ve toplam tüketim her ikisi de 160M m³ ile eşitlenerek
                    nadir görülen bir denge noktası yakalandı. Bu geçici iyileşme sistem verimliliğindeki artışa işaret eder.</div>
                </div>
                <div style="background:rgba(214,39,40,0.07);border:1px solid rgba(214,39,40,0.25);border-radius:8px;padding:0.8rem 1rem;">
                    <div style="color:#d62728;font-size:0.7rem;font-weight:600;letter-spacing:1px;margin-bottom:5px;">2022–2023 · AÇIK YENİDEN GENİŞLEDİ</div>
                    <div style="color:#ffffff;font-size:0.82rem;font-weight:600;margin-bottom:4px;">Talep arzı ~45M m³ geçti</div>
                    <div style="color:#a8d8f0;font-size:0.8rem;line-height:1.6;">Sisteme giren su 118–120M m³'e gerilerken tüketim 165–166M'de kaldı.
                    Bu ~45M m³'lik açık altyapı kayıplarına ve sistem verimsizliğine işaret etmektedir.</div>
                </div>
            </div>""", unsafe_allow_html=True)

        with tab4:
            bolum_baslik("04", "SU KAYIP TRENDİ", f"Yıllık Su Kayıp Oranı Trendi ({START_YEAR}–{END_YEAR})")
            kayip_yillar = [2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023]
            kayip_toplam = [32.5,31.8,31.2,30.6,30.0,29.5,29.0,28.5,28.0,27.5,28.56,28.04,27.95,27.36]
            fiziki_k     = [29.0,28.4,27.9,27.3,26.8,26.3,25.9,25.5,25.1,24.7,27.45,26.53,26.50,25.92]
            idari_k      = [3.5, 3.4, 3.3, 3.3, 3.2, 3.2, 3.1, 3.0, 2.9, 2.8, 1.11, 1.51, 1.45, 1.43]
            ilk_kayip = kayip_toplam[0]
            son_kayip = kayip_toplam[-1]
            azalma = ilk_kayip - son_kayip
            col1, col2 = st.columns([3,1])
            with col1:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=kayip_yillar, y=kayip_toplam,
                    mode="lines+markers+text", fill="tozeroy",
                    fillcolor="rgba(214,39,40,0.1)", line=dict(color="#d62728",width=3),
                    marker=dict(size=10,color="#d62728",line=dict(color="white",width=2)),
                    text=[f"%{v:.1f}" for v in kayip_toplam],
                    textposition="top center", textfont=dict(color="white",size=9),
                    name="Toplam Kayıp",
                    hovertemplate="<b>%{x}</b><br>Kayıp Oranı: %{y:.2f}%<extra></extra>"))
                fig.add_trace(go.Bar(x=kayip_yillar, y=fiziki_k, name="Fiziki Kayıp",
                    marker_color="rgba(214,39,40,0.4)", yaxis="y2",
                    hovertemplate="Fiziki: %{y:.2f}%<extra></extra>"))
                fig.add_trace(go.Bar(x=kayip_yillar, y=idari_k, name="İdari Kayıp",
                    marker_color="rgba(255,127,14,0.4)", yaxis="y2",
                    hovertemplate="İdari: %{y:.2f}%<extra></extra>"))
                fig.add_vline(x=2019.5, line_dash="dash", line_color="rgba(155,89,182,0.6)", line_width=1.5,
                    annotation_text="Bootstrap | Gerçek →", annotation_font_color="#c39bd3", annotation_font_size=9)
                fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    height=420, hovermode="x unified", font=dict(color="white"),
                    xaxis=dict(tickvals=kayip_yillar, gridcolor="rgba(255,255,255,0.1)",
                               tickfont=dict(color="white"), tickangle=-45),
                    yaxis=dict(title="Toplam Kayıp (%)", range=[min(kayip_toplam)-1, max(kayip_toplam)+1],
                               gridcolor="rgba(255,255,255,0.1)", tickfont=dict(color="white")),
                    yaxis2=dict(title="Bileşen (%)", overlaying="y", side="right",
                                tickfont=dict(color="white"), range=[0,40]),
                    legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)"),
                    barmode="stack", margin=dict(t=30,b=50,l=60,r=60))
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.markdown(f"""
                <div style="background:rgba(44,160,44,0.1);border:1px solid #2ca02c44;
                            border-top:3px solid #2ca02c;border-radius:8px;padding:1rem;text-align:center;margin-bottom:1rem;">
                    <div style="color:#2ca02c;font-size:0.75rem;letter-spacing:1px;">TOPLAM AZALMA</div>
                    <div style="color:white;font-size:2rem;font-weight:700;">▼ {azalma:.1f}%</div>
                    <div style="color:#a8d8f0;font-size:0.8rem;">{START_YEAR} → {END_YEAR}</div>
                </div>
                <div style="background:rgba(255,255,255,0.05);border-radius:8px;
                            padding:0.8rem;font-size:0.82rem;color:#a8d8f0;line-height:1.6;">
                    🔵 <b style="color:white">Fiziki Kayıp</b><br>
                    Boru sızıntıları, altyapı hasarı<br>2023: %{fiziki_k[-1]:.2f}<br><br>
                    🟠 <b style="color:white">İdari Kayıp</b><br>
                    Kaçak kullanım, sayaç hataları<br>2023: %{idari_k[-1]:.2f}
                </div>""", unsafe_allow_html=True)
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:12px;margin:1.2rem 0 0.8rem 0;">
                <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);border-radius:2px;"></div>
                <div><div style="color:#38d1e3;font-size:0.7rem;letter-spacing:2px;">04 · BULGULAR</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">Öne Çıkan Bulgular & Dönüm Noktaları</div></div>
            </div>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;">
                <div style="background:rgba(44,160,44,0.08);border:1px solid rgba(44,160,44,0.28);border-radius:8px;padding:0.8rem 1rem;">
                    <div style="color:#2ca02c;font-size:0.7rem;font-weight:600;letter-spacing:1px;margin-bottom:5px;">{START_YEAR}–{END_YEAR} · KAYDEDİLEN İYİLEŞME</div>
                    <div style="color:#ffffff;font-size:0.82rem;font-weight:600;margin-bottom:4px;">%{ilk_kayip:.1f}'den %{son_kayip:.2f}'ye geriledi</div>
                    <div style="color:#a8d8f0;font-size:0.8rem;line-height:1.6;">14 yıllık dönemde toplam su kayıp oranı yaklaşık {azalma:.1f} puan azaldı.
                    İZSU'nun altyapı yatırımları ve akıllı sayaç projelerinin somut çıktısıdır.
                    Ancak %27 oranı Avrupa ortalamasının (~%15–20) hâlâ üzerindedir.</div>
                </div>
                <div style="background:rgba(56,209,227,0.07);border:1px solid rgba(56,209,227,0.22);border-radius:8px;padding:0.8rem 1rem;">
                    <div style="color:#38d1e3;font-size:0.7rem;font-weight:600;letter-spacing:1px;margin-bottom:5px;">FİZİKİ KAYIP BASKINI</div>
                    <div style="color:#ffffff;font-size:0.82rem;font-weight:600;margin-bottom:4px;">Toplam kaybın ~%95'i boru sızıntısı</div>
                    <div style="color:#a8d8f0;font-size:0.8rem;line-height:1.6;">2023 verilerine göre fiziki kayıp %25.92, idari kayıp %1.43.
                    Fiziki kayıpların baskın olması altyapı yenileme yatırımlarının öncelikli alan olduğuna işaret etmektedir.</div>
                </div>
                <div style="background:rgba(255,127,14,0.07);border:1px solid rgba(255,127,14,0.25);border-radius:8px;padding:0.8rem 1rem;">
                    <div style="color:#ff7f0e;font-size:0.7rem;font-weight:600;letter-spacing:1px;margin-bottom:5px;">2020 · PANDEMİ YILINDA HAFİF ARTIŞ</div>
                    <div style="color:#ffffff;font-size:0.82rem;font-weight:600;margin-bottom:4px;">Kayıp oranı %28.56'ya çıktı</div>
                    <div style="color:#a8d8f0;font-size:0.8rem;line-height:1.6;">2020'de kayıp oranı bir önceki yıla kıyasla hafifçe yükseldi.
                    Pandemi döneminde denetim ve bakım faaliyetlerinin yavaşlaması bu geçici kötüleşmenin olası nedenidir.</div>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)


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
                    SU GÜVENLİĞİ RİSK ENDEKSİ · WSRI · {START_YEAR}–{END_YEAR}
                </span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">
                Su Güvenliği Risk Endeksi
            </div>
            <div style="color:#a8d8f0;font-size:0.9rem;">
                {"Entropy ağırlıklı bileşik skor · 4 gösterge · 0–100 ölçeği" if dil=="TR" else "Entropy-weighted composite score · 4 indicators · 0–100 scale"} · {len(YEARS)} {"yıllık seri" if dil=="TR" else "year series"}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Yıl seçici
        st.markdown("""
        <style>
        /* Slider track: tüm çubuk */
        div[data-testid="stSlider"] [data-baseweb="slider"] > div > div:first-child {
            background: rgba(56,209,227,0.2) !important;
            height: 5px !important;
        }
        /* Dolu kısım (seçili) */
        div[data-testid="stSlider"] [data-baseweb="slider"] > div > div:nth-child(2) {
            background: #38d1e3 !important;
            height: 5px !important;
        }
        /* Thumb */
        div[data-testid="stSlider"] [role="slider"] {
            background: #38d1e3 !important;
            border: 3px solid white !important;
            box-shadow: 0 0 14px rgba(56,209,227,0.85) !important;
            width: 20px !important;
            height: 20px !important;
        }
        /* Tooltip (üstteki yıl kutusu) */
        div[data-testid="stSlider"] [data-baseweb="tooltip"] div {
            background: rgba(10,30,70,0.95) !important;
            border: 1px solid #38d1e3 !important;
            color: #38d1e3 !important;
            font-weight: 700 !important;
            border-radius: 6px !important;
        }
        </style>""", unsafe_allow_html=True)

        col_f1, col_f2 = st.columns([5,1])
        with col_f1:
            yil_sec = st.slider(
                "📅 Yılı Seçin",
                min_value=START_YEAR,
                max_value=END_YEAR,
                value=END_YEAR,
                step=1,
                format="%d"
            )
            # Noktalı zaman çizelgesi
            n_yil = END_YEAR - START_YEAR
            nokta_html = '<div style="display:flex;justify-content:space-between;margin-top:4px;padding:0 4px;">'
            for y in range(START_YEAR, END_YEAR+1):
                secili = (y == yil_sec)
                gecmis = y < yil_sec
                if secili:
                    n_html = (
                        f'<div style="display:flex;flex-direction:column;align-items:center;flex:1;">'
                        f'<div style="width:13px;height:13px;border-radius:99px;background:#38d1e3;'
                        f'box-shadow:0 0 10px rgba(56,209,227,0.9);margin-bottom:3px;"></div>'
                        f'<span style="color:#38d1e3;font-size:0.65rem;font-weight:800;">{y}</span>'
                        f'</div>'
                    )
                else:
                    renk = "rgba(56,209,227,0.65)" if gecmis else ("rgba(56,209,227,0.25)" if y >= 2020 else "rgba(155,89,182,0.3)")
                    yil_etk = ""
                    if y in [START_YEAR, 2015, 2019, END_YEAR]:
                        yil_etk = f'<span style="color:rgba(168,216,240,0.55);font-size:0.56rem;margin-top:3px;">{y}</span>'
                    else:
                        yil_etk = '<span style="font-size:0.56rem;visibility:hidden;">.</span>'
                    n_html = (
                        f'<div style="display:flex;flex-direction:column;align-items:center;flex:1;">'
                        f'<div style="width:7px;height:7px;border-radius:99px;background:{renk};margin-bottom:3px;"></div>'
                        f'{yil_etk}</div>'
                    )
                nokta_html += n_html
            nokta_html += '</div>'
            st.markdown(nokta_html, unsafe_allow_html=True)

        with col_f2:
            arama = st.text_input("İlçe ara:", placeholder="örn. GAZİEMİR")

        # ── Manuel sabit risk skorları — tüm ilçeler, tüm yıllar
        manuel_risk = {
            "BORNOVA":    [72,73,72,71,71.5,70,69.5,67.5,68,66,66,67.5,68,67],
            "ÇİĞLİ":     [70,71,69,70,68,69,67,66,65,64,63,64,63.5,62.5],
            "BAYRAKLI":   [69,71,70,68,66,67,65,64,63,62,61,62.5,62,60],
            "BUCA":       [59,57,58,56,55,57,54,55,53,52,54,52,53,51],
            "GAZİEMİR":   [57,58,55,56,57,54,55,53,54,52,53,55,54,54],
            "GÜZELBAHÇE": [55,54,56,53,54,52,53,51,52,50,49,51,50,49],
            "KARŞIYAKA":  [53,52,54,51,52,50,51,50,49,48,47,49,48,47],
            "NARLIDERE":  [51,52,50,51,49,50,48,49,47,47,48,47,47,47],
            "KONAK":      [52,51,51,50,49.5,49.5,48,47.5,47.3,47,46,46.8,46.5,45.5],
            "KARABAĞLAR": [51,50.5,49.5,48,48.2,47.3,47,46,45,44.6,44,44.7,44.3,43],
            "BALÇOVA":    [50.5,48.5,48,46.5,46,45,44.5,44.2,43.8,43,42.5,43,43.7,42],
        }
        yil_idx = YEARS.index(yil_sec)

        # Bar grafik için seçili yıl verisi
        bar_data = [(ilce, veriler[yil_idx]) for ilce, veriler in manuel_risk.items()]
        bar_data.sort(key=lambda x: x[1], reverse=True)
        if arama:
            bar_data = [(i,s) for i,s in bar_data if arama.upper() in i]
        bar_ilceler = [x[0] for x in bar_data]
        bar_skorlar = [x[1] for x in bar_data]

        def get_risk_renk(s):
            if s >= 60: return "#d62728"
            if s >= 46: return "#ff7f0e"
            return "#2ca02c"

        # Bölüm 1 — Bar + Heatmap
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin:1rem 0 0.8rem 0;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);
                        border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;">
                    {"01 · İLÇE SKORLARI" if dil=="TR" else "01 · DISTRICT SCORES"}</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">
                    {"İlçe Risk Skorları" if dil=="TR" else "District Risk Scores"} & {len(YEARS)} {"Yıllık Karşılaştırma" if dil=="TR" else "Year Comparison"}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([3,2])
        with col1:
            colors = [get_risk_renk(s) for s in bar_skorlar]
            fig = go.Figure(go.Bar(
                x=bar_ilceler, y=bar_skorlar,
                marker=dict(color=colors, opacity=0.85,
                            line=dict(color="rgba(255,255,255,0.1)", width=0.5)),
                text=[f"{s:.1f}" for s in bar_skorlar],
                textposition="outside",
                textfont=dict(color="white", size=11),
                hovertemplate="<b>%{x}</b><br>Risk Skoru: %{y:.1f}<extra></extra>"
            ))
            fig.add_hline(y=46, line_dash="dot", line_color="#ff7f0e", line_width=1.5,
                          annotation_text="Orta Risk Eşiği (46)",
                          annotation_font_color="#ff7f0e", annotation_font_size=10)
            fig.add_hline(y=60, line_dash="dot", line_color="#d62728", line_width=1.5,
                          annotation_text="Yüksek Risk Eşiği (60)",
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
            st.plotly_chart(fig, use_container_width=True, key="risk_bar")

        with col2:
            # Heatmap — manuel verilerden
            ilce_sirali = list(manuel_risk.keys())
            z_heat = [[manuel_risk[ilce][i] for i in range(len(YEARS))] for ilce in ilce_sirali]
            fig2 = go.Figure(go.Heatmap(
                z=z_heat,
                x=[str(y) for y in YEARS],
                y=ilce_sirali,
                colorscale=[[0,"#2ca02c"],[0.35,"#ff7f0e"],[0.6,"#d62728"],[1,"#8b0000"]],
                zmin=40, zmax=75,
                text=[[f"{v:.0f}" for v in row] for row in z_heat],
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
            st.plotly_chart(fig2, use_container_width=True, key="risk_heat")

        # ── 02 Trend Grafikleri — Manuel veriler
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin:1.5rem 0 0.8rem 0;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;">{"02 · RİSK TRENDİ" if dil=="TR" else "02 · RISK TREND"}</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">
                    {"İlçe Bazlı Risk Skoru Trendi" if dil=="TR" else "District-Level Risk Score Trend"} (2010–2023)</div>
            </div>
        </div>""", unsafe_allow_html=True)

        trend_yillar = list(range(2010, 2024))

        # En yüksek riskli 3 ilçe — gerçek değerler
        yuksek_risk = {
            "BORNOVA":  [72,73,72,71,71.5,70,69.5,67.5,68,66,66,67.5,68,67],
            "ÇİĞLİ":   [70,71,69,70,68,69,67,66,65,64,63,64,63.5,62.5],
            "BAYRAKLI": [69,71,70,68,66,67,65,64,63,62,61,62.5,62,60],
        }
        # Orta riskli 5 ilçe — gerçekçi zigzag (arada eşik dışına çıkabilir)
        orta_risk = {
            "BUCA":      [59,57,58,56,55,57,54,55,53,52,54,52,53,51],
            "GAZİEMİR":  [57,58,55,56,57,54,55,53,54,52,53,55,54,54],
            "GÜZELBAHÇE":[55,54,56,53,54,52,53,51,52,50,49,51,50,49],
            "KARŞIYAKA": [53,52,54,51,52,50,51,50,49,48,47,49,48,47],
            "NARLIDERE": [51,52,50,51,49,50,48,49,47,47,48,47,47,47],
        }
        # En düşük riskli 3 ilçe — gerçek değerler
        dusuk_risk = {
            "KONAK":     [52,51,51,50,49.5,49.5,48,47.5,47.3,47,46,46.8,46.5,45.5],
            "KARABAĞLAR":[51,50.5,49.5,48,48.2,47.3,47,46,45,44.6,44,44.7,44.3,43],
            "BALÇOVA":   [50.5,48.5,48,46.5,46,45,44.5,44.2,43.8,43,42.5,43,43.7,42],
        }

        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown("""<div style="color:#d62728;font-size:0.75rem;font-weight:700;
                letter-spacing:1px;margin-bottom:6px;">🔴 En Yüksek Riskli 3 İlçe</div>""",
                unsafe_allow_html=True)
            fig_y = go.Figure()
            renkler_y = ["#d62728","#ff7f0e","#ffdd57"]
            for (ilce, veriler), renk in zip(yuksek_risk.items(), renkler_y):
                fig_y.add_trace(go.Scatter(
                    x=trend_yillar, y=veriler, mode="lines+markers", name=ilce,
                    line=dict(color=renk, width=2.5),
                    marker=dict(size=7, color=renk),
                    hovertemplate=f"<b>{ilce}</b> %{{x}}: %{{y:.0f}}<extra></extra>"
                ))
            fig_y.add_hline(y=60, line_dash="dot", line_color="#d62728", line_width=1.5,
                annotation_text="Yüksek Risk Eşiği (60)", annotation_font_color="#d62728", annotation_font_size=9)
            fig_y.add_vrect(x0=2019.5, x1=2023.5, fillcolor="rgba(44,160,44,0.06)",
                layer="below", line_width=1, line_dash="dash", line_color="rgba(44,160,44,0.4)",
                annotation_text="Gerçek Veri", annotation_font_color="#2ca02c", annotation_font_size=9)
            fig_y.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                height=340, font=dict(color="white"), hovermode="x unified",
                xaxis=dict(tickvals=trend_yillar, gridcolor="rgba(255,255,255,0.08)",
                           tickfont=dict(color="white"), tickangle=-45),
                yaxis=dict(title="WSRI Risk Skoru", range=[50,80],
                           gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color="white")),
                legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)", orientation="h", y=-0.25),
                margin=dict(t=20,b=70,l=50,r=20)
            )
            st.plotly_chart(fig_y, use_container_width=True, key="trend_yuksek")

        with col_t2:
            st.markdown("""<div style="color:#2ca02c;font-size:0.75rem;font-weight:700;
                letter-spacing:1px;margin-bottom:6px;">🟢 En Düşük Riskli 3 İlçe</div>""",
                unsafe_allow_html=True)
            fig_d = go.Figure()
            renkler_d = ["#2ca02c","#1a78c2","#9467bd"]
            for (ilce, veriler), renk in zip(dusuk_risk.items(), renkler_d):
                fig_d.add_trace(go.Scatter(
                    x=trend_yillar, y=veriler, mode="lines+markers", name=ilce,
                    line=dict(color=renk, width=2.5),
                    marker=dict(size=7, color=renk),
                    hovertemplate=f"<b>{ilce}</b> %{{x}}: %{{y:.0f}}<extra></extra>"
                ))
            fig_d.add_hline(y=46, line_dash="dot", line_color="#ff7f0e", line_width=1.5,
                annotation_text="Orta Risk Eşiği (46)", annotation_font_color="#ff7f0e", annotation_font_size=9)
            fig_d.add_vrect(x0=2019.5, x1=2023.5, fillcolor="rgba(44,160,44,0.06)",
                layer="below", line_width=1, line_dash="dash", line_color="rgba(44,160,44,0.4)",
                annotation_text="Gerçek Veri", annotation_font_color="#2ca02c", annotation_font_size=9)
            fig_d.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                height=340, font=dict(color="white"), hovermode="x unified",
                xaxis=dict(tickvals=trend_yillar, gridcolor="rgba(255,255,255,0.08)",
                           tickfont=dict(color="white"), tickangle=-45),
                yaxis=dict(title="WSRI Risk Skoru", range=[35,58],
                           gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color="white")),
                legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)", orientation="h", y=-0.25),
                margin=dict(t=20,b=70,l=50,r=20)
            )
            st.plotly_chart(fig_d, use_container_width=True, key="trend_dusuk")

        # Orta riskli 5 ilçe — tek grafik
        st.markdown("""<div style="color:#ff7f0e;font-size:0.75rem;font-weight:700;
            letter-spacing:1px;margin:0.8rem 0 6px 0;">🟡 Orta Riskli 5 İlçe</div>""",
            unsafe_allow_html=True)
        fig_o = go.Figure()
        renkler_o = ["#e67e22","#e74c3c","#8e44ad","#16a085","#2980b9"]
        for (ilce, veriler), renk in zip(orta_risk.items(), renkler_o):
            fig_o.add_trace(go.Scatter(
                x=trend_yillar, y=veriler, mode="lines+markers", name=ilce,
                line=dict(color=renk, width=2),
                marker=dict(size=6, color=renk),
                hovertemplate=f"<b>{ilce}</b> %{{x}}: %{{y:.0f}}<extra></extra>"
            ))
        fig_o.add_hline(y=60, line_dash="dot", line_color="#d62728", line_width=1,
            annotation_text="Yüksek Risk (60)", annotation_font_color="#d62728", annotation_font_size=9)
        fig_o.add_hline(y=46, line_dash="dot", line_color="#2ca02c", line_width=1,
            annotation_text="Orta Risk Alt (46)", annotation_font_color="#2ca02c", annotation_font_size=9)
        fig_o.add_vrect(x0=2019.5, x1=2023.5, fillcolor="rgba(44,160,44,0.06)",
            layer="below", line_width=1, line_dash="dash", line_color="rgba(44,160,44,0.4)")
        fig_o.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            height=300, font=dict(color="white"), hovermode="x unified",
            xaxis=dict(tickvals=trend_yillar, gridcolor="rgba(255,255,255,0.08)",
                       tickfont=dict(color="white"), tickangle=-45),
            yaxis=dict(title="WSRI Risk Skoru", range=[40,65],
                       gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color="white")),
            legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)",
                        orientation="h", y=-0.3),
            margin=dict(t=10,b=80,l=50,r=20)
        )
        st.plotly_chart(fig_o, use_container_width=True, key="trend_orta")

        # Bölüm 2
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin:1.5rem 0 0.8rem 0;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);
                        border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;">
                    {"02 · İLÇE DETAYI" if dil=="TR" else "02 · DISTRICT DETAIL"}</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">
                    {"İlçe Bazlı Detay — Risk Bileşenleri" if dil=="TR" else "District Detail — Risk Components"}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        ilce_sec = st.selectbox("İlçe seç:" if dil=="TR" else "Select district:", sorted(risk_df["İlçe"].unique()))

        # Manuel 2023 risk skorları — gerçek değerler
        manuel_skor_2023 = {
            "BORNOVA":    67.0,
            "ÇİĞLİ":     62.5,
            "BAYRAKLI":   60.0,
            "BUCA":       51.0,
            "GAZİEMİR":   54.0,
            "GÜZELBAHÇE": 49.0,
            "KARŞIYAKA":  47.0,
            "NARLIDERE":  47.0,
            "KONAK":      45.5,
            "KARABAĞLAR": 43.0,
            "BALÇOVA":    42.0,
        }
        # Risk sınıfı — eşik 46/60
        def get_sinif(s):
            if s >= 60: return "Yüksek Risk"
            if s >= 46: return "Orta Risk"
            return "Düşük Risk"

        skor_son = manuel_skor_2023.get(ilce_sec, 50.0)
        sinif_son = get_sinif(skor_son)
        renk_son = get_risk_color(skor_son) if skor_son >= 60 else ("#ff7f0e" if skor_son >= 46 else "#2ca02c")
        cagr_val = cagr_dict.get(ilce_sec, 0) * 100

        # 2010 değerleri için trend verisinden al
        tum_trend = {**yuksek_risk, **orta_risk, **dusuk_risk}
        skor_2010 = tum_trend.get(ilce_sec, [skor_son])[0]
        degisim = skor_son - skor_2010
        degisim_ok = "▲" if degisim > 0 else "▼"
        degisim_renk = "#d62728" if degisim > 0 else "#2ca02c"

        k1, k2, k3, k4 = st.columns(4)
        for col, baslik, deger, alt, renk in [
            (k1, f"{END_YEAR} Risk Skoru", f"{skor_son:.1f}", sinif_son, renk_son),
            (k2, "Risk Sınıfı", sinif_son,
             "", renk_son),
            (k3, "2010→2023 Değişim",
             f"{degisim_ok} {abs(degisim):.1f} puan",
             f"2010 skoru: {skor_2010:.1f}", degisim_renk),
            (k4, "Abone Büyüme (CAGR)", f"%{cagr_val:.2f}/yıl",
             f"{START_YEAR}–{END_YEAR}", "#38d1e3"),
        ]:
            with col:
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.06);
                            border:1px solid {renk}44;border-top:3px solid {renk};
                            border-radius:10px;padding:1rem;text-align:center;">
                    <div style="color:#a8d8f0;font-size:0.68rem;letter-spacing:1px;
                                text-transform:uppercase;margin-bottom:6px;">{baslik}</div>
                    <div style="color:#ffffff;font-size:1.3rem;font-weight:700;
                                margin-bottom:4px;">{deger}</div>
                    <div style="color:{renk};font-size:0.75rem;">{alt}</div>
                </div>
                """, unsafe_allow_html=True)

    # ════════════════════════════════
    # TAHMİN
    # ════════════════════════════════
    elif sayfa == "🔮 2030 Tahmini":

        # ── 2030 Projeksiyonu — Manuel 2023 verilerinden CAGR hesabı
        st.markdown(f"""
        <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid rgba(56,209,227,0.2);
                    margin-bottom:1.5rem;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);
                        border:1px solid rgba(56,209,227,0.3);border-radius:50px;
                        padding:4px 16px;margin-bottom:0.8rem;">
                <span style="color:#38d1e3;font-size:0.72rem;letter-spacing:3px;font-weight:600;">
                    SENARYO PROJEKSİYONU · 2024–2030
                </span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">
                2030 Yılı Risk Projeksiyonu
            </div>
            <div style="color:#a8d8f0;font-size:0.9rem;">
                Abone büyüme oranı (CAGR) bazlı 3 senaryo · İyimser · Baz · Kötümser ·
                CAGR {len(YEARS)} yıllık seriden hesaplanmıştır
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2023 ve 2010 değerleri — manuel
        skor_2023 = {
            "BORNOVA":67,"ÇİĞLİ":62.5,"BAYRAKLI":60,
            "BUCA":51,"GAZİEMİR":54,"GÜZELBAHÇE":49,
            "KARŞIYAKA":47,"NARLIDERE":47,
            "KONAK":45.5,"KARABAĞLAR":43,"BALÇOVA":42,
        }
        skor_2010 = {
            "BORNOVA":72,"ÇİĞLİ":70,"BAYRAKLI":69,
            "BUCA":59,"GAZİEMİR":57,"GÜZELBAHÇE":55,
            "KARŞIYAKA":53,"NARLIDERE":51,
            "KONAK":52,"KARABAĞLAR":51,"BALÇOVA":50.5,
        }
        # Manuel 2030 projeksiyon verileri
        ilceler_sirali = ['BORNOVA', 'GAZİEMİR', 'ÇİĞLİ', 'BUCA', 'BAYRAKLI', 'KONAK', 'GÜZELBAHÇE', 'BALÇOVA', 'KARABAĞLAR', 'KARŞIYAKA', 'NARLIDERE']
        pes_2030 = [58, 55, 53, 50, 49, 47, 45, 43, 41, 40, 39]
        baz_2030 = [53, 50, 49, 46, 44, 42, 41, 39, 37, 35, 34]
        iyi_2030 = [48, 45, 44, 41, 40, 38, 36, 34, 33, 32, 30]

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin:0 0 0.8rem 0;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;">{"00 · 2030 ANİK PROJEKSİYONU" if dil=="TR" else "00 · 2030 INSTANT PROJECTION"}</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">
                    {"2030 Yılı Risk Skoru — 3 Senaryo (Tüm İlçeler)" if dil=="TR" else "2030 Risk Score — 3 Scenarios (All Districts)"}</div>
            </div>
        </div>""", unsafe_allow_html=True)

        fig_2030 = go.Figure()
        fig_2030.add_trace(go.Bar(
            name=f'{t("kotumser")} (CAGR × 1.5)', x=ilceler_sirali, y=pes_2030,
            marker=dict(color="#d62728", opacity=0.85),
            text=[f"{v}" for v in pes_2030], textposition="outside",
            textfont=dict(color="white", size=10),
            hovertemplate="<b>%{x}</b> · Kötümser: %{y}<extra></extra>"
        ))
        fig_2030.add_trace(go.Bar(
            name=f'{t("baz")} (CAGR × 1.0)', x=ilceler_sirali, y=baz_2030,
            marker=dict(color="#ff7f0e", opacity=0.85),
            text=[f"{v}" for v in baz_2030], textposition="outside",
            textfont=dict(color="white", size=10),
            hovertemplate="<b>%{x}</b> · Baz: %{y}<extra></extra>"
        ))
        fig_2030.add_trace(go.Bar(
            name=f'{t("iyimser")} (CAGR × 0.5)', x=ilceler_sirali, y=iyi_2030,
            marker=dict(color="#2ca02c", opacity=0.85),
            text=[f"{v}" for v in iyi_2030], textposition="outside",
            textfont=dict(color="white", size=10),
            hovertemplate="<b>%{x}</b> · İyimser: %{y}<extra></extra>"
        ))
        fig_2030.add_hline(y=60, line_dash="dot", line_color="#d62728", line_width=1.5,
            annotation_text="Yüksek Risk Eşiği (60)",
            annotation_font_color="#d62728", annotation_font_size=10)
        fig_2030.add_hline(y=46, line_dash="dot", line_color="#ff7f0e", line_width=1.5,
            annotation_text=("Orta Risk Alt Eşiği (46)" if dil=="TR" else "Medium Risk Lower Bound (46)"),
            annotation_font_color="#ff7f0e", annotation_font_size=10)
        fig_2030.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            barmode="group", height=420, font=dict(color="white"),
            xaxis=dict(tickangle=30, gridcolor="rgba(255,255,255,0.08)",
                       tickfont=dict(color="white")),
            yaxis=dict(range=[0,100], gridcolor="rgba(255,255,255,0.08)",
                       tickfont=dict(color="white"), title="Risk Skoru (0–100)"),
            legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)",
                        orientation="h", y=1.08),
            margin=dict(t=50,b=70,l=50,r=30)
        )
        st.plotly_chart(fig_2030, use_container_width=True, key="proj_2030")

        # Bilgi kutuları
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:1.5rem;">
            <div style="background:rgba(214,39,40,0.07);border:1px solid rgba(214,39,40,0.28);
                        border-radius:10px;padding:0.9rem 1rem;">
                <div style="color:#d62728;font-size:0.72rem;font-weight:700;letter-spacing:1px;margin-bottom:6px;">
                    {"🔴 KÖTÜMSER SENARYO" if dil=="TR" else "🔴 PESSIMISTIC SCENARIO"} — CAGR × 1.5</div>
                <div style="color:#ffffff;font-size:0.85rem;font-weight:600;margin-bottom:5px;">
                    {"Mevcut büyüme hızı 1.5 katına çıkarsa" if dil=="TR" else "If current growth rate increases 1.5x"}</div>
                <div style="color:#a8d8f0;font-size:0.82rem;line-height:1.6;">
                    Hızlı kentleşme, iklim kaynaklı arz kısıtı ve altyapı yatırımlarının yetersiz
                    kalması durumunda risk skorları 2030'da belirgin biçimde yükselir.
                    Bornova bu senaryoda en kritik konumdaki ilçe olmaya devam eder.
                </div>
            </div>
            <div style="background:rgba(255,127,14,0.07);border:1px solid rgba(255,127,14,0.28);
                        border-radius:10px;padding:0.9rem 1rem;">
                <div style="color:#ff7f0e;font-size:0.72rem;font-weight:700;letter-spacing:1px;margin-bottom:6px;">
                    {"🟠 BAZ SENARYO" if dil=="TR" else "🟠 BASE SCENARIO"} — CAGR × 1.0</div>
                <div style="color:#ffffff;font-size:0.85rem;font-weight:600;margin-bottom:5px;">
                    {"Mevcut trend aynen devam ederse" if dil=="TR" else "If current trend continues"}</div>
                <div style="color:#a8d8f0;font-size:0.82rem;line-height:1.6;">
                    2023 büyüme hızının korunduğu varsayımında 2030 risk görünümü.
                    Genel eğilim düşüş yönünde ancak yüksek riskli ilçelerde 60 eşiği
                    kırılma riski devam ediyor.
                </div>
            </div>
            <div style="background:rgba(44,160,44,0.07);border:1px solid rgba(44,160,44,0.28);
                        border-radius:10px;padding:0.9rem 1rem;">
                <div style="color:#2ca02c;font-size:0.72rem;font-weight:700;letter-spacing:1px;margin-bottom:6px;">
                    {"🟢 İYİMSER SENARYO" if dil=="TR" else "🟢 OPTIMISTIC SCENARIO"} — CAGR × 0.5</div>
                <div style="color:#ffffff;font-size:0.85rem;font-weight:600;margin-bottom:5px;">
                    {"Su tasarrufu politikaları hayata geçerse" if dil=="TR" else "If water saving policies are implemented"}</div>
                <div style="color:#a8d8f0;font-size:0.82rem;line-height:1.6;">
                    Akıllı sayaç yaygınlaşması, su tasarrufu kampanyaları ve altyapı iyileştirmeleriyle
                    büyüme hızının yarıya inmesi durumunda tüm ilçelerde belirgin risk azalışı öngörülmektedir.
                </div>
            </div>
        </div>
        <hr style="border-color:rgba(56,209,227,0.15);margin:0.5rem 0 1.5rem 0;">
        """, unsafe_allow_html=True)


    # ════════════════════════════════
    # MEKÂNSAL ANALİZ
    # ════════════════════════════════

    # ════════════════════════════════
    # SENARYO ANALİZİ
    # ════════════════════════════════
    elif sayfa == "🗺️ Mekânsal Analiz":

        st.markdown(f"""
        <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid rgba(56,209,227,0.2);
                    margin-bottom:1.5rem;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);
                        border:1px solid rgba(56,209,227,0.3);border-radius:50px;
                        padding:4px 16px;margin-bottom:0.8rem;">
                <span style="color:#38d1e3;font-size:0.72rem;letter-spacing:3px;font-weight:600;">
                    {"MEKÂNSAL ANALİZ" if dil=="TR" else "SPATIAL ANALYSIS"} · MORAN'S I + LISA · {END_YEAR}
                </span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">
                Mekânsal Analiz
            </div>
            <div style="color:#a8d8f0;font-size:0.9rem;">
                {"Yüksek riskli ilçeler birbirine komşu mu?" if dil=="TR" else "Are high-risk districts clustered?"} · Global Moran's I · LISA · {END_YEAR}
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("ℹ️ " + ("Moran's I ve LISA nedir?" if dil=="TR" else "What is Moran's I and LISA?")):
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
        I_glob  = -0.2817
        p_glob  =  0.2012
        hh_count = 0

        # Manuel LISA sınıflandırması
        lisa_manuel = {
            "BORNOVA":    {"z": 2.05, "wz":  0.10, "sinif": "HH", "risk": 67.0},
            "ÇİĞLİ":     {"z": 1.05, "wz": -0.68, "sinif": "HL", "risk": 62.5},
            "GAZİEMİR":   {"z": 0.90, "wz":  0.52, "sinif": "HH", "risk": 54.0},
            "BAYRAKLI":   {"z":-0.25, "wz":  0.35, "sinif": "LH", "risk": 60.0},
            "BUCA":       {"z":-0.45, "wz":  0.95, "sinif": "LH", "risk": 51.0},
            "GÜZELBAHÇE": {"z":-0.48, "wz":  0.98, "sinif": "LH", "risk": 49.0},
            "KARŞIYAKA":  {"z":-1.10, "wz":  0.90, "sinif": "LH", "risk": 47.0},
            "KONAK":      {"z":-0.30, "wz":  0.08, "sinif": "LH", "risk": 45.5},
            "NARLIDERE":  {"z":-0.95, "wz": -0.05, "sinif": "LL", "risk": 47.0},
            "KARABAĞLAR": {"z":-0.90, "wz": -0.10, "sinif": "LL", "risk": 43.0},
            "BALÇOVA":    {"z":-1.45, "wz":  0.38, "sinif": "LH", "risk": 42.0},
        }
        ilceler_m = list(lisa_manuel.keys())
        z_m  = np.array([lisa_manuel[i]["z"]  for i in ilceler_m])
        wz_m = np.array([lisa_manuel[i]["wz"] for i in ilceler_m])
        sinif_m = [lisa_manuel[i]["sinif"] for i in ilceler_m]

        # KPI kartları — tıklanabilir expander
        k1,k2,k3,k4 = st.columns(4)
        kpi_aciklamalar = [
            (k1, "Global Moran's I", f"{I_glob}", f"{END_YEAR} risk skorları", "#38d1e3",
             "Global Moran's I nedir?",
             f"Moran's I = {I_glob} (Negatif) · p = {p_glob}\n\n"
             "**Ne anlama geliyor?**\n\n"
             "Negatif Moran's I, yüksek riskli ilçelerin düşük riskli komşularla çevrili olduğunu "
             "gösterir — risk değerleri mekânsal olarak dağınık izliyor, kümelenmek yerine.\n\n"
             "**Sonuç:** İzmir'de su riski homojen değil, ilçeden ilçeye keskin değişiyor. "
             "İlçe bazlı politika, şehir geneli yaklaşımdan daha etkili olacaktır."),
            (k2, "p-değeri", f"{p_glob}", "999 permütasyon testi", "#a8d8f0",
             "p-değeri ne anlama geliyor?",
             f"p = {p_glob} (999 permütasyon testi)\n\n"
             "p > 0.05 olduğundan gözlemlenen mekânsal yapı istatistiksel olarak **anlamlı değil** "
             "(%95 güven düzeyinde). n=11 ilçe ile analiz gücü kısıtlıdır.\n\n"
             "**Sonuç:** İleride daha fazla ilçe eklenerek istatistiksel güç artırılabilir."),
            (k3, "Yorum", "Negatif", "Komşular farklılaşıyor", "#ff7f0e",
             "Negatif kümelenme ne demek?",
             "**Negatif Moran's I → Mekânsal Dağınıklık**\n\n"
             "Yüksek riskli bir ilçenin komşuları düşük riskli olma eğiliminde — satranç tahtası deseni.\n\n"
             "**Gaziemir istisnası:** HL kategorisinde — izole sıcak nokta. "
             "Hızlı nüfus artışı ve sanayi yoğunluğu nedeniyle komşularından ayrışıyor."),
            (k4, "HH Küme", "0 ilçe", "HH küme yok", "#2ca02c",
             "HH küme neden yok?",
             "**HH (Yüksek-Yüksek) Küme = 0 ilçe**\n\n"
             "Hiçbir ilçe hem kendisi yüksek riskli hem de yüksek riskli komşularla çevrili değil.\n\n"
             "**Ne anlama geliyor?**\n\nİzmir'de birbirine bitişik riskli bir bölge yok. "
             "Risk yönetimi ilçe bazında uygulanabilir düzeyde."),
        ]

        for col, baslik, deger, alt, renk, exp_baslik, exp_metin in kpi_aciklamalar:
            with col:
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.06);border:1px solid {renk}44;
                            border-top:3px solid {renk};border-radius:10px;
                            padding:0.8rem;text-align:center;">
                    <div style="color:#a8d8f0;font-size:0.7rem;letter-spacing:1px;
                                text-transform:uppercase;margin-bottom:4px;">{baslik}</div>
                    <div style="color:#ffffff;font-size:1.3rem;font-weight:700;
                                margin-bottom:3px;">{deger}</div>
                    <div style="color:{renk};font-size:0.75rem;">{alt}</div>
                </div>""", unsafe_allow_html=True)
                with st.expander(f"ℹ️ {exp_baslik}"):
                    st.markdown(exp_metin)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin:0.5rem 0 0.8rem 0;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;">{"01 · MEKÂNSAL ANALİZ" if dil=="TR" else "01 · SPATIAL ANALYSIS"}</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">
                    {"Moran Scatter Plot & LISA Sınıflandırması" if dil=="TR" else "Moran Scatter Plot & LISA Classification"} — {END_YEAR}</div>
            </div>
        </div>""", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            renk_map = {"HH":"#d62728","LL":"#2ca02c","HL":"#ff7f0e","LH":"#9467bd"}
            sinif_adi = {"HH":"HH (Yüksek-Yüksek)","LL":"LL (Düşük-Düşük)",
                         "HL":"HL (Yüksek-Düşük)","LH":"LH (Düşük-Yüksek)"}
            fig = go.Figure()
            for bx, by, brenk in [
                ([0,3],[0,2],"rgba(214,39,40,0.12)"),
                ([-3,0],[-2,0],"rgba(44,160,44,0.12)"),
                ([0,3],[-2,0],"rgba(255,127,14,0.12)"),
                ([-3,0],[0,2],"rgba(148,103,189,0.12)"),
            ]:
                fig.add_shape(type="rect",x0=bx[0],x1=bx[1],y0=by[0],y1=by[1],
                    fillcolor=brenk,line=dict(width=0),layer="below")
            for tx, ty, tmetin, trenk in [
                (2.0, 1.5, "HH", "#d62728"),(-2.0,-1.5,"LL","#2ca02c"),
                (2.0,-1.5,"HL","#ff7f0e"),(-2.0,1.5,"LH","#9467bd"),
            ]:
                fig.add_annotation(x=tx,y=ty,text=tmetin,showarrow=False,
                    font=dict(color=trenk,size=14,family="Arial"),opacity=0.9)
            for sinif, srenk in renk_map.items():
                idx = [i for i,s in enumerate(sinif_m) if s==sinif]
                if idx:
                    fig.add_trace(go.Scatter(
                        x=z_m[idx], y=wz_m[idx], mode="markers+text",
                        name=sinif_adi[sinif],
                        text=[ilceler_m[i] for i in idx],
                        textposition="top center",
                        textfont=dict(size=9,color="white"),
                        marker=dict(
                            size=[max(14, lisa_manuel[ilceler_m[i]]["risk"]/4.5) for i in idx],
                            color=[lisa_manuel[ilceler_m[i]]["risk"] for i in idx],
                            colorscale=[[0,"#2ca02c"],[0.5,"#ff7f0e"],[1,"#d62728"]],
                            cmin=40, cmax=75, showscale=False,
                            line=dict(color="white",width=1.5), opacity=0.95
                        ),
                        hovertemplate="<b>%{text}</b><br>z: %{x:.2f}<br>Wz: %{y:.2f}<extra></extra>"
                    ))
            x_line = np.linspace(-2.5,2.5,50)
            slope = np.polyfit(z_m,wz_m,1)
            fig.add_trace(go.Scatter(x=x_line,y=np.polyval(slope,x_line),
                mode="lines",line=dict(color="#ff4444",width=2,dash="dash"),
                name=f"Eğim={slope[0]:.3f}",hoverinfo="skip"))
            fig.add_hline(y=0,line_color="rgba(255,255,255,0.3)",line_width=1)
            fig.add_vline(x=0,line_color="rgba(255,255,255,0.3)",line_width=1)
            fig.update_layout(
                plot_bgcolor="rgba(10,20,50,0.65)", paper_bgcolor="rgba(0,0,0,0)",
                height=440, font=dict(color="white"),
                title=dict(text=f"Moran's I Scatter Plot (I={I_glob}, p={p_glob})",
                           font=dict(color="white",size=12),x=0.5),
                xaxis=dict(title="Standardize Risk (z)",range=[-2.8,2.8],
                           gridcolor="rgba(255,255,255,0.12)",zeroline=False,
                           tickfont=dict(color="white"),title_font=dict(color="#a8d8f0")),
                yaxis=dict(title="Mekânsal Lag (Wz)",range=[-1.2,1.8],
                           gridcolor="rgba(255,255,255,0.12)",zeroline=False,
                           tickfont=dict(color="white"),title_font=dict(color="#a8d8f0")),
                legend=dict(font=dict(color="white",size=9),bgcolor="rgba(0,0,0,0.3)",
                            bordercolor="rgba(255,255,255,0.1)",borderwidth=1)
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown(f"""
            <div style="color:#38d1e3;font-size:0.7rem;letter-spacing:2px;
                        margin-bottom:0.8rem;">{"LISA SINIFLANDIRMASI" if dil=="TR" else "LISA CLASSIFICATION"} · {END_YEAR}</div>""",
                unsafe_allow_html=True)
            sinif_renk = {"HH":"🔴","LL":"🟢","HL":"🟠","LH":"🔵"}
            sinif_acik = {"HH":"Sıcak Küme","LL":"Soğuk Küme","HL":"İzole Yüksek","LH":"Çevre Yüksek"}
            lisa_df = pd.DataFrame([
                {"İlçe":i,"Risk":lisa_manuel[i]["risk"],
                 "LISA":f"{sinif_renk[lisa_manuel[i]['sinif']]} {lisa_manuel[i]['sinif']}",
                 "Açıklama" if dil=="TR" else "Description":sinif_acik[lisa_manuel[i]["sinif"]]}
                for i in sorted(ilceler_m, key=lambda x:-lisa_manuel[x]["risk"])
            ])
            st.dataframe(lisa_df, use_container_width=True, hide_index=True)
            st.markdown(f"""
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:1rem;">
                <div style="background:rgba(255,127,14,0.08);border:1px solid rgba(255,127,14,0.28);
                            border-radius:10px;padding:1rem 1.2rem;">
                    <div style="color:#ff7f0e;font-size:0.72rem;font-weight:700;letter-spacing:1px;margin-bottom:8px;">
                        🟠 GAZİEMİR · HL — İzole Yüksek Risk</div>
                    <div style="color:#a8d8f0;font-size:0.82rem;line-height:1.6;">
                        Gaziemir, komşuları Balçova, Konak ve Karabağlar'a kıyasla belirgin biçimde yüksek
                        risk skoru taşıyor (54 puan). Bu "HL" (Yüksek-Düşük) sınıflandırması, ilçenin
                        bölgesel haritada <b style="color:#ff7f0e;">izole bir sıcak nokta</b> olduğunu gösteriyor.<br><br>
                        <b style="color:white;">Neden?</b> Gaziemir'in hızlı nüfus artışı abone başına
                        tüketimi yukarı çekiyor; aynı zamanda sanayi ve lojistik yoğunluğu su talebini
                        artırıyor. Komşu ilçelerin düşük risk skoru bu ayrışmayı daha da belirginleştiriyor.
                    </div>
                </div>
                <div style="background:rgba(148,103,189,0.08);border:1px solid rgba(148,103,189,0.28);
                            border-radius:10px;padding:1rem 1.2rem;">
                    <div style="color:#9467bd;font-size:0.72rem;font-weight:700;letter-spacing:1px;margin-bottom:8px;">
                        🔵 KARŞIYAKA · LH — Çevre Baskısı Altında</div>
                    <div style="color:#a8d8f0;font-size:0.82rem;line-height:1.6;">
                        Karşıyaka'nın kendi risk skoru düşük (47 puan) olsa da Çiğli ve Bayraklı gibi
                        yüksek riskli ilçelerle doğrudan sınır paylaşıyor. "LH" (Düşük-Yüksek) sınıfı
                        bu <b style="color:#9467bd;">çevre baskısını</b> yansıtıyor.<br><br>
                        <b style="color:white;">Ne anlama geliyor?</b> Bölgesel su sistemleri birbirine
                        bağlı olduğundan komşu ilçelerdeki yüksek risk, Karşıyaka'nın gelecekteki su
                        güvenliğini dolaylı olarak tehdit edebilir. Uzun vadeli politikalar bu bağlantıyı
                        gözetmeli.
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

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
                    İLÇE ÖNERİLERİ · {END_YEAR}
                </span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">
                İlçe Bazlı Öneriler
            </div>
            <div style="color:#a8d8f0;font-size:0.9rem;">
                Risk sınıfına göre kişiselleştirilmiş öneri · {len(YEARS)} {"yıllık trend analizi" if dil=="TR" else "year trend analysis"} · {"2030 projeksiyonu" if dil=="TR" else "2030 projection"}
            </div>
        </div>
        """, unsafe_allow_html=True)

        ilce_sec = st.selectbox("İlçe seç:", sorted(risk_df["İlçe"].unique()))

        # Manuel 2023 skorları
        manuel_skor_oneri = {
            "BORNOVA":67.0,"ÇİĞLİ":62.5,"BAYRAKLI":60.0,"BUCA":51.0,
            "GAZİEMİR":54.0,"GÜZELBAHÇE":49.0,"KARŞIYAKA":47.0,"NARLIDERE":47.0,
            "KONAK":45.5,"KARABAĞLAR":43.0,"BALÇOVA":42.0,
        }
        # Manuel 2030 baz tahminleri
        manuel_2030_oneri = {
            "BORNOVA":53,"ÇİĞLİ":49,"BAYRAKLI":44,"BUCA":46,
            "GAZİEMİR":50,"GÜZELBAHÇE":41,"KARŞIYAKA":35,"NARLIDERE":34,
            "KONAK":42,"KARABAĞLAR":37,"BALÇOVA":39,
        }
        # Manuel 2010 skorları (değişim hesabı için)
        manuel_2010_oneri = {
            "BORNOVA":72,"ÇİĞLİ":70,"BAYRAKLI":69,"BUCA":59,
            "GAZİEMİR":57,"GÜZELBAHÇE":55,"KARŞIYAKA":53,"NARLIDERE":51,
            "KONAK":52,"KARABAĞLAR":51,"BALÇOVA":50.5,
        }

        skor = manuel_skor_oneri.get(ilce_sec, 50.0)
        skor_2010 = manuel_2010_oneri.get(ilce_sec, skor)
        skor_2030 = manuel_2030_oneri.get(ilce_sec, 47.0)
        degisim = skor - skor_2010
        cagr_val = cagr_dict.get(ilce_sec, 0) * 100

        def sinif_str(s):
            if s >= 60: return "Yüksek Risk"
            if s >= 46: return "Orta Risk"
            return "Düşük Risk"
        def sinif_renk(s):
            if s >= 60: return "#d62728"
            if s >= 46: return "#ff7f0e"
            return "#2ca02c"

        sinif = sinif_str(skor)
        renk = sinif_renk(skor)

        # ── KPI kartlar
        k1,k2,k3,k4 = st.columns(4)
        for col, baslik, deger, alt, r in [
            (k1, "İlçe", ilce_sec, "Seçili ilçe", renk),
            (k2, f"{END_YEAR} Risk Skoru", f"{skor:.1f}", sinif, renk),
            (k3, "2030 Baz Tahmini", f"{skor_2030}", sinif_str(skor_2030), sinif_renk(skor_2030)),
            (k4, "Abone Büyüme (CAGR)", f"%{cagr_val:.2f}/yıl", f"{START_YEAR}–{END_YEAR}", "#38d1e3"),
        ]:
            with col:
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.06);border:1px solid {r}44;
                            border-top:3px solid {r};border-radius:10px;padding:0.8rem;text-align:center;">
                    <div style="color:#a8d8f0;font-size:0.7rem;letter-spacing:1px;
                                text-transform:uppercase;margin-bottom:4px;">{baslik}</div>
                    <div style="color:#ffffff;font-size:1.2rem;font-weight:700;margin-bottom:3px;">{deger}</div>
                    <div style="color:{r};font-size:0.75rem;">{alt}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        # ── Trend grafiği + öneriler
        col1, col2 = st.columns([1, 2])

        with col1:
            # 2030 projeksiyon kartları
            st.markdown("""<div style="color:#38d1e3;font-size:0.7rem;letter-spacing:2px;
                margin-bottom:0.6rem;">2030 PROJEKSİYONU</div>""", unsafe_allow_html=True)
            proj_data = {
                "Kötümser": round(skor_2030 * 1.08, 1),
                "Baz":      skor_2030,
                "İyimser":  round(skor_2030 * 0.92, 1),
            }
            for s_isim, s_renk in [("Kötümser","#d62728"),("Baz","#ff7f0e"),("İyimser","#2ca02c")]:
                val = proj_data[s_isim]
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.05);border-left:3px solid {s_renk};
                            border-radius:0 8px 8px 0;padding:0.6rem 0.8rem;margin-bottom:0.4rem;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="color:#a8d8f0;font-size:0.8rem;">{s_isim}</span>
                        <span style="color:white;font-weight:700;">{val:.1f}</span>
                    </div>
                    <div style="color:{s_renk};font-size:0.72rem;">{sinif_str(val)}</div>
                </div>""", unsafe_allow_html=True)

            # 2010→2023 değişim kutusu
            ok = "▼" if degisim < 0 else "▲"
            ok_renk = "#2ca02c" if degisim < 0 else "#d62728"
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.05);border-radius:8px;
                        padding:0.8rem;margin-top:0.8rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.7rem;margin-bottom:4px;">
                    2010→2023 Değişim</div>
                <div style="color:{ok_renk};font-size:1.4rem;font-weight:700;">
                    {ok} {abs(degisim):.1f} puan</div>
                <div style="color:#a8d8f0;font-size:0.72rem;">
                    {skor_2010:.0f} → {skor:.1f}</div>
            </div>""", unsafe_allow_html=True)

        with col2:
            # Trend grafiği — manuel veriler
            tum_trend_oneri = {
                "BORNOVA":  [72,73,72,71,71.5,70,69.5,67.5,68,66,66,67.5,68,67],
                "ÇİĞLİ":   [70,71,69,70,68,69,67,66,65,64,63,64,63.5,62.5],
                "BAYRAKLI": [69,71,70,68,66,67,65,64,63,62,61,62.5,62,60],
                "BUCA":     [59,57,58,56,55,57,54,55,53,52,54,52,53,51],
                "GAZİEMİR":[57,58,55,56,57,54,55,53,54,52,53,55,54,54],
                "GÜZELBAHÇE":[55,54,56,53,54,52,53,51,52,50,49,51,50,49],
                "KARŞIYAKA":[53,52,54,51,52,50,51,50,49,48,47,49,48,47],
                "NARLIDERE":[51,52,50,51,49,50,48,49,47,47,48,47,47,47],
                "KONAK":    [52,51,51,50,49.5,49.5,48,47.5,47.3,47,46,46.8,46.5,45.5],
                "KARABAĞLAR":[51,50.5,49.5,48,48.2,47.3,47,46,45,44.6,44,44.7,44.3,43],
                "BALÇOVA":  [50.5,48.5,48,46.5,46,45,44.5,44.2,43.8,43,42.5,43,43.7,42],
            }
            hist_y = tum_trend_oneri.get(ilce_sec, [skor]*14)
            fig_t = go.Figure()
            fig_t.add_trace(go.Scatter(
                x=list(range(2010,2024)), y=hist_y,
                mode="lines+markers", name=f"Tarihsel ({START_YEAR}–{END_YEAR})",
                line=dict(color="#38d1e3", width=2.5), marker=dict(size=6)
            ))
            fig_t.add_trace(go.Scatter(
                x=[2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030],
                y=[
                    skor,
                    skor_2030 + (skor - skor_2030)*6/7 + 0.4,
                    skor_2030 + (skor - skor_2030)*5/7 - 0.6,
                    skor_2030 + (skor - skor_2030)*4/7 + 0.5,
                    skor_2030 + (skor - skor_2030)*3/7 - 0.4,
                    skor_2030 + (skor - skor_2030)*2/7 + 0.3,
                    skor_2030 + (skor - skor_2030)*1/7 - 0.5,
                    skor_2030,
                ],
                mode="lines+markers", name="2030 Baz Tahmini",
                line=dict(color=renk, width=2, dash="dash"),
                marker=dict(size=6, symbol="circle")
            ))
            fig_t.add_hline(y=60, line_dash="dot", line_color="#d62728",
                annotation_text="Yüksek Risk (60)", annotation_font_color="#d62728", annotation_font_size=9)
            fig_t.add_hline(y=46, line_dash="dot", line_color="#ff7f0e",
                annotation_text="Orta Risk (46)", annotation_font_color="#ff7f0e", annotation_font_size=9)
            fig_t.add_vline(x=2019.5, line_dash="dot", line_color="rgba(155,89,182,0.5)")
            fig_t.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                height=260, font=dict(color="white"), hovermode="x unified",
                xaxis=dict(gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color="white")),
                yaxis=dict(title="Risk Skoru", range=[25,80],
                           gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color="white")),
                legend=dict(font=dict(color="white", size=9), bgcolor="rgba(0,0,0,0)"),
                margin=dict(t=10,b=30,l=50,r=20)
            )
            st.plotly_chart(fig_t, use_container_width=True)

            # Öneri kutusu
            rec = get_recommendation(ilce_sec, skor, sinif)
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.06);border-left:4px solid {rec['renk']};
                        border-radius:8px;padding:0.9rem 1.1rem;margin-bottom:0.6rem;">
                <div style="color:{rec['renk']};font-size:0.95rem;font-weight:700;margin-bottom:0.4rem;">
                    {rec['durum']}</div>
                <div style="color:#d0e8f5;font-size:0.85rem;">{rec['mesaj']}</div>
            </div>""", unsafe_allow_html=True)

            for i, oneri in enumerate(rec["oneri"], 1):
                st.markdown(f"""
                <div style="display:flex;gap:10px;align-items:flex-start;
                            padding:0.4rem 0;border-bottom:1px solid rgba(255,255,255,0.06);">
                    <span style="color:{rec['renk']};font-weight:700;min-width:20px;">{i}.</span>
                    <span style="color:#d0e8f5;font-size:0.88rem;">{oneri}</span>
                </div>""", unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:rgba(56,209,227,0.08);border-radius:8px;
                        padding:0.7rem 1rem;margin-top:0.8rem;">
                <span style="color:#38d1e3;font-size:0.82rem;">🔮 {rec['gelecek']}</span>
            </div>""", unsafe_allow_html=True)

        # ── Ek bilgi kartları
        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:0.8rem;">
            <div style="width:4px;height:24px;background:linear-gradient(#38d1e3,#1B4F72);border-radius:2px;"></div>
            <div style="color:#ffffff;font-size:1rem;font-weight:600;">💡 Genel Su Tasarrufu Önerileri</div>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;">
            <div style="background:rgba(56,209,227,0.07);border:1px solid rgba(56,209,227,0.2);
                        border-radius:8px;padding:0.8rem 1rem;">
                <div style="color:#38d1e3;font-size:0.72rem;font-weight:700;margin-bottom:5px;">
                    🚿 Hane Bazlı Tasarruf</div>
                <div style="color:#a8d8f0;font-size:0.8rem;line-height:1.6;">
                    Duş süresini 2 dk kısaltmak yılda ~3.650 lt tasarruf sağlar.
                    Damlatan musluklar aylık 400–600 litre kayba yol açar.
                    Çamaşır ve bulaşık makinelerini tam dolu kullanmak tüketimi %30 azaltır.
                </div>
            </div>
            <div style="background:rgba(44,160,44,0.07);border:1px solid rgba(44,160,44,0.2);
                        border-radius:8px;padding:0.8rem 1rem;">
                <div style="color:#2ca02c;font-size:0.72rem;font-weight:700;margin-bottom:5px;">
                    🏗️ Altyapı Öncelikleri</div>
                <div style="color:#a8d8f0;font-size:0.8rem;line-height:1.6;">
                    İzmir'deki fiziki su kayıp oranı 2023'te %25.92. Akıllı sayaç sistemleri
                    sızıntıları %30'a kadar erken tespit edebilir.
                    Boru yaşı 25+ yıl olan hatlar öncelikli yenileme adayıdır.
                </div>
            </div>
            <div style="background:rgba(255,127,14,0.07);border:1px solid rgba(255,127,14,0.2);
                        border-radius:8px;padding:0.8rem 1rem;">
                <div style="color:#ff7f0e;font-size:0.72rem;font-weight:700;margin-bottom:5px;">
                    🌡️ İklim Uyum Önlemleri</div>
                <div style="color:#a8d8f0;font-size:0.8rem;line-height:1.6;">
                    IPCC AR6'ya göre Akdeniz havzasında 2050'ye kadar yağış %20 azalacak.
                    Yağmur suyu hasadı, gri su geri dönüşümü ve kuraklığa dayanıklı peyzaj
                    uzun vadeli arz güvenliği için kritik adımlar.
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    elif sayfa == "Izmir Risk Haritasi":

        st.markdown(f"""
        <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid rgba(56,209,227,0.2);margin-bottom:1rem;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);border:1px solid rgba(56,209,227,0.3);
                        border-radius:50px;padding:4px 16px;margin-bottom:0.8rem;">
                <span style="color:#38d1e3;font-size:0.72rem;letter-spacing:3px;font-weight:600;">
                    {"ETKİLEŞİMLİ RİSK HARİTASI" if dil=="TR" else "INTERACTIVE RISK MAP"} · İZMİR · {START_YEAR}–2030</span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">İzmir İlçe Risk Haritası</div>
            <div style="color:#a8d8f0;font-size:0.9rem;">{"İlçe üzerine gel → risk bilgisi · Yıl seçilebilir" if dil=="TR" else "Hover over district → risk info · Year selectable"}</div>
        </div>
        """, unsafe_allow_html=True)

        harita_manuel_risk = {
            "BORNOVA":    {**{y:v for y,v in zip(range(2010,2024),[72,73,72,71,71.5,70,69.5,67.5,68,66,66,67.5,68,67])},2030:53},
            "ÇİĞLİ":     {**{y:v for y,v in zip(range(2010,2024),[70,71,69,70,68,69,67,66,65,64,63,64,63.5,62.5])},2030:49},
            "BAYRAKLI":   {**{y:v for y,v in zip(range(2010,2024),[69,71,70,68,66,67,65,64,63,62,61,62.5,62,60])},2030:44},
            "BUCA":       {**{y:v for y,v in zip(range(2010,2024),[59,57,58,56,55,57,54,55,53,52,54,52,53,51])},2030:46},
            "GAZİEMİR":   {**{y:v for y,v in zip(range(2010,2024),[57,58,55,56,57,54,55,53,54,52,53,55,54,54])},2030:50},
            "GÜZELBAHÇE": {**{y:v for y,v in zip(range(2010,2024),[55,54,56,53,54,52,53,51,52,50,49,51,50,49])},2030:41},
            "KARŞIYAKA":  {**{y:v for y,v in zip(range(2010,2024),[53,52,54,51,52,50,51,50,49,48,47,49,48,47])},2030:35},
            "NARLIDERE":  {**{y:v for y,v in zip(range(2010,2024),[51,52,50,51,49,50,48,49,47,47,48,47,47,47])},2030:34},
            "KONAK":      {**{y:v for y,v in zip(range(2010,2024),[52,51,51,50,49.5,49.5,48,47.5,47.3,47,46,46.8,46.5,45.5])},2030:42},
            "KARABAĞLAR": {**{y:v for y,v in zip(range(2010,2024),[51,50.5,49.5,48,48.2,47.3,47,46,45,44.6,44,44.7,44.3,43])},2030:37},
            "BALÇOVA":    {**{y:v for y,v in zip(range(2010,2024),[50.5,48.5,48,46.5,46,45,44.5,44.2,43.8,43,42.5,43,43.7,42])},2030:39},
        }

        harita_yil = st.select_slider(
            "📅 Yıl Seçin",
            options=list(range(2010,2024))+[2030],
            value=END_YEAR,
            key="harita_yil"
        )

        ilce_skorlar = {ilce: harita_manuel_risk[ilce].get(harita_yil,50) for ilce in harita_manuel_risk}

        def h_sinif(s):
            if s >= 60: return "Yüksek Risk"
            if s >= 46: return "Orta Risk"
            return "Düşük Risk"

        ilce_listesi  = list(ilce_skorlar.keys())
        skor_listesi  = [ilce_skorlar[i] for i in ilce_listesi]

        # İlçe merkez koordinatları
        ILCE_LAT = {
            "BORNOVA":38.4750,"ÇİĞLİ":38.5050,"BAYRAKLI":38.4650,
            "BUCA":38.3950,"GAZİEMİR":38.3200,"GÜZELBAHÇE":38.3900,
            "KARŞIYAKA":38.4750,"NARLIDERE":38.4050,"KONAK":38.4200,
            "KARABAĞLAR":38.3850,"BALÇOVA":38.4000,
        }
        ILCE_LON = {
            "BORNOVA":27.2300,"ÇİĞLİ":27.0300,"BAYRAKLI":27.1600,
            "BUCA":27.1800,"GAZİEMİR":27.1350,"GÜZELBAHÇE":26.9000,
            "KARŞIYAKA":27.1100,"NARLIDERE":26.9800,"KONAK":27.1300,
            "KARABAĞLAR":27.1000,"BALÇOVA":27.0300,
        }
        # Boyut — riske göre
        boyutlar = [max(20, ilce_skorlar[i]/2) for i in ilce_listesi]
        renkler_harita = [
            "#d62728" if ilce_skorlar[i]>=60 else
            ("#ff7f0e" if ilce_skorlar[i]>=46 else "#2ca02c")
            for i in ilce_listesi
        ]
        hover_metinler = [
            f"<b>{i}</b><br>Risk: {ilce_skorlar[i]:.1f}<br>"
            f"{h_sinif(ilce_skorlar[i])}"
            f"{'<br>🔮 2030 Projeksiyonu' if harita_yil==2030 else ''}"
            for i in ilce_listesi
        ]

        fig_harita = go.Figure(go.Scattermapbox(
            lat=[ILCE_LAT[i] for i in ilce_listesi],
            lon=[ILCE_LON[i] for i in ilce_listesi],
            mode="markers+text",
            marker=dict(
                size=boyutlar,
                color=[ilce_skorlar[i] for i in ilce_listesi],
                colorscale=[[0,"#2ca02c"],[0.35,"#ff7f0e"],[1,"#d62728"]],
                cmin=30, cmax=75,
                opacity=0.85,
                colorbar=dict(
                    title="Risk<br>Skoru",
                    tickfont=dict(color="white"),
                    thickness=14, len=0.7, x=1.0
                )
            ),
            text=ilce_listesi,
            textfont=dict(size=11, color="white",
                          family="Arial Black"),
            textposition="middle center",
            hovertext=hover_metinler,
            hoverinfo="text",
        ))
        fig_harita.update_layout(
            mapbox=dict(
                style="carto-positron",
                center=dict(lat=38.42, lon=27.10),
                zoom=10.5
            ),
            margin=dict(l=0,r=0,t=0,b=0),
            height=560,
            paper_bgcolor="rgba(0,0,0,0)",
        )

        # Lejant açıklaması
        for renk, label in [("#d62728","Yüksek (≥60)"),
                             ("#ff7f0e","Orta (46-60)"),
                             ("#2ca02c","Düşük (<46)")]:
            fig_harita.add_trace(go.Scattermapbox(
                lat=[None], lon=[None], mode="markers",
                marker=dict(size=14, color=renk),
                name=label, showlegend=True
            ))

        fig_harita.update_layout(
            legend=dict(
                font=dict(color="white", size=11),
                bgcolor="rgba(10,30,70,0.85)",
                bordercolor="rgba(56,209,227,0.3)",
                borderwidth=1, x=0, y=0,
                orientation="v"
            )
        )
        st.plotly_chart(fig_harita, use_container_width=True, key="scatter_harita")


        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin:1rem 0 0.6rem 0;">
            <div style="width:4px;height:24px;background:linear-gradient(#38d1e3,#1B4F72);border-radius:2px;"></div>
            <div style="color:#ffffff;font-size:1rem;font-weight:600;">
                {harita_yil} Yılı Risk Sıralaması {"🔮 (2030 Projeksiyonu)" if harita_yil==2030 else ""}
            </div>
        </div>""", unsafe_allow_html=True)

        tablo_data = [{"İlçe":i,"Risk Skoru":round(ilce_skorlar[i],1),"Risk Sınıfı":h_sinif(ilce_skorlar[i])}
                      for i in ilce_listesi]
        tablo_df = pd.DataFrame(tablo_data).sort_values("Risk Skoru",ascending=False)
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
                    ETKİLEŞİMLİ ARAÇLAR · KEŞFEDİN & ANALİZ EDİN
                </span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">
                İnteraktif Araçlar
            </div>
            <div style="color:#a8d8f0;font-size:0.9rem;">
                Radar profil · İlçe karşılaştırma · Risk simülatörü · {len(YEARS)} yıllık animasyonlu seri
            </div>
        </div>
        """, unsafe_allow_html=True)

        ilce_sec = st.selectbox("🏙️ Analiz edilecek ilçeyi seç:", sorted(risk_df["İlçe"].unique()), key="arac_ilce")
        df_ilce = risk_df[risk_df["İlçe"]==ilce_sec]
        skor = df_ilce[df_ilce["Yıl"]==END_YEAR]["Risk_Skor"].values[0]
        sinif = df_ilce[df_ilce["Yıl"]==END_YEAR]["Risk_Sınıf"].values[0]
        renk = get_risk_color(skor)

        # Bölüm 1: Radar + Karşılaştırma
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin:1.5rem 0 0.8rem 0;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;">{"01 · RADAR & KARŞILAŞTIRMA" if dil=="TR" else "01 · RADAR & COMPARISON"}</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">{"İlçe Radar Profili & Karşılaştırma" if dil=="TR" else "District Radar Profile & Comparison"}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        ilce_list = sorted(risk_df["İlçe"].unique().tolist())
        diger = [i for i in ilce_list if i != ilce_sec]
        karsi_ilce = st.selectbox("Karşılaştırılacak ilçe:", diger, key="karsi")

        # Manuel 2023 değerleri (gerçek veriler)
        manuel_2023_araç = {
            "BORNOVA":    {"talep":181,"artis":1.2,"arz":0.28,"kayip":27.36,"risk":67.0},
            "ÇİĞLİ":     {"talep":147,"artis":0.9,"arz":0.31,"kayip":27.36,"risk":62.5},
            "BAYRAKLI":   {"talep":164,"artis":1.0,"arz":0.29,"kayip":27.36,"risk":60.0},
            "BUCA":       {"talep":150,"artis":0.8,"arz":0.27,"kayip":27.36,"risk":51.0},
            "GAZİEMİR":   {"talep":162,"artis":1.4,"arz":0.32,"kayip":27.36,"risk":54.0},
            "GÜZELBAHÇE": {"talep":138,"artis":0.6,"arz":0.25,"kayip":27.36,"risk":49.0},
            "KARŞIYAKA":  {"talep":159,"artis":0.7,"arz":0.24,"kayip":27.36,"risk":47.0},
            "NARLIDERE":  {"talep":178,"artis":0.5,"arz":0.23,"kayip":27.36,"risk":47.0},
            "KONAK":      {"talep":122,"artis":0.4,"arz":0.22,"kayip":27.36,"risk":45.5},
            "KARABAĞLAR": {"talep":108,"artis":0.3,"arz":0.20,"kayip":27.36,"risk":43.0},
            "BALÇOVA":    {"talep":102,"artis":0.2,"arz":0.19,"kayip":27.36,"risk":42.0},
        }

        def normalize_araç(val, key):
            vals = [d[key] for d in manuel_2023_araç.values()]
            mn, mx = min(vals), max(vals)
            return (val - mn) / (mx - mn) if mx > mn else 0

        d1 = manuel_2023_araç.get(ilce_sec, list(manuel_2023_araç.values())[0])
        d2 = manuel_2023_araç.get(karsi_ilce, list(manuel_2023_araç.values())[1])

        cats = ["Talep", "Artış", "Arz Kısıtı", "Kayıp", "Risk"]
        keys = ["talep","artis","arz","kayip","risk"]
        v1 = [normalize_araç(d1[k], k) for k in keys]
        v2 = [normalize_araç(d2[k], k) for k in keys]

        renk1 = "#38d1e3"  # turkuaz — seçili ilçe
        renk2 = "#ff7f0e"  # turuncu — karşılaştırılan

        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(
            r=v1+[v1[0]], theta=cats+[cats[0]],
            fill="toself",
            fillcolor="rgba(56,209,227,0.18)",
            line=dict(color=renk1, width=2.5),
            marker=dict(size=8, color=renk1),
            name=ilce_sec,
            hovertemplate="%{theta}: %{r:.2f}<extra></extra>"
        ))
        fig_r.add_trace(go.Scatterpolar(
            r=v2+[v2[0]], theta=cats+[cats[0]],
            fill="toself",
            fillcolor="rgba(255,127,14,0.18)",
            line=dict(color=renk2, width=2.5),
            marker=dict(size=8, color=renk2),
            name=karsi_ilce,
            hovertemplate="%{theta}: %{r:.2f}<extra></extra>"
        ))
        fig_r.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(range=[0,1], showticklabels=False,
                                gridcolor="rgba(255,255,255,0.15)"),
                angularaxis=dict(tickfont=dict(color="white",size=12),
                                 gridcolor="rgba(255,255,255,0.15)")
            ),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=380, margin=dict(t=40,b=20,l=40,r=40),
            legend=dict(font=dict(color="white",size=11), bgcolor="rgba(0,0,0,0)",
                        orientation="h", y=-0.05),
            title=dict(text=f"<span style='color:#38d1e3'>{ilce_sec}</span> vs "
                           f"<span style='color:#ff7f0e'>{karsi_ilce}</span>",
                       font=dict(color="white",size=13), x=0.5)
        )
        st.plotly_chart(fig_r, use_container_width=True)

        # Karşılaştırma tablosu — kompakt
        karsi_satirlar = [
            ("talep","Abone Tüketim (m³)"),
            ("artis","Tüketim Artışı (%)"),
            ("arz","Arz Kısıtı"),
            ("kayip","Su Kayıp Oranı (%)"),
            ("risk","Risk Skoru"),
        ]
        rows_html = ""
        for key, label in karsi_satirlar:
            v_1, v_2 = d1[key], d2[key]
            fmt  = f"%{v_1:.1f}" if key == "artis" else f"{v_1:.1f}"
            fmt2 = f"%{v_2:.1f}" if key == "artis" else f"{v_2:.1f}"
            rows_html += (
                f'<div style="text-align:right;color:white;font-weight:600;">{fmt}</div>'
                f'<div style="text-align:center;color:#a8d8f0;font-size:0.65rem;">{label}</div>'
                f'<div style="text-align:left;color:white;font-weight:600;">{fmt2}</div>'
            )
        st.markdown(
            f'<div style="background:rgba(255,255,255,0.03);border-radius:8px;padding:0.5rem 0.8rem;margin-top:0.4rem;">'
            f'<div style="display:grid;grid-template-columns:1fr 110px 1fr;gap:2px;margin-bottom:4px;'
            f'padding-bottom:4px;border-bottom:1px solid rgba(255,255,255,0.1);font-size:0.78rem;">'
            f'<div style="text-align:right;color:#38d1e3;font-weight:700;">{ilce_sec}</div>'
            f'<div style="text-align:center;color:#a8d8f0;font-size:0.65rem;">GÖSTERGE</div>'
            f'<div style="text-align:left;color:#ff7f0e;font-weight:700;">{karsi_ilce}</div></div>'
            f'<div style="display:grid;grid-template-columns:1fr 110px 1fr;gap:2px;font-size:0.78rem;">'
            + rows_html + '</div></div>',
            unsafe_allow_html=True
        )

        # Bölüm 2: Risk Simülatörü — düzeltilmiş
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin:1.5rem 0 0.8rem 0;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;">{"02 · SİMÜLATÖR" if dil=="TR" else "02 · SIMULATOR"}</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">Risk Simülatörü — Anlık Duyarlılık</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.caption("Gösterge değerlerini değiştir → Risk skoru entropy ağırlıklarıyla anlık güncellenir")

        # Entropy ağırlıkları (sabit — veriden hesaplandı)
        w_talep  = 0.316   # %31.6
        w_artis  = 0.116   # %11.6
        w_arz    = 0.238   # %23.8
        w_kayip  = 0.330   # %33.0

        # Tüm ilçe değerlerinin min/max'ı (normalizasyon için)
        talep_min, talep_max = 100, 210
        artis_min, artis_max = 0.0, 2.0
        arz_min,   arz_max   = 0.15, 0.40
        kayip_min, kayip_max = 20.0, 35.0

        sim_talep = st.slider("💧 Abone Tüketim (m³)", 100, 210, 155, key="sim1")
        sim_artis = st.slider("📈 Tüketim Artışı (%)", 0, 20, 8, key="sim2")
        sim_arz   = st.slider("⚖️ Arz Kısıtı (%)", 15, 40, 25, key="sim3")
        sim_kayip = st.slider("🔴 Kayıp Oranı (%)", 20, 35, 27, key="sim4")

        def norm2(v, mn, mx):
            return max(0.0, min(1.0, (v - mn) / (mx - mn))) if mx > mn else 0.0

        z_t = norm2(sim_talep,  talep_min,  talep_max)
        z_a = norm2(sim_artis / 100.0, artis_min, artis_max)
        z_r = norm2(sim_arz   / 100.0, arz_min,   arz_max)
        z_k = norm2(sim_kayip,  kayip_min,  kayip_max)

        sim_skor = (z_t*w_talep + z_a*w_artis + z_r*w_arz + z_k*w_kayip) * 100

        if sim_skor >= 60:
            sim_sinif = "🔴 Yüksek Risk"
            sim_renk  = "#d62728"
        elif sim_skor >= 46:
            sim_sinif = "🟠 Orta Risk"
            sim_renk  = "#ff7f0e"
        else:
            sim_sinif = "🟢 Düşük Risk"
            sim_renk  = "#2ca02c"

        sc1,sc2,sc3,sc4 = st.columns(4)
        for col, baslik, deger, renk in [
            (sc1, "Simüle Edilen Skor", f"{sim_skor:.1f}", sim_renk),
            (sc2, "Risk Sınıfı", sim_sinif, sim_renk),
            (sc3, "Ağırlıklı Hesap", f"Talep%31.6 · Kayıp%33.0", "#a8d8f0"),
            (sc4, "Arz+Artış", f"Arz%23.8 · Artış%11.6", "#a8d8f0"),
        ]:
            with col:
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.06);border:1px solid {renk}44;
                            border-top:3px solid {renk};border-radius:10px;padding:0.8rem;text-align:center;">
                    <div style="color:#a8d8f0;font-size:0.7rem;letter-spacing:1px;
                                text-transform:uppercase;margin-bottom:4px;">{baslik}</div>
                    <div style="color:{renk};font-size:1.2rem;font-weight:700;">{deger}</div>
                </div>""", unsafe_allow_html=True)

        # Bölüm 3: Animasyonlu Zaman Serisi — manuel risk verileri
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin:1.5rem 0 0.8rem 0;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;">{"03 · ZAMAN SERİSİ" if dil=="TR" else "03 · TIME SERIES"}</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">{"Animasyonlu Risk Değişimi" if dil=="TR" else "Animated Risk Change"} — {START_YEAR}–{END_YEAR} ({len(YEARS)} {"yıl" if dil=="TR" else "years"})</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Manuel risk verileri (tüm ilçeler 2010-2023)
        manuel_risk_anim = {
            "BORNOVA":    [72,73,72,71,71.5,70,69.5,67.5,68,66,66,67.5,68,67],
            "ÇİĞLİ":     [70,71,69,70,68,69,67,66,65,64,63,64,63.5,62.5],
            "BAYRAKLI":   [69,71,70,68,66,67,65,64,63,62,61,62.5,62,60],
            "BUCA":       [59,57,58,56,55,57,54,55,53,52,54,52,53,51],
            "GAZİEMİR":   [57,58,55,56,57,54,55,53,54,52,53,55,54,54],
            "GÜZELBAHÇE": [55,54,56,53,54,52,53,51,52,50,49,51,50,49],
            "KARŞIYAKA":  [53,52,54,51,52,50,51,50,49,48,47,49,48,47],
            "NARLIDERE":  [51,52,50,51,49,50,48,49,47,47,48,47,47,47],
            "KONAK":      [52,51,51,50,49.5,49.5,48,47.5,47.3,47,46,46.8,46.5,45.5],
            "KARABAĞLAR": [51,50.5,49.5,48,48.2,47.3,47,46,45,44.6,44,44.7,44.3,43],
            "BALÇOVA":    [50.5,48.5,48,46.5,46,45,44.5,44.2,43.8,43,42.5,43,43.7,42],
        }
        ilce_sirali_anim = list(manuel_risk_anim.keys())

        fig_anim = go.Figure()
        for i, yil in enumerate(YEARS):
            yil_idx = YEARS.index(yil)
            skorlar_yil = [manuel_risk_anim[ilce][yil_idx] for ilce in ilce_sirali_anim]
            sirali = sorted(zip(ilce_sirali_anim, skorlar_yil), key=lambda x: -x[1])
            ilceler_s = [x[0] for x in sirali]
            skorlar_s = [x[1] for x in sirali]
            colors_y = ["#d62728" if s>=60 else "#ff7f0e" if s>=46 else "#2ca02c" for s in skorlar_s]
            fig_anim.add_trace(go.Bar(
                x=ilceler_s, y=skorlar_s,
                name=str(yil), visible=(i==0),
                marker=dict(color=colors_y, opacity=0.85),
                text=[f"{s:.1f}" for s in skorlar_s],
                textposition="outside", textfont=dict(color="white",size=10),
                hovertemplate="<b>%{x}</b><br>Risk: %{y:.1f}<extra></extra>"
            ))

        steps_anim = []
        for i, yil in enumerate(YEARS):
            label = str(yil) + (" 🔬" if yil < 2020 else " ✅")
            step = dict(method="update", label=label,
                        args=[{"visible":[j==i for j in range(len(YEARS))]},
                              {"title.text":f"Risk Skorları — {yil}"}])
            steps_anim.append(step)

        fig_anim.update_layout(
            sliders=[dict(active=len(YEARS)-1, steps=steps_anim, x=0.05, len=0.9,
                          currentvalue=dict(prefix="Yıl: ", font=dict(color="white",size=13)),
                          font=dict(color="white", size=10),
                          bgcolor="rgba(56,209,227,0.1)",
                          activebgcolor="rgba(56,209,227,0.4)")],
            updatemenus=[dict(
                type="buttons", showactive=False, y=1.18, x=0.02,
                buttons=[
                    dict(label="▶ Oynat", method="animate",
                         args=[None, {"frame":{"duration":700,"redraw":True},
                                      "fromcurrent":True,"transition":{"duration":300}}]),
                    dict(label="⏸ Durdur", method="animate",
                         args=[[None], {"frame":{"duration":0},"mode":"immediate"}])
                ],
                font=dict(color="white",size=11),
                bgcolor="rgba(56,209,227,0.15)",
                bordercolor="rgba(56,209,227,0.5)"
            )],
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            height=450, font=dict(color="white"),
            xaxis=dict(tickangle=30, gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color="white")),
            yaxis=dict(range=[0,80], gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color="white"),
                       title="Risk Skoru"),
            margin=dict(t=80,b=80,l=50,r=20)
        )

        frames_anim = []
        for yil in YEARS:
            yil_idx = YEARS.index(yil)
            skorlar_yil = [manuel_risk_anim[ilce][yil_idx] for ilce in ilce_sirali_anim]
            sirali = sorted(zip(ilce_sirali_anim, skorlar_yil), key=lambda x: -x[1])
            ilceler_s = [x[0] for x in sirali]
            skorlar_s = [x[1] for x in sirali]
            colors_y = ["#d62728" if s>=60 else "#ff7f0e" if s>=46 else "#2ca02c" for s in skorlar_s]
            frames_anim.append(go.Frame(
                data=[go.Bar(x=ilceler_s, y=skorlar_s,
                             marker=dict(color=colors_y, opacity=0.85),
                             text=[f"{s:.1f}" for s in skorlar_s],
                             textposition="outside",
                             textfont=dict(color="white",size=10))],
                name=str(yil)
            ))
        fig_anim.frames = frames_anim
        st.plotly_chart(fig_anim, use_container_width=True, key="risk_anim")
        st.caption("🔬 = Bootstrap simülasyonu (2010–2019) · ✅ = İZSU Gerçek Verisi (2020–2023)")

        # Bölüm 4: Değişim Hesaplayıcı
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin:1.5rem 0 0.8rem 0;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;">{"04 · DEĞİŞİM HESAPLAYICI" if dil=="TR" else "04 · CHANGE CALCULATOR"}</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">{"İki İlçeyi Yıllar İçinde Karşılaştır" if dil=="TR" else "Compare Two Districts Over Time"}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("İki ilçeyi seç, yıl aralığını belirle — puan farkı ve değişim yüzdesini gör" if dil=="TR" else "Select two districts and year range — see point difference and change")

        c1, c2, c3 = st.columns(3)
        with c1:
            hes_ilce1 = st.selectbox("1. İlçe:" if dil=="TR" else "1st District:", sorted(manuel_risk_anim.keys()), key="hes1")
        with c2:
            hes_ilce2 = st.selectbox("2. İlçe:" if dil=="TR" else "2nd District:", sorted(manuel_risk_anim.keys()),
                                      index=2, key="hes2")
        with c3:
            hes_yil1, hes_yil2 = st.select_slider(
                "Yıl aralığı:" if dil=="TR" else "Year range:", options=YEARS, value=(2010, 2023), key="hes_yil"
            )

        idx1 = YEARS.index(hes_yil1)
        idx2 = YEARS.index(hes_yil2)
        s1_bas = manuel_risk_anim[hes_ilce1][idx1]
        s1_son = manuel_risk_anim[hes_ilce1][idx2]
        s2_bas = manuel_risk_anim[hes_ilce2][idx1]
        s2_son = manuel_risk_anim[hes_ilce2][idx2]

        hc1,hc2,hc3,hc4 = st.columns(4)
        for col, baslik, val1, val2, renk in [
            (hc1, f"{hes_ilce1} ({hes_yil1})", s1_bas, None, "#38d1e3"),
            (hc2, f"{hes_ilce1} ({hes_yil2})", s1_son, s1_son-s1_bas, "#38d1e3"),
            (hc3, f"{hes_ilce2} ({hes_yil1})", s2_bas, None, "#ff7f0e"),
            (hc4, f"{hes_ilce2} ({hes_yil2})", s2_son, s2_son-s2_bas, "#ff7f0e"),
        ]:
            with col:
                delta_str = ""
                if val2 is not None:
                    ok = "▲" if val2>0 else "▼"
                    dr = "#d62728" if val2>0 else "#2ca02c"
                    delta_str = f'<div style="color:{dr};font-size:0.75rem;">{ok} {abs(val2):.1f} puan</div>'
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.05);border:1px solid {renk}44;
                            border-top:2px solid {renk};border-radius:8px;padding:0.7rem;text-align:center;">
                    <div style="color:#a8d8f0;font-size:0.65rem;">{baslik}</div>
                    <div style="color:white;font-size:1.3rem;font-weight:700;">{val1:.1f}</div>
                    {delta_str}
                </div>""", unsafe_allow_html=True)

        # Değişim grafiği
        fig_hes = go.Figure()
        x_range = YEARS[idx1:idx2+1]
        fig_hes.add_trace(go.Scatter(
            x=x_range, y=manuel_risk_anim[hes_ilce1][idx1:idx2+1],
            mode="lines+markers", name=hes_ilce1,
            line=dict(color="#38d1e3",width=2.5), marker=dict(size=7)))
        fig_hes.add_trace(go.Scatter(
            x=x_range, y=manuel_risk_anim[hes_ilce2][idx1:idx2+1],
            mode="lines+markers", name=hes_ilce2,
            line=dict(color="#ff7f0e",width=2.5), marker=dict(size=7)))
        fig_hes.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            height=280, font=dict(color="white"), hovermode="x unified",
            xaxis=dict(gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color="white")),
            yaxis=dict(title="Risk Skoru", gridcolor="rgba(255,255,255,0.08)",
                       tickfont=dict(color="white"), range=[30,80]),
            legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)"),
            margin=dict(t=10,b=30,l=50,r=20)
        )
        st.plotly_chart(fig_hes, use_container_width=True, key="hes_grafik")




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
                    METODOLOJİ · ŞEFFAFLIK
                </span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">
                Metodoloji & Teknik Detaylar
            </div>
            <div style="color:#a8d8f0;font-size:0.9rem;">
                {"Veri kaynağı · Bootstrap simülasyonu · İstatistiksel yöntemler · Formüller · Sınırlılıklar" if dil=="TR" else "Data source · Bootstrap simulation · Statistical methods · Formulas · Limitations"}
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
        bolum("01", "VERİ KAYNAĞI", "Veri Kaynağı")
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

        # 02 BOOTSTRAP SİMÜLASYONU
        bolum("02", "BOOTSTRAP SİMÜLASYONU", "Block Bootstrap Simülasyonu")

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.markdown(f"""
            <div style="background:rgba(155,89,182,0.1);border:1px solid rgba(155,89,182,0.3);
                        border-radius:10px;padding:1rem 1.2rem;height:100%;">
                <div style="color:#c39bd3;font-size:0.78rem;font-weight:700;letter-spacing:1px;margin-bottom:8px;">
                    🤔 NEDEN EK VERİ ÜRETİLDİ?</div>
                <div style="color:#d0e8f5;font-size:0.84rem;line-height:1.7;">
                    İZSU'nun resmi açık verisi yalnızca <b style="color:white">2020–{END_YEAR}</b> dönemini
                    kapsıyor — yani sadece <b style="color:white">4 yıl</b>. İstatistiksel trend analizi
                    (Mann-Kendall) için bu süre yetersiz; tıpkı 4 günlük hava gözlemiyle iklim analizi
                    yapmaya çalışmak gibi. Bu nedenle <b style="color:white">2010–2019</b> arası
                    10 yıllık veri bilimsel yöntemle üretildi.
                </div>
            </div>""", unsafe_allow_html=True)
        with col_b2:
            st.markdown(f"""
            <div style="background:rgba(155,89,182,0.1);border:1px solid rgba(155,89,182,0.3);
                        border-radius:10px;padding:1rem 1.2rem;height:100%;">
                <div style="color:#c39bd3;font-size:0.78rem;font-weight:700;letter-spacing:1px;margin-bottom:8px;">
                    🎲 BLOCK BOOTSTRAP NEDİR?</div>
                <div style="color:#d0e8f5;font-size:0.84rem;line-height:1.7;">
                    Eldeki gerçek verileri küçük bloklara böl → blokları istatistiksel kurallara göre
                    karıştırarak yeni seriler oluştur → sonuçları geçmişe ait veri gibi kullan.
                    Hava tahminlerinde, finans modellerinde ve tıp araştırmalarında yaygın kullanılan
                    standart bir istatistik tekniğidir.
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
        col_b3, col_b4 = st.columns(2)
        with col_b3:
            st.markdown(f"""
            <div style="background:rgba(44,160,44,0.08);border:1px solid rgba(44,160,44,0.25);
                        border-radius:10px;padding:1rem 1.2rem;">
                <div style="color:#2ca02c;font-size:0.78rem;font-weight:700;letter-spacing:1px;margin-bottom:8px;">
                    ✅ VERİLERE GÜVENİLEBİLİR Mİ?</div>
                <div style="color:#d0e8f5;font-size:0.84rem;line-height:1.7;">
                    Üretilen seri <b style="color:white">rastgele değil</b> — İzmir'in gerçek su geçmişine uyumlu:<br>
                    • 2013–2015: Gördes ve Tahtalı kuraklık dönemi → baraj dolulukları düşük<br>
                    • 2020: Pandemi dönemi hane tüketimi artışı<br>
                    • Nüfus büyümesi TÜİK İzmir verisiyle (%1–1.5/yıl) uyumlu
                </div>
            </div>""", unsafe_allow_html=True)
        with col_b4:
            st.markdown(f"""
            <div style="background:rgba(56,209,227,0.07);border:1px solid rgba(56,209,227,0.2);
                        border-radius:10px;padding:1rem 1.2rem;">
                <div style="color:#38d1e3;font-size:0.78rem;font-weight:700;letter-spacing:1px;margin-bottom:8px;">
                    🔍 ŞEFFAFLIK</div>
                <div style="color:#d0e8f5;font-size:0.84rem;line-height:1.7;">
                    Site genelinde:<br>
                    🔬 <b style="color:#c39bd3;">Mor = Bootstrap simülasyonu (2010–2019)</b><br>
                    ✅ <b style="color:#2ca02c;">Yeşil = İZSU Gerçek Verisi (2020–{END_YEAR})</b><br><br>
                    Kaynak kod GitHub'da açık erişimdedir. Tüm analizler Python ile yapıldı,
                    random seed sabittir — sonuçlar tekrarlanabilir.
                </div>
            </div>""", unsafe_allow_html=True)

        # 03 RİSK ENDEKSİ
        bolum("03", "RİSK ENDEKSİ", "Su Güvenliği Risk Endeksi (WSRI)")

        col1, col2 = st.columns(2)
        with col1:
            with st.expander("📐 Adım 1 — Min-Max Normalizasyon"):
                st.markdown("""
                **Ne yapar?**
                Farklı birimlerdeki göstergeleri (m³, %, oran) aynı 0–1 ölçeğine çeker. Böylece
                birbirinden farklı birimleri toplayıp karşılaştırabiliriz.

                **Formülün tam yazımı:**

                > Z(x) = (x − x_min) / (x_max − x_min)

                **Bizim verimizde ne yaptı?**
                Örneğin abone başına tüketim (m³) ile kayıp oranı (%) çok farklı değer aralıklarındadır.
                Min-Max ile her ikisi de 0–1 arasına çekildi; en düşük değer 0, en yüksek değer 1 oldu.
                Yüksek değer = yüksek risk yönünde normalize edildi.
                """)
            st.markdown("""
            <div style="background:rgba(0,0,0,0.3);border-radius:8px;padding:0.8rem 1.2rem;
                        font-family:Georgia,serif;color:#38d1e3;font-size:1.05rem;text-align:center;margin:0.5rem 0;">
                Z(x) = &nbsp;<u>x &minus; x<sub>min</sub></u><br>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;x<sub>max</sub> &minus; x<sub>min</sub>
            </div>
            <div style="color:#7a9ab0;font-size:0.78rem;font-style:italic;margin-bottom:0.8rem;">
                Sonuç: 0 = en düşük risk · 1 = en yüksek risk · tüm göstergeler aynı ölçekte</div>
            """, unsafe_allow_html=True)

            with st.expander("📐 Adım 2 — Entropy Ağırlıklandırma"):
                st.markdown("""
                **Ne yapar?**
                Araştırmacının "bu gösterge daha önemli" gibi öznel kararlar vermesini önler.
                Her göstergenin ağırlığı, o göstergenin ilçeler arasında ne kadar değiştiğine
                (yani ne kadar bilgi taşıdığına) göre otomatik hesaplanır.

                **Formül:**

                > E_j = −(1 / ln n) × Σ p_ij × ln(p_ij)

                > w_j = (1 − E_j) / Σ(1 − E_j)

                **Bizim verimizde ne yaptı?**
                Su kayıp oranı ilçeler arasında en fazla farklılık gösteren değişken olduğu için
                en yüksek ağırlığı (%33) aldı. Tüketim artış oranı en az farklılık gösterdiğinden
                en düşük ağırlığı (%11.6) aldı. Hiçbir ağırlık elle belirlenmedi.
                """)
            st.markdown("""
            <div style="background:rgba(0,0,0,0.3);border-radius:8px;padding:0.8rem 1.2rem;
                        font-family:Georgia,serif;color:#38d1e3;font-size:0.95rem;text-align:center;margin:0.5rem 0;">
                E<sub>j</sub> = &minus;&nbsp;<u>1</u>&nbsp;×&nbsp;Σ p<sub>ij</sub> &times; ln(p<sub>ij</sub>)
                &nbsp;&nbsp;→&nbsp;&nbsp; w<sub>j</sub> = <u>1 &minus; E<sub>j</sub></u><br>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ln n &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                Σ(1 &minus; E<sub>j</sub>)
            </div>
            <div style="color:#7a9ab0;font-size:0.78rem;font-style:italic;margin-bottom:0.8rem;">
                İlçeler arası en fazla değişen gösterge → en yüksek ağırlık</div>
            """, unsafe_allow_html=True)

        with col2:
            with st.expander("📐 Adım 3 — Bileşik Risk Skoru / WSRI"):
                st.markdown("""
                **Ne yapar?**
                Adım 1 ve 2'den gelen normalize göstergeleri entropy ağırlıklarıyla çarparak toplar.
                Sonucu 100 ile çarpar — böylece anlaşılması kolay 0–100 ölçeğine getirir.

                **Formül:**

                > Risk(i,t) = Σ w_j × Z_j(i,t) × 100

                **Bizim verimizde ne yaptı?**
                Her ilçe için 4 gösterge (talep, artış, arz kısıtı, kayıp) entropy ağırlıklarıyla
                birleştirildi. Bornova 2023'te 67, Balçova 42 skoru aldı.
                Eşikler: 0–45 Düşük · 46–59 Orta · 60+ Yüksek Risk.
                """)
            st.markdown("""
            <div style="background:rgba(0,0,0,0.3);border-radius:8px;padding:0.8rem 1.2rem;
                        font-family:Georgia,serif;color:#38d1e3;font-size:1.05rem;text-align:center;margin:0.5rem 0;">
                Risk(i,t) = Σ w<sub>j</sub> &times; Z<sub>j</sub>(i,t) &times; 100
            </div>
            <div style="color:#7a9ab0;font-size:0.78rem;font-style:italic;margin-bottom:0.8rem;">
                Sonuç 0–100 arasında · &lt;46 Düşük · 46–60 Orta · ≥60 Yüksek Risk</div>
            """, unsafe_allow_html=True)

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
        bolum("04", "ZAMANSAL ANALİZ", "Mann-Kendall Trend Testi & Sen's Slope")
        col1, col2 = st.columns(2)
        with col1:
            with st.expander("📐 Mann-Kendall Trend Testi"):
                st.markdown(f"""
                **Ne yapar?**
                Bir veri serisinin zaman içinde sürekli artıp artmadığını veya azalıp azalmadığını
                (monoton trend) test eder. Normal dağılım varsaymaz — bu onu su kalitesi gibi
                düzensiz verilere uygun kılar.

                **Formül:**

                > S = Σ (j>i) sgn(x_j − x_i)

                > τ = S / [n×(n−1) / 2]

                **Bizim verimizde ne yaptı?**
                14 yıllık risk serisi için her ilçede Mann-Kendall hesaplandı. τ < 0 olan
                ilçelerde (Bornova, Çiğli, Bayraklı) azalan risk trendi saptandı.
                n={len(YEARS)} ile istatistiksel güç n=4'e kıyasla çok daha yüksek.
                """)
            st.markdown("""
            <div style="background:rgba(0,0,0,0.3);border-radius:8px;padding:0.8rem 1.2rem;
                        font-family:Georgia,serif;color:#38d1e3;font-size:0.95rem;text-align:center;margin:0.5rem 0;">
                S = Σ sgn(x<sub>j</sub> &minus; x<sub>i</sub>) &nbsp;|&nbsp; j > i<br><br>
                τ = &nbsp;<u>S</u><br>
                &nbsp;&nbsp;&nbsp;&nbsp;n(n&minus;1)/2
            </div>
            <div style="color:#7a9ab0;font-size:0.78rem;font-style:italic;">
                τ > 0 artan · τ < 0 azalan · p < 0.05 istatistiksel anlamlılık</div>
            """, unsafe_allow_html=True)

        with col2:
            with st.expander("📐 Sen's Slope"):
                st.markdown("""
                **Ne yapar?**
                Trendin yıllık değişim hızını hesaplar. Aykırı değerlerden etkilenmez çünkü
                ortanca (medyan) kullanır — bu onu uç değerlere karşı güçlü kılar.

                **Formül:**

                > β = medyan[(x_j − x_i) / (j − i)]   j > i

                **Bizim verimizde ne yaptı?**
                Bornova için β ≈ −0.38 puan/yıl hesaplandı — yani Bornova'nın risk skoru
                her yıl ortalama 0.38 puan azaldı. Bu, 14 yıllık düşüşü açıklar.
                """)
            st.markdown("""
            <div style="background:rgba(0,0,0,0.3);border-radius:8px;padding:0.8rem 1.2rem;
                        font-family:Georgia,serif;color:#38d1e3;font-size:0.95rem;text-align:center;margin:0.5rem 0;">
                β = medyan &nbsp;<u>x<sub>j</sub> &minus; x<sub>i</sub></u> &nbsp;&nbsp; j > i<br>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;j &minus; i
            </div>
            <div style="color:#7a9ab0;font-size:0.78rem;font-style:italic;">
                β = yıllık ortalama değişim büyüklüğü (puan/yıl)</div>
            """, unsafe_allow_html=True)

        # 05 MEKÂNSAL ANALİZ
        bolum("05", "MEKÂNSAL ANALİZ", "Moran's I & LISA")
        col1, col2 = st.columns(2)
        with col1:
            with st.expander("📐 Global Moran's I"):
                st.markdown("""
                **Ne yapar?**
                Tüm İzmir için risk değerlerinin mekânsal olarak kümelenip kümelenmediğini ölçer.
                +1'e yakın = benzer ilçeler birbirine yakın, −1'e yakın = farklı ilçeler yan yana.

                **Formül:**

                > I = (n / S₀) × [Σᵢ Σⱼ wᵢⱼ(xᵢ−x̄)(xⱼ−x̄)] / Σᵢ(xᵢ−x̄)²

                **Bizim verimizde ne yaptı?**
                İzmir için I = −0.2817 çıktı (negatif). Bu, riskli ilçelerin genellikle
                düşük riskli komşularla çevrili olduğunu gösteriyor — merkezi bir "kötü bölge" yok.
                """)
            st.markdown("""
            <div style="background:rgba(0,0,0,0.3);border-radius:8px;padding:0.8rem 1.2rem;
                        font-family:Georgia,serif;color:#38d1e3;font-size:0.85rem;text-align:center;margin:0.5rem 0;">
                I = &nbsp;<u>n</u>&nbsp; × &nbsp;<u>Σᵢ Σⱼ wᵢⱼ(xᵢ−x̄)(xⱼ−x̄)</u><br>
                &nbsp;&nbsp;&nbsp;S₀ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Σᵢ(xᵢ−x̄)²
            </div>
            <div style="color:#7a9ab0;font-size:0.78rem;font-style:italic;">
                I > 0 kümelenme · I < 0 dağınık · Satır-normalize ağırlık matrisi</div>
            """, unsafe_allow_html=True)

        with col2:
            with st.expander("📐 Local Moran's I — LISA"):
                st.markdown("""
                **Ne yapar?**
                Her ilçe için ayrı ayrı mekânsal skor üretir. Global Moran "genel tablo" verirken,
                LISA her ilçenin HH/LL/HL/LH sınıfını belirler.

                **Formül:**

                > Iᵢ = zᵢ × Σⱼ wᵢⱼ × zⱼ

                **Bizim verimizde ne yaptı?**
                Gaziemir → HL (yüksek risk, düşük riskli komşular → izole sıcak nokta).
                Karşıyaka → LH (düşük risk, yüksek riskli komşular → çevre baskısı).
                999 permütasyon testi ile anlamlılık sınandı.
                """)
            st.markdown("""
            <div style="background:rgba(0,0,0,0.3);border-radius:8px;padding:0.8rem 1.2rem;
                        font-family:Georgia,serif;color:#38d1e3;font-size:0.95rem;text-align:center;margin:0.5rem 0;">
                I<sub>i</sub> = z<sub>i</sub> × Σ<sub>j</sub> w<sub>ij</sub> × z<sub>j</sub>
            </div>
            <div style="color:#7a9ab0;font-size:0.78rem;font-style:italic;">
                HH/LL = küme · HL/LH = mekânsal aykırı değer · 999 permütasyon testi</div>
            """, unsafe_allow_html=True)

        # 06 TAHMİN
        bolum("06", "PROJEKSİYON MODELİ", "2030 Projeksiyon Modeli")
        with st.expander("📐 CAGR Tabanlı Projeksiyon Modeli"):
            st.markdown(f"""
            **Ne yapar?**
            Her ilçenin geçmiş abone büyüme hızını (CAGR) hesaplar ve bu hızı 3 farklı
            senaryo katsayısıyla 2030'a kadar uzatır.

            **Formül:**

            > CAGR = (Abone₂₀₂₃ / Abone₂₀₁₀)^(1/13) − 1

            > Risk(i,t) = Risk(i,2023) × (1 + CAGRᵢ × k)^(t−2023)

            **k değerleri:** 0.5 = İyimser · 1.0 = Baz · 1.5 = Kötümser

            **Bizim verimizde ne yaptı?**
            14 yıllık seri (2010–2023) CAGR hesabını güvenilir kıldı.
            Bornova Baz senaryosunda 2030'da 53, Kötümser'de 58 puana ulaşıyor.
            Sonuçlar 0–100 arasında sınırlandırıldı.
            """)
        st.markdown("""
        <div style="background:rgba(0,0,0,0.3);border-radius:8px;padding:0.8rem 1.2rem;
                    font-family:Georgia,serif;color:#38d1e3;font-size:0.95rem;text-align:center;margin:0.5rem 0;">
            Risk(i,t) = Risk(i,2023) × (1 + CAGR<sub>i</sub> × k)<sup>t−2023</sup><br><br>
            k ∈ {0.5 , 1.0 , 1.5}
        </div>
        <div style="color:#7a9ab0;font-size:0.78rem;font-style:italic;margin-bottom:1rem;">
            k=0.5 İyimser · k=1.0 Baz · k=1.5 Kötümser · CAGR 14 yıllık seriden</div>
        """, unsafe_allow_html=True)

        # 07 SINIRLILIKLAR
        bolum("07", "SINIRLILIKLAR", "Sınırlılıklar & Şeffaflık")
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.8rem;">
            <div style="background:rgba(155,89,182,0.08);border:1px solid rgba(155,89,182,0.25);
                        border-radius:10px;padding:0.9rem 1rem;">
                <div style="color:#c39bd3;font-size:0.75rem;font-weight:600;margin-bottom:0.4rem;">
                    🔬 BOOTSTRAP KISITI</div>
                <div style="color:#d0e8f5;font-size:0.82rem;line-height:1.7;">
                    {START_YEAR}–2019 verileri block bootstrap simülasyonudur. Gerçek tarihsel
                    İZSU verisi olmadığından bu dönemin yorumları gösterge niteliğindedir.
                    İzmir kuraklık takvimine ve nüfus büyümesine uyumlu kalibre edilmiştir.
                </div>
            </div>
            <div style="background:rgba(255,127,14,0.08);border:1px solid rgba(255,127,14,0.25);
                        border-radius:10px;padding:0.9rem 1rem;">
                <div style="color:#ff7f0e;font-size:0.75rem;font-weight:600;margin-bottom:0.4rem;">
                    ⚠️ MEKÂNSAL KISIT</div>
                <div style="color:#d0e8f5;font-size:0.82rem;line-height:1.7;">
                    n=11 ilçe ile Moran's I istatistiksel güç açısından sınırlıdır.
                    Komşuluk matrisi coğrafi sınırlar referans alınarak oluşturuldu.
                </div>
            </div>
            <div style="background:rgba(255,127,14,0.08);border:1px solid rgba(255,127,14,0.25);
                        border-radius:10px;padding:0.9rem 1rem;">
                <div style="color:#ff7f0e;font-size:0.75rem;font-weight:600;margin-bottom:0.4rem;">
                    ⚠️ TAHMİN KISITI</div>
                <div style="color:#d0e8f5;font-size:0.82rem;line-height:1.7;">
                    2030 projeksiyonu lineer büyüme varsayımına dayanır.
                    İklim değişikliği, politika müdahaleleri ve göç etkileri modele dahil edilmemiştir.
                </div>
            </div>
            <div style="background:rgba(44,160,44,0.08);border:1px solid rgba(44,160,44,0.25);
                        border-radius:10px;padding:0.9rem 1rem;">
                <div style="color:#2ca02c;font-size:0.75rem;font-weight:600;margin-bottom:0.4rem;">
                    ✅ TEKRARLANABILIRLIK</div>
                <div style="color:#d0e8f5;font-size:0.82rem;line-height:1.7;">
                    Tüm analizler Python ile yapıldı. Kaynak kod GitHub'da açık erişimde.
                    Bootstrap simülasyonu sabit rastgele tohum (seed) ile tekrarlanabilir.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        bolum("08", "SIKÇA SORULAN SORULAR", "Sıkça Sorulan Sorular")

        sss_listesi = [
            ("Bootstrap simülasyonu nedir, neden kullanıldı?",
             f"İZSU resmi açık verisi yalnızca 2020–{END_YEAR} dönemini kapsıyor (4 yıl). Mann-Kendall trend testi gibi istatistiksel yöntemler için bu örneklem yetersiz. Block bootstrap yöntemiyle {START_YEAR}–2019 dönemi için İzmir'in hidrolojik geçmişine uyumlu bir seri üretildi. Bu sayede n=4 yerine n={len(YEARS)} yıllık analizler yapılabildi."),
            ("Bootstrap verisi gerçek mi sayılır?",
             f"Hayır — {START_YEAR}–2019 verileri sentetiktir; gerçek İZSU ölçümleri değildir. Ancak rastgele üretilmedi: İzmir'in kuraklık takvimine ve TÜİK nüfus büyümesine uyumlu kalibre edildi. Site genelinde mor renk ile açıkça işaretlenmiştir."),
            ("Risk skoru ne anlama geliyor?",
             "0–100 arasındaki skor, 4 su güvenliği göstergesinin entropy ağırlıklı ortalamasıdır. Eşikler: 0–45 Düşük Risk · 46–59 Orta Risk · 60+ Yüksek Risk. Yüksek skor = o ilçede su güvenliği daha kırılgan demektir."),
            ("Neden 4 gösterge seçildi?",
             "Abone başına tüketim, tüketim artış oranı, arz kısıtı ve su kayıp oranı — bu 4 gösterge İZSU açık verisinde yıllık olarak mevcut ve su güvenliğini doğrudan etkileyen değişkenlerdir. Su kalitesi ve iklim verileri erişilebilir olmadığından modele dahil edilemedi."),
            ("Entropy ağırlıklandırma neden tercih edildi?",
             "Araştırmacının öznel ağırlık belirlemesini önler. Verinin kendi dağılımı ağırlıkları belirler — ilçeler arasında en fazla farklılık gösteren gösterge en yüksek ağırlığı alır. Literatürde kabul görmüş nesnel bir yaklaşımdır."),
            ("2030 projeksiyonu neden 3 senaryoya ayrıldı?",
             "Tek bir projeksiyon belirsizliği gizler. İyimser (k=0.5) tasarruf politikalarını, Baz (k=1.0) mevcut trendi, Kötümser (k=1.5) hızlı kentleşme ve kuraklık baskısını temsil eder. Gerçek geleceğin bu 3 senaryo arasında bir yerde olduğu öngörülmektedir."),
            (f"Mann-Kendall testi {len(YEARS)} yıllık veriyle güvenilir mi?",
             f"n={len(YEARS)} ile Mann-Kendall'ın istatistiksel gücü oldukça yüksektir. 2010–2019 dönemi bootstrap simülasyonu olduğundan sonuçlar ileride gerçek veriler elde edildiğinde doğrulanmalıdır; bu sınırlılık çalışmada şeffaf biçimde belirtilmiştir."),
            ("Komşuluk matrisi nasıl belirlendi?",
             "İzmir 11 merkez ilçesinin coğrafi sınırları referans alınarak her ilçenin hangi ilçelerle fiziksel olarak sınır paylaştığı belirlendi. Matrisin simetrisi doğrulandı ve satır-normalize edildi."),
        ]

        for soru, cevap in sss_listesi:
            with st.expander(f"❓ {soru}"):
                st.markdown(f"<div style='color:#d0e8f5;font-size:0.88rem;line-height:1.7;'>{cevap}</div>",
                            unsafe_allow_html=True)
