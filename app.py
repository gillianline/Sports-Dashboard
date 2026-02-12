import streamlit as st
import pandas as pd
import requests

# -------------------
# HELPER FUNCTIONS
# -------------------
def inches_to_feet(inches):
    if pd.isna(inches) or inches == "": return "N/A"
    try:
        val = float(inches)
        return f"{int(val // 12)}'{int(val % 12)}\""
    except: return str(inches)

def load_image_from_url(url):
    """Bypasses Google Drive embed blocks by fetching raw content"""
    if pd.isna(url) or "drive.google.com" not in str(url):
        return "https://via.placeholder.com/250x350/0d1117/3880ff?text=PHOTO+MISSING"
    try:
        # Standardize URL to the direct download/view format
        if "id=" not in url and "/d/" in url:
            file_id = url.split("/d/")[1].split("/")[0]
            url = f"https://drive.google.com/uc?export=view&id={file_id}"
        
        # Fetch raw data to bypass browser '403 Forbidden' blocks
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.content  # Return the actual image bytes
        return "https://via.placeholder.com/250x350/0d1117/3880ff?text=IMAGE+ERROR"
    except:
        return "https://via.placeholder.com/250x350/0d1117/3880ff?text=LOAD+FAILED"

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
.stApp { background-color: #0d1117; color: #ffffff; font-family: 'Arial', sans-serif; }
h1, h3 { text-align: center !important; color: white !important; }
.player-card { 
    background: linear-gradient(90deg, #161b22 0%, #1b1f27 100%); 
    padding: 30px; border-radius: 20px; border-left: 8px solid #3880ff; 
    margin-bottom: 25px; display: flex; align-items: center; 
}
.player-info { margin-left: 30px; width: 100%; }
.player-name { font-size: 3rem; font-weight: 800; margin: 0; color: #ffffff; }
.player-meta { font-size: 1.2rem; opacity: 1; margin: 5px 0 15px 0; color: #d0d0d0; }
.metrics { display: flex; gap: 20px; }
.metric-box { background: #161b22; border: 1px solid rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; text-align: center; flex:1; }
.m-label { color: #00d4ff; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom:5px; }
.m-value { font-size: 2rem; font-weight: 700; color: #ffffff; margin: 0; }
.m-sub { font-size: 0.8rem; color: #a0a0a0; margin-top: 5px; }
.vibe-table { color: #ffffff; width:100%; border-collapse: collapse; margin-bottom: 20px; }
.vibe-table th { color: #00d4ff; border-bottom: 1px solid rgba(255,255,255,0.2); padding: 12px; text-align: center; background-color: #1b1f27; }
.vibe-table td { padding: 12px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.1); }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='letter-spacing:-2px; color:white;'>PERFORMANCE CONSOLE</h1>", unsafe_allow_html=True)

# -------------------
# PLAYER SELECTION
# -------------------
selected_player = st.selectbox("Search Athlete", sorted(df_phys['Player'].unique()))
p_history = df_phys[df_phys['Player'] == selected_player].sort_values('Date')
latest = p_history.iloc[-1]

tab_indiv, tab_team = st.tabs(["INDIVIDUAL PROFILE", "TEAM PERFORMANCE"])

with tab_indiv:
    st.subheader("Player Profile")
    col_img, col_info = st.columns([1,3])
    
    with col_img:
        # FETCH THE ACTUAL IMAGE BYTES
        img_content = load_image_from_url(latest.get('Image_URL', ""))
        st.image(img_content, width=250)

    with col_info:
        h_str = inches_to_feet(latest.get('Height', ""))
        st.markdown(f"""
        <div class="player-info">
            <p class="player-name">{selected_player}</p>
            <p class="player-meta">{latest.get('Position','')} | Height: {h_str} | Weight: {latest.get('Weight','')} LBS</p>
            <div class="metrics">
                <div class="metric-box"><p class="m-label">Max Speed</p><p class="m-value">{latest.get('Max_Speed',0)}</p></div>
                <div class="metric-box"><p class="m-label">Vertical</p><p class="m-value">{latest.get('Vertical',0)}"</p></div>
                <div class="metric-box"><p class="m-label">Bench</p><p class="m-value">{latest.get('Bench',0)}</p></div>
                <div class="metric-box"><p class="m-label">Squat</p><p class="m-value">{latest.get('Squat',0)}</p></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # RECENT PERFORMANCE TABLE
    st.subheader("Recent Performance")
    metrics_list = ['Max_Speed','Vertical','Bench','Squat']
    recent = p_history.tail(5).copy()
    for m in metrics_list:
        vals = recent[m].values
        new_col = []
        for i in range(len(vals)):
            if i == 0: new_col.append(f"{vals[i]} –")
            else:
                arrow = "<span style='color:#00ff88'>↑</span>" if vals[i] > vals[i-1] else ("<span style='color:#ff4b4b'>↓</span>" if vals[i] < vals[i-1] else "–")
                new_col.append(f"{vals[i]} {arrow}")
        recent[m] = new_col
    recent['Date'] = recent['Date'].dt.strftime('%Y-%m-%d')
    st.markdown(f'<div style="text-align:center;">{recent[["Date"] + metrics_list].to_html(classes="vibe-table", escape=False, index=False, border=0)}</div>', unsafe_allow_html=True)

with tab_team:
    st.subheader("Team Performance")
    t_col1, t_col2 = st.columns(2)
    for i, metric in enumerate(metrics_list):
        target_col = t_col1 if i % 2 == 0 else t_col2
        with target_col:
            st.markdown(f"<p style='text-align:center; color:#00d4ff;'><b>Top 5: {metric.replace('_',' ')}</b></p>", unsafe_allow_html=True)
            top5 = df_phys.groupby('Player')[metric].max().sort_values(ascending=False).head(5).reset_index()
            st.markdown(f"<div style='text-align:center'>{top5.to_html(classes='vibe-table', index=False, border=0)}</div>", unsafe_allow_html=True)
    st.subheader("Team Averages by Position")
    avg_metrics = df_phys.groupby('Position')[metrics_list].mean().round(1).reset_index()
    st.markdown(f"<div style='text-align:center'>{avg_metrics.to_html(classes='vibe-table', index=False, border=0)}</div>", unsafe_allow_html=True)
