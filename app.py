import streamlit as st
import pandas as pd

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
/* 1. Global & Text */
.stApp { background-color: #0d1117; color: #ffffff; font-family: 'Arial', sans-serif; }
h1, h2, h3 { text-align: center !important; color: white !important; }

/* 2. Search Athlete Label & Tab Colors */
.stSelectbox label p { color: #00d4ff !important; font-weight: bold !important; font-size: 1.1rem !important; }
button[data-baseweb="tab"] p { color: #ffffff !important; font-weight: 600 !important; font-size: 1rem !important; }
button[data-baseweb="tab"][aria-selected="true"] { border-bottom-color: #3880ff !important; }

/* 3. Kill the "Weird Shadow" / Focus Highlight */
*:focus, *:active, .stSelectbox:focus-within, div[data-baseweb="select"] {
    outline: none !important;
    box-shadow: none !important;
    border-color: rgba(255,255,255,0.2) !important;
}

/* 4. Layout Components */
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

/* 5. Tables */
.vibe-table { color: #ffffff; width:100%; border-collapse: collapse; margin: 20px auto; }
.vibe-table th { color: #00d4ff; border-bottom: 1px solid rgba(255,255,255,0.2); padding: 12px; text-align: center; background-color: #1b1f27; }
.vibe-table td { padding: 12px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.1); }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='letter-spacing:-2px;'>PERFORMANCE CONSOLE</h1>", unsafe_allow_html=True)

# -------------------
# TAB SELECTION
# -------------------
tab_indiv, tab_team = st.tabs(["INDIVIDUAL PROFILE", "TEAM PERFORMANCE"])
metrics_list = ['Max_Speed', 'Vertical', 'Bench', 'Squat']

with tab_indiv:
    # Athlete Search - ONLY in this tab
    selected_player = st.selectbox("Search Athlete", sorted(df_phys['Player'].unique()))
    p_history = df_phys[df_phys['Player'] == selected_player].sort_values('Date')
    latest = p_history.iloc[-1]

    # Team Rankings (Calculated based on everyone's Personal Bests)
    team_pbs = df_phys.groupby('Player')[metrics_list].max()
    team_ranks = team_pbs.rank(ascending=False, method='min').astype(int)
    player_pbs = team_pbs.loc[selected_player]
    player_ranks = team_ranks.loc[selected_player]

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
                <div class="metric-box"><p class="m-label">Bench</p><p class="m-value">{player_pbs['Bench']}</p><p class="m-sub">Ranked #{player_ranks['Bench']}</p></div>
                <div class="metric-box"><p class="m-label">Squat</p><p class="m-value">{player_pbs['Squat']}</p><p class="m-sub">Ranked #{player_ranks['Squat']}</p></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("Recent Evaluation History")
    recent = p_history.tail(5).copy()
    for m in metrics_list:
        vals = recent[m].values
        new_col = []
        for i in range(len(vals)):
            if i == 0: new_col.append(f"{vals[i]} –")
            else:
                color = "#00ff88" if vals[i] > vals[i-1] else "#ff4b4b"
                arrow = "↑" if vals[i] > vals[i-1] else ("↓" if vals[i] < vals[i-1] else "–")
                new_col.append(f"{vals[i]} <span style='color:{color}'>{arrow}</span>")
        recent[m] = new_col
    recent['Date'] = recent['Date'].dt.strftime('%Y-%m-%d')
    st.markdown(f'<div style="text-align:center;">{recent[["Date"] + metrics_list].to_html(classes="vibe-table", escape=False, index=False, border=0)}</div>', unsafe_allow_html=True)

with tab_team:
    # Filter by position
    pos_list = sorted(df_phys['Position'].unique())
    selected_pos = st.selectbox("Filter Position", ["All Positions"] + pos_list)

    # Calculation logic for "Averages" (Average of each person's PB)
    # First, get the best for every player in the entire sheet
    all_player_pbs = df_phys.groupby(['Player', 'Position'])[metrics_list].max().reset_index()

    if selected_pos == "All Positions":
        display_df = all_player_pbs
    else:
        display_df = all_player_pbs[all_player_pbs['Position'] == selected_pos]

    st.subheader(f"Top 5 Leaderboard: {selected_pos}")
    t_col1, t_col2 = st.columns(2)
    for i, m in enumerate(metrics_list):
        with (t_col1 if i % 2 == 0 else t_col2):
            st.markdown(f"<p style='text-align:center; color:#00d4ff; margin-top:15px;'><b>{m.replace('_',' ')}</b></p>", unsafe_allow_html=True)
            top5 = display_df[['Player', m]].sort_values(m, ascending=False).head(5)
            st.markdown(f"<div style='text-align:center'>{top5.to_html(classes='vibe-table', index=False, border=0)}</div>", unsafe_allow_html=True)

    st.subheader(f"Position Averages")
    # Group by position and find the mean of those PBs
    avg_data = all_player_pbs.groupby('Position')[metrics_list].mean().reset_index()
    
    if selected_pos != "All Positions":
        avg_data = avg_data[avg_data['Position'] == selected_pos]

    st.markdown(f"<div style='text-align:center'>{avg_data.to_html(classes='vibe-table', index=False, border=0)}</div>", unsafe_allow_html=True)
