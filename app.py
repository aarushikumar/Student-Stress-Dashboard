import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Setup
st.set_page_config(page_title="Student Stress Dashboard", layout="wide")


# 2. Load and Clean Data
@st.cache_data
def load_data():
    df1 = pd.read_csv('Stress_Dataset.csv')
    df2 = pd.read_csv('StressLevelDataset.csv')

    # REMOVE AGE GROUPS ABOVE 70
    df1 = df1[df1['Age'] <= 70]

    return df1, df2


df_survey, df_metrics = load_data()

# 3. Sidebar Navigation
st.sidebar.title("Main Menu")
page = st.sidebar.radio("Go to:", ["Data Analytics", "Stress Test"])

# --- PAGE 1: DATA ANALYTICS ---
if page == "Data Analytics":
    st.title("📊 Simple Stress Analytics")
    st.write("This page shows survey results for students aged 70 and below.")

    # Simple Age Selection
    st.sidebar.subheader("Filter by Age")
    all_ages = sorted(df_survey['Age'].unique())
    selected_ages = st.sidebar.multiselect("Select Ages to view:", options=all_ages, default=all_ages)

    # Filter data based on selection
    filtered_df = df_survey[df_survey['Age'].isin(selected_ages)]

    # Summary Numbers
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Students", len(filtered_df))
    c2.metric("Avg. Anxiety Level", round(df_metrics['anxiety_level'].mean(), 1))
    c3.metric("Avg. Sleep Quality", f"{round(df_metrics['sleep_quality'].mean(), 1)} / 5")

    st.markdown("---")

    # Simple Layout with 2 Columns
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("What kind of stress do they feel?")
        # Find this line and add the height parameter:
        fig_pie = px.pie(filtered_df,
                         names='Which type of stress do you primarily experience?',
                         color_discrete_sequence=px.colors.qualitative.Pastel,
                         height=500)
        st.plotly_chart(fig_pie, use_container_width=True)


    with col_right:
        st.subheader("Stress Intensity by Age")
        # Simple Bar Chart showing average stress score per age
        age_data = filtered_df.groupby('Age')['Have you recently experienced stress in your life?'].mean().reset_index()
        fig_bar = px.bar(age_data, x='Age', y='Have you recently experienced stress in your life?',
                         labels={'Have you recently experienced stress in your life?': 'Stress Score (1-5)'},
                         color_discrete_sequence=['#3366CC'])
        st.plotly_chart(fig_bar, use_container_width=True)

    # Symptom Bar Chart
    st.subheader("Common Struggles")
    symptoms = {
        'Sleep Issues': filtered_df['Do you face any sleep problems or difficulties falling asleep?'].mean(),
        'Headaches': filtered_df['Have you been getting headaches more often than usual?'].mean(),
        'Irritability': filtered_df['Do you get irritated easily?'].mean()
    }
    symp_df = pd.DataFrame(list(symptoms.items()), columns=['Symptom', 'Average Score'])
    fig_symp = px.bar(symp_df, x='Symptom', y='Average Score', color='Symptom', text_auto='.1f')
    st.plotly_chart(fig_symp, use_container_width=True)

# --- PAGE 2: STRESS TEST ---
else:
    st.title("📝 Simple Stress Test")
    st.write("Adjust the sliders to see how your anxiety compares to the student average.")

    # Input Sliders
    my_anxiety = st.slider("Your Anxiety Level (0 to 20):", 0, 20, 10)
    my_sleep = st.slider("Your Sleep Quality (0 = Bad, 5 = Good):", 0, 5, 3)

    st.markdown("---")

    # Calculation
    avg_anxiety = df_metrics['anxiety_level'].mean()

    st.subheader("Your Comparison")

    # Simple Comparison Bar
    comp_df = pd.DataFrame({
        'Who': ['You', 'Average Student'],
        'Anxiety Level': [my_anxiety, avg_anxiety]
    })

    fig_comp = px.bar(comp_df, x='Who', y='Anxiety Level', color='Who',
                      color_discrete_map={'You': '#FF4B4B', 'Average Student': '#3366CC'})
    st.plotly_chart(fig_comp, use_container_width=True)

    if my_anxiety > avg_anxiety:
        st.warning("Your anxiety level is higher than the average student. Consider taking a break!")
    else:
        st.success("You are doing great! Your anxiety is lower than the average student.")
