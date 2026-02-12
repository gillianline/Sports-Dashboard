import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
from streamlit_autorefresh import st_autorefresh

# -------------------
# PAGE CONFIG (Must be first)
# -------------------
st.set_page_config(page_title="Performance Console", layout="wide")

# -------------------
# AUTO REFRESH EVERY 10 SECONDS
# -------------------
st_autorefresh(interval=10000, key="data_refresh")

# -------------------
# HELPER FUNCTIONS
# -------------------
def inches_to_feet(inches):
    """Convert inches to feet/inches string"""
    try:
        if pd.isna(inches) or inches == "":
            return "N/A"
        val = float(inches)
        feet = int(val // 12)
        remaining = int(val % 12)
        return f"{feet}'{remaining}\""
    except:
        return str(inches)

# -------------------
# DATA ENGINE (Google Sheets Fix)
# -------------------
sheet_id = "1I3SX2Cmo8jB6YiJAhrzWOunaNHUq0QT5"
sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

@st.cache_data(ttl=10)
def load_data():
    try:
        df = pd.read_csv(sheet_url)
        df.columns = df.columns.str.strip()
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        # We process the height for display but keep numeric for logic if needed
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df_phys = load_data()

if df_phys.empty:
    st.warning("No data found. Ensure the Google Sheet is shared as 'Anyone with the link can view'.")
    st.stop()

# -------------------
# CUSTOM CSS STYLING
# -------------------
st.markdown("""
<style>
.stApp { background-color: #0d1117; color: #ffffff; font-family: 'Arial', sans-serif; }
/* Player Card Styling */
.player-info { 
    background: linear-gradient(90deg, #161b22 0%, #1b1f27 100%); 
    padding: 30px; 
    border-radius: 20px; 
    border-left: 8px solid #3880ff; 
    margin-bottom: 25px; 
}
.player-name { font-size: 3rem; font-weight: 800; margin: 0; color: #ffffff; line-height:1; }
.player-meta { font-size: 1.1rem; opacity: 0.8; margin: 10px 0 20px 0; color: #d0d0d0; }
/* Metric Box Styling */
.metrics-container { display: flex; gap: 15px; flex-wrap: wrap; }
.metric-box { 
    background: #0d1117; 
    border: 1px solid rgba(255,255,255,0.1); 
    padding: 15px; 
    border-radius: 12px; 
    text-align: center; 
    min-width: 140px;
    flex: 1;
}
.m-label { color: #3880ff; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom:5px; font-weight: bold;}
.m-value { font-size: 1.8rem; font-weight: 700; color: #ffffff; margin: 0; }
.m-sub { font-size: 0.7rem; color: #888; margin-top: 5px; }
/* Table Styling */
table { width: 100%; border-collapse: collapse; color: white; background: #161b22; border-radius: 10px; overflow: hidden; }
th { background: #1b1f27; color: #3880ff; padding: 12px; text-align: center; border-bottom: 2px solid #0d1117; }
td { padding: 12px; text-align: center; border-bottom: 1px solid #21262d; }
.highlight { color: #00d4ff; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# -------------------
# DASHBOARD HEADER
# -------------------
st.markdown("<h1 style='letter-spacing:-2px; color:white; margin-bottom:0;'>PERFORMANCE CONSOLE</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#3880ff; margin-top:0;'>Live Athlete Analytics Engine</p>", unsafe_allow_html=True)

# -------------------
# PLAYER SELECTION
# -------------------
all_players = sorted(df_phys['Player'].unique())
selected_player = st.selectbox("Search Athlete", all_players)

# Filter Data
p_history = df_phys[df_phys['Player'] == selected_player].sort_values('Date')
latest = p_history.iloc[-1]

tab_indiv, tab_team = st.tabs(["INDIVIDUAL PROFILE", "TEAM PERFORMANCE"])

# -------------------
# INDIVIDUAL PROFILE
# -------------------
with tab_indiv:
    col_img, col_info = st.columns([1,3], gap="large")
    
    with col_img:
        # Check for image URL in sheet, otherwise use placeholder
        img_url = latest.get('Image_URL', "https://via.placeholder.com/250x350/161b22/3880ff?text=ATHLETE+PHOTO")
        if pd.isna(img_url) or img_url == "":
            img_url = "https://via.placeholder.com/250x350/161b22/3880ff?text=PHOTO+MISSING"
        st.image(img_url, use_container_width=True)

    with col_info:
        # Convert height for display
        display_height = inches_to_feet(latest.get('Height', 0))
        
        # Player Bio Card
        st.markdown(f"""
        <div class="player-info">
            <p class="player-name">{selected_player.upper()}</p>
            <p class="player-meta">
                {latest.get('Position','N/A')} &nbsp;|&nbsp; 
                HT: {display_height} &nbsp;|&nbsp; 
                WT: {latest.get('Weight','N/A')} LBS &nbsp;|&nbsp; 
                BF: {latest.get('Body_Fat','N/A')}% &nbsp;|&nbsp; 
                WINGSPAN: {latest.get('Wingspan','N/A')}"
            </p>
            <div class="metrics-container">
                <div class="metric-box">
                    <p class="m-label">Max Speed</p>
                    <p class="m-value">{latest.get('Max_Speed', 0)}</p>
                    <p class="m-sub">Top {int((latest['Max_Speed']/df_phys['Max_Speed'].max())*100) if df_phys['Max_Speed'].max() > 0 else 0}%</p>
                </div>
                <div class="metric-box">
                    <p class="m-label">Vertical</p>
                    <p class="m-value">{latest.get('Vertical', 0)}"</p>
                    <p class="m-sub">Top {int((latest['Vertical']/df_phys['Vertical'].max())*100) if df_phys['Vertical'].max() > 0 else 0}%</p>
                </div>
                <div class="metric-box">
                    <p class="m-label">Bench</p>
                    <p class="m-value">{latest.get('Bench', 0)}</p>
                    <p class="m-sub">Top {int((latest['Bench']/df_phys['Bench'].max())*100) if df_phys['Bench'].max() > 0 else 0}%</p>
                </div>
                <div class="metric-box">
                    <p class="m-label">Squat</p>
                    <p class="m-value">{latest.get('Squat', 0)}</p>
                    <p class="m-sub">Top {int((latest['Squat']/df_phys['Squat'].max())*100) if df_phys['Squat'].max() > 0 else 0}%</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Recent Performance with Trends
    st.subheader("Recent Performance")
    metrics_list = ['Max_Speed','Vertical','Bench','Squat']
    recent = p_history.tail(5).copy()
    recent['Date'] = recent['Date'].dt.strftime('%Y-%m-%d')

    # Calculate Trends
    for m in metrics_list:
        recent[f"{m}_Trend"] = "–"
        vals = recent[m].values
        for i in range(1, len(vals)):
            if vals[i] > vals[i-1]:
                recent.iloc[i, recent.columns.get_loc(f"{m}_Trend")] = "<span style='color:#00ff88'>↑</span>"
            elif vals[i] < vals[i-1]:
                recent.iloc[i, recent.columns.get_loc(f"{m}_Trend")] = "<span style='color:#ff4b4b'>↓</span>"

    # Merge value and trend for display
    display_df = recent[['Date']].copy()
    for m in metrics_list:
        display_df[m.replace('_', ' ')] = recent[m].astype(str) + " " + recent[f"{m}_Trend"]

    st.markdown(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)

# -------------------
# TEAM PERFORMANCE
# -------------------
with tab_team:
    st.subheader("Team Leaderboard")
    
    # Leaderboard grid
    l_col1, l_col2 = st.columns(2)
    
    for i, m in enumerate(metrics_list):
        target_col = l_col1 if i % 2 == 0 else l_col2
        with target_col:
            st.markdown(f"<p style='color:#3880ff; font-weight:bold; margin-bottom:5px;'>TOP 5: {m.replace('_',' ')}</p>", unsafe_allow_html=True)
            top5 = df_phys.groupby('Player')[m].max().sort_values(ascending=False).head(5).reset_index()
            # Highlight #1
            top5[m] = top5[m].astype(str)
            top5.iloc[0, 1] = f"<span class='highlight'>{top5.iloc[0,1]} ⭐</span>"
            st.markdown(top5.to_html(escape=False, index=False), unsafe_allow_html=True)
            st.write("")

    st.subheader("Position Averages")
    avg_metrics = df_phys.groupby('Position')[metrics_list].mean().round(1).reset_index()
    st.dataframe(avg_metrics, use_container_width=True, hide_index=True)
