import io
import zipfile
import pydicom
from pydicom.dataset import Dataset, FileDataset
import streamlit as st
import pandas as pd
import datetime
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="MedPhys DICOM Toolkit",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Open-Source DICOM Toolkit for Medical Physics")
st.markdown("""
A lightweight, open-source web application designed for medical physicists and researchers to quickly inspect, 
adjust, and securely anonymize DICOM files locally.
""")

def generate_demo_dicom():
    file_meta = pydicom.dataset.FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = pydicom.uid.UID('1.2.840.10008.5.1.4.1.1.2') 
    file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
    file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian

    ds = FileDataset(None, {}, file_meta=file_meta, preamble=b"\0" * 128)
    
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
    ds.RescaleIntercept = 0.0
    ds.RescaleSlope = 1.0
    
    # Fake image array (circle mimicking an object)
    y, x = np.ogrid[:512, :512]
    mask = (x - 256)**2 + (y - 256)**2 <= 100**2
    img_array = np.zeros((512, 512), dtype=np.int16)
    img_array[mask] = 400 # HU imitation
    ds.PixelData = img_array.tobytes()
    
    out_bytes = io.BytesIO()
    ds.is_little_endian = True
    ds.is_implicit_VR = False
    ds.save_as(out_bytes)
    out_bytes.seek(0)
    return out_bytes.getvalue()

tab1, tab2 = st.tabs(["🔒 DICOM Anonymizer", "🔍 DICOM Inspector & Advanced Viewer"])

with tab1:
    st.header("Batch DICOM Anonymizer")
    st.markdown("Upload a **ZIP archive** containing your DICOM files, or generate a demo ZIP file to test the tool instantly.")

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
    st.header("DICOM Quick Inspector & Advanced Viewer")
    st.markdown("Upload a single DICOM file to inspect technical tags, adjust window levels, and view the image.")

    uploaded_dcm = st.file_uploader("Upload DICOM File (.dcm)", type=["dcm", "IMA"], key="inspect_dcm")

    if uploaded_dcm is not None:
        try:
            ds = pydicom.dcmread(uploaded_dcm)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Key Metadata Summary")
                info = {
                    "Modality": getattr(ds, "Modality", "Unknown"),
                    "Patient ID": getattr(ds, "PatientID", "N/A"),
                    "Study Description": getattr(ds, "StudyDescription", "N/A"),
                    "Manufacturer": getattr(ds, "Manufacturer", "N/A"),
                    "Rows x Columns": f"{getattr(ds, 'Rows', 'N/A')} x {getattr(ds, 'Columns', 'N/A')}",
                    "Slice Thickness": getattr(ds, "Slice Thickness", "N/A"),
                }
                df_info = pd.DataFrame(list(info.items()), columns=["Parameter", "Value"])
                st.table(df_info)

            with col2:
                st.subheader("Interactive Image Viewer")
                if hasattr(ds, "pixel_array"):
                    # Get pixel data and apply rescale slope/intercept if available
                    pixel_array = ds.pixel_array.astype(np.float32)
                    slope = float(getattr(ds, "RescaleSlope", 1.0))
                    intercept = float(getattr(ds, "RescaleIntercept", 0.0))
                    img_data = pixel_array * slope + intercept
                    
                    # Window / Level controls
                    min_val, max_val = float(img_data.min()), float(img_data.max())
                    default_center = float(np.mean(img_data))
                    default_width = float(max(100.0, max_val - min_val))
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        wc = st.slider("Window Center (Level)", min_value=min_val, max_value=max_val, value=default_center)
                    with c2:
                        ww = st.slider("Window Width", min_value=1.0, max_value=max(10.0, max_val - min_val), value=default_width)
                    
                    vmin = wc - ww / 2
                    vmax = wc + ww / 2
                    
                    fig, ax = plt.subplots(figsize=(5, 5))
                    im = ax.imshow(img_data, cmap=plt.cm.bone, vmin=vmin, vmax=vmax)
                    ax.axis('off')
                    st.pyplot(fig)
                else:
                    st.info("No pixel data found in this DICOM file.")

            # Full Tag Explorer Expander
            with st.expander("📋 Explore All DICOM Tags (Raw Metadata)"):
                all_tags = []
                for elem in ds:
                    if elem.tag != 0x7fe00010: # Exclude raw pixel data binary
                        all_tags.append({
                            "Tag": str(elem.tag),
                            "Keyword": getattr(elem, "keyword", ""),
                            "Name": elem.name,
                            "Value": str(elem.value)[:100] # truncate long values
                        })
                df_tags = pd.DataFrame(all_tags)
                tag_search = st.text_input("🔍 Search all DICOM tags", "")
                if tag_search:
                    df_tags = df_tags[df_tags.apply(lambda row: row.astype(str).str.contains(tag_search, case=False).any(), axis=1)]
                st.dataframe(df_tags, use_container_width=True)

        except Exception as e:
            st.error(f"Could not read the DICOM file: {e}")
