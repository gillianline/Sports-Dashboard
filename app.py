import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random

# -------------------
# HELPER FUNCTIONS
# -------------------
def inches_to_feet(inches):
    """Convert inches to feet/inches string"""
    if pd.isna(inches):
        return "N/A"
    feet = int(inches // 12)
    remaining = int(inches % 12)
    return f"{feet}'{remaining}\""

# -------------------
# GOOGLE SHEET DATA
# -------------------
# Replace YOUR_SHEET_ID with your Google Sheet ID
sheet_url = "https://docs.google.com/spreadsheets/d/1I3SX2Cmo8jB6YiJAhrzWOunaNHUq0QT5/edit?usp=sharing&ouid=107856439302599552529&rtpof=true&sd=true"

@st.cache_data(ttl=30)
def load_data():
    st.cache_data(ttl=30)
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
# PAGE CONFIG
# -------------------
st.set_page_config(page_title="Performance Console", layout="wide")
st.markdown("""
<style>
.stApp { background-color: #0d1117; color: #ffffff; font-family: 'Arial', sans-serif; }
.player-card { background: linear-gradient(90deg, #161b22 0%, #1b1f27 100%); padding: 30px; border-radius: 20px; border-left: 8px solid #3880ff; margin-bottom: 25px; display: flex; align-items: center; }
.player-info { margin-left: 30px; }
.player-name { font-size: 3rem; font-weight: 800; margin: 0; color: #ffffff; }
.player-meta { font-size: 1.2rem; opacity: 1; margin: 5px 0 15px 0; color: #d0d0d0; }
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
# DASHBOARD HEADER
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
    # Fake images for demo
    fake_images = [
        "https://via.placeholder.com/250x350/0d1117/3880ff?text=ATHLETE+PHOTO",
        "https://via.placeholder.com/250x350/161b22/00d4ff?text=PLAYER",
        "https://via.placeholder.com/250x350/1b1f27/00d4ff?text=ATHLETE"
    ]
    img_url = random.choice(fake_images)

    col_img, col_info = st.columns([1,3])
    with col_img:
        st.image(img_url, width=250)
    with col_info:
        st.markdown(f"""
        <div class="player-info">
            <p class="player-name">{selected_player}</p>
            <p class="player-meta">{latest['Position']} | Height: {latest['Height']} | Weight: {latest['Weight']} LBS | BF: {latest['Body_Fat']} | Wingspan: {latest['Wingspan']}</p>
            <div class="metrics">
                <div class="metric-box">
                    <p class="m-label">Max Speed</p>
                    <p class="m-value">{latest['Max_Speed']}</p>
                    <p class="m-sub">Top {int((latest['Max_Speed']/df_phys['Max_Speed'].max())*100)}% of team</p>
                </div>
                <div class="metric-box">
                    <p class="m-label">Vertical Jump</p>
                    <p class="m-value">{latest['Vertical']}"</p>
                    <p class="m-sub">Top {int((latest['Vertical']/df_phys['Vertical'].max())*100)}%</p>
                </div>
                <div class="metric-box">
                    <p class="m-label">Bench Press</p>
                    <p class="m-value">{latest['Bench']}</p>
                    <p class="m-sub">Top {int((latest['Bench']/df_phys['Bench'].max())*100)}%</p>
                </div>
                <div class="metric-box">
                    <p class="m-label">Squat</p>
                    <p class="m-value">{latest['Squat']}</p>
                    <p class="m-sub">Top {int((latest['Squat']/df_phys['Squat'].max())*100)}%</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Recent Performance Table
    st.subheader("Recent Performance")
    metrics = ['Max_Speed','Vertical','Bench','Squat']
    recent = p_history.tail(5).copy()
    recent['Date'] = recent['Date'].dt.strftime('%Y-%m-%d')

    # Build trend arrows
    for metric in metrics:
        recent[f"{metric}_Trend"] = "–"
        vals = recent[metric].values
        for i in range(1, len(vals)):
            recent.loc[recent.index[i], f"{metric}_Trend"] = "↑" if vals[i]>vals[i-1] else ("↓" if vals[i]<vals[i-1] else "–")

    display_cols = ['Date']
    for metric in metrics:
        display_cols.extend([metric, f"{metric}_Trend"])

    st.markdown(f"""
    <div style="text-align:center;">
    {recent[display_cols].to_html(escape=False, index=False)}
    </div>
    """, unsafe_allow_html=True)

# -------------------
# TEAM PERFORMANCE
# -------------------
with tab_team:
    st.subheader("Team Top Performers")
    metric_labels = {
        'Max_Speed': 'Max Speed',
        'Vertical': 'Vertical Jump',
        'Bench': 'Bench Press',
        'Squat': 'Squat'
    }

    for metric in metrics:
        st.markdown(f"<div style='text-align:center; color:white;'><b>Top 5 Players: {metric_labels[metric]}</b></div>", unsafe_allow_html=True)
        top5 = df_phys.groupby('Player')[metric].max().sort_values(ascending=False).head(5).reset_index()
        top5_display = top5.rename(columns={metric: metric_labels[metric]})
        top5_display.iloc[0,1] = f"<span class='highlight'>{top5_display.iloc[0,1]}</span>"
        st.markdown(f"<div style='text-align:center'>{top5_display.to_html(escape=False, index=False)}</div>", unsafe_allow_html=True)

    st.subheader("Team Averages by Position")
    avg_metrics = df_phys.groupby('Position')[metrics].mean().round(1).reset_index()
    avg_metrics = avg_metrics.rename(columns=metric_labels)
    st.table(avg_metrics)
