import io
import zipfile
import pydicom
from pydicom.dataset import Dataset, FileDataset
import streamlit as st
import pandas as pd
import datetime

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

# Helper function to generate a dummy/demo DICOM file for testing
def generate_demo_dicom():
    file_meta = pydicom.dataset.FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = pydicom.uid.UID('1.2.840.10008.5.1.4.1.1.2') # CT Image Storage
    file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
    file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian

    ds = FileDataset(None, {}, file_meta=file_meta, preamble=b"\0" * 128)
    
    # Add dummy patient and technical tags
    ds.PatientName = "DOE^JOHN"
    ds.PatientID = "12345678"
    ds.PatientBirthDate = "19800101"
    ds.StudyDate = datetime.datetime.now().strftime("%Y%m%d")
    ds.Modality = "CT"
    ds.Manufacturer = "DEMO_VENDOR"
    ds.StudyDescription = "Routine Head CT Test"
    ds.Rows = 512
    ds.Columns = 512
    ds.SliceThickness = "2.5"
    ds.PixelSpacing = [0.5, 0.5]
    ds.InstitutionName = "UNIVERSITY HOSPITAL"
    
    out_bytes = io.BytesIO()
    ds.is_little_endian = True
    ds.is_implicit_VR = False
    ds.save_as(out_bytes)
    out_bytes.seek(0)
    return out_bytes.getvalue()

# Create Tabs for the tools
tab1, tab2 = st.tabs(["🔒 DICOM Anonymizer", "🔍 DICOM Quick Inspector"])

with tab1:
    st.header("Batch DICOM Anonymizer")
    st.markdown("Upload a **ZIP archive** containing your DICOM files, or generate a demo ZIP file to test the tool instantly.")

    # Demo generator section
    with st.expander("🧪 Don't have DICOM files? Generate Test Data"):
        if st.button("Generate Demo DICOM ZIP"):
            demo_dcm_bytes = generate_demo_dicom()
            demo_zip_buffer = io.BytesIO()
            with zipfile.ZipFile(demo_zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_out:
                zip_out.writestr("demo_patient_scan.dcm", demo_dcm_bytes)
            demo_zip_buffer.seek(0)
            
            st.success("Demo ZIP generated successfully!")
            st.download_button(
                label="📥 Download Demo ZIP",
                data=demo_zip_buffer,
                file_name="demo_dicom_files.zip",
                mime="application/zip"
            )

    uploaded_zip = st.file_uploader("Upload DICOM ZIP Archive", type=["zip"], key="anon_zip")

    # Anonymization settings
    st.subheader("Anonymization Settings")
    replacement_id = st.text_input("Replacement ID / Patient Name", value="ANON_PATIENT")
    remove_dates = st.checkbox("Remove Birth Dates & Study Dates", value=True)

    if uploaded_zip is not None:
        if st.button("Run Anonymization"):
            try:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(uploaded_zip, 'r') as zip_in:
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_out:
                        for filename in zip_in.namelist():
                            if filename.endswith(('.dcm', '.DCM')) or '.' not in filename.split('/')[-1]:
                                file_content = zip_in.read(filename)
                                try:
                                    ds = pydicom.dcmread(io.BytesIO(file_content))
                                    
                                    ds.PatientName = replacement_id
                                    ds.PatientID = replacement_id
                                    if remove_dates:
                                        if 'PatientBirthDate' in ds:
                                            ds.PatientBirthDate = ""
                                        if 'StudyDate' in ds:
                                            ds.StudyDate = ""
                                    
                                    if 'InstitutionName' in ds:
                                        ds.InstitutionName = "REDACTED_CLINIC"

                                    out_bytes = io.BytesIO()
                                    ds.save_as(out_bytes)
                                    zip_out.writestr(filename, out_bytes.getvalue())
                                except Exception:
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
    st.markdown("Upload a single DICOM file (or use the demo generator above to create one) to inspect its core properties and filter metadata tags.")

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
            
            # Tag Search Filter
            search_query = st.text_input("🔍 Filter Parameters", "")
            if search_query:
                df_info = df_info[df_info['Parameter'].str.contains(search_query, case=False) | 
                                  df_info['Value'].str.contains(search_query, case=False)]
            
            st.table(df_info)

            if getattr(ds, "Modality", "") == "RTDOSE":
                st.info("Detected RT Dose file.")
                if hasattr(ds, "DoseGridScaling"):
                    st.write(f"**Dose Grid Scaling Factor:** {ds.DoseGridScaling}")

        except Exception as e:
            st.error(f"Could not read the DICOM file: {e}")
