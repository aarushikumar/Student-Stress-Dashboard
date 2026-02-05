import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration - Forces Wide Mode
st.set_page_config(page_title="Student Stress Analytics", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS TO REMOVE TOP MARGINS AND MAXIMIZE SPACE ---
st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 0rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)

# 2. Load and Clean Data
@st.cache_data
def load_data():
    df1 = pd.read_csv('Stress_Dataset.csv')
    df2 = pd.read_csv('StressLevelDataset.csv')
    # Filter ages above 70
    df1 = df1[df1['Age'] <= 70]
    return df1, df2

df_survey, df_metrics = load_data()

# 3. Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Data Analytics", "Stress Test"])

if page == "Data Analytics":
    st.title("📊 Student Wellness Dashboard")
    
    # Simple Age Selection in Sidebar
    all_ages = sorted(df_survey['Age'].unique())
    selected_ages = st.sidebar.multiselect("Filter by Age:", options=all_ages, default=all_ages)
    filtered_df = df_survey[df_survey['Age'].isin(selected_ages)]

    # Row 1: Key Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Students", len(filtered_df))
    m2.metric("Avg Anxiety Score", round(df_metrics['anxiety_level'].mean(), 1))
    m3.metric("Avg Sleep Quality", f"{round(df_metrics['sleep_quality'].mean(), 1)} / 5")

    st.divider()

    # Row 2: THE MAIN GRAPHS (Side-by-Side to fill space)
    col_left, col_right = st.columns([1.2, 1]) # Left column slightly wider for the bar graph

    with col_left:
        st.subheader("📈 Stress Intensity by Age")
        age_data = filtered_df.groupby('Age')['Have you recently experienced stress in your life?'].mean().reset_index()
        fig_bar = px.bar(age_data, x='Age', y='Have you recently experienced stress in your life?',
                         labels={'Have you recently experienced stress in your life?': 'Stress (1-5)'},
                         color_discrete_sequence=['#3366CC'],
                         height=400) # Balanced height
        fig_bar.update_layout(margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.subheader("💡 Stress Type Distribution")
        fig_pie = px.pie(filtered_df, names='Which type of stress do you primarily experience?',
                         color_discrete_sequence=px.colors.qualitative.Pastel,
                         height=400) # Matches the bar chart height
        fig_pie.update_layout(margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(fig_pie, use_container_width=True)

    # Row 3: Symptoms (Full Width)
    st.divider()
    st.subheader("🩺 Common Symptom Analysis")
    symptoms = {
        'Sleep Issues': filtered_df['Do you face any sleep problems or difficulties falling asleep?'].mean(),
        'Headaches': filtered_df['Have you been getting headaches more often than usual?'].mean(),
        'Irritability': filtered_df['Do you get irritated easily?'].mean(),
        'Low Mood': filtered_df['Have you been feeling sadness or low mood?'].mean()
    }
    symp_df = pd.DataFrame(list(symptoms.items()), columns=['Symptom', 'Average Score'])
    fig_symp = px.bar(symp_df, x='Symptom', y='Average Score', color='Symptom', text_auto='.1f', height=350)
    st.plotly_chart(fig_symp, use_container_width=True)

# --- PAGE 2: STRESS TEST ---
else:
    st.title("📝 Quick Stress Assessment")
    st.info("How do you compare to the current student data?")
    
    my_anxiety = st.slider("Your Anxiety Level (0-20):", 0, 20, 10)
    
    avg_anxiety = df_metrics['anxiety_level'].mean()
    
    comp_df = pd.DataFrame({
        'Who': ['You', 'Global Average'],
        'Anxiety': [my_anxiety, avg_anxiety]
    })
    
    fig_comp = px.bar(comp_df, x='Who', y='Anxiety', color='Who', 
                      color_discrete_map={'You': '#FF4B4B', 'Global Average': '#3366CC'},
                      height=400)
    st.plotly_chart(fig_comp, use_container_width=True)

    if my_anxiety > avg_anxiety:
        st.warning(f"Your score ({my_anxiety}) is higher than the average ({avg_anxiety:.1f}). Take some time for yourself today!")
    else:
        st.success(f"Your score ({my_anxiety}) is lower than average! Keep up the healthy habits.")
