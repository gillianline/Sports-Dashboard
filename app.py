import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# -------------------
# HELPER FUNCTIONS
# -------------------
def inches_to_feet(inches):
    if pd.isna(inches) or inches == "": return "N/A"
    try:
        val = float(inches)
        return f"{int(val // 12)}'{int(val % 12)}\""
    except: return str(inches)

def get_drive_image(url):
    if pd.isna(url) or "drive.google.com" not in str(url):
        return "https://via.placeholder.com/250x350/0d1117/3880ff?text=PHOTO+MISSING"
    try:
        if "id=" in str(url):
            file_id = str(url).split("id=")[1].split("&")[0]
        elif "/d/" in str(url):
            file_id = str(url).split("/d/")[1].split("/")[0]
        else: return url
        return f"https://drive.google.com/thumbnail?id={file_id}&sz=w1000"
    except: return url

# -------------------
# DATA ENGINE
# -------------------
sheet_id = "1I3SX2Cmo8jB6YiJAhrzWOunaNHUq0QT5"
sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

@st.cache_data(ttl=10)
def load_data():
    try:
        df = pd.read_csv(sheet_url)
        df.columns = df.columns.str.strip()
        for col in ['Max_Speed', 'Vertical', 'Bench', 'Squat', 'Weight']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Data Error: {e}")
        return pd.DataFrame()

df_phys = load_data()
if df_phys.empty: st.stop()

# -------------------
# SHARED CALCULATIONS
# -------------------
metrics_list = ['Max_Speed', 'Vertical', 'Bench', 'Squat']
team_pbs = df_phys.groupby(['Player', 'Position'])[metrics_list].max().reset_index()
team_ranks = team_pbs[metrics_list].rank(ascending=False, method='min').astype(int)
team_percentiles = team_pbs[metrics_list].rank(pct=True) * 100
team_pbs['Ath_Score'] = team_percentiles.mean(axis=1).astype(int)

# -------------------
# PAGE CONFIG & CSS
# -------------------
st.set_page_config(page_title="Performance Console", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #0d1117; color: #ffffff; font-family: 'Arial', sans-serif; }
h1, h2, h3 { text-align: center !important; color: white !important; padding-top: 10px; }

/* DROPDOWN STYLING: Forced White/Dark */
div[data-baseweb="select"] { background-color: white !important; border-radius: 8px !important; }
div[data-baseweb="select"] div { color: #0d1117 !important; }
input[data-baseweb="input"] { color: #0d1117 !important; }

/* COMPONENT BOXES */
.metric-box { background: #161b22; border: 1px solid rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; text-align: center; }
.m-label { color: #00d4ff; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1.5px; }
.m-value { font-size: 2rem; font-weight: 700; color: #ffffff; margin: 0; }

/* BADGE STYLING */
.status-badge {
    padding: 8px 15px; border-radius: 50px; font-weight: 800; font-size: 0.8rem; 
    text-transform: uppercase; letter-spacing: 1px; margin-top: 15px; display: inline-block;
}
.elite { background: rgba(56, 128, 255, 0.2); border: 1px solid #3880ff; color: #3880ff; box-shadow: 0 0 15px rgba(56, 128, 255, 0.3); }
.advanced { background: rgba(0, 212, 255, 0.2); border: 1px solid #00d4ff; color: #00d4ff; }
.solid { background: rgba(255, 255, 255, 0.1); border: 1px solid #ffffff; color: #ffffff; }
.dev { background: rgba(160, 160, 160, 0.1); border: 1px solid #a0a0a0; color: #a0a0a0; }

/* TAB CENTERING */
div[data-baseweb="tabs"] { display: flex !important; justify-content: center !important; }
div[role="tablist"] { display: flex !important; justify-content: center !important; width: 100% !important; }
button[data-baseweb="tab"] { padding: 10px 40px !important; }
button[data-baseweb="tab"] p { color: #ffffff !important; font-weight: 600 !important; font-size: 1.1rem !important; }
button[data-baseweb="tab"][aria-selected="true"] { border-bottom: 3px solid #3880ff !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>PERFORMANCE CONSOLE</h1>", unsafe_allow_html=True)

tab_indiv, tab_team, tab_compare = st.tabs(["INDIVIDUAL", "TEAM", "HEAD TO HEAD"])

# --- INDIVIDUAL PROFILE ---
with tab_indiv:
    _, col_sel, _ = st.columns([1, 1, 1])
    with col_sel:
        selected_player = st.selectbox("Search Athlete", sorted(df_phys['Player'].unique()), key="sb_indiv")
    
    p_history = df_phys[df_phys['Player'] == selected_player].sort_values('Date')
    latest = p_history.iloc[-1]
    p_data = team_pbs[team_pbs['Player'] == selected_player].iloc[0]
    p_rank_row = team_ranks.iloc[p_data.name]
    p_pct_row = team_percentiles.iloc[p_data.name]

    # BADGE LOGIC
    score = p_data["Ath_Score"]
    if score >= 90: b_class, b_text = "elite", "ELITE PROSPECT"
    elif score >= 75: b_class, b_text = "advanced", "ADVANCED LEVEL"
    elif score >= 50: b_class, b_text = "solid", "SOLID PERFORMER"
    else: b_class, b_text = "dev", "DEVELOPMENTAL"

    col_img, col_info, col_radar = st.columns([1.2, 2.5, 2])
    with col_img:
        img_df = p_history[p_history['Image_URL'].notna()]
        current_img_url = img_df.iloc[-1]['Image_URL'] if not img_df.empty else ""
        st.image(get_drive_image(current_img_url), use_container_width=True)
        
        # ATH SCORE BOX + NEW BADGE UNDERNEATH
        st.markdown(f"""
            <div class="metric-box" style="margin-top:10px; border: 2px solid #3880ff;">
                <p class="m-label">Athleticism Score</p>
                <p class="m-value">{score}</p>
                <div class="status-badge {b_class}">{b_text}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col_info:
        st.markdown(f"""
        <div style="margin-left:20px;">
            <p style="font-size: 2.5rem; font-weight: 800; margin: 0;">{selected_player}</p>
            <p style="color: #a0a0a0; margin-bottom:20px;">{latest.get('Position','')} | {latest.get('Weight', 'N/A')} LBS</p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div class="metric-box"><p class="m-label">Max Speed</p><p class="m-value">{p_data['Max_Speed']}</p></div>
                <div class="metric-box"><p class="m-label">Vertical</p><p class="m-value">{p_data['Vertical']}"</p></div>
                <div class="metric-box"><p class="m-label">Bench</p><p class="m-value">{int(p_data['Bench'])}</p></div>
                <div class="metric-box"><p class="m-label">Squat</p><p class="m-value">{int(p_data['Squat'])}</p></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_radar:
        fig = go.Figure(go.Scatterpolar(r=p_pct_row.values, theta=['Speed', 'Vert', 'Bench', 'Squat'], fill='toself', line_color='#3880ff'))
        fig.update_layout(polar=dict(bgcolor='#0d1117', radialaxis=dict(visible=True, range=[0, 100], color='white')), 
                         paper_bgcolor='rgba(0,0,0,0)', height=380, margin=dict(t=50, b=50))
        st.plotly_chart(fig, use_container_width=True)
