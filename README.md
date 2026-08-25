# 🏥 Open-Source DICOM Toolkit for Medical Physics

A lightweight, open-source web application built with Python and Streamlit, designed for medical physicists, researchers, and students. This tool provides a simple, secure local interface for quick DICOM file inspection and batch anonymization.

## 🚀 Features

* **🔒 Batch DICOM Anonymizer:** 
  * Upload a ZIP archive of DICOM files.
  * Automatically strips sensitive patient metadata (Patient Name, ID, Birth Date, Study Date) while keeping technical and spatial tags (Image Position, Slice Thickness, etc.) completely intact.
  * Download the processed files instantly as a clean ZIP archive.
* **🔍 DICOM Quick Inspector:** 
  * Upload individual DICOM files (`.dcm`, `.IMA`) to instantly view essential technical parameters.
  * Displays Modality, Matrix Dimensions, Pixel Spacing, Manufacturer, and specific metadata (e.g., Dose Grid Scaling for RT Dose files).

---
🛡️ Privacy & Security
All processing is performed locally in your session environment. No patient health information (PHI) is transmitted, stored, or shared externally.

📄 License
This project is open-source and available under the MIT License.

## 🛠️ Tech Stack

* **Python** (Core processing)
* **Streamlit** (Web user interface)
* **Pydicom** (DICOM file parsing and manipulation)
* **Pandas** (Data structuring and tabular display)
