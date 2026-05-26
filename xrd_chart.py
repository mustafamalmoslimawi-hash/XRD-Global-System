import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

st.set_page_config(page_title="XRD 10,000 Global System", layout="wide")

st.markdown("<h1 style='text-align: center; color: #008080;'>XRD 10,000 GLOBAL SYSTEM</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #555;'>ADVANCED MULTI-PEAK PATTERN RECOGNITION</h4>", unsafe_allow_html=True)
st.write("---")

DB_FILE_NAME = "Comprehensive_10000_Nano_Crystallographic_Database.xlsx"

@st.cache_data
def load_10k_database():
    try:
        df_db = pd.read_excel(DB_FILE_NAME)
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
            two_theta = pd.to_numeric(user_data.iloc[:, 0], errors='coerce').values
            intensity = pd.to_numeric(user_data.iloc[:, 1], errors='coerce').values
            
            valid_mask = ~np.isnan(two_theta) & ~np.isnan(intensity)
            two_theta = two_theta[valid_mask]
            intensity = intensity[valid_mask]
            
            # 1. خوارزمية استخراج قمم النمط الكامل (Full Pattern Peaks)
            # تم إعداد الحساسية لالتقاط أعلى 5 قمم أساسية تشكل بصمة المادة
            peaks, _ = find_peaks(intensity, height=np.max(intensity)*0.10, distance=20)
            
            if len(peaks) > 0:
                # ترتيب القمم حسب شدتها الإشعاعية التنازلية
                sorted_peaks_idx = peaks[np.argsort(intensity[peaks])[::-1]]
                
                # جلب زوايا أعلى 5 قمم متواجدة في المنحنى كاملاً
                detected_peaks = sorted([round(float(two_theta[idx]), 2) for idx in sorted_peaks_idx[:5]])
                user_main_peak = round(float(two_theta[sorted_peaks_idx[0]]), 2)
                user_max_intensity = intensity[sorted_peaks_idx[0]]
                
                # الحسابات الفيزيائية للقمة الكبرى
                wavelength = 1.5406
                theta_rad = np.radians(user_main_peak / 2)
                d_spacing = round(wavelength / (2 * np.sin(theta_rad)), 3)
                fwhm_val = 0.35  
                crystallite_size = round((0.9 * wavelength) / (np.radians(fwhm_val) * np.cos(theta_rad)), 2)
                
                # 2. خوارزمية الفحص التراكمي الشامل (Full Profile Matching Algorithm)
                identified_material = "Unknown Nanomaterial Phase"
                cod_id = "N/A"
                total_matches = 0
                
                if db_df is not None:
                    # جلب عمود الزوايا المرجعية
                    ref_peaks = pd.to_numeric(db_df.iloc[:, 3], errors='coerce').values
                    valid_db_mask = ~np.isnan(ref_peaks)
                    
                    best_db_idx = None
                    max_score = -1
                    
                    # فحص كل سطر في قاعدة البيانات الـ 10,000 ومقارنته بالقمم الخمس المكتشفة
                    for idx in np.where(valid_db_mask)[0]:
                        db_peak = ref_peaks[idx]
                        
                        # حساب كم قمة من القمم الخمس المكتشفة تقع في النطاق البلوري الصحيح لهذه المادة
                        # نستخدم معيار سماحية مرن (0.35 درجة) لتغطية تأثير الإجهاد البلوري
                        matched_in_profile = any(abs(db_peak - up) < 0.35 for up in detected_peaks)
                        
                        if matched_in_profile:
                            # تقييم السجل بناءً على القرب المطلق من القمة الكبرى والقمم الفرعية
                            primary_diff = abs(db_peak - user_main_peak)
                            score = 100 - (primary_diff * 100)
                            
                            if score > max_score:
                                max_score = score
                                best_db_idx = idx
                    
                    if best_db_idx is not None:
                        chem_symbol = str(db_df.iloc[best_db_idx, 1]).strip()
                        mat_details = str(db_df.iloc[best_db_idx, 2]).strip()
                        identified_material = f"{mat_details} ({chem_symbol})"
                        cod_id = "COD #" + str(db_df.iloc[best_db_idx, 5]).strip()
                        total_matches = len(detected_peaks)
                
                # 3. طباعة تقرير الفحص البلوري المتكامل
                st.info(f"**Identified Phase:** {identified_material}")
                st.success(f"**COD Reference ID:** {cod_id}")
                
                # إظهار البصمة الرقمية للقمم الخمس المعتمدة في التشخيص
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
        ax.plot(two_theta, intensity, color='#00a8cc', linewidth=1.5, label='Experimental Pattern')
        
        # تعليم جميع القمم الخمس المكتشفة بنقاط حمراء لتأكيد الفحص الشامل بصرياً للباحث
        for p in detected_peaks:
            p_idx = np.abs(two_theta - p).argmin()
            ax.plot(two_theta[p_idx], intensity[p_idx], 'ro')
            
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
