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
    """Aggressively fetches image bytes, bypassing Google Drive's virus scan warning."""
    if pd.isna(url) or "drive.google.com" not in str(url):
        return "https://via.placeholder.com/250x350/0d1117/3880ff?text=PHOTO+MISSING"
    
    try:
        # Extract ID
        if "id=" in url:
            file_id = url.split("id=")[1].split("&")[0]
        elif "/d/" in url:
            file_id = url.split("/d/")[1].split("/")[0]
        else:
            return url

        direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        # Use a session to handle cookies (bypasses the 'confirm virus scan' page)
        session = requests.Session()
        response = session.get(direct_url, stream=True, timeout=10)
        
        # Check for Google's 'confirm' token in cookies
        confirm_token = None
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                confirm_token = value
                break
        
        if confirm_token:
            confirm_url = direct_url + f"&confirm={confirm_token}"
            response = session.get(confirm_url, stream=True)
            
        if response.status_code == 200:
            return response.content
        return "https://via.placeholder.com/250x350/0d1117/3880ff?text=ACCESS+DENIED"
    except Exception as e:
        return "https://via.placeholder.com/250x350/0d1117/3880ff?text=LOAD+ERROR"

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
# PAGE CONFIG & CSS (Centered + Dark Vibes)
# -------------------
st.set_page_config(page_title="Performance Console", layout="wide")
st.markdown("""
<style>
.stApp { background-color: #0d1117; color: #ffffff; font-family: 'Arial', sans-serif; }
h1, h2, h3 { text-align: center !important; color: white !important; }
.player-card { 
    background: linear-gradient(90deg, #161b22 0%, #1b1f27 100%); 
    padding: 30px; border-radius: 20px; border-left: 8px solid #3880ff; 
    margin-bottom: 25px; display: flex; align-items: center; 
}
.player-info { margin-left: 30px; width: 100%; }
.player-name { font-size: 3rem; font-weight: 800; margin: 0; color: #ffffff; text-align: left;}
.player-meta { font-size: 1.2rem; opacity: 1; margin: 5px 0 15px 0; color: #d0d0d0; text-align: left;}
.metrics { display: flex; gap: 20px; justify-content: flex-start; }
.metric-box { background: #161b22; border: 1px solid rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; text-align: center; flex:1; }
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
# PLAYER SELECTION
# -------------------
selected_player = st.selectbox("Search Athlete", sorted(df_phys['Player'].unique()))
p_history = df_phys[df_phys['Player'] == selected_player].sort_values('Date')
latest = p_history.iloc[-1]

tab_indiv, tab_team = st.tabs(["INDIVIDUAL PROFILE", "TEAM PERFORMANCE"])

with tab_indiv:
    st.subheader("Athlete Evaluation")
    col_img, col_info = st.columns([1,3])
    
    with col_img:
        img_bytes = load_image_from_url(latest.get('Image_URL', ""))
        st.image(img_bytes, width=250)

    with col_info:
        h_str = inches_to_feet(latest.get('Height', ""))
        st.markdown(f"""
        <div class="player-info">
            <p class="player-name">{selected_player}</p>
            <p class="player-meta">{latest.get('Position','')} | Ht: {h_str} | Wt: {latest.get('Weight','')} LBS</p>
            <div class="metrics">
                <div class="metric-box"><p class="m-label">Max Speed</p><p class="m-value">{latest.get('Max_Speed',0)}</p></div>
                <div class="metric-box"><p class="m-label">Vertical</p><p class="m-value">{latest.get('Vertical',0)}"</p></div>
                <div class="metric-box"><p class="m-label">Bench</p><p class="m-value">{latest.get('Bench',0)}</p></div>
                <div class="metric-box"><p class="m-label">Squat</p><p class="m-value">{latest.get('Squat',0)}</p></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # RECENT PERFORMANCE
    st.subheader("Evaluation History")
    metrics_list = ['Max_Speed','Vertical','Bench','Squat']
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
    st.subheader("Positional Intelligence")
    t_col1, t_col2 = st.columns(2)
    for i, metric in enumerate(metrics_list):
        with (t_col1 if i % 2 == 0 else t_col2):
            st.markdown(f"<p style='text-align:center; color:#00d4ff;'><b>Top 5: {metric.replace('_',' ')}</b></p>", unsafe_allow_html=True)
            top5 = df_phys.groupby('Player')[metric].max().sort_values(ascending=False).head(5).reset_index()
            st.markdown(f"<div style='text-align:center'>{top5.to_html(classes='vibe-table', index=False, border=0)}</div>", unsafe_allow_html=True)
    
    st.subheader("Team Averages by Position")
    avg_metrics = df_phys.groupby('Position')[metrics_list].mean().round(1).reset_index()
    st.markdown(f"<div style='text-align:center'>{avg_metrics.to_html(classes='vibe-table', index=False, border=0)}</div>", unsafe_allow_html=True)
