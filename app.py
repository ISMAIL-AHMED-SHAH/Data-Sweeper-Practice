import streamlit as st
import pandas as pd
import os
from io import BytesIO

# ---- PAGE CONFIGURATION ----
st.set_page_config(page_title="💿 Data Sweeper", layout="wide")

# ---- DARK MODE TOGGLE ----
dark_mode = st.checkbox("Toggle Dark Mode", value=False)

# ---- CUSTOM CSS ----
st.markdown(
    f"""
    <style>
        .main {{ background-color: {'#3A3A3A' if dark_mode else 'white'}; border-radius: 10px; padding: 20px; }}
        h1 {{ text-align: center; font-weight: 700; color: {'#FFFFFF' if dark_mode else '#2C3E50'}; }}
        .upload-section {{ padding: 15px; border: 2px dashed #3498DB; border-radius: 10px; }}
        .stButton button, .stDownloadButton button {{ width: 100%; border-radius: 8px; font-weight: bold; }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---- HEADER ----
st.markdown(
    """
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #578FCA,#3674B5); border-radius: 10px; color: white;">
        <h1>💿 Data Sweeper</h1>
        <p>Effortlessly transform, clean, and visualize your data.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---- FILE UPLOADER ----
st.markdown("### 📂 Upload Your File")
uploaded_file = st.file_uploader("Upload CSV, Excel (XLSX), or ODS files", type=["csv", "xlsx", "ods"])

# ---- FUNCTION TO LOAD DATA ----
@st.cache_data
def load_data(file):
    file_ext = os.path.splitext(file.name)[-1].lower()
    if file_ext == ".csv":
        return pd.read_csv(file)
    elif file_ext == ".xlsx":
        return pd.read_excel(file, engine="openpyxl")
    elif file_ext == ".ods":
        return pd.read_excel(file, engine="odf")
    else:
        return None

# ---- PROCESS FILE ----
if uploaded_file:
    df = load_data(uploaded_file)

    if df is None:
        st.error("❌ Unsupported file format.")
    else:
        st.markdown(f"#### 📄 File: {uploaded_file.name} ({uploaded_file.size / 1024:.2f} KB)")

        # ---- SEARCH BAR ----
        search_term = st.text_input("Search in DataFrame", "")
        filtered_df = df[df.astype(str).apply(lambda row: row.str.contains(search_term, case=False, na=False).any(), axis=1)] if search_term else df

        # ---- DISPLAY DATA ----
        st.markdown("### 🔍 Data Preview")
        st.dataframe(filtered_df.head())

        # ---- DATA CLEANING ----
        st.markdown("### 🧹 Data Cleaning")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🗑 Remove Duplicates"):
                df.drop_duplicates(inplace=True)
                st.success("✔ Duplicates Removed!")

        with col2:
            if st.button("🛠 Fill Missing Values"):
                df.fillna(df.mean(numeric_only=True), inplace=True)
                st.success("✔ Missing Values Filled!")

        # ---- COLUMN SELECTION ----
        st.markdown("### 🎯 Select Columns")
        selected_columns = st.multiselect("Choose columns", df.columns, default=df.columns)
        df = df[selected_columns]

        # ---- DATA VISUALIZATION ----
        st.markdown("### 📊 Data Visualization")
        if st.checkbox("📈 Show Visualization"):
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if len(numeric_cols) >= 2:
                x_column = st.selectbox("Select X Axis", numeric_cols)
                y_column = st.selectbox("Select Y Axis", numeric_cols)
                st.line_chart(df.set_index(x_column)[y_column])
            else:
                st.warning("⚠️ Need at least two numeric columns for visualization.")

        # ---- FILE CONVERSION ----
        st.markdown("### 🔄 Convert File")
        conversion_type = st.radio("Convert to:", ["CSV", "Excel"])

        if st.button("📥 Convert & Download"):
            buffer = BytesIO()
            file_name = uploaded_file.name.split(".")[0]

            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                mime_type = "text/csv"
                file_name += ".csv"
            else:
                df.to_excel(buffer, index=False, engine="openpyxl")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                file_name += ".xlsx"

            buffer.seek(0)
            st.download_button("📩 Download", data=buffer, file_name=file_name, mime=mime_type)

# ---- FOOTER ----
st.markdown("<p style='text-align: center;'>Made with ❤️ by Ismail Ahmed Shah</p>", unsafe_allow_html=True)
