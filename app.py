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
from PIL import Image, ImageFilter, ImageOps, ImageEnhance

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
    img_array[mask] = 0  # Water phantom region = 0 HU
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
    ds.StationName = "PORTABLE_XRAY_01"
    ds.StudyDescription = "PORTABLE CHEST X-RAY"
    ds.KVP = "75"
    ds.XRayTubeCurrent = "320"
    ds.ExposureTime = "150"
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
            if st.button("Generate Demo Portable X-Ray (DX) ZIP"):
                demo_dx_bytes = generate_demo_dx()
                demo_dx_buffer = io.BytesIO()
                with zipfile.ZipFile(demo_dx_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_out:
                    zip_out.writestr("demo_portable_dx.dcm", demo_dx_bytes)
                demo_dx_buffer.seek(0)
                st.success("Demo Portable X-Ray ZIP generated!")
                st.download_button("📥 Download Demo Portable X-Ray ZIP", demo_dx_buffer, "demo_dx_files.zip", "application/zip", key="dl_dx")

    uploaded_zip = st.file_uploader("Upload DICOM ZIP Archive", type=["zip"], key="anon_zip")

    st.subheader("Anonymization Settings")
    base_replacement_id = st.text_input("Base Prefix for Anonymized ID", value="ANON_PATIENT")
    remove_dates = st.checkbox("Remove Birth Dates & Study Dates*", value=True)

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
            
            study_desc = str(getattr(ds, "StudyDescription", "")).upper()
            series_desc = str(getattr(ds, "SeriesDescription", "")).upper()
            station_name = str(getattr(ds, "StationName", "")).upper()
            is_portable = "PORTABLE" in study_desc or "MOBILE" in study_desc or "PORTABLE" in station_name or "MOBILE" in station_name
            
            if modality == "CT":
                st.success(f"📌 Detected Modality: **CT (Computed Tomography)** — Hounsfield Units active.")
            elif modality == "MG":
                st.info(f"📌 Detected Modality: **MG (Mammography)** — High-resolution mode active.")
            elif modality in ["DX", "CR"]:
                portable_tag = " [⚠️ PORTABLE / MOBILE UNIT]" if is_portable else ""
                st.info(f"📌 Detected Modality: **Radiography ({modality}){portable_tag}** — Raw Pixel Intensity active.")
            else:
                st.warning(f"📌 Detected Modality: **{modality}**")

            # --- 2-COLUMN LAYOUT ---
            col_left_viewer, col_right_controls = st.columns([1.1, 0.9], gap="large")
            
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
                    
                    # --- QUICK ADJUSTMENTS & ENHANCED FILTERS PANEL ---
                    st.markdown("##### Quick Adjustments & Filters")
                    q_col1, q_col2 = st.columns(2)
                    with q_col1:
                        brightness_offset = st.slider("Brightness", -300.0, 300.0, 0.0, step=10.0)
                        gamma_val = st.slider("Gamma", 0.2, 3.0, 1.0, step=0.1)
                    with q_col2:
                        contrast_factor = st.slider("Contrast", 0.2, 3.0, 1.0, step=0.1)
                        sharpness_val = st.slider("Sharpness", 0.0, 3.0, 1.0, step=0.1)
                    
                    selected_filter = st.selectbox(
                        "Advanced Spatial Filter", 
                        ["None", "Smoothing / Blur", "Unsharp Mask (Pro Edge)", "Median Filter (Noise Reduction)", "Histogram Equalization"]
                    )
                    
                    # Apply Brightness & Contrast
                    img_adjusted = img_data + brightness_offset
                    mean_val = np.mean(img_adjusted)
                    img_adjusted = (img_adjusted - mean_val) * contrast_factor + mean_val
                    
                    # Apply Gamma
                    min_v, max_v = img_adjusted.min(), img_adjusted.max()
                    if max_v > min_v:
                        norm_g = np.clip((img_adjusted - min_v) / (max_v - min_v), 0, 1)
                        img_adjusted = min_v + (norm_g ** gamma_val) * (max_v - min_v)
                    
                    # Apply Spatial Filters & Sharpness via PIL
                    norm_p = np.clip((img_adjusted - min_v) / (max_v - min_v + 1e-5) * 255, 0, 255).astype(np.uint8)
                    pil_img = Image.fromarray(norm_p)
                    
                    if sharpness_val != 1.0:
                        enhancer = ImageEnhance.Sharpness(pil_img)
                        pil_img = enhancer.enhance(sharpness_val)
                        
                    if selected_filter == "Smoothing / Blur":
                        pil_img = pil_img.filter(ImageFilter.BLUR)
                    elif selected_filter == "Unsharp Mask (Pro Edge)":
                        pil_img = pil_img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
                    elif selected_filter == "Median Filter (Noise Reduction)":
                        pil_img = pil_img.filter(ImageFilter.MedianFilter(size=3))
                    elif selected_filter == "Histogram Equalization":
                        pil_img = ImageOps.equalize(pil_img)
                        
                    back = np.array(pil_img).astype(np.float32)
                    img_adjusted = min_v + (back / 255.0) * (max_v - min_v)

                    colormap_choice = st.session_state.get("colormap_choice", "bone")
                    invert_choice = st.session_state.get("invert_choice", False)
                    
                    plot_data = img_adjusted
                    if invert_choice:
                        plot_data = max_v - (img_adjusted - min_v)

                    fig, ax = plt.subplots(figsize=(5, 5))
                    ax.imshow(plot_data, cmap=colormap_choice)
                    ax.axis('off')
                    
                    img_h, img_w = img_data.shape
                    cx_default, cy_default = img_w // 2, img_h // 2
                    
                    roi_summary_data = []
                    
                    # --- RENDER SELECTED ROIS ONLY ---
                    roi_configs_all = [
                        {"name": "Center", "default_dx": 0, "default_dy": 0, "color": "red"},
                        {"name": "Top", "default_dx": 0, "default_dy": -int(img_h * 0.25), "color": "blue"},
                        {"name": "Bottom", "default_dx": 0, "default_dy": int(img_h * 0.25), "color": "green"},
                        {"name": "Left", "default_dx": -int(img_w * 0.25), "default_dy": 0, "color": "orange"},
                        {"name": "Right", "default_dx": int(img_w * 0.25), "default_dy": 0, "color": "purple"}
                    ]
                    
                    for rc in roi_configs_all:
                        r_name = rc["name"]
                        is_active = st.session_state.get(f"chk_{r_name}", False)
                        if not is_active:
                            continue
                            
                        pos_x = st.session_state.get(f"x_{r_name}", cx_default + rc["default_dx"])
                        pos_y = st.session_state.get(f"y_{r_name}", cy_default + rc["default_dy"])
                        r_shape = st.session_state.get(f"shape_{r_name}", "Circle")
                        
                        max_dim = min(img_h, img_w) // 4
                        if r_shape == "Square":
                            r_size = st.session_state.get(f"size_{r_name}", 30)
                            x1, x2 = max(0, pos_x - r_size//2), min(img_w, pos_x + r_size//2)
                            y1, y2 = max(0, pos_y - r_size//2), min(img_h, pos_y + r_size//2)
                            roi_pixels = img_data[y1:y2, x1:x2]
                            
                            rect = patches.Rectangle((x1, y1), x2 - x1, y2 - y1, linewidth=1.0, edgecolor=rc["color"], facecolor='none')
                            ax.add_patch(rect)
                            ax.text(x1, y1 - 4, r_name, color=rc["color"], fontsize=8, weight='bold')
                        else:
                            r_radius = st.session_state.get(f"rad_{r_name}", 20)
                            y_grid, x_grid = np.ogrid[:img_h, :img_w]
                            mask = (x_grid - pos_x)**2 + (y_grid - pos_y)**2 <= r_radius**2
                            roi_pixels = img_data[mask]
                            
                            circle = patches.Circle((pos_x, pos_y), r_radius, linewidth=1.0, edgecolor=rc["color"], facecolor='none')
                            ax.add_patch(circle)
                            ax.text(pos_x - r_radius, pos_y - r_radius - 4, r_name, color=rc["color"], fontsize=8, weight='bold')
                        
                        if roi_pixels.size > 0:
                            roi_summary_data.append({
                                "ROI Name": r_name,
                                "Shape": r_shape,
                                "Mean": np.mean(roi_pixels),
                                "StdDev": np.std(roi_pixels),
                                "Min": np.min(roi_pixels),
                                "Max": np.max(roi_pixels)
                            })

                    # --- RENDER DISTANCE RULER ---
                    enable_ruler = st.session_state.get("enable_ruler", False)
                    pixel_spacing_val = st.session_state.get("calib_spacing", 1.0)

                    if enable_ruler:
                        rx1 = st.session_state.get("ruler_x1", img_w // 4)
                        ry1 = st.session_state.get("ruler_y1", img_h // 2)
                        rx2 = st.session_state.get("ruler_x2", 3 * img_w // 4)
                        ry2 = st.session_state.get("ruler_y2", img_h // 2)
                        
                        ax.plot([rx1, rx2], [ry1, ry2], color='yellow', linewidth=1.0, marker='o', markersize=4)

                    # --- RENDER LINE INTENSITY PROFILE OVERLAY ---
                    enable_lp = st.session_state.get("enable_line_profile", False)
                    if enable_lp:
                        lx1 = st.session_state.get("lp_x1", img_w // 4)
                        ly1 = st.session_state.get("lp_y1", img_h // 2)
                        lx2 = st.session_state.get("lp_x2", 3 * img_w // 4)
                        ly2 = st.session_state.get("lp_y2", img_h // 2)
                        
                        ax.plot([lx1, lx2], [ly1, ly2], color='cyan', linewidth=1.0, linestyle='--', marker='o', markersize=4)

                    st.pyplot(fig)
                    
                    img_buf = io.BytesIO()
                    fig.savefig(img_buf, format="png", bbox_inches='tight', dpi=150)
                    img_buf.seek(0)
                    st.download_button("📥 Download Preview PNG", img_buf, file_name="dicom_preview.png", mime="image/png")

            with col_right_controls:
                st.subheader("⚙️ Toolbox & QC Tools")
                
                # --- 1. VISUAL ENHANCEMENTS & COLORMAPS ---
                with st.expander("🎨 Visual Enhancements & Colormaps", expanded=False):
                    st.selectbox("Color Palette", ["bone", "gray", "jet", "hot", "viridis"], key="colormap_choice")
                    st.checkbox("Invert Black/White (Invert Image)", key="invert_choice")

                # --- 2. MULTI-ROI ANALYSIS ---
                with st.expander("🎯 Multi-ROI Analysis", expanded=True):
                    st.markdown("Select ROIs to display & analyze:")
                    
                    c_chk1, c_chk2, c_chk3, c_chk4, c_chk5 = st.columns(5)
                    with c_chk1: st.checkbox("Center", key="chk_Center")
                    with c_chk2: st.checkbox("Top", key="chk_Top")
                    with c_chk3: st.checkbox("Bottom", key="chk_Bottom")
                    with c_chk4: st.checkbox("Left", key="chk_Left")
                    with c_chk5: st.checkbox("Right", key="chk_Right")
                    
                    st.markdown("---")
                    for rc in roi_configs_all:
                        r_name = rc["name"]
                        if st.session_state.get(f"chk_{r_name}", False):
                            st.markdown(f"**{r_name} ROI Settings**")
                            st.selectbox(f"Shape ({r_name})", ["Circle", "Square"], key=f"shape_{r_name}")
                            col_sx, col_sy = st.columns(2)
                            with col_sx:
                                st.slider(f"X ({r_name})", min_value=0, max_value=img_w, value=cx_default + rc["default_dx"], key=f"x_{r_name}")
                            with col_sy:
                                st.slider(f"Y ({r_name})", min_value=0, max_value=img_h, value=cy_default + rc["default_dy"], key=f"y_{r_name}")
                            
                            if st.session_state.get(f"shape_{r_name}", "Circle") == "Square":
                                st.slider(f"Size ({r_name})", min_value=5, max_value=100, value=30, key=f"size_{r_name}")
                            else:
                                st.slider(f"Radius ({r_name})", min_value=5, max_value=50, value=20, key=f"rad_{r_name}")
                            st.divider()

                # --- 3. DISTANCE RULER & CALIBRATION ---
                with st.expander("📏 Distance Ruler & Calibration", expanded=False):
                    auto_sp = 1.0
                    if hasattr(ds, "PixelSpacing") and ds.PixelSpacing:
                        try:
                            auto_sp = float(ds.PixelSpacing[0])
                        except:
                            pass
                    
                    st.markdown(f"📌 **Auto-detected Pixel Spacing:** `{auto_sp} mm/pixel`")
                    st.number_input("Resolution (mm/pixel) - Manual Override", min_value=0.001, value=auto_sp, format="%.4f", key="calib_spacing")
                    
                    st.markdown("---")
                    st.checkbox("📏 Enable Distance Ruler", key="enable_ruler")
                    if st.session_state.get("enable_ruler", False):
                        col_r1, col_r2 = st.columns(2)
                        with col_r1:
                            st.number_input("X1", 0, img_w, img_w // 4, key="ruler_x1")
                            st.number_input("Y1", 0, img_h, img_h // 2, key="ruler_y1")
                        with col_r2:
                            st.number_input("X2", 0, img_w, 3 * img_w // 4, key="ruler_x2")
                            st.number_input("Y2", 0, img_h, img_h // 2, key="ruler_y2")
                        
                        dx = st.session_state.ruler_x2 - st.session_state.ruler_x1
                        dy = st.session_state.ruler_y2 - st.session_state.ruler_y1
                        p_dist = np.sqrt(dx**2 + dy**2)
                        m_dist = p_dist * st.session_state.calib_spacing
                        st.info(f"📐 **Ruler Length:** `{p_dist:.1f} px` | `{m_dist:.2f} mm`")

                # --- 4. LINE INTENSITY PROFILE (ESF / MTF) ---
                with st.expander("📈 Line Intensity Profile (ESF / MTF)", expanded=False):
                    st.markdown("Define a line profile across an edge for spatial resolution analysis:")
                    st.checkbox("📏 Enable Line Intensity Profile", key="enable_line_profile")
                    
                    if st.session_state.get("enable_line_profile", False):
                        lp_col1, lp_col2 = st.columns(2)
                        with lp_col1:
                            st.number_input("X1 (#1)", 0, img_w, img_w // 4, key="lp_x1")
                            st.number_input("Y1 (#1)", 0, img_h, img_h // 2, key="lp_y1")
                        with lp_col2:
                            st.number_input("X2 (#2)", 0, img_w, 3 * img_w // 4, key="lp_x2")
                            st.number_input("Y2 (#2)", 0, img_h, img_h // 2, key="lp_y2")

                # --- 5. ADVANCED SNR & CNR METRICS (GRID LAYOUT) ---
                with st.expander("🔬 Advanced SNR & CNR Metrics", expanded=False):
                    if roi_summary_data:
                        st.markdown("**SNR per Active ROI:**")
                        # 2-column grid for SNR
                        snr_list = [(d['ROI Name'], (d['Mean'] / d['StdDev']) if d['StdDev'] > 0 else 0.0) for d in roi_summary_data]
                        for i in range(0, len(snr_list), 2):
                            col_s1, col_s2 = st.columns(2)
                            with col_s1:
                                st.write(f"- **{snr_list[i][0]} SNR:** `{snr_list[i][1]:.2f}`")
                            with col_s2:
                                if i + 1 < len(snr_list):
                                    st.write(f"- **{snr_list[i+1][0]} SNR:** `{snr_list[i+1][1]:.2f}`")
                        
                        means = {d["ROI Name"]: d["Mean"] for d in roi_summary_data}
                        stds = {d["ROI Name"]: d["StdDev"] for d in roi_summary_data}
                        
                        if "Center" in means and stds.get("Center", 0) > 0:
                            c_mean, c_sd = means["Center"], stds["Center"]
                            st.markdown("---")
                            st.markdown("**CNR (vs Center):**")
                            
                            cnr_list = []
                            for d in roi_summary_data:
                                if d["ROI Name"] != "Center":
                                    cnr_val = abs(d["Mean"] - c_mean) / c_sd
                                    cnr_list.append((d["ROI Name"], cnr_val))
                            
                            # 2-column grid for CNR
                            for i in range(0, len(cnr_list), 2):
                                col_c1, col_c2 = st.columns(2)
                                with col_c1:
                                    st.write(f"- **{cnr_list[i][0]} -> C:** `{cnr_list[i][1]:.2f}`")
                                with col_c2:
                                    if i + 1 < len(cnr_list):
                                        st.write(f"- **{cnr_list[i+1][0]} -> C:** `{cnr_list[i+1][1]:.2f}`")
                    else:
                        st.warning("Enable and configure ROIs in 'Multi-ROI Analysis' to calculate metrics.")

                # --- 6. UNIFORMITY & NOISE ANALYZER (GRID LAYOUT) ---
                with st.expander("🎯 Uniformity & Noise Analyzer (QC)", expanded=False):
                    if roi_summary_data:
                        means_dict = {d["ROI Name"]: d["Mean"] for d in roi_summary_data}
                        stds_dict = {d["ROI Name"]: d["StdDev"] for d in roi_summary_data}
                        
                        if "Center" in means_dict:
                            c_mean = means_dict["Center"]
                            st.markdown(f"**Center Reference Mean:** `{c_mean:.2f} {unit_label}`")
                            
                            if modality == "CT":
                                water_diff = abs(c_mean - 0.0)
                                if water_diff <= 4.0:
                                    st.success(f"✅ **CT Water Calibration: PASS** ({c_mean:.1f} HU within 0 ± 4 HU)")
                                else:
                                    st.warning(f"⚠️ **CT Water Calibration: CHECK** ({c_mean:.1f} HU outside 0 ± 4 HU)")
                            
                            periph_names = [k for k in means_dict.keys() if k != "Center"]
                            if periph_names:
                                unif_vals = []
                                st.markdown("**Peripheral Uniformity Assessment:**")
                                
                                # 2-column grid for Uniformity
                                p_items = []
                                for p_name in periph_names:
                                    p_mean = means_dict[p_name]
                                    unif_pct = 100.0 * (1.0 - abs(p_mean - c_mean) / (abs(c_mean) + 1e-5))
                                    unif_vals.append(unif_pct)
                                    p_items.append((p_name, unif_pct))
                                    
                                for i in range(0, len(p_items), 2):
                                    col_u1, col_u2 = st.columns(2)
                                    with col_u1:
                                        st.write(f"- **{p_items[i][0]}:** `{p_items[i][1]:.1f}%`")
                                    with col_u2:
                                        if i + 1 < len(p_items):
                                            st.write(f"- **{p_items[i+1][0]}:** `{p_items[i+1][1]:.1f}%`")
                                
                                avg_unif = np.mean(unif_vals)
                                avg_noise = np.mean([stds_dict[k] for k in stds_dict.keys()])
                                
                                st.markdown("---")
                                col_sum1, col_sum2 = st.columns(2)
                                with col_sum1:
                                    st.write(f"📊 **Avg Unif:** `{avg_unif:.1f}%`")
                                with col_sum2:
                                    st.write(f"📉 **Noise (SD):** `{avg_noise:.2f}`")
                                
                                if avg_unif >= 90.0:
                                    st.success("✅ **QC Status: PASS** (>= 90%)")
                                else:
                                    st.warning("⚠️ **QC Status: CHECK** (< 90%)")
                            else:
                                st.info("Enable peripheral ROIs (Top, Bottom, Left, Right) to calculate Uniformity.")
                        else:
                            st.warning("Enable the 'Center' ROI in Multi-ROI Analysis to perform Uniformity QC.")
                    else:
                        st.warning("Enable ROIs in Multi-ROI Analysis first.")

                # --- 7. DICOM HEADER EDITOR & FIXER ---
                with st.expander("✏️ DICOM Header Editor & Fixer", expanded=False):
                    st.markdown("Modify core metadata tags and download the updated DICOM file:")
                    new_pname = st.text_input("Patient Name", value=str(getattr(ds, "PatientName", "")))
                    new_pid = st.text_input("Patient ID", value=str(getattr(ds, "PatientID", "")))
                    new_study = st.text_input("Study Description", value=str(getattr(ds, "StudyDescription", "")))
                    new_inst = st.text_input("Institution Name", value=str(getattr(ds, "InstitutionName", "")))
                    
                    if st.button("💾 Apply Edits & Download DICOM"):
                        ds.PatientName = new_pname
                        ds.PatientID = new_pid
                        ds.StudyDescription = new_study
                        ds.InstitutionName = new_inst
                        
                        edited_bytes = io.BytesIO()
                        ds.save_as(edited_bytes)
                        edited_bytes.seek(0)
                        st.success("Header updated successfully!")
                        st.download_button("📥 Download Edited .dcm", edited_bytes, file_name="edited_file.dcm", mime="application/octet-stream")

                # --- 8. AUTOMATED QC REPORT GENERATOR ---
                with st.expander("📄 Automated QC Report Generator", expanded=False):
                    st.info("Coming soon: Export complete QA/QC reports with images and tables.")

                # --- MEASUREMENTS TABLE ---
                if roi_summary_data:
                    st.subheader("📋 Measurements Table")
                    df_display = pd.DataFrame([{
                        "ROI": d["ROI Name"],
                        "Mean": f"{d['Mean']:.2f}",
                        "StdDev": f"{d['StdDev']:.2f}",
                        "Min": f"{d['Min']:.1f}",
                        "Max": f"{d['Max']:.1f}"
                    } for d in roi_summary_data])
                    st.table(df_display)

            # --- DEDICATED FULL-WIDTH LINE INTENSITY PROFILE (ESF & MTF) ---
            if st.session_state.get("enable_line_profile", False):
                st.markdown("---")
                st.subheader("📈 Spatial Resolution Analysis: ESF & MTF")
                
                lx1 = st.session_state.get("lp_x1", img_w // 4)
                ly1 = st.session_state.get("lp_y1", img_h // 2)
                lx2 = st.session_state.get("lp_x2", 3 * img_w // 4)
                ly2 = st.session_state.get("lp_y2", img_h // 2)
                
                num_points = int(np.hypot(lx2 - lx1, ly2 - ly1))
                if num_points > 1:
                    x_coords = np.linspace(lx1, lx2, num_points)
                    y_coords = np.linspace(ly1, ly2, num_points)
                    
                    profile_values = img_data[np.clip(np.round(y_coords).astype(int), 0, img_h - 1),
                                              np.clip(np.round(x_coords).astype(int), 0, img_w - 1)]
                    
                    distances_mm = np.linspace(0, num_points * pixel_spacing_val, num_points)
                    
                    # 1. ESF Plot
                    fig_esf, ax_esf = plt.subplots(figsize=(10, 3.2))
                    ax_esf.plot(distances_mm, profile_values, color='crimson', linewidth=2)
                    ax_esf.set_title(f"Edge Spread Function (ESF) — {modality} ({unit_label})", fontsize=11, weight='bold')
                    ax_esf.set_xlabel("Distance along edge (mm)", fontsize=10)
                    ax_esf.set_ylabel(f"Pixel Value / Unit ({unit_label})", fontsize=10)
                    ax_esf.grid(True, linestyle='--', alpha=0.6)
                    st.pyplot(fig_esf)
                    
                    esf_buf = io.BytesIO()
                    fig_esf.savefig(esf_buf, format="png", bbox_inches='tight', dpi=150)
                    esf_buf.seek(0)
                    st.download_button("📥 Download ESF Plot PNG", esf_buf, file_name="esf_plot.png", mime="image/png")

                    # 2. MTF Calculation & MTF50 / MTF10 Metrics
                    lsf = np.abs(np.gradient(profile_values))
                    if np.sum(lsf) > 0:
                        lsf = lsf / np.sum(lsf)
                        fft_vals = np.abs(np.fft.rfft(lsf))
                        if fft_vals[0] > 0:
                            mtf = fft_vals / fft_vals[0]
                            
                            dx = pixel_spacing_val if pixel_spacing_val > 0 else 1.0
                            freqs = np.fft.rfftfreq(len(lsf), d=dx)
                            
                            try:
                                idx_50 = np.argmin(np.abs(mtf - 0.5))
                                mtf_50_freq = freqs[idx_50]
                            except:
                                mtf_50_freq = 0.0
                                
                            try:
                                idx_10 = np.argmin(np.abs(mtf - 0.1))
                                mtf_10_freq = freqs[idx_10]
                            except:
                                mtf_10_freq = 0.0
                            
                            fig_mtf, ax_mtf = plt.subplots(figsize=(10, 3.2))
                            ax_mtf.plot(freqs, mtf, color='navy', linewidth=2)
                            ax_mtf.axhline(0.5, color='gray', linestyle=':', label=f"MTF50: {mtf_50_freq:.2f} cyc/mm")
                            ax_mtf.axhline(0.1, color='orange', linestyle=':', label=f"MTF10: {mtf_10_freq:.2f} cyc/mm")
                            ax_mtf.set_title("Modulation Transfer Function (MTF)", fontsize=11, weight='bold')
                            ax_mtf.set_xlabel("Spatial Frequency (cycles/mm)", fontsize=10)
                            ax_mtf.set_ylabel("Modulation Factor (MTF)", fontsize=10)
                            ax_mtf.set_ylim(0, 1.05)
                            ax_mtf.legend(loc="upper right")
                            ax_mtf.grid(True, linestyle='--', alpha=0.6)
                            st.pyplot(fig_mtf)
                            
                            st.markdown(f"📏 **Spatial Resolution Metrics:** `MTF₅₀ = {mtf_50_freq:.2f} cyc/mm` | `MTF₁₀ (Limiting) = {mtf_10_freq:.2f} cyc/mm`")
                            
                            mtf_buf = io.BytesIO()
                            fig_mtf.savefig(mtf_buf, format="png", bbox_inches='tight', dpi=150)
                            mtf_buf.seek(0)
                            st.download_button("📥 Download MTF Plot PNG", mtf_buf, file_name="mtf_plot.png", mime="image/png")

            st.markdown("---")
            col_meta1, col_meta2 = st.columns(2)
            
            with col_meta1:
                with st.expander("📋 Key Metadata Summary"):
                    info = {
                        "Modality": modality,
                        "Portable / Mobile": "Yes ⚠️" if is_portable else "No",
                        "Patient ID": getattr(ds, "PatientID", "N/A"),
                        "Study Description": getattr(ds, "StudyDescription", "N/A"),
                        "Manufacturer": getattr(ds, "Manufacturer", "N/A"),
                        "Matrix Size": f"{getattr(ds, 'Rows', 'N/A')} x {getattr(ds, 'Columns', 'N/A')}",
                    }
                    st.table(pd.DataFrame(list(info.items()), columns=["Parameter", "Value"]))

            with col_meta2:
                with st.expander("📊 Scientific Image Statistics & Histogram"):
                    st.write(f"- **Image Mean:** {np.mean(img_data):.2f} {unit_label}")
                    st.write(f"- **Image StdDev:** {np.std(img_data):.2f}")
                    
                    fig_hist, ax_hist = plt.subplots(figsize=(4.5, 2.5))
                    ax_hist.hist(img_data.ravel(), bins=50, color='skyblue', edgecolor='black')
                    ax_hist.set_title("Pixel Intensity / HU Distribution", fontsize=10)
                    ax_hist.set_xlabel(f"Pixel Value / Unit ({unit_label})", fontsize=9)
                    ax_hist.set_ylabel("Frequency (Pixel Count)", fontsize=9)
                    st.pyplot(fig_hist)
                    
                    hist_buf = io.BytesIO()
                    fig_hist.savefig(hist_buf, format="png", bbox_inches='tight', dpi=150)
                    hist_buf.seek(0)
                    st.download_button("📥 Download Histogram PNG", hist_buf, file_name="image_histogram.png", mime="image/png")

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
