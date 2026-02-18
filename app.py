import streamlit as st
import pandas as pd
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
        for col in ['Max_Speed', 'Vertical', 'Bench', 'Squat']:
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
.player-info { margin-left: 30px; width: 100%; }
.player-name { font-size: 3rem; font-weight: 800; margin: 0; color: #ffffff; text-align: left;}
.player-meta { font-size: 1.2rem; opacity: 1; margin: 5px 0 15px 0; color: #ffffff ; text-align: left;}
.metrics { display: flex; gap: 20px; justify-content: flex-start; flex-wrap: wrap; }
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
tab_indiv, tab_team = st.tabs(["INDIVIDUAL PROFILE", "TEAM PERFORMANCE"])
metrics_list = ['Max_Speed', 'Vertical', 'Bench', 'Squat']

with tab_indiv:
    selected_player = st.selectbox("Search Athlete", sorted(df_phys['Player'].unique()))
    p_history = df_phys[df_phys['Player'] == selected_player].sort_values('Date')
    latest = p_history.iloc[-1]

    team_pbs = df_phys.groupby('Player')[metrics_list].max()
    team_ranks = team_pbs.rank(ascending=False, method='min').astype(int)
    player_pbs = team_pbs.loc[selected_player]
    player_ranks = team_ranks.loc[selected_player]

    b_val = int(player_pbs['Bench']) if pd.notna(player_pbs['Bench']) else 0
    s_val = int(player_pbs['Squat']) if pd.notna(player_pbs['Squat']) else 0

    valid_images = p_history[p_history['Image_URL'].notna() & (p_history['Image_URL'] != "")]
    current_img_url = valid_images.iloc[-1]['Image_URL'] if not valid_images.empty else ""

    st.subheader("Athlete Evaluation")
    col_img, col_info = st.columns([1,3])
    with col_img:
        st.image(get_drive_image(current_img_url), use_container_width=True)

    with col_info:
        h_str = inches_to_feet(latest.get('Height', ""))
        st.markdown(f"""
        <div class="player-info">
            <p class="player-name">{selected_player}</p>
            <p class="player-meta">{latest.get('Position','')} | Ht: {h_str} | Wt: {latest.get('Weight','')} LBS</p>
            <div class="metrics">
                <div class="metric-box"><p class="m-label">Max Speed</p><p class="m-value">{player_pbs['Max_Speed']}</p><p class="m-sub">Ranked #{player_ranks['Max_Speed']}</p></div>
                <div class="metric-box"><p class="m-label">Vertical</p><p class="m-value">{player_pbs['Vertical']}"</p><p class="m-sub">Ranked #{player_ranks['Vertical']}</p></div>
                <div class="metric-box"><p class="m-label">Bench</p><p class="m-value">{b_val}</p><p class="m-sub">Ranked #{player_ranks['Bench']}</p></div>
                <div class="metric-box"><p class="m-label">Squat</p><p class="m-value">{s_val}</p><p class="m-sub">Ranked #{player_ranks['Squat']}</p></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("Recent Evaluation History")
    recent = p_history.tail(5).copy()
    for m in metrics_list:
        vals = recent[m].values
        new_col = []
        for i in range(len(vals)):
            curr_display = int(vals[i]) if (m in ['Bench', 'Squat'] and pd.notna(vals[i])) else vals[i]
            if i == 0: new_col.append(f"{curr_display} –")
            else:
                color = "#00ff88" if vals[i] > vals[i-1] else "#ff4b4b"
                arrow = "↑" if vals[i] > vals[i-1] else ("↓" if vals[i] < vals[i-1] else "–")
                new_col.append(f"{curr_display} <span style='color:{color}'>{arrow}</span>")
        recent[m] = new_col
    
    # Rename for table display
    recent_display = recent[["Date"] + metrics_list].rename(columns={'Max_Speed': 'Max Speed'})
    recent_display['Date'] = recent_display['Date'].dt.strftime('%Y-%m-%d')
    
    st.markdown(f'<div style="text-align:center;">{recent_display.to_html(classes="vibe-table", escape=False, index=False, border=0)}</div>', unsafe_allow_html=True)

with tab_team:
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        pos_list = sorted(df_phys['Position'].dropna().unique())
        selected_pos = st.selectbox("Filter Position", ["All Positions"] + pos_list)
    
    with col_f2:
        min_date = df_phys['Date'].min().to_pydatetime()
        max_date = df_phys['Date'].max().to_pydatetime()
        date_range = st.slider("Filter Date Range", 
                               min_value=min_date, 
                               max_value=max_date, 
                               value=(min_date, max_date),
                               format="MMM DD, YYYY")

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
            top5 = range_pbs[['Player', m]].sort_values(m, ascending=False).head(5).copy()
            top5 = top5.rename(columns={m: clean_name})
            if m in ['Bench', 'Squat']:
                top5[clean_name] = top5[clean_name].fillna(0).astype(int)
            st.markdown(f"<div style='text-align:center'>{top5.to_html(classes='vibe-table', index=False, border=0)}</div>", unsafe_allow_html=True)

    st.subheader("Team Averages)")
    avg_data = range_pbs.groupby('Position')[metrics_list].mean().reset_index()
    avg_data['Max_Speed'] = avg_data['Max_Speed'].round(1)
    avg_data['Vertical'] = avg_data['Vertical'].round(1)
    avg_data['Bench'] = avg_data['Bench'].round(0).fillna(0).astype(int)
    avg_data['Squat'] = avg_data['Squat'].round(0).fillna(0).astype(int)
    
    # Final rename for the averages table
    avg_display = avg_data.rename(columns={'Max_Speed': 'Max Speed'})
    st.markdown(f"<div style='text-align:center'>{avg_display.to_html(classes="vibe-table", index=False, border=0)}</div>", unsafe_allow_html=True)
