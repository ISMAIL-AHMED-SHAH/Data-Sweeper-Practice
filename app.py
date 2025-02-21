import streamlit as st
import pandas as pd
import os
from io import BytesIO

# ---- PAGE CONFIGURATION ----
st.set_page_config(page_title="💿 Data Sweeper", layout="wide")

# ---- LIGHT/DARK MODE TOGGLE ----
dark_mode = st.checkbox("Toggle Dark Mode", value=False)

# ---- CUSTOM CSS ----
if dark_mode:
    st.markdown("""
        <style>
            body { background-color: #2C2C2C; color: white; }
            .main { background-color: #3A3A3A; border-radius: 10px; padding: 20px; }
            h1 { text-align: center; font-weight: 700; color: #FFFFFF; }
            .upload-section { padding: 15px; border: 2px dashed #3498DB; border-radius: 10px; }
            .stButton button { width: 100%; border-radius: 8px; font-weight: bold; }
            .stDownloadButton button { width: 100%; border-radius: 8px; background-color: #28A745; color: white; }
            .stDataFrame { border-radius: 10px; }
            .icon { font-size: 22px; color: #3498DB; margin-right: 5px; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            body { background-color: #f4f7f9; color: black; }
            .main { background-color: white; border-radius: 10px; padding: 20px; }
            h1 { text-align: center; font-weight: 700; color: #2C3E50; }
            .upload-section { padding: 15px; border: 2px dashed #3498DB; border-radius: 10px; }
            .stButton button { width: 100%; border-radius: 8px; font-weight: bold; }
            .stDownloadButton button { width: 100%; border-radius: 8px; background-color: #28A745; color: white; }
            .stDataFrame { border-radius: 10px; }
            .icon { font-size: 22px; color: #3498DB; margin-right: 5px; }
        </style>
    """, unsafe_allow_html=True)

# ---- HEADER ----
st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #578FCA,#3674B5); border-radius: 10px; color: white; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);">
        <h1 style="font-size: 36px; font-weight: bold; margin-bottom: 10px;">💿 Data Sweeper</h1>
        <p style="font-size: 18px; font-weight: 400; opacity: 0.9;">Effortlessly transform, clean, and visualize your data.</p>
    </div>
""", unsafe_allow_html=True)

# ---- FILE UPLOAD SECTION ----
st.markdown(
    """
    <div style="text-align: center;">
        <h2 style="color: #4CAF50; font-size: 26px;">📂 Upload Your Files</h2>
        <p style="font-size: 16px; color: #666;">
            Upload CSV, Excel (XLSX), or ODS files for processing.
        </p>
    </div>
    """, 
    unsafe_allow_html=True
)

# File Uploader with better spacing
uploaded_files = st.file_uploader(
    label="Choose files to upload",
    type=["csv", "xlsx", "ods"],
    accept_multiple_files=True
)

# ---- SEARCH BAR ----
search_term = st.text_input("Search in DataFrame", "")

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()
        
        try:
            # ---- LOAD FILE BASED ON TYPE ----
            if file_ext == ".csv":
                df = pd.read_csv(file)
            elif file_ext == ".xlsx":
                df = pd.read_excel(file, engine="openpyxl")
            elif file_ext == ".ods":
                df = pd.read_excel(file, engine="odf")
            else:
                st.error(f"❌ Unsupported file type: {file_ext}")
                continue

            # ---- FILE DETAILS ----
            st.markdown(f"<h3>📄 {file.name}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size: 16px;'><strong>Size:</strong> {file.size / 1024:.2f} KB</p>", unsafe_allow_html=True)

            # ---- DATA PREVIEW ----
            st.markdown("#### 🔍 Data Preview")
            if search_term:
                filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
                st.dataframe(filtered_df.head())
            else:
                st.dataframe(df.head())

            # ---- DATA CLEANING ----
            st.markdown("### 🧹 Data Cleaning Options")
            if st.checkbox(f"Enable Cleaning for `{file.name}`"):
                col1, col2 = st.columns(2)

                with col1:
                    if st.button(f"🗑 Remove Duplicates from {file.name}"):
                        df.drop_duplicates(inplace=True)
                        st.success("✔ Duplicates Removed Successfully!")

                with col2:
                    if st.button(f"🛠 Fill Missing Values for {file.name}"):
                        numeric_cols = df.select_dtypes(include=['number']).columns
                        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                        st.success("✔ Missing Values Filled!")

            # ---- COLUMN SELECTION ----
            st.markdown("### 🎯 Choose Columns to Keep")
            selected_columns = st.multiselect(f"📌 Select columns for `{file.name}`", df.columns, default=df.columns)
            df = df[selected_columns]

            # ---- DATA VISUALIZATION ----
            st.markdown("### 📊 Data Visualization")
            if st.checkbox(f"📈 Show Visualization for `{file.name}`"):
                st.bar_chart(df.select_dtypes(include='number').iloc[:, :2])

            # ---- FILE CONVERSION ----
            st.markdown("### 🔄 Convert File Format")
            conversion_type = st.radio(f"📝 Convert `{file.name}` to:", ["CSV", "Excel"], key=file.name + "_convert")

            if st.button(f"📥 Convert `{file.name}`"):
                buffer = BytesIO()

                if conversion_type == "CSV":
                    df.to_csv(buffer, index=False)
                    file_name = file.name.replace(file_ext, ".csv")
                    mime_type = "text/csv"
                elif conversion_type == "Excel":
                    df.to_excel(buffer, index=False, engine="openpyxl")
                    file_name = file.name.replace(file_ext, ".xlsx")
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

                buffer.seek(0)

                st.download_button(
                    label="📩 Download Converted File",
                    data=buffer,
                    file_name=file_name,
                    mime=mime_type
                )

        except Exception as e:
            st.error(f"⚠️ Error processing `{file.name}`: {e}")

# Success message with enhanced styling
st.markdown(
    """
    <div style="text-align: center; padding: 10px; background-color: #e8f5e9; border-radius: 10px;">
        <h3 style="color: #2e7d32; font-size: 20px;">✅ All files processed successfully!</h3>
    </div>
    """,
    unsafe_allow_html=True
)
