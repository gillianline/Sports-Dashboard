import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

df_phys = load_data()
if df_phys.empty: st.stop()

# -------------------
# CUSTOM CSS (VIBE CHECK)
# -------------------
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    
    /* Center all subheaders and titles */
    h1, h2, h3, .centered-title { 
        text-align: center !important; 
        font-family: 'Arial Black', sans-serif;
        letter-spacing: -1px;
    }

    /* Player Card */
    .player-info { 
        background: linear-gradient(90deg, #161b22 0%, #1b1f27 100%); 
        padding: 30px; border-radius: 20px; 
        border-left: 8px solid #3880ff; border-right: 8px solid #3880ff;
        margin-bottom: 25px; text-align: center;
    }
    .player-name { font-size: 3.5rem; font-weight: 800; margin: 0; color: #ffffff; }
    
    /* Metric Boxes */
    .metrics-container { display: flex; gap: 15px; justify-content: center; margin-top: 20px; }
    .metric-box { 
        background: #0d1117; border: 1px solid #3880ff; 
        padding: 15px; border-radius: 12px; min-width: 130px; 
    }
    .m-label { color: #3880ff; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; }
    .m-value { font-size: 2rem; font-weight: 700; margin: 0; }

    /* The "Vibe" Table - Applies to Recent Performance & Position Averages */
    .vibe-table {
        margin: 20px auto;
        border-collapse: collapse;
        width: 100%;
        background-color: #161b22;
        border-radius: 15px;
        overflow: hidden;
        border: 1px solid #21262d;
    }
    .vibe-table th {
        background-color: #1b1f27;
        color: #3880ff;
        padding: 15px;
        text-transform: uppercase;
        font-size: 0.85rem;
        border-bottom: 2px solid #0d1117;
    }
    .vibe-table td {
        padding: 15px;
        text-align: center;
        border-bottom: 1px solid #21262d;
        font-family: 'Courier New', monospace;
    }
    .highlight { color: #00d4ff; font-weight: bold; text-shadow: 0 0 5px #00d4ff; }
</style>
""", unsafe_allow_html=True)

# -------------------
# MAIN UI
# -------------------
st.markdown("<h1 style='color:white; margin-bottom:0;'>PERFORMANCE CONSOLE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#3880ff; margin-top:0;'>SYSTEM STATUS: ONLINE</p>", unsafe_allow_html=True)

selected_player = st.selectbox("Search Athlete", sorted(df_phys['Player'].unique()))
p_history = df_phys[df_phys['Player'] == selected_player].sort_values('Date')
latest = p_history.iloc[-1]

tab_indiv, tab_team = st.tabs(["INDIVIDUAL PROFILE", "TEAM PERFORMANCE"])

with tab_indiv:
    st.markdown("<h3 style='margin-top:20px;'>ATHLETE DATA SHEET</h3>", unsafe_allow_html=True)
    
    # Player Bio Card
    st.markdown(f"""
    <div class="player-info">
        <p class="player-name">{selected_player.upper()}</p>
        <p style="color:#d0d0d0; font-size:1.2rem;">{latest.get('Position','')} | {latest.get('Weight','')} LBS | BF: {latest.get('Body_Fat','')}%</p>
        <div class="metrics-container">
            <div class="metric-box"><p class="m-label">Max Speed</p><p class="m-value">{latest.get('Max_Speed',0)}</p></div>
            <div class="metric-box"><p class="m-label">Vertical</p><p class="m-value">{latest.get('Vertical',0)}"</p></div>
            <div class="metric-box"><p class="m-label">Bench</p><p class="m-value">{latest.get('Bench',0)}</p></div>
            <div class="metric-box"><p class="m-label">Squat</p><p class="m-value">{latest.get('Squat',0)}</p></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Styled Recent Performance Table
    st.markdown("<h3>RECENT EVALUATIONS</h3>", unsafe_allow_html=True)
    recent = p_history.tail(5).copy()
    recent['Date'] = recent['Date'].dt.strftime('%Y-%m-%d')
    
    # Generate HTML Table with "vibe-table" class
    st.markdown(f'<div class="vibe-table">{recent[["Date", "Max_Speed", "Vertical", "Bench", "Squat"]].to_html(classes="vibe-table", index=False, border=0)}</div>', unsafe_allow_html=True)

with tab_team:
    st.markdown("<h3 style='margin-top:20px;'>POSITIONAL INTELLIGENCE</h3>", unsafe_allow_html=True)
    
    # Leaderboards
    metrics_list = ['Max_Speed','Vertical','Bench','Squat']
    cols = st.columns(2)
    for i, m in enumerate(metrics_list):
        with cols[i % 2]:
            st.markdown(f"<p style='text-align:center; color:#3880ff; font-weight:bold;'>TOP 5: {m.replace('_',' ')}</p>", unsafe_allow_html=True)
            top5 = df_phys.groupby('Player')[m].max().sort_values(ascending=False).head(5).reset_index()
            st.markdown(f'<div class="vibe-table">{top5.to_html(index=False, border=0)}</div>', unsafe_allow_html=True)

    # Position Averages - Now matching the vibe
    st.markdown("<h3>TEAM AVERAGES BY POSITION</h3>", unsafe_allow_html=True)
    avg_metrics = df_phys.groupby('Position')[metrics_list].mean().round(1).reset_index()
    
    # Injecting the same custom table class
    st.markdown(f'<div class="vibe-table">{avg_metrics.to_html(index=False, border=0)}</div>', unsafe_allow_html=True)der("Position Averages")
    avg_metrics = df_phys.groupby('Position')[metrics_list].mean().round(1).reset_index()
    st.dataframe(avg_metrics, use_container_width=True, hide_index=True)
