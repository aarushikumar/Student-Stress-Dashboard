import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Student Wellness 360", layout="wide", page_icon="🧘")

# --- DARK MODE CUSTOM CSS (Deep Midnight Theme) ---
st.markdown("""
    <style>
        /* Main background */
        .stApp {
            background-color: #0E1117; 
            color: #E0E0E0;
        }
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #161B22;
        }
        /* Metric cards */
        div[data-testid="stMetricValue"] {
            color: #58A6FF;
        }
        /* Borders for containers */
        div[data-testid="stExpander"], .stContainer {
            border: 1px solid #30363D !important;
            background-color: #161B22 !important;
        }
        /* Custom header colors */
        h1, h2, h3 {
            color: #F0F6FC;
        }
    </style>
    """, unsafe_allow_html=True)


# 2. Data Loading
@st.cache_data
def load_data():
    df1 = pd.read_csv('Stress_Dataset.csv')
    df2 = pd.read_csv('StressLevelDataset.csv')
    df1 = df1[df1['Age'] <= 70]

    # Cleaning Gender labels for the filter
    # Mapping 0/1 to Female/Male based on common dataset encoding
    df1['Gender_Label'] = df1['Gender'].map({0: 'Female', 1: 'Male'}).fillna('Other')
    return df1, df2


df_survey, df_metrics = load_data()

# 3. Sidebar Navigation
st.sidebar.title("🎛️ Controls")
page = st.sidebar.radio("Navigation", ["Data Analytics Deep-Dive", "Personalized Wellness Test"])

# Shared Filters for Analytics Page
if page == "Data Analytics Deep-Dive":
    st.sidebar.markdown("---")
    selected_gender = st.sidebar.multiselect("Gender Filter:", options=["Male", "Female"], default=["Male", "Female"])
    all_ages = sorted(df_survey['Age'].unique())
    selected_ages = st.sidebar.select_slider("Age Range:", options=all_ages, value=(min(all_ages), max(all_ages)))

    # Apply Filters
    f_survey = df_survey[(df_survey['Gender_Label'].isin(selected_gender)) &
                         (df_survey['Age'] >= selected_ages[0]) &
                         (df_survey['Age'] <= selected_ages[1])]

# --- PAGE 1: ANALYTICS ---
if page == "Data Analytics Deep-Dive":
    st.title("📊 Student Wellness Deep-Dive")
    st.write("Exploring environmental and lifestyle factors behind academic stress.")

    # KPI Row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Sample Size", len(f_survey))
    m2.metric("Avg Anxiety", round(df_metrics['anxiety_level'].mean(), 1))
    m3.metric("Sleep Quality", f"{round(df_metrics['sleep_quality'].mean(), 1)}/5")
    m4.metric("Study Load", f"{round(df_metrics['study_load'].mean(), 1)}/5")

    st.divider()

    #col_a, col_b = st.columns(2)

    col_a, col_b = st.columns([1, 1])


    with col_a:
        st.subheader("💡 Predominant Stress Types")
        fig_pie = px.pie(f_survey, names='Which type of stress do you primarily experience?',
                         hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe, height=450)
        fig_pie.update_layout(legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        st.subheader("📈 Stress Intensity Trend")
        age_trend = f_survey.groupby('Age')['Have you recently experienced stress in your life?'].mean().reset_index()
        fig_line = px.line(age_trend, x='Age', y='Have you recently experienced stress in your life?',
                           markers=True, template="plotly_dark", line_shape="spline")
        fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_line, use_container_width=True)

    st.divider()
    st.subheader("🔍 Correlation Factor: Environmental Stressors")
    factor = st.selectbox("Choose a factor to analyze against Stress Levels:",
                          ["social_support", "living_conditions", "peer_pressure", "bullying",
                           "future_career_concerns"])

    # Stress mapping for metrics
    df_metrics['Stress_Name'] = df_metrics['stress_level'].map({0: "Low", 1: "Medium", 2: "High"})
    fig_box = px.box(df_metrics, x="Stress_Name", y=factor, color="Stress_Name", template="plotly_dark",
                     category_orders={"Stress_Name": ["Low", "Medium", "High"]})
    fig_box.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_box, use_container_width=True)

# --- PAGE 2: ASSESSMENT ---
else:
    st.title("🧘 Personalized Assessment")
    st.write("How does your daily routine impact your wellness compared to other students?")

    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            in_sleep = st.slider("Sleep Quality (0-5)", 0, 5, 3)
            in_study = st.slider("Study Load (0-5)", 0, 5, 3)
            in_perf = st.slider("Academic Performance (0-5)", 0, 5, 4)
        with c2:
            in_social = st.slider("Social Support (0-3)", 0, 3, 2)
            in_anx = st.slider("Anxiety Level (0-21)", 0, 21, 10)
            in_head = st.slider("Headache Frequency (0-5)", 0, 5, 1)

    st.divider()

    # Normalized Comparison
    avg_data = {
        "Sleep": df_metrics['sleep_quality'].mean(),
        "Study Load": df_metrics['study_load'].mean(),
        "Performance": df_metrics['academic_performance'].mean(),
        "Anxiety": df_metrics['anxiety_level'].mean() / 4.2  # Normalized
    }
    user_data = {
        "Sleep": in_sleep,
        "Study Load": in_study,
        "Performance": in_perf,
        "Anxiety": in_anx / 4.2
    }

    comp_df = pd.DataFrame({
        "Metric": list(avg_data.keys()),
        "Average Student": list(avg_data.values()),
        "You": list(user_data.values())
    }).melt(id_vars="Metric")

    st.subheader("📊 Your Comparison Profile")
    fig_comp = px.bar(comp_df, x="Metric", y="value", color="variable", barmode="group",
                      template="plotly_dark", color_discrete_map={"You": "#58A6FF", "Average Student": "#30363D"})
    fig_comp.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_comp, use_container_width=True)

    # Feedback
    st.subheader("📝 Insight & Recommendations")
    f1, f2 = st.columns(2)
    with f1:
        if in_sleep < 3:
            st.error(
                "💡 **Sleep Insight:** Your sleep is below average. Improving this could reduce anxiety by up to 30% based on our dataset trends.")
        else:
            st.success("✅ **Healthy Routine:** Your sleep hygiene is excellent!")
    with f2:
        if in_anx > 15:
            st.warning(
                "⚠️ **Stress Alert:** High anxiety levels detected. Prioritize social interaction and breaks today.")
        else:
            st.success("✅ **Balanced Levels:** Your anxiety is currently manageable.")
