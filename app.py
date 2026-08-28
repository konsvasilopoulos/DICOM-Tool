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
    uploaded_dcm = st.file_uploader("Upload a single DICOM file (.dcm)", type=["dcm", "IMA"], key="inspect_dcm")

    if uploaded_dcm is not None:
        try:
            ds = pydicom.dcmread(uploaded_dcm)
            modality = getattr(ds, "Modality", "UNKNOWN")
            
            if modality == "CT":
                st.success(f"📌 Detected Modality: **CT** — Hounsfield Units active.")
            elif modality in ["DX", "CR", "MG"]:
                st.info(f"📌 Detected Modality: **Radiography ({modality})** — Raw Pixel Intensity mode active.")
            else:
                st.warning(f"📌 Detected Modality: **{modality}**")

            # --- NEW PROFESSIONAL 2-COLUMN LAYOUT ---
            col_left_viewer, col_right_controls = st.columns([1.1, 0.9], gap="large")
            
            # --- LEFT COLUMN: VIEWER & CONTRAST (Always visible, no scroll needed) ---
            with col_left_viewer:
                st.subheader("🖼️ Diagnostic Viewer")
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
                    
                    if modality == "CT":
                        preset = st.selectbox("Window Presets", ["Custom", "Soft Tissue (C:40, W:400)", "Bone (C:400, W:1500)", "Lung (C:-600, W:1500)", "Brain (C:40, W:80)"])
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
                        default_center = float(np.mean(img_data))
                        default_width = float(max(1.0, max_val - min_val))
                    
                    wc = st.slider(f"Window Center ({unit_label})", min_value=min_val, max_value=max_val, value=float(np.clip(default_center, min_val, max_val)))
                    ww = st.slider(f"Window Width ({unit_label})", min_value=1.0, max_value=max(10.0, max_val - min_val), value=float(default_width))
                    
                    vmin = wc - ww / 2
                    vmax = wc + ww / 2
                    
                    # Read dynamic ROI positions from right column session states
                    img_h, img_w = img_data.shape
                    cx_default, cy_default = img_w // 2, img_h // 2
                    
                    roi_configs = [
                        {"name": "Center", "default_dx": 0, "default_dy": 0, "color": "red"},
                        {"name": "Top", "default_dx": 0, "default_dy": -int(img_h * 0.25), "color": "blue"},
                        {"name": "Bottom", "default_dx": 0, "default_dy": int(img_h * 0.25), "color": "green"},
                        {"name": "Left", "default_dx": -int(img_w * 0.25), "default_dy": 0, "color": "orange"},
                        {"name": "Right", "default_dx": int(img_w * 0.25), "default_dy": 0, "color": "purple"}
                    ]
                    
                    fig, ax = plt.subplots(figsize=(5, 5))
                    ax.imshow(img_data, cmap=plt.cm.bone, vmin=vmin, vmax=vmax)
                    ax.axis('off')
                    
                    roi_summary_data = []
                    
                    # We store active states locally based on widget keys
                    for rc in roi_configs:
                        r_name = rc["name"]
                        # Fetch current slider values if available in session state
                        pos_x = st.session_state.get(f"x_{r_name}", cx_default + rc["default_dx"])
                        pos_y = st.session_state.get(f"y_{r_name}", cy_default + rc["default_dy"])
                        r_shape = st.session_state.get(f"shape_{r_name}", "Circle")
                        
                        max_dim = min(img_h, img_w) // 4
                        if r_shape == "Square":
                            r_size = st.session_state.get(f"size_{r_name}", 30)
                            x1, x2 = max(0, pos_x - r_size//2), min(img_w, pos_x + r_size//2)
                            y1, y2 = max(0, pos_y - r_size//2), min(img_h, pos_y + r_size//2)
                            roi_pixels = img_data[y1:y2, x1:x2]
                            
                            rect = patches.Rectangle((x1, y1), x2 - x1, y2 - y1, linewidth=1.5, edgecolor=rc["color"], facecolor='none')
                            ax.add_patch(rect)
                            ax.text(x1, y1 - 5, r_name, color=rc["color"], fontsize=9, weight='bold')
                        else:
                            r_radius = st.session_state.get(f"rad_{r_name}", 20)
                            y_grid, x_grid = np.ogrid[:img_h, :img_w]
                            mask = (x_grid - pos_x)**2 + (y_grid - pos_y)**2 <= r_radius**2
                            roi_pixels = img_data[mask]
                            
                            circle = patches.Circle((pos_x, pos_y), r_radius, linewidth=1.5, edgecolor=rc["color"], facecolor='none')
                            ax.add_patch(circle)
                            ax.text(pos_x - r_radius, pos_y - r_radius - 5, r_name, color=rc["color"], fontsize=9, weight='bold')
                        
                        if roi_pixels.size > 0:
                            roi_summary_data.append({
                                "ROI Name": r_name,
                                "Shape": r_shape,
                                "Mean": f"{np.mean(roi_pixels):.2f}",
                                "Noise (StdDev)": f"{np.std(roi_pixels):.2f}",
                                "Min": f"{np.min(roi_pixels):.1f}",
                                "Max": f"{np.max(roi_pixels):.1f}"
                            })
                    
                    st.pyplot(fig)
                    
                    img_buf = io.BytesIO()
                    fig.savefig(img_buf, format="png", bbox_inches='tight', dpi=150)
                    img_buf.seek(0)
                    st.download_button("📥 Download Preview PNG", img_buf, file_name="dicom_preview.png", mime="image/png")

            # --- RIGHT COLUMN: MULTI-ROI CONTROLS & METADATA ---
            with col_right_controls:
                st.subheader("⚙️ Multi-ROI & QC Tools")
                
                with st.expander("🎯 Configure ROIs (Center, Top, Bottom, Left, Right)", expanded=True):
                    for rc in roi_configs:
                        r_name = rc["name"]
                        with st.container():
                            st.markdown(f"**{r_name} ROI**")
                            r_shape = st.selectbox(f"Shape {r_name}", ["Circle", "Square"], key=f"shape_{r_name}")
                            col_sx, col_sy = st.columns(2)
                            with col_sx:
                                st.slider(f"X ({r_name})", min_value=0, max_value=img_w, value=cx_default + rc["default_dx"], key=f"x_{r_name}")
                            with col_sy:
                                st.slider(f"Y ({r_name})", min_value=0, max_value=img_h, value=cy_default + rc["default_dy"], key=f"y_{r_name}")
                            
                            if r_shape == "Square":
                                st.slider(f"Size {r_name}", min_value=5, max_value=100, value=30, key=f"size_{r_name}")
                            else:
                                st.slider(f"Radius {r_name}", min_value=5, max_value=50, value=20, key=f"rad_{r_name}")
                            st.divider()

                if roi_summary_data:
                    st.subheader("📋 Measurements Table")
                    df_roi = pd.DataFrame(roi_summary_data)
                    st.table(df_roi)

            # --- FULL WIDTH SECTIONS BELOW ---
            st.markdown("---")
            col_meta1, col_meta2 = st.columns(2)
            
            with col_meta1:
                with st.expander("📋 Key Metadata Summary"):
                    info = {
                        "Modality": modality,
                        "Patient ID": getattr(ds, "PatientID", "N/A"),
                        "Study Description": getattr(ds, "StudyDescription", "N/A"),
                        "Manufacturer": getattr(ds, "Manufacturer", "N/A"),
                        "Matrix Size": f"{getattr(ds, 'Rows', 'N/A')} x {getattr(ds, 'Columns', 'N/A')}",
                    }
                    st.table(pd.DataFrame(list(info.items()), columns=["Parameter", "Value"]))

            with col_meta2:
                with st.expander("📊 Full Image Statistics & Histogram"):
                    st.write(f"- **Image Mean:** {np.mean(img_data):.2f} {unit_label}")
                    st.write(f"- **Image StdDev:** {np.std(img_data):.2f}")
                    
                    fig_hist, ax_hist = plt.subplots(figsize=(4, 2))
                    ax_hist.hist(img_data.ravel(), bins=32, color='skyblue', edgecolor='black')
                    st.pyplot(fig_hist)

            with st.expander("📋 Explore All DICOM Tags (Raw Metadata)"):
                all_tags = [{"Tag": str(elem.tag), "Keyword": getattr(elem, "keyword", ""), "Name": elem.name, "Value": str(elem.value)[:100]} for elem in ds if elem.tag != 0x7fe00010]
                df_tags = pd.DataFrame(all_tags)
                tag_search = st.text_input("🔍 Search DICOM tags", "")
                if tag_search:
                    df_tags = df_tags[df_tags.apply(lambda row: row.astype(str).str.contains(tag_search, case=False).any(), axis=1)]
                st.dataframe(df_tags, use_container_width=True)

        except Exception as e:
            st.error(f"Could not read DICOM file: {e}")

with tab3:
    st.header("📊 Batch Dataset Report & CSV Export")
    st.markdown("Upload a ZIP folder containing multiple DICOM files. The tool automatically groups CT slices per patient/series and aggregates summary statistics.")

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
                        "Total Slices": v["Slice Count"],
                        "Avg Mean / HU": f"{mean_val:.2f}"
                    })
                
                if summary_data:
                    df_summary = pd.DataFrame(summary_data)
                    st.success(f"Aggregated {len(summary_data)} series successfully!")
                    st.dataframe(df_summary, use_container_width=True)
                    
                    csv_bytes = df_summary.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Download CSV Report", csv_bytes, "medphys_batch_report.csv", "text/csv")
                else:
                    st.warning("No valid DICOM files found in ZIP.")
            except Exception as e:
                st.error(f"Error processing batch archive: {e}")

# --- FOOTER ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Developed by <b>Konstantinos G. Vasilopoulos</b> (Medical Physicist & Researcher) | Contact: kostasvasilopoulosgr@yahoo.com</p>", unsafe_allow_html=True)
