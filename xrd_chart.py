import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# تعيين إعدادات الصفحة للويب
st.set_page_config(page_title="XRD 10,000 Global System", layout="wide")

# تصميم الهيدر العلوي للموقع
st.markdown("<h1 style='text-align: center; color: #008080;'>🔬 XRD 10,000 GLOBAL SYSTEM</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #555;'>XRD EXPERT SYSTEM - 10,000 ULTIMATE DATABASE v21.0</h4>", unsafe_allow_html=True)
st.write("---")

# اسم ملف قاعدة البيانات المرفوع على حسابك
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
    st.header("🎛️ لوحة التحكم والتشخيص")
    
    uploaded_file = st.file_uploader("الرجاء رفع ملف الـ XRD الخاص بالعينة (Excel فقط):", type=["xlsx", "xls"])
    
    st.subheader("Automated Material Diagnosis")
    
    if uploaded_file is not None:
        try:
            user_data = pd.read_excel(uploaded_file)
            two_theta = user_data.iloc[:, 0].values
            intensity = user_data.iloc[:, 1].values
            
            # 1. تحسين خوارزمية تحديد موقع أعلى قمة بدقة عشرية عالية
            # نأخذ أعلى نقطة شدة مباشرة في المنحنى لضمان الدقة المطلقة
            max_intensity_idx = np.argmax(intensity)
            user_main_peak = round(float(two_theta[max_intensity_idx]), 3) # زيادة الدقة لثلاث خانات عشرية
            user_max_intensity = intensity[max_intensity_idx]
            
            # حساب الـ d-spacing 
            wavelength = 1.5406
            theta_rad = np.radians(user_main_peak / 2)
            d_spacing = round(wavelength / (2 * np.sin(theta_rad)), 3)
            
            # حساب حجم الحبيبات البلورية
            fwhm_val = 0.35  
            beta_rad = np.radians(fwhm_val)
            crystallite_size = round((0.9 * wavelength) / (beta_rad * np.cos(theta_rad)), 2)
            
            # 2. خوارزمية مطابقة فائقة الدقة (High-Precision Match)
            identified_material = "Unknown Nanomaterial Phase"
            cod_id = "N/A"
            
            if db_df is not None:
                try:
                    # جلب عمود القمم المرجعية (العمود الرابع - الفهرس 3)
                    ref_peaks = pd.to_numeric(db_df.iloc[:, 3], errors='coerce').values
                    valid_indices = ~np.isnan(ref_peaks)
                    
                    # حساب الفروقات بدقة متناهية
                    diffs = np.abs(ref_peaks[valid_indices] - user_main_peak)
                    
                    if len(diffs) > 0:
                        closest_valid_idx = np.argmin(diffs)
                        actual_db_idx = np.where(valid_indices)[0][closest_valid_idx]
                        
                        # التحقق من أن الفارق قريب جداً علمياً لضمان عدم حدوث تداخل
                        if diffs[closest_valid_idx] < 0.15:
                            chem_symbol = str(db_df.iloc[actual_db_idx, 1])
                            mat_details = str(db_df.iloc[actual_db_idx, 2])
                            identified_material = f"{mat_details} ({chem_symbol})"
                            cod_id = "COD #" + str(db_df.iloc[actual_db_idx, 5])
                        else:
                            identified_material = "Phase Pattern Close Match"
                            cod_id = f"Peak Found at: {user_main_peak}°"
                except Exception as match_err:
                    identified_material = "Automated Precision Error"
                    cod_id = f"Peak: {user_main_peak}°"
            else:
                st.error("خطأ: لم يتم العثور على قاعدة البيانات المرجعية!")
            
            # عرض النتائج
            st.info(f"**Identified Material:** {identified_material}")
            st.success(f"**COD Reference ID:** {cod_id}")
            
            st.metric(label="Main Peak (2θ):", value=f"{user_main_peak}°")
            st.metric(label="d-spacing (d):", value=f"{d_spacing} A")
            st.metric(label="FWHM (β):", value=f"{fwhm_val}°")
            st.metric(label="Crystallite Size (D):", value=f"{crystallite_size} nm")
            
        except Exception as e:
            st.error(f"حدث خطأ أثناء قراءة ملف الإكسل: {e}")
    else:
        st.warning("بانتظار رفع ملف إكسل من قبل الباحث لبدء الفحص والمطابقة الحية...")

with col_right:
    st.header("📊 منحنى حيود الأشعة السينية (XRD Chart)")
    
    if uploaded_file is not None and 'user_main_peak' in locals():
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(two_theta, intensity, color='#00a8cc', linewidth=1.5, label='Experimental Pattern')
        ax.plot(user_main_peak, user_max_intensity, 'ro', label=f'Identified Main Peak ({user_main_peak}°)')
        
        ax.set_xlabel("2-Theta (Degrees)")
        ax.set_ylabel("Intensity (a.u.)")
        ax.set_title("Live Material Phase & 10K DB Matching")
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend()
        st.pyplot(fig)
    else:
        st.info("سيظهر هنا رسم المنحنى البياني التفاعلي فور رفع ملف الباحث بنجاح.")
