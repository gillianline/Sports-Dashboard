import streamlit as st
import pandas as pd

# --------------------------------------------------
# PAGE CONFIG & CUSTOM STYLING
# --------------------------------------------------
st.set_page_config(page_title="Performance Console", layout="wide")

# Add some custom CSS for that "Console" look
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    [data-testid="stMetricValue"] {
        font-size: 28px;
        color: #007BFF;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        font-weight: bold;
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# DATA ENGINE (The Fix)
# --------------------------------------------------
sheet_id = "1I3SX2Cmo8jB6YiJAhrzWOunaNHUq0QT5"
sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

@st.cache_data(ttl=10)
def load_data():
    try:
        # We use storage_options and a specific encoding to prevent the Unicode error
        df = pd.read_csv(sheet_url, encoding="utf-8")
        df.columns = df.columns.str.strip()
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        return df
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("No data found. Please check your Google Sheet sharing settings (Anyone with the link can view).")
    st.stop()

metrics = ["Max_Speed", "Vertical", "Bench", "Squat"]

# --------------------------------------------------
# SIDEBAR / FILTERS
# --------------------------------------------------
with st.sidebar:
    st.header("Console Controls")
    selected_player = st.selectbox("Select Athlete", df["Player"].unique())
    st.divider()
    st.info("Data auto-refreshes every 10 seconds.")

# Logic for selection
p_history = df[df["Player"] == selected_player].sort_values("Date")
latest = p_history.iloc[-1]

# --------------------------------------------------
# MAIN HEADER
# --------------------------------------------------
st.title("⚡ Performance Console")
st.caption(f"Last updated data for: {selected_player}")
st.divider()

tab1, tab2 = st.tabs(["👤 Individual Profile", "📊 Team Performance"])

# ==================================================
# TAB 1: INDIVIDUAL PROFILE
# ==================================================
with tab1:
    col1, col2 = st.columns([1, 2], gap="large")

    with col1:
        if "Image_URL" in df.columns:
            image_url = latest.get("Image_URL", "")
            if pd.notna(image_url) and image_url != "":
                st.image(image_url, use_container_width=True, caption=selected_player)
            else:
                st.image("https://via.placeholder.com/300x400?text=No+Photo", use_container_width=True)

    with col2:
        st.subheader(f"Athlete Bio: {selected_player}")
        
        # Grid for Bio Info
        b1, b2, b3 = st.columns(3)
        b1.write(f"**Pos:** {latest.get('Position','')}")
        b1.write(f"**Ht:** {latest.get('Height','')}")
        b2.write(f"**Wt:** {latest.get('Weight','')}")
        b2.write(f"**BF%:** {latest.get('Body_Fat','')}")
        b3.write(f"**Wingspan:** {latest.get('Wingspan','')}")

        st.markdown("### Key Metrics")
        m_cols = st.columns(len(metrics))

        for i, metric in enumerate(metrics):
            if metric in df.columns:
                max_val = df[metric].max()
                # Calculate percentile (safety check for div by zero)
                percentile = int((latest[metric] / max_val) * 100) if max_val > 0 else 0
                
                m_cols[i].metric(
                    label=metric.replace("_", " "),
                    value=latest[metric],
                    delta=f"Top {percentile}%",
                    delta_color="normal"
                )

    st.divider()
    st.subheader("📈 Performance Trend")
    recent = p_history.tail(5).copy()
    if "Date" in recent.columns:
        recent["Date"] = recent["Date"].dt.strftime("%Y-%m-%d")
    
    st.dataframe(recent[["Date"] + metrics], use_container_width=True, hide_index=True)

# ==================================================
# TAB 2: TEAM PERFORMANCE
# ==================================================
with tab2:
    st.subheader("🏆 Leaderboard (Top 5)")
    
    l_cols = st.columns(2)
    for i, metric in enumerate(metrics):
        target_col = l_cols[i % 2] # Split into two columns
        if metric in df.columns:
            with target_col:
                st.write(f"**{metric.replace('_',' ')}**")
                top5 = (
                    df.groupby("Player")[metric]
                    .max()
                    .sort_values(ascending=False)
                    .head(5)
                    .reset_index()
                )
                st.dataframe(top5, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("📋 Positional Averages")
    avg_metrics = df.groupby("Position")[metrics].mean().round(1).reset_index()
    st.table(avg_metrics) # Using table for a cleaner static look
