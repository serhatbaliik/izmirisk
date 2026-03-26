import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="AquaRisk İzmir",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    h1 { color: #1B4F72; font-size: 1.8rem; }
    h2 { color: #1B4F72; font-size: 1.3rem; }
    h3 { color: #2874A6; font-size: 1.1rem; }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        border: 1px solid #e2e8f0;
        text-align: center;
    }
    .risk-low { color: #2ca02c; font-weight: 600; }
    .risk-med { color: #ff7f0e; font-weight: 600; }
    .risk-high { color: #d62728; font-weight: 600; }
    .stAlert { border-radius: 10px; }
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
    recs = {
        "Düşük Risk": [
            "Mevcut su tasarrufu uygulamalarını sürdürün.",
            "Abone başına tüketimi izlemeye devam edin.",
            "Komşu ilçelerdeki risk artışlarını takip edin.",
        ],
        "Orta Risk": [
            "Su tasarrufu kampanyaları başlatın.",
            "Altyapı sızıntı tespiti ve onarımlarını hızlandırın.",
            "Yüksek tüketen abonelere bilinçlendirme yapın.",
            "Alternatif su kaynakları araştırın.",
        ],
        "Yüksek Risk": [
            "ACİL: Su kısıtlama önlemleri alın.",
            "Yüksek tüketen sektörleri denetleyin.",
            "Yağmur suyu hasadı sistemleri kurun.",
            "Geri dönüştürülmüş su kullanımını artırın.",
            "İZSU ile acil eylem planı oluşturun.",
        ]
    }
    return recs.get(str(sinif), recs["Orta Risk"])


# ── Veri yükle
try:
    tablo1, tablo2, abone_df = load_data()
    risk_df, W = compute_risk(tablo1, tablo2)
    tahmin_df, cagr_dict = compute_forecast(risk_df, abone_df)
    data_loaded = True
except Exception as e:
    data_loaded = False
    st.error(f"Veri yüklenemedi: {e}")

if data_loaded:
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Izmir_seal.svg/200px-Izmir_seal.svg.png", width=80)
        st.title("💧 AquaRisk İzmir")
        st.caption("Su Güvenliği Risk Endeksi")
        st.divider()

        sayfa = st.radio("Sayfa seç:", [
            "🏠 Ana Sayfa",
            "📊 EDA Analizi",
            "📈 Risk Endeksi",
            "🔮 2040 Tahmin",
            "🗺️ İzmir Risk Haritası",
            "🗺️ Mekânsal Analiz",
            "💡 Öneriler"
        ])

        st.divider()
        st.caption("Veri: İZSU (2020–2023)")
        st.caption("Yöntem: Entropy-WSRI, Mann-Kendall, LISA")
    # ════════════════════════════════
    # ANA SAYFA
    # ════════════════════════════════
    if sayfa == "🏠 Ana Sayfa":
        st.title("💧 İzmir Su Güvenliği Risk Endeksi")
        st.markdown("**2020–2023 verilerine dayanan entropy ağırlıklı bileşik risk analizi — 11 merkez ilçe**")
        st.divider()

        # KPI kartları
        df23 = risk_df[risk_df["Yıl"]==2023].sort_values("Risk_Skor", ascending=False)
        en_riskli = df23.iloc[0]
        en_az = df23.iloc[-1]
        orta_sayi = len(df23[df23["Risk_Sınıf"]=="Orta Risk"])

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("En Riskli İlçe", en_riskli["İlçe"], f"Skor: {en_riskli['Risk_Skor']:.1f}")
        c2.metric("En Az Riskli", en_az["İlçe"], f"Skor: {en_az['Risk_Skor']:.1f}")
        c3.metric("Orta Risk İlçe", f"{orta_sayi} ilçe", "2023 yılı")
        c4.metric("Tahtalı Doluluk", f"%{tablo2[tablo2['Yıl']==2023]['Tahtalı_Doluluk_%'].values[0]:.1f}", "2023 yılı")

        st.divider()

        # Risk sıralaması
        col1, col2 = st.columns([2,1])
        with col1:
            st.subheader("2023 Yılı Risk Sıralaması")
            fig = go.Figure()
            colors = [get_risk_color(s) for s in df23["Risk_Skor"]]
            fig.add_trace(go.Bar(
                x=df23["Risk_Skor"], y=df23["İlçe"],
                orientation='h',
                marker_color=colors,
                text=df23["Risk_Skor"].round(1),
                textposition='outside',
                hovertemplate="%{y}<br>Risk: %{x:.1f}<extra></extra>"
            ))
            fig.add_vline(x=40, line_dash="dot", line_color="orange", line_width=1.5)
            fig.add_vline(x=70, line_dash="dot", line_color="red", line_width=1.5)
            fig.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                height=380, margin=dict(t=20,b=20,l=10,r=60),
                xaxis=dict(range=[0,80], gridcolor="#eee"),
                yaxis=dict(autorange="reversed")
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Entropy Ağırlıkları")
            labels = ["Kayıp Oranı","Talep","Arz Kısıtı","Tüketim Artışı"]
            fig2 = go.Figure(go.Pie(
                labels=labels, values=W.round(4),
                hole=0.4,
                marker=dict(colors=["#d62728","#1f77b4","#2ca02c","#ff7f0e"]),
                textinfo="percent",
                hovertemplate="%{label}: %{value:.4f}<extra></extra>"
            ))
            fig2.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                height=280, margin=dict(t=20,b=20,l=10,r=10),
                showlegend=True,
                legend=dict(font=dict(size=10))
            )
            st.plotly_chart(fig2, use_container_width=True)

            st.info("**Veri kaynağı:** İZSU Açık Veri Portalı\n\n**Kapsam:** 2020–2023, 11 merkez ilçe\n\n**Yöntem:** Min-Max + Entropy + WSRI")

    # ════════════════════════════════
    # EDA ANALİZİ
    # ════════════════════════════════
    elif sayfa == "📊 EDA Analizi":
        st.title("📊 Keşifsel Veri Analizi")
        st.divider()

        tab1, tab2, tab3 = st.tabs(["Baraj Doluluk", "İlçe Tüketim", "Arz-Talep"])

        with tab1:
            st.subheader("Baraj Doluluk Oranları (2020–2023)")
            esik = float(pd.concat([tablo2["Tahtalı_Doluluk_%"],
                                     tablo2["Balçova_Doluluk_%"],
                                     tablo2["Gördes_Doluluk_%"]]).quantile(0.25))
            fig = go.Figure()
            for baraj, renk in [("Tahtalı_Doluluk_%","#1f77b4"),
                                  ("Balçova_Doluluk_%","#2ca02c"),
                                  ("Gördes_Doluluk_%","#d62728")]:
                isim = baraj.replace("_Doluluk_%","")
                fig.add_trace(go.Scatter(
                    x=[2020,2021,2022,2023], y=tablo2[baraj],
                    mode="lines+markers", name=isim,
                    line=dict(color=renk,width=2.5), marker=dict(size=9),
                    hovertemplate=f"{isim}: %{{y:.1f}}%<extra></extra>"
                ))
            fig.add_hline(y=esik, line_dash="dash", line_color="orange",
                          annotation_text=f"Kritik eşik Q1: {esik:.1f}%")
            fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",
                              height=380,xaxis=dict(tickvals=[2020,2021,2022,2023],gridcolor="#eee"),
                              yaxis=dict(title="Doluluk (%)",gridcolor="#eee",range=[0,65]),
                              hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
            st.caption(f"Kritik eşik veri temelli belirlendi: tüm doluluk değerlerinin alt çeyreği Q1 = %{esik:.1f}")

        with tab2:
            st.subheader("Abone Başına Tüketim Isı Haritası")
            pivot = tablo1.pivot(index="İlçe",columns="Yıl",values="AbbTuketim")
            fig = go.Figure(go.Heatmap(
                z=pivot.values, x=[str(y) for y in pivot.columns],
                y=pivot.index.tolist(), colorscale="YlOrRd",
                text=pivot.values.round(0).astype(int),
                texttemplate="%{text}",
                hovertemplate="İlçe: %{y}<br>Yıl: %{x}<br>%{z:.1f} m³/abone<extra></extra>",
                colorbar=dict(title="m³/abone")
            ))
            fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",
                              height=420,margin=dict(l=120))
            st.plotly_chart(fig, use_container_width=True)

        with tab3:
            st.subheader("Arz-Talep Dengesi")
            fig = go.Figure()
            fig.add_trace(go.Bar(x=[2020,2021,2022,2023],
                y=tablo2["Sisteme_Giren_m3"]/1e6, name="Sisteme Giren Su",
                marker_color="#1f77b4", opacity=0.85))
            fig.add_trace(go.Bar(x=[2020,2021,2022,2023],
                y=tablo2["Toplam_Üretim_m3"]/1e6, name="Toplam Üretim",
                marker_color="#2ca02c", opacity=0.85))
            fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",
                              barmode="group",height=380,
                              yaxis=dict(title="Milyon m³",gridcolor="#eee"),
                              hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)

    # ════════════════════════════════
    # RİSK ENDEKSİ
    # ════════════════════════════════
    elif sayfa == "📈 Risk Endeksi":
        st.title("📈 Su Güvenliği Risk Endeksi (WSRI)")
        st.divider()

        yil_sec = st.slider("Yıl seç:", 2020, 2023, 2023)
        df_yil = risk_df[risk_df["Yıl"]==yil_sec].sort_values("Risk_Skor",ascending=False)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"{yil_sec} Yılı Risk Skorları")
            colors = [get_risk_color(s) for s in df_yil["Risk_Skor"]]
            fig = go.Figure(go.Bar(
                x=df_yil["İlçe"], y=df_yil["Risk_Skor"],
                marker_color=colors, opacity=0.85,
                text=df_yil["Risk_Skor"].round(1),
                textposition="outside",
                hovertemplate="%{x}<br>Risk: %{y:.1f}<extra></extra>"
            ))
            fig.add_hline(y=40,line_dash="dot",line_color="orange",
                          annotation_text="Düşük/Orta sınırı")
            fig.add_hline(y=70,line_dash="dot",line_color="red",
                          annotation_text="Orta/Yüksek sınırı")
            fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",
                              height=380,xaxis=dict(tickangle=30),
                              yaxis=dict(range=[0,85],gridcolor="#eee"))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader(f"{yil_sec} Risk Isı Haritası")
            pivot = risk_df.pivot(index="İlçe",columns="Yıl",values="Risk_Skor")
            fig = go.Figure(go.Heatmap(
                z=pivot.values, x=[str(y) for y in pivot.columns],
                y=pivot.index.tolist(), colorscale="RdYlGn_r",
                text=pivot.values.round(1),
                texttemplate="%{text}",
                hovertemplate="İlçe: %{y}<br>Yıl: %{x}<br>Risk: %{z:.1f}<extra></extra>",
                colorbar=dict(title="Risk Skoru")
            ))
            fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",
                              height=380,margin=dict(l=120))
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("İlçe Detayı")
        ilce_sec = st.selectbox("İlçe seç:", sorted(risk_df["İlçe"].unique()))
        df_ilce = risk_df[risk_df["İlçe"]==ilce_sec].sort_values("Yıl")
        skor_2023 = df_ilce[df_ilce["Yıl"]==2023]["Risk_Skor"].values[0]
        sinif_2023 = df_ilce[df_ilce["Yıl"]==2023]["Risk_Sınıf"].values[0]

        c1,c2,c3 = st.columns(3)
        c1.metric("2023 Risk Skoru", f"{skor_2023:.1f}")
        c2.metric("Risk Sınıfı", str(sinif_2023))
        c3.metric("CAGR (Abone)", f"%{cagr_dict.get(ilce_sec,0)*100:.2f}/yıl")

    # ════════════════════════════════
    # TAHMİN
    # ════════════════════════════════
    elif sayfa == "🔮 2040 Tahmin":
        st.title("🔮 2040 Yılı Risk Projeksiyonu")
        st.divider()

        senaryo = st.radio("Senaryo:", ["Baz","İyimser","Kötümser"], horizontal=True)
        hedef_yil = st.slider("Hedef yıl:", 2024, 2040, 2030)

        df_hedef = tahmin_df[tahmin_df["Yıl"]==hedef_yil].sort_values(senaryo,ascending=False)
        colors = [get_risk_color(s) for s in df_hedef[senaryo]]

        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"{hedef_yil} Yılı — {senaryo} Senaryo")
            fig = go.Figure(go.Bar(
                x=df_hedef["İlçe"], y=df_hedef[senaryo],
                marker_color=colors, opacity=0.85,
                text=df_hedef[senaryo].round(1),
                textposition="outside",
                hovertemplate="%{x}: %{y:.1f}<extra></extra>"
            ))
            fig.add_hline(y=40,line_dash="dot",line_color="orange")
            fig.add_hline(y=70,line_dash="dot",line_color="red")
            fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",
                              height=380,xaxis=dict(tickangle=30),
                              yaxis=dict(range=[0,100],gridcolor="#eee"))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Projeksiyon Trendi")
            ilce_sec = st.selectbox("İlçe seç:", sorted(tahmin_df["İlçe"].unique()))

            hist = risk_df[risk_df["İlçe"]==ilce_sec].sort_values("Yıl")
            pred = tahmin_df[tahmin_df["İlçe"]==ilce_sec].sort_values("Yıl")

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hist["Yıl"], y=hist["Risk_Skor"],
                mode="lines+markers", name="Gerçek veri",
                line=dict(color="#1B4F72",width=2.5), marker=dict(size=8)
            ))
            fig.add_trace(go.Scatter(
                x=pred["Yıl"], y=pred[senaryo],
                mode="lines", name=f"{senaryo} senaryo",
                line=dict(color="#d62728",width=2,dash="dash")
            ))
            fig.add_trace(go.Scatter(
                x=list(pred["Yıl"])+list(pred["Yıl"])[::-1],
                y=list(pred["Kötümser"])+list(pred["İyimser"])[::-1],
                fill="toself", fillcolor="rgba(214,39,40,0.1)",
                line=dict(color="rgba(0,0,0,0)"),
                name="Senaryo bandı", hoverinfo="skip"
            ))
            fig.add_hline(y=40,line_dash="dot",line_color="orange")
            fig.add_hline(y=70,line_dash="dot",line_color="red")
            fig.add_vline(x=2023.5,line_dash="dash",line_color="gray",
                          annotation_text="Tahmin →")
            fig.update_layout(
                plot_bgcolor="white",paper_bgcolor="white",height=380,
                xaxis=dict(gridcolor="#eee",tickvals=list(range(2020,2041,5))),
                yaxis=dict(title="Risk Skoru",gridcolor="#eee",range=[0,100]),
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)

    # ════════════════════════════════
    # MEKÂNSAL ANALİZ
    # ════════════════════════════════
    elif sayfa == "🗺️ Mekânsal Analiz":
        st.title("🗺️ Mekânsal Analiz — Moran's I + LISA")
        st.divider()

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

        c1,c2,c3 = st.columns(3)
        c1.metric("Global Moran's I", f"{I_glob}")
        c2.metric("p-değeri", f"{p_glob}")
        c3.metric("Yorum", "Negatif otokorelasyon")

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Moran Scatter Plot")
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
            fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",height=380,
                xaxis=dict(title="Standardize Risk (z)",gridcolor="#eee"),
                yaxis=dict(title="Mekânsal Lag (Wz)",gridcolor="#eee"))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("LISA Sınıflandırması")
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
        st.title("💡 İlçe Bazlı Öneriler")
        st.divider()

        ilce_sec = st.selectbox("İlçe seç:", sorted(risk_df["İlçe"].unique()))
        df_ilce = risk_df[risk_df["İlçe"]==ilce_sec]
        skor = df_ilce[df_ilce["Yıl"]==2023]["Risk_Skor"].values[0]
        sinif = df_ilce[df_ilce["Yıl"]==2023]["Risk_Sınıf"].values[0]
        renk = get_risk_color(skor)

        col1, col2 = st.columns([1,2])
        with col1:
            st.markdown(f"""
            <div style='background:white;border-radius:12px;padding:20px;
                        border:2px solid {renk};text-align:center;'>
                <h2 style='color:#1B4F72;margin:0'>{ilce_sec}</h2>
                <p style='font-size:2rem;font-weight:600;color:{renk};margin:10px 0'>
                    {skor:.1f}
                </p>
                <p style='color:{renk};font-weight:600;font-size:1.1rem;margin:0'>
                    {sinif}
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.divider()
            pred_2040 = tahmin_df[(tahmin_df["İlçe"]==ilce_sec)&(tahmin_df["Yıl"]==2040)]
            st.metric("2040 Baz Tahmin", f"{pred_2040['Baz'].values[0]:.1f}")
            st.metric("2040 Kötümser", f"{pred_2040['Kötümser'].values[0]:.1f}")
            st.metric("2040 İyimser", f"{pred_2040['İyimser'].values[0]:.1f}")

        with col2:
            st.subheader("Risk Trendi")
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
            fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",height=280,
                xaxis=dict(gridcolor="#eee"),
                yaxis=dict(title="Risk Skoru",gridcolor="#eee",range=[0,100]),
                hovermode="x unified",margin=dict(t=10))
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Öneriler")
            recs = get_recommendation(ilce_sec, skor, sinif)
            for rec in recs:
                st.markdown(f"• {rec}")
# ════════════════════════════════
    # İZMİR RİSK HARİTASI
    # ════════════════════════════════
    elif sayfa == "🗺️ İzmir Risk Haritası":
        st.title("🗺️ İzmir İlçe Risk Haritası")
        st.markdown("Gerçek ilçe sınırları üzerinde risk skorları — yıl ve senaryo seçilebilir.")
        st.divider()

        import json
        import requests

        # GeoJSON URL — Türkiye ilçe sınırları
        with open("izmir.geojson", "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

        @st.cache_data
            r = requests.get(GEOJSON_URL, timeout=30)
            return r.json()

        col1, col2, col3 = st.columns(3)
        with col1:
            harita_yil = st.slider("Yıl:", 2020, 2040, 2023, key="harita_yil")
        with col2:
            harita_senaryo = st.radio("Senaryo:", ["Baz","İyimser","Kötümser"],
                                       horizontal=True, key="harita_senaryo")
        with col3:
            st.metric("Seçili Yıl", harita_yil)

        # Risk skorlarını hesapla
        def get_risk_score(ilce, yil, senaryo):
            if yil <= 2023:
                row = risk_df[(risk_df["İlçe"]==ilce) & (risk_df["Yıl"]==yil)]
                if len(row) > 0:
                    return float(row["Risk_Skor"].values[0])
                return None
            else:
                row = tahmin_df[(tahmin_df["İlçe"]==ilce) & (tahmin_df["Yıl"]==yil)]
                if len(row) > 0:
                    return float(row[senaryo].values[0])
                return None

        ILCE_ESLESME = {
            "Balçova": "BALÇOVA",
            "Bayraklı": "BAYRAKLI",
            "Bornova": "BORNOVA",
            "Buca": "BUCA",
            "Çiğli": "ÇİĞLİ",
            "Gaziemir": "GAZİEMİR",
            "Güzelbahçe": "GÜZELBAHÇE",
            "Karabağlar": "KARABAĞLAR",
            "Karşıyaka": "KARŞIYAKA",
            "Konak": "KONAK",
            "Narlıdere": "NARLIDERE",
        }

        try:

            # İzmir ilçelerini filtrele
            izmir_features = []
            for feature in geojson_data["features"]:
                props = feature.get("properties", {})
                name = props.get("name", "") or props.get("NAME_2", "") or props.get("ilce", "")
                if name in ILCE_ESLESME:
                    ilce_kodu = ILCE_ESLESME[name]
                    skor = get_risk_score(ilce_kodu, harita_yil, harita_senaryo)
                    feature["properties"]["risk_skor"] = skor if skor else 0
                    feature["properties"]["ilce_adi"] = ilce_kodu
                    feature["properties"]["risk_sinif"] = get_risk_label(skor) if skor else "Bilinmiyor"
                    izmir_features.append(feature)

            izmir_geojson = {"type": "FeatureCollection", "features": izmir_features}

            # Skor tablosu
            skor_listesi = []
            for geo_isim, kod in ILCE_ESLESME.items():
                skor = get_risk_score(kod, harita_yil, harita_senaryo)
                if skor:
                    skor_listesi.append({
                        "İlçe": kod,
                        "Risk Skoru": round(skor, 1),
                        "Sınıf": get_risk_label(skor)
                    })

            skor_df = pd.DataFrame(skor_listesi).sort_values("Risk Skoru", ascending=False)

            # Plotly choropleth haritası
            fig_harita = go.Figure(go.Choropleth(
                geojson=izmir_geojson,
                locations=[f["properties"]["ilce_adi"] for f in izmir_features],
                z=[f["properties"]["risk_skor"] for f in izmir_features],
                featureidkey="properties.ilce_adi",
                colorscale=[
                    [0.0, "#2ca02c"],
                    [0.4, "#2ca02c"],
                    [0.4, "#ff7f0e"],
                    [0.7, "#ff7f0e"],
                    [0.7, "#d62728"],
                    [1.0, "#d62728"],
                ],
                zmin=0, zmax=100,
                colorbar=dict(
                    title="Risk Skoru",
                    tickvals=[20, 40, 55, 70, 85],
                    ticktext=["20", "40 (Düşük/Orta)", "55", "70 (Orta/Yüksek)", "85"]
                ),
                hovertemplate="<b>%{location}</b><br>Risk Skoru: %{z:.1f}<extra></extra>"
            ))

            fig_harita.update_geos(
                fitbounds="locations",
                visible=False,
                bgcolor="lightblue"
            )
            fig_harita.update_layout(
                title=f"İzmir İlçe Risk Haritası — {harita_yil} ({harita_senaryo} Senaryo)",
                height=550,
                margin=dict(t=50, b=0, l=0, r=0),
                paper_bgcolor="white",
                geo=dict(
                    showland=True,
                    landcolor="#e8f4f8",
                    showocean=True,
                    oceancolor="#cce5f0",
                    showcoastlines=True,
                    coastlinecolor="white",
                )
            )
            st.plotly_chart(fig_harita, use_container_width=True)

            # Risk tablosu
            col1, col2 = st.columns([2,1])
            with col1:
                st.subheader("İlçe Risk Sıralaması")
                st.dataframe(skor_df, use_container_width=True, hide_index=True)
            with col2:
                st.subheader("Renk Açıklaması")
                st.markdown("""
                🟢 **Düşük Risk** (0–40)
                Risk henüz kritik seviyede değil.

                🟡 **Orta Risk** (40–70)
                Dikkat ve önlem gerekiyor.

                🔴 **Yüksek Risk** (70–100)
                Acil müdahale gerekli.
                """)
                if harita_yil > 2023:
                    st.info(f"📊 {harita_yil} yılı tahmini — {harita_senaryo} senaryo")
                else:
                    st.success(f"📊 {harita_yil} yılı gerçek veri")

        except Exception as e:
            st.error(f"Harita yüklenemedi: {e}")
            st.info("GeoJSON verisi yüklenirken hata oluştu. Lütfen internet bağlantısını kontrol edin.")
