# XRD-Global-System# 
🔬 XRD 10,000 Global System (Automated Nano Material Diagnosis)

An expert system for automated nanomaterial phase identification and X-ray diffraction (XRD) analysis, provided free of charge to support researchers, material scientists, and postgraduate students worldwide.

This interactive web platform allows users to upload their experimental XRD data via **Excel files**. The system automatically processes the data, matches peak profiles with a comprehensive built-in database of 10,000+ structural variants (e.g., Zinc Oxide Wurtzite), and instantly calculates key crystallographic parameters.

---

## ✨ Key Features
* **Smart Excel Parser:** Directly processes `.xlsx` and `.xls` files.
* **Automated Phase Identification:** Matches experimental diffraction peaks with built-in reference cards (COD Reference IDs).
* **Crystallographic Calculations:** Automatically calculates FWHM, d-spacing, and Crystallite Size ($D$) using standard physical formulas (Scherrer Equation).
* **Interactive XRD Charting:** Visualizes the diffraction pattern (Intensity vs. 2-Theta) with zoom, pan, and hover capabilities for precise peak inspection.
* **100% Free & Open-Access:** Built purely to accelerate academic research in nanotechnology.

---

## 📊 Required Excel File Format (Columns Layout)

To ensure the automated system processes your data without errors, please format your uploaded Excel sheet strictly as follows:

* **Column 1 (First Column):** 2-Theta values (Degrees, e.g., $20^\circ$ to $80^\circ$).
* **Column 2 (Second Column):** Intensity values (Arbitrary Units, a.u.).

> ⚠️ **Important Note:** Do not include any textual headers, metadata, or blank rows at the very top of the spreadsheet. The data rows should start directly from the first row so the Python engine can parse the columns correctly.

---

## 🛠️ Built With
* **Python** - Core data analytics and peak detection algorithms.
* **Streamlit** - Web application framework.
* **Pandas & NumPy** - Matrix manipulation and data cleaning.
* **Plotly** - High-fidelity interactive charts.
