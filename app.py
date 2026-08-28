import io
import zipfile
import pydicom
from pydicom.dataset import Dataset, FileDataset
import streamlit as st
import pandas as pd
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from streamlit_drawable_canvas import st_canvas

st.set_page_config(
    page_title="MedPhys DICOM Toolkit",
    page_icon="🏥",
    layout="wide"
)

# --- SIDEBAR: AUTHOR & INFO ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/medical-doctor.png", width=64)
    st.header("MedPhys Toolkit")
    st.markdown("""
    A lightweight, open-source web application designed for medical physicists and researchers.
    """)
    st.divider()
    st.markdown("**Developer / Creator:**")
    st.markdown("👨‍💻 **Konstantinos G. Vasilopoulos**")
    st.markdown("*Medical Physicist & Researcher*")
    st.markdown("✉️ **Email:** `kostasvasilopoulosgr@yahoo.com`")
    st.divider()

# --- MAIN PAGE ---
st.title("🏥 Open-Source DICOM Toolkit for Medical Physics")
st.markdown("""
Quickly inspect, adjust, anonymize, and batch-analyze DICOM datasets locally with modality-aware processing.
""")

def generate_demo_ct():
    file_meta = pydicom.dataset.FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = pydicom.uid.UID('1.2.840.10008.5.1.4.1.1.2') 
    file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
    file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian

    ds = FileDataset(None, {}, file_meta=file_meta, preamble=b"\0" * 128)
    ds.PatientName = "DOE^JOHN"
    ds.PatientID = "CT_PATIENT_001"
    ds.PatientBirthDate = "19800101"
    ds.StudyDate = datetime.datetime.now().strftime("%Y%m%d")
    ds.Modality = "CT"
    ds.Manufacturer = "SIEMENS_DEMO"
    ds.StationName = "CT_ROOM_01"
    ds.KVP = "120"
    ds.XRayTubeCurrent = "250"
    ds.ExposureTime = "1000"
    ds.StudyDescription = "Routine Head CT"
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
    ds.PatientID = "DX_PATIENT_002"
    ds.PatientBirthDate = "19900515"
    ds.StudyDate = datetime.datetime.now().strftime("%Y%m%d")
    ds.Modality = "DX"
    ds.Manufacturer = "PHILIPS_DEMO"
    ds.StationName = "XRAY_ROOM_03"
    ds.KVP = "75"
    ds.XRayTubeCurrent = "320"
    ds.ExposureTime = "150"
    ds.StudyDescription = "Chest X-Ray"
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

tab1, tab2, tab3 = st.tabs(["🔒 DICOM Anonymizer", "🔍 Inspector & Viewer", "📊 Batch CSV Report Generator"])

with tab1:
    st.header("🔒 Batch DICOM Anonymizer")
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
                st.download_button("📥 Download Demo CT ZIP", demo_zip_buffer, "demo_ct_files.zip", "application/zip", key="dl_ct")
        with col_d2:
            if st.button("Generate Demo X-Ray (DX) ZIP"):
                demo_dx_bytes = generate_demo_dx()
                demo_dx_buffer = io.BytesIO()
                with zipfile.ZipFile(demo_dx_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_out:
                    zip_out.writestr("demo_dx_scan.dcm", demo_dx_bytes)
                demo_dx_buffer.seek(0)
                st.success("Demo X-Ray ZIP generated!")
                st.download_button("📥 Download Demo X-Ray ZIP", demo_dx_buffer, "demo_dx_files.zip", "application/zip", key="dl_dx")

    uploaded_zip = st.file_uploader("Upload DICOM ZIP Archive", type=["zip"], key="anon_zip")

    st.subheader("Anonymization Settings")
    base_replacement_id = st.text_input("Base Prefix for Anonymized ID", value="ANON_PATIENT")
    remove_dates = st.checkbox("Remove Birth Dates & Study Dates*", value=True)
    st.markdown("<small>* **Checked:** Erases Patient Birth Date & Study Date for strict privacy. \n* **Unchecked:** Keeps original dates intact as found in raw headers.</small>", unsafe_allow_html=True)

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
                st.success(f"Anonymization completed successfully! Processed {counter - 1} files.")
                st.download_button("📥 Download Anonymized ZIP", zip_buffer, "anonymized_dicom_files.zip", "application/zip")
            except Exception as e:
                st.error(f"An error occurred during processing: {e}")

with tab2:
    st.header("🔍 DICOM Inspector & Diagnostic Viewer")
    st.markdown("Upload a single diagnostic DICOM file (CT, DX, CR, MG, etc.) or use the demo generators.")

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
                    "Station Name": getattr(ds, "StationName", "N/A"),
                    "Tube Voltage (kVp)": getattr(ds, "KVP", "N/A"),
                    "Tube Current (mA)": getattr(ds, "XRayTubeCurrent", "N/A"),
                    "Exposure Time (ms)": getattr(ds, "ExposureTime", "N/A"),
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
                    
                    # Modality-Aware Window Controls (Presets ONLY for CT)
                    if modality == "CT":
                        preset = st.selectbox("Window Presets (CT Only)", ["Custom", "Soft Tissue (C:40, W:400)", "Bone (C:400, W:1500)", "Lung (C:-600, W:1500)", "Brain (C:40, W:80)"])
                        if preset == "Soft Tissue (C:40, W:400)":
                            default_center, default_width = 40.0, 400.0
                        elif preset == "Bone (C:400, W:1500)":
                            default_center, default_width = 400.0, 1500.0
                        elif preset == "Lung (C:-600, W:1500)":
                            default_center, default_width = -600.0, 1500.0
                        elif preset == "Brain (C:40, W:80)":
                            default_center, default_width = 40.0, 80.0
                        else:
                            default_center = float(np.mean(img_data))
                            default_width = float(max(1.0, max_val - min_val))
                    else:
                        st.markdown("*Radiography / Direct Intensity Contrast Controls*")
                        default_center = float(np.mean(img_data))
                        default_width = float(max(1.0, max_val - min_val))
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        wc = st.slider(f"Window Center ({unit_label})", min_value=min_val, max_value=max_val, value=float(np.clip(default_center, min_val, max_val)))
                    with c2:
                        ww = st.slider(f"Window Width ({unit_label})", min_value=1.0, max_value=max(10.0, max_val - min_val), value=float(default_width))
                    
                    vmin = wc - ww / 2
                    vmax = wc + ww / 2
                    
                    # Normalize image to 0-255 for interactive canvas preview
                    img_clipped = np.clip(img_data, vmin, vmax)
                    img_norm = ((img_clipped - vmin) / (vmax - vmin + 1e-5) * 255).astype(np.uint8)
                    pil_img = Image.fromarray(img_norm).convert("RGB")
                    
                    st.markdown("---")
                    st.subheader("🎯 Interactive ROI Canvas (Draw/Select on Image)")
                    st.markdown("Use the rectangle or circle drawing tool on the canvas below to inspect specific regions.")
                    
                    drawing_mode = st.selectbox("Drawing Tool", ["rect", "circle"], index=0)
                    
                    # Canvas component for interactive drawing
                    canvas_result = st_canvas(
                        fill_color="rgba(255, 0, 0, 0.2)",
                        stroke_width=2,
                        stroke_color="red",
                        background_image=pil_img,
                        update_streamlit=True,
                        height=400,
                        width=400,
                        drawing_mode=drawing_mode,
                        key="canvas",
                    )
                    
                    # Extract ROI pixels from drawn objects
                    roi_pixels_list = []
                    if canvas_result.json_data is not None:
                        objects = canvas_result.json_data["objects"]
                        if objects:
                            obj = objects[-1]
                            scale_x = img_data.shape[1] / 400.0
                            scale_y = img_data.shape[0] / 400.0
                            
                            if obj["type"] == "rect":
                                left = int(obj["left"] * scale_x)
                                top = int(obj["top"] * scale_y)
                                width = int(obj["width"] * obj["scaleX"] * scale_x)
                                height = int(obj["height"] * obj["scaleY"] * scale_y)
                                
                                x1, x2 = max(0, left), min(img_data.shape[1], left + width)
                                y1, y2 = max(0, top), min(img_data.shape[0], top + height)
                                roi_pixels_list = img_data[y1:y2, x1:x2].ravel()
                                
                            elif obj["type"] == "circle":
                                cx = int((obj["left"] + obj["radius"]) * scale_x)
                                cy = int((obj["top"] + obj["radius"]) * scale_y)
                                radius = int(obj["radius"] * obj["scaleX"] * scale_x)
                                
                                y, x = np.ogrid[:img_data.shape[0], :img_data.shape[1]]
                                mask = (x - cx)**2 + (y - cy)**2 <= radius**2
                                roi_pixels_list = img_data[mask]
                    
                    # ROI Statistics Output
                    if len(roi_pixels_list) > 0:
                        with st.expander("📌 Drawn ROI Statistics Results", expanded=True):
                            r_mean = np.mean(roi_pixels_list)
                            r_std = np.std(roi_pixels_list)
                            r_min = np.min(roi_pixels_list)
                            r_max = np.max(roi_pixels_list)
                            st.write(f"- **ROI Mean:** {r_mean:.2f} {unit_label}")
                            st.write(f"- **ROI Noise (StdDev):** {r_std:.2f} {unit_label}")
                            st.write(f"- **ROI Min Value:** {r_min:.1f} {unit_label}")
                            st.write(f"- **ROI Max Value:** {r_max:.1f} {unit_label}")
                    else:
                        st.info("💡 Draw a rectangle or circle directly on the image above to calculate ROI statistics.")
                    
                    with st.expander("📊 Full Image Statistics & Histogram"):
                        st.write(f"- **Image Mean:** {np.mean(img_data):.2f} {unit_label}")
                        st.write(f"- **Image StdDev:** {np.std(img_data):.2f}")
                        st.write(f"- **Min / Max:** {min_val:.1f} / {max_val:.1f} {unit_label}")
                        
                        fig_hist, ax_hist = plt.subplots(figsize=(5, 2.5))
                        ax_hist.hist(img_data.ravel(), bins=64, color='skyblue', edgecolor='black')
                        ax_hist.set_title(f"Pixel Intensity Distribution ({unit_label})", fontsize=10)
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

with tab3:
    st.header("📊 Batch Dataset Report & CSV Export")
    st.markdown("Upload a ZIP folder containing multiple DICOM files (mixed patients, CT series, or X-rays). The tool automatically groups CT slices per patient/series and aggregates summary statistics into a clean report.")

    batch_zip = st.file_uploader("Upload Multi-Dataset ZIP", type=["zip"], key="batch_zip")

    if batch_zip is not None:
        if st.button("Process & Aggregate Dataset"):
            try:
                records = {}
                with zipfile.ZipFile(batch_zip, 'r') as zip_in:
                    for filename in zip_in.namelist():
                        if filename.endswith(('.dcm', '.DCM')) or '.' not in filename.split('/')[-1]:
                            file_content = zip_in.read(filename)
                            try:
                                ds = pydicom.dcmread(io.BytesIO(file_content))
                                patient_id = str(getattr(ds, "PatientID", "UNKNOWN_PATIENT"))
                                modality = str(getattr(ds, "Modality", "UNKNOWN"))
                                series_uid = str(getattr(ds, "SeriesInstanceUID", "UNKNOWN_SERIES"))
                                
                                group_key = f"{patient_id}_{modality}_{series_uid}"
                                
                                if group_key not in records:
                                    records[group_key] = {
                                        "Patient ID": patient_id,
                                        "Modality": modality,
                                        "Study Description": str(getattr(ds, "StudyDescription", "N/A")),
                                        "Manufacturer": str(getattr(ds, "Manufacturer", "N/A")),
                                        "Station Name": str(getattr(ds, "StationName", "N/A")),
                                        "kVp": str(getattr(ds, "KVP", "N/A")),
                                        "Tube Current (mA)": str(getattr(ds, "XRayTubeCurrent", "N/A")),
                                        "Exposure Time (ms)": str(getattr(ds, "ExposureTime", "N/A")),
                                        "Slice Thickness": str(getattr(ds, "Slice Thickness", "N/A")),
                                        "Matrix Size": f"{getattr(ds, 'Rows', 'N/A')} x {getattr(ds, 'Columns', 'N/A')}",
                                        "Slice Count": 0,
                                        "Mean Pixel Value": []
                                    }
                                
                                records[group_key]["Slice Count"] += 1
                                if hasattr(ds, "pixel_array"):
                                    arr = ds.pixel_array.astype(np.float32)
                                    if modality == "CT":
                                        slope = float(getattr(ds, "RescaleSlope", 1.0))
                                        intercept = float(getattr(ds, "RescaleIntercept", 0.0))
                                        arr = arr * slope + intercept
                                    records[group_key]["Mean Pixel Value"].append(np.mean(arr))
                                    
                            except Exception:
                                continue
                
                summary_data = []
                for k, v in records.items():
                    mean_val = np.mean(v["Mean Pixel Value"]) if v["Mean Pixel Value"] else 0.0
                    summary_data.append({
                        "Patient ID": v["Patient ID"],
                        "Modality": v["Modality"],
                        "Study Description": v["Study Description"],
                        "Manufacturer": v["Manufacturer"],
                        "Station Name": v["Station Name"],
                        "kVp": v["kVp"],
                        "Tube Current (mA)": v["Tube Current (mA)"],
                        "Exposure Time (ms)": v["Exposure Time (ms)"],
                        "Total Slices / Files": v["Slice Count"],
                        "Slice Thickness": v["Slice Thickness"],
                        "Matrix Size": v["Matrix Size"],
                        "Avg Mean Pixel / HU": f"{mean_val:.2f}"
                    })
                
                if summary_data:
                    df_summary = pd.DataFrame(summary_data)
                    st.success(f"Successfully aggregated dataset! Found {len(summary_data)} distinct patient/series groups.")
                    st.dataframe(df_summary, use_container_width=True)
                    
                    csv_bytes = df_summary.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Summary CSV Report",
                        data=csv_bytes,
                        file_name="medphys_dicom_batch_report.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No valid DICOM files were found inside the ZIP archive.")
                    
            except Exception as e:
                st.error(f"Error processing batch archive: {e}")

# --- FOOTER ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Developed by <b>Konstantinos G. Vasilopoulos</b> (Medical Physicist & Researcher) | Contact: kostasvasilopoulosgr@yahoo.com</p>", unsafe_allow_html=True)
