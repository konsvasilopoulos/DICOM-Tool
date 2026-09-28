# 🏥 Open-Source DICOM Toolkit for Medical Physics

A lightweight, open-source web application built with Python and Streamlit, designed for medical physicists, researchers, and students. It provides a secure, local interface for DICOM file inspection, advanced image processing, quantitative QA/QC analysis, dosimetric batch extraction, and clinical protocol auditing.

## 🚀 Key Features

* **🔒 Batch DICOM Anonymizer:** 
  * Upload and process ZIP archives of DICOM files.
  * Automatically strips sensitive patient metadata (PHI) while preserving technical, spatial tags, and internal series consistency.
  * **Extended PHI & UID Management:** Optional scrubbing of operators, physicians, study/accession IDs, alongside cryptographic UID pseudonymization compliant with **DICOM Standard PS3.15 Annex E**.
  * **Compliance Audit Trail:** Instant generation and download of detailed de-identification audit reports (`.csv`) for clinical trials and GDPR/HIPAA verification.

* **🔍 Inspector & 3D Diagnostic Viewer:** 
  * **Modality-Aware Processing:** Automatically detects modalities (CT with Hounsfield Units, Radiography/Mammography with Raw Intensities).
  * **3D Volume Projections:** Dynamic Maximum (MIP) and Minimum (MinIP) Intensity Projections across Axial, Coronal, and Sagittal planes for CT volumes.
  * **Image Enhancement:** Brightness, Contrast, Gamma, Sharpness, Unsharp Mask, Median Filter, and Histogram Equalization.
  * **Multi-ROI Analysis:** Interactive coordinate and shape adjustments (Circle/Square) for Center, Top, Bottom, Left, and Right ROIs, including automatic physical area ($mm^2$) calculations.
  * **Spatial Resolution (ESF & MTF):** Line Intensity Profiling extracting Edge Spread Function and Modulation Transfer Function with automatic $MTF_{50}$ and $MTF_{10}$ metrics.
  * **Quality Control Checks:** Real-time SNR, CNR, percentage field uniformity, CT water calibration ($0 \pm 4\text{ HU}$), Linearity & Sensitometry ($\rho_e$), Slice Thickness (FWHM), 2D Noise Power Spectrum (NPS), Light/Radiation Field Alignment (DX/CR), and 1cm Geometric Distortion Grid.
  * **DICOM Editor:** In-place header editing and download of updated `.dcm` files.

* **📊 Batch CSV Report Generator (DRLs):** 
  * Aggregate multiple DICOM series per patient and export comprehensive dosimetric summary reports as CSV files for Diagnostic Reference Levels (DRLs).
  * **Radiography (DX/CR):** kVp, mAs, SID, Field Size, Entrance Dose, DAP/KAP.
  * **Mammography (MG):** MGD, ESAK, breast thickness, compression force, target/filter, projections.
  * **Computed Tomography (CT):** Z-coverage, CTDIvol, Scan DLP, Total DLP, Scan Length, Head/Body categorization.
  * **Fluoroscopy & Interventional:** Parses Radiation Dose Structured Reports (RDSR) to extract Fluoroscopy Time, Cumulative Air Kerma, and DAP.
  * **Dental & CBCT:** Tube parameters, Entrance Dose, DAP/KAP, CTDIvol, DLP.

* **⚖️ Protocol Auditor & Comparator:** 
  * Upload your department's "Gold Standard" reference DICOM alongside a clinical scan.
  * Automatically cross-checks core geometric and dosimetric tags (kVp, mAs, Slice Thickness, CTDIvol, Pixel Spacing, etc.).
  * Generates a color-coded Pass/Fail compliance table and calculates an overall **Protocol Compliance Score (%)** to detect unauthorized protocol deviations.

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
