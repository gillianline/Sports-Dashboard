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

/* TAB CENTERING */
div[data-baseweb="tabs"] { display: flex !important; justify-content: center !important; }
div[role="tablist"] { display: flex !important; justify-content: center !important; width: 100% !important; }
button[data-baseweb="tab"] { padding: 10px 40px !important; }
button[data-baseweb="tab"] p { color: #ffffff !important; font-weight: 600 !important; font-size: 1.1rem !important; }
button[data-baseweb="tab"][aria-selected="true"] { border-bottom: 3px solid #3880ff !important; }

/* DROPDOWN STYLING */
div[data-baseweb="select"] { background-color: white !important; border-radius: 8px !important; }
div[data-baseweb="select"] div { color: #0d1117 !important; }
input[data-baseweb="input"] { color: #0d1117 !important; }
div[role="listbox"] { background-color: white !important; }
div[role="option"] { color: #0d1117 !important; background-color: white !important; }

/* COMPONENT BOXES */
.metric-box { background: #161b22; border: 1px solid rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; text-align: center; }
.m-label { color: #00d4ff; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1.5px; }
.m-value { font-size: 2rem; font-weight: 700; color: #ffffff; margin: 0; }

/* TABLE STYLING */
.vibe-table { color: #ffffff; width:100%; border-collapse: collapse; margin: 0 auto; }
.vibe-table th { color: #00d4ff; border-bottom: 1px solid rgba(255,255,255,0.2); padding: 15px; background-color: #1b1f27; }
.vibe-table td { padding: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); }
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

    col_img, col_info, col_radar = st.columns([1.2, 2.5, 2])
    with col_img:
        img_df = p_history[p_history['Image_URL'].notna()]
        current_img_url = img_df.iloc[-1]['Image_URL'] if not img_df.empty else ""
        st.image(get_drive_image(current_img_url), use_container_width=True)
        st.markdown(f'<div class="metric-box" style="margin-top:10px; border: 2px solid #3880ff;"><p class="m-label">Athleticism Score</p><p class="m-value">{p_data["Ath_Score"]}</p></div>', unsafe_allow_html=True)
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
        fig = go.Figure(go.Scatterpolar(r=p_pct_row.values, theta=metrics_list, fill='toself', line_color='#3880ff'))
        fig.update_layout(polar=dict(bgcolor='#0d1117', radialaxis=dict(visible=True, range=[0, 100], color='white')), 
                         paper_bgcolor='rgba(0,0,0,0)', height=350, margin=dict(t=30, b=30))
        st.plotly_chart(fig, use_container_width=True)

# --- TEAM PERFORMANCE ---
with tab_team:
    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        selected_pos = st.selectbox("Filter Position", ["All Positions"] + sorted(df_phys['Position'].dropna().unique()), key="sb_team_pos")
    with col_f2:
        st.write("") # Spacer
        date_range = st.slider("Filter Date Range", min_value=df_phys['Date'].min().to_pydatetime(), max_value=df_phys['Date'].max().to_pydatetime(), value=(df_phys['Date'].min().to_pydatetime(), df_phys['Date'].max().to_pydatetime()))

# --- HEAD TO HEAD ---
with tab_compare:
    # 1. Centered Selectors with better spacing
    st.write("### Choose Athletes")
    _, c1, c2, _ = st.columns([0.5, 1, 1, 0.5])
    with c1:
        p1_name = st.selectbox("Athlete 1", team_pbs['Player'].values, index=0, key="comp_1")
    with c2:
        p2_name = st.selectbox("Athlete 2", team_pbs['Player'].values, index=1, key="comp_2")
    
    st.markdown("---")
    
    # 2. Layout Balancing: The Radar and the Table
    col_l, col_r = st.columns([1.2, 1])
    
    p1_data = team_pbs[team_pbs['Player'] == p1_name].iloc[0]
    p2_data = team_pbs[team_pbs['Player'] == p2_name].iloc[0]
    p1_pct = team_percentiles.iloc[p1_data.name]
    p2_pct = team_percentiles.iloc[p2_data.name]

    with col_l:
        # Pushing the radar chart down slightly to align with table header
        st.write("") 
        categories = ['Max Speed', 'Vertical', 'Bench', 'Squat']
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Scatterpolar(r=p1_pct.values, theta=categories, fill='toself', name=p1_name, line_color='#3880ff'))
        fig_comp.add_trace(go.Scatterpolar(r=p2_pct.values, theta=categories, fill='toself', name=p2_name, line_color='#00ff88'))
        fig_comp.update_layout(
            polar=dict(bgcolor='#0d1117', radialaxis=dict(visible=True, range=[0, 100], color='rgba(255,255,255,0.2)')),
            paper_bgcolor='rgba(0,0,0,0)', 
            font=dict(color="white"),
            legend=dict(font=dict(color="white", size=14), orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
            margin=dict(t=80, b=20)
        )
        st.plotly_chart(fig_comp, use_container_width=True)

    with col_r:
        st.markdown(f"<h3 style='text-align:left !important; margin-bottom:30px;'>Comparison Breakdown</h3>", unsafe_allow_html=True)
        comp_data = []
        for m in metrics_list:
            diff = round(p1_data[m] - p2_data[m], 1)
            color = "#3880ff" if diff > 0 else ("#00ff88" if diff < 0 else "white")
            arrow = "→" if diff == 0 else ("↑" if diff > 0 else "↓")
            comp_data.append({
                "Metric": m.replace('_',' '), 
                p1_name: int(p1_data[m]) if m in ['Bench', 'Squat'] else p1_data[m], 
                p2_name: int(p2_data[m]) if m in ['Bench', 'Squat'] else p2_data[m], 
                "Gap": f"<span style='color:{color}'>{arrow} {abs(diff)}</span>"
            })
        st.markdown(f'{pd.DataFrame(comp_data).to_html(classes="vibe-table", escape=False, index=False, border=0)}', unsafe_allow_html=True)
