import streamlit as st
import pandas as pd

# --------------------------------------------------
# PAGE CONFIG (MUST BE FIRST)
# --------------------------------------------------
st.set_page_config(page_title="Performance Console", layout="wide")

# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------
def inches_to_feet(value):
    if isinstance(value, str):
        return value
    if pd.isna(value):
        return "N/A"
    try:
        value = float(value)
        feet = int(value // 12)
        remainder = int(value % 12)
        return f"{feet}'{remainder}\""
    except:
        return "N/A"

# --------------------------------------------------
# GOOGLE SHEET
# --------------------------------------------------
sheet_url = "https://docs.google.com/spreadsheets/d/1I3SX2Cmo8jB6YiJAhrzWOunaNHUq0QT5/export?format=csv"

@st.cache_data(ttl=10)
def load_data():
    df = pd.read_csv(sheet_url)
    df.columns = df.columns.str.strip()

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    if "Height" in df.columns:
        df["Height"] = df["Height"].apply(inches_to_feet)

    return df

df_phys = load_data()

if df_phys.empty:
    st.warning("No data found.")
    st.stop()

metrics = ["Max_Speed", "Vertical", "Bench", "Squat"]

# --------------------------------------------------
# CLEAN DARK THEME CSS (FORCES WHITE + CENTER)
# --------------------------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #0d1117;
    color: #ffffff;
    font-family: Arial, sans-serif;
}

/* Fix ALL table headers */
thead tr th {
    color: #ffffff !important;
    text-align: center !important;
    background-color: #161b22 !important;
}

/* Fix ALL table cells */
tbody tr td {
    color: #ffffff !important;
    text-align: center !important;
}

/* Remove grey header styling Streamlit applies */
[data-testid="stTable"] {
    color: white !important;
}

/* Player styling */
.player-name {
    font-size: 2.8rem;
    font-weight: 800;
    margin: 0;
    color: #ffffff;
}

.player-meta {
    font-size: 1.1rem;
    margin: 8px 0 15px 0;
    color: #d0d0d0;
}

.metrics {
    display: flex;
    gap: 20px;
}

.metric-box {
    background: #161b22;
    border: 1px solid rgba(255,255,255,0.1);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    flex:1;
}

.m-label {
    color: #00d4ff;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom:5px;
}

.m-value {
    font-size: 2rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0;
}

.m-sub {
    font-size: 0.8rem;
    color: #a0a0a0;
    margin-top: 5px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown("<h1 style='letter-spacing:-2px;'>PERFORMANCE CONSOLE</h1>", unsafe_allow_html=True)

# --------------------------------------------------
# PLAYER SELECT
# --------------------------------------------------
selected_player = st.selectbox("Search Athlete", df_phys["Player"].unique())
p_history = df_phys[df_phys["Player"] == selected_player].sort_values("Date")
latest = p_history.iloc[-1]

tab1, tab2 = st.tabs(["INDIVIDUAL PROFILE", "TEAM PERFORMANCE"])

# ==================================================
# INDIVIDUAL PROFILE
# ==================================================
with tab1:

    st.subheader("Player Profile")

    col_img, col_info = st.columns([1, 3])

    with col_img:
        # Reliable image that always loads
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png",
            width=250
        )

    with col_info:
        st.markdown(f"""
        <p class="player-name">{selected_player}</p>
        <p class="player-meta">
        {latest.get('Position','')} |
        Height: {latest.get('Height','')} |
        Weight: {latest.get('Weight','')} LBS |
        BF: {latest.get('Body_Fat','')} |
        Wingspan: {latest.get('Wingspan','')}
        </p>
        """, unsafe_allow_html=True)

        st.markdown("<div class='metrics'>", unsafe_allow_html=True)

        for metric in metrics:
            if metric in df_phys.columns:
                percentile = int((latest[metric] / df_phys[metric].max()) * 100)
                st.markdown(f"""
                    <div class="metric-box">
                        <p class="m-label">{metric.replace("_"," ")}</p>
                        <p class="m-value">{latest[metric]}</p>
                        <p class="m-sub">Top {percentile}% of team</p>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # Recent Performance
    st.subheader("Recent Performance")

    recent = p_history.tail(5).copy()
    if "Date" in recent.columns:
        recent["Date"] = recent["Date"].dt.strftime("%Y-%m-%d")

    display_cols = ["Date"] + metrics
    display_cols = [col for col in display_cols if col in recent.columns]

    st.markdown(
        f"<div>{recent[display_cols].to_html(index=False)}</div>",
        unsafe_allow_html=True
    )

# ==================================================
# TEAM PERFORMANCE
# ==================================================
with tab2:

    st.subheader("Team Top Performers")

    for metric in metrics:
        if metric in df_phys.columns:

            st.markdown(
                f"<div style='text-align:center; font-weight:bold;'>Top 5 Players: {metric.replace('_',' ')}</div>",
                unsafe_allow_html=True
            )

            top5 = (
                df_phys.groupby("Player")[metric]
                .max()
                .sort_values(ascending=False)
                .head(5)
                .reset_index()
            )

            st.markdown(
                top5.to_html(index=False),
                unsafe_allow_html=True
            )

    st.subheader("Team Averages by Position")

    avg_metrics = (
        df_phys.groupby("Position")[metrics]
        .mean()
        .round(1)
        .reset_index()
    )

    st.markdown(avg_metrics.to_html(index=False), unsafe_allow_html=True)
