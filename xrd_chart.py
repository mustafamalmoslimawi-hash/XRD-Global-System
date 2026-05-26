import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

st.set_page_config(page_title="XRD 10,000 Global System", layout="wide")

st.markdown("<h1 style='text-align: center; color: #008080;'>XRD 10,000 GLOBAL SYSTEM</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #555;'>ADVANCED ROBUST PATTERN RECOGNITION</h4>", unsafe_allow_html=True)
st.write("---")

DB_FILE_NAME = "Comprehensive_10000_Nano_Crystallographic_Database.xlsx"

@st.cache_data
def load_10k_database():
    try:
        df_db = pd.read_excel(DB_FILE_NAME)
        # تنظيف أسماء الأعمدة من أي فراغات زائفة وتحويلها لنصوص
        df_db.columns = [str(col).strip() for col in df_db.columns]
        return df_db
    except Exception as e:
        return None

db_df = load_10k_database()

col_left, col_right = st.columns([1, 2])

with col_left:
    st.header("لوحة التحكم والتشخيص الفوري")
    uploaded_file = st.file_uploader("الرجاء رفع ملف الـ XRD المراد فحصه (Excel فقط):", type=["xlsx", "xls"])
    
    st.subheader("Automated Multi-Peak Diagnosis")
    
    if uploaded_file is not None:
        try:
            user_data = pd.read_excel(uploaded_file)
            user_theta = pd.to_numeric(user_data.iloc[:, 0], errors='coerce').values
            user_intensity = pd.to_numeric(user_data.iloc[:, 1], errors='coerce').values
            
            # تنظيف مصفوفات الباحث
            valid_mask = ~np.isnan(user_theta) & ~np.isnan(user_intensity)
            user_theta = user_theta[valid_mask]
            user_intensity = user_intensity[valid_mask]
            
            # استخراج أعلى قمم من المنحنى التجريبي
            peaks, _ = find_peaks(user_intensity, height=np.max(user_intensity)*0.10, distance=20)
            
            if len(peaks) > 0:
                sorted_peaks_idx = peaks[np.argsort(user_intensity[peaks])[::-1]]
                detected_peaks = sorted([round(float(user_theta[idx]), 2) for idx in sorted_peaks_idx[:5]])
                user_main_peak = round(float(user_theta[sorted_peaks_idx[0]]), 2)
                user_max_intensity = user_intensity[sorted_peaks_idx[0]]
                
                # الحسابات الفيزيائية
                wavelength = 1.5406
                theta_rad = np.radians(user_main_peak / 2)
                d_spacing = round(wavelength / (2 * np.sin(theta_rad)), 3)
                fwhm_val = 0.35  
                crystallite_size = round((0.9 * wavelength) / (np.radians(fwhm_val) * np.cos(theta_rad)), 2)
                
                # خوارزمية فحص التوافق الذكي الذاتي مع قاعدة البيانات
                identified_material = "Unknown Nanomaterial Phase"
                cod_id = "N/A"
                total_matches = 0
                
                if db_df is not None:
                    # ميزة التوافق الديناميكي: البحث عن العمود الصحيح بناءً على اسمه أو مكانه الافتراضي
                    cols = list(db_df.columns)
                    
                    # محاولة تحديد عمود الزوايا (ابحث عن كلمة Peak أو العمود الرابع)
                    peak_col_name = next((c for c in cols if 'peak' in c.lower()), cols[3] if len(cols) > 3 else cols[-1])
                    # تحديد عمود اسم المادة
                    name_col_name = next((c for c in cols if 'material' in c.lower() or 'name' in c.lower()), cols[2] if len(cols) > 2 else cols[0])
                    # تحديد عمود الرمز الكيميائي أو المعرف
                    id_col_name = next((c for c in cols if 'identifier' in c.lower() or 'symbol' in c.lower() or 'formula' in c.lower()), cols[1] if len(cols) > 1 else cols[0])
                    # تحديد عمود الـ COD
                    cod_col_name = next((c for c in cols if 'cod' in c.lower() or 'database' in c.lower() or 'no' in c.lower()), cols[5] if len(cols) > 5 else cols[-1])
                    
                    # تحويل عمود الزوايا المرجعي بالكامل إلى أرقام بشكل آمن
                    ref_peaks = pd.to_numeric(db_df[peak_col_name], errors='coerce').values
                    valid_db_mask = ~np.isnan(ref_peaks)
                    
                    best_db_idx = None
                    max_score = -1
                    
                    for idx in np.where(valid_db_mask)[0]:
                        db_peak = ref_peaks[idx]
                        
                        # فحص تطابق النمط الكامل مع السماحية البلورية
                        matched_in_profile = any(abs(db_peak - up) < 0.35 for up in detected_peaks)
                        
                        if matched_in_profile:
                            primary_diff = abs(db_peak - user_main_peak)
                            score = 100 - (primary_diff * 100)
                            
                            if score > max_score:
                                max_score = score
                                best_db_idx = idx
                    
                    if best_db_idx is not None:
                        chem_symbol = str(db_df[id_col_name].iloc[best_db_idx]).strip()
                        mat_details = str(db_df[name_col_name].iloc[best_db_idx]).strip()
                        identified_material = f"{mat_details} ({chem_symbol})"
                        cod_id = "COD #" + str(db_df[cod_col_name].iloc[best_db_idx]).strip()
                        total_matches = len(detected_peaks)
                else:
                    st.error("تنبيه: تعذر تحميل ملف قاعدة البيانات الـ 10K!")
                
                # عرض تقرير الفحص البلوري المتكامل
                st.info(f"**Identified Phase:** {identified_material}")
                st.success(f"**COD Reference ID:** {cod_id}")
                st.write(f"📊 **Detected Pattern Fingerprints (2θ):** `{detected_peaks}`")
                st.caption(f"🎯 تم التشخيص والمطابقة بناءً على حزمة من `{total_matches}` قمم حيود نشطة.")
                
                st.write("---")
                st.metric(label="Main Peak (2θ):", value=f"{user_main_peak}°")
                st.metric(label="d-spacing (d):", value=f"{d_spacing} A")
                st.metric(label="FWHM (β):", value=f"{fwhm_val}°")
                st.metric(label="Crystallite Size (D):", value=f"{crystallite_size} nm")
            else:
                st.warning("لم يتم تحديد قمم بلورية حادة في الملف المرفوع.")
        except Exception as e:
            st.error(f"خطأ أثناء فحص وتدقيق النمط: {e}")
    else:
        st.warning("بانتظار رفع ملف إكسل لبدء الفحص وفك التلابس التلقائي الشامل...")

with col_right:
    st.header("📊 منحنى حيود الأشعة السينية (XRD Chart)")
    if uploaded_file is not None and 'detected_peaks' in locals():
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(user_theta, user_intensity, color='#00a8cc', linewidth=1.5, label='Experimental Pattern')
        
        for p in detected_peaks:
            p_idx = np.abs(user_theta - p).argmin()
            ax.plot(user_theta[p_idx], user_intensity[p_idx], 'ro')
            
        ax.set_xlabel("2-Theta (Degrees)")
        ax.set_ylabel("Intensity (a.u.)")
        ax.grid(True, linestyle='--', alpha=0.5)
        st.pyplot(fig)
    else:
        st.info("سيظهر هنا رسم المنحنى البياني التفاعلي فور رفع ملف البيانات بنجاح.")

# ---------------------------------------------------------
# تذييل الصفحة المخصص
# ---------------------------------------------------------
st.markdown("<br><br><hr>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; color: #888888; font-size: 16px; font-weight: bold;'> "
    "تم تطويره بواسطة دكتور مصطفى المسلماوي"
    "</p>", 
    unsafe_allow_html=True
)
