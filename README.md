# 🏥 Open-Source DICOM Toolkit for Medical Physics

A lightweight, open-source web application built with Python and Streamlit, designed for medical physicists, researchers, and clinical engineers. It provides a secure, local interface for DICOM file inspection, advanced image processing, quantitative QA/QC analysis, de-identification compliance, and batch extraction of Diagnostic Reference Levels (DRLs / ΔΕΑ).

## 🌐 Live Application
* **Access the web app here:** [MedPhys DICOM Toolkit](https://dicom-tool-fcpymgt4csqtakjfw2d35r.streamlit.app/)

## 🚀 Key Features

* **🔒 Batch DICOM Anonymizer:** 
  * Local de-identification of DICOM ZIP archives preserving technical tags.
  * Extended PHI scrubbing (physicians, operators, accession numbers, study IDs) following DICOM PS3.15 Annex E.
  * Instant generation and download of HIPAA/GDPR compliance audit reports (`.csv`).

* **🔍 Inspector & Diagnostic Viewer:** 
  * **Modality-Aware Engine:** Automatic mode switching between Hounsfield Units (CT) and Pixel Intensities (Radiography / Mammography).
  * **Image Enhancement:** Brightness, Contrast, Gamma, Sharpness, Unsharp Mask, Median Filter, and Histogram Equalization.
  * **Multi-ROI QC:** Interactive 5-point ROI evaluation (Center, Top, Bottom, Left, Right) in circular or rectangular geometries.
  * **Spatial Resolution (ESF & MTF):** Line Intensity Profiling extracting Edge Spread Function and Modulation Transfer Function with automatic $MTF_{50}$ and $MTF_{10}$ metrics.
  * **Quality Control Checks:** Real-time SNR, CNR, percentage field uniformity, and CT water calibration checks ($0 \pm 4\text{ HU}$).
  * **DICOM Editor:** In-place header editing and download of updated `.dcm` files.

* **📊 Batch DRLs & Dataset CSV Report Generator:** 
  * **Radiography (DX / CR / DEXA):** Tube parameters (kVp, mA, s, mAs), SID, physical **Field Size at detector plane (mm/cm)**, DAP/KAP, and Entrance Dose.
  * **Mammography (MG):** **Mean Glandular Dose (MGD)**, **ESAK**, compressed breast thickness, compression force, target/filter combinations, and projections (CC/MLO).
  * **Computed Tomography (CT Volumes):** Patient/series grouping, Z-coverage, **$CTDI_{vol}$**, **Scan DLP**, **Total DLP**, calculated **Scan Length** ($\text{DLP}/\text{CTDI}_{\text{vol}}$), Helical mode detection, and Head (16 cm) vs. Body (32 cm) categorization.

## 🛡️ Privacy & Security
All computations are executed locally in the browser session. No medical imaging data or PHI is stored or transmitted externally.

## 🛠️ Tech Stack
* **Python** (Core computing)
* **Streamlit** (Web application framework)
* **Pydicom** (DICOM dataset processing)
* **NumPy / SciPy / Matplotlib** (Image mathematics & plotting)
* **Pillow (PIL)** (Spatial filtering)
* **Pandas** (Tabular summary structures & CSV reports)

## 📄 License
This project is open-source and distributed under the [MIT License](LICENSE).

---
**Developer / Creator:** Konstantinos G. Vasilopoulos *(Medical Physicist & Researcher)* | ✉️ `kostasvasilopoulosgr@yahoo.com`
