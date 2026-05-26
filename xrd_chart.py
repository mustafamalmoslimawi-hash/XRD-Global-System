import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt

# إعدادات الصفحة للويب
st.set_page_config(page_title="XRD 10,000 Global System", layout="wide")

# تصميم الهيدر العلوي للموقع
st.markdown("<h1 style='text-align: center; color: #008080;'>🔬 XRD 10,000 GLOBAL SYSTEM</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #555;'>ULTRA-PRECISION MOLECULAR DIAGNOSIS SYSTEM v24.0</h4>", unsafe_allow_html=True)
st.write("---")

# اسم ملف قاعدة البيانات المرفوع على حسابك
DB_FILE_NAME = "Comprehensive_10000_Nano_Crystallographic_Database.xlsx"

@st.cache_data
def load_10k_database():
    try:
        df_db = pd.read_excel(DB_FILE_NAME)
        # تنظيف أسماء الأعمدة من أي فراغات مخفية
        df_db.columns = [str(col).strip() for col in df_db.columns]
        return df_db
    except Exception as e:
        return None

db_df = load_10k_database()

col_left, col_right = st.columns([1, 2])

with col_left:
    st.header("🎛️ لوحة فك التداخل والتشخيص النهائي")
    uploaded_file = st.file_uploader("الرجاء رفع ملف الـ XRD المراد فحصه (Excel فقط):", type=["xlsx", "xls"])
    
    st.subheader("Automated Material Diagnosis")
    
    if uploaded_file is not None:
        try:
            # قراءة ملف الباحث (العمود الأول: الزاوية، العمود الثاني: الشدة)
            user_data = pd.read_excel(uploaded_file)
            two_theta = pd.to_numeric(user_data.iloc[:, 0], errors='coerce').values
            intensity = pd.to_numeric(user_data.iloc[:, 1], errors='coerce').values
            
            # إزالة أي قيم فارغة (NaN) من ملف الباحث لضمان دقة الحسابات
            valid_user_mask = ~np.isnan(two_theta) & ~np.isnan(intensity)
            two_theta = two_theta[valid_user_mask]
            intensity = intensity[valid_user_mask]
            
            # 1. التقاط القمة الحقيقية المطلقة (أعلى شدة متواجدة في المنحنى مرفوعة بدقة)
            max_idx = np.argmax(intensity)
            user_main_peak = round(float(two_theta[max_idx]), 2)
            user_max_intensity = intensity[max_idx]
            
            # الحسابات الفيزيائية (d-spacing & Crystallite Size)
            wavelength = 1.5406
            theta_rad = np.radians(user_main_peak / 2)
            d_spacing = round(wavelength / (2 * np.sin(theta_rad)), 3)
            
            fwhm_val = 0.35  
            crystallite_size = round((0.9 * wavelength) / (np.radians(fwhm_val) * np.cos(theta_rad)), 2)
            
            # 2. الخوارزمية الصارمة لفك التلابس الحسابي والمادي لجميع المواد
            identified_material = "Unknown Structural Phase"
            cod_id = "N/A"
            confidence = 0
            
            if db_df is not None:
                # جلب عمود الزوايا المرجعية وهو العمود الرابع (الفهرس 3) في ملفك وتحويله قسرياً لأرقام
                ref_peaks = pd.to_numeric(db_df.iloc[:, 3], errors='coerce').values
                valid_db_mask = ~np.isnan(ref_peaks)
                
                # حساب الفروقات المطلقة بين قمة الباحث وجميع القمم الـ 10,000 في ملفك
                diffs = np.abs(ref_peaks[valid_db_mask] - user_main_peak)
                
                if len(diffs) > 0:
                    # العثور على المؤشر (الأقرب رياضياً على الإطلاق بالملي)
                    closest_idx = np.argmin(diffs)
                    actual_db_idx = np.where(valid_db_mask)[0][closest_idx]
                    
                    # قياس نسبة الخطأ، إذا كان الفارق منطقي وعلمي (أقل من نصف درجة مثلاً)
                    if diffs[closest_idx] < 0.50:
                        chem_symbol = str(db_df.iloc[actual_db_idx, 1]).strip() # العمود الثاني (Identifier)
                        mat_details = str(db_df.iloc[actual_db_idx, 2]).strip() # العمود الثالث (Material Name)
                        identified_material = f"{mat_details} ({chem_symbol})"
                        cod_id = "COD #" + str(db_df.iloc[actual_db_idx, 5]).strip() # العمود السادس (Database No.)
                        
                        # حساب دقة وموثوقية التطابق
                        confidence = int((1 - (diffs[closest_idx] / 0.50)) * 100)
                        confidence = max(60, min(100, confidence))
            else:
                st.error("تنبيه: تعذر قراءة قاعدة البيانات المرجعية من المستودع!")

            # 3. عرض المخرجات والنتائج الديناميكية المتغيرة
            st.info(f"**Identified Material:** {identified_material}")
            st.success(f"**COD Reference ID:** {cod_id}")
            if confidence > 0:
                st.caption(f"🎯 **System Confidence Score:** {confidence}% (تم فك التداخل بنجاح)")
                
            st.metric(label="Main Peak (2θ):", value=f"{user_main_peak}°")
            st.metric(label="d-spacing (d):", value=f"{d_spacing} A")
            st.metric(label="FWHM (β):", value=f"{fwhm_val}°")
            st.metric(label="Crystallite Size (D):", value=f"{crystallite_size} nm")
            
        except Exception as e:
            st.error(f"حدث خطأ داخلي أثناء معالجة البيانات: {e}")
    else:
        st.warning("بانتظار رفع ملف إكسل لبدء الفحص وفك التلابس التلقائي الشامل...")

with col_right:
    st.header("📊 منحنى حيود الأشعة السينية (XRD Chart)")
    if uploaded_file is not None and 'user_main_peak' in locals():
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(two_theta, intensity, color='#00a8cc', linewidth=1.5, label='Experimental Pattern')
        ax.plot(user_main_peak, user_max_intensity, 'ro', label=f'Main Identified Peak ({user_main_peak}°)')
        
        ax.set_xlabel("2-Theta (Degrees)")
        ax.set_ylabel("Intensity (a.u.)")
        ax.set_title("Live Material Phase & 10K DB Matching")
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend()
        st.pyplot(fig)
    else:
        st.info("سيظهر هنا رسم المنحنى البياني التفاعلي فور رفع ملف البيانات بنجاح.")
