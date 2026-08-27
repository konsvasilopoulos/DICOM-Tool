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
adjust, and securely anonymize DICOM files locally, ensuring modality-aware processing.
""")

def generate_demo_ct():
    file_meta = pydicom.dataset.FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = pydicom.uid.UID('1.2.840.10008.5.1.4.1.1.2') 
    file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
    file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian

    ds = FileDataset(None, {}, file_meta=file_meta, preamble=b"\0" * 128)
    
    ds.PatientName = "DOE^JOHN"
    ds.PatientID = "CT_DEMO_01"
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
    
    y, x = np.ogrid[:512, :512]
    mask = (x - 256)**2 + (y - 256)**2 <= 100**2
    img_array = np.zeros((512, 512), dtype=np.int16) - 1000
    img_array[mask] = 400
    ds.PixelData = img_array.tobytes()
    
    out_bytes = io.BytesIO()
    ds.is_little_endian = True
    ds.is_implicit_VR = False
    ds.save_as(out_bytes)
    out_bytes.seek(0)
    return out_bytes.getvalue()

def generate_demo_dx():
    file_meta = pydicom.dataset.FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = pydicom.uid.UID('1.2.840.10008.5.1.4.1.1.1') 
    file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
    file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian

    ds = FileDataset(None, {}, file_meta=file_meta, preamble=b"\0" * 128)
    
    ds.PatientName = "SMITH^JANE"
    ds.PatientID = "DX_DEMO_02"
    ds.PatientBirthDate = "19900515"
    ds.StudyDate = datetime.datetime.now().strftime("%Y%m%d")
    ds.Modality = "DX"
    ds.Manufacturer = "DEMO_VENDOR"
    ds.StudyDescription = "Chest X-Ray Test"
    ds.Rows = 512
    ds.Columns = 512
    ds.PixelSpacing = [0.15, 0.15]
    ds.InstitutionName = "UNIVERSITY HOSPITAL"
    
    y, x = np.ogrid[:512, :512]
    img_array = np.linspace(100, 3000, 512, dtype=np.uint16)
    rib_mask = np.sin(x / 20.0) * np.cos(y / 30.0) * 500 + 1500
    img_array = np.clip(rib_mask, 0, 4095).astype(np.uint16)
    ds.PixelData = img_array.tobytes()
    
    out_bytes = io.BytesIO()
    ds.is_little_endian = True
    ds.is_implicit_VR = False
    ds.save_as(out_bytes)
    out_bytes.seek(0)
    return out_bytes.getvalue()

tab1, tab2 = st.tabs(["🔒 DICOM Anonymizer", "🔍 DICOM Inspector & Diagnostic Viewer"])

with tab1:
    st.header("Batch DICOM Anonymizer")
    st.markdown("Upload a **ZIP archive** containing your DICOM files, or generate demo datasets to test the tool instantly.")

    with st.expander("🧪 Don't have DICOM files? Generate Test Data"):
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            if st.button("Generate Demo CT ZIP"):
                demo_dcm_bytes = generate_demo_ct()
                demo_zip_buffer = io.BytesIO()
                with zipfile.ZipFile(demo_zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_out:
                    zip_out.writestr("demo_ct_scan.dcm", demo_dcm_bytes)
                demo_zip_buffer.seek(0)
                
                st.success("Demo CT ZIP generated!")
                st.download_button(
                    label="📥 Download Demo CT ZIP",
                    data=demo_zip_buffer,
                    file_name="demo_ct_files.zip",
                    mime="application/zip",
                    key="dl_ct"
                )
        with col_d2:
            if st.button("Generate Demo X-Ray (DX) ZIP"):
                demo_dx_bytes = generate_demo_dx()
                demo_dx_buffer = io.BytesIO()
                with zipfile.ZipFile(demo_dx_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_out:
                    zip_out.writestr("demo_dx_scan.dcm", demo_dx_bytes)
                demo_dx_buffer.seek(0)
                
                st.success("Demo X-Ray ZIP generated!")
                st.download_button(
                    label="📥 Download Demo X-Ray ZIP",
                    data=demo_dx_buffer,
                    file_name="demo_dx_files.zip",
                    mime="application/zip",
                    key="dl_dx"
                )

    uploaded_zip = st.file_uploader("Upload DICOM ZIP Archive", type=["zip"], key="anon_zip")

    st.subheader("Anonymization Settings")
    base_replacement_id = st.text_input("Base Prefix for Anonymized ID", value="ANON_PATIENT")
    remove_dates = st.checkbox("Remove Birth Dates & Study Dates*", value=True)
    st.markdown("<small>* **Checked:** Erases Patient Birth Date & Study Date for strict privacy. \n* **Unchecked:** Keeps original dates intact as found in the raw DICOM headers.</small>", unsafe_allow_html=True)

    if uploaded_zip is not None:
        if st.button("Run Anonymization"):
            try:
                zip_buffer = io.BytesIO()
                counter = 1
                with zipfile.ZipFile(uploaded_zip, 'r') as zip_in:
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_out:
                        for filename in zip_in.namelist():
                            if filename.endswith(('.dcm', '.DCM')) or '.' not in filename.split('/')[-1]:
                                file_content = zip_in.read(filename)
                                try:
                                    ds = pydicom.dcmread(io.BytesIO(file_content))
                                    
                                    # Αυτόματος αύξων αριθμός ανά αρχείο (π.χ. ANON_PATIENT_001)
                                    current_id = f"{base_replacement_id}_{counter:03d}"
                                    ds.PatientName = current_id
                                    ds.PatientID = current_id
                                    
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
                                    counter += 1
                                except Exception:
                                    zip_out.writestr(filename, file_content)
                
                zip_buffer.seek(0)
                st.success(f"Anonymization completed successfully! Processed {counter - 1} DICOM files with sequential IDs.")
                
                st.download_button(
                    label="📥 Download Anonymized ZIP",
                    data=zip_buffer,
                    file_name="anonymized_dicom_files.zip",
                    mime="application/zip"
                )
            except Exception as e:
                st.error(f"An error occurred during processing: {e}")

with tab2:
    st.header("DICOM Inspector & Diagnostic Viewer")
    st.markdown("Upload a single diagnostic DICOM file (CT, DX, CR, MG, etc.) or use one of the demo generators above.")

    uploaded_dcm = st.file_uploader("Upload DICOM File (.dcm)", type=["dcm", "IMA"], key="inspect_dcm")

    if uploaded_dcm is not None:
        try:
            ds = pydicom.dcmread(uploaded_dcm)
            modality = getattr(ds, "Modality", "UNKNOWN")
            
            if modality == "CT":
                st.success(f"📌 Detected Modality: **CT (Computed Tomography)** — Hounsfield Units (HU) scaling active.")
            elif modality in ["DX", "CR", "MG"]:
                st.info(f"📌 Detected Modality: **Radiography / Projection Imaging ({modality})** — Raw Pixel Intensity mode active.")
            else:
                st.warning(f"📌 Detected Modality: **{modality}** — Standard DICOM viewer mode active.")

            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Key Metadata Summary")
                info = {
                    "Modality": modality,
                    "Patient ID": getattr(ds, "PatientID", "N/A"),
                    "Study Description": getattr(ds, "StudyDescription", "N/A"),
                    "Manufacturer": getattr(ds, "Manufacturer", "N/A"),
                    "Matrix Size": f"{getattr(ds, 'Rows', 'N/A')} x {getattr(ds, 'Columns', 'N/A')}",
                    "Slice Thickness": getattr(ds, "Slice Thickness", "N/A"),
                }
                df_info = pd.DataFrame(list(info.items()), columns=["Parameter", "Value"])
                st.table(df_info)

            with col2:
                st.subheader("Diagnostic Image Viewer & Controls")
                if hasattr(ds, "pixel_array"):
                    pixel_array = ds.pixel_array.astype(np.float32)
                    
                    if modality == "CT":
                        slope = float(getattr(ds, "RescaleSlope", 1.0))
                        intercept = float(getattr(ds, "RescaleIntercept", 0.0))
                        img_data = pixel_array * slope + intercept
                        unit_label = "HU"
                    else:
                        img_data = pixel_array
                        unit_label = "Intensity"
                    
                    min_val, max_val = float(img_data.min()), float(img_data.max())
                    default_center = float(np.mean(img_data))
                    default_width = float(max(1.0, max_val - min_val))
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        wc = st.slider(f"Window Center ({unit_label})", min_value=min_val, max_value=max_val, value=default_center)
                    with c2:
                        ww = st.slider(f"Window Width ({unit_label})", min_value=1.0, max_value=max(10.0, max_val - min_val), value=default_width)
                    
                    vmin = wc - ww / 2
                    vmax = wc + ww / 2
                    
                    fig, ax = plt.subplots(figsize=(4.5, 4.5))
                    im = ax.imshow(img_data, cmap=plt.cm.bone, vmin=vmin, vmax=vmax)
                    ax.axis('off')
                    st.pyplot(fig)
                    
                    with st.expander("📊 Pixel Statistics & Histogram"):
                        mean_val = np.mean(img_data)
                        std_val = np.std(img_data)
                        st.write(f"- **Mean Value:** {mean_val:.2f} {unit_label}")
                        st.write(f"- **Standard Deviation:** {std_val:.2f}")
                        st.write(f"- **Min / Max:** {min_val:.1f} / {max_val:.1f} {unit_label}")
                        
                        fig_hist, ax_hist = plt.subplots(figsize=(5, 2.5))
                        ax_hist.hist(img_data.ravel(), bins=64, color='skyblue', edgecolor='black')
                        ax_hist.set_title(f"Pixel Intensity Distribution ({unit_label})", fontsize=10)
                        ax_hist.set_xlabel(unit_label, fontsize=8)
                        ax_hist.set_ylabel("Frequency", fontsize=8)
                        st.pyplot(fig_hist)
                else:
                    st.info("No pixel data found in this DICOM file.")

            with st.expander("📋 Explore All DICOM Tags (Raw Metadata)"):
                all_tags = []
                for elem in ds:
                    if elem.tag != 0x7fe00010:
                        all_tags.append({
                            "Tag": str(elem.tag),
                            "Keyword": getattr(elem, "keyword", ""),
                            "Name": elem.name,
                            "Value": str(elem.value)[:100]
                        })
                df_tags = pd.DataFrame(all_tags)
                tag_search = st.text_input("🔍 Search all DICOM tags", "")
                if tag_search:
                    df_tags = df_tags[df_tags.apply(lambda row: row.astype(str).str.contains(tag_search, case=False).any(), axis=1)]
                st.dataframe(df_tags, use_container_width=True)

        except Exception as e:
            st.error(f"Could not read the DICOM file: {e}")
