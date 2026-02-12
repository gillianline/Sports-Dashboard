import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# -------------------
# PAGE CONFIG (MUST BE FIRST STREAMLIT COMMAND)
# -------------------
st.set_page_config(page_title="Performance Console", layout="wide")

# -------------------
# HELPER FUNCTIONS
# -------------------
def inches_to_feet(inches):
    if pd.isna(inches):
        return "N/A"
    feet = int(inches // 12)
    remaining = int(inches % 12)
    return f"{feet}'{remaining}\""

# -------------------
# GOOGLE SHEET DATA
# -------------------
sheet_url = "https://docs.google.com/spreadsheets/d/1I3SX2Cmo8jB6YiJAhrzWOunaNHUq0QT5/export?format=csv"

@st.cache_data(ttl=10)  # auto refresh every 10 seconds
def load_data():
    df = pd.read_csv(sheet_url)
    df.columns = df.columns.str.strip()

    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])

    if 'Height' in df.columns:
        df['Height'] = df['Height'].apply(inches_to_feet)

    return df

df_phys = load_data()

if df_phys.empty:
    st.warning("No data found in the Google Sheet.")
    st.stop()

# -------------------
# GLOBAL METRICS LIST
# -------------------
metrics = ['Max_Speed','Vertical','Bench','Squat']

# -------------------
# STYLING
# -------------------
st.markdown("""
<style>
.stApp { background-color: #0d1117; color: #ffffff; font-family: 'Arial', sans-serif; }
.player-card { background: linear-gradient(90deg, #161b22 0%, #1b1f27 100%); padding: 30px; border-radius: 20px; border-left: 8px solid #3880ff; margin-bottom: 25px; display: flex; align-items: center; }
.player-info { margin-left: 30px; }
.player-name { font-size: 3rem; font-weight: 800; margin: 0; color: #ffffff; }
.player-meta { font-size: 1.2rem; margin: 5px 0 15px 0; color: #d0d0d0; }
.metrics { display: flex; gap: 20px; }
.metric-box { background: #161b22; border: 1px solid rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; text-align: center; flex:1; }
.m-label { color: #00d4ff; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom:5px; }
.m-value { font-size: 2rem; font-weight: 700; color: #ffffff; margin: 0; }
.m-sub { font-size: 0.8rem; color: #a0a0a0; margin-top: 5px; }
table { color: #ffffff; width:90%; margin-left:auto; margin-right:auto; border-collapse: collapse; margin-bottom: 20px; }
th, td { padding: 10px 15px; text-align: center; color:#ffffff; }
th { color: #00d4ff; border-bottom: 1px solid rgba(255,255,255,0.2); }
td { border-bottom: 1px solid rgba(255,255,255,0.1); }
.highlight { background-color: rgba(56,128,255,0.2); border-radius:5px; padding:2px 5px; }
</style>
""", unsafe_allow_html=True)

# -------------------
# HEADER
# -------------------
st.markdown("<h1 style='letter-spacing:-2px; color:white;'>PERFORMANCE CONSOLE</h1>", unsafe_allow_html=True)

# -------------------
# PLAYER SELECTION
# -------------------
selected_player = st.selectbox("Search Athlete", df_phys['Player'].unique())
p_history = df_phys[df_phys['Player'] == selected_player].sort_values('Date')
latest = p_history.iloc[-1]

tab_indiv, tab_team = st.tabs(["INDIVIDUAL PROFILE", "TEAM PERFORMANCE"])

# -------------------
# INDIVIDUAL PROFILE
# -------------------
with tab_indiv:

    st.subheader("Player Profile")

    col_img, col_info = st.columns([1,3])

    with col_img:
        st.image("https://via.placeholder.com/250x350/161b22/00d4ff?text=ATHLETE", width=250)

    with col_info:
        st.markdown(f"""
        <div class="player-info">
            <p class="player-name">{selected_player}</p>
            <p class="player-meta">
            {latest['Position']} | Height: {latest['Height']} | 
            Weight: {latest['Weight']} LBS | 
            BF: {latest['Body_Fat']} | 
            Wingspan: {latest['Wingspan']}
            </p>
            <div class="metrics">
        """, unsafe_allow_html=True)

        for metric in metrics:
            percentile = int((latest[metric] / df_phys[metric].max()) * 100)
            st.markdown(f"""
                <div class="metric-box">
                    <p class="m-label">{metric.replace("_"," ")}</p>
                    <p class="m-value">{latest[metric]}</p>
                    <p class="m-sub">Top {percentile}% of team</p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("</div></div>", unsafe_allow_html=True)

    # Recent Table
    st.subheader("Recent Performance")
    recent = p_history.tail(5).copy()
    recent['Date'] = recent['Date'].dt.strftime('%Y-%m-%d')

    st.markdown(
        f"<div style='text-align:center'>{recent[['Date'] + metrics].to_html(index=False)}</div>",
        unsafe_allow_html=True
    )

# -------------------
# TEAM PERFORMANCE
# -------------------
with tab_team:

    st.subheader("Team Top Performers")

    for metric in metrics:
        st.markdown(f"<div style='text-align:center; color:white;'><b>Top 5 Players: {metric.replace('_',' ')}</b></div>", unsafe_allow_html=True)

        top5 = (
            df_phys.groupby('Player')[metric]
            .max()
            .sort_values(ascending=False)
            .head(5)
            .reset_index()
        )

        st.markdown(
            f"<div style='text-align:center'>{top5.to_html(index=False)}</div>",
            unsafe_allow_html=True
        )

    st.subheader("Team Averages by Position")
    avg_metrics = df_phys.groupby('Position')[metrics].mean().round(1).reset_index()
    st.table(avg_metrics)
