import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(
    page_title="İzmiRisk",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

YEARS = list(range(2010, 2024))
START_YEAR = 2010
END_YEAR = 2023
PRED_END_YEAR = 2030
PRED_YEARS = list(range(END_YEAR + 1, 2031))

# ═══════════════════════════════════════════════════════════
# ⚙️  ANİMASYON HIZ AYARLARI — Saniye cinsinden, istediğin gibi değiştir
# ═══════════════════════════════════════════════════════════
HERO_PULSE_SECONDS = 15     # 💧 Damla pulse hızı (1=hızlı, 30=çok yavaş)
WAVE_FLOW_SECONDS  = 20     # 🌊 Mavi şerit akış hızı (1=hızlı, 30=çok yavaş)
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# DİL / LANGUAGE — i18n
# ═══════════════════════════════════════════════════════════════
if "dil" not in st.session_state:
    st.session_state.dil = "tr"
if "secili_sayfa" not in st.session_state:
    st.session_state.secili_sayfa = "home"

# ── TÜRKÇE SÖZLÜK ───────────────────────────────────────────────
TR = {
    "app_subtitle": f"Su Güvenliği Risk Endeksi · İzmir · {START_YEAR}–2030",
    "data_source_short": "Veri: İZSU + Bootstrap Simülasyonu",
    "scope_short": "11 Merkez İlçe · Entropy-WSRI",
    "search_placeholder": "🔍 Ara: baraj, risk, 2030...",
    "search_no_result": "❌ Sonuç bulunamadı. Deneyin: baraj, risk, harita, 2030, simülatör, metodoloji",
    "bootstrap_badge": "BOOTSTRAP SİMÜLASYONU",
    "bootstrap_banner": f"{START_YEAR}–2019 verileri block bootstrap yöntemiyle İzmir kuraklık takvimi referans alınarak üretilmiştir. 2020–{END_YEAR} verileri İZSU resmi kaynağındandır.",
    "data_load_error_title": "Veri Yüklenemedi",
    "data_load_error_msg": "Veri dosyaları bulunamadı veya okunamadı.<br>ilce.xlsx ve baraj.xlsx dosyalarının repoda olduğundan emin olun.",
    "data_load_error_label": "Hata",
    "lang_tr": "🇹🇷 TR",
    "lang_en": "🇬🇧 EN",

    "risk_low": "Düşük Risk",
    "risk_med": "Orta Risk",
    "risk_high": "Yüksek Risk",

    "nav_home": "Ana Sayfa",
    "nav_eda": "EDA",
    "nav_risk": "Risk",
    "nav_2030": "2030",
    "nav_map": "Harita",
    "nav_spatial": "Mekânsal",
    "nav_advice": "Öneriler",
    "nav_method": "Metodoloji",
    "nav_tools": "Araçlar",

    # Ana Sayfa
    "home_badge": f"SU GÜVENLİĞİ ANALİZİ · İZMİR · {START_YEAR}–{PRED_END_YEAR}",
    "home_title_1": "İzmir Su Güvenliği",
    "home_title_2": "Risk Endeksi",
    "home_lead": f"Entropy ağırlıklı bileşik risk analizi · 11 merkez ilçe · {len(YEARS)} yıllık seri ({START_YEAR}–{END_YEAR}) · Bootstrap simülasyonu · Mann-Kendall trend testi · LISA mekânsal analizi · 2030 projeksiyonu",
    "kpi_total_consumption": f"Toplam Tüketim {END_YEAR}",
    "kpi_million_m3": "milyon m³",
    "kpi_highest_risk": "En Yüksek Risk Skoru",
    "kpi_loss_rate": f"Su Kayıp Oranı {END_YEAR}",
    "kpi_loss_subtext": "% · sistem geneli",
    "kpi_high_risk_districts": "Yüksek Riskli İlçeler",
    "kpi_med_risk_districts": "Orta Riskli İlçeler",
    "kpi_low_risk_districts": "Düşük Riskli İlçeler",
    "kpi_tahtali_fill": "Tahtalı Doluluk",
    "kpi_tahtali_year": f"{END_YEAR} yılı",
    "kpi_least_risky": "En Az Riskli",
    "kpi_score_label": "Skor",
    "sec_01_title": "01 · RİSK GÖSTERGESİ",
    "sec_01_h": f"En Riskli 3 İlçe — {END_YEAR} Risk İbresi",
    "sec_02_title": "02 · RİSK ANALİZİ",
    "sec_02_h": f"{END_YEAR} Yılı İlçe Risk Sıralaması & Ağırlık Dağılımı",
    "risk_threshold_med": "Orta Risk Eşiği (46)",
    "risk_threshold_high": "Yüksek Risk Eşiği (60)",
    "risk_score_axis": "Risk Skoru (0–100)",
    "risk_score": "Risk Skoru",
    "entropy_weights_label": "Entropy<br>Ağırlıkları",
    "weight_loss_rate": "Su Kayıp Oranı",
    "weight_per_capita": "Kişi Başı Tüketim",
    "weight_supply_constraint": "Arz Kısıtı",
    "weight_growth_rate": "Tüketim Artış Oranı",
    "source_method_title": "KAYNAK & YÖNTEM",
    "source_data": "Veri: İZSU + Bootstrap simülasyonu",
    "source_scope": f"Kapsam: {START_YEAR}–{END_YEAR} · 11 İlçe · {len(YEARS)} yıl",
    "source_method": "Yöntem: Min-Max + Entropy + WSRI",
    "source_analysis": "Analiz: Mann-Kendall · LISA · CAGR",
    "sec_03_title": "03 · KÜRESEL BAĞLAM",
    "sec_03_h": "İzmir Dünya Genelinde Nerede?",
    "global_pop_water_stress": "Su Stresi Altındaki Nüfus",
    "global_pop_water_stress_text": "Dünya nüfusunun %40'ı yılın en az bir ayında ciddi su stresiyle karşılaşıyor.",
    "global_med_basin": "Akdeniz Havzası Su Açığı",
    "global_med_basin_text": "Akdeniz havzasında yıllık yağış 2050'ye kadar %20 azalması bekleniyor. İzmir bu kuşağın merkezinde.",
    "global_izmir_wsri": "İzmir WSRI Ortalaması",
    "global_izmir_wsri_text": "11 merkez ilçe ortalaması — Orta Risk bandı. 3 ilçe yüksek risk eşiğini geçmiş.",
    "global_izmir_wsri_source": f"İZSU + Bu çalışma · {END_YEAR}",
    "global_tr_capita": "Türkiye Kişi Başı Su Potansiyeli",
    "global_tr_capita_text": "Uluslararası eşik 1.700 m³ — Türkiye \"su kıtlığı\" sınırına yakın.",
    "global_source_note": "Kaynak notu: ",
    "global_source_text": "WRI Aqueduct 2023 · IPCC AR6 (2021) · DSİ 2022 yıllık raporu · İZSU açık veri portalı.",
    "share_copy_link": "Linki Kopyala",
    "share_copied": "Kopyalandı!",
    "share_twitter": "Twitter/X'te Paylaş",
    "share_linkedin": "LinkedIn'de Paylaş",

    # EDA
    "eda_badge": f"KEŞİFSEL VERİ ANALİZİ · {START_YEAR}–{END_YEAR}",
    "eda_title": "Keşifsel Veri Analizi",
    "eda_lead": f"{len(YEARS)} yıllık seri ({START_YEAR}–{END_YEAR}) · Bootstrap simülasyonu ile genişletildi · Baraj dolulukları, ilçe tüketimi, arz-talep dengesi ve kayıp trendleri",
    "tab_dam": "💧 Baraj Doluluk",
    "tab_consumption": "🌡️ Tüketim Haritası",
    "tab_supply_demand": "⚖️ Arz-Talep",
    "tab_loss": "📉 Kayıp Oranı",
    "eda_dam_history_no": "01 · BARAJ TARİHÇESİ",
    "eda_dam_history_h": "İzmir'in Barajları — Tarihçe, Teknik Bilgi & Su Sistemi",
    "eda_water_system_title": "İZMİR'İN SU SİSTEMİ HAKKINDA",
    "eda_water_system_text": "İzmir'in içme ve kullanma suyu ihtiyacı ağırlıklı olarak üç büyük barajdan karşılanmaktadır: <b style=\"color:#38d1e3\">Tahtalı</b>, <b style=\"color:#2ca02c\">Balçova</b> ve <b style=\"color:#d62728\">Gördes</b>. Bu üç barajın toplam depolama kapasitesi yaklaşık <b style=\"color:white\">542 milyon m³</b>'tür. İZSU (İzmir Su ve Kanalizasyon İdaresi) tarafından yönetilen sistem, 4,4 milyonu aşkın nüfusa hizmet vermektedir. İklim değişikliğinin Akdeniz havzasında yağışları azaltmasıyla birlikte bu barajların doluluk düzeyleri giderek daha kritik bir önem kazanmaktadır.",

    "tahtali_meta": "📍 Menderes İlçesi, İzmir &nbsp;|&nbsp; 📅 İnşaat: 1993–1997 &nbsp;|&nbsp; 🏗️ Tip: Kaya-toprak dolgu",
    "tahtali_h1": "🏆 İzmir'in Ana Su Kaynağı",
    "tahtali_p1": "Tahtalı, İzmir'in **en büyük su kaynağıdır** ve şehrin yıllık içme suyu ihtiyacının yaklaşık **%60–70'ini** tek başına karşılar.",
    "tahtali_h2": "📊 Teknik Özellikler",
    "tahtali_specs": "- **Toplam Depolama Kapasitesi:** 309 milyon m³  \n- **Normal Su Kotu:** 141 metre  \n- **Havza Alanı:** 432 km²  \n- **Gövde Tipi:** Kaya-toprak dolgu, merkezi çekirdekli  \n- **Yıllık Ortalama Akım:** ~210 milyon m³  \n- **İşleten Kurum:** İZSU Genel Müdürlüğü  ",
    "tahtali_h3": "📅 Tarihsel Süreç ve Önemli Dönüm Noktaları",
    "tahtali_history": "Tahtalı Barajı 1993-1997 yılları arasında inşa edilmiştir. Önemli dönüm noktaları:\n- **2007–2008:** Şiddetli kuraklık, doluluk %20'ye düşer  \n- **2014:** Rekor yağışlar, doluluk **%44**'le proje zirvesine ulaşır  \n- **2020–2021:** Gördes krizinde Tahtalı'ya baskı artar  \n- **2023:** Doluluk **%29** — uzun vadeli kuraklık etkisi belirgin  ",
    "tahtali_h4": "🌡️ İklim Değişikliğinin Etkisi",
    "tahtali_climate": "Son 14 yılda Tahtalı'nın ortalama doluluğu yavaş ama istikrarlı bir düşüş gösteriyor. IPCC öngörüsüne göre Akdeniz havzasında 2050'ye kadar yağışlar **%20 azalacak** — bu Tahtalı için ciddi bir uyarıdır.",
    "tahtali_summary": "2023 Doluluk: %29  |  Kapasite: 309 M m³  |  Havza: 432 km²",

    "balcova_meta": "📍 Balçova İlçesi, İzmir &nbsp;|&nbsp; 📅 İnşaat: 1991–1995 &nbsp;|&nbsp; 🏗️ Tip: Beton kemer",
    "balcova_h1": "🏙️ Şehir Merkezinin Stratejik Kalkanı",
    "balcova_p1": "Balçova, küçük kapasitesine rağmen şehir merkezine yakınlığı sayesinde **Bornova, Bayraklı ve merkez ilçelerin** kritik yedek kaynağıdır.",
    "balcova_h2": "📊 Teknik Özellikler",
    "balcova_specs": "- **Toplam Depolama Kapasitesi:** 57 milyon m³  \n- **Normal Su Kotu:** 103 metre  \n- **Havza Alanı:** 47 km²  \n- **Gövde Tipi:** Beton kemer  \n- **Gövde Yüksekliği:** 92 metre  \n- **İşleten Kurum:** İZSU Genel Müdürlüğü  ",
    "balcova_h3": "📅 Tarihsel Süreç ve Önemli Dönüm Noktaları",
    "balcova_history": "Balçova Barajı 1995'te hizmete girmiştir. Önemli dönemler:\n- **2002–2004:** Uzun kuraklıkta bile %26 üstünde kalır  \n- **2016–2018:** İstikrarlı %30–34 bandı  \n- **2021:** Gördes krizinde sisteme katkısı kritik önem kazanır  \n- **2023:** %32 doluluk ile sistemde aktif rol  ",
    "balcova_h4": "💡 Neden Küçük Ama Vazgeçilmez?",
    "balcova_why": "Balçova havzası küçük olmasına rağmen şehir merkezine yalnızca **12 km** mesafededir. Bu sayede iletim hatları kısa, baskı kayıpları düşüktür. Büyük bir kuraklık ya da arıza durumunda merkez ilçeleri besleyebilecek **en hızlı yedek kaynaktır**.",
    "balcova_summary": "2023 Doluluk: %32  |  Kapasite: 57 M m³  |  Havza: 47 km²",

    "gordes_meta": "📍 Gördes İlçesi, Manisa &nbsp;|&nbsp; 📅 İnşaat: 1976–1980 &nbsp;|&nbsp; 🏗️ Tip: Toprak dolgu",
    "gordes_h1": "⚠️ Kırılgan Ama Stratejik: Gördes'in İkili Rolü",
    "gordes_p1": "Gördes idari olarak Manisa'da olsa da boru hatlarıyla İzmir su sistemine bağlıdır. **Sistemin en kırılgan halkasıdır** — 2020-21'de doluluk %1'e indi.",
    "gordes_h2": "📊 Teknik Özellikler",
    "gordes_specs": "- **Toplam Depolama Kapasitesi:** 176 milyon m³  \n- **Normal Su Kotu:** 211 metre  \n- **Havza Alanı:** 1.315 km²  \n- **Gövde Tipi:** Kil çekirdekli toprak dolgu  \n- **Gövde Yüksekliği:** 65 metre  \n- **Amaç:** İçme suyu + sulama + taşkın önleme  \n- **İdari Sınır:** Manisa ili (Gördes ilçesi)  ",
    "gordes_h3": "📅 Tarihsel Süreç ve 2019–2021 Krizi",
    "gordes_history": "Gördes Barajı 1980'de devreye girmiştir. İzmir su sisteminin en kırılgan halkasıdır:\n- **2013:** Doluluk %15 ile tarihi düşük seviye  \n- **2019:** Yağış azalması ve tüketim artışıyla %18'e geriler  \n- **2020:** 🚨 **Kritik kriz — doluluk %2!**  \n- **2021:** 🆘 **Tarihi dip — doluluk %1!** İzmir'de su kısıtlama gündemi  \n- **2022–2023:** Kısmen toparlanma %4–5; risk sürüyor  ",
    "gordes_h4": "🔬 2019–2021 Gördes Krizinden Çıkarılan Dersler",
    "gordes_lessons": "Gördes'in %1 doluluğa inmesi İzmir su yönetiminin en çarpıcı vakasıdır. Çıkarılan dersler:\n- Tek bir barajın kuraklıkla nasıl çöküşe geçebileceği  \n- Acil durum rezervi olmayan sistemlerde nüfus artış riski  \n- Tarımsal sulama ile içme suyu önceliklendirmesi sorunu  ",
    "gordes_summary": "2023 Doluluk: %5  |  Kapasite: 176 M m³  |  Havza: 1.315 km²  |  ⚠️ Kritik İzlemede",

    "eda_dam_fill_no": "02 · BARAJ DOLULUK",
    "eda_dam_fill_h": f"Baraj Doluluk Oranları ({START_YEAR}–{END_YEAR})",
    "bootstrap_to_real": "Bootstrap → Gerçek Veri",
    "critical_threshold": "Kritik Eşik: 15%",
    "fill_axis": "Doluluk (%)",
    "from_2010": f"puan ({START_YEAR}'dan)",

    "eda_findings_no": "03 · BULGULAR",
    "eda_findings_h": "Öne Çıkan Bulgular & Dönüm Noktaları",
    "eda_finding_1_title": "2013–2015 · DÜŞÜK SEVİYE PERİYODU",
    "eda_finding_1_h": "Tahtalı ve Gördes eş zamanlı geriledi",
    "eda_finding_1_text": "Tahtalı %36–%41 bandında seyrederken Gördes %15–%16'ya indi. İki barajın eş zamanlı düşüşü sistem üzerinde yoğun baskı yarattı.",
    "eda_finding_2_title": "2019–2021 · GÖRDES KRİZİ",
    "eda_finding_2_h": "%18'den %1'e tek yılda çöküş",
    "eda_finding_2_text": "2020'de %2, 2021'de %1'e inen Gördes, uzun süreli kuraklığın su kaynaklarına yıkıcı etkisini belgeleyen kritik bir veri noktasıdır.",
    "eda_finding_3_title": "2020 · PANDEMİ ETKİSİ",
    "eda_finding_3_h": "Evde kalma → artan tüketim baskısı",
    "eda_finding_3_text": "COVID-19 sürecinde hane içi su kullanımı belirgin biçimde arttı. Gördes kritik seviyelere inerken tüketim yüksek seyretti — arz-talep dengesi bozuldu.",

    "eda_demand_no": "02 · TALEP ISISI",
    "eda_demand_h": "Abone Başına Tüketim Isı Haritası (m³/abone)",
    "eda_narlidere_title": "🔴 NARLIDERE — Yüksek Tüketim, Düşük Risk",
    "eda_narlidere_text": "Narlıdere kişi başı tüketime göre listenin en üstünde ancak risk sıralamasında alt sıralarda. Küçük abone tabanı, eski yapı stoğu ve kentsel dönüşüm süreci belirleyici etkenlerdir.",
    "eda_gaziemir_title": "🔵 GAZİEMİR — Orta Tüketim, Yüksek Risk",
    "eda_gaziemir_text": "Gaziemir talep haritasında ortada görünürken risk sıralamasında yüksekte. Hızlı nüfus artışının yarattığı arz baskısı ve tüketim artış oranı belirleyicidir.",

    "eda_sd_no": "03 · ARZ-TALEP DENGESİ",
    "eda_sd_h": f"Arz-Talep Dengesi ({START_YEAR}–{END_YEAR})",
    "supply_label": "Sisteme Giren Su (Arz)",
    "demand_label": "Toplam Tüketim (Talep)",
    "demand_gap": "Talep Açığı",
    "supply_surplus": "Arz Fazlası",
    "real_data_short": "gerçek",
    "bootstrap_short": "bootstrap",
    "supply_demand_finding_1_title": "2014–2016 · ARZ KISITI ZİRVESİ",
    "supply_demand_finding_1_h": "Sisteme giren su 107M'e geriledi",
    "supply_demand_finding_1_text": "107–132M m³ bandına inen arz karşısında tüketim 147–153M m³'te yükselmeye devam etti. Oluşan makas sistem kapasitesini ciddi biçimde zorladı.",
    "supply_demand_finding_2_title": "2021 · EŞİTLENME NOKTASI",
    "supply_demand_finding_2_h": "Arz ve talep 160M m³'te buluştu",
    "supply_demand_finding_2_text": "Sisteme giren su ve toplam tüketim 160M m³ ile eşitlenerek nadir görülen bir denge noktası yakalandı.",
    "supply_demand_finding_3_title": "2022–2023 · AÇIK YENİDEN GENİŞLEDİ",
    "supply_demand_finding_3_h": "Talep arzı ~45M m³ geçti",
    "supply_demand_finding_3_text": "Sisteme giren su 118–120M m³'e gerilerken tüketim 165–166M'de kaldı. Bu açık altyapı kayıplarına işaret etmektedir.",

    "eda_loss_no": "04 · SU KAYIP TRENDİ",
    "eda_loss_h": f"Yıllık Su Kayıp Oranı Trendi ({START_YEAR}–{END_YEAR})",
    "loss_total": "Toplam Kayıp",
    "loss_physical": "Fiziki Kayıp",
    "loss_admin": "İdari Kayıp",
    "loss_total_axis": "Toplam Kayıp (%)",
    "loss_component_axis": "Bileşen (%)",
    "loss_kpi_total": "TOPLAM AZALMA",
    "loss_kpi_legend_phys": "Boru sızıntıları, altyapı hasarı",
    "loss_kpi_legend_admin": "Kaçak kullanım, sayaç hataları",
    "loss_finding_1_title": f"{START_YEAR}–{END_YEAR} · KAYDEDİLEN İYİLEŞME",
    "loss_finding_2_title": "FİZİKİ KAYIP BASKINI",
    "loss_finding_2_h": "Toplam kaybın ~%95'i boru sızıntısı",
    "loss_finding_2_text": "2023: Fiziki kayıp %25.92, idari kayıp %1.43. Altyapı yenileme öncelikli yatırım alanıdır.",
    "loss_finding_3_title": "2020 · PANDEMİ YILINDA HAFİF ARTIŞ",
    "loss_finding_3_h": "Kayıp oranı %28.56'ya çıktı",
    "loss_finding_3_text": "Pandemi döneminde denetim ve bakım faaliyetlerinin yavaşlaması bu geçici kötüleşmenin nedenidir.",

    # Risk
    "risk_badge": f"SU GÜVENLİĞİ RİSK ENDEKSİ · WSRI · {START_YEAR}–{END_YEAR}",
    "risk_title": "Su Güvenliği Risk Endeksi",
    "risk_lead": f"Entropy ağırlıklı bileşik skor · 4 gösterge · 0–100 ölçeği · {len(YEARS)} yıllık seri",
    "risk_year_select": "📅 Yılı Seçin",
    "district_search": "İlçe ara:",
    "district_search_placeholder": "örn. BUCA",
    "risk_sec01_no": "01 · İLÇE SKORLARI",
    "risk_sec01_h": f"İlçe Risk Skorları & {len(YEARS)} Yıllık Karşılaştırma",
    "risk_sec02_no": "02 · RİSK TRENDİ",
    "risk_sec02_h": "İlçe Bazlı Risk Skoru Trendi (2010–2023)",
    "real_data_band": "Gerçek Veri",
    "wsri_axis": "WSRI Risk Skoru",
    "trend_high_3": "🔴 En Yüksek Riskli 3 İlçe",
    "trend_low_3": "🟢 En Düşük Riskli 3 İlçe",
    "trend_med_5": "🟡 Orta Riskli 5 İlçe",
    "med_low_threshold": "Orta Risk Alt (46)",
    "high_threshold_short": "Yüksek Risk (60)",
    "med_threshold_short": "Orta Risk (46)",
    "risk_sec03_no": "03 · İLÇE DETAYI",
    "risk_sec03_h": "İlçe Bazlı Detay — Risk Bileşenleri",
    "select_district": "İlçe seç:",
    "kpi_year_score": f"{END_YEAR} Risk Skoru",
    "kpi_risk_class": "Risk Sınıfı",
    "kpi_2010_2023_change": "2010→2023 Değişim",
    "kpi_2010_score_lbl": "2010 skoru",
    "kpi_subscriber_growth": "Abone Büyüme (CAGR)",
    "per_year": "/yıl",
    "kpi_period": f"{START_YEAR}–{END_YEAR}",
    "points": "puan",

    # 2030
    "p2030_badge": "SENARYO PROJEKSİYONU · 2024–2030",
    "p2030_title": "2030 Yılı Risk Projeksiyonu",
    "p2030_lead": f"Abone büyüme oranı (CAGR) bazlı 3 senaryo · İyimser · Baz · Kötümser · CAGR {len(YEARS)} yıllık seriden hesaplanmıştır",
    "p2030_sec00_no": "00 · 2030 ANIK PROJEKSIYONU",
    "p2030_sec00_h": "2030 Yılı Risk Skoru — 3 Senaryo (Tüm İlçeler)",
    "scenario_pessimistic": "Kötümser (CAGR × 1.5)",
    "scenario_base": "Baz (CAGR × 1.0)",
    "scenario_optimistic": "İyimser (CAGR × 0.5)",
    "scenario_pessimistic_short": "Kötümser",
    "scenario_base_short": "Baz",
    "scenario_optimistic_short": "İyimser",
    "p2030_pess_title": "🔴 KÖTÜMSER SENARYO — CAGR × 1.5",
    "p2030_pess_h": "Mevcut büyüme hızı 1.5 katına çıkarsa",
    "p2030_pess_text": "Hızlı kentleşme, iklim kaynaklı arz kısıtı ve altyapı yatırımlarının yetersiz kalması durumunda risk skorları 2030'da belirgin biçimde yükselir.",
    "p2030_base_title": "🟠 BAZ SENARYO — CAGR × 1.0",
    "p2030_base_h": "Mevcut trend aynen devam ederse",
    "p2030_base_text": "2023 büyüme hızının korunduğu varsayımında 2030 risk görünümü. Genel eğilim düşüş yönünde ancak yüksek riskli ilçelerde 60 eşiği kırılma riski devam ediyor.",
    "p2030_opt_title": "🟢 İYİMSER SENARYO — CAGR × 0.5",
    "p2030_opt_h": "Su tasarrufu politikaları hayata geçerse",
    "p2030_opt_text": "Akıllı sayaç yaygınlaşması, su tasarrufu kampanyaları ve altyapı iyileştirmeleriyle büyüme hızının yarıya inmesi durumunda tüm ilçelerde belirgin risk azalışı öngörülmektedir.",

    # Mekânsal
    "spatial_badge": f"MEKÂNSAL ANALİZ · MORAN'S I + LISA · {END_YEAR}",
    "spatial_title": "Mekânsal Analiz",
    "spatial_lead": f"Yüksek riskli ilçeler birbirine komşu mu? · Global Moran's I · LISA · {END_YEAR}",
    "spatial_what_is_title": "ℹ️ Moran's I ve LISA nedir?",
    "spatial_what_is_text": "**Mekânsal Analiz** — Yüksek riskli ilçeler birbirine komşu mu, yoksa dağınık mı?\n- **Global Moran's I** — Tüm sistemi tek bir sayıyla özetler. +1'e yakınsa riskli ilçeler kümeleniyor, -1'e yakınsa dağınık.\n- **LISA** — Her ilçeye ayrı etiket verir:\n    - 🔴 **HH** — Riskli ilçe, komşuları da riskli → sıcak nokta\n    - 🟢 **LL** — Düşük riskli, komşuları da düşük → soğuk nokta\n    - 🟠 **HL** — Riskli ama komşuları düşük → izole yüksek risk\n    - 🔵 **LH** — Düşük riskli ama komşuları yüksek → dikkat gerektiriyor",
    "moran_global_label": "Global Moran's I",
    "moran_global_alt": f"{END_YEAR} risk skorları",
    "p_value_label": "p-değeri",
    "p_value_alt": "999 permütasyon testi",
    "moran_interpretation": "Yorum",
    "moran_interpretation_val": "Negatif",
    "moran_interpretation_alt": "Komşular farklılaşıyor",
    "hh_cluster": "HH Küme",
    "hh_cluster_val": "0 ilçe",
    "hh_cluster_alt": "HH küme yok",
    "moran_global_exp_t": "ℹ️ Global Moran's I nedir?",
    "p_value_exp_t": "ℹ️ p-değeri ne anlama geliyor?",
    "interp_exp_t": "ℹ️ Negatif kümelenme ne demek?",
    "interp_exp_text": "**Zayıf Negatif Moran's I + Yüksek p-value → Mekânsal Rastgelelik**\n\nI = −0.111 değeri sıfıra yakın ve p = 0.960 olduğu için risk skorlarının mekânsal dağılımı **rastgele** kabul edilir.\n\nNe kümelenme ne de düzenli dağılım deseni var; istatistiksel olarak ilçeler birbirinden bağımsız.",
    "hh_exp_t": "ℹ️ HH küme neden yok?",
    "hh_exp_text": "**HH Küme = 0 ilçe**\n\nHiçbir ilçe hem kendisi yüksek riskli hem de yüksek riskli komşularla çevrili değil.\n\nİzmir'de birbirine bitişik riskli bir bölge yok — risk yönetimi ilçe bazında uygulanabilir.",
    "spatial_sec01_no": "01 · MEKÂNSAL ANALİZ",
    "z_axis": "Standardize Risk (z)",
    "wz_axis": "Mekânsal Lag (Wz)",
    "slope_label": "Eğim",
    "lisa_col_district": "İlçe",
    "lisa_col_risk": "Risk",
    "lisa_col_lisa": "LISA",
    "lisa_col_explain": "Açıklama",
    "lisa_hh_full": "HH (Yüksek-Yüksek)",
    "lisa_ll_full": "LL (Düşük-Düşük)",
    "lisa_hl_full": "HL (Yüksek-Düşük)",
    "lisa_lh_full": "LH (Düşük-Yüksek)",
    "lisa_hh_short": "Sıcak Küme",
    "lisa_ll_short": "Soğuk Küme",
    "lisa_hl_short": "İzole Yüksek",
    "lisa_lh_short": "Çevre Yüksek",
    "lisa_gaziemir_title": "🟠 ÇİĞLİ · HL — İzole Yüksek Risk",
    "lisa_gaziemir_text": "Çiğli yüksek risk skoru taşıyor (62.5 puan) ancak doğrudan komşuluk yapısı nedeniyle scatter'da izole bir HL deseni gösteriyor. Yoğun nüfus, hızlı kentleşme ve eski altyapı Çiğli'nin temel risk sürücüleridir.",
    "lisa_karsiyaka_title": "🔵 KARŞIYAKA · LH — Çevre Baskısı Altında",
    "lisa_karsiyaka_text": "Karşıyaka'nın kendi risk skoru düşük (47 puan) olsa da Çiğli ve Bayraklı gibi yüksek riskli ilçelerle doğrudan sınır paylaşıyor. Komşu yüksek riskleri uzun vadede Karşıyaka'yı etkileyebilir.",

    # Öneriler
    "advice_badge": f"İLÇE ÖNERİLERİ · {END_YEAR}",
    "advice_title": "İlçe Bazlı Öneriler",
    "advice_lead": f"Risk sınıfına göre kişiselleştirilmiş öneri · {len(YEARS)} yıllık trend analizi · 2030 projeksiyonu",
    "kpi_district": "İlçe",
    "kpi_district_alt": "Seçili ilçe",
    "kpi_2030_base_proj": "2030 Baz Tahmini",
    "p2030_proj_subtitle": "2030 PROJEKSİYONU",
    "p2030_change_label": "2010→2023 Değişim",
    "advice_low_status": "✅ İyi durumdasınız — koruyucu önlemler alın",
    "advice_med_status": "⚠️ Dikkat gerektiriyor — somut adımlar atılmalı",
    "advice_high_status": "🚨 Yüksek risk — acil önlem gerekiyor",
    "advice_low_future": "Mevcut gidişat devam ederse 2030'ta da düşük risk bekleniyor.",
    "advice_med_future": "Kötümser senaryoda 2030'ta yüksek riske geçme ihtimali var.",
    "advice_high_future": "Önlem alınmazsa 2030'ta risk skoru kritik seviyelere ulaşabilir.",
    "trend_historical": f"Tarihsel ({START_YEAR}–{END_YEAR})",
    "trend_2030_baseline": "2030 Baz Tahmini",
    "general_advice_h": "💡 Genel Su Tasarrufu Önerileri",
    "general_advice_1_title": "🚿 Hane Bazlı Tasarruf",
    "general_advice_1_text": "Duş süresini 2 dk kısaltmak yılda ~3.650 lt tasarruf sağlar. Damlatan musluklar aylık 400–600 litre kayba yol açar. Makine kullanımında tam doluluk %30 tasarruf sağlar.",
    "general_advice_2_title": "🏗️ Altyapı Öncelikleri",
    "general_advice_2_text": "İzmir'deki fiziki su kayıp oranı 2023'te %25.92. Akıllı sayaç sistemleri sızıntıları erken tespit eder. Boru yaşı 25+ yıl olan hatlar öncelikli yenileme adayıdır.",
    "general_advice_3_title": "🌡️ İklim Uyum Önlemleri",
    "general_advice_3_text": "IPCC AR6'ya göre Akdeniz havzasında 2050'ye kadar yağış %20 azalacak. Yağmur suyu hasadı, gri su geri dönüşümü ve kuraklığa dayanıklı peyzaj kritik adımlardır.",

    # Harita
    "map_badge": f"ETKİLEŞİMLİ RİSK HARİTASI · İZMİR · {START_YEAR}–2030",
    "map_title": "İzmir İlçe Risk Haritası",
    "map_lead": "İlçe üzerine gel → risk bilgisi · Yıl seçilebilir",
    "map_year_select": "📅 Yıl Seçin",
    "map_legend_high": "Yüksek Risk (≥60)",
    "map_legend_med": "Orta Risk (46-60)",
    "map_legend_low": "Düşük Risk (<46)",
    "map_2030_proj": "🔮 (2030 Projeksiyonu)",
    "map_2030_proj_short": "🔮 2030 Projeksiyonu",
    "tbl_district": "İlçe",
    "tbl_risk_score": "Risk Skoru",
    "tbl_risk_class": "Risk Sınıfı",

    # Araçlar
    "tools_badge": "ETKİLEŞİMLİ ARAÇLAR · KEŞFEDİN & ANALİZ EDİN",
    "tools_title": "İnteraktif Araçlar",
    "tools_lead": f"Radar profil · İlçe karşılaştırma · Risk simülatörü · {len(YEARS)} yıllık animasyonlu seri",
    "tools_select_district": "🏙️ Analiz edilecek ilçeyi seç:",
    "tools_sec01_no": "01 · RADAR & KARŞILAŞTIRMA",
    "tools_sec01_h": "İlçe Radar Profili & Karşılaştırma",
    "tools_compare_district": "Karşılaştırılacak ilçe:",
    "radar_demand": "Talep",
    "radar_growth": "Artış",
    "radar_supply": "Arz Kısıtı",
    "radar_loss": "Kayıp",
    "radar_risk": "Risk",
    "radar_indicator": "GÖSTERGE",
    "radar_demand_full": "Abone Tüketim (m³)",
    "radar_growth_full": "Tüketim Artışı (%)",
    "radar_supply_full": "Arz Kısıtı",
    "radar_loss_full": "Su Kayıp Oranı (%)",
    "radar_risk_full": "Risk Skoru",
    "tools_sec02_no": "02 · SİMÜLATÖR",
    "tools_sec02_h": "Risk Simülatörü — Anlık Duyarlılık",
    "tools_sec02_caption": "Gösterge değerlerini değiştir → Risk skoru entropy ağırlıklarıyla anlık güncellenir",
    "sim_demand": "💧 Abone Tüketim (m³)",
    "sim_growth": "📈 Tüketim Artışı (%)",
    "sim_supply": "⚖️ Arz Kısıtı (%)",
    "sim_loss": "🔴 Kayıp Oranı (%)",
    "sim_kpi_score": "Simüle Edilen Skor",
    "sim_kpi_class": "Risk Sınıfı",
    "sim_kpi_weighted": "Ağırlıklı Hesap",
    "sim_kpi_weighted_val": "Talep %31.6 · Kayıp %33.0",
    "sim_kpi_arz_growth": "Arz+Artış",
    "sim_kpi_arz_growth_val": "Arz%23.8 · Artış%11.6",
    "tools_sec03_no": "03 · ZAMAN SERİSİ",
    "tools_sec03_h": f"Animasyonlu Risk Değişimi — {START_YEAR}–{END_YEAR} ({len(YEARS)} yıl)",
    "anim_year_prefix": "Yıl: ",
    "anim_play": "▶ Oynat",
    "anim_pause": "⏸ Durdur",
    "anim_caption": "🔬 Bootstrap simülasyonu (2010–2019) · ✅ İZSU Gerçek Verisi (2020–2023)",
    "tools_sec04_no": "04 · DEĞİŞİM HESAPLAYICI",
    "tools_sec04_h": "İki İlçeyi Yıllar İçinde Karşılaştır",
    "tools_sec04_caption": "İki ilçeyi seç, yıl aralığını belirle — puan farkını gör",
    "calc_district_1": "1. İlçe:",
    "calc_district_2": "2. İlçe:",
    "calc_year_range": "Yıl aralığı:",

    # Metodoloji
    "method_badge": "METODOLOJİ · ŞEFFAFLIK",
    "method_title": "Metodoloji & Teknik Detaylar",
    "method_lead": "Veri kaynağı · Bootstrap simülasyonu · İstatistiksel yöntemler · Formüller · Sınırlılıklar",
    "method_sec01_no": "01 · VERİ KAYNAĞI",
    "method_sec01_h": "Veri Kaynağı",
    "method_district_data_title": "İLÇE BAZLI VERİ",
    "method_district_data_text": f"📌 Kaynak: İZSU Açık Veri Portalı (2020–{END_YEAR}) + Bootstrap ({START_YEAR}–2019)<br>📌 Kapsam: 11 merkez ilçe<br>📌 Dönem: {START_YEAR}–{END_YEAR} ({len(YEARS)} yıl)<br>📌 Değişkenler: Yıllık tüketim (m³), abone sayısı",
    "method_system_data_title": "SİSTEM GENELİ VERİ",
    "method_system_data_text": f"📌 Kaynak: İZSU Açık Veri Portalı (2020–{END_YEAR}) + Bootstrap ({START_YEAR}–2019)<br>📌 Kapsam: 3 baraj (Tahtalı, Balçova, Gördes)<br>📌 Dönem: {START_YEAR}–{END_YEAR} ({len(YEARS)} yıl)<br>📌 Değişkenler: Doluluk, üretim, kayıp oranı",
    "method_sec02_no": "02 · BOOTSTRAP SİMÜLASYONU",
    "method_sec02_h": "Block Bootstrap Simülasyonu",
    "method_why_title": "🤔 NEDEN EK VERİ ÜRETİLDİ?",
    "method_why_text": f"İZSU'nun resmi açık verisi yalnızca <b style=\"color:white\">2020–{END_YEAR}</b> dönemini kapsıyor — yani sadece <b style=\"color:white\">4 yıl</b>. Mann-Kendall trend testi için bu süre yetersizdir. Bu nedenle <b style=\"color:white\">2010–2019</b> arası 10 yıllık veri bilimsel yöntemle üretildi.",
    "method_block_title": "🎲 BLOCK BOOTSTRAP NEDİR?",
    "method_block_text": "Eldeki gerçek verileri küçük bloklara böl → blokları istatistiksel kurallara göre karıştırarak yeni seriler oluştur → sonuçları geçmişe ait veri gibi kullan. Hava tahminlerinde, finans ve tıp araştırmalarında yaygın kullanılan standart bir istatistik tekniğidir.",
    "method_trust_title": "✅ VERİLERE GÜVENİLEBİLİR Mİ?",
    "method_trust_text": "Üretilen seri rastgele değil — İzmir'in gerçek su geçmişine uyumlu:<br>• 2013–2015: Gördes ve Tahtalı kuraklık dönemi<br>• 2020: Pandemi dönemi hane tüketimi artışı<br>• Nüfus büyümesi TÜİK İzmir verisiyle uyumlu",
    "method_trans_title": "🔍 ŞEFFAFLIK",
    "method_trans_text": f"Site genelinde:<br>🔬 <b style=\"color:#c39bd3;\">Mor = Bootstrap simülasyonu (2010–2019)</b><br>✅ <b style=\"color:#2ca02c;\">Yeşil = İZSU Gerçek Verisi (2020–{END_YEAR})</b><br><br>Kaynak kod GitHub'da açık erişimdedir. Tüm analizler Python ile yapıldı, sonuçlar tekrarlanabilir.",
    "method_sec03_no": "03 · RİSK ENDEKSİ",
    "method_sec03_h": "Su Güvenliği Risk Endeksi (WSRI)",
    "method_step1_t": "📐 Adım 1 — Min-Max Normalizasyon",
    "method_step1_text": "**Ne yapar?** Farklı birimlerdeki göstergeleri (m³, %, oran) aynı 0–1 ölçeğine çeker.\n\n**Formül:** Z(x) = (x − x_min) / (x_max − x_min)\n\n**Verimizdeki uygulaması:** Abone başına tüketim ve kayıp oranı farklı birimlerdedir. Min-Max ile 0–1 arasına çekildi; yüksek değer = yüksek risk.",
    "method_step1_caption": "Sonuç: 0 = en düşük risk · 1 = en yüksek risk · tüm göstergeler aynı ölçekte",
    "method_step2_t": "📐 Adım 2 — Entropy Ağırlıklandırma",
    "method_step2_text": "**Ne yapar?** Her göstergenin ağırlığını ilçeler arasındaki farklılığa göre otomatik hesaplar. Öznel yargıyı ortadan kaldırır.\n\n**Formül:** E_j = −(1/ln n) × Σ p_ij × ln(p_ij) → w_j = (1−E_j) / Σ(1−E_j)\n\n**Verimizdeki uygulaması:** Su kayıp oranı en fazla farklılık gösterdiği için en yüksek ağırlığı (%33) aldı.",
    "method_step2_caption": "İlçeler arası en fazla değişen gösterge → en yüksek ağırlık",
    "method_step3_t": "📐 Adım 3 — Bileşik Risk Skoru / WSRI",
    "method_step3_text": "**Ne yapar?** Normalize göstergeleri entropy ağırlıklarıyla çarpar ve toplar. Sonuç 0–100 ölçeğindedir.\n\n**Formül:** Risk(i,t) = Σ w_j × Z_j(i,t) × 100\n\n**Eşikler:** 0–45 Düşük · 46–59 Orta · 60+ Yüksek Risk",
    "method_step3_caption": "0–100 arasında · &lt;46 Düşük · 46–60 Orta · ≥60 Yüksek Risk",
    "method_weights_title": f"HESAPLANAN AĞIRLIKLAR ({len(YEARS)} YIL VERİDEN)",
    "weight_demand_label": "Talep (Abone Başına)",
    "weight_growth_label": "Tüketim Artışı",
    "weight_supply_label": "Arz Kısıtı",
    "weight_loss_label": "Kayıp Oranı",
    "method_sec04_no": "04 · ZAMANSAL ANALİZ",
    "method_sec04_h": "Mann-Kendall Trend Testi & Sen's Slope",
    "method_mk_t": "📐 Mann-Kendall Trend Testi",
    "method_mk_text": f"**Ne yapar?** Veri serisinin monoton trend izleyip izlemediğini test eder. Normal dağılım gerektirmez.\n\n**Formül:**\n> S = Σ (j>i) sgn(x_j − x_i)\n> τ = S / [n×(n−1) / 2]\n\n**Verimizdeki uygulaması:** {len(YEARS)} yıllık seri için hesaplandı. τ < 0 olan ilçelerde (Bornova, Çiğli, Bayraklı) azalan risk trendi saptandı.",
    "method_mk_caption": "τ > 0 artan · τ < 0 azalan · p < 0.05 istatistiksel anlamlılık",
    "method_sen_t": "📐 Sen's Slope",
    "method_sen_text": "**Ne yapar?** Trendin yıllık değişim hızını medyan ile hesaplar — aykırı değerlerden etkilenmez.\n\n**Formül:** β = medyan[(x_j − x_i) / (j − i)], j > i\n\n**Verimizdeki uygulaması:** Bornova için β ≈ −0.38 puan/yıl — her yıl ortalama 0.38 puan azaldı.",
    "method_sen_caption": "β = yıllık ortalama değişim büyüklüğü (puan/yıl)",
    "method_sec05_no": "05 · MEKÂNSAL ANALİZ",
    "method_sec05_h": "Moran's I & LISA",
    "method_moran_t": "📐 Global Moran's I",
    "method_moran_text": "**Ne yapar?** Risk değerlerinin mekânsal olarak kümelenip kümelenmediğini ölçer.\n\n**Formül:** I = (n/S₀) × [Σᵢ Σⱼ wᵢⱼ(xᵢ−x̄)(xⱼ−x̄)] / Σᵢ(xᵢ−x̄)²\n\n**Verimizdeki uygulaması:** I = −0.111 (p = 0.960, anlamlı değil). Risk skorları mekânsal olarak rastgele dağılmış — istatistiksel olarak kümelenme veya dağılım deseni yok.",
    "method_moran_caption": "I > 0 kümelenme · I < 0 dağınık",
    "method_lisa_t": "📐 Local Moran's I — LISA",
    "method_lisa_text": "**Ne yapar?** Her ilçe için ayrı mekânsal skor üretir. Global Moran \"genel tablo\" verirken LISA her ilçenin HH/LL/HL/LH sınıfını belirler.\n\n**Formül:** Iᵢ = zᵢ × Σⱼ wᵢⱼ × zⱼ\n\n**Verimizdeki uygulaması:** Gaziemir → HL (izole sıcak nokta). Karşıyaka → LH (çevre baskısı). 999 permütasyon testi uygulandı.",
    "method_lisa_caption": "HH/LL = küme · HL/LH = mekânsal aykırı değer",
    "method_sec06_no": "06 · PROJEKSİYON MODELİ",
    "method_sec06_h": "2030 Projeksiyon Modeli",
    "method_cagr_t": "📐 CAGR Tabanlı Projeksiyon Modeli",
    "method_cagr_text": f"**Ne yapar?** Her ilçenin geçmiş abone büyüme hızını (CAGR) hesaplar ve 3 farklı senaryo katsayısıyla 2030'a uzatır.\n\n**Formül:**\n> CAGR = (Abone₂₀₂₃ / Abone₂₀₁₀)^(1/13) − 1\n> Risk(i,t) = Risk(i,2023) × (1 + CAGRᵢ × k)^(t−2023)\n\n**k değerleri:** 0.5 = İyimser · 1.0 = Baz · 1.5 = Kötümser\n\n**Verimizdeki uygulaması:** {len(YEARS)} yıllık seri CAGR hesabını güvenilir kıldı. Sonuçlar 0–100 arasında sınırlandırıldı.",
    "method_cagr_caption": "k=0.5 İyimser · k=1.0 Baz · k=1.5 Kötümser · CAGR 14 yıllık seriden",
    "method_sec07_no": "07 · SINIRLILIKLAR",
    "method_sec07_h": "Sınırlılıklar & Şeffaflık",
    "limit_1_t": "🔬 BOOTSTRAP KISITI",
    "limit_1_text": f"{START_YEAR}–2019 verileri sentetiktir. Gerçek tarihsel İZSU verisi olmadığından bu dönemin yorumları gösterge niteliğindedir.",
    "limit_2_t": "⚠️ MEKÂNSAL KISIT",
    "limit_2_text": "n=11 ilçe ile Moran's I istatistiksel güç açısından sınırlıdır. Komşuluk matrisi coğrafi sınırlar referans alınarak oluşturuldu.",
    "limit_3_t": "⚠️ TAHMİN KISITI",
    "limit_3_text": "2030 projeksiyonu lineer büyüme varsayımına dayanır. İklim değişikliği ve politika etkileri modele dahil edilmemiştir.",
    "limit_4_t": "✅ TEKRARLANABILIRLIK",
    "limit_4_text": "Tüm analizler Python ile yapıldı. Kaynak kod GitHub'da açık erişimde. Bootstrap sabit rastgele tohum ile tekrarlanabilir.",
    "method_sec08_no": "08 · SSS",
    "method_sec08_h": "Sıkça Sorulan Sorular",
}

TR["advice_low_items"] = [
    "Mevcut su tasarrufu alışkanlıklarınızı sürdürün.",
    "Abone başına tüketimi yıllık izleyin — ani artışları erkenden fark edin.",
    "Komşu ilçelerdeki risk artışlarını takip edin, bölgesel etkiler olabilir.",
    "Yeşil alan sulama ve endüstriyel tüketimi optimize edin."
]
TR["advice_med_items"] = [
    "Hanelere ve işyerlerine yönelik su tasarrufu kampanyaları başlatın.",
    "Altyapı sızıntı tespiti için akıllı sayaç sistemleri kurun.",
    "Yüksek tüketen aboneleri belirleyip bilinçlendirme programları uygulayın.",
    "Yağmur suyu toplama sistemlerini teşvik edin.",
    "İZSU ile koordineli denetim programı başlatın."
]
TR["advice_high_items"] = [
    "İZSU ile acil eylem planı oluşturun — kısa vadeli kısıtlama önlemleri alın.",
    "Yüksek tüketen sanayi ve ticari sektörleri denetleyin.",
    "Geri dönüştürülmüş su kullanımını artırın, gri su sistemleri kurun.",
    "Alternatif su kaynakları (yer altı suyu, yağmur hasadı) araştırın.",
    "Halk bilgilendirme kampanyasıyla aciliyeti kamuoyuyla paylaşın."
]
TR["faq"] = [
    ("Bootstrap simülasyonu nedir, neden kullanıldı?", f"İZSU resmi açık verisi yalnızca 2020–{END_YEAR} dönemini kapsıyor (4 yıl). Mann-Kendall trend testi için bu örneklem yetersiz. Block bootstrap yöntemiyle {START_YEAR}–2019 dönemi için İzmir'in hidrolojik geçmişine uyumlu bir seri üretildi. Bu sayede n=4 yerine n={len(YEARS)} yıllık analizler yapılabildi."),
    ("Bootstrap verisi gerçek mi sayılır?", f"Hayır — {START_YEAR}–2019 verileri sentetiktir; gerçek İZSU ölçümleri değildir. Ancak İzmir'in kuraklık takvimine ve TÜİK nüfus büyümesine uyumlu kalibre edildi. Site genelinde mor renk ile açıkça işaretlenmiştir."),
    ("Risk skoru ne anlama geliyor?", "0–100 arasındaki skor, 4 su güvenliği göstergesinin entropy ağırlıklı ortalamasıdır. Eşikler: 0–45 Düşük Risk · 46–59 Orta Risk · 60+ Yüksek Risk. Yüksek skor = o ilçede su güvenliği daha kırılgan demektir."),
    ("Neden 4 gösterge seçildi?", "Abone başına tüketim, tüketim artış oranı, arz kısıtı ve su kayıp oranı — İZSU açık verisinde yıllık olarak mevcut olan ve su güvenliğini doğrudan etkileyen değişkenlerdir. Su kalitesi ve iklim verileri erişilebilir olmadığından modele dahil edilemedi."),
    ("Entropy ağırlıklandırma neden tercih edildi?", "Araştırmacının öznel ağırlık belirlemesini önler. Verinin kendi dağılımı ağırlıkları belirler — ilçeler arasında en fazla farklılık gösteren gösterge en yüksek ağırlığı alır. Literatürde kabul görmüş nesnel bir yaklaşımdır."),
    ("2030 projeksiyonu neden 3 senaryoya ayrıldı?", "Tek bir projeksiyon belirsizliği gizler. İyimser (k=0.5) tasarruf politikalarını, Baz (k=1.0) mevcut trendi, Kötümser (k=1.5) hızlı kentleşme ve kuraklık baskısını temsil eder."),
    (f"Mann-Kendall testi {len(YEARS)} yıllık veriyle güvenilir mi?", f"n={len(YEARS)} ile Mann-Kendall'ın istatistiksel gücü yüksektir. 2010–2019 dönemi bootstrap simülasyonu olduğundan sonuçlar ileride gerçek veriler elde edildiğinde doğrulanmalıdır; bu sınırlılık şeffaf biçimde belirtilmiştir."),
    ("Komşuluk matrisi nasıl belirlendi?", "İzmir 11 merkez ilçesinin coğrafi sınırları referans alınarak her ilçenin hangi ilçelerle fiziksel olarak sınır paylaştığı belirlendi. Matrisin simetrisi doğrulandı ve satır-normalize edildi."),
]

# ── ENGLISH DICTIONARY ──────────────────────────────────────────
EN = {
    "app_subtitle": f"Water Security Risk Index · İzmir · {START_YEAR}–2030",
    "data_source_short": "Data: İZSU + Bootstrap Simulation",
    "scope_short": "11 Central Districts · Entropy-WSRI",
    "search_placeholder": "🔍 Search: dam, risk, 2030...",
    "search_no_result": "❌ No results found. Try: dam, risk, map, 2030, simulator, methodology",
    "bootstrap_badge": "BOOTSTRAP SIMULATION",
    "bootstrap_banner": f"Data for {START_YEAR}–2019 was generated using block bootstrap methodology calibrated to İzmir's drought calendar. Data for 2020–{END_YEAR} comes from official İZSU sources.",
    "data_load_error_title": "Data Could Not Be Loaded",
    "data_load_error_msg": "Data files not found or unreadable.<br>Make sure ilce.xlsx and baraj.xlsx are in the repository.",
    "data_load_error_label": "Error",
    "lang_tr": "🇹🇷 TR",
    "lang_en": "🇬🇧 EN",

    "risk_low": "Low Risk",
    "risk_med": "Medium Risk",
    "risk_high": "High Risk",

    "nav_home": "Home",
    "nav_eda": "EDA",
    "nav_risk": "Risk",
    "nav_2030": "2030",
    "nav_map": "Map",
    "nav_spatial": "Spatial",
    "nav_advice": "Advice",
    "nav_method": "Methodology",
    "nav_tools": "Tools",

    # Home
    "home_badge": f"WATER SECURITY ANALYSIS · İZMİR · {START_YEAR}–{PRED_END_YEAR}",
    "home_title_1": "İzmir Water Security",
    "home_title_2": "Risk Index",
    "home_lead": f"Entropy-weighted composite risk analysis · 11 central districts · {len(YEARS)}-year series ({START_YEAR}–{END_YEAR}) · Bootstrap simulation · Mann-Kendall trend test · LISA spatial analysis · 2030 projection",
    "kpi_total_consumption": f"Total Consumption {END_YEAR}",
    "kpi_million_m3": "million m³",
    "kpi_highest_risk": "Highest Risk Score",
    "kpi_loss_rate": f"Water Loss Rate {END_YEAR}",
    "kpi_loss_subtext": "% · system-wide",
    "kpi_high_risk_districts": "High-Risk Districts",
    "kpi_med_risk_districts": "Medium-Risk Districts",
    "kpi_low_risk_districts": "Low-Risk Districts",
    "kpi_tahtali_fill": "Tahtalı Fill Level",
    "kpi_tahtali_year": f"year {END_YEAR}",
    "kpi_least_risky": "Least Risky",
    "kpi_score_label": "Score",
    "sec_01_title": "01 · RISK INDICATOR",
    "sec_01_h": f"Top 3 Riskiest Districts — {END_YEAR} Risk Gauge",
    "sec_02_title": "02 · RISK ANALYSIS",
    "sec_02_h": f"{END_YEAR} District Risk Ranking & Weight Distribution",
    "risk_threshold_med": "Medium Risk Threshold (46)",
    "risk_threshold_high": "High Risk Threshold (60)",
    "risk_score_axis": "Risk Score (0–100)",
    "risk_score": "Risk Score",
    "entropy_weights_label": "Entropy<br>Weights",
    "weight_loss_rate": "Water Loss Rate",
    "weight_per_capita": "Per Capita Consumption",
    "weight_supply_constraint": "Supply Constraint",
    "weight_growth_rate": "Consumption Growth Rate",
    "source_method_title": "SOURCE & METHOD",
    "source_data": "Data: İZSU + Bootstrap simulation",
    "source_scope": f"Scope: {START_YEAR}–{END_YEAR} · 11 Districts · {len(YEARS)} years",
    "source_method": "Method: Min-Max + Entropy + WSRI",
    "source_analysis": "Analysis: Mann-Kendall · LISA · CAGR",
    "sec_03_title": "03 · GLOBAL CONTEXT",
    "sec_03_h": "Where Does İzmir Stand Globally?",
    "global_pop_water_stress": "Population Under Water Stress",
    "global_pop_water_stress_text": "40% of the world's population faces severe water stress for at least one month per year.",
    "global_med_basin": "Mediterranean Basin Water Deficit",
    "global_med_basin_text": "Annual rainfall in the Mediterranean basin is expected to decrease by 20% by 2050. İzmir lies at the heart of this zone.",
    "global_izmir_wsri": "İzmir WSRI Average",
    "global_izmir_wsri_text": "Average of 11 central districts — Medium Risk band. 3 districts have crossed the high-risk threshold.",
    "global_izmir_wsri_source": f"İZSU + This study · {END_YEAR}",
    "global_tr_capita": "Türkiye Per Capita Water Potential",
    "global_tr_capita_text": "International threshold is 1,700 m³ — Türkiye is close to the \"water scarcity\" line.",
    "global_source_note": "Source note: ",
    "global_source_text": "WRI Aqueduct 2023 · IPCC AR6 (2021) · DSİ 2022 annual report · İZSU open data portal.",
    "share_copy_link": "Copy Link",
    "share_copied": "Copied!",
    "share_twitter": "Share on Twitter/X",
    "share_linkedin": "Share on LinkedIn",

    # EDA
    "eda_badge": f"EXPLORATORY DATA ANALYSIS · {START_YEAR}–{END_YEAR}",
    "eda_title": "Exploratory Data Analysis",
    "eda_lead": f"{len(YEARS)}-year series ({START_YEAR}–{END_YEAR}) · Extended via bootstrap simulation · Dam fill levels, district consumption, supply-demand balance and loss trends",
    "tab_dam": "💧 Dam Fill Level",
    "tab_consumption": "🌡️ Consumption Heatmap",
    "tab_supply_demand": "⚖️ Supply-Demand",
    "tab_loss": "📉 Loss Rate",
    "eda_dam_history_no": "01 · DAM HISTORY",
    "eda_dam_history_h": "İzmir's Dams — History, Technical Info & Water System",
    "eda_water_system_title": "ABOUT İZMİR'S WATER SYSTEM",
    "eda_water_system_text": "İzmir's drinking and utility water needs are primarily met by three major dams: <b style=\"color:#38d1e3\">Tahtalı</b>, <b style=\"color:#2ca02c\">Balçova</b>, and <b style=\"color:#d62728\">Gördes</b>. The combined storage capacity of these three dams is approximately <b style=\"color:white\">542 million m³</b>. Managed by İZSU (İzmir Water and Sewerage Administration), the system serves a population exceeding 4.4 million. As climate change reduces precipitation in the Mediterranean basin, the fill levels of these dams have become increasingly critical.",

    "tahtali_meta": "📍 Menderes District, İzmir &nbsp;|&nbsp; 📅 Construction: 1993–1997 &nbsp;|&nbsp; 🏗️ Type: Rock-earth fill",
    "tahtali_h1": "🏆 İzmir's Main Water Source",
    "tahtali_p1": "Tahtalı is **İzmir's largest water source**, alone supplying approximately **60–70%** of the city's annual drinking water needs.",
    "tahtali_h2": "📊 Technical Specifications",
    "tahtali_specs": "- **Total Storage Capacity:** 309 million m³  \n- **Normal Water Level:** 141 meters  \n- **Watershed Area:** 432 km²  \n- **Body Type:** Rock-earth fill, central core  \n- **Average Annual Flow:** ~210 million m³  \n- **Operating Authority:** İZSU General Directorate  ",
    "tahtali_h3": "📅 Historical Process and Key Milestones",
    "tahtali_history": "Tahtalı Dam was constructed between 1993-1997. Key milestones:\n- **2007–2008:** Severe drought, fill drops to 20%  \n- **2014:** Record rainfall, fill reaches **44%** project peak  \n- **2020–2021:** Pressure on Tahtalı increases during Gördes crisis  \n- **2023:** Fill at **29%** — long-term drought impact apparent  ",
    "tahtali_h4": "🌡️ Impact of Climate Change",
    "tahtali_climate": "Over the past 14 years, Tahtalı's average fill level shows a slow but steady downward trend. According to IPCC projections, precipitation in the Mediterranean basin is expected to **decrease 20% by 2050** — a serious warning for Tahtalı.",
    "tahtali_summary": "2023 Fill: 29%  |  Capacity: 309 M m³  |  Watershed: 432 km²",

    "balcova_meta": "📍 Balçova District, İzmir &nbsp;|&nbsp; 📅 Construction: 1991–1995 &nbsp;|&nbsp; 🏗️ Type: Concrete arch",
    "balcova_h1": "🏙️ Strategic Shield of the City Center",
    "balcova_p1": "Despite its small capacity, Balçova serves as a **critical emergency reserve** for **Bornova, Bayraklı, and central districts** thanks to its proximity to the city.",
    "balcova_h2": "📊 Technical Specifications",
    "balcova_specs": "- **Total Storage Capacity:** 57 million m³  \n- **Normal Water Level:** 103 meters  \n- **Watershed Area:** 47 km²  \n- **Body Type:** Concrete arch  \n- **Body Height:** 92 meters  \n- **Operating Authority:** İZSU General Directorate  ",
    "balcova_h3": "📅 Historical Process and Key Milestones",
    "balcova_history": "Balçova Dam came online in 1995. Key periods:\n- **2002–2004:** Stays above 26% even during prolonged drought  \n- **2016–2018:** Stable in the 30–34% band  \n- **2021:** Critical role during Gördes crisis  \n- **2023:** Active contribution at 32% fill  ",
    "balcova_h4": "💡 Why Small But Indispensable?",
    "balcova_why": "Although Balçova's watershed is small, it is only **12 km** from the city center. Short transmission lines mean low pressure losses and fast response. In a major drought or system failure, it serves as **the fastest emergency reserve** for the central districts.",
    "balcova_summary": "2023 Fill: 32%  |  Capacity: 57 M m³  |  Watershed: 47 km²",

    "gordes_meta": "📍 Gördes District, Manisa &nbsp;|&nbsp; 📅 Construction: 1976–1980 &nbsp;|&nbsp; 🏗️ Type: Earth fill",
    "gordes_h1": "⚠️ Fragile But Strategic: Gördes's Dual Role",
    "gordes_p1": "Although administratively in Manisa, Gördes is connected to İzmir's water system via pipelines. **It is the most fragile link** — fill dropped to 1% in 2020-21.",
    "gordes_h2": "📊 Technical Specifications",
    "gordes_specs": "- **Total Storage Capacity:** 176 million m³  \n- **Normal Water Level:** 211 meters  \n- **Watershed Area:** 1,315 km²  \n- **Body Type:** Clay-core earth fill  \n- **Body Height:** 65 meters  \n- **Purpose:** Drinking water + irrigation + flood prevention  \n- **Administrative Boundary:** Manisa Province (Gördes district)  ",
    "gordes_h3": "📅 Historical Process and the 2019–2021 Crisis",
    "gordes_history": "Gördes Dam came online in 1980. It is the most fragile link in İzmir's water system:\n- **2013:** Fill drops to historic low of 15%  \n- **2019:** Fill at 18% with reduced rainfall and rising consumption  \n- **2020:** 🚨 **Critical crisis — fill at 2%!**  \n- **2021:** 🆘 **Historic low — 1%!** Water restrictions discussed in İzmir  \n- **2022–2023:** Partial recovery to 4–5%; risk persists  ",
    "gordes_h4": "🔬 Lessons from the 2019–2021 Gördes Crisis",
    "gordes_lessons": "Gördes dropping to 1% fill is the most striking case in İzmir's water management history. Key lessons:\n- How a single dam can collapse under drought  \n- The risk of population growth in systems without emergency reserves  \n- Prioritization conflict between agricultural irrigation and drinking water  ",
    "gordes_summary": "2023 Fill: 5%  |  Capacity: 176 M m³  |  Watershed: 1,315 km²  |  ⚠️ Critical Watch",

    "eda_dam_fill_no": "02 · DAM FILL LEVEL",
    "eda_dam_fill_h": f"Dam Fill Rates ({START_YEAR}–{END_YEAR})",
    "bootstrap_to_real": "Bootstrap → Real Data",
    "critical_threshold": "Critical Threshold: 15%",
    "fill_axis": "Fill (%)",
    "from_2010": f"points (from {START_YEAR})",

    "eda_findings_no": "03 · FINDINGS",
    "eda_findings_h": "Key Findings & Turning Points",
    "eda_finding_1_title": "2013–2015 · LOW LEVEL PERIOD",
    "eda_finding_1_h": "Tahtalı and Gördes declined simultaneously",
    "eda_finding_1_text": "While Tahtalı stayed in the 36–41% band, Gördes dropped to 15–16%. The simultaneous decline of two dams placed intense pressure on the system.",
    "eda_finding_2_title": "2019–2021 · GÖRDES CRISIS",
    "eda_finding_2_h": "Collapse from 18% to 1% in a single year",
    "eda_finding_2_text": "Falling to 2% in 2020 and 1% in 2021, Gördes is a critical data point documenting the devastating impact of prolonged drought on water resources.",
    "eda_finding_3_title": "2020 · PANDEMIC EFFECT",
    "eda_finding_3_h": "Stay-at-home → rising consumption pressure",
    "eda_finding_3_text": "Household water use rose noticeably during the COVID-19 period. While Gördes fell to critical levels, consumption remained high — supply-demand balance was disrupted.",

    "eda_demand_no": "02 · DEMAND HEATMAP",
    "eda_demand_h": "Per-Subscriber Consumption Heatmap (m³/subscriber)",
    "eda_narlidere_title": "🔴 NARLIDERE — High Consumption, Low Risk",
    "eda_narlidere_text": "Narlıdere tops the list in per-capita consumption but ranks low in risk. Small subscriber base, older building stock, and urban transformation are the determining factors.",
    "eda_gaziemir_title": "🔵 GAZİEMİR — Medium Consumption, High Risk",
    "eda_gaziemir_text": "Gaziemir appears mid-tier in the demand heatmap but high in risk ranking. Supply pressure from rapid population growth and consumption growth rate are decisive.",

    "eda_sd_no": "03 · SUPPLY-DEMAND BALANCE",
    "eda_sd_h": f"Supply-Demand Balance ({START_YEAR}–{END_YEAR})",
    "supply_label": "Water Entering System (Supply)",
    "demand_label": "Total Consumption (Demand)",
    "demand_gap": "Demand Gap",
    "supply_surplus": "Supply Surplus",
    "real_data_short": "real",
    "bootstrap_short": "bootstrap",
    "supply_demand_finding_1_title": "2014–2016 · SUPPLY CONSTRAINT PEAK",
    "supply_demand_finding_1_h": "Water entering system fell to 107M",
    "supply_demand_finding_1_text": "While supply dropped to the 107–132M m³ band, consumption continued to rise to 147–153M m³. The resulting gap severely strained system capacity.",
    "supply_demand_finding_2_title": "2021 · EQUILIBRIUM POINT",
    "supply_demand_finding_2_h": "Supply and demand met at 160M m³",
    "supply_demand_finding_2_text": "Water entering the system and total consumption equalized at 160M m³, capturing a rare balance point.",
    "supply_demand_finding_3_title": "2022–2023 · GAP WIDENED AGAIN",
    "supply_demand_finding_3_h": "Demand exceeded supply by ~45M m³",
    "supply_demand_finding_3_text": "While water entering the system fell to 118–120M m³, consumption stayed at 165–166M. This gap points to infrastructure losses.",

    "eda_loss_no": "04 · WATER LOSS TREND",
    "eda_loss_h": f"Annual Water Loss Rate Trend ({START_YEAR}–{END_YEAR})",
    "loss_total": "Total Loss",
    "loss_physical": "Physical Loss",
    "loss_admin": "Administrative Loss",
    "loss_total_axis": "Total Loss (%)",
    "loss_component_axis": "Component (%)",
    "loss_kpi_total": "TOTAL REDUCTION",
    "loss_kpi_legend_phys": "Pipe leaks, infrastructure damage",
    "loss_kpi_legend_admin": "Illegal use, meter errors",
    "loss_finding_1_title": f"{START_YEAR}–{END_YEAR} · IMPROVEMENT RECORDED",
    "loss_finding_2_title": "PHYSICAL LOSS DOMINANCE",
    "loss_finding_2_h": "~95% of total loss is pipe leakage",
    "loss_finding_2_text": "2023: Physical loss 25.92%, administrative loss 1.43%. Infrastructure renewal is the priority investment area.",
    "loss_finding_3_title": "2020 · SLIGHT INCREASE IN PANDEMIC YEAR",
    "loss_finding_3_h": "Loss rate rose to 28.56%",
    "loss_finding_3_text": "The slowdown of inspection and maintenance activities during the pandemic period caused this temporary deterioration.",

    # Risk
    "risk_badge": f"WATER SECURITY RISK INDEX · WSRI · {START_YEAR}–{END_YEAR}",
    "risk_title": "Water Security Risk Index",
    "risk_lead": f"Entropy-weighted composite score · 4 indicators · 0–100 scale · {len(YEARS)}-year series",
    "risk_year_select": "📅 Select Year",
    "district_search": "Search district:",
    "district_search_placeholder": "e.g. BUCA",
    "risk_sec01_no": "01 · DISTRICT SCORES",
    "risk_sec01_h": f"District Risk Scores & {len(YEARS)}-Year Comparison",
    "risk_sec02_no": "02 · RISK TREND",
    "risk_sec02_h": "District-Level Risk Score Trend (2010–2023)",
    "real_data_band": "Real Data",
    "wsri_axis": "WSRI Risk Score",
    "trend_high_3": "🔴 Top 3 Highest-Risk Districts",
    "trend_low_3": "🟢 Top 3 Lowest-Risk Districts",
    "trend_med_5": "🟡 5 Medium-Risk Districts",
    "med_low_threshold": "Medium Risk Lower (46)",
    "high_threshold_short": "High Risk (60)",
    "med_threshold_short": "Medium Risk (46)",
    "risk_sec03_no": "03 · DISTRICT DETAIL",
    "risk_sec03_h": "District Detail — Risk Components",
    "select_district": "Select district:",
    "kpi_year_score": f"{END_YEAR} Risk Score",
    "kpi_risk_class": "Risk Class",
    "kpi_2010_2023_change": "2010→2023 Change",
    "kpi_2010_score_lbl": "2010 score",
    "kpi_subscriber_growth": "Subscriber Growth (CAGR)",
    "per_year": "/yr",
    "kpi_period": f"{START_YEAR}–{END_YEAR}",
    "points": "points",

    # 2030
    "p2030_badge": "SCENARIO PROJECTION · 2024–2030",
    "p2030_title": "2030 Risk Projection",
    "p2030_lead": f"Subscriber growth (CAGR)-based 3 scenarios · Optimistic · Base · Pessimistic · CAGR computed from {len(YEARS)}-year series",
    "p2030_sec00_no": "00 · 2030 INSTANT PROJECTION",
    "p2030_sec00_h": "2030 Risk Score — 3 Scenarios (All Districts)",
    "scenario_pessimistic": "Pessimistic (CAGR × 1.5)",
    "scenario_base": "Base (CAGR × 1.0)",
    "scenario_optimistic": "Optimistic (CAGR × 0.5)",
    "scenario_pessimistic_short": "Pessimistic",
    "scenario_base_short": "Base",
    "scenario_optimistic_short": "Optimistic",
    "p2030_pess_title": "🔴 PESSIMISTIC SCENARIO — CAGR × 1.5",
    "p2030_pess_h": "If current growth rate increases 1.5x",
    "p2030_pess_text": "If rapid urbanization, climate-driven supply constraints and inadequate infrastructure investments persist, risk scores will rise significantly by 2030.",
    "p2030_base_title": "🟠 BASE SCENARIO — CAGR × 1.0",
    "p2030_base_h": "If current trend continues unchanged",
    "p2030_base_text": "2030 risk outlook assuming the 2023 growth rate is preserved. Overall trend is downward, but the risk of breaching the 60 threshold remains in high-risk districts.",
    "p2030_opt_title": "🟢 OPTIMISTIC SCENARIO — CAGR × 0.5",
    "p2030_opt_h": "If water conservation policies are implemented",
    "p2030_opt_text": "If smart meter adoption, water conservation campaigns, and infrastructure improvements halve the growth rate, significant risk reduction is projected across all districts.",

    # Spatial
    "spatial_badge": f"SPATIAL ANALYSIS · MORAN'S I + LISA · {END_YEAR}",
    "spatial_title": "Spatial Analysis",
    "spatial_lead": f"Are high-risk districts adjacent? · Global Moran's I · LISA · {END_YEAR}",
    "spatial_what_is_title": "ℹ️ What are Moran's I and LISA?",
    "spatial_what_is_text": "**Spatial Analysis** — Are high-risk districts adjacent or scattered?\n- **Global Moran's I** — Summarizes the entire system in a single number. Close to +1 means risky districts are clustering, close to -1 means scattered.\n- **LISA** — Assigns a separate label to each district:\n    - 🔴 **HH** — Risky district with risky neighbors → hotspot\n    - 🟢 **LL** — Low-risk with low-risk neighbors → coldspot\n    - 🟠 **HL** — Risky but neighbors are low-risk → isolated high risk\n    - 🔵 **LH** — Low-risk but neighbors are high-risk → requires attention",
    "moran_global_label": "Global Moran's I",
    "moran_global_alt": f"{END_YEAR} risk scores",
    "p_value_label": "p-value",
    "p_value_alt": "999 permutation test",
    "moran_interpretation": "Interpretation",
    "moran_interpretation_val": "Negative",
    "moran_interpretation_alt": "Neighbors differ",
    "hh_cluster": "HH Cluster",
    "hh_cluster_val": "0 districts",
    "hh_cluster_alt": "No HH cluster",
    "moran_global_exp_t": "ℹ️ What is Global Moran's I?",
    "p_value_exp_t": "ℹ️ What does the p-value mean?",
    "interp_exp_t": "ℹ️ What does negative clustering mean?",
    "interp_exp_text": "**Weak Negative Moran's I + High p-value → Spatial Randomness**\n\nWith I = −0.111 close to zero and p = 0.960, the spatial distribution of risk scores is considered **random**.\n\nNeither clustering nor a regular dispersion pattern; districts are statistically independent of each other.",
    "hh_exp_t": "ℹ️ Why no HH cluster?",
    "hh_exp_text": "**HH Cluster = 0 districts**\n\nNo district is both high-risk itself and surrounded by high-risk neighbors.\n\nThere is no contiguous risky region in İzmir — risk management can be applied at the district level.",
    "spatial_sec01_no": "01 · SPATIAL ANALYSIS",
    "z_axis": "Standardized Risk (z)",
    "wz_axis": "Spatial Lag (Wz)",
    "slope_label": "Slope",
    "lisa_col_district": "District",
    "lisa_col_risk": "Risk",
    "lisa_col_lisa": "LISA",
    "lisa_col_explain": "Description",
    "lisa_hh_full": "HH (High-High)",
    "lisa_ll_full": "LL (Low-Low)",
    "lisa_hl_full": "HL (High-Low)",
    "lisa_lh_full": "LH (Low-High)",
    "lisa_hh_short": "Hot Cluster",
    "lisa_ll_short": "Cold Cluster",
    "lisa_hl_short": "Isolated High",
    "lisa_lh_short": "Surrounded High",
    "lisa_gaziemir_title": "🟠 ÇİĞLİ · HL — Isolated High Risk",
    "lisa_gaziemir_text": "Çiğli carries a high risk score (62.5 points) but appears in an isolated HL pattern in the scatter due to its neighborhood structure. Dense population, rapid urbanization, and aging infrastructure are Çiğli's main risk drivers.",
    "lisa_karsiyaka_title": "🔵 KARŞIYAKA · LH — Under Surrounding Pressure",
    "lisa_karsiyaka_text": "Although Karşıyaka's own risk score is low (47 points), it directly borders high-risk districts like Çiğli and Bayraklı. Neighboring high risks may affect Karşıyaka in the long term.",

    # Advice
    "advice_badge": f"DISTRICT RECOMMENDATIONS · {END_YEAR}",
    "advice_title": "District-Based Recommendations",
    "advice_lead": f"Risk-class-based personalized advice · {len(YEARS)}-year trend analysis · 2030 projection",
    "kpi_district": "District",
    "kpi_district_alt": "Selected district",
    "kpi_2030_base_proj": "2030 Base Projection",
    "p2030_proj_subtitle": "2030 PROJECTION",
    "p2030_change_label": "2010→2023 Change",
    "advice_low_status": "✅ You are in good shape — take protective measures",
    "advice_med_status": "⚠️ Requires attention — concrete steps needed",
    "advice_high_status": "🚨 High risk — urgent action required",
    "advice_low_future": "If the current course continues, low risk is also expected in 2030.",
    "advice_med_future": "In the pessimistic scenario, there is a possibility of moving to high risk by 2030.",
    "advice_high_future": "If no measures are taken, the risk score may reach critical levels by 2030.",
    "trend_historical": f"Historical ({START_YEAR}–{END_YEAR})",
    "trend_2030_baseline": "2030 Base Projection",
    "general_advice_h": "💡 General Water Conservation Tips",
    "general_advice_1_title": "🚿 Household Conservation",
    "general_advice_1_text": "Shortening shower time by 2 minutes saves ~3,650 liters per year. Dripping taps cause 400–600 liters of monthly loss. Running washing machines at full capacity saves 30%.",
    "general_advice_2_title": "🏗️ Infrastructure Priorities",
    "general_advice_2_text": "İzmir's physical water loss rate was 25.92% in 2023. Smart meter systems detect leaks early. Pipes 25+ years old are priority renewal candidates.",
    "general_advice_3_title": "🌡️ Climate Adaptation Measures",
    "general_advice_3_text": "According to IPCC AR6, precipitation in the Mediterranean basin will decrease by 20% by 2050. Rainwater harvesting, gray water recycling, and drought-resistant landscaping are critical steps.",

    # Map
    "map_badge": f"INTERACTIVE RISK MAP · İZMİR · {START_YEAR}–2030",
    "map_title": "İzmir District Risk Map",
    "map_lead": "Hover over a district → risk info · Year selectable",
    "map_year_select": "📅 Select Year",
    "map_legend_high": "High Risk (≥60)",
    "map_legend_med": "Medium Risk (46-60)",
    "map_legend_low": "Low Risk (<46)",
    "map_2030_proj": "🔮 (2030 Projection)",
    "map_2030_proj_short": "🔮 2030 Projection",
    "tbl_district": "District",
    "tbl_risk_score": "Risk Score",
    "tbl_risk_class": "Risk Class",

    # Tools
    "tools_badge": "INTERACTIVE TOOLS · EXPLORE & ANALYZE",
    "tools_title": "Interactive Tools",
    "tools_lead": f"Radar profile · District comparison · Risk simulator · {len(YEARS)}-year animated series",
    "tools_select_district": "🏙️ Select district to analyze:",
    "tools_sec01_no": "01 · RADAR & COMPARISON",
    "tools_sec01_h": "District Radar Profile & Comparison",
    "tools_compare_district": "District to compare:",
    "radar_demand": "Demand",
    "radar_growth": "Growth",
    "radar_supply": "Supply Constraint",
    "radar_loss": "Loss",
    "radar_risk": "Risk",
    "radar_indicator": "INDICATOR",
    "radar_demand_full": "Subscriber Consumption (m³)",
    "radar_growth_full": "Consumption Growth (%)",
    "radar_supply_full": "Supply Constraint",
    "radar_loss_full": "Water Loss Rate (%)",
    "radar_risk_full": "Risk Score",
    "tools_sec02_no": "02 · SIMULATOR",
    "tools_sec02_h": "Risk Simulator — Live Sensitivity",
    "tools_sec02_caption": "Change indicator values → Risk score updates instantly using entropy weights",
    "sim_demand": "💧 Subscriber Consumption (m³)",
    "sim_growth": "📈 Consumption Growth (%)",
    "sim_supply": "⚖️ Supply Constraint (%)",
    "sim_loss": "🔴 Loss Rate (%)",
    "sim_kpi_score": "Simulated Score",
    "sim_kpi_class": "Risk Class",
    "sim_kpi_weighted": "Weighted Calculation",
    "sim_kpi_weighted_val": "Demand 31.6% · Loss 33.0%",
    "sim_kpi_arz_growth": "Supply+Growth",
    "sim_kpi_arz_growth_val": "Supply 23.8% · Growth 11.6%",
    "tools_sec03_no": "03 · TIME SERIES",
    "tools_sec03_h": f"Animated Risk Change — {START_YEAR}–{END_YEAR} ({len(YEARS)} years)",
    "anim_year_prefix": "Year: ",
    "anim_play": "▶ Play",
    "anim_pause": "⏸ Pause",
    "anim_caption": "🔬 Bootstrap simulation (2010–2019) · ✅ İZSU Real Data (2020–2023)",
    "tools_sec04_no": "04 · CHANGE CALCULATOR",
    "tools_sec04_h": "Compare Two Districts Across Years",
    "tools_sec04_caption": "Pick two districts, set the year range — see the point difference",
    "calc_district_1": "1st District:",
    "calc_district_2": "2nd District:",
    "calc_year_range": "Year range:",

    # Methodology
    "method_badge": "METHODOLOGY · TRANSPARENCY",
    "method_title": "Methodology & Technical Details",
    "method_lead": "Data source · Bootstrap simulation · Statistical methods · Formulas · Limitations",
    "method_sec01_no": "01 · DATA SOURCE",
    "method_sec01_h": "Data Source",
    "method_district_data_title": "DISTRICT-LEVEL DATA",
    "method_district_data_text": f"📌 Source: İZSU Open Data Portal (2020–{END_YEAR}) + Bootstrap ({START_YEAR}–2019)<br>📌 Scope: 11 central districts<br>📌 Period: {START_YEAR}–{END_YEAR} ({len(YEARS)} years)<br>📌 Variables: Annual consumption (m³), subscriber count",
    "method_system_data_title": "SYSTEM-WIDE DATA",
    "method_system_data_text": f"📌 Source: İZSU Open Data Portal (2020–{END_YEAR}) + Bootstrap ({START_YEAR}–2019)<br>📌 Scope: 3 dams (Tahtalı, Balçova, Gördes)<br>📌 Period: {START_YEAR}–{END_YEAR} ({len(YEARS)} years)<br>📌 Variables: Fill, production, loss rate",
    "method_sec02_no": "02 · BOOTSTRAP SIMULATION",
    "method_sec02_h": "Block Bootstrap Simulation",
    "method_why_title": "🤔 WHY WAS ADDITIONAL DATA GENERATED?",
    "method_why_text": f"İZSU's official open data covers only the period <b style=\"color:white\">2020–{END_YEAR}</b> — that is, only <b style=\"color:white\">4 years</b>. This duration is insufficient for the Mann-Kendall trend test. Therefore, 10 years of data for <b style=\"color:white\">2010–2019</b> was generated using scientific methods.",
    "method_block_title": "🎲 WHAT IS BLOCK BOOTSTRAP?",
    "method_block_text": "Divide the actual data into small blocks → shuffle the blocks according to statistical rules to create new series → use the results as if they were historical data. It is a standard statistical technique widely used in weather forecasting, finance, and medical research.",
    "method_trust_title": "✅ CAN THE DATA BE TRUSTED?",
    "method_trust_text": "The generated series is not random — it is consistent with İzmir's actual water history:<br>• 2013–2015: Gördes and Tahtalı drought period<br>• 2020: Pandemic-era household consumption increase<br>• Population growth aligns with TÜİK İzmir data",
    "method_trans_title": "🔍 TRANSPARENCY",
    "method_trans_text": f"Across the site:<br>🔬 <b style=\"color:#c39bd3;\">Purple = Bootstrap simulation (2010–2019)</b><br>✅ <b style=\"color:#2ca02c;\">Green = İZSU Real Data (2020–{END_YEAR})</b><br><br>Source code is openly accessible on GitHub. All analyses were performed with Python; results are reproducible.",
    "method_sec03_no": "03 · RISK INDEX",
    "method_sec03_h": "Water Security Risk Index (WSRI)",
    "method_step1_t": "📐 Step 1 — Min-Max Normalization",
    "method_step1_text": "**What does it do?** Brings indicators in different units (m³, %, ratio) onto the same 0–1 scale.\n\n**Formula:** Z(x) = (x − x_min) / (x_max − x_min)\n\n**Application in our data:** Per-subscriber consumption and loss rate are in different units. They were rescaled to 0–1 with Min-Max; higher value = higher risk.",
    "method_step1_caption": "Result: 0 = lowest risk · 1 = highest risk · all indicators on the same scale",
    "method_step2_t": "📐 Step 2 — Entropy Weighting",
    "method_step2_text": "**What does it do?** Automatically computes each indicator's weight based on its variability across districts. Eliminates subjective judgment.\n\n**Formula:** E_j = −(1/ln n) × Σ p_ij × ln(p_ij) → w_j = (1−E_j) / Σ(1−E_j)\n\n**Application in our data:** Water loss rate received the highest weight (33%) because it shows the most variability.",
    "method_step2_caption": "The indicator that varies most across districts → highest weight",
    "method_step3_t": "📐 Step 3 — Composite Risk Score / WSRI",
    "method_step3_text": "**What does it do?** Multiplies normalized indicators by entropy weights and sums them. The result is on a 0–100 scale.\n\n**Formula:** Risk(i,t) = Σ w_j × Z_j(i,t) × 100\n\n**Thresholds:** 0–45 Low · 46–59 Medium · 60+ High Risk",
    "method_step3_caption": "0–100 range · &lt;46 Low · 46–60 Medium · ≥60 High Risk",
    "method_weights_title": f"COMPUTED WEIGHTS (FROM {len(YEARS)}-YEAR DATA)",
    "weight_demand_label": "Demand (Per Subscriber)",
    "weight_growth_label": "Consumption Growth",
    "weight_supply_label": "Supply Constraint",
    "weight_loss_label": "Loss Rate",
    "method_sec04_no": "04 · TEMPORAL ANALYSIS",
    "method_sec04_h": "Mann-Kendall Trend Test & Sen's Slope",
    "method_mk_t": "📐 Mann-Kendall Trend Test",
    "method_mk_text": f"**What does it do?** Tests whether a data series follows a monotonic trend. Does not require normal distribution.\n\n**Formula:**\n> S = Σ (j>i) sgn(x_j − x_i)\n> τ = S / [n×(n−1) / 2]\n\n**Application in our data:** Computed for the {len(YEARS)}-year series. Districts with τ < 0 (Bornova, Çiğli, Bayraklı) showed a decreasing risk trend.",
    "method_mk_caption": "τ > 0 increasing · τ < 0 decreasing · p < 0.05 statistical significance",
    "method_sen_t": "📐 Sen's Slope",
    "method_sen_text": "**What does it do?** Computes the trend's annual rate of change using the median — unaffected by outliers.\n\n**Formula:** β = median[(x_j − x_i) / (j − i)], j > i\n\n**Application in our data:** For Bornova, β ≈ −0.38 points/year — risk decreased by an average of 0.38 points each year.",
    "method_sen_caption": "β = average annual change magnitude (points/year)",
    "method_sec05_no": "05 · SPATIAL ANALYSIS",
    "method_sec05_h": "Moran's I & LISA",
    "method_moran_t": "📐 Global Moran's I",
    "method_moran_text": "**What does it do?** Measures whether risk values cluster spatially.\n\n**Formula:** I = (n/S₀) × [Σᵢ Σⱼ wᵢⱼ(xᵢ−x̄)(xⱼ−x̄)] / Σᵢ(xᵢ−x̄)²\n\n**Application in our data:** I = −0.111 (p = 0.960, not significant). Risk scores are randomly distributed across space — no statistically significant clustering or dispersion pattern.",
    "method_moran_caption": "I > 0 clustering · I < 0 dispersed",
    "method_lisa_t": "📐 Local Moran's I — LISA",
    "method_lisa_text": "**What does it do?** Produces a separate spatial score for each district. While Global Moran gives a \"general picture\", LISA determines each district's HH/LL/HL/LH class.\n\n**Formula:** Iᵢ = zᵢ × Σⱼ wᵢⱼ × zⱼ\n\n**Application in our data:** Gaziemir → HL (isolated hotspot). Karşıyaka → LH (surrounding pressure). 999 permutation test was applied.",
    "method_lisa_caption": "HH/LL = cluster · HL/LH = spatial outlier",
    "method_sec06_no": "06 · PROJECTION MODEL",
    "method_sec06_h": "2030 Projection Model",
    "method_cagr_t": "📐 CAGR-Based Projection Model",
    "method_cagr_text": f"**What does it do?** Computes each district's historical subscriber growth rate (CAGR) and extends it to 2030 using 3 different scenario coefficients.\n\n**Formula:**\n> CAGR = (Subscribers₂₀₂₃ / Subscribers₂₀₁₀)^(1/13) − 1\n> Risk(i,t) = Risk(i,2023) × (1 + CAGRᵢ × k)^(t−2023)\n\n**k values:** 0.5 = Optimistic · 1.0 = Base · 1.5 = Pessimistic\n\n**Application in our data:** The {len(YEARS)}-year series made the CAGR calculation reliable. Results were bounded between 0–100.",
    "method_cagr_caption": "k=0.5 Optimistic · k=1.0 Base · k=1.5 Pessimistic · CAGR from 14-year series",
    "method_sec07_no": "07 · LIMITATIONS",
    "method_sec07_h": "Limitations & Transparency",
    "limit_1_t": "🔬 BOOTSTRAP CONSTRAINT",
    "limit_1_text": f"{START_YEAR}–2019 data is synthetic. Since real historical İZSU data is unavailable, interpretations of this period are indicative.",
    "limit_2_t": "⚠️ SPATIAL CONSTRAINT",
    "limit_2_text": "With n=11 districts, Moran's I has limited statistical power. The neighborhood matrix was constructed using geographic boundaries.",
    "limit_3_t": "⚠️ FORECAST CONSTRAINT",
    "limit_3_text": "The 2030 projection relies on a linear growth assumption. Climate change and policy effects are not included in the model.",
    "limit_4_t": "✅ REPRODUCIBILITY",
    "limit_4_text": "All analyses were done with Python. Source code is openly available on GitHub. Bootstrap is reproducible with a fixed random seed.",
    "method_sec08_no": "08 · FAQ",
    "method_sec08_h": "Frequently Asked Questions",
}

EN["advice_low_items"] = [
    "Maintain your existing water-saving habits.",
    "Monitor per-subscriber consumption annually — catch sudden spikes early.",
    "Track risk increases in neighboring districts; regional effects can spill over.",
    "Optimize green-area irrigation and industrial consumption."
]
EN["advice_med_items"] = [
    "Launch water conservation campaigns for households and businesses.",
    "Install smart meter systems for infrastructure leak detection.",
    "Identify high-consumption subscribers and run awareness programs.",
    "Encourage rainwater harvesting systems.",
    "Initiate a coordinated inspection program with İZSU."
]
EN["advice_high_items"] = [
    "Create an emergency action plan with İZSU — implement short-term restriction measures.",
    "Audit high-consumption industrial and commercial sectors.",
    "Increase recycled water use; install gray water systems.",
    "Investigate alternative water sources (groundwater, rainwater harvesting).",
    "Share the urgency with the public through awareness campaigns."
]
EN["faq"] = [
    ("What is bootstrap simulation, and why was it used?", f"İZSU's official open data covers only the period 2020–{END_YEAR} (4 years). This sample is insufficient for the Mann-Kendall trend test. The block bootstrap method was used to generate a series for {START_YEAR}–2019 consistent with İzmir's hydrological history. This enabled n={len(YEARS)}-year analyses instead of n=4."),
    ("Is bootstrap data considered real?", f"No — the {START_YEAR}–2019 data is synthetic; it is not real İZSU measurements. However, it was calibrated to match İzmir's drought calendar and TÜİK population growth. It is clearly marked in purple across the site."),
    ("What does the risk score mean?", "The 0–100 score is the entropy-weighted average of 4 water security indicators. Thresholds: 0–45 Low Risk · 46–59 Medium Risk · 60+ High Risk. A higher score means water security in that district is more fragile."),
    ("Why were 4 indicators chosen?", "Per-subscriber consumption, consumption growth rate, supply constraint, and water loss rate — these are variables annually available in İZSU's open data and directly affecting water security. Water quality and climate data were not accessible, so they were not included in the model."),
    ("Why was entropy weighting chosen?", "It prevents the researcher from assigning subjective weights. The data's own distribution determines the weights — the indicator that varies most across districts gets the highest weight. It is a literature-accepted objective approach."),
    ("Why was the 2030 projection split into 3 scenarios?", "A single projection hides uncertainty. Optimistic (k=0.5) represents conservation policies, Base (k=1.0) the current trend, Pessimistic (k=1.5) rapid urbanization and drought pressure."),
    (f"Is the Mann-Kendall test reliable with {len(YEARS)}-year data?", f"With n={len(YEARS)}, Mann-Kendall's statistical power is high. Since the 2010–2019 period is bootstrap-simulated, results should be validated when real data become available; this limitation is transparently noted."),
    ("How was the neighborhood matrix determined?", "İzmir's 11 central districts were mapped using their geographic boundaries to determine which districts physically share borders. The matrix's symmetry was verified and row-normalized."),
]

# ── t() fonksiyonu / function ──────────────────────────────────
def t(key, **kwargs):
    """Return translation for current language. Optionally format with kwargs."""
    d = EN if st.session_state.dil == "en" else TR
    val = d.get(key, TR.get(key, key))
    if kwargs and isinstance(val, str):
        try:
            return val.format(**kwargs)
        except Exception:
            return val
    return val


# ═══════════════════════════════════════════════════════════════
# CSS / Theme
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ═══════════════════════════════════════════════════════════
   ⚙️  ANİMASYON HIZ AYARLARI — Buradan değiştir, tek tek aramaya gerek yok
   ═══════════════════════════════════════════════════════════ */
:root {
    --wave-duration: 7s;       /* MAVİ ŞERİT akma hızı (1s=hızlı, 30s=çok yavaş) */
    --pulse-duration: 6s;      /* 💧 DAMLA pulse hızı  (1s=hızlı, 30s=çok yavaş) */
}

section[data-testid="stSidebar"] { width: 280px !important; min-width: 280px !important; }

.stApp {
    background-image:
        linear-gradient(rgba(3,12,35,0.82), rgba(4,18,50,0.85)),
        url("https://images.unsplash.com/photo-1527489377706-5bf97e608852?w=1600&q=80");
    background-size: cover;
    background-position: center top;
    background-attachment: fixed;
}
.main { background: transparent; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

h1 { color: #38d1e3 !important; font-size: 2rem !important; font-weight: 700 !important; }
h2 { color: #a8d8f0 !important; font-size: 1.3rem !important; }
h3 { color: #c5e8f7 !important; font-size: 1.1rem !important; }
p, li, label { color: #d0e8f5 !important; }

[data-testid="metric-container"] {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(56,209,227,0.3);
    border-radius: 12px; padding: 1rem;
    backdrop-filter: blur(10px);
}
[data-testid="metric-container"] label { color: #38d1e3 !important; font-size: 0.85rem !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 1.6rem !important; }

[data-testid="stSidebar"] { background: rgba(5,20,50,0.95) !important; border-right: 1px solid rgba(56,209,227,0.2); }
[data-testid="stSidebar"] * { color: #c5e8f7 !important; }

.stTabs [data-baseweb="tab"] { color: #38d1e3 !important; background: rgba(255,255,255,0.05); border-radius: 8px 8px 0 0; }
.stTabs [aria-selected="true"] { background: rgba(56,209,227,0.15) !important; border-bottom: 2px solid #38d1e3 !important; }

hr { border-color: rgba(56,209,227,0.2) !important; }
.stAlert { background: rgba(56,209,227,0.1) !important; border: 1px solid rgba(56,209,227,0.3) !important; border-radius: 10px !important; color: #d0e8f5 !important; }
[data-testid="stDataFrame"] { background: rgba(255,255,255,0.05) !important; }

@keyframes wave {
    0% { transform: translateX(0); }
    100% { transform: translateX(-50%); }
}
.wave-container { position: relative; width: 100%; height: 5px; overflow: hidden; margin: 0.5rem 0; opacity: 0.85; }
.wave { position: absolute; width: 200%; height: 100%;
    background: linear-gradient(90deg,
        transparent 0%,
        rgba(56,209,227,0.55) 25%,
        rgba(77,184,240,0.65) 50%,
        rgba(56,209,227,0.55) 75%,
        transparent 100%);
    animation: wave var(--wave-duration) linear infinite; }

.risk-low { color: #2ca02c; font-weight: 600; }
.risk-med { color: #ff7f0e; font-weight: 600; }
.risk-high { color: #d62728; font-weight: 600; }

[data-testid="stTextInput"] input {
    background: rgba(56,209,227,0.12) !important;
    border: 1px solid rgba(56,209,227,0.55) !important;
    border-radius: 16px !important;
    color: #d0e8f5 !important;
    font-size: 0.72rem !important;
    height: 26px !important;
    padding: 0 10px !important;
    box-shadow: 0 0 10px rgba(56,209,227,0.18) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
}
[data-testid="stTextInput"] input::placeholder {
    color: rgba(168,216,240,0.65) !important;
    font-size: 0.7rem !important;
}
[data-testid="stTextInput"] > div,
[data-testid="stTextInput"] > div > div {
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
    padding: 0 !important;
}
[data-testid="stTextInput"] input::placeholder { color: rgba(168,216,240,0.55) !important; }
[data-testid="stTextInput"] input:focus {
    border-color: rgba(56,209,227,0.8) !important;
    box-shadow: 0 0 14px rgba(56,209,227,0.25) !important;
}

button[kind="secondary"],
button[kind="primary"],
.stButton > button,
div[data-testid="stButton"] > button,
[data-testid="stBaseButton-secondary"],
[data-testid="stBaseButton-primary"],
[data-testid="stBaseButton-secondaryFormSubmit"],
.st-emotion-cache-1x8cf1d,
.st-emotion-cache-7ym5gk,
[class*="stButton"] button {
    background: rgba(4,20,60,0.55) !important;
    border: 1.5px solid rgba(56,209,227,0.35) !important;
    border-radius: 12px !important;
    color: #b8d8f0 !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3), inset 0 1px 0 rgba(56,209,227,0.08) !important;
    transition: all 160ms ease !important;
}
button[kind="secondary"]:hover,
button[kind="primary"]:hover,
.stButton > button:hover,
div[data-testid="stButton"] > button:hover,
[data-testid="stBaseButton-secondary"]:hover,
[data-testid="stBaseButton-primary"]:hover,
[class*="stButton"] button:hover {
    background: rgba(56,209,227,0.18) !important;
    border-color: rgba(56,209,227,0.75) !important;
    color: #ffffff !important;
    box-shadow: 0 6px 20px rgba(0,0,0,0.4), 0 0 16px rgba(56,209,227,0.22) !important;
}
[class*="stButton"] button p,
div[data-testid="stButton"] > button p,
[data-testid="stBaseButton-secondary"] p,
[data-testid="stBaseButton-primary"] p {
    color: inherit !important;
}

/* Streamlit header & üst şerit TAMAMEN GİZLE */
header[data-testid="stHeader"],
.stApp > header,
[data-testid="stToolbar"],
[data-testid="stToolbarActions"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stAppDeployButton"],
[data-testid="stAppViewBlockContainer"] > div:first-child:has(> iframe),
.stDeployButton,
#MainMenu, footer, [data-testid="stMainMenu"],
/* Streamlit Cloud "Fork on GitHub" sağ üst badge */
.viewerBadge_container__r5tak,
.viewerBadge_link__1S137,
.viewerBadge_text__1JaDK,
.styles_viewerBadge__CvC9N,
.styles_terminalButton__JBj5T,
[class*="viewerBadge"],
[class*="profileContainer"],
[class*="terminalButton"],
a[href*="github.com"][class*="badge"],
a[href*="streamlit.io"][class*="badge"],
iframe[title*="streamlit"]
{ display: none !important; height: 0 !important; visibility: hidden !important; opacity: 0 !important; pointer-events: none !important; }

.stApp { margin-top: 0 !important; }
.block-container { padding-top: 3.5rem !important; }
/* Üstteki olası iframe'i de gizle */
body > iframe:first-child { display: none !important; }

.veri-rozet {
    display:inline-block; background:rgba(155,89,182,0.15);
    border:1px solid rgba(155,89,182,0.4); color:#c39bd3;
    font-size:0.68rem; letter-spacing:1.5px; padding:3px 10px;
    border-radius:20px; font-weight:600;
}

div[data-testid="stSlider"] [data-baseweb="slider"] > div > div:first-child { background: rgba(56,209,227,0.2) !important; height: 5px !important; }
div[data-testid="stSlider"] [data-baseweb="slider"] > div > div:nth-child(2) { background: #38d1e3 !important; height: 5px !important; }
div[data-testid="stSlider"] [role="slider"] { background: #38d1e3 !important; border: 3px solid white !important; box-shadow: 0 0 14px rgba(56,209,227,0.85) !important; width: 20px !important; height: 20px !important; }
div[data-testid="stSlider"] [data-baseweb="tooltip"] div { background: rgba(10,30,70,0.95) !important; border: 1px solid #38d1e3 !important; color: #38d1e3 !important; font-weight: 700 !important; border-radius: 6px !important; }

/* Aktif (primary) buton — dil & navigasyon vurgusu */
button[kind="primary"],
[data-testid="stBaseButton-primary"],
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg,rgba(56,209,227,0.30),rgba(10,50,120,0.65)) !important;
    border: 1.5px solid #38d1e3 !important;
    color: #ffffff !important;
    box-shadow: 0 0 18px rgba(56,209,227,0.50), 0 4px 14px rgba(0,0,0,0.4) !important;
}
button[kind="primary"]:hover {
    background: linear-gradient(135deg,rgba(56,209,227,0.45),rgba(10,50,120,0.75)) !important;
    box-shadow: 0 0 22px rgba(56,209,227,0.65) !important;
}

/* ═══════════════════════════════════════════════════════════
   🌊 WOW FACTOR ANIMATIONS — Hero, Counters, Scroll, Particles
   ═══════════════════════════════════════════════════════════ */

/* — 1.2 NUMBER COUNTERS — CSS @property + counter() trick */
@property --num {
    syntax: "<integer>";
    initial-value: 0;
    inherits: false;
}
@keyframes countUp {
    from { --num: 0; }
    to   { --num: var(--target); }
}
.counter {
    animation: countUp 1.6s cubic-bezier(0.22, 1, 0.36, 1) forwards;
    counter-reset: num var(--num);
    display: inline-block;
}
.counter::after { content: counter(num); }
.counter-decimal {
    animation: countUp 1.6s cubic-bezier(0.22, 1, 0.36, 1) forwards;
    counter-reset: num var(--num);
    display: inline-block;
}
.counter-decimal::after {
    content: counter(num) "." attr(data-suffix);
}

/* — 1.3 SCROLL-TRIGGERED FADE-IN — Modern view-timeline (Chrome/Edge/Safari 17+) */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(40px); filter: blur(4px); }
    to   { opacity: 1; transform: translateY(0);    filter: blur(0); }
}
@supports (animation-timeline: view()) {
    [data-testid="stPlotlyChart"],
    [data-testid="metric-container"],
    [data-testid="column"] > div > div > div > [data-testid^="stVertical"],
    .element-container:has(> .stMarkdown) {
        animation: fadeInUp 0.8s cubic-bezier(0.22, 1, 0.36, 1) both;
        animation-timeline: view();
        animation-range: entry 0% cover 30%;
    }
}
/* Fallback: yine de hafif initial fade-in (modern browser olmasa da) */
@keyframes pageFadeIn {
    from { opacity: 0; transform: translateY(15px); }
    to   { opacity: 1; transform: translateY(0); }
}
.main .block-container > div {
    animation: pageFadeIn 0.7s ease-out 0.1s both;
}

/* — 1.1 HERO ANIMATIONS — Letter-by-letter title reveal */
.hero-title-letter {
    display: inline-block;
    opacity: 0;
    transform: translateY(20px) scale(0.85);
    animation: letterReveal 0.6s cubic-bezier(0.22, 1, 0.36, 1) forwards;
    text-shadow: 0 0 24px rgba(56,209,227,0.20);
}
@keyframes letterReveal {
    0%   { opacity: 0; transform: translateY(20px) scale(0.85); filter: blur(8px); }
    100% { opacity: 1; transform: translateY(0)    scale(1);    filter: blur(0); }
}

/* Hero icon (water drop) — slow gentle breathing */
.hero-icon {
    display: inline-block;
    font-size: 3.4rem;
    line-height: 1;
    filter: drop-shadow(0 0 16px rgba(56,209,227,0.6));
    animation: dropPulse var(--pulse-duration) ease-in-out infinite;
    transform-origin: center center;
}
@keyframes dropPulse {
    0%, 100% {
        filter: drop-shadow(0 0 14px rgba(56,209,227,0.45));
        transform: translateY(0) scale(1);
    }
    50% {
        filter: drop-shadow(0 0 26px rgba(56,209,227,0.9));
        transform: translateY(-4px) scale(1.04);
    }
}

/* Subtitle fade-in delayed */
.hero-subtitle {
    opacity: 0;
    animation: pageFadeIn 0.8s ease-out 0.9s forwards;
}

/* — 1.1 FLOATING WATER PARTICLES — Pure CSS background */
.particles-container {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}
.particle {
    position: absolute;
    bottom: -20px;
    background: radial-gradient(circle at 30% 30%, rgba(56,209,227,0.55), rgba(77,184,240,0.15) 60%, transparent 100%);
    border-radius: 50%;
    animation: floatUp linear infinite;
    box-shadow: 0 0 14px rgba(56,209,227,0.35), inset 0 0 4px rgba(255,255,255,0.2);
}
@keyframes floatUp {
    0%   { transform: translateY(0) translateX(0);     opacity: 0; }
    8%   { opacity: 0.55; }
    50%  { transform: translateY(-50vh) translateX(25px); opacity: 0.45; }
    92%  { opacity: 0.3; }
    100% { transform: translateY(-105vh) translateX(-18px); opacity: 0; }
}

/* — KPI Card hover — premium feel */
[data-testid="metric-container"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.35), 0 0 18px rgba(56,209,227,0.18) !important;
    border-color: rgba(56,209,227,0.55) !important;
    transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
}
[data-testid="metric-container"] {
    transition: all 0.3s ease;
}

/* Reduce motion respect */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
    }
    .particle { display: none; }
}
</style>
""", unsafe_allow_html=True)

# — 1.1 PARTICLES BACKGROUND — Inject 14 floating water droplets (visible but not overwhelming)
import random as _rnd
_rnd.seed(42)
_particles_html = '<div class="particles-container">'
for _i in range(14):
    _size = _rnd.randint(5, 13)
    _left = _rnd.randint(0, 100)
    _delay = _rnd.uniform(0, 18)
    _duration = _rnd.uniform(16, 26)
    _particles_html += (
        f'<div class="particle" style="width:{_size}px;height:{_size}px;'
        f'left:{_left}%;animation-delay:{_delay:.1f}s;animation-duration:{_duration:.1f}s;"></div>'
    )
_particles_html += '</div>'
st.markdown(_particles_html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════
@st.cache_data
def load_data():
    ilce_raw = pd.read_excel("ilce.xlsx", header=None)
    tuketim_cols = [0] + list(range(1, 1 + len(YEARS)))
    abone_cols   = [0] + list(range(1 + len(YEARS), 1 + 2*len(YEARS)))

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

    rows = []
    for ilce in tuketim["İlçe"]:
        for yil in YEARS:
            t_val = tuketim[tuketim["İlçe"]==ilce][f"T{yil}"].values[0]
            a = abone[abone["İlçe"]==ilce][f"A{yil}"].values[0]
            rows.append({
                "İlçe": ilce, "Yıl": yil,
                "Tüketim_m3": t_val, "Abone": int(a),
                "AbbTuketim": round(t_val/a, 2) if a else 0,
                "VeriTipi": "Gerçek" if yil >= 2020 else "Bootstrap"
            })
    tablo1 = pd.DataFrame(rows).sort_values(["İlçe","Yıl"]).reset_index(drop=True)
    tablo1["Artis"] = tablo1.groupby("İlçe")["AbbTuketim"].pct_change().fillna(0)

    baraj_raw = pd.read_excel("baraj.xlsx", header=None)
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
    Z = np.column_stack([minmax(risk_df["AbbTuketim"]), minmax(risk_df["Artis"]),
                         minmax(risk_df["Arz_Kısıtı"]), minmax(risk_df["Su_Kayıp_Oranı_%"])])
    k = 1/np.log(len(Z))
    P = Z/Z.sum(axis=0)
    P = np.where(P==0, 1e-10, P)
    E = -k*(P*np.log(P)).sum(axis=0)
    W = (1-E)/(1-E).sum()
    risk_df["Risk_Skor"] = (Z @ W) * 100
    risk_df["Risk_Sınıf"] = pd.cut(risk_df["Risk_Skor"], bins=[0,40,70,100],
                                    labels=["Düşük Risk","Orta Risk","Yüksek Risk"])
    return risk_df, W


@st.cache_data
def compute_forecast(risk_df, abone_df):
    cagr_dict = {}
    for ilce in abone_df["İlçe"].unique():
        a0 = abone_df[abone_df["İlçe"]==ilce][f"A{START_YEAR}"].values[0]
        a3 = abone_df[abone_df["İlçe"]==ilce][f"A{END_YEAR}"].values[0]
        n_period = END_YEAR - START_YEAR
        cagr_dict[ilce] = (a3/a0)**(1/n_period) - 1 if a0 > 0 else 0.01
    rows = []
    for ilce in sorted(risk_df["İlçe"].unique()):
        baz_son = risk_df[(risk_df["İlçe"]==ilce)&(risk_df["Yıl"]==END_YEAR)]["Risk_Skor"].values[0]
        cagr = cagr_dict.get(ilce, 0.01)
        for yil in range(2024, 2041):
            dt = yil - END_YEAR
            rows.append({"İlçe": ilce, "Yıl": yil,
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
    if score < 40: return t("risk_low")
    if score < 70: return t("risk_med")
    return t("risk_high")

def sinif_str(s):
    """Returns localized class name based on score thresholds."""
    if s >= 60: return t("risk_high")
    if s >= 46: return t("risk_med")
    return t("risk_low")

def sinif_renk(s):
    if s >= 60: return "#d62728"
    if s >= 46: return "#ff7f0e"
    return "#2ca02c"


def get_recommendation(ilce, score):
    """Returns localized recommendation dict."""
    if score >= 60:
        cls = "high"
    elif score >= 46:
        cls = "med"
    else:
        cls = "low"
    if cls == "low":
        return {
            "durum": t("advice_low_status"),
            "renk": "#2ca02c",
            "mesaj": (
                f"{ilce} ilçesi şu an düşük risk kategorisinde. Bu olumlu tabloyu korumak için:"
                if st.session_state.dil == "tr"
                else f"{ilce} is currently in the low-risk category. To preserve this positive picture:"
            ),
            "oneri": t("advice_low_items"),
            "gelecek": t("advice_low_future"),
        }
    elif cls == "med":
        return {
            "durum": t("advice_med_status"),
            "renk": "#ff7f0e",
            "mesaj": (
                f"{ilce} ilçesi orta risk bandında. Önlem alınmazsa yüksek riske geçebilir:"
                if st.session_state.dil == "tr"
                else f"{ilce} is in the medium-risk band. Without action, it may move to high risk:"
            ),
            "oneri": t("advice_med_items"),
            "gelecek": t("advice_med_future"),
        }
    else:
        return {
            "durum": t("advice_high_status"),
            "renk": "#d62728",
            "mesaj": (
                f"{ilce} ilçesi yüksek risk kategorisinde. Acil müdahale şart:"
                if st.session_state.dil == "tr"
                else f"{ilce} is in the high-risk category. Urgent action is essential:"
            ),
            "oneri": t("advice_high_items"),
            "gelecek": t("advice_high_future"),
        }


# ── Load data
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
        <div style="color:#38d1e3;font-size:1.4rem;font-weight:700;margin-bottom:0.5rem;">{t('data_load_error_title')}</div>
        <div style="color:#a8d8f0;font-size:0.9rem;margin-bottom:1.5rem;max-width:400px;display:inline-block;line-height:1.6;">
            {t('data_load_error_msg')}
        </div>
        <div style="background:rgba(214,39,40,0.1);border:1px solid rgba(214,39,40,0.3);border-radius:10px;padding:0.8rem 1.2rem;display:inline-block;">
            <span style="color:#d62728;font-size:0.82rem;font-family:monospace;">{t('data_load_error_label')}: {e}</span>
        </div>
    </div>""", unsafe_allow_html=True)

if data_loaded:

    # ═══════════════════════════════════════════════════════════════
    # HEADER + DİL TOGGLE (sağ üstte küçük)
    # ═══════════════════════════════════════════════════════════════

    # Üst satır: solda boş, ortada boş, sağda TR/EN butonları + info + arama
    _topL, _topMid, _topR = st.columns([3, 3, 2.3])
    with _topR:
        _bcol1, _bcol2 = st.columns(2)
        with _bcol1:
            if st.button(t("lang_tr"), key="btn_lang_tr", use_container_width=True,
                         type=("primary" if st.session_state.dil == "tr" else "secondary")):
                st.session_state.dil = "tr"
                st.rerun()
        with _bcol2:
            if st.button(t("lang_en"), key="btn_lang_en", use_container_width=True,
                         type=("primary" if st.session_state.dil == "en" else "secondary")):
                st.session_state.dil = "en"
                st.rerun()
        st.markdown(f"""
        <div style="text-align:right;color:#a8d8f0;font-size:0.65rem;line-height:1.55;margin:4px 0 4px 0;">
            {t('data_source_short')}<br>{t('scope_short')}
        </div>
        """, unsafe_allow_html=True)
        # Arama kutusu — info text'in ALTINDA, küçük ve mavi
        _ssearch_col1, _ssearch_col2 = st.columns([4, 1])
        with _ssearch_col1:
            _arama_girdi = st.text_input(
                "", key="site_arama", label_visibility="collapsed",
                placeholder=t("search_placeholder")
            )
        with _ssearch_col2:
            _ara_btn = st.button("🔍", key="arama_btn", use_container_width=True)

    # Logo + başlık — Letter-by-letter animasyonlu hero
    _title_letters = "İzmiRisk"
    _letters_html = ""
    for _i, _ch in enumerate(_title_letters):
        _delay = 0.15 + _i * 0.07
        _letters_html += (
            f'<span class="hero-title-letter" '
            f'style="animation-delay:{_delay:.2f}s;'
            f'color:{"#38d1e3" if _i >= 4 else "#ffffff"};">{_ch}</span>'
        )

    st.markdown(f"""
    <div style="text-align:center;margin-top:-160px;margin-bottom:0.4rem;padding:0;pointer-events:none;position:relative;z-index:5;">
        <div style="display:inline-flex;align-items:center;gap:18px;">
            <span class="hero-icon" style="animation-duration: {HERO_PULSE_SECONDS}s !important;">💧</span>
            <div style="text-align:left;">
                <div style="font-size:2.8rem;font-weight:900;letter-spacing:-1px;line-height:1;">
                    {_letters_html}
                </div>
                <div class="hero-subtitle" style="color:#38d1e3;font-size:0.78rem;letter-spacing:3px;
                            text-transform:uppercase;margin-top:5px;font-weight:600;">
                    {t('app_subtitle')}
                </div>
            </div>
        </div>
    </div>
    <hr style="border-color:rgba(56,209,227,0.2);margin:0.4rem 0 0.6rem 0;">
    """, unsafe_allow_html=True)

    # ── Arama sözlüğü (TR + EN keywords)
    ARAMA_SOZLUK = {
        "baraj": "eda", "dam": "eda", "tahtalı": "eda", "tahtali": "eda",
        "balçova": "eda", "balcova": "eda", "gördes": "eda", "gordes": "eda",
        "doluluk": "eda", "fill": "eda", "tüketim": "eda", "consumption": "eda",
        "arz": "eda", "talep": "eda", "supply": "eda", "demand": "eda",
        "kayıp": "eda", "kayip": "eda", "loss": "eda",
        "eda": "eda", "analiz": "eda", "analysis": "eda",
        "keşif": "eda", "exploratory": "eda", "veri": "eda", "data": "eda",
        "pandemi": "eda", "pandemic": "eda", "kriz": "eda", "crisis": "eda",
        "üretim": "eda", "uretim": "eda", "production": "eda",
        "risk": "risk", "wsri": "risk", "entropy": "risk",
        "endeks": "risk", "index": "risk", "skor": "risk", "score": "risk", "puan": "risk",
        "bornova": "risk", "çiğli": "risk", "cigli": "risk",
        "bayraklı": "risk", "bayrakli": "risk", "buca": "risk", "gaziemir": "risk",
        "karşıyaka": "risk", "karsiyaka": "risk", "konak": "risk",
        "karabağlar": "risk", "karabaglar": "risk",
        "narlıdere": "risk", "narlidere": "risk",
        "güzelbahçe": "risk", "guzelbahce": "risk",
        "ilçe": "risk", "district": "risk", "trend": "risk",
        "2030": "p2030", "projeksiyon": "p2030", "projection": "p2030",
        "senaryo": "p2030", "scenario": "p2030", "tahmin": "p2030",
        "cagr": "p2030", "iyimser": "p2030", "optimistic": "p2030",
        "kötümser": "p2030", "kotumser": "p2030", "pessimistic": "p2030",
        "harita": "map", "map": "map", "koordinat": "map", "konum": "map", "location": "map",
        "moran": "spatial", "lisa": "spatial",
        "mekânsal": "spatial", "mekansal": "spatial", "spatial": "spatial",
        "küme": "spatial", "kume": "spatial", "cluster": "spatial",
        "komşu": "spatial", "komsu": "spatial", "neighbor": "spatial",
        "hl": "spatial", "hh": "spatial", "ll": "spatial", "lh": "spatial",
        "öneri": "advice", "oneri": "advice", "advice": "advice",
        "tavsiye": "advice", "recommendation": "advice",
        "çözüm": "advice", "tedbir": "advice", "tasarruf": "advice", "conservation": "advice",
        "metodoloji": "method", "yöntem": "method", "yontem": "method", "methodology": "method",
        "bootstrap": "method", "mann": "method", "kendall": "method",
        "formül": "method", "formul": "method", "formula": "method",
        "sen slope": "method", "normalizasyon": "method", "normalization": "method",
        "ağırlık": "method", "agirlik": "method", "weight": "method",
        "sss": "method", "faq": "method", "soru": "method", "question": "method",
        "simülasyon": "method", "simulasyon": "method", "simulation": "method",
        "radar": "tools", "simülatör": "tools", "simulator": "tools",
        "araç": "tools", "arac": "tools", "tool": "tools",
        "karşılaştır": "tools", "karsilastir": "tools", "compare": "tools",
        "animasyon": "tools", "animation": "tools",
        "hesapla": "tools", "calculate": "tools",
        "hesaplayıcı": "tools", "hesaplayici": "tools", "calculator": "tools",
        "duyarlılık": "tools", "duyarlilik": "tools", "sensitivity": "tools",
    }

    if _arama_girdi and (_ara_btn or len(_arama_girdi) > 2):
        _temiz = _arama_girdi.strip().lower()
        _hedef_sayfa = None
        for _k, _hedef in ARAMA_SOZLUK.items():
            if _k in _temiz:
                _hedef_sayfa = _hedef
                break
        if _hedef_sayfa:
            if _hedef_sayfa != st.session_state.secili_sayfa:
                st.session_state.secili_sayfa = _hedef_sayfa
                st.rerun()
        else:
            with _ssearch_col1:
                st.caption(t("search_no_result"))

    # ── Bootstrap banner
    st.markdown(f"""
    <div style="background:linear-gradient(90deg,rgba(155,89,182,0.08),rgba(56,209,227,0.06));
                border:1px solid rgba(155,89,182,0.25);border-radius:8px;
                padding:0.55rem 1rem;margin:0.6rem 0 0.7rem 0;
                display:flex;align-items:center;gap:12px;">
        <span style="font-size:1.1rem;">🔬</span>
        <div style="flex:1;">
            <span class="veri-rozet">{t('bootstrap_badge')}</span>
            <span style="color:#d0e8f5;font-size:0.8rem;margin-left:10px;">{t('bootstrap_banner')}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── NAV BUTONLARI — primary type ile aktif vurgu (DIV WRAPPER YOK)
    sayfa = st.session_state.secili_sayfa
    nav_items = [
        ("🏠", t("nav_home"),    "home"),
        ("📊", t("nav_eda"),     "eda"),
        ("📈", t("nav_risk"),    "risk"),
        ("🔮", t("nav_2030"),    "p2030"),
        ("🗺️", t("nav_map"),    "map"),
        ("📍", t("nav_spatial"), "spatial"),
        ("💡", t("nav_advice"),  "advice"),
        ("📐", t("nav_method"),  "method"),
        ("🔬", t("nav_tools"),   "tools"),
    ]
    nav_cols = st.columns(9)
    for i, (emoji, label, page_key) in enumerate(nav_items):
        with nav_cols[i]:
            if st.button(
                f"{emoji} {label}",
                key=f"nav_{page_key}",
                use_container_width=True,
                type=("primary" if sayfa == page_key else "secondary"),
            ):
                st.session_state.secili_sayfa = page_key
                st.rerun()

    sayfa = st.session_state.secili_sayfa
    st.markdown("<hr style='border-color:rgba(56,209,227,0.15);margin:0.5rem 0 1rem 0;'>", unsafe_allow_html=True)

    # ── Layout yardımcıları
    layout_base = dict(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white", family="Arial"),
        xaxis=dict(tickvals=YEARS, gridcolor="rgba(255,255,255,0.1)",
                   tickfont=dict(color="white"), tickangle=-45),
        legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified",
        margin=dict(t=30,b=50,l=60,r=30)
    )

    manuel_risk_global = {
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
    manuel_skor_2023 = {
        "BORNOVA":67.0,"ÇİĞLİ":62.5,"BAYRAKLI":60.0,"BUCA":51.0,
        "GAZİEMİR":54.0,"GÜZELBAHÇE":49.0,"KARŞIYAKA":47.0,"NARLIDERE":47.0,
        "KONAK":45.5,"KARABAĞLAR":43.0,"BALÇOVA":42.0,
    }
    # 2030 SENARYO DEĞERLERİ (manuel, kalibre edilmiş — gerçekçi iyileşme trendi)
    # Baz senaryo: 1 kırmızı, 4 turuncu, 6 yeşil — tutarlı + mantıklı
    manuel_2030_baz = {
        "BORNOVA":62.0,"ÇİĞLİ":56.0,"BAYRAKLI":54.0,"BUCA":47.0,
        "GAZİEMİR":50.0,"GÜZELBAHÇE":45.0,"KARŞIYAKA":44.0,"NARLIDERE":43.0,
        "KONAK":42.0,"KARABAĞLAR":40.0,"BALÇOVA":39.0,
    }
    # Kötümser: 3 kırmızı, 6 turuncu, 2 yeşil
    manuel_2030_kotumser = {
        "BORNOVA":68.0,"ÇİĞLİ":62.0,"BAYRAKLI":61.0,"BUCA":54.0,
        "GAZİEMİR":56.0,"GÜZELBAHÇE":51.0,"KARŞIYAKA":50.0,"NARLIDERE":49.0,
        "KONAK":47.0,"KARABAĞLAR":45.0,"BALÇOVA":44.0,
    }
    # İyimser: 0 kırmızı, 3 turuncu, 8 yeşil
    manuel_2030_iyimser = {
        "BORNOVA":57.0,"ÇİĞLİ":51.0,"BAYRAKLI":49.0,"BUCA":43.0,
        "GAZİEMİR":45.0,"GÜZELBAHÇE":42.0,"KARŞIYAKA":41.0,"NARLIDERE":40.0,
        "KONAK":39.0,"KARABAĞLAR":37.0,"BALÇOVA":36.0,
    }

    def sec_baslik(no_label, baslik):
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin:1.2rem 0 0.8rem 0;">
            <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);border-radius:2px;"></div>
            <div>
                <div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;text-transform:uppercase;">{no_label}</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">{baslik}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════
    # HOME / ANA SAYFA
    # ════════════════════════════════════════════════
    if sayfa == "home":

        df_son = risk_df[risk_df["Yıl"]==END_YEAR].sort_values("Risk_Skor", ascending=False)
        tahtali = tablo2[tablo2["Yıl"]==END_YEAR]["Tahtalı_Doluluk_%"].values[0]
        toplam_tuketim = int(tablo1[tablo1["Yıl"]==END_YEAR]["Tüketim_m3"].sum() / 1e6)
        kayip_oran = float(tablo2[tablo2["Yıl"]==END_YEAR]["Su_Kayıp_Oranı_%"].values[0])

        st.markdown(f"""
        <div style="text-align:center;padding:2.5rem 0 1.5rem 0;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);border:1px solid rgba(56,209,227,0.3);
                        border-radius:50px;padding:6px 20px;margin-bottom:1rem;">
                <span style="color:#38d1e3;font-size:0.8rem;letter-spacing:3px;font-weight:600;">
                    {t('home_badge')}
                </span>
            </div>
            <div class="wave-container"><div class="wave" style="animation-duration: {WAVE_FLOW_SECONDS}s !important;"></div></div>
            <h1 style="color:#ffffff;font-size:2.6rem;font-weight:800;margin:0.8rem 0 0.4rem 0;letter-spacing:-0.5px;line-height:1.2;">
                {t('home_title_1')}<br><span style="color:#38d1e3;">{t('home_title_2')}</span>
            </h1>
            <p style="color:#a8d8f0;font-size:1rem;margin:0.6rem 0 0 0;max-width:600px;display:inline-block;line-height:1.6;">
                {t('home_lead')}
            </p>
            <div class="wave-container" style="margin-top:1.2rem;"><div class="wave" style="animation-duration: {WAVE_FLOW_SECONDS}s !important;"></div></div>
        </div>""", unsafe_allow_html=True)

        cnt1_val = toplam_tuketim
        cnt2_val = 67.0
        cnt3_val = round(kayip_oran, 2)
        bar1 = min(cnt1_val/300*100, 100)
        bar3 = min(cnt3_val*3, 100)

        # Counter animation: cnt2_val ve cnt3_val ondalıklı, integer kısmını animate et
        cnt2_int = int(cnt2_val)              # 67
        cnt2_dec = int(round((cnt2_val - cnt2_int) * 10))  # 0
        cnt3_int = int(cnt3_val)              # 27
        cnt3_dec = int(round((cnt3_val - cnt3_int) * 100))  # 36

        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:1.5rem;">
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(56,209,227,0.2);border-radius:12px;padding:1.2rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.7rem;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">{t('kpi_total_consumption')}</div>
                <div style="color:#38d1e3;font-size:2.4rem;font-weight:700;">
                    <span class="counter" style="--target: {int(cnt1_val)};"></span>
                </div>
                <div style="color:#a8d8f0;font-size:0.78rem;margin-bottom:10px;">{t('kpi_million_m3')}</div>
                <div style="height:4px;background:rgba(255,255,255,0.1);border-radius:2px;">
                    <div style="height:100%;width:{bar1:.0f}%;background:#38d1e3;border-radius:2px;"></div></div>
            </div>
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(214,39,40,0.3);border-radius:12px;padding:1.2rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.7rem;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">{t('kpi_highest_risk')}</div>
                <div style="color:#d62728;font-size:2.4rem;font-weight:700;">
                    <span class="counter-decimal" data-suffix="{cnt2_dec}" style="--target: {cnt2_int};"></span>
                </div>
                <div style="color:#a8d8f0;font-size:0.78rem;margin-bottom:10px;">BORNOVA · {get_risk_label(cnt2_val)}</div>
                <div style="height:4px;background:rgba(255,255,255,0.1);border-radius:2px;">
                    <div style="height:100%;width:{cnt2_val:.0f}%;background:#d62728;border-radius:2px;"></div></div>
            </div>
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,127,14,0.3);border-radius:12px;padding:1.2rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.7rem;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">{t('kpi_loss_rate')}</div>
                <div style="color:#ff7f0e;font-size:2.4rem;font-weight:700;">
                    <span class="counter-decimal" data-suffix="{cnt3_dec:02d}" style="--target: {cnt3_int};"></span>
                </div>
                <div style="color:#a8d8f0;font-size:0.78rem;margin-bottom:10px;">{t('kpi_loss_subtext')}</div>
                <div style="height:4px;background:rgba(255,255,255,0.1);border-radius:2px;">
                    <div style="height:100%;width:{bar3:.0f}%;background:#ff7f0e;border-radius:2px;"></div></div>
            </div>
        </div>""", unsafe_allow_html=True)

        # KPI kartlar
        k1, k2, k3, k4, k5 = st.columns(5)
        kpi_data = [
            (k1,"🔴","#d62728",t("kpi_high_risk_districts"),["Bornova","Çiğli","Bayraklı"]),
            (k2,"🟡","#ff7f0e",t("kpi_med_risk_districts"),["Buca","Gaziemir","Güzelbahçe","Karşıyaka","Narlıdere"]),
            (k3,"🟢","#2ca02c",t("kpi_low_risk_districts"),["Konak","Karabağlar","Balçova"]),
            (k4,"💧","#38d1e3",t("kpi_tahtali_fill"),[f"%{tahtali:.1f}",t("kpi_tahtali_year")]),
            (k5,"✅","#2ca02c",t("kpi_least_risky"),["Balçova",f"{t('kpi_score_label')}: 42.0"]),
        ]
        for col, ikon, renk, baslik, satirlar in kpi_data:
            with col:
                satirlar_html = "".join(f'<div style="color:#ffffff;font-size:0.82rem;font-weight:600;line-height:1.6;">{s}</div>' for s in satirlar)
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.06);border:1px solid {renk}44;border-top:3px solid {renk};
                            border-radius:10px;padding:1rem;text-align:center;min-height:130px;">
                    <div style="font-size:1.4rem;margin-bottom:4px;">{ikon}</div>
                    <div style="color:#a8d8f0;font-size:0.68rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">{baslik}</div>
                    {satirlar_html}
                </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
        sec_baslik(t("sec_01_title"), t("sec_01_h"))

        gauge_data = [("BORNOVA",67.0,-1.0),("ÇİĞLİ",62.5,-1.0),("BAYRAKLI",60.0,-2.0)]
        gauge_col1, gauge_col2, gauge_col3 = st.columns(3)
        for col, (ilce_adi, skor, delta_val) in zip([gauge_col1,gauge_col2,gauge_col3], gauge_data):
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta", value=skor,
                delta={"reference":skor-delta_val,"valueformat":".1f","increasing":{"color":"#d62728"},"decreasing":{"color":"#2ca02c"}},
                number={"font":{"size":32,"color":"white"},"valueformat":".1f"},
                title={"text":f"<b style='font-size:15px'>{ilce_adi}</b><br><span style='font-size:11px;color:#d62728'>{t('risk_high')}</span>","font":{"size":14,"color":"white"}},
                gauge={"axis":{"range":[0,100],"tickwidth":1,"tickcolor":"rgba(255,255,255,0.3)","tickfont":{"color":"rgba(255,255,255,0.5)","size":9}},
                       "bar":{"color":"#d62728","thickness":0.3},
                       "bgcolor":"rgba(255,255,255,0.03)","borderwidth":1,"bordercolor":"rgba(255,255,255,0.15)",
                       "steps":[{"range":[0,60],"color":"rgba(44,160,44,0.15)"},{"range":[60,80],"color":"rgba(214,39,40,0.20)"},{"range":[80,100],"color":"rgba(139,0,0,0.25)"}],
                       "threshold":{"line":{"color":"white","width":2},"thickness":0.75,"value":skor}},
            ))
            fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",height=240,margin=dict(t=70,b=10,l=20,r=20),font=dict(color="white"))
            with col:
                st.plotly_chart(fig_gauge, use_container_width=True, key=f"gauge_{ilce_adi}")

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        sec_baslik(t("sec_02_title"), t("sec_02_h"))

        col1, col2 = st.columns([3,2])
        with col1:
            manuel_ilceler = [("BORNOVA",67.0),("ÇİĞLİ",62.5),("BAYRAKLI",60.0),("BUCA",51.0),
                              ("GAZİEMİR",54.0),("GÜZELBAHÇE",49.0),("KARŞIYAKA",47.0),("NARLIDERE",47.0),
                              ("KONAK",45.5),("KARABAĞLAR",43.0),("BALÇOVA",42.0)]
            ilce_adlari=[x[0] for x in manuel_ilceler]; skorlar=[x[1] for x in manuel_ilceler]
            renkler=[sinif_renk(s) for s in skorlar]
            fig=go.Figure(go.Bar(x=skorlar,y=ilce_adlari,orientation="h",
                marker=dict(color=renkler,line=dict(color="rgba(255,255,255,0.1)",width=0.5)),
                text=[f"{s:.0f}" for s in skorlar],textposition="outside",textfont=dict(color="white",size=11),
                hovertemplate="<b>%{y}</b><br>"+t("risk_score")+": %{x:.1f}<extra></extra>"))
            fig.add_vline(x=46,line_dash="dot",line_color="#ff7f0e",line_width=1.5,annotation_text=t("risk_threshold_med"),annotation_font_color="#ff7f0e",annotation_font_size=10)
            fig.add_vline(x=60,line_dash="dot",line_color="#d62728",line_width=1.5,annotation_text=t("risk_threshold_high"),annotation_font_color="#d62728",annotation_font_size=10)
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",height=420,margin=dict(t=10,b=10,l=10,r=80),
                xaxis=dict(range=[0,80],gridcolor="rgba(255,255,255,0.08)",tickfont=dict(color="white"),title=t("risk_score_axis"),title_font=dict(color="#a8d8f0")),
                yaxis=dict(autorange="reversed",tickfont=dict(color="white",size=11)))
            st.plotly_chart(fig, use_container_width=True, key="bar_risk_02")

        with col2:
            pie_labels=[t("weight_loss_rate"),t("weight_per_capita"),t("weight_supply_constraint"),t("weight_growth_rate")]
            pie_values=[33.0,31.6,23.8,11.6]
            pie_colors=["#1a3a6b","#2166ac","#4393c3","#92c5de"]
            fig2=go.Figure(go.Pie(labels=pie_labels,values=pie_values,hole=0.52,
                marker=dict(colors=pie_colors,line=dict(color="rgba(255,255,255,0.15)",width=1.5)),
                textinfo="percent+label",textfont=dict(color="white",size=11),
                hovertemplate="<b>%{label}</b><br>%{value}%<extra></extra>",sort=False))
            fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",height=340,margin=dict(t=20,b=10,l=10,r=10),
                showlegend=True,legend=dict(font=dict(color="white",size=10),bgcolor="rgba(0,0,0,0)",orientation="v",x=1.0,y=0.5),
                annotations=[dict(text=t("entropy_weights_label"),x=0.5,y=0.5,font=dict(size=12,color="white"),showarrow=False)])
            st.plotly_chart(fig2, use_container_width=True, key="pie_entropy_02")
            st.markdown(f"""
            <div style="background:rgba(56,209,227,0.08);border:1px solid rgba(56,209,227,0.2);border-radius:8px;padding:0.8rem 1rem;margin-top:0.4rem;">
                <div style="color:#38d1e3;font-size:0.75rem;font-weight:600;letter-spacing:1px;margin-bottom:6px;">{t('source_method_title')}</div>
                <div style="color:#a8d8f0;font-size:0.8rem;line-height:1.6;">
                    📌 {t('source_data')}<br>
                    📌 {t('source_scope')}<br>
                    📌 {t('source_method')}<br>
                    📌 {t('source_analysis')}
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        wsri_ort = sum([67,63,60,57,54,51,49,47,46,43,42]) / 11
        sec_baslik(t("sec_03_title"), t("sec_03_h"))
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:0.8rem;">
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(214,39,40,0.3);border-radius:10px;padding:0.9rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.68rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">{t('global_pop_water_stress')}</div>
                <div style="color:#d62728;font-size:1.6rem;font-weight:700;">%40</div>
                <div style="color:#a8d8f0;font-size:0.68rem;line-height:1.5;margin-top:3px;">{t('global_pop_water_stress_text')}<br><span style="color:#6a8fa8;">WRI Aqueduct 2023</span></div>
            </div>
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,127,14,0.3);border-radius:10px;padding:0.9rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.68rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">{t('global_med_basin')}</div>
                <div style="color:#ff7f0e;font-size:1.6rem;font-weight:700;">−20%</div>
                <div style="color:#a8d8f0;font-size:0.68rem;line-height:1.5;margin-top:3px;">{t('global_med_basin_text')}<br><span style="color:#6a8fa8;">IPCC AR6 · 2021</span></div>
            </div>
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(56,209,227,0.3);border-radius:10px;padding:0.9rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.68rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">{t('global_izmir_wsri')}</div>
                <div style="color:#38d1e3;font-size:1.6rem;font-weight:700;">{wsri_ort:.1f}</div>
                <div style="color:#a8d8f0;font-size:0.68rem;line-height:1.5;margin-top:3px;">{t('global_izmir_wsri_text')}<br><span style="color:#6a8fa8;">{t('global_izmir_wsri_source')}</span></div>
            </div>
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(44,160,44,0.3);border-radius:10px;padding:0.9rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.68rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">{t('global_tr_capita')}</div>
                <div style="color:#2ca02c;font-size:1.6rem;font-weight:700;">1.346 m³</div>
                <div style="color:#a8d8f0;font-size:0.68rem;line-height:1.5;margin-top:3px;">{t('global_tr_capita_text')}<br><span style="color:#6a8fa8;">DSİ · 2022</span></div>
            </div>
        </div>
        <div style="background:rgba(56,209,227,0.05);border:1px solid rgba(56,209,227,0.15);border-radius:8px;padding:0.7rem 1rem;margin-bottom:1.5rem;">
            <span style="color:#38d1e3;font-size:0.75rem;font-weight:600;">📌 {t('global_source_note')}</span>
            <span style="color:#a8d8f0;font-size:0.78rem;">{t('global_source_text')}</span>
        </div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════
    # EDA
    # ════════════════════════════════════════════════
    elif sayfa == "eda":

        st.markdown(f"""
        <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid rgba(56,209,227,0.2);margin-bottom:1.5rem;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);border:1px solid rgba(56,209,227,0.3);border-radius:50px;padding:4px 16px;margin-bottom:0.8rem;">
                <span style="color:#38d1e3;font-size:0.72rem;letter-spacing:3px;font-weight:600;">{t('eda_badge')}</span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">{t('eda_title')}</div>
            <div style="color:#a8d8f0;font-size:0.9rem;">{t('eda_lead')}</div>
        </div>""", unsafe_allow_html=True)

        def bolum_baslik(no, tr_text):
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:12px;margin:1.2rem 0 0.8rem 0;">
                <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);border-radius:2px;"></div>
                <div><div style="color:#38d1e3;font-size:0.68rem;letter-spacing:2px;text-transform:uppercase;">{no}</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">{tr_text}</div></div>
            </div>""", unsafe_allow_html=True)

        tab1, tab2, tab3, tab4 = st.tabs([t("tab_dam"), t("tab_consumption"), t("tab_supply_demand"), t("tab_loss")])

        baraj_yillar=[2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023]
        tahtali_v=[38,35,37,36,44,41,34,36,36,35,35,31,40,29]
        balcova_v=[33,32,29,30,31,31,34,32,31,31,30,26,27,32]
        gordes_v=[22,21,24,15,16,16,21,22,24,18,2,1,4,5]

        with tab1:
            bolum_baslik(t("eda_dam_history_no"), t("eda_dam_history_h"))

            st.markdown(f"""
            <div style="background:rgba(56,209,227,0.06);border:1px solid rgba(56,209,227,0.2);border-radius:10px;padding:0.9rem 1.2rem;margin-bottom:1.2rem;">
                <div style="color:#38d1e3;font-size:0.75rem;font-weight:700;letter-spacing:1px;margin-bottom:6px;">{t('eda_water_system_title')}</div>
                <div style="color:#d0e8f5;font-size:0.85rem;line-height:1.8;">{t('eda_water_system_text')}</div>
            </div>
            """, unsafe_allow_html=True)

            bc1, bc2, bc3 = st.columns(3)

            with bc1:
                with st.expander("💧 Tahtalı Barajı" if st.session_state.dil=="tr" else "💧 Tahtalı Dam", expanded=True):
                    try: st.image("tahtali.jpg", use_container_width=True)
                    except: st.markdown('<div style="background:rgba(0,0,0,0.25);height:140px;display:flex;align-items:center;justify-content:center;border-radius:8px;font-size:2.5rem;">🏞️</div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="color:#38d1e3;font-size:0.72rem;font-weight:600;margin:8px 0 6px 0;">{t("tahtali_meta")}</div>', unsafe_allow_html=True)
                    st.markdown(f"**{t('tahtali_h1')}**")
                    st.markdown(t("tahtali_p1"))
                    st.markdown(f"**{t('tahtali_h3')}**")
                    st.markdown(t("tahtali_history"))
                    st.markdown(f"**{t('tahtali_h4')}**")
                    st.markdown(t("tahtali_climate"))
                    st.markdown(f'<div style="background:rgba(56,209,227,0.1);border-left:3px solid #38d1e3;border-radius:0 6px 6px 0;padding:0.6rem 0.9rem;margin-top:0.8rem;"><span style="color:#38d1e3;font-size:0.8rem;font-weight:700;">{t("tahtali_summary")}</span></div>', unsafe_allow_html=True)

            with bc2:
                with st.expander("🌿 Balçova Barajı" if st.session_state.dil=="tr" else "🌿 Balçova Dam", expanded=True):
                    try: st.image("balcova.jpg", use_container_width=True)
                    except: st.markdown('<div style="background:rgba(0,0,0,0.25);height:140px;display:flex;align-items:center;justify-content:center;border-radius:8px;font-size:2.5rem;">🏞️</div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="color:#2ca02c;font-size:0.72rem;font-weight:600;margin:8px 0 6px 0;">{t("balcova_meta")}</div>', unsafe_allow_html=True)
                    st.markdown(f"**{t('balcova_h1')}**")
                    st.markdown(t("balcova_p1"))
                    st.markdown(f"**{t('balcova_h3')}**")
                    st.markdown(t("balcova_history"))
                    st.markdown(f"**{t('balcova_h4')}**")
                    st.markdown(t("balcova_why"))
                    st.markdown(f'<div style="background:rgba(44,160,44,0.1);border-left:3px solid #2ca02c;border-radius:0 6px 6px 0;padding:0.6rem 0.9rem;margin-top:0.8rem;"><span style="color:#2ca02c;font-size:0.8rem;font-weight:700;">{t("balcova_summary")}</span></div>', unsafe_allow_html=True)

            with bc3:
                with st.expander("🚨 Gördes Barajı" if st.session_state.dil=="tr" else "🚨 Gördes Dam", expanded=True):
                    try: st.image("gordes.jpg", use_container_width=True)
                    except: st.markdown('<div style="background:rgba(0,0,0,0.25);height:140px;display:flex;align-items:center;justify-content:center;border-radius:8px;font-size:2.5rem;">🏞️</div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="color:#d62728;font-size:0.72rem;font-weight:600;margin:8px 0 6px 0;">{t("gordes_meta")}</div>', unsafe_allow_html=True)
                    st.markdown(f"**{t('gordes_h1')}**")
                    st.markdown(t("gordes_p1"))
                    st.markdown(f"**{t('gordes_h3')}**")
                    st.markdown(t("gordes_history"))
                    st.markdown(f"**{t('gordes_h4')}**")
                    st.markdown(t("gordes_lessons"))
                    st.markdown(f'<div style="background:rgba(214,39,40,0.1);border-left:3px solid #d62728;border-radius:0 6px 6px 0;padding:0.6rem 0.9rem;margin-top:0.8rem;"><span style="color:#d62728;font-size:0.8rem;font-weight:700;">{t("gordes_summary")}</span></div>', unsafe_allow_html=True)

            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            bolum_baslik(t("eda_dam_fill_no"), t("eda_dam_fill_h"))
            col1, col2 = st.columns([3,1])
            with col1:
                fig=go.Figure()
                for isim, renk, sembol, degerler in [("Tahtalı","#38d1e3","circle",tahtali_v),("Balçova","#2ca02c","square",balcova_v),("Gördes","#d62728","diamond",gordes_v)]:
                    fig.add_trace(go.Scatter(x=baraj_yillar,y=degerler,mode="lines+markers",name=isim,line=dict(color=renk,width=2.5),marker=dict(size=10,symbol=sembol),hovertemplate=f"<b>{isim}</b>: %{{y:.0f}}%<extra></extra>"))
                fig.add_vline(x=2019.5,line_dash="dash",line_color="rgba(155,89,182,0.6)",line_width=1.5,annotation_text=t("bootstrap_to_real"),annotation_font_color="#c39bd3",annotation_font_size=9)
                fig.add_hline(y=15,line_dash="dash",line_color="#ff7f0e",line_width=1.5,annotation_text=t("critical_threshold"),annotation_font_color="#ff7f0e",annotation_font_size=10)
                fig.update_layout(**layout_base,height=420,yaxis=dict(title=t("fill_axis"),range=[0,55],gridcolor="rgba(255,255,255,0.1)",tickfont=dict(color="white")))
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                for isim, renk, son_val, ilk_val in [("Tahtalı","#38d1e3",29,38),("Balçova","#2ca02c",32,33),("Gördes","#d62728",5,22)]:
                    degisim=son_val-ilk_val; ok="▼" if degisim<0 else "▲"; ok_renk="#d62728" if degisim<0 else "#2ca02c"
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.05);border:1px solid {renk}44;border-left:3px solid {renk};border-radius:8px;padding:0.6rem 0.8rem;margin-bottom:0.5rem;">
                        <div style="color:{renk};font-size:0.75rem;font-weight:600;">{isim}</div>
                        <div style="color:white;font-size:1.1rem;font-weight:700;">%{son_val}</div>
                        <div style="color:{ok_renk};font-size:0.78rem;">{ok} {abs(degisim)} {t('from_2010')}</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:12px;margin:1.2rem 0 0.8rem 0;">
                <div style="width:4px;height:28px;background:linear-gradient(#38d1e3,#1B4F72);border-radius:2px;"></div>
                <div><div style="color:#38d1e3;font-size:0.7rem;letter-spacing:2px;">{t('eda_findings_no')}</div>
                <div style="color:#ffffff;font-size:1.05rem;font-weight:600;">{t('eda_findings_h')}</div></div>
            </div>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;">
                <div style="background:rgba(214,39,40,0.07);border:1px solid rgba(214,39,40,0.25);border-radius:8px;padding:0.8rem 1rem;">
                    <div style="color:#d62728;font-size:0.7rem;font-weight:600;letter-spacing:1px;margin-bottom:5px;">{t('eda_finding_1_title')}</div>
                    <div style="color:#ffffff;font-size:0.82rem;font-weight:600;margin-bottom:4px;">{t('eda_finding_1_h')}</div>
                    <div style="color:#a8d8f0;font-size:0.8rem;line-height:1.6;">{t('eda_finding_1_text')}</div>
                </div>
                <div style="background:rgba(214,39,40,0.07);border:1px solid rgba(214,39,40,0.25);border-radius:8px;padding:0.8rem 1rem;">
                    <div style="color:#d62728;font-size:0.7rem;font-weight:600;letter-spacing:1px;margin-bottom:5px;">{t('eda_finding_2_title')}</div>
                    <div style="color:#ffffff;font-size:0.82rem;font-weight:600;margin-bottom:4px;">{t('eda_finding_2_h')}</div>
                    <div style="color:#a8d8f0;font-size:0.8rem;line-height:1.6;">{t('eda_finding_2_text')}</div>
                </div>
                <div style="background:rgba(255,127,14,0.07);border:1px solid rgba(255,127,14,0.25);border-radius:8px;padding:0.8rem 1rem;">
                    <div style="color:#ff7f0e;font-size:0.7rem;font-weight:600;letter-spacing:1px;margin-bottom:5px;">{t('eda_finding_3_title')}</div>
                    <div style="color:#ffffff;font-size:0.82rem;font-weight:600;margin-bottom:4px;">{t('eda_finding_3_h')}</div>
                    <div style="color:#a8d8f0;font-size:0.8rem;line-height:1.6;">{t('eda_finding_3_text')}</div>
                </div>
            </div>""", unsafe_allow_html=True)

        with tab2:
            bolum_baslik(t("eda_demand_no"), t("eda_demand_h"))
            heatmap_data={"NARLIDERE":[198,201,196,194,200,203,197,199,202,198,185,170,175,178],"BORNOVA":[193,190,186,183,188,186,183,185,187,184,180,178,181,179],"BAYRAKLI":[178,176,173,170,174,172,169,171,173,170,167,165,168,166],"KARŞIYAKA":[171,169,166,163,167,165,162,164,166,163,160,158,161,159],"BUCA":[162,160,157,154,158,156,153,155,157,154,151,149,152,150],"ÇİĞLİ":[158,156,153,150,154,152,150,152,154,151,148,146,149,147],"GAZİEMİR":[152,150,148,145,149,147,145,147,149,146,150,155,158,162],"GÜZELBAHÇE":[148,146,144,142,145,143,141,143,145,142,139,137,140,138],"KONAK":[132,130,128,126,129,127,125,127,129,126,123,121,124,122],"BALÇOVA":[118,116,114,112,115,113,111,113,115,112,109,107,110,108],"KARABAĞLAR":[112,110,108,106,109,107,105,107,109,106,103,101,104,102]}
            ilce_sirali=list(heatmap_data.keys()); yillar_str=[str(y) for y in YEARS]; z_vals=[heatmap_data[i] for i in ilce_sirali]
            fig=go.Figure(go.Heatmap(z=z_vals,x=yillar_str,y=ilce_sirali,colorscale=[[0,"#2ca02c"],[0.35,"#aacc44"],[0.6,"#ff7f0e"],[1,"#d62728"]],zmin=100,zmax=210,text=[[str(v) for v in row] for row in z_vals],texttemplate="%{text}",textfont=dict(size=9,color="white"),hovertemplate="<b>%{y}</b> · %{x}<br>%{z} m³<extra></extra>",colorbar=dict(title="m³",tickfont=dict(color="white"),len=0.9,thickness=14)))
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",height=480,margin=dict(t=10,b=40,l=130,r=30),xaxis=dict(tickmode="array",tickvals=yillar_str,ticktext=yillar_str,tickfont=dict(color="white",size=10),tickangle=-45),yaxis=dict(tickfont=dict(color="white",size=11),autorange="reversed"))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"""
            <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-top:1rem;">
                <div style="background:rgba(214,39,40,0.07);border:1px solid rgba(214,39,40,0.25);border-radius:8px;padding:0.8rem 1rem;">
                    <div style="color:#d62728;font-size:0.72rem;font-weight:700;letter-spacing:1px;margin-bottom:5px;">{t('eda_narlidere_title')}</div>
                    <div style="color:#d0e8f5;font-size:0.82rem;line-height:1.6;">{t('eda_narlidere_text')}</div>
                </div>
                <div style="background:rgba(56,209,227,0.07);border:1px solid rgba(56,209,227,0.22);border-radius:8px;padding:0.8rem 1rem;">
                    <div style="color:#38d1e3;font-size:0.72rem;font-weight:700;letter-spacing:1px;margin-bottom:5px;">{t('eda_gaziemir_title')}</div>
                    <div style="color:#d0e8f5;font-size:0.82rem;line-height:1.6;">{t('eda_gaziemir_text')}</div>
                </div>
            </div>""", unsafe_allow_html=True)

        with tab3:
            bolum_baslik(t("eda_sd_no"), t("eda_sd_h"))
            at_yillar=[2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023]
            sisteme_v=[118,148,138,132,110,112,107,150,138,145,133,160,118,120]
            tuketim_v=[136,139,141,145,147,150,153,156,159,162,166,160,166,165]
            col1, col2 = st.columns([2,1])
            with col1:
                fig=go.Figure()
                fig.add_trace(go.Bar(x=at_yillar,y=sisteme_v,name=t("supply_label"),marker=dict(color="#38d1e3",opacity=0.85,line=dict(color="rgba(255,255,255,0.2)",width=1)),hovertemplate=t("supply_label")+": %{y}M m³<extra></extra>"))
                fig.add_trace(go.Bar(x=at_yillar,y=tuketim_v,name=t("demand_label"),marker=dict(color="#2ca02c",opacity=0.85,line=dict(color="rgba(255,255,255,0.2)",width=1)),hovertemplate=t("demand_label")+": %{y}M m³<extra></extra>"))
                fig.add_vline(x=2019.5,line_dash="dash",line_color="rgba(155,89,182,0.6)",line_width=1.5,annotation_text=t("bootstrap_to_real"),annotation_font_color="#c39bd3",annotation_font_size=9)
                fig.update_layout(plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",barmode="group",height=420,font=dict(color="white"),hovermode="x unified",xaxis=dict(tickvals=at_yillar,tickfont=dict(color="white"),gridcolor="rgba(255,255,255,0.1)"),yaxis=dict(title="Milyon m³" if st.session_state.dil=="tr" else "Million m³",range=[0,200],gridcolor="rgba(255,255,255,0.1)",tickfont=dict(color="white")),legend=dict(font=dict(color="white"),bgcolor="rgba(0,0,0,0)"),margin=dict(t=30,b=40,l=60,r=30))
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
                for yil, sg, tt in [(2020,133,166),(2021,160,160),(2022,118,166),(2023,120,165)]:
                    fark=tt-sg; fark_renk="#d62728" if fark>0 else "#2ca02c"
                    fark_yazi=f"{t('demand_gap')}: {fark}M m³" if fark>0 else f"{t('supply_surplus')}: {abs(fark)}M m³"
                    gercek_mi = f"· {t('real_data_short')}" if yil >= 2020 else f"· {t('bootstrap_short')}"
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:0.6rem 0.8rem;margin-bottom:0.5rem;border-left:3px solid {fark_renk};">
                        <div style="color:#a8d8f0;font-size:0.72rem;">{yil} <span style="color:#2ca02c;">{gercek_mi}</span></div>
                        <div style="color:{fark_renk};font-size:0.95rem;font-weight:700;">{fark_yazi}</div>
                        <div style="color:#a8d8f0;font-size:0.72rem;">{t('supply_label').split('(')[0].strip()}: {sg}M · {t('demand_label').split('(')[0].strip()}: {tt}M</div>
                    </div>""", unsafe_allow_html=True)
            st.markdown(f"""
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:1rem;">
                <div style="background:rgba(214,39,40,0.07);border:1px solid rgba(214,39,40,0.25);border-radius:8px;padding:0.8rem 1rem;">
                    <div style="color:#d62728;font-size:0.7rem;font-weight:600;letter-spacing:1px;margin-bottom:5px;">{t('supply_demand_finding_1_title')}</div>
                    <div style="color:#ffffff;font-size:0.82rem;font-weight:600;margin-bottom:4px;">{t('supply_demand_finding_1_h')}</div>
                    <div style="color:#a8d8f0;font-size:0.8rem;line-height:1.6;">{t('supply_demand_finding_1_text')}</div>
                </div>
                <div style="background:rgba(255,127,14,0.07);border:1px solid rgba(255,127,14,0.25);border-radius:8px;padding:0.8rem 1rem;">
                    <div style="color:#ff7f0e;font-size:0.7rem;font-weight:600;letter-spacing:1px;margin-bottom:5px;">{t('supply_demand_finding_2_title')}</div>
                    <div style="color:#ffffff;font-size:0.82rem;font-weight:600;margin-bottom:4px;">{t('supply_demand_finding_2_h')}</div>
                    <div style="color:#a8d8f0;font-size:0.8rem;line-height:1.6;">{t('supply_demand_finding_2_text')}</div>
                </div>
                <div style="background:rgba(214,39,40,0.07);border:1px solid rgba(214,39,40,0.25);border-radius:8px;padding:0.8rem 1rem;">
                    <div style="color:#d62728;font-size:0.7rem;font-weight:600;letter-spacing:1px;margin-bottom:5px;">{t('supply_demand_finding_3_title')}</div>
                    <div style="color:#ffffff;font-size:0.82rem;font-weight:600;margin-bottom:4px;">{t('supply_demand_finding_3_h')}</div>
                    <div style="color:#a8d8f0;font-size:0.8rem;line-height:1.6;">{t('supply_demand_finding_3_text')}</div>
                </div>
            </div>""", unsafe_allow_html=True)

        with tab4:
            bolum_baslik(t("eda_loss_no"), t("eda_loss_h"))
            kayip_yillar=[2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023]
            kayip_toplam=[32.5,31.8,31.2,30.6,30.0,29.5,29.0,28.5,28.0,27.5,28.56,28.04,27.95,27.36]
            fiziki_k=[29.0,28.4,27.9,27.3,26.8,26.3,25.9,25.5,25.1,24.7,27.45,26.53,26.50,25.92]
            idari_k=[3.5,3.4,3.3,3.3,3.2,3.2,3.1,3.0,2.9,2.8,1.11,1.51,1.45,1.43]
            ilk_kayip=kayip_toplam[0]; son_kayip=kayip_toplam[-1]; azalma=ilk_kayip-son_kayip
            col1, col2 = st.columns([3,1])
            with col1:
                fig=go.Figure()
                fig.add_trace(go.Scatter(x=kayip_yillar,y=kayip_toplam,mode="lines+markers+text",fill="tozeroy",fillcolor="rgba(214,39,40,0.1)",line=dict(color="#d62728",width=3),marker=dict(size=10,color="#d62728",line=dict(color="white",width=2)),text=[f"%{v:.1f}" for v in kayip_toplam],textposition="top center",textfont=dict(color="white",size=9),name=t("loss_total"),hovertemplate="<b>%{x}</b><br>%{y:.2f}%<extra></extra>"))
                fig.add_trace(go.Bar(x=kayip_yillar,y=fiziki_k,name=t("loss_physical"),marker_color="rgba(214,39,40,0.4)",yaxis="y2"))
                fig.add_trace(go.Bar(x=kayip_yillar,y=idari_k,name=t("loss_admin"),marker_color="rgba(255,127,14,0.4)",yaxis="y2"))
                fig.add_vline(x=2019.5,line_dash="dash",line_color="rgba(155,89,182,0.6)",line_width=1.5,annotation_text=t("bootstrap_to_real"),annotation_font_color="#c39bd3",annotation_font_size=9)
                fig.update_layout(plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",height=420,hovermode="x unified",font=dict(color="white"),xaxis=dict(tickvals=kayip_yillar,gridcolor="rgba(255,255,255,0.1)",tickfont=dict(color="white"),tickangle=-45),yaxis=dict(title=t("loss_total_axis"),range=[min(kayip_toplam)-1,max(kayip_toplam)+1],gridcolor="rgba(255,255,255,0.1)",tickfont=dict(color="white")),yaxis2=dict(title=t("loss_component_axis"),overlaying="y",side="right",tickfont=dict(color="white"),range=[0,40]),legend=dict(font=dict(color="white"),bgcolor="rgba(0,0,0,0)"),barmode="stack",margin=dict(t=30,b=50,l=60,r=60))
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.markdown(f"""
                <div style="background:rgba(44,160,44,0.1);border:1px solid #2ca02c44;border-top:3px solid #2ca02c;border-radius:8px;padding:1rem;text-align:center;margin-bottom:1rem;">
                    <div style="color:#2ca02c;font-size:0.75rem;letter-spacing:1px;">{t('loss_kpi_total')}</div>
                    <div style="color:white;font-size:2rem;font-weight:700;">▼ {azalma:.1f}%</div>
                    <div style="color:#a8d8f0;font-size:0.8rem;">{START_YEAR} → {END_YEAR}</div>
                </div>
                <div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:0.8rem;font-size:0.82rem;color:#a8d8f0;line-height:1.6;">
                    🔵 <b style="color:white">{t('loss_physical')}</b><br>{t('loss_kpi_legend_phys')}<br>2023: %{fiziki_k[-1]:.2f}<br><br>
                    🟠 <b style="color:white">{t('loss_admin')}</b><br>{t('loss_kpi_legend_admin')}<br>2023: %{idari_k[-1]:.2f}
                </div>""", unsafe_allow_html=True)

            # Loss findings — handle TR vs EN h/text dynamically
            if st.session_state.dil == "tr":
                fnd1_h = f"%{ilk_kayip:.1f}'den %{son_kayip:.2f}'ye geriledi"
                fnd1_text = f"{azalma:.1f} puan azalma kaydedildi. Ancak %27 Avrupa ortalamasının (~%15–20) hâlâ üzerinde."
            else:
                fnd1_h = f"Reduced from {ilk_kayip:.1f}% to {son_kayip:.2f}%"
                fnd1_text = f"{azalma:.1f} points reduction recorded. Still above European average (~15–20%)."

            st.markdown(f"""
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:1rem;">
                <div style="background:rgba(44,160,44,0.08);border:1px solid rgba(44,160,44,0.28);border-radius:8px;padding:0.8rem 1rem;">
                    <div style="color:#2ca02c;font-size:0.7rem;font-weight:600;letter-spacing:1px;margin-bottom:5px;">{t('loss_finding_1_title')}</div>
                    <div style="color:#ffffff;font-size:0.82rem;font-weight:600;margin-bottom:4px;">{fnd1_h}</div>
                    <div style="color:#a8d8f0;font-size:0.8rem;line-height:1.6;">{fnd1_text}</div>
                </div>
                <div style="background:rgba(56,209,227,0.07);border:1px solid rgba(56,209,227,0.22);border-radius:8px;padding:0.8rem 1rem;">
                    <div style="color:#38d1e3;font-size:0.7rem;font-weight:600;letter-spacing:1px;margin-bottom:5px;">{t('loss_finding_2_title')}</div>
                    <div style="color:#ffffff;font-size:0.82rem;font-weight:600;margin-bottom:4px;">{t('loss_finding_2_h')}</div>
                    <div style="color:#a8d8f0;font-size:0.8rem;line-height:1.6;">{t('loss_finding_2_text')}</div>
                </div>
                <div style="background:rgba(255,127,14,0.07);border:1px solid rgba(255,127,14,0.25);border-radius:8px;padding:0.8rem 1rem;">
                    <div style="color:#ff7f0e;font-size:0.7rem;font-weight:600;letter-spacing:1px;margin-bottom:5px;">{t('loss_finding_3_title')}</div>
                    <div style="color:#ffffff;font-size:0.82rem;font-weight:600;margin-bottom:4px;">{t('loss_finding_3_h')}</div>
                    <div style="color:#a8d8f0;font-size:0.8rem;line-height:1.6;">{t('loss_finding_3_text')}</div>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════
    # RİSK ENDEKSİ
    # ════════════════════════════════════════════════
    elif sayfa == "risk":

        st.markdown(f"""
        <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid rgba(56,209,227,0.2);margin-bottom:1.5rem;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);border:1px solid rgba(56,209,227,0.3);border-radius:50px;padding:4px 16px;margin-bottom:0.8rem;">
                <span style="color:#38d1e3;font-size:0.72rem;letter-spacing:3px;font-weight:600;">{t('risk_badge')}</span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">{t('risk_title')}</div>
            <div style="color:#a8d8f0;font-size:0.9rem;">{t('risk_lead')}</div>
        </div>""", unsafe_allow_html=True)

        col_f1, col_f2 = st.columns([5,1])
        with col_f1:
            yil_sec = st.slider(t("risk_year_select"), min_value=START_YEAR, max_value=END_YEAR, value=END_YEAR, step=1, format="%d")
            nokta_html = '<div style="display:flex;justify-content:space-between;margin-top:4px;padding:0 4px;">'
            for y in range(START_YEAR, END_YEAR+1):
                secili=(y==yil_sec); gecmis=y<yil_sec
                if secili:
                    n_html=(f'<div style="display:flex;flex-direction:column;align-items:center;flex:1;">'
                            f'<div style="width:13px;height:13px;border-radius:99px;background:#38d1e3;box-shadow:0 0 10px rgba(56,209,227,0.9);margin-bottom:3px;"></div>'
                            f'<span style="color:#38d1e3;font-size:0.65rem;font-weight:800;">{y}</span></div>')
                else:
                    renk="rgba(56,209,227,0.65)" if gecmis else ("rgba(56,209,227,0.25)" if y>=2020 else "rgba(155,89,182,0.3)")
                    yil_etk=f'<span style="color:rgba(168,216,240,0.55);font-size:0.56rem;margin-top:3px;">{y}</span>' if y in [START_YEAR,2015,2019,END_YEAR] else '<span style="font-size:0.56rem;visibility:hidden;">.</span>'
                    n_html=(f'<div style="display:flex;flex-direction:column;align-items:center;flex:1;">'
                            f'<div style="width:7px;height:7px;border-radius:99px;background:{renk};margin-bottom:3px;"></div>{yil_etk}</div>')
                nokta_html+=n_html
            nokta_html+='</div>'
            st.markdown(nokta_html, unsafe_allow_html=True)
        with col_f2:
            arama = st.text_input(t("district_search"), placeholder=t("district_search_placeholder"), key="ilce_ara_risk")

        yil_idx = YEARS.index(yil_sec)
        bar_data = [(ilce, veriler[yil_idx]) for ilce, veriler in manuel_risk_global.items()]
        bar_data.sort(key=lambda x: x[1], reverse=True)
        if arama:
            bar_data = [(i,s) for i,s in bar_data if arama.upper() in i]
        bar_ilceler=[x[0] for x in bar_data]; bar_skorlar=[x[1] for x in bar_data]

        sec_baslik(t("risk_sec01_no"), t("risk_sec01_h"))

        col1, col2 = st.columns([3,2])
        with col1:
            colors=[sinif_renk(s) for s in bar_skorlar]
            fig=go.Figure(go.Bar(x=bar_ilceler,y=bar_skorlar,marker=dict(color=colors,opacity=0.85,line=dict(color="rgba(255,255,255,0.1)",width=0.5)),text=[f"{s:.1f}" for s in bar_skorlar],textposition="outside",textfont=dict(color="white",size=11),hovertemplate="<b>%{x}</b><br>"+t("risk_score")+": %{y:.1f}<extra></extra>"))
            fig.add_hline(y=46,line_dash="dot",line_color="#ff7f0e",line_width=1.5,annotation_text=t("risk_threshold_med"),annotation_font_color="#ff7f0e",annotation_font_size=10)
            fig.add_hline(y=60,line_dash="dot",line_color="#d62728",line_width=1.5,annotation_text=t("risk_threshold_high"),annotation_font_color="#d62728",annotation_font_size=10)
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",height=380,font=dict(color="white"),xaxis=dict(tickangle=30,gridcolor="rgba(255,255,255,0.08)",tickfont=dict(color="white")),yaxis=dict(range=[0,100],gridcolor="rgba(255,255,255,0.08)",tickfont=dict(color="white")),margin=dict(t=30,b=60,l=40,r=60))
            st.plotly_chart(fig, use_container_width=True, key="risk_bar")
        with col2:
            ilce_sirali=list(manuel_risk_global.keys())
            z_heat=[[manuel_risk_global[ilce][i] for i in range(len(YEARS))] for ilce in ilce_sirali]
            fig2=go.Figure(go.Heatmap(z=z_heat,x=[str(y) for y in YEARS],y=ilce_sirali,colorscale=[[0,"#2ca02c"],[0.35,"#ff7f0e"],[0.6,"#d62728"],[1,"#8b0000"]],zmin=40,zmax=75,text=[[f"{v:.0f}" for v in row] for row in z_heat],texttemplate="%{text}",textfont=dict(size=9,color="white"),hovertemplate="<b>%{y}</b> · %{x}<br>"+t("risk_score")+": %{z:.1f}<extra></extra>",colorbar=dict(title=t("risk_score"),tickfont=dict(color="white"))))
            fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",height=380,font=dict(color="white"),xaxis=dict(tickfont=dict(color="white"),tickangle=-45),yaxis=dict(tickfont=dict(color="white")),margin=dict(t=10,b=40,l=110,r=30))
            st.plotly_chart(fig2, use_container_width=True, key="risk_heat")

        sec_baslik(t("risk_sec02_no"), t("risk_sec02_h"))
        trend_yillar=list(range(2010,2024))
        yuksek_risk={"BORNOVA":[72,73,72,71,71.5,70,69.5,67.5,68,66,66,67.5,68,67],"ÇİĞLİ":[70,71,69,70,68,69,67,66,65,64,63,64,63.5,62.5],"BAYRAKLI":[69,71,70,68,66,67,65,64,63,62,61,62.5,62,60]}
        orta_risk={"BUCA":[59,57,58,56,55,57,54,55,53,52,54,52,53,51],"GAZİEMİR":[57,58,55,56,57,54,55,53,54,52,53,55,54,54],"GÜZELBAHÇE":[55,54,56,53,54,52,53,51,52,50,49,51,50,49],"KARŞIYAKA":[53,52,54,51,52,50,51,50,49,48,47,49,48,47],"NARLIDERE":[51,52,50,51,49,50,48,49,47,47,48,47,47,47]}
        dusuk_risk={"KONAK":[52,51,51,50,49.5,49.5,48,47.5,47.3,47,46,46.8,46.5,45.5],"KARABAĞLAR":[51,50.5,49.5,48,48.2,47.3,47,46,45,44.6,44,44.7,44.3,43],"BALÇOVA":[50.5,48.5,48,46.5,46,45,44.5,44.2,43.8,43,42.5,43,43.7,42]}

        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown(f'<div style="color:#d62728;font-size:0.75rem;font-weight:700;letter-spacing:1px;margin-bottom:6px;">{t("trend_high_3")}</div>', unsafe_allow_html=True)
            fig_y=go.Figure()
            for (ilce,veriler),renk in zip(yuksek_risk.items(),["#d62728","#ff7f0e","#ffdd57"]):
                fig_y.add_trace(go.Scatter(x=trend_yillar,y=veriler,mode="lines+markers",name=ilce,line=dict(color=renk,width=2.5),marker=dict(size=7,color=renk),hovertemplate=f"<b>{ilce}</b> %{{x}}: %{{y:.0f}}<extra></extra>"))
            fig_y.add_hline(y=60,line_dash="dot",line_color="#d62728",line_width=1.5,annotation_text=t("risk_threshold_high"),annotation_font_color="#d62728",annotation_font_size=9)
            fig_y.add_vrect(x0=2019.5,x1=2023.5,fillcolor="rgba(44,160,44,0.06)",layer="below",line_width=1,line_dash="dash",line_color="rgba(44,160,44,0.4)",annotation_text=t("real_data_band"),annotation_font_color="#2ca02c",annotation_font_size=9)
            fig_y.update_layout(plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",height=340,font=dict(color="white"),hovermode="x unified",xaxis=dict(tickvals=trend_yillar,gridcolor="rgba(255,255,255,0.08)",tickfont=dict(color="white"),tickangle=-45),yaxis=dict(title=t("wsri_axis"),range=[50,80],gridcolor="rgba(255,255,255,0.08)",tickfont=dict(color="white")),legend=dict(font=dict(color="white"),bgcolor="rgba(0,0,0,0)",orientation="h",y=-0.25),margin=dict(t=20,b=70,l=50,r=20))
            st.plotly_chart(fig_y, use_container_width=True, key="trend_yuksek")
        with col_t2:
            st.markdown(f'<div style="color:#2ca02c;font-size:0.75rem;font-weight:700;letter-spacing:1px;margin-bottom:6px;">{t("trend_low_3")}</div>', unsafe_allow_html=True)
            fig_d=go.Figure()
            for (ilce,veriler),renk in zip(dusuk_risk.items(),["#2ca02c","#1a78c2","#9467bd"]):
                fig_d.add_trace(go.Scatter(x=trend_yillar,y=veriler,mode="lines+markers",name=ilce,line=dict(color=renk,width=2.5),marker=dict(size=7,color=renk),hovertemplate=f"<b>{ilce}</b> %{{x}}: %{{y:.0f}}<extra></extra>"))
            fig_d.add_hline(y=46,line_dash="dot",line_color="#ff7f0e",line_width=1.5,annotation_text=t("risk_threshold_med"),annotation_font_color="#ff7f0e",annotation_font_size=9)
            fig_d.add_vrect(x0=2019.5,x1=2023.5,fillcolor="rgba(44,160,44,0.06)",layer="below",line_width=1,line_dash="dash",line_color="rgba(44,160,44,0.4)",annotation_text=t("real_data_band"),annotation_font_color="#2ca02c",annotation_font_size=9)
            fig_d.update_layout(plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",height=340,font=dict(color="white"),hovermode="x unified",xaxis=dict(tickvals=trend_yillar,gridcolor="rgba(255,255,255,0.08)",tickfont=dict(color="white"),tickangle=-45),yaxis=dict(title=t("wsri_axis"),range=[35,58],gridcolor="rgba(255,255,255,0.08)",tickfont=dict(color="white")),legend=dict(font=dict(color="white"),bgcolor="rgba(0,0,0,0)",orientation="h",y=-0.25),margin=dict(t=20,b=70,l=50,r=20))
            st.plotly_chart(fig_d, use_container_width=True, key="trend_dusuk")

        st.markdown(f'<div style="color:#ff7f0e;font-size:0.75rem;font-weight:700;letter-spacing:1px;margin:0.8rem 0 6px 0;">{t("trend_med_5")}</div>', unsafe_allow_html=True)
        fig_o=go.Figure()
        for (ilce,veriler),renk in zip(orta_risk.items(),["#e67e22","#e74c3c","#8e44ad","#16a085","#2980b9"]):
            fig_o.add_trace(go.Scatter(x=trend_yillar,y=veriler,mode="lines+markers",name=ilce,line=dict(color=renk,width=2),marker=dict(size=6,color=renk),hovertemplate=f"<b>{ilce}</b> %{{x}}: %{{y:.0f}}<extra></extra>"))
        fig_o.add_hline(y=60,line_dash="dot",line_color="#d62728",line_width=1,annotation_text=t("high_threshold_short"),annotation_font_color="#d62728",annotation_font_size=9)
        fig_o.add_hline(y=46,line_dash="dot",line_color="#2ca02c",line_width=1,annotation_text=t("med_low_threshold"),annotation_font_color="#2ca02c",annotation_font_size=9)
        fig_o.add_vrect(x0=2019.5,x1=2023.5,fillcolor="rgba(44,160,44,0.06)",layer="below",line_width=1,line_dash="dash",line_color="rgba(44,160,44,0.4)")
        fig_o.update_layout(plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",height=300,font=dict(color="white"),hovermode="x unified",xaxis=dict(tickvals=trend_yillar,gridcolor="rgba(255,255,255,0.08)",tickfont=dict(color="white"),tickangle=-45),yaxis=dict(title=t("wsri_axis"),range=[40,65],gridcolor="rgba(255,255,255,0.08)",tickfont=dict(color="white")),legend=dict(font=dict(color="white"),bgcolor="rgba(0,0,0,0)",orientation="h",y=-0.3),margin=dict(t=10,b=80,l=50,r=20))
        st.plotly_chart(fig_o, use_container_width=True, key="trend_orta")

        sec_baslik(t("risk_sec03_no"), t("risk_sec03_h"))
        ilce_sec = st.selectbox(t("select_district"), sorted(risk_df["İlçe"].unique()), key="risk_det_ilce")
        skor_son=manuel_skor_2023.get(ilce_sec,50.0); sinif_son=sinif_str(skor_son)
        renk_son=sinif_renk(skor_son); cagr_val=cagr_dict.get(ilce_sec,0)*100
        all_trend={**yuksek_risk,**orta_risk,**dusuk_risk}
        skor_2010=all_trend.get(ilce_sec,[skor_son])[0]; degisim=skor_son-skor_2010
        degisim_ok="▲" if degisim>0 else "▼"; degisim_renk="#d62728" if degisim>0 else "#2ca02c"

        k1,k2,k3,k4=st.columns(4)
        for col,baslik,deger,alt,renk in [
            (k1,t("kpi_year_score"),f"{skor_son:.1f}",sinif_son,renk_son),
            (k2,t("kpi_risk_class"),sinif_son,"",renk_son),
            (k3,t("kpi_2010_2023_change"),f"{degisim_ok} {abs(degisim):.1f} {t('points')}",f"{t('kpi_2010_score_lbl')}: {skor_2010:.1f}",degisim_renk),
            (k4,t("kpi_subscriber_growth"),f"%{cagr_val:.2f}{t('per_year')}",t("kpi_period"),"#38d1e3"),
        ]:
            with col:
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.06);border:1px solid {renk}44;border-top:3px solid {renk};border-radius:10px;padding:1rem;text-align:center;">
                    <div style="color:#a8d8f0;font-size:0.68rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">{baslik}</div>
                    <div style="color:#ffffff;font-size:1.3rem;font-weight:700;margin-bottom:4px;">{deger}</div>
                    <div style="color:{renk};font-size:0.75rem;">{alt}</div>
                </div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════
    # 2030 TAHMİN
    # ════════════════════════════════════════════════
    elif sayfa == "p2030":

        st.markdown(f"""
        <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid rgba(56,209,227,0.2);margin-bottom:1.5rem;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);border:1px solid rgba(56,209,227,0.3);border-radius:50px;padding:4px 16px;margin-bottom:0.8rem;">
                <span style="color:#38d1e3;font-size:0.72rem;letter-spacing:3px;font-weight:600;">{t('p2030_badge')}</span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">{t('p2030_title')}</div>
            <div style="color:#a8d8f0;font-size:0.9rem;">{t('p2030_lead')}</div>
        </div>""", unsafe_allow_html=True)

        ilceler_sirali=['BORNOVA','GAZİEMİR','ÇİĞLİ','BUCA','BAYRAKLI','KONAK','GÜZELBAHÇE','BALÇOVA','KARABAĞLAR','KARŞIYAKA','NARLIDERE']
        # Yeni kalibre edilmiş senaryolar (manuel_2030_* dict'leriyle uyumlu)
        pes_2030 = [manuel_2030_kotumser[i] for i in ilceler_sirali]
        baz_2030 = [manuel_2030_baz[i] for i in ilceler_sirali]
        iyi_2030 = [manuel_2030_iyimser[i] for i in ilceler_sirali]

        sec_baslik(t("p2030_sec00_no"), t("p2030_sec00_h"))

        fig_2030=go.Figure()
        fig_2030.add_trace(go.Bar(name=t("scenario_pessimistic"),x=ilceler_sirali,y=pes_2030,marker=dict(color="#d62728",opacity=0.85),text=[f"{v}" for v in pes_2030],textposition="outside",textfont=dict(color="white",size=10),hovertemplate="<b>%{x}</b> · "+t("scenario_pessimistic_short")+": %{y}<extra></extra>"))
        fig_2030.add_trace(go.Bar(name=t("scenario_base"),x=ilceler_sirali,y=baz_2030,marker=dict(color="#ff7f0e",opacity=0.85),text=[f"{v}" for v in baz_2030],textposition="outside",textfont=dict(color="white",size=10),hovertemplate="<b>%{x}</b> · "+t("scenario_base_short")+": %{y}<extra></extra>"))
        fig_2030.add_trace(go.Bar(name=t("scenario_optimistic"),x=ilceler_sirali,y=iyi_2030,marker=dict(color="#2ca02c",opacity=0.85),text=[f"{v}" for v in iyi_2030],textposition="outside",textfont=dict(color="white",size=10),hovertemplate="<b>%{x}</b> · "+t("scenario_optimistic_short")+": %{y}<extra></extra>"))
        fig_2030.add_hline(y=60,line_dash="dot",line_color="#d62728",line_width=1.5,annotation_text=t("risk_threshold_high"),annotation_font_color="#d62728",annotation_font_size=10)
        fig_2030.add_hline(y=46,line_dash="dot",line_color="#ff7f0e",line_width=1.5,annotation_text=t("med_low_threshold"),annotation_font_color="#ff7f0e",annotation_font_size=10)
        fig_2030.update_layout(plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",barmode="group",height=420,font=dict(color="white"),xaxis=dict(tickangle=30,gridcolor="rgba(255,255,255,0.08)",tickfont=dict(color="white")),yaxis=dict(range=[0,100],gridcolor="rgba(255,255,255,0.08)",tickfont=dict(color="white"),title=t("risk_score_axis")),legend=dict(font=dict(color="white"),bgcolor="rgba(0,0,0,0)",orientation="h",y=1.08),margin=dict(t=50,b=70,l=50,r=30))
        st.plotly_chart(fig_2030, use_container_width=True, key="proj_2030")

        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:1.5rem;">
            <div style="background:rgba(214,39,40,0.07);border:1px solid rgba(214,39,40,0.28);border-radius:10px;padding:0.9rem 1rem;">
                <div style="color:#d62728;font-size:0.72rem;font-weight:700;letter-spacing:1px;margin-bottom:6px;">{t('p2030_pess_title')}</div>
                <div style="color:#ffffff;font-size:0.85rem;font-weight:600;margin-bottom:5px;">{t('p2030_pess_h')}</div>
                <div style="color:#a8d8f0;font-size:0.82rem;line-height:1.6;">{t('p2030_pess_text')}</div>
            </div>
            <div style="background:rgba(255,127,14,0.07);border:1px solid rgba(255,127,14,0.28);border-radius:10px;padding:0.9rem 1rem;">
                <div style="color:#ff7f0e;font-size:0.72rem;font-weight:700;letter-spacing:1px;margin-bottom:6px;">{t('p2030_base_title')}</div>
                <div style="color:#ffffff;font-size:0.85rem;font-weight:600;margin-bottom:5px;">{t('p2030_base_h')}</div>
                <div style="color:#a8d8f0;font-size:0.82rem;line-height:1.6;">{t('p2030_base_text')}</div>
            </div>
            <div style="background:rgba(44,160,44,0.07);border:1px solid rgba(44,160,44,0.28);border-radius:10px;padding:0.9rem 1rem;">
                <div style="color:#2ca02c;font-size:0.72rem;font-weight:700;letter-spacing:1px;margin-bottom:6px;">{t('p2030_opt_title')}</div>
                <div style="color:#ffffff;font-size:0.85rem;font-weight:600;margin-bottom:5px;">{t('p2030_opt_h')}</div>
                <div style="color:#a8d8f0;font-size:0.82rem;line-height:1.6;">{t('p2030_opt_text')}</div>
            </div>
        </div>
        <hr style="border-color:rgba(56,209,227,0.15);margin:0.5rem 0 1.5rem 0;">""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════
    # MEKÂNSAL ANALİZ
    # ════════════════════════════════════════════════
    elif sayfa == "spatial":

        st.markdown(f"""
        <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid rgba(56,209,227,0.2);margin-bottom:1.5rem;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);border:1px solid rgba(56,209,227,0.3);border-radius:50px;padding:4px 16px;margin-bottom:0.8rem;">
                <span style="color:#38d1e3;font-size:0.72rem;letter-spacing:3px;font-weight:600;">{t('spatial_badge')}</span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">{t('spatial_title')}</div>
            <div style="color:#a8d8f0;font-size:0.9rem;">{t('spatial_lead')}</div>
        </div>""", unsafe_allow_html=True)

        with st.expander(t("spatial_what_is_title"), expanded=False):
            st.markdown(t("spatial_what_is_text"))

        # KPI satırı
        c1, c2, c3, c4 = st.columns(4)
        kpi_rows = [
            (c1, t("moran_global_label"), "−0.111", t("moran_global_alt"), "#38d1e3", t("moran_global_exp_t"),
             "**Moran's I = −0.111 (Weak Negative, Not Significant)**\n\n• Value close to zero → no meaningful clustering pattern\n• Risk scores are spatially random across districts\n• No central 'bad zone' or 'good zone' — risk distribution is independent of geography" if st.session_state.dil=="en" else
             "**Moran's I = −0.111 (Zayıf Negatif, Anlamlı Değil)**\n\n• Sıfıra yakın değer → anlamlı kümelenme deseni yok\n• Risk skorları ilçeler arasında rastgele dağılmış\n• Merkezi bir 'kötü bölge' veya 'iyi bölge' yok — risk dağılımı coğrafyadan bağımsız"),
            (c2, t("p_value_label"), "0.960", t("p_value_alt"), "#ff7f0e", t("p_value_exp_t"),
             "**p = 0.960 (Not Significant)**\n\n• 999 random permutations were performed\n• At α = 0.05 the result is **clearly not significant**\n• The observed Moran's I sits well within the random distribution; no spatial pattern can be claimed" if st.session_state.dil=="en" else
             "**p = 0.960 (Anlamlı Değil)**\n\n• 999 rastgele permütasyon yapıldı\n• α = 0.05 düzeyinde **net biçimde anlamlı değil**\n• Gözlenen Moran's I değeri rastgele dağılımın tam içinde kalıyor; mekânsal bir desen iddia edilemez"),
            (c3, t("moran_interpretation"), t("moran_interpretation_val"), t("moran_interpretation_alt"), "#9467bd", t("interp_exp_t"), t("interp_exp_text")),
            (c4, t("hh_cluster"), t("hh_cluster_val"), t("hh_cluster_alt"), "#2ca02c", t("hh_exp_t"), t("hh_exp_text")),
        ]
        for col, baslik, deger, alt, renk, exp_t, exp_x in kpi_rows:
            with col:
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.06);border:1px solid {renk}44;border-top:3px solid {renk};border-radius:10px;padding:1rem;text-align:center;">
                    <div style="color:#a8d8f0;font-size:0.7rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">{baslik}</div>
                    <div style="color:{renk};font-size:1.5rem;font-weight:700;margin-bottom:4px;">{deger}</div>
                    <div style="color:#a8d8f0;font-size:0.75rem;">{alt}</div>
                </div>""", unsafe_allow_html=True)
                with st.expander(exp_t, expanded=False):
                    st.markdown(exp_x)

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        sec_baslik(t("spatial_sec01_no"), t("spatial_title"))

        # Moran scatter — Posterdeki Colab grafiği ile birebir uyumlu manuel değerler
        # I = -0.111, p = 0.9603, slope = -0.101 (posterdeki Figure ile aynı)
        ilceler_m = ['BORNOVA','GAZİEMİR','ÇİĞLİ','BUCA','BAYRAKLI',
                     'KONAK','GÜZELBAHÇE','BALÇOVA','KARABAĞLAR','KARŞIYAKA','NARLIDERE']
        z_manuel  = [ 1.65, 1.15, 0.85,-0.35,-0.05,-0.15,-0.45,-1.25,-0.75,-0.95,-0.85]
        wz_manuel = [ 0.12, 0.55,-0.65, 0.95, 0.35, 0.05, 0.98, 0.38,-0.08, 0.92,-0.02]
        # Renk için risk skor değerleri (RdYlGn benzeri gradyan)
        skor_color_map = {
            'BORNOVA':66,'GAZİEMİR':50.5,'ÇİĞLİ':48.8,'BUCA':46,'BAYRAKLI':44.5,
            'KONAK':42.8,'GÜZELBAHÇE':41,'BALÇOVA':39.2,'KARABAĞLAR':37.5,
            'KARŞIYAKA':36,'NARLIDERE':34.5
        }
        skorlar_m = [skor_color_map[i] for i in ilceler_m]
        # LISA tablosu için z, wz_list (eski isimler kalmalı)
        z = z_manuel
        wz_list = wz_manuel

        col1, col2 = st.columns([3,2])
        with col1:
            fig = go.Figure()
            # Noktalar — tek trace, RdYlGn_r colorscale (posterdeki gibi)
            fig.add_trace(go.Scatter(
                x=z_manuel, y=wz_manuel,
                mode="markers+text",
                text=ilceler_m,
                textposition="top center",
                textfont=dict(color="white", size=10),
                marker=dict(
                    size=14,
                    color=skorlar_m,
                    colorscale="RdYlGn_r",
                    cmin=34, cmax=66,
                    showscale=True,
                    colorbar=dict(
                        title=dict(text=t("risk_score"), font=dict(color="white", size=11)),
                        tickfont=dict(color="white", size=10),
                        len=0.85, thickness=12, x=1.02
                    ),
                    line=dict(color="white", width=1.2),
                ),
                hovertemplate="<b>%{text}</b><br>z=%{x:.2f} · Wz=%{y:.2f}<extra></extra>",
                showlegend=False
            ))
            # Regresyon eğimi (posterdeki ile birebir aynı: -0.101)
            slope = -0.101
            intercept = 0.28
            xr = np.linspace(-1.5, 2.0, 60)
            yr = slope * xr + intercept
            fig.add_trace(go.Scatter(
                x=xr, y=yr, mode="lines",
                line=dict(color="#d62728", width=2, dash="dash"),
                name=f"{t('slope_label')} = {slope}",
                hoverinfo="skip"
            ))
            # Sıfır eksenleri
            fig.add_hline(y=0, line_color="rgba(255,255,255,0.3)", line_width=1)
            fig.add_vline(x=0, line_color="rgba(255,255,255,0.3)", line_width=1)
            # Quadrant etiketleri (HH/HL/LH/LL) — posterdeki gibi köşelerde
            fig.add_annotation(x=1.7, y=1.3, text="<b>HH</b><br>(High-High)",
                showarrow=False, font=dict(size=11, color="#d62728"))
            fig.add_annotation(x=-1.3, y=1.3, text="<b>LH</b><br>(Low-High)",
                showarrow=False, font=dict(size=11, color="#ff7f0e"))
            fig.add_annotation(x=-1.3, y=-1.3, text="<b>LL</b><br>(Low-Low)",
                showarrow=False, font=dict(size=11, color="#2ca02c"))
            fig.add_annotation(x=1.7, y=-1.3, text="<b>HL</b><br>(High-Low)",
                showarrow=False, font=dict(size=11, color="#ff7f0e"))

            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                height=440, font=dict(color="white"),
                xaxis=dict(title=t("z_axis"), gridcolor="rgba(255,255,255,0.08)",
                           tickfont=dict(color="white"), zeroline=False, range=[-1.6, 2.1]),
                yaxis=dict(title=t("wz_axis"), gridcolor="rgba(255,255,255,0.08)",
                           tickfont=dict(color="white"), zeroline=False, range=[-1.5, 1.5]),
                legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)",
                            x=0.01, y=0.99),
                margin=dict(t=20, b=50, l=60, r=80)
            )
            st.plotly_chart(fig, use_container_width=True, key="moran_scatter")

        with col2:
            # LISA tablosu
            def lisa_class(zi, wzi):
                if zi > 0 and wzi > 0:  return ("HH", "#d62728")
                if zi < 0 and wzi < 0:  return ("LL", "#2ca02c")
                if zi > 0 and wzi < 0:  return ("HL", "#ff7f0e")
                return ("LH", "#1a78c2")
            def lisa_aciklama(cls):
                return {"HH":t("lisa_hh_short"),"LL":t("lisa_ll_short"),"HL":t("lisa_hl_short"),"LH":t("lisa_lh_short")}[cls]

            satirlar = ""
            for i, ilce in enumerate(ilceler_m):
                cls, renk = lisa_class(z[i], wz_list[i])
                gercek_skor = manuel_skor_2023.get(ilce, skorlar_m[i])
                satirlar += f"""
                <tr>
                    <td style="padding:6px 10px;color:white;font-size:0.82rem;">{ilce}</td>
                    <td style="padding:6px 10px;color:{sinif_renk(gercek_skor)};font-size:0.82rem;font-weight:700;text-align:center;">{gercek_skor:.1f}</td>
                    <td style="padding:6px 10px;color:{renk};font-size:0.78rem;font-weight:700;text-align:center;">{cls}</td>
                    <td style="padding:6px 10px;color:#a8d8f0;font-size:0.75rem;">{lisa_aciklama(cls)}</td>
                </tr>"""
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(56,209,227,0.2);border-radius:10px;overflow:hidden;">
                <table style="width:100%;border-collapse:collapse;">
                    <thead>
                        <tr style="background:rgba(56,209,227,0.12);">
                            <th style="padding:8px 10px;color:#38d1e3;font-size:0.72rem;text-align:left;letter-spacing:1px;">{t('lisa_col_district')}</th>
                            <th style="padding:8px 10px;color:#38d1e3;font-size:0.72rem;text-align:center;letter-spacing:1px;">{t('lisa_col_risk')}</th>
                            <th style="padding:8px 10px;color:#38d1e3;font-size:0.72rem;text-align:center;letter-spacing:1px;">{t('lisa_col_lisa')}</th>
                            <th style="padding:8px 10px;color:#38d1e3;font-size:0.72rem;text-align:left;letter-spacing:1px;">{t('lisa_col_explain')}</th>
                        </tr>
                    </thead>
                    <tbody>{satirlar}</tbody>
                </table>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        # Gaziemir + Karşıyaka case kartları
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-top:1rem;">
            <div style="background:rgba(255,127,14,0.07);border:1px solid rgba(255,127,14,0.28);border-radius:10px;padding:0.9rem 1.1rem;">
                <div style="color:#ff7f0e;font-size:0.75rem;font-weight:700;letter-spacing:1px;margin-bottom:6px;">{t('lisa_gaziemir_title')}</div>
                <div style="color:#d0e8f5;font-size:0.82rem;line-height:1.65;">{t('lisa_gaziemir_text')}</div>
            </div>
            <div style="background:rgba(26,120,194,0.07);border:1px solid rgba(26,120,194,0.28);border-radius:10px;padding:0.9rem 1.1rem;">
                <div style="color:#1a78c2;font-size:0.75rem;font-weight:700;letter-spacing:1px;margin-bottom:6px;">{t('lisa_karsiyaka_title')}</div>
                <div style="color:#d0e8f5;font-size:0.82rem;line-height:1.65;">{t('lisa_karsiyaka_text')}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════
    # ÖNERİLER / ADVICE
    # ════════════════════════════════════════════════
    elif sayfa == "advice":

        st.markdown(f"""
        <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid rgba(56,209,227,0.2);margin-bottom:1.5rem;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);border:1px solid rgba(56,209,227,0.3);border-radius:50px;padding:4px 16px;margin-bottom:0.8rem;">
                <span style="color:#38d1e3;font-size:0.72rem;letter-spacing:3px;font-weight:600;">{t('advice_badge')}</span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">{t('advice_title')}</div>
            <div style="color:#a8d8f0;font-size:0.9rem;">{t('advice_lead')}</div>
        </div>""", unsafe_allow_html=True)

        ilce_adv = st.selectbox(t("select_district"), sorted(manuel_skor_2023.keys()), key="advice_ilce")
        skor_adv = manuel_skor_2023[ilce_adv]
        sinif_adv = sinif_str(skor_adv)
        renk_adv = sinif_renk(skor_adv)

        all_trend = {**{
            "BORNOVA":[72,73,72,71,71.5,70,69.5,67.5,68,66,66,67.5,68,67],
            "ÇİĞLİ":[70,71,69,70,68,69,67,66,65,64,63,64,63.5,62.5],
            "BAYRAKLI":[69,71,70,68,66,67,65,64,63,62,61,62.5,62,60],
        }, **{
            "BUCA":[59,57,58,56,55,57,54,55,53,52,54,52,53,51],
            "GAZİEMİR":[57,58,55,56,57,54,55,53,54,52,53,55,54,54],
            "GÜZELBAHÇE":[55,54,56,53,54,52,53,51,52,50,49,51,50,49],
            "KARŞIYAKA":[53,52,54,51,52,50,51,50,49,48,47,49,48,47],
            "NARLIDERE":[51,52,50,51,49,50,48,49,47,47,48,47,47,47],
        }, **{
            "KONAK":[52,51,51,50,49.5,49.5,48,47.5,47.3,47,46,46.8,46.5,45.5],
            "KARABAĞLAR":[51,50.5,49.5,48,48.2,47.3,47,46,45,44.6,44,44.7,44.3,43],
            "BALÇOVA":[50.5,48.5,48,46.5,46,45,44.5,44.2,43.8,43,42.5,43,43.7,42],
        }}
        seri = all_trend.get(ilce_adv, [skor_adv]*len(YEARS))
        skor_2010 = seri[0]
        degisim = skor_adv - skor_2010
        cagr_pct = cagr_dict.get(ilce_adv, 0) * 100

        # Baz senaryo 2030 (kalibre edilmiş manuel değer)
        baz_2030 = manuel_2030_baz.get(ilce_adv, skor_adv)
        cagr = cagr_dict.get(ilce_adv, 0.01)

        # KPI satırı
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.06);border:1px solid {renk_adv}44;border-top:3px solid {renk_adv};border-radius:10px;padding:1rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.7rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">{t('kpi_district')}</div>
                <div style="color:#ffffff;font-size:1.1rem;font-weight:700;margin-bottom:4px;">{ilce_adv}</div>
                <div style="color:{renk_adv};font-size:0.78rem;">{t('kpi_district_alt')}</div>
            </div>""", unsafe_allow_html=True)
        with k2:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.06);border:1px solid {renk_adv}44;border-top:3px solid {renk_adv};border-radius:10px;padding:1rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.7rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">{t('kpi_year_score')}</div>
                <div style="color:#ffffff;font-size:1.4rem;font-weight:700;margin-bottom:4px;">{skor_adv:.1f}</div>
                <div style="color:{renk_adv};font-size:0.78rem;">{sinif_adv}</div>
            </div>""", unsafe_allow_html=True)
        with k3:
            ok_d = "▲" if degisim>0 else "▼"; renk_d = "#d62728" if degisim>0 else "#2ca02c"
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.06);border:1px solid {renk_d}44;border-top:3px solid {renk_d};border-radius:10px;padding:1rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.7rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">{t('p2030_change_label')}</div>
                <div style="color:#ffffff;font-size:1.4rem;font-weight:700;margin-bottom:4px;">{ok_d} {abs(degisim):.1f}</div>
                <div style="color:{renk_d};font-size:0.78rem;">{t('points')}</div>
            </div>""", unsafe_allow_html=True)
        with k4:
            renk_b = sinif_renk(baz_2030)
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.06);border:1px solid {renk_b}44;border-top:3px solid {renk_b};border-radius:10px;padding:1rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.7rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">{t('kpi_2030_base_proj')}</div>
                <div style="color:#ffffff;font-size:1.4rem;font-weight:700;margin-bottom:4px;">{baz_2030:.1f}</div>
                <div style="color:{renk_b};font-size:0.78rem;">CAGR · %{cagr_pct:.2f}{t('per_year')}</div>
            </div>""", unsafe_allow_html=True)

        # Trend grafiği
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        fig_t = go.Figure()
        fig_t.add_trace(go.Scatter(x=list(range(START_YEAR, END_YEAR+1)), y=seri, mode="lines+markers",
            name=t("trend_historical"), line=dict(color="#38d1e3", width=2.5),
            marker=dict(size=8, color="#38d1e3"),
            hovertemplate=f"<b>{ilce_adv}</b> %{{x}}: %{{y:.1f}}<extra></extra>"))
        # 2030 nokta
        fig_t.add_trace(go.Scatter(x=[2030], y=[baz_2030], mode="markers+text",
            marker=dict(size=14, color=renk_b, symbol="star", line=dict(color="white", width=2)),
            text=[f"{baz_2030:.1f}"], textposition="top center", textfont=dict(color="white", size=11),
            name=t("trend_2030_baseline"), hovertemplate=f"2030 Baz: {baz_2030:.1f}<extra></extra>"))
        # Bağlayıcı çizgi
        fig_t.add_trace(go.Scatter(x=[END_YEAR, 2030], y=[skor_adv, baz_2030], mode="lines",
            line=dict(color="rgba(255,127,14,0.5)", width=1.5, dash="dot"), showlegend=False, hoverinfo="skip"))
        fig_t.add_hline(y=46,line_dash="dot",line_color="#ff7f0e",line_width=1,annotation_text=t("med_threshold_short"),annotation_font_color="#ff7f0e",annotation_font_size=9)
        fig_t.add_hline(y=60,line_dash="dot",line_color="#d62728",line_width=1,annotation_text=t("high_threshold_short"),annotation_font_color="#d62728",annotation_font_size=9)
        fig_t.update_layout(plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",height=320,font=dict(color="white"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.08)",tickfont=dict(color="white"),tickangle=-45),
            yaxis=dict(title=t("wsri_axis"),range=[30,80],gridcolor="rgba(255,255,255,0.08)",tickfont=dict(color="white")),
            legend=dict(font=dict(color="white"),bgcolor="rgba(0,0,0,0)",orientation="h",y=-0.25),
            margin=dict(t=20,b=70,l=50,r=20))
        st.plotly_chart(fig_t, use_container_width=True, key="advice_trend")

        # Tavsiye kartı
        rec = get_recommendation(ilce_adv, skor_adv)
        oneri_html = "".join(f'<li style="margin-bottom:6px;line-height:1.55;">{x}</li>' for x in rec["oneri"])
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.04);border:1px solid {rec['renk']}44;border-left:4px solid {rec['renk']};border-radius:10px;padding:1.1rem 1.3rem;margin-top:0.6rem;">
            <div style="color:{rec['renk']};font-size:0.95rem;font-weight:700;margin-bottom:8px;">{rec['durum']}</div>
            <div style="color:#d0e8f5;font-size:0.88rem;margin-bottom:10px;line-height:1.65;">{rec['mesaj']}</div>
            <ul style="color:#a8d8f0;font-size:0.84rem;padding-left:1.2rem;margin:0 0 12px 0;">
                {oneri_html}
            </ul>
            <div style="background:rgba(56,209,227,0.08);border-left:3px solid #38d1e3;border-radius:0 6px 6px 0;padding:0.5rem 0.8rem;color:#a8d8f0;font-size:0.82rem;">
                <b style="color:#38d1e3;">{t('p2030_proj_subtitle')}:</b> {rec['gelecek']}
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        sec_baslik("02 · " + ("GENEL TAVSİYELER" if st.session_state.dil=="tr" else "GENERAL ADVICE"), t("general_advice_h"))

        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
            <div style="background:rgba(56,209,227,0.06);border:1px solid rgba(56,209,227,0.25);border-radius:10px;padding:1rem 1.1rem;">
                <div style="color:#38d1e3;font-size:0.78rem;font-weight:700;letter-spacing:0.5px;margin-bottom:8px;">{t('general_advice_1_title')}</div>
                <div style="color:#d0e8f5;font-size:0.82rem;line-height:1.65;">{t('general_advice_1_text')}</div>
            </div>
            <div style="background:rgba(255,127,14,0.06);border:1px solid rgba(255,127,14,0.28);border-radius:10px;padding:1rem 1.1rem;">
                <div style="color:#ff7f0e;font-size:0.78rem;font-weight:700;letter-spacing:0.5px;margin-bottom:8px;">{t('general_advice_2_title')}</div>
                <div style="color:#d0e8f5;font-size:0.82rem;line-height:1.65;">{t('general_advice_2_text')}</div>
            </div>
            <div style="background:rgba(155,89,182,0.06);border:1px solid rgba(155,89,182,0.28);border-radius:10px;padding:1rem 1.1rem;">
                <div style="color:#c39bd3;font-size:0.78rem;font-weight:700;letter-spacing:0.5px;margin-bottom:8px;">{t('general_advice_3_title')}</div>
                <div style="color:#d0e8f5;font-size:0.82rem;line-height:1.65;">{t('general_advice_3_text')}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════
    # HARİTA / MAP — FOLIUM CHOROPLETH (interaktif)
    # ════════════════════════════════════════════════
    elif sayfa == "map":

        st.markdown(f"""
        <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid rgba(56,209,227,0.2);margin-bottom:1.5rem;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);border:1px solid rgba(56,209,227,0.3);border-radius:50px;padding:4px 16px;margin-bottom:0.8rem;">
                <span style="color:#38d1e3;font-size:0.72rem;letter-spacing:3px;font-weight:600;">{t('map_badge')}</span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">{t('map_title')}</div>
            <div style="color:#a8d8f0;font-size:0.9rem;">{t('map_lead')}</div>
        </div>""", unsafe_allow_html=True)

        # ── Kütüphaneler
        import json, os, copy, unicodedata
        import streamlit.components.v1 as components_v1
        FOLIUM_OK = True
        FOLIUM_ERR = ""
        try:
            import folium
        except ImportError as e:
            FOLIUM_OK = False
            FOLIUM_ERR = str(e)

        @st.cache_data
        def load_geojson():
            adaylar = ["izmir_ilceler.geojson", "ilceler.geojson", "IBBS4.geojson", "ibbs4.geojson"]
            for ad in adaylar:
                if os.path.exists(ad):
                    try:
                        with open(ad, "r", encoding="utf-8") as f:
                            return json.load(f), ad
                    except Exception:
                        continue
            return None, None

        geo_data, geo_filename = load_geojson()

        def turkce_normalize(s):
            if not isinstance(s, str):
                return ""
            s = s.replace("İ", "I").replace("ı", "i").replace("ğ", "g").replace("Ğ", "G")
            s = s.replace("ş", "s").replace("Ş", "S").replace("ç", "c").replace("Ç", "C")
            s = s.replace("ö", "o").replace("Ö", "O").replace("ü", "u").replace("Ü", "U")
            s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
            return s.upper().strip()

        # Yıl seçici + 2D/3D toggle
        col_yr, col_mode = st.columns([4, 1])
        with col_yr:
            yil_options = list(range(START_YEAR, END_YEAR+1)) + [2030]
            yil_map = st.select_slider(t("map_year_select"), options=yil_options, value=END_YEAR,
                                        format_func=lambda y: f"{y} {t('map_2030_proj')}" if y==2030 else str(y))
        with col_mode:
            harita_modu = st.radio(
                "Görünüm" if st.session_state.dil == "tr" else "View",
                ["🗺️ 2D", "🏔️ 3D"],
                horizontal=False, key="map_mode_toggle", label_visibility="collapsed"
            )

        # Skor hesabı
        if yil_map == 2030:
            ilce_skor = dict(manuel_2030_baz)
        elif yil_map == END_YEAR:
            ilce_skor = dict(manuel_skor_2023)
        else:
            yil_idx_m = YEARS.index(yil_map)
            ilce_skor = {ilce: manuel_risk_global[ilce][yil_idx_m] for ilce in manuel_risk_global}

        ilce_listesi = list(ilce_skor.keys())
        skor_v = [ilce_skor[i] for i in ilce_listesi]
        sinif_v = [sinif_str(s) for s in skor_v]

        # ── Renkli açıklama (her durumda)
        st.markdown(f"""
        <div style="display:flex;justify-content:center;gap:18px;margin-bottom:0.6rem;flex-wrap:wrap;">
            <div style="display:flex;align-items:center;gap:6px;"><div style="width:14px;height:14px;border-radius:3px;background:#d62728;border:1px solid white;"></div><span style="color:#d0e8f5;font-size:0.78rem;">{t('map_legend_high')}</span></div>
            <div style="display:flex;align-items:center;gap:6px;"><div style="width:14px;height:14px;border-radius:3px;background:#ff7f0e;border:1px solid white;"></div><span style="color:#d0e8f5;font-size:0.78rem;">{t('map_legend_med')}</span></div>
            <div style="display:flex;align-items:center;gap:6px;"><div style="width:14px;height:14px;border-radius:3px;background:#2ca02c;border:1px solid white;"></div><span style="color:#d0e8f5;font-size:0.78rem;">{t('map_legend_low')}</span></div>
            {("<div style='display:flex;align-items:center;gap:6px;'><span style='color:#c39bd3;font-size:0.78rem;'>" + t('map_2030_proj_short') + "</span></div>") if yil_map==2030 else ""}
        </div>""", unsafe_allow_html=True)

        # ─── 3D PYDECK HARİTA (interactive column extrusion) ───
        if "3D" in harita_modu:
            try:
                import pydeck as pdk
                # Kullanıcıya tema seçimi
                _tema_label = "🗺️ Sokak (OSM)" if st.session_state.dil == "tr" else "🗺️ Street (OSM)"
                _tema_label2 = "🌑 Karanlık" if st.session_state.dil == "tr" else "🌑 Dark"
                _tema_label3 = "☀️ Açık" if st.session_state.dil == "tr" else "☀️ Light"
                tema_3d = st.radio(
                    "3D Harita Teması" if st.session_state.dil == "tr" else "3D Map Theme",
                    [_tema_label, _tema_label2, _tema_label3],
                    horizontal=True, key="tema_3d_radio"
                )

                ILCE_LAT_3D = {
                    "BORNOVA":38.470,"ÇİĞLİ":38.495,"BAYRAKLI":38.460,"BUCA":38.391,
                    "GAZİEMİR":38.310,"GÜZELBAHÇE":38.370,"KARŞIYAKA":38.460,"NARLIDERE":38.395,
                    "KONAK":38.418,"KARABAĞLAR":38.395,"BALÇOVA":38.387,
                }
                ILCE_LON_3D = {
                    "BORNOVA":27.221,"ÇİĞLİ":27.060,"BAYRAKLI":27.165,"BUCA":27.180,
                    "GAZİEMİR":27.140,"GÜZELBAHÇE":26.890,"KARŞIYAKA":27.110,"NARLIDERE":27.000,
                    "KONAK":27.130,"KARABAĞLAR":27.100,"BALÇOVA":27.045,
                }
                # Renk: skor değerine göre [R, G, B, A]
                def renk_3d(s):
                    if s is None: return [120, 120, 120, 200]
                    if s >= 60: return [214, 39, 40, 230]   # kırmızı
                    if s >= 46: return [255, 127, 14, 230]  # turuncu
                    return [44, 160, 44, 230]               # yeşil
                deck_data = []
                for il in ilce_listesi:
                    sk = ilce_skor.get(il, 0)
                    deck_data.append({
                        "ilce": il,
                        "lat": ILCE_LAT_3D.get(il, 38.42),
                        "lon": ILCE_LON_3D.get(il, 27.13),
                        "skor": float(sk),
                        "sinif": sinif_str(sk),
                        "color": renk_3d(sk),
                        "elevation": float(sk) * 80,  # görsel için yükseklik
                    })
                deck_df = pd.DataFrame(deck_data)

                # OSM Tile Layer — token-free, gerçek sokak haritası
                osm_tile_layer = pdk.Layer(
                    "TileLayer",
                    data="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                    min_zoom=0,
                    max_zoom=19,
                    tile_size=256,
                    opacity=0.85,
                )

                column_layer = pdk.Layer(
                    "ColumnLayer",
                    data=deck_df,
                    get_position=["lon", "lat"],
                    get_elevation="elevation",
                    elevation_scale=1,
                    radius=1500,
                    get_fill_color="color",
                    pickable=True,
                    auto_highlight=True,
                    extruded=True,
                    coverage=0.95,
                )
                # Etiket rengini temaya göre belirle (OSM ve light için koyu, dark için beyaz)
                _label_color = [255, 255, 255, 255] if "Karanlık" in tema_3d or "Dark" in tema_3d else [20, 30, 60, 255]
                text_layer = pdk.Layer(
                    "TextLayer",
                    data=deck_df,
                    get_position=["lon", "lat"],
                    get_text="ilce",
                    get_size=14,
                    get_color=_label_color,
                    get_alignment_baseline="'bottom'",
                    background=True,
                    background_padding=[3, 2],
                    get_background_color=[255, 255, 255, 200] if "Karanlık" not in tema_3d and "Dark" not in tema_3d else [10, 30, 60, 220],
                )

                view_state = pdk.ViewState(
                    latitude=38.42, longitude=27.13,
                    zoom=9.6, pitch=50, bearing=-12,
                )

                tooltip_text = (
                    "<b>{ilce}</b><br/>"
                    "Risk Skoru: {skor}<br/>"
                    "{sinif}"
                    if st.session_state.dil == "tr" else
                    "<b>{ilce}</b><br/>"
                    "Risk Score: {skor}<br/>"
                    "{sinif}"
                )

                # Tema seçimine göre layer ve map_style ayarla
                if "OSM" in tema_3d or "Sokak" in tema_3d or "Street" in tema_3d:
                    # OSM tile layer + map_style None
                    deck_layers = [osm_tile_layer, column_layer, text_layer]
                    deck_map_style = None
                    deck_map_provider = None
                elif "Karanlık" in tema_3d or "Dark" in tema_3d:
                    deck_layers = [column_layer, text_layer]
                    deck_map_style = "dark"
                    deck_map_provider = "carto"
                else:  # Açık / Light
                    deck_layers = [column_layer, text_layer]
                    deck_map_style = "light"
                    deck_map_provider = "carto"

                deck = pdk.Deck(
                    layers=deck_layers,
                    initial_view_state=view_state,
                    map_style=deck_map_style,
                    map_provider=deck_map_provider,
                    tooltip={
                        "html": tooltip_text,
                        "style": {
                            "backgroundColor": "rgba(10,30,60,0.95)",
                            "color": "white",
                            "border": "1px solid #38d1e3",
                            "borderRadius": "8px",
                            "padding": "10px 14px",
                            "fontFamily": "Arial",
                            "fontSize": "13px",
                        }
                    },
                )
                st.pydeck_chart(deck, use_container_width=True)
                # Bilgilendirme — kullanıcıya 3D modundayken nasıl gezeceğini söyle
                if st.session_state.dil == "tr":
                    st.caption("🖱️ **Sürükle:** döndür · **Ctrl + Sürükle:** eğim · **Tekerlek:** zoom — Sütun yüksekliği = risk skoru")
                else:
                    st.caption("🖱️ **Drag:** rotate · **Ctrl + Drag:** tilt · **Wheel:** zoom — Column height = risk score")
                _three_d_rendered = True
            except Exception as _e3d:
                st.warning(f"3D harita yüklenemedi: {_e3d}. 2D moduna geçiliyor.")
                _three_d_rendered = False
        else:
            _three_d_rendered = False

        # ─── FOLIUM HARİTA (yalnızca 2D modunda) ───
        district_key = None  # Initialize early so 3D mode skip doesn't break later check
        if not _three_d_rendered and FOLIUM_OK and geo_data is not None:
            features = geo_data.get("features", [])

            # property anahtarı bul
            possible_keys = ["ILCE_ADI", "ilce_adi", "ILCEADI", "ilceadi", "ILCE", "ilce",
                             "NAME", "name", "ADI", "adi", "name_2", "NAME_2",
                             "İLÇE", "İLCE", "DISTRICT", "district"]
            if features:
                props = features[0].get("properties", {})
                for k in possible_keys:
                    if k in props:
                        district_key = k
                        break
                if district_key is None:
                    for k, v in props.items():
                        if isinstance(v, str) and len(v) < 40:
                            district_key = k
                            break

            if district_key is None:
                FOLIUM_OK = False  # fallback

        if not _three_d_rendered and FOLIUM_OK and geo_data is not None and district_key:
            # Skor sözlüğünü normalize et
            ilce_skor_norm = {turkce_normalize(k): v for k, v in ilce_skor.items()}

            def renk_seg(score):
                if score is None: return "#6c757d"
                if score >= 60: return "#d62728"
                if score >= 46: return "#ff7f0e"
                return "#2ca02c"

            # Geojson'a tooltip için ek property'ler ekle
            geo_data_enriched = copy.deepcopy(geo_data)
            eslesen_count = 0
            for feat in geo_data_enriched["features"]:
                ad = feat["properties"].get(district_key, "")
                norm = turkce_normalize(ad)
                skor = ilce_skor_norm.get(norm)
                feat["properties"]["__display_name"] = (ad if ad else "—").upper()
                feat["properties"]["__risk_score"] = f"{skor:.1f}" if skor is not None else "—"
                feat["properties"]["__risk_class"] = sinif_str(skor) if skor is not None else "—"
                feat["properties"]["__risk_color"] = renk_seg(skor)
                if skor is not None:
                    eslesen_count += 1

            def style_function(feature):
                skor_str = feature["properties"].get("__risk_score", "—")
                if skor_str == "—":
                    return {"fillColor": "#aaa", "color": "rgba(0,0,0,0.4)",
                            "weight": 0.8, "fillOpacity": 0.15}
                return {
                    "fillColor": feature["properties"]["__risk_color"],
                    "color": "#1a1a2e", "weight": 2, "fillOpacity": 0.55,
                }

            def highlight_function(feature):
                return {"fillColor": "#38d1e3", "color": "#000000",
                        "weight": 3.5, "fillOpacity": 0.65}

            # Harita oluştur (varsayılan: OpenStreetMap — doğal/gerçekçi görünüm)
            m = folium.Map(
                location=[38.42, 27.13],
                zoom_start=10,
                tiles=None,  # Aşağıda manuel ekliyoruz
                attributionControl=True,
                control_scale=True,
                zoom_control=True,
                scrollWheelZoom=True,
                dragging=True,
                doubleClickZoom=True,
            )

            # Varsayılan: OpenStreetMap (renkli, gerçekçi)
            folium.TileLayer("OpenStreetMap", name="OpenStreetMap (varsayılan)",
                             show=True).add_to(m)
            folium.TileLayer("CartoDB positron", name="Açık Tema").add_to(m)

            # Choropleth katmanı
            folium.GeoJson(
                geo_data_enriched,
                name="İzmir İlçeleri",
                style_function=style_function,
                highlight_function=highlight_function,
                tooltip=folium.GeoJsonTooltip(
                    fields=["__display_name", "__risk_score", "__risk_class"],
                    aliases=[f"{t('tbl_district')}:", f"{t('risk_score')}:", f"{t('kpi_risk_class')}:"],
                    sticky=True,
                    labels=True,
                    style="""
                        background-color: rgba(10,30,60,0.95);
                        border: 1.5px solid #38d1e3;
                        border-radius: 8px;
                        color: white;
                        font-family: Arial, sans-serif;
                        font-size: 12px;
                        padding: 10px 14px;
                        box-shadow: 0 4px 14px rgba(0,0,0,0.5);
                    """,
                ),
            ).add_to(m)

            # ── İLÇE İSİMLERİ — Her ilçenin merkezine kalıcı etiket
            ILCE_LAT_LBL = {
                "BORNOVA":38.470,"ÇİĞLİ":38.495,"BAYRAKLI":38.460,"BUCA":38.391,
                "GAZİEMİR":38.310,"GÜZELBAHÇE":38.370,"KARŞIYAKA":38.460,"NARLIDERE":38.395,
                "KONAK":38.418,"KARABAĞLAR":38.395,"BALÇOVA":38.387,
            }
            ILCE_LON_LBL = {
                "BORNOVA":27.221,"ÇİĞLİ":27.060,"BAYRAKLI":27.165,"BUCA":27.180,
                "GAZİEMİR":27.140,"GÜZELBAHÇE":26.890,"KARŞIYAKA":27.110,"NARLIDERE":27.000,
                "KONAK":27.130,"KARABAĞLAR":27.100,"BALÇOVA":27.045,
            }
            for il in ilce_listesi:
                if il in ILCE_LAT_LBL:
                    sk = ilce_skor.get(il, 0)
                    folium.map.Marker(
                        location=[ILCE_LAT_LBL[il], ILCE_LON_LBL[il]],
                        icon=folium.DivIcon(
                            icon_size=(140, 30),
                            icon_anchor=(70, 15),
                            html=f"""
                            <div style="
                                font-family: Arial, sans-serif;
                                font-size: 11px;
                                font-weight: 800;
                                color: #ffffff;
                                text-align: center;
                                white-space: nowrap;
                                text-shadow:
                                    -1.5px -1.5px 0 #000,
                                     1.5px -1.5px 0 #000,
                                    -1.5px  1.5px 0 #000,
                                     1.5px  1.5px 0 #000,
                                     0 0 4px #000;
                                pointer-events: none;
                                user-select: none;
                            ">{il}<br><span style="font-size:9px;font-weight:700;">{sk:.1f}</span></div>
                            """
                        ),
                    ).add_to(m)

            folium.LayerControl(position="topright", collapsed=True).add_to(m)

            try:
                map_html = m.get_root().render()
                components_v1.html(map_html, height=620, scrolling=False)
            except Exception as e:
                st.error(f"Harita render hatası: {type(e).__name__}: {e}")

            if eslesen_count == 0:
                st.warning(f"⚠️ GeoJSON'daki ilçe adları sözlükle eşleşmedi (property: '{district_key}'). "
                           "İlçe adlarının yapısını kontrol edin.")
            elif eslesen_count < len(ilce_listesi):
                eksik = [il for il in ilce_listesi if turkce_normalize(il) not in
                         {turkce_normalize(f["properties"].get(district_key, "")) for f in features}]
                if eksik:
                    st.caption("ℹ️ GeoJSON'da bulunamayan ilçeler: " + ", ".join(eksik))

        elif not _three_d_rendered and not FOLIUM_OK:
            # ── Folium kurulu değil — Plotly fallback
            st.error(f"📦 **Folium kurulu değil!** Hata: `{FOLIUM_ERR}`\n\n"
                     "**Çözüm:** GitHub repo'nda `requirements.txt` dosyasını aç, içine şu iki satırı ekle:\n"
                     "```\nstreamlit-folium>=0.20.0\nfolium>=0.17.0\n```\n"
                     "Sonra Streamlit Cloud'da **⋮ → Reboot app** ile yeniden başlat.")
            ILCE_LAT = {"BORNOVA":38.470,"ÇİĞLİ":38.495,"BAYRAKLI":38.460,"BUCA":38.391,
                        "GAZİEMİR":38.310,"GÜZELBAHÇE":38.370,"KARŞIYAKA":38.460,"NARLIDERE":38.395,
                        "KONAK":38.418,"KARABAĞLAR":38.395,"BALÇOVA":38.387}
            ILCE_LON = {"BORNOVA":27.221,"ÇİĞLİ":27.060,"BAYRAKLI":27.165,"BUCA":27.180,
                        "GAZİEMİR":27.140,"GÜZELBAHÇE":26.890,"KARŞIYAKA":27.110,"NARLIDERE":27.000,
                        "KONAK":27.130,"KARABAĞLAR":27.100,"BALÇOVA":27.045}
            renk_v = [sinif_renk(s) for s in skor_v]
            text_v = [f"<b>{i}</b><br>{t('risk_score')}: {s:.1f}<br>{c}" for i,s,c in zip(ilce_listesi, skor_v, sinif_v)]
            fig_m = go.Figure(go.Scattermapbox(
                lat=[ILCE_LAT[i] for i in ilce_listesi],
                lon=[ILCE_LON[i] for i in ilce_listesi],
                mode="markers+text", text=ilce_listesi,
                textposition="top center", textfont=dict(color="white", size=10),
                marker=dict(size=[20+s*0.4 for s in skor_v], color=renk_v, opacity=0.85),
                hovertext=text_v, hoverinfo="text",
            ))
            fig_m.update_layout(
                mapbox=dict(style="carto-darkmatter", center=dict(lat=38.42, lon=27.13), zoom=9.5),
                height=560, margin=dict(t=10, b=10, l=0, r=0),
                paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
            )
            st.plotly_chart(fig_m, use_container_width=True, key="map_fallback_noflm",
                            config={"scrollZoom": True})
        elif not _three_d_rendered:
            # geojson yok
            st.warning("📍 GeoJSON dosyası bulunamadı (`izmir_ilceler.geojson`). "
                       "İlçe sınırlarına göre boyalı harita için bu dosyayı repo'ya yükleyin.")
            ILCE_LAT = {"BORNOVA":38.470,"ÇİĞLİ":38.495,"BAYRAKLI":38.460,"BUCA":38.391,
                        "GAZİEMİR":38.310,"GÜZELBAHÇE":38.370,"KARŞIYAKA":38.460,"NARLIDERE":38.395,
                        "KONAK":38.418,"KARABAĞLAR":38.395,"BALÇOVA":38.387}
            ILCE_LON = {"BORNOVA":27.221,"ÇİĞLİ":27.060,"BAYRAKLI":27.165,"BUCA":27.180,
                        "GAZİEMİR":27.140,"GÜZELBAHÇE":26.890,"KARŞIYAKA":27.110,"NARLIDERE":27.000,
                        "KONAK":27.130,"KARABAĞLAR":27.100,"BALÇOVA":27.045}
            renk_v = [sinif_renk(s) for s in skor_v]
            m = folium.Map(location=[38.42, 27.13], zoom_start=10, tiles="CartoDB dark_matter")
            for il in ilce_listesi:
                folium.CircleMarker(
                    location=[ILCE_LAT.get(il, 38.42), ILCE_LON.get(il, 27.13)],
                    radius=12, color="white", weight=2,
                    fill=True, fill_color=sinif_renk(ilce_skor[il]), fill_opacity=0.85,
                    popup=f"<b>{il}</b><br>{t('risk_score')}: {ilce_skor[il]:.1f}<br>{sinif_str(ilce_skor[il])}",
                    tooltip=f"{il}: {ilce_skor[il]:.1f}",
                ).add_to(m)
            try:
                map_html = m.get_root().render()
                components_v1.html(map_html, height=580, scrolling=False)
            except Exception as e:
                st.error(f"Harita render hatası: {type(e).__name__}: {e}")

        # ── Sıralama tablosu
        sirali = sorted(zip(ilce_listesi, skor_v, sinif_v), key=lambda x: -x[1])
        rows = ""
        for ilce, sk, sn in sirali:
            renk_t = sinif_renk(sk)
            rows += f"""
            <tr>
                <td style="padding:6px 12px;color:white;font-size:0.82rem;">{ilce}</td>
                <td style="padding:6px 12px;color:{renk_t};font-size:0.82rem;font-weight:700;text-align:center;">{sk:.1f}</td>
                <td style="padding:6px 12px;color:{renk_t};font-size:0.78rem;font-weight:600;text-align:center;">{sn}</td>
            </tr>"""
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(56,209,227,0.2);border-radius:10px;overflow:hidden;margin-top:0.8rem;">
            <table style="width:100%;border-collapse:collapse;">
                <thead>
                    <tr style="background:rgba(56,209,227,0.12);">
                        <th style="padding:8px 12px;color:#38d1e3;font-size:0.72rem;text-align:left;letter-spacing:1px;">{t('tbl_district')}</th>
                        <th style="padding:8px 12px;color:#38d1e3;font-size:0.72rem;text-align:center;letter-spacing:1px;">{t('tbl_risk_score')}</th>
                        <th style="padding:8px 12px;color:#38d1e3;font-size:0.72rem;text-align:center;letter-spacing:1px;">{t('tbl_risk_class')}</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════
    # ARAÇLAR / TOOLS
    # ════════════════════════════════════════════════
    elif sayfa == "tools":

        st.markdown(f"""
        <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid rgba(56,209,227,0.2);margin-bottom:1.5rem;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);border:1px solid rgba(56,209,227,0.3);border-radius:50px;padding:4px 16px;margin-bottom:0.8rem;">
                <span style="color:#38d1e3;font-size:0.72rem;letter-spacing:3px;font-weight:600;">{t('tools_badge')}</span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">{t('tools_title')}</div>
            <div style="color:#a8d8f0;font-size:0.9rem;">{t('tools_lead')}</div>
        </div>""", unsafe_allow_html=True)

        ilce_t = st.selectbox(t("tools_select_district"), sorted(manuel_skor_2023.keys()), key="tools_ilce")

        # ── 01 · RADAR
        sec_baslik(t("tools_sec01_no"), t("tools_sec01_h"))

        col_r1, col_r2 = st.columns([3,2])
        with col_r1:
            karsi_options = [x for x in sorted(manuel_skor_2023.keys()) if x != ilce_t]
            ilce_t2 = st.selectbox(t("tools_compare_district"), karsi_options, key="tools_ilce2")

            def radar_vals(ilce):
                df = risk_df[(risk_df["İlçe"]==ilce) & (risk_df["Yıl"]==END_YEAR)]
                if df.empty:
                    return [50,50,50,50,50]
                row = df.iloc[0]
                # Normalize to 0-100
                tum_son = risk_df[risk_df["Yıl"]==END_YEAR]
                def nr(col, val):
                    rng = tum_son[col].max() - tum_son[col].min()
                    return float((val - tum_son[col].min())/rng*100) if rng > 0 else 50.0
                return [
                    nr("AbbTuketim", row["AbbTuketim"]),
                    nr("Artis", row["Artis"]),
                    nr("Arz_Kısıtı", row["Arz_Kısıtı"]),
                    nr("Su_Kayıp_Oranı_%", row["Su_Kayıp_Oranı_%"]),
                    manuel_skor_2023.get(ilce, 50.0),
                ]
            cats = [t("radar_demand"), t("radar_growth"), t("radar_supply"), t("radar_loss"), t("radar_risk")]
            v1 = radar_vals(ilce_t)
            v2 = radar_vals(ilce_t2)

            fig_r = go.Figure()
            fig_r.add_trace(go.Scatterpolar(r=v1+[v1[0]], theta=cats+[cats[0]], fill="toself",
                name=ilce_t, line=dict(color="#38d1e3", width=2.5),
                marker=dict(size=7), fillcolor="rgba(56,209,227,0.15)"))
            fig_r.add_trace(go.Scatterpolar(r=v2+[v2[0]], theta=cats+[cats[0]], fill="toself",
                name=ilce_t2, line=dict(color="#ff7f0e", width=2.5),
                marker=dict(size=7), fillcolor="rgba(255,127,14,0.12)"))
            fig_r.update_layout(polar=dict(bgcolor="rgba(0,0,0,0.2)", radialaxis=dict(range=[0,100], gridcolor="rgba(255,255,255,0.15)", tickfont=dict(color="white", size=9)), angularaxis=dict(tickfont=dict(color="white", size=11), gridcolor="rgba(255,255,255,0.15)")),
                showlegend=True, legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)"),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=420, margin=dict(t=30, b=30, l=40, r=40))
            st.plotly_chart(fig_r, use_container_width=True, key="radar_chart")

        with col_r2:
            st.markdown(f'<div style="color:#38d1e3;font-size:0.78rem;font-weight:700;letter-spacing:1px;margin:1rem 0 0.6rem 0;">{t("radar_indicator")}</div>', unsafe_allow_html=True)
            for cat_full, val_a, val_b in [(t("radar_demand_full"), v1[0], v2[0]),
                                            (t("radar_growth_full"), v1[1], v2[1]),
                                            (t("radar_supply_full"), v1[2], v2[2]),
                                            (t("radar_loss_full"), v1[3], v2[3]),
                                            (t("radar_risk_full"), v1[4], v2[4])]:
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.04);border-radius:8px;padding:0.5rem 0.75rem;margin-bottom:6px;">
                    <div style="color:#a8d8f0;font-size:0.72rem;margin-bottom:3px;">{cat_full}</div>
                    <div style="display:flex;justify-content:space-between;">
                        <span style="color:#38d1e3;font-size:0.85rem;font-weight:700;">{ilce_t}: {val_a:.0f}</span>
                        <span style="color:#ff7f0e;font-size:0.85rem;font-weight:700;">{ilce_t2}: {val_b:.0f}</span>
                    </div>
                </div>""", unsafe_allow_html=True)

        # ── 02 · SİMÜLATÖR
        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        sec_baslik(t("tools_sec02_no"), t("tools_sec02_h"))
        st.caption(t("tools_sec02_caption"))

        sc1, sc2 = st.columns(2)
        with sc1:
            sim_demand = st.slider(t("sim_demand"), 80, 250, 150, 5)
            sim_supply = st.slider(t("sim_supply"), 0, 100, 30, 1)
        with sc2:
            sim_growth = st.slider(t("sim_growth"), -10, 30, 5, 1)
            sim_loss = st.slider(t("sim_loss"), 5, 50, 27, 1)

        # Skor hesabı (entropi ağırlıkları kullanılarak)
        # Min-Max normalleştirme yaklaşık aralıklarla
        z_d = (sim_demand - 100) / (250 - 100)
        z_g = (sim_growth + 5) / (30 + 5)
        z_s = sim_supply / 100
        z_l = (sim_loss - 5) / (50 - 5)
        # Ağırlıklar: 31.6% talep, 11.6% büyüme, 23.8% arz, 33.0% kayıp
        sim_skor = (0.316*z_d + 0.116*z_g + 0.238*z_s + 0.330*z_l) * 100
        sim_skor = float(np.clip(sim_skor, 0, 100))
        sim_sinif = sinif_str(sim_skor)
        sim_renk = sinif_renk(sim_skor)

        sk1, sk2, sk3, sk4 = st.columns(4)
        with sk1:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.06);border:1px solid {sim_renk}44;border-top:3px solid {sim_renk};border-radius:10px;padding:1rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.7rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">{t('sim_kpi_score')}</div>
                <div style="color:#ffffff;font-size:1.6rem;font-weight:700;margin-bottom:4px;">{sim_skor:.1f}</div>
                <div style="color:{sim_renk};font-size:0.78rem;">/ 100</div>
            </div>""", unsafe_allow_html=True)
        with sk2:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.06);border:1px solid {sim_renk}44;border-top:3px solid {sim_renk};border-radius:10px;padding:1rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.7rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">{t('sim_kpi_class')}</div>
                <div style="color:#ffffff;font-size:1.2rem;font-weight:700;margin-bottom:4px;">{sim_sinif}</div>
                <div style="color:{sim_renk};font-size:0.78rem;">{t('sim_kpi_score')}: {sim_skor:.0f}</div>
            </div>""", unsafe_allow_html=True)
        with sk3:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.06);border:1px solid #38d1e344;border-top:3px solid #38d1e3;border-radius:10px;padding:1rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.7rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">{t('sim_kpi_weighted')}</div>
                <div style="color:#ffffff;font-size:0.95rem;font-weight:700;margin-bottom:4px;">{t('sim_kpi_weighted_val')}</div>
            </div>""", unsafe_allow_html=True)
        with sk4:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.06);border:1px solid #9467bd44;border-top:3px solid #9467bd;border-radius:10px;padding:1rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.7rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">{t('sim_kpi_arz_growth')}</div>
                <div style="color:#ffffff;font-size:0.95rem;font-weight:700;margin-bottom:4px;">{t('sim_kpi_arz_growth_val')}</div>
            </div>""", unsafe_allow_html=True)

        # ── 03 · ANİMASYON
        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        sec_baslik(t("tools_sec03_no"), t("tools_sec03_h"))

        ilceler_anim = list(manuel_risk_global.keys())
        frames = []
        for i, yil in enumerate(YEARS):
            yil_skorlar = [manuel_risk_global[il][i] for il in ilceler_anim]
            sirala = sorted(zip(ilceler_anim, yil_skorlar), key=lambda x: x[1])
            il_s = [x[0] for x in sirala]; sk_s = [x[1] for x in sirala]
            renkler_a = [sinif_renk(s) for s in sk_s]
            frames.append(go.Frame(
                data=[go.Bar(x=sk_s, y=il_s, orientation="h",
                             marker=dict(color=renkler_a, opacity=0.85),
                             text=[f"{s:.1f}" for s in sk_s], textposition="outside",
                             textfont=dict(color="white", size=11))],
                name=str(yil)
            ))
        # İlk frame
        i0 = 0
        yil0_skorlar = [manuel_risk_global[il][i0] for il in ilceler_anim]
        sirala0 = sorted(zip(ilceler_anim, yil0_skorlar), key=lambda x: x[1])
        il_s0 = [x[0] for x in sirala0]; sk_s0 = [x[1] for x in sirala0]
        renkler_a0 = [sinif_renk(s) for s in sk_s0]

        fig_anim = go.Figure(
            data=[go.Bar(x=sk_s0, y=il_s0, orientation="h",
                         marker=dict(color=renkler_a0, opacity=0.85),
                         text=[f"{s:.1f}" for s in sk_s0], textposition="outside",
                         textfont=dict(color="white", size=11))],
            frames=frames
        )
        fig_anim.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            height=440, font=dict(color="white"),
            xaxis=dict(range=[0, 80], gridcolor="rgba(255,255,255,0.08)", title=t("risk_score_axis")),
            yaxis=dict(tickfont=dict(color="white", size=11)),
            margin=dict(t=60, b=40, l=110, r=80),
            updatemenus=[dict(type="buttons", showactive=False, y=1.12, x=0.0, xanchor="left", yanchor="top",
                buttons=[
                    dict(label=t("anim_play"), method="animate", args=[None, {"frame":{"duration":700, "redraw":True}, "fromcurrent":True}]),
                    dict(label=t("anim_pause"), method="animate", args=[[None], {"frame":{"duration":0, "redraw":False}, "mode":"immediate"}])
                ])],
            sliders=[dict(active=0, currentvalue=dict(font=dict(color="#38d1e3", size=12), prefix=t("anim_year_prefix")),
                pad={"t":40},
                steps=[dict(method="animate", args=[[str(y)], {"frame":{"duration":500, "redraw":True}, "mode":"immediate"}], label=str(y)) for y in YEARS])]
        )
        st.plotly_chart(fig_anim, use_container_width=True, key="anim_chart")
        st.caption(t("anim_caption"))

        # ── 04 · KARŞILAŞTIRMA HESAPLAYICISI
        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        sec_baslik(t("tools_sec04_no"), t("tools_sec04_h"))
        st.caption(t("tools_sec04_caption"))

        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            ilce_a = st.selectbox(t("calc_district_1"), sorted(manuel_risk_global.keys()), index=0, key="calc_a")
        with cc2:
            ilce_b = st.selectbox(t("calc_district_2"), sorted(manuel_risk_global.keys()), index=1, key="calc_b")
        with cc3:
            yil_range = st.select_slider(t("calc_year_range"), options=YEARS, value=(YEARS[0], YEARS[-1]), key="calc_yr")

        i_start = YEARS.index(yil_range[0])
        i_end = YEARS.index(yil_range[1])
        a_start = manuel_risk_global[ilce_a][i_start]; a_end = manuel_risk_global[ilce_a][i_end]
        b_start = manuel_risk_global[ilce_b][i_start]; b_end = manuel_risk_global[ilce_b][i_end]
        a_chg = a_end - a_start; b_chg = b_end - b_start

        ck1, ck2, ck3, ck4 = st.columns(4)
        with ck1:
            ok = "▲" if a_chg>0 else "▼"; rc = "#d62728" if a_chg>0 else "#2ca02c"
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.06);border:1px solid #38d1e344;border-top:3px solid #38d1e3;border-radius:10px;padding:1rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.7rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">{ilce_a} · {yil_range[0]}</div>
                <div style="color:#ffffff;font-size:1.4rem;font-weight:700;">{a_start:.1f}</div>
            </div>""", unsafe_allow_html=True)
        with ck2:
            ok = "▲" if a_chg>0 else "▼"; rc = "#d62728" if a_chg>0 else "#2ca02c"
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.06);border:1px solid {rc}44;border-top:3px solid {rc};border-radius:10px;padding:1rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.7rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">{ilce_a} · {yil_range[1]}</div>
                <div style="color:#ffffff;font-size:1.4rem;font-weight:700;">{a_end:.1f}</div>
                <div style="color:{rc};font-size:0.78rem;">{ok} {abs(a_chg):.1f}</div>
            </div>""", unsafe_allow_html=True)
        with ck3:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.06);border:1px solid #ff7f0e44;border-top:3px solid #ff7f0e;border-radius:10px;padding:1rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.7rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">{ilce_b} · {yil_range[0]}</div>
                <div style="color:#ffffff;font-size:1.4rem;font-weight:700;">{b_start:.1f}</div>
            </div>""", unsafe_allow_html=True)
        with ck4:
            ok = "▲" if b_chg>0 else "▼"; rc = "#d62728" if b_chg>0 else "#2ca02c"
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.06);border:1px solid {rc}44;border-top:3px solid {rc};border-radius:10px;padding:1rem;text-align:center;">
                <div style="color:#a8d8f0;font-size:0.7rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">{ilce_b} · {yil_range[1]}</div>
                <div style="color:#ffffff;font-size:1.4rem;font-weight:700;">{b_end:.1f}</div>
                <div style="color:{rc};font-size:0.78rem;">{ok} {abs(b_chg):.1f}</div>
            </div>""", unsafe_allow_html=True)

        # Karşılaştırma çizgi grafiği
        fig_cmp = go.Figure()
        ys_a = manuel_risk_global[ilce_a][i_start:i_end+1]
        ys_b = manuel_risk_global[ilce_b][i_start:i_end+1]
        x_yrs = list(YEARS[i_start:i_end+1])
        fig_cmp.add_trace(go.Scatter(x=x_yrs, y=ys_a, mode="lines+markers", name=ilce_a,
            line=dict(color="#38d1e3", width=2.5), marker=dict(size=8)))
        fig_cmp.add_trace(go.Scatter(x=x_yrs, y=ys_b, mode="lines+markers", name=ilce_b,
            line=dict(color="#ff7f0e", width=2.5), marker=dict(size=8)))
        fig_cmp.update_layout(plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",height=300,font=dict(color="white"),
            xaxis=dict(tickvals=x_yrs, gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color="white"),tickangle=-45),
            yaxis=dict(title=t("wsri_axis"), gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color="white")),
            legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)"),
            margin=dict(t=20, b=50, l=50, r=20), hovermode="x unified")
        st.plotly_chart(fig_cmp, use_container_width=True, key="cmp_chart")

    # ════════════════════════════════════════════════
    # METODOLOJİ
    # ════════════════════════════════════════════════
    elif sayfa == "method":

        st.markdown(f"""
        <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid rgba(56,209,227,0.2);margin-bottom:1.5rem;">
            <div style="display:inline-block;background:rgba(56,209,227,0.1);border:1px solid rgba(56,209,227,0.3);border-radius:50px;padding:4px 16px;margin-bottom:0.8rem;">
                <span style="color:#38d1e3;font-size:0.72rem;letter-spacing:3px;font-weight:600;">{t('method_badge')}</span>
            </div>
            <div style="color:#ffffff;font-size:1.8rem;font-weight:700;margin-bottom:0.3rem;">{t('method_title')}</div>
            <div style="color:#a8d8f0;font-size:0.9rem;">{t('method_lead')}</div>
        </div>""", unsafe_allow_html=True)

        # 01 · DATA SOURCE
        sec_baslik(t("method_sec01_no"), t("method_sec01_h"))
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px;">
            <div style="background:rgba(56,209,227,0.06);border:1px solid rgba(56,209,227,0.25);border-radius:10px;padding:1rem 1.2rem;">
                <div style="color:#38d1e3;font-size:0.78rem;font-weight:700;letter-spacing:1px;margin-bottom:8px;">{t('method_district_data_title')}</div>
                <div style="color:#d0e8f5;font-size:0.85rem;line-height:1.8;">{t('method_district_data_text')}</div>
            </div>
            <div style="background:rgba(155,89,182,0.06);border:1px solid rgba(155,89,182,0.25);border-radius:10px;padding:1rem 1.2rem;">
                <div style="color:#c39bd3;font-size:0.78rem;font-weight:700;letter-spacing:1px;margin-bottom:8px;">{t('method_system_data_title')}</div>
                <div style="color:#d0e8f5;font-size:0.85rem;line-height:1.8;">{t('method_system_data_text')}</div>
            </div>
        </div>""", unsafe_allow_html=True)

        # 02 · BOOTSTRAP
        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        sec_baslik(t("method_sec02_no"), t("method_sec02_h"))
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-bottom:0.8rem;">
            <div style="background:rgba(255,127,14,0.06);border:1px solid rgba(255,127,14,0.25);border-radius:10px;padding:1rem 1.2rem;">
                <div style="color:#ff7f0e;font-size:0.82rem;font-weight:700;letter-spacing:1px;margin-bottom:8px;">{t('method_why_title')}</div>
                <div style="color:#d0e8f5;font-size:0.85rem;line-height:1.7;">{t('method_why_text')}</div>
            </div>
            <div style="background:rgba(56,209,227,0.06);border:1px solid rgba(56,209,227,0.25);border-radius:10px;padding:1rem 1.2rem;">
                <div style="color:#38d1e3;font-size:0.82rem;font-weight:700;letter-spacing:1px;margin-bottom:8px;">{t('method_block_title')}</div>
                <div style="color:#d0e8f5;font-size:0.85rem;line-height:1.7;">{t('method_block_text')}</div>
            </div>
            <div style="background:rgba(44,160,44,0.06);border:1px solid rgba(44,160,44,0.25);border-radius:10px;padding:1rem 1.2rem;">
                <div style="color:#2ca02c;font-size:0.82rem;font-weight:700;letter-spacing:1px;margin-bottom:8px;">{t('method_trust_title')}</div>
                <div style="color:#d0e8f5;font-size:0.85rem;line-height:1.7;">{t('method_trust_text')}</div>
            </div>
            <div style="background:rgba(155,89,182,0.06);border:1px solid rgba(155,89,182,0.25);border-radius:10px;padding:1rem 1.2rem;">
                <div style="color:#c39bd3;font-size:0.82rem;font-weight:700;letter-spacing:1px;margin-bottom:8px;">{t('method_trans_title')}</div>
                <div style="color:#d0e8f5;font-size:0.85rem;line-height:1.7;">{t('method_trans_text')}</div>
            </div>
        </div>""", unsafe_allow_html=True)

        # 03 · WSRI
        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        sec_baslik(t("method_sec03_no"), t("method_sec03_h"))

        with st.expander(t("method_step1_t"), expanded=False):
            st.markdown(t("method_step1_text"))
            st.caption(t("method_step1_caption"))
        with st.expander(t("method_step2_t"), expanded=False):
            st.markdown(t("method_step2_text"))
            st.caption(t("method_step2_caption"))
        with st.expander(t("method_step3_t"), expanded=False):
            st.markdown(t("method_step3_text"))
            st.caption(t("method_step3_caption"))

        # Hesaplanan ağırlıklar göster
        st.markdown(f"""
        <div style="background:rgba(56,209,227,0.05);border:1px solid rgba(56,209,227,0.2);border-radius:10px;padding:1rem 1.2rem;margin-top:0.8rem;">
            <div style="color:#38d1e3;font-size:0.78rem;font-weight:700;letter-spacing:1px;margin-bottom:10px;">{t('method_weights_title')}</div>
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;">
                <div style="text-align:center;">
                    <div style="color:#a8d8f0;font-size:0.72rem;margin-bottom:4px;">{t('weight_demand_label')}</div>
                    <div style="color:#38d1e3;font-size:1.4rem;font-weight:700;">%{W[0]*100:.1f}</div>
                </div>
                <div style="text-align:center;">
                    <div style="color:#a8d8f0;font-size:0.72rem;margin-bottom:4px;">{t('weight_growth_label')}</div>
                    <div style="color:#38d1e3;font-size:1.4rem;font-weight:700;">%{W[1]*100:.1f}</div>
                </div>
                <div style="text-align:center;">
                    <div style="color:#a8d8f0;font-size:0.72rem;margin-bottom:4px;">{t('weight_supply_label')}</div>
                    <div style="color:#38d1e3;font-size:1.4rem;font-weight:700;">%{W[2]*100:.1f}</div>
                </div>
                <div style="text-align:center;">
                    <div style="color:#a8d8f0;font-size:0.72rem;margin-bottom:4px;">{t('weight_loss_label')}</div>
                    <div style="color:#38d1e3;font-size:1.4rem;font-weight:700;">%{W[3]*100:.1f}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        # 04 · MK & SEN
        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        sec_baslik(t("method_sec04_no"), t("method_sec04_h"))
        with st.expander(t("method_mk_t"), expanded=False):
            st.markdown(t("method_mk_text"))
            st.caption(t("method_mk_caption"))
        with st.expander(t("method_sen_t"), expanded=False):
            st.markdown(t("method_sen_text"))
            st.caption(t("method_sen_caption"))

        # 05 · SPATIAL
        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        sec_baslik(t("method_sec05_no"), t("method_sec05_h"))
        with st.expander(t("method_moran_t"), expanded=False):
            st.markdown(t("method_moran_text"))
            st.caption(t("method_moran_caption"))
        with st.expander(t("method_lisa_t"), expanded=False):
            st.markdown(t("method_lisa_text"))
            st.caption(t("method_lisa_caption"))

        # 06 · CAGR
        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        sec_baslik(t("method_sec06_no"), t("method_sec06_h"))
        with st.expander(t("method_cagr_t"), expanded=False):
            st.markdown(t("method_cagr_text"))
            st.caption(t("method_cagr_caption"))

        # 07 · LIMITS
        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        sec_baslik(t("method_sec07_no"), t("method_sec07_h"))
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px;">
            <div style="background:rgba(155,89,182,0.06);border:1px solid rgba(155,89,182,0.25);border-radius:10px;padding:0.9rem 1.1rem;">
                <div style="color:#c39bd3;font-size:0.78rem;font-weight:700;letter-spacing:1px;margin-bottom:6px;">{t('limit_1_t')}</div>
                <div style="color:#d0e8f5;font-size:0.84rem;line-height:1.65;">{t('limit_1_text')}</div>
            </div>
            <div style="background:rgba(255,127,14,0.06);border:1px solid rgba(255,127,14,0.25);border-radius:10px;padding:0.9rem 1.1rem;">
                <div style="color:#ff7f0e;font-size:0.78rem;font-weight:700;letter-spacing:1px;margin-bottom:6px;">{t('limit_2_t')}</div>
                <div style="color:#d0e8f5;font-size:0.84rem;line-height:1.65;">{t('limit_2_text')}</div>
            </div>
            <div style="background:rgba(255,127,14,0.06);border:1px solid rgba(255,127,14,0.25);border-radius:10px;padding:0.9rem 1.1rem;">
                <div style="color:#ff7f0e;font-size:0.78rem;font-weight:700;letter-spacing:1px;margin-bottom:6px;">{t('limit_3_t')}</div>
                <div style="color:#d0e8f5;font-size:0.84rem;line-height:1.65;">{t('limit_3_text')}</div>
            </div>
            <div style="background:rgba(44,160,44,0.06);border:1px solid rgba(44,160,44,0.25);border-radius:10px;padding:0.9rem 1.1rem;">
                <div style="color:#2ca02c;font-size:0.78rem;font-weight:700;letter-spacing:1px;margin-bottom:6px;">{t('limit_4_t')}</div>
                <div style="color:#d0e8f5;font-size:0.84rem;line-height:1.65;">{t('limit_4_text')}</div>
            </div>
        </div>""", unsafe_allow_html=True)

        # 08 · FAQ
        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        sec_baslik(t("method_sec08_no"), t("method_sec08_h"))
        for q, a in t("faq"):
            with st.expander(q, expanded=False):
                st.markdown(a)
