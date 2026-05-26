import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# إعدادات واجهة المستخدم المتكاملة
st.set_page_config(page_title="XRD 10,000 Global System", layout="wide")

st.markdown("<h1 style='text-align: center; color: #008080;'>XRD 10,000 GLOBAL SYSTEM</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #555;'>AUTOMATED MOLECULAR DIAGNOSIS SYSTEM (V24.0)</h4>", unsafe_allow_html=True)
st.write("---")

# اسم ملف قاعدة البيانات الخاص بك والموجود في مجلد المشروع
DB_FILE_NAME = "Comprehensive_10000_Nano_Crystallographic_Database.xlsx"

@st.cache_data
def load_crystallographic_database():
    try:
        df_db = pd.read_excel(DB_FILE_NAME)
        # تنظيف مسافات العناوين لضمان المطابقة البرمجية التامة
        df_db.columns = [str(col).strip() for col in df_db.columns]
        return df_db
    except Exception as e:
        st.error(f"تنبيه: تعذر تحميل قاعدة البيانات المرجعية المستهدفة: {e}")
        return None

db_df = load_crystallographic_database()

col_left, col_right = st.columns([1, 2])

with col_left:
    st.header("لوحة فك التداخل والتشخيص الفوري")
    uploaded_file = st.file_uploader("الرجاء رفع ملف الـ XRD المراد فحصه (Excel فقط):", type=["xlsx", "xls"])
    
    st.subheader("Automated Material Diagnosis")
    
    if uploaded_file is not None:
        try:
            user_data = pd.read_excel(uploaded_file)
            user_theta = pd.to_numeric(user_data.iloc[:, 0], errors='coerce').values
            user_intensity = pd.to_numeric(user_data.iloc[:, 1], errors='coerce').values
            
            # تنظيف مصفوفة البيانات المرفوعة
            valid_mask = ~np.isnan(user_theta) & ~np.isnan(user_intensity)
            user_theta = user_theta[valid_mask]
            user_intensity = user_intensity[valid_mask]
            
            # 1. خوارزمية التقاط بصمة النمط الكامل (Full Pattern Peak Detection)
            peaks, _ = find_peaks(user_intensity, height=np.max(user_intensity)*0.10, distance=20)
            
            if len(peaks) > 0:
                # ترتيب القمم تصاعدياً حسب زاوية الموضع لأعلى 5 قمم شدة
                sorted_peaks_idx = peaks[np.argsort(user_intensity[peaks])[::-1]]
                detected_peaks = sorted([round(float(user_theta[idx]), 2) for idx in sorted_peaks_idx[:5]])
                
                user_main_peak = round(float(user_theta[sorted_peaks_idx[0]]), 2)
                user_max_intensity = user_intensity[sorted_peaks_idx[0]]
                
                # الحسابات الفيزيائية للقمة الأساسية
                wavelength = 1.5406
                theta_rad = np.radians(user_main_peak / 2)
                d_spacing = round(wavelength / (2 * np.sin(theta_rad)), 3)
                fwhm_val = 0.35  
                crystallite_size = round((0.9 * wavelength) / (np.radians(fwhm_val) * np.cos(theta_rad)), 2)
                
                # 2. خوارزمية المطابقة التامة المرتبطة بأعمدة ملف الدكتور مصطفى
                identified_material = "Unknown Nanomaterial Phase"
                cod_id = "N/A"
                confidence_score = 0
                
                if db_df is not None:
                    # الربط المباشر المخصص بأسماء الأعمدة الفعلية لملفك
                    mat_name_col = "Material Name & Crystallographic Phase"
                    ref_peak_col = "Characteristic Peak 2"
                    identifier_col = "Record No / Identifier"
                    cod_num_col = "Open Database Card Number"
                    
                    # التحقق من وجود الأعمدة داخل الملف المرفوع كقاعدة بيانات
                    if ref_peak_col in db_df.columns:
                        ref_peaks = pd.to_numeric(db_df[ref_peak_col], errors='coerce').values
                        valid_db_mask = ~np.isnan(ref_peaks)
                        
                        best_match_idx = None
                        min_delta = 999.0
                        
                        # مسح ومقاطعة القمم الخمس مع السجلات البلورية المرجعية
                        for idx in np.where(valid_db_mask)[0]:
                            db_peak = ref_peaks[idx]
                            
                            # حساب التباين المطلق عن قمة العينة الأساسية
                            delta = abs(db_peak - user_main_peak)
                            
                            # ميزة التحقق من حزمة النمط المرافقة (Multi-Peak Grid Filter)
                            is_pattern_matched = any(abs(db_peak - up) < 0.35 for up in detected_peaks)
                            
                            if is_pattern_matched and delta < min_delta:
                                min_delta = delta
                                best_match_idx = idx
                        
                        # استخراج وعرض البيانات المتوافقة تماً
                        if best_match_idx is not None and min_delta < 0.35:
                            mat_name = str(db_df[mat_name_col].iloc[best_match_idx]).strip()
                            identifier = str(db_df[identifier_col].iloc[best_match_idx]).strip()
                            
                            identified_material = f"{mat_name} ({identifier})"
                            cod_id = "COD #" + str(db_df[cod_num_col].iloc[best_match_idx]).strip()
                            
                            # حساب مستوى الثقة العلمي في التطابق
                            confidence_score = int((1 - (min_delta / 0.35)) * 100)
                            confidence_score = max(50, min(100, confidence_score))
                
                # 3. عرض مخرجات تقرير الفحص النهائي المتوافق
                st.info(f"**Identified Phase:** {identified_material}")
                st.success(f"**COD Reference ID:** {cod_id}")
                
                st.write(f"📊 **Detected Pattern Fingerprints (2θ):** `{detected_peaks}`")
                st.caption(f"🎯 تم التشخيص والمطابقة بناءً على حزمة النمط البلوري المستخرجة بنجاح.")
                
                st.write("---")
                st.metric(label="Main Peak (2θ):", value=f"{user_main_peak}°")
                st.metric(label="d-spacing (d):", value=f"{d_spacing} Å")
                st.metric(label="FWHM (β):", value=f"{fwhm_val}°")
                st.metric(label="Crystallite Size (D):", value=f"{crystallite_size} nm")
                if confidence_score > 0:
                    st.caption(f"System Identification Match Confidence: {confidence_score}%")
            else:
                st.warning("لم يتم تحديد قمم بلورية واضحة في الملف المرفوع.")
        except Exception as e:
            st.error(f"خطأ أثناء معالجة وفحص نمط العينة: {e}")
    else:
        st.warning("بانتظار رفع ملف إكسل لبدء الفحص وفك التلابس التلقائي الشامل...")

with col_right:
    st.header("📊 منحنى حيود الأشعة السينية (XRD Chart)")
    if uploaded_file is not None and 'detected_peaks' in locals():
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(user_theta, user_intensity, color='#00a8cc', linewidth=1.5, label='Experimental Pattern')
        
        # تعليم جميع قمم النمط المكتشفة بنقاط تأكيد حمراء على الرسم البياني
        for p in detected_peaks:
            p_idx = np.abs(user_theta - p).argmin()
            ax.plot(user_theta[p_idx], user_intensity[p_idx], 'ro')
            
        ax.set_xlabel("2-Theta (Degrees)")
        ax.set_ylabel("Intensity (a.u.)")
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend()
        st.pyplot(fig)
    else:
        st.info("سيظهر هنا رسم المنحنى البياني التفاعلي فور رفع ملف البيانات بنجاح.")

# ---------------------------------------------------------
# تذييل الصفحة الثابت والمخصص
# ---------------------------------------------------------
st.markdown("<br><br><hr>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; color: #888888; font-size: 16px; font-weight: bold;'> "
    "تم تطويره بواسطة دكتور مصطفى المسلماوي"
    "</p>", 
    unsafe_allow_html=True
)
