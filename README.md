# 🏥 Open-Source DICOM Toolkit for Medical Physics

A lightweight, open-source web application built with Python and Streamlit, designed for medical physicists, researchers, and students. It provides a secure, local interface for DICOM file inspection, advanced image processing, quantitative QA/QC analysis, and batch anonymization.

## 🚀 Key Features

* **🔒 Batch DICOM Anonymizer:** 
  * Upload and process ZIP archives of DICOM files.
  * Automatically strips sensitive patient metadata while preserving technical and spatial tags.
  * Instant download of anonymized archives.

* **🔍 Inspector & Diagnostic Viewer:** 
  * **Modality-Aware Processing:** Automatically detects modalities (CT with Hounsfield Units, Radiography/Mammography with Raw Intensities).
  * **Quick Adjustments & Filters:** Real-time controls for Brightness, Contrast, Gamma, Sharpness, and advanced spatial filters (Unsharp Mask, Median Filter, Histogram Equalization).
  * **Multi-ROI Analysis:** Interactive coordinate and shape adjustments (Circle/Square) for Center, Top, Bottom, Left, and Right ROIs.
  * **Distance Ruler & Calibration:** Automatic DICOM `PixelSpacing` detection with manual override for accurate physical measurements in millimeters (mm).
  * **Line Intensity Profile (ESF & MTF):** Spatial resolution analysis extracting Edge Spread Function (ESF) and Modulation Transfer Function (MTF) along custom line profiles with automatic $MTF_{50}$ and $MTF_{10}$ metrics.
  * **Advanced SNR & CNR Metrics:** Quantitative quality control metrics evaluating signal-to-noise and contrast-to-noise ratios across active ROIs.
  * **Uniformity & Noise Analyzer:** Automated evaluation of field uniformity percentage, system noise (SD), and CT water calibration Pass/Fail checks.
  * **DICOM Header Editor & Fixer:** Live metadata correction and direct download of updated `.dcm` files.

* **📊 Batch CSV Report Generator:** 
  * Aggregate multiple DICOM series per patient, calculate slice counts, and export comprehensive summary reports as CSV files.

## 🛡️ Privacy & Security
All processing is performed locally in your session environment. No patient health information (PHI) is transmitted, stored, or shared externally.

## 🛠️ Tech Stack
* **Python** (Core processing & scientific computing)
* **Streamlit** (Web user interface)
* **Pydicom** (DICOM parsing & metadata editing)
* **NumPy / SciPy / Matplotlib** (Image analysis & plotting)
* **Pillow (PIL)** (Spatial image filtering)

## 🌐 Live Application
* **Access the web app here:** [MedPhys DICOM Toolkit](https://dicom-tool-fcpymgt4csqtakjfw2d35r.streamlit.app/)

## 📄 License
This project is open-source and available under the MIT License.

---
**Developer / Creator:** Konstantinos G. Vasilopoulos *(Medical Physicist & Researcher)* | ✉️ `kostasvasilopoulosgr@yahoo.com`
