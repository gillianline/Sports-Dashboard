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
# GOOGLE SHEET DATA (FIXED URL)
# -------------------
sheet_id = "1I3SX2Cmo8jB6YiJAhrzWOunaNHUq0QT5"
sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

@st.cache_data(ttl=10)
def load_data():
    df = pd.read_csv(sheet_url)
    df.columns = df.columns.str.strip()
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
    # Removed the height apply here to keep logic clean, handled in display
    return df

df_phys = load_data()

if df_phys.empty:
    st.warning("No data found in the Google Sheet.")
    st.stop()

# -------------------
# PAGE CONFIG & CSS
# -------------------
st.set_page_config(page_title="Performance Console", layout="wide")
st.markdown("""
<style>
.stApp { background-color: #0d1117; color: #ffffff; font-family: 'Arial', sans-serif; }
h1, h3 { text-align: center !important; } /* CENTER TITLES */
.player-card { background: linear-gradient(90deg, #161b22 0%, #1b1f27 100%); padding: 30px; border-radius: 20px; border-left: 8px solid #3880ff; margin-bottom: 25px; display: flex; align-items: center; }
.player-info { margin-left: 30px; }
.player-name { font-size: 3rem; font-weight: 800; margin: 0; color: #ffffff; }
.player-meta { font-size: 1.2rem; opacity: 1; margin: 5px 0 15px 0; color: #d0d0d0; }
.metrics { display: flex; gap: 20px; }
.metric-box { background: #161b22; border: 1px solid rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; text-align: center; flex:1; }
.m-label { color: #00d4ff; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom:5px; }
.m-value { font-size: 2rem; font-weight: 700; color: #ffffff; margin: 0; }
.m-sub { font-size: 0.8rem; color: #a0a0a0; margin-top: 5px; }
/* VIBE TABLE STYLING */
.vibe-table { color: #ffffff; width:100%; border-collapse: collapse; margin-bottom: 20px; }
.vibe-table th { color: #00d4ff; border-bottom: 1px solid rgba(255,255,255,0.2); padding: 10px; text-align: center; }
.vibe-table td { padding: 10px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.1); }
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
    
    # Keeping your original placeholder image logic
    img_url = "https://via.placeholder.com/250x350/0d1117/3880ff?text=ATHLETE+PHOTO"

    col_img, col_info = st.columns([1,3])
    with col_img:
        st.image(img_url, width=250)
    with col_info:
        # Handling height conversion for display
        h_str = inches_to_feet(latest['Height']) if 'Height' in latest else "N/A"
        
        st.markdown(f"""
        <div class="player-info">
            <p class="player-name">{selected_player}</p>
            <p class="player-meta">{latest.get('Position','')} | Height: {h_str} | Weight: {latest.get('Weight','')} LBS | BF: {latest.get('Body_Fat','')}% | Wingspan: {latest.get('Wingspan','')}"</p>
            <div class="metrics">
                <div class="metric-box">
                    <p class="m-label">Max Speed</p>
                    <p class="m-value">{latest.get('Max_Speed',0)}</p>
                    <p class="m-sub">Top {int((latest['Max_Speed']/df_phys['Max_Speed'].max())*100) if df_phys['Max_Speed'].max() > 0 else 0}% of team</p>
                </div>
                <div class="metric-box">
                    <p class="m-label">Vertical Jump</p>
                    <p class="m-value">{latest.get('Vertical',0)}"</p>
                    <p class="m-sub">Top {int((latest['Vertical']/df_phys['Vertical'].max())*100) if df_phys['Vertical'].max() > 0 else 0}%</p>
                </div>
                <div class="metric-box">
                    <p class="m-label">Bench Press</p>
                    <p class="m-value">{latest.get('Bench',0)}</p>
                    <p class="m-sub">Top {int((latest['Bench']/df_phys['Bench'].max())*100) if df_phys['Bench'].max() > 0 else 0}%</p>
                </div>
                <div class="metric-box">
                    <p class="m-label">Squat</p>
                    <p class="m-value">{latest.get('Squat',0)}</p>
                    <p class="m-sub">Top {int((latest['Squat']/df_phys['Squat'].max())*100) if df_phys['Squat'].max() > 0 else 0}%</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Recent Performance Table
    st.subheader("Recent Performance")
    metrics = ['Max_Speed','Vertical','Bench','Squat']
    recent = p_history.tail(5).copy()
    recent['Date'] = recent['Date'].dt.strftime('%Y-%m-%d')

    st.markdown(f"""
    <div style="text-align:center;">
    {recent[['Date'] + metrics].to_html(classes="vibe-table", escape=False, index=False, border=0)}
    </div>
    """, unsafe_allow_html=True)

# -------------------
# TEAM PERFORMANCE
# -------------------
with tab_team:
    st.subheader("Team Top Performers")
    
    for metric in metrics:
        st.markdown(f"<div style='text-align:center; color:#00d4ff; margin-top:20px;'><b>Top 5 Players: {metric.replace('_',' ')}</b></div>", unsafe_allow_html=True)
        top5 = df_phys.groupby('Player')[metric].max().sort_values(ascending=False).head(5).reset_index()
        st.markdown(f"<div style='text-align:center'>{top5.to_html(classes='vibe-table', escape=False, index=False, border=0)}</div>", unsafe_allow_html=True)

    st.subheader("Team Averages by Position")
    avg_metrics = df_phys.groupby('Position')[metrics].mean().round(1).reset_index()
    
    # FIXED: Using vibe-table for position averages to match the vibes
    st.markdown(f"<div style='text-align:center'>{avg_metrics.to_html(classes='vibe-table', escape=False, index=False, border=0)}</div>", unsafe_allow_html=True)
