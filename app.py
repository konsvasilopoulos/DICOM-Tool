import io
import zipfile
import pydicom
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="MedPhys DICOM Toolkit",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Open-Source DICOM Toolkit for Medical Physics")
st.markdown("""
A lightweight, open-source web application designed for medical physicists and researchers to quickly inspect 
and securely anonymize DICOM files locally, ensuring patient data privacy.
""")

# Create Tabs for the tools
tab1, tab2 = st.tabs(["🔒 DICOM Anonymizer", "🔍 DICOM Quick Inspector"])

with tab1:
    st.header("Batch DICOM Anonymizer")
    st.markdown("Upload a **ZIP archive** containing your DICOM files. The tool will strip sensitive patient metadata while keeping technical and spatial tags intact.")

    uploaded_zip = st.file_uploader("Upload DICOM ZIP Archive", type=["zip"], key="anon_zip")

    # Anonymization settings
    st.subheader("Anonymization Settings")
    replacement_id = st.text_input("Replacement ID / Patient Name", value="ANON_PATIENT")
    remove_dates = st.checkbox("Remove Birth Dates & Study Dates", value=True)

    if uploaded_zip is not None:
        if st.button("Run Anonymization"):
            try:
                # Handle ZIP in memory
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(uploaded_zip, 'r') as zip_in:
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_out:
                        for filename in zip_in.namelist():
                            if filename.endswith(('.dcm', '.DCM')) or '.' not in filename.split('/')[-1]:
                                file_content = zip_in.read(filename)
                                try:
                                    # Read DICOM from bytes
                                    ds = pydicom.dcmread(io.BytesIO(file_content))
                                    
                                    # Modify Tags
                                    ds.PatientName = replacement_id
                                    ds.PatientID = replacement_id
                                    if remove_dates:
                                        if 'PatientBirthDate' in ds:
                                            ds.PatientBirthDate = ""
                                        if 'StudyDate' in ds:
                                            ds.StudyDate = ""
                                    
                                    if 'InstitutionName' in ds:
                                        ds.InstitutionName = "REDACTED_CLINIC"

                                    # Save to memory buffer
                                    out_bytes = io.BytesIO()
                                    ds.save_as(out_bytes)
                                    zip_out.writestr(filename, out_bytes.getvalue())
                                except Exception:
                                    # If a file inside the zip is not a valid DICOM file
                                    zip_out.writestr(filename, file_content)
                
                zip_buffer.seek(0)
                st.success("Anonymization completed successfully!")
                
                st.download_button(
                    label="📥 Download Anonymized ZIP",
                    data=zip_buffer,
                    file_name="anonymized_dicom_files.zip",
                    mime="application/zip"
                )
            except Exception as e:
                st.error(f"An error occurred during processing: {e}")

with tab2:
    st.header("DICOM Quick Inspector")
    st.markdown("Upload a single DICOM file to inspect its core technical properties (Modality, Matrix Dimensions, Pixel Spacing, etc.).")

    uploaded_dcm = st.file_uploader("Upload DICOM File (.dcm)", type=["dcm", "IMA"], key="inspect_dcm")

    if uploaded_dcm is not None:
        try:
            ds = pydicom.dcmread(uploaded_dcm)
            
            # Extract basic metadata
            info = {
                "Modality": getattr(ds, "Modality", "Unknown"),
                "Patient ID (Anonymized check)": getattr(ds, "PatientID", "N/A"),
                "Study Description": getattr(ds, "StudyDescription", "N/A"),
                "Manufacturer": getattr(ds, "Manufacturer", "N/A"),
                "Rows": getattr(ds, "Rows", "N/A"),
                "Columns": getattr(ds, "Columns", "N/A"),
                "Slice Thickness": getattr(ds, "Slice Thickness", "N/A"),
                "Pixel Spacing": str(getattr(ds, "PixelSpacing", "N/A")),
            }
            
            st.subheader("Technical Summary")
            df_info = pd.DataFrame(list(info.items()), columns=["Parameter", "Value"])
            st.table(df_info)

            # If it's an RT Dose file
            if getattr(ds, "Modality", "") == "RTDOSE":
                st.info("Detected RT Dose file.")
                if hasattr(ds, "DoseGridScaling"):
                    st.write(f"**Dose Grid Scaling Factor:** {ds.DoseGridScaling}")

        except Exception as e:
            st.error(f"Could not read the DICOM file: {e}")
