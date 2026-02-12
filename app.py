import streamlit as st
import pandas as pd

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Performance Console", layout="wide")

# --------------------------------------------------
# GOOGLE SHEET
# --------------------------------------------------
sheet_url = "https://drive.google.com/file/d/1I3SX2Cmo8jB6YiJAhrzWOunaNHUq0QT5/view?usp=sharing"

@st.cache_data(ttl=10)
def load_data():
    df = pd.read_csv(sheet_url)
    df.columns = df.columns.str.strip()

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    return df

df = load_data()

if df.empty:
    st.warning("No data found.")
    st.stop()

metrics = ["Max_Speed", "Vertical", "Bench", "Squat"]

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("Performance Console")

# --------------------------------------------------
# PLAYER SELECT
# --------------------------------------------------
selected_player = st.selectbox("Select Athlete", df["Player"].unique())
p_history = df[df["Player"] == selected_player].sort_values("Date")
latest = p_history.iloc[-1]

tab1, tab2 = st.tabs(["Individual Profile", "Team Performance"])

# ==================================================
# INDIVIDUAL PROFILE
# ==================================================
with tab1:

    col1, col2 = st.columns([1, 2])

    # -------------------
    # IMAGE FROM GOOGLE SHEET
    # -------------------
    with col1:
        if "Image_URL" in df.columns:
            image_url = latest.get("Image_URL", "")
            if pd.notna(image_url) and image_url != "":
                st.image(image_url, use_container_width=True)
            else:
                st.info("No image available.")

    # -------------------
    # PLAYER INFO
    # -------------------
    with col2:
        st.subheader(selected_player)

        st.write(f"**Position:** {latest.get('Position','')}")
        st.write(f"**Height:** {latest.get('Height','')}")
        st.write(f"**Weight:** {latest.get('Weight','')}")
        st.write(f"**Body Fat:** {latest.get('Body_Fat','')}")
        st.write(f"**Wingspan:** {latest.get('Wingspan','')}")

        st.divider()

        cols = st.columns(len(metrics))

        for i, metric in enumerate(metrics):
            if metric in df.columns:
                percentile = int((latest[metric] / df[metric].max()) * 100)
                cols[i].metric(
                    metric.replace("_", " "),
                    latest[metric],
                    f"Top {percentile}%"
                )

    # -------------------
    # RECENT PERFORMANCE
    # -------------------
    st.subheader("Recent Performance")

    recent = p_history.tail(5).copy()
    if "Date" in recent.columns:
        recent["Date"] = recent["Date"].dt.strftime("%Y-%m-%d")

    st.dataframe(recent[["Date"] + metrics], use_container_width=True)


# ==================================================
# TEAM PERFORMANCE
# ==================================================
with tab2:

    st.subheader("Top Performers")

    for metric in metrics:
        if metric in df.columns:
            st.write(f"### {metric.replace('_',' ')}")

            top5 = (
                df.groupby("Player")[metric]
                .max()
                .sort_values(ascending=False)
                .head(5)
                .reset_index()
            )

            st.dataframe(top5, use_container_width=True)

    st.subheader("Team Averages by Position")

    avg_metrics = (
        df.groupby("Position")[metrics]
        .mean()
        .round(1)
        .reset_index()
    )

    st.dataframe(avg_metrics, use_container_width=True)
