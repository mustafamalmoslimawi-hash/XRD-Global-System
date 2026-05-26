import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # منع تداخل مكتبة الرسم مع نظام نوافذ سطح المكتب القديم
import matplotlib.pyplot as plt

# تعيين إعدادات الصفحة لتكون مريحة واحترافية للباحث
st.set_page_config(page_title="XRD 10,000 Global System", layout="wide")

# تصميم الهيدر العلوي يشبه واجهتك الأصلية الممتازة
st.markdown("<h1 style='text-align: center; color: #008080;'>🔬 XRD 10,000 GLOBAL SYSTEM</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #555;'>XRD EXPERT SYSTEM - 10,000 ULTIMATE DATABASE v21.0</h4>", unsafe_allow_html=True)
st.write("---")

# وظيفة تحميل قاعدة البيانات المرجعية الـ 10K في الخلفية مرة واحدة لتسريع التطبيق
@st.cache_data
def load_reference_database():
    try:
        db_path = "Comprehensive_10000_Nano_Crystallographic_Database.xlsx"
        df_db = pd.read_excel(db_path)
        return df_df
    except Exception as e:
        return None

# محاولة تحميل قاعدة البيانات الخاصة بك
db_df = load_reference_database()

# تقسيم الشاشة إلى عمودين (الجانب الأيسر للبيانات والتحليل، والجانب الأيمن للرسم البياني)
col_left, col_right = st.columns([1, 2])

with col_left:
    st.header("🎛️ لوحة التحكم والتشخيص")
    
    # زر رفع ملف الإكسل المخصص للباحث
    uploaded_file = st.file_uploader("الرجاء رفع ملف الـ XRD (صيغة Excel فقط):", type=["xlsx", "xls"])
    
    st.subheader("Automated Material Diagnosis")
    
    if uploaded_file is not None:
        try:
            # قراءة ملف الباحث
            user_data = pd.read_excel(uploaded_file)
            
            # نفترض أن العمود الأول 2-Theta والثاني الشدة
            two_theta = user_data.iloc[:, 0].values
            intensity = user_data.iloc[:, 1].values
            
            # ----------------------------------------------------
            #  ملاحظة: هنا تجري العمليات الحسابية المأخوذة من خوارزميتك الأصلية
            #  كمثال توضيحي بناءً على الصورة المرفقة من تطبيقك المبدع:
            # ----------------------------------------------------
            
            identified_material = "Zinc Oxide (Wurtzite) (Doped Structural Variant Type-1)"
            cod_id = "COD #2307928"
            main_peak = 36.26
            d_spacing = 2.477
            fwhm = 0.384
            crystallite_size = 21.81
            
            # عرض النتائج بنفس المسميات في تطبيقك الأصلي
            st.info(f"**Identified Material:** {identified_material}")
            st.success(f"**COD Reference ID:** {cod_id}")
            
            st.metric(label="Main Peak (2θ):", value=f"{main_peak}°")
            st.metric(label="d-spacing (d):", value=f"{d_spacing} A")
            st.metric(label="FWHM (β):", value=f"{fwhm}°")
            st.metric(label="Crystallite Size (D):", value=f"{crystallite_size} nm")
            
        except Exception as e:
            st.error(f"حدث خطأ أثناء معالجة الملف الحسابي: {e}")
    else:
        st.warning("بانتظار قيام الباحث برفع ملف الإكسل لبدء التشخيص التلقائي...")
        
        # قيم افتراضية فارغة قبل الرفع
        st.text("Identified Material: --")
        st.text("COD Reference ID: --")

with col_right:
    st.header("📊 منحنى حيود الأشعة السينية (XRD Chart)")
    
    if uploaded_file is not None:
        # بناء الرسم البياني ليعرض على المتصفح أونلاين بشكل نظيف
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(two_theta, intensity, color='#00a8cc', linewidth=1.5)
        
        # إضافة النقاط الحمراء على القمم كمثال من تطبيقك الأصلي
        # (يمكنك ربط نقاطك المحددة من دالة peak detection هنا)
        # ax.plot([31.8, 34.4, 36.3], [1800, 1650, 2600], 'ro') 
        
        ax.set_xlabel("2-Theta (Degrees)")
        ax.set_ylabel("Intensity (a.u.)")
        ax.set_title("10K DB Match Visualization")
        ax.grid(True, linestyle='--', alpha=0.5)
        
        # عرض الرسمة داخل المتصفح بأمان عبر Streamlit
        st.pyplot(fig)
    else:
        st.info("سيظهر هنا المخطط البياني التفاعلي فور رفع ملف البيانات.")
