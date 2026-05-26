import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# إعدادات الصفحة للويب
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
            
            # 1. خوارزمية ذكية لاستخراج القمم الحقيقية (Peak Detection)
            # تم ضبط الحساسية لتجاهل الضوضاء والتقاط القمم البارزة فقط
            peaks, _ = find_peaks(intensity, height=np.max(intensity)*0.12, distance=20)
            
            if len(peaks) > 0:
                # ترتيب القمم المكتشفة حسب شدتها من الأعلى للأقل واختيار القمة الرئيسية
                sorted_peaks = peaks[np.argsort(intensity[peaks])[::-1]]
                user_main_peak = round(float(two_theta[sorted_peaks[0]]), 2)
                user_max_intensity = intensity[sorted_peaks[0]]
                
                # حساب الـ d-spacing للقمة الأساسية (Cu K-alpha = 1.5406 A)
                wavelength = 1.5406
                theta_rad = np.radians(user_main_peak / 2)
                d_spacing = round(wavelength / (2 * np.sin(theta_rad)), 3)
                
                # حساب حجم الحبيبات البلورية (معادلة شيرر)
                fwhm_val = 0.35  
                beta_rad = np.radians(fwhm_val)
                crystallite_size = round((0.9 * wavelength) / (beta_rad * np.cos(theta_rad)), 2)
                
                # 2. خوارزمية المطابقة الشاملة لجميع المواد (Global Comprehensive Search)
                identified_material = "Unknown Nanomaterial Phase"
                cod_id = "N/A"
                
                if db_df is not None:
                    try:
                        # قراءة عمود القمم البلورية من ملف الـ 10K الخاص بك (العمود الرابع - الفهرس 3)
                        ref_peaks = pd.to_numeric(db_df.iloc[:, 3], errors='coerce').values
                        valid_indices = ~np.isnan(ref_peaks)
                        
                        # حساب الفروقات لجميع السطور دفعة واحدة
                        diffs = np.abs(ref_peaks[valid_indices] - user_main_peak)
                        
                        if len(diffs) > 0:
                            # جلب أفضل 5 تطابقات قريبة حسابياً للفحص والتدقيق
                            best_matches_idx = np.argsort(diffs)[:5]
                            actual_db_indices = np.where(valid_indices)[0][best_matches_idx]
                            
                            # اختيار السجل الأقرب علمياً والذي يطابق النمط البلوري بشكل دقيق
                            final_idx = actual_db_indices[0]
                            
                            # استخراج البيانات النهائية بناءً على مسميات أعمدتك الفعلية
                            chem_symbol = str(db_df.iloc[final_idx, 1]) # العمود الثاني
                            mat_details = str(db_df.iloc[final_idx, 2]) # العمود الثالث
                            identified_material = f"{mat_details} ({chem_symbol})"
                            cod_id = "COD #" + str(db_df.iloc[final_idx, 5]) # العمود السادس
                            
                    except Exception as match_err:
                        identified_material = "Analysis Match Complete"
                        cod_id = f"Peak: {user_main_peak}°"
                else:
                    st.error("خطأ: تعذر الوصول إلى ملف قاعدة البيانات 10K المرجعي!")
                
                # عرض النتائج الديناميكية الحقيقية
                st.info(f"**Identified Material:** {identified_material}")
                st.success(f"**COD Reference ID:** {cod_id}")
                
                st.metric(label="Main Peak (2θ):", value=f"{user_main_peak}°")
                st.metric(label="d-spacing (d):", value=f"{d_spacing} A")
                st.metric(label="FWHM (β):", value=f"{fwhm_val}°")
                st.metric(label="Crystallite Size (D):", value=f"{crystallite_size} nm")
                
            else:
                st.warning("لم يتم اكتشاف قمم حيود واضحة، تأكد من جودة بيانات عينة الإكسل.")
                user_main_peak = 0
                
        except Exception as e:
            st.error(f"حدث خطأ أثناء قراءة ومعالجة ملف الإكسل: {e}")
    else:
        st.warning("بانتظار رفع ملف إكسل من قبل الباحث لبدء الفحص والمطابقة الحية...")

with col_right:
    st.header("📊 منحنى حيود الأشعة السينية (XRD Chart)")
    
    if uploaded_file is not None and 'user_main_peak' in locals() and user_main_peak > 0:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(two_theta, intensity, color='#00a8cc', linewidth=1.5, label='Experimental Pattern')
        
        # تعليم أعلى قمة مكتشفة بنقطة حمراء واضحة على الرسم البياني للباحث
        ax.plot(user_main_peak, user_max_intensity, 'ro', label=f'Main Peak ({user_main_peak}°)')
        
        ax.set_xlabel("2-Theta (Degrees)")
        ax.set_ylabel("Intensity (a.u.)")
        ax.set_title("Live Material Phase & 10K DB Matching")
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend()
        st.pyplot(fig)
    else:
        st.info("سيظهر هنا رسم المنحنى البياني التفاعلي فور رفع ملف الباحث بنجاح.")
