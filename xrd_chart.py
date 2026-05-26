import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # لضمان تشغيل الرسوم البيانية سحابياً بدون مكتبات الواجهات الرسومية
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# إعدادات واجهة المستخدم المتقدمة
st.set_page_config(page_title="XRD 10,000 Global System", layout="wide")

st.markdown("<h1 style='text-align: center; color: #008080;'>XRD 10,000 GLOBAL SYSTEM</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #555;'>HIGH-PRECISION AUTOMATED MOLECULAR DIAGNOSIS</h4>", unsafe_allow_html=True)
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
    
    st.subheader("Automated Material Diagnosis")
    
    if uploaded_file is not None:
        try:
            user_data = pd.read_excel(uploaded_file)
            two_theta = pd.to_numeric(user_data.iloc[:, 0], errors='coerce').values
            intensity = pd.to_numeric(user_data.iloc[:, 1], errors='coerce').values
            
            # تنظيف مصفوفات الباحث من أي قيم فارغة
            valid_mask = ~np.isnan(two_theta) & ~np.isnan(intensity)
            two_theta = two_theta[valid_mask]
            intensity = intensity[valid_mask]
            
            # 1. التقاط البصمة البلورية الفردية والممتدة (Peak Detection)
            peaks, _ = find_peaks(intensity, height=np.max(intensity)*0.10, distance=15)
            
            if len(peaks) > 0:
                sorted_peaks = peaks[np.argsort(intensity[peaks])[::-1]]
                user_main_peak = round(float(two_theta[sorted_peaks[0]]), 2)
                user_max_intensity = intensity[sorted_peaks[0]]
                
                # الحسابات الفيزيائية
                wavelength = 1.5406
                theta_rad = np.radians(user_main_peak / 2)
                d_spacing = round(wavelength / (2 * np.sin(theta_rad)), 3)
                
                fwhm_val = 0.35  
                crystallite_size = round((0.9 * wavelength) / (np.radians(fwhm_val) * np.cos(theta_rad)), 2)
                
                # 2. خوارزمية الحساب والمطابقة الصارمة (Strict Delta Filter)
                identified_material = "Unknown Nanomaterial Phase"
                cod_id = "N/A"
                confidence = 0
                
                if db_df is not None:
                    # جلب عمود الزوايا البلورية المرجعية (العمود الرابع - الفهرس 3)
                    ref_peaks = pd.to_numeric(db_df.iloc[:, 3], errors='coerce').values
                    valid_db_mask = ~np.isnan(ref_peaks)
                    
                    diffs = np.abs(ref_peaks[valid_db_mask] - user_main_peak)
                    
                    if len(diffs) > 0:
                        closest_idx = np.argmin(diffs)
                        actual_db_idx = np.where(valid_db_mask)[0][closest_idx]
                        
                        # نطاق فحص وحصار ضيق جداً (0.25 درجة) لمنع التداخل تماماً بين المتشابهات
                        if diffs[closest_idx] < 0.25:
                            chem_symbol = str(db_df.iloc[actual_db_idx, 1]).strip() # العمود الثاني
                            mat_details = str(db_df.iloc[actual_db_idx, 2]).strip() # العمود الثالث
                            identified_material = f"{mat_details} ({chem_symbol})"
                            cod_id = "COD #" + str(db_df.iloc[actual_db_idx, 5]).strip() # العمود السادس
                            
                            confidence = int((1 - (diffs[closest_idx] / 0.25)) * 100)
                            confidence = max(50, min(100, confidence))
                else:
                    st.error("تنبيه: لم يتم العثور على قاعدة البيانات المرجعية المرفقة!")
                
                # عرض المخرجات
                st.info(f"**Identified Material:** {identified_material}")
                st.success(f"**COD Reference ID:** {cod_id}")
                if confidence > 0:
                    st.caption(f"System Confidence Score: {confidence}%")
                
                st.metric(label="Main Peak (2θ):", value=f"{user_main_peak}°")
                st.metric(label="d-spacing (d):", value=f"{d_spacing} A")
                st.metric(label="FWHM (β):", value=f"{fwhm_val}°")
                st.metric(label="Crystallite Size (D):", value=f"{crystallite_size} nm")
            else:
                st.warning("لم يتم العثور على قمم واضحة في ملف العينة.")
        except Exception as e:
            st.error(f"خطأ أثناء معالجة البيانات: {e}")
    else:
        st.warning("بانتظار رفع ملف إكسل لبدء الفحص وفك التلابس التلقائي الشامل...")

with col_right:
    st.header("📊 منحنى حيود الأشعة السينية (XRD Chart)")
    if uploaded_file is not None and 'user_main_peak' in locals():
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(two_theta, intensity, color='#00a8cc', linewidth=1.5, label='Experimental Pattern')
        ax.plot(user_main_peak, user_max_intensity, 'ro', label=f'Main Peak ({user_main_peak}°)')
        ax.set_xlabel("2-Theta (Degrees)")
        ax.set_ylabel("Intensity (a.u.)")
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend()
        st.pyplot(fig)
    else:
        st.info("سيظهر هنا رسم المنحنى البياني التفاعلي فور رفع ملف البيانات بنجاح.")

# ---------------------------------------------------------
# إضافة التزييل السفلي المخصص باسم دكتور مصطفى المسلماوي
# ---------------------------------------------------------
st.markdown("<br><br><hr>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; color: #888888; font-size: 16px; font-weight: bold;'> "
    "تم تطويره بواسطة دكتور مصطفى المسلماوي"
    "</p>", 
    unsafe_allow_html=True
)
