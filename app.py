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
# SHARED CALCULATIONS (Percentiles & Rankings)
# -------------------
metrics_list = ['Max_Speed', 'Vertical', 'Bench', 'Squat']
team_pbs = df_phys.groupby('Player')[metrics_list].max()
team_ranks = team_pbs.rank(ascending=False, method='min').astype(int)
team_percentiles = team_pbs.rank(pct=True) * 100

# -------------------
# PAGE CONFIG & CSS
# -------------------
st.set_page_config(page_title="Performance Console", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #0d1117; color: #ffffff; font-family: 'Arial', sans-serif; }
h1, h2, h3 { text-align: center !important; color: white !important; }
.stSelectbox label p, .stSlider label p { color: #00d4ff !important; font-weight: bold !important; font-size: 1.1rem !important; }
button[data-baseweb="tab"] p { color: #ffffff !important; font-weight: 600 !important; font-size: 1rem !important; }
button[data-baseweb="tab"][aria-selected="true"] { border-bottom-color: #3880ff !important; }
*:focus, *:active, .stSelectbox:focus-within, div[data-baseweb="select"] {
    outline: none !important; box-shadow: none !important; border-color: rgba(255,255,255,0.2) !important;
}
.metric-box { 
    background: #161b22; border: 1px solid rgba(255,255,255,0.1); 
    padding: 20px; border-radius: 15px; text-align: center; min-width: 150px; flex: 1; 
}
.m-label { color: #00d4ff; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom:5px; }
.m-value { font-size: 2rem; font-weight: 700; color: #ffffff; margin: 0; }
.m-sub { font-size: 0.8rem; color: #a0a0a0; margin-top: 5px; }
.vibe-table { color: #ffffff; width:100%; border-collapse: collapse; margin: 20px auto; }
.vibe-table th { color: #00d4ff; border-bottom: 1px solid rgba(255,255,255,0.2); padding: 12px; text-align: center; background-color: #1b1f27; }
.vibe-table td { padding: 12px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.1); }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='letter-spacing:-2px;'>PERFORMANCE CONSOLE</h1>", unsafe_allow_html=True)

# -------------------
# MAIN TABS
# -------------------
tab_indiv, tab_team, tab_compare = st.tabs(["INDIVIDUAL PROFILE", "TEAM PERFORMANCE", "HEAD-TO-HEAD"])

# --- INDIVIDUAL PROFILE ---
with tab_indiv:
    selected_player = st.selectbox("Search Athlete", sorted(df_phys['Player'].unique()), key="sb_indiv")
    p_history = df_phys[df_phys['Player'] == selected_player].sort_values('Date')
    latest = p_history.iloc[-1]
    
    player_pbs = team_pbs.loc[selected_player]
    player_ranks = team_ranks.loc[selected_player]
    player_pcts = team_percentiles.loc[selected_player]
    ath_score = int(player_pcts.mean())

    st.subheader("Athlete Evaluation")
    col_img, col_info, col_radar = st.columns([1.2, 2.5, 2])
    
    with col_img:
        img_df = p_history[p_history['Image_URL'].notna()]
        current_img_url = img_df.iloc[-1]['Image_URL'] if not img_df.empty else ""
        st.image(get_drive_image(current_img_url), use_container_width=True)
        st.markdown(f'<div class="metric-box" style="margin-top:10px; border: 2px solid #3880ff;"><p class="m-label">Athleticism Score</p><p class="m-value">{ath_score}</p><p class="m-sub">Team Percentile</p></div>', unsafe_allow_html=True)

    with col_info:
        h_str = inches_to_feet(latest.get('Height', ""))
        st.markdown(f"""
        <div style="margin-left:20px;">
            <p style="font-size: 2.5rem; font-weight: 800; margin: 0;">{selected_player}</p>
            <p style="font-size: 1.1rem; color: #a0a0a0; margin-bottom:20px;">{latest.get('Position','')} | Ht: {h_str} | Wt: {latest.get('Weight', 'N/A')} LBS</p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div class="metric-box"><p class="m-label">Max Speed</p><p class="m-value">{player_pbs['Max_Speed']}</p><p class="m-sub">Rank #{player_ranks['Max_Speed']}</p></div>
                <div class="metric-box"><p class="m-label">Vertical</p><p class="m-value">{player_pbs['Vertical']}"</p><p class="m-sub">Rank #{player_ranks['Vertical']}</p></div>
                <div class="metric-box"><p class="m-label">Bench</p><p class="m-value">{int(player_pbs['Bench'])}</p><p class="m-sub">Rank #{player_ranks['Bench']}</p></div>
                <div class="metric-box"><p class="m-label">Squat</p><p class="m-value">{int(player_pbs['Squat'])}</p><p class="m-sub">Rank #{player_ranks['Squat']}</p></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_radar:
        categories = ['Max Speed', 'Vertical', 'Bench', 'Squat']
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=player_pcts.values, theta=categories, fill='toself', name=selected_player, line_color='#3880ff'))
        fig.update_layout(polar=dict(bgcolor='#0d1117', radialaxis=dict(visible=True, range=[0, 100], color='white', gridcolor='rgba(255,255,255,0.1)')), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', height=350, margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Recent Evaluation History")
    recent = p_history.tail(5).copy()
    for m in metrics_list:
        vals = recent[m].values
        new_col = []
        for i in range(len(vals)):
            curr_display = int(vals[i]) if (m in ['Bench', 'Squat'] and pd.notna(vals[i])) else vals[i]
            if i == 0: 
                new_col.append(f"{curr_display} –")
            else:
                color = "#00ff88" if vals[i] > vals[i-1] else "#ff4b4b"
                arrow = "↑" if vals[i] > vals[i-1] else ("↓" if vals[i] < vals[i-1] else "–")
                new_col.append(f"{curr_display} <span style='color:{color}'>{arrow}</span>")
        recent[m] = new_col
    
    recent_display = recent[["Date"] + metrics_list].rename(columns={'Max_Speed': 'Max Speed'})
    recent_display['Date'] = recent_display['Date'].dt.strftime('%Y-%m-%d')
    st.markdown(f'<div style="text-align:center;">{recent_display.to_html(classes="vibe-table", escape=False, index=False, border=0)}</div>', unsafe_allow_html=True)

# --- TEAM PERFORMANCE ---
with tab_team:
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        pos_list = sorted(df_phys['Position'].dropna().unique())
        selected_pos = st.selectbox("Filter Position", ["All Positions"] + pos_list, key="sb_team_pos")
    with col_f2:
        min_date, max_date = df_phys['Date'].min().to_pydatetime(), df_phys['Date'].max().to_pydatetime()
        date_range = st.slider("Filter Date Range", min_value=min_date, max_value=max_date, value=(min_date, max_date), key="slider_team")

    mask = (df_phys['Date'] >= date_range[0]) & (df_phys['Date'] <= date_range[1])
    filtered_df = df_phys.loc[mask]
    range_pbs = filtered_df.groupby(['Player', 'Position'])[metrics_list].max().reset_index()

    if selected_pos != "All Positions":
        range_pbs = range_pbs[range_pbs['Position'] == selected_pos]

    st.subheader(f"Leaderboard ({date_range[0].strftime('%b %d')} - {date_range[1].strftime('%b %d')})")
    t_col1, t_col2 = st.columns(2)
    for i, m in enumerate(metrics_list):
        with (t_col1 if i % 2 == 0 else t_col2):
            clean_name = m.replace('_', ' ')
            st.markdown(f"<p style='text-align:center; color:#00d4ff; margin-top:15px;'><b>{clean_name}</b></p>", unsafe_allow_html=True)
            top5 = range_pbs[['Player', m]].sort_values(m, ascending=False).head(5).copy().rename(columns={m: clean_name})
            if m in ['Bench', 'Squat']: top5[clean_name] = top5[clean_name].fillna(0).astype(int)
            st.markdown(f"<div style='text-align:center'>{top5.to_html(classes='vibe-table', index=False, border=0)}</div>", unsafe_allow_html=True)

    # FIXED: Dynamic Average Header & Column Removal
    avg_header = "Positional Averages" if selected_pos == "All Positions" else f"{selected_pos} Averages"
    st.subheader(avg_header)
    
    avg_data = range_pbs.groupby('Position')[metrics_list].mean().round(1).reset_index()
    avg_data['Bench'] = avg_data['Bench'].fillna(0).astype(int)
    avg_data['Squat'] = avg_data['Squat'].fillna(0).astype(int)
    avg_display = avg_data.rename(columns={'Max_Speed': 'Max Speed'})

    if selected_pos != "All Positions":
        avg_display = avg_display[avg_display['Position'] == selected_pos].drop(columns=['Position'])
    
    st.markdown(f"<div style='text-align:center'>{avg_display.to_html(classes='vibe-table', index=False, border=0)}</div>", unsafe_allow_html=True)

# --- HEAD-TO-HEAD ---
with tab_compare:
    st.subheader("Head-to-Head Athlete Comparison")
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        p1 = st.selectbox("Select Athlete 1", sorted(df_phys['Player'].unique()), index=0)
    with c_col2:
        p2 = st.selectbox("Select Athlete 2", sorted(df_phys['Player'].unique()), index=1)
    
    comp_col_left, comp_col_right = st.columns([1, 1])
    
    with comp_col_left:
        categories = ['Max Speed', 'Vertical', 'Bench', 'Squat']
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Scatterpolar(r=team_percentiles.loc[p1].values, theta=categories, fill='toself', name=p1, line_color='#3880ff'))
        fig_comp.add_trace(go.Scatterpolar(r=team_percentiles.loc[p2].values, theta=categories, fill='toself', name=p2, line_color='#00ff88'))
        fig_comp.update_layout(polar=dict(bgcolor='#0d1117', radialaxis=dict(visible=True, range=[0, 100], color='white')), 
                               paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="center", x=0.5))
        st.plotly_chart(fig_comp, use_container_width=True)

    with comp_col_right:
        st.markdown("<p style='text-align:center; color:#00d4ff;'><b>Direct Comparison</b></p>", unsafe_allow_html=True)
        pb1, pb2 = team_pbs.loc[p1], team_pbs.loc[p2]
        comp_data = []
        for m in metrics_list:
            diff = round(pb1[m] - pb2[m], 1)
            color = "#3880ff" if diff > 0 else ("#00ff88" if diff < 0 else "white")
            arrow = "→" if diff == 0 else ("↑" if diff > 0 else "↓")
            comp_data.append({
                "Metric": m.replace('_',' '),
                p1: int(pb1[m]) if m in ['Bench', 'Squat'] else pb1[m],
                p2: int(pb2[m]) if m in ['Bench', 'Squat'] else pb2[m],
                "Gap": f"<span style='color:{color}'>{arrow} {abs(diff)}</span>"
            })
        st.markdown(f'<div style="text-align:center;">{pd.DataFrame(comp_data).to_html(classes="vibe-table", escape=False, index=False, border=0)}</div>', unsafe_allow_html=True)
