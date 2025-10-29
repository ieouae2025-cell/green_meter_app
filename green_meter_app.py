import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Green Meter Dashboard", layout="wide")

# --- Custom CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;600;700&display=swap');

:root {
    --accent: #2ecc71;
    --light-green: #eaf8ef;
    --dark-green: #063321;
}

* { font-family: 'Roboto', sans-serif; }
body { background-color: #ffffff; color: var(--dark-green); }

/* Hero Section */
.hero {
    background: linear-gradient(145deg, #43b47d, #2ecc71);
    border-radius: 25px;
    padding: 60px 40px;
    text-align: center;
    color: white;
    box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    animation: fadeIn 2s ease;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(25px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Sections */
.section {
    background-color: var(--light-green);
    border-radius: 20px;
    padding: 35px;
    margin: 25px 0;
    box-shadow: 0 6px 14px rgba(10,30,20,0.08);
    animation: fadeIn 1.5s ease;
}
h1, h2, h3 { color: var(--dark-green); font-weight: 700; }

.btn {
    background: var(--accent);
    color: white;
    padding: 12px 25px;
    border-radius: 25px;
    text-decoration: none;
    font-weight: 600;
    box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    transition: 0.3s ease;
}
.btn:hover { background: #29b765; transform: translateY(-3px); }
</style>
""", unsafe_allow_html=True)

# --- Hero Section ---
st.markdown("""
<div class="hero">
    <h1>🌿 Green Meter Dashboard</h1>
    <p>Track, model, and visualize your logistics CO₂ footprint — aligned with ISO 14083 & GLEC standards.</p>
    <a href="#measure" class="btn">Start Measuring</a>
</div>
""", unsafe_allow_html=True)

st.markdown('<div id="measure"></div>', unsafe_allow_html=True)

# --- Step 1: Upload Emission Data ---
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header("Step 1: Upload or Use Sample Emission Data")

use_sample = st.checkbox("Use sample data")
if use_sample:
    data = pd.DataFrame({
        'Category': ['Cars', 'Trucks', 'Planes', 'Forklifts', 'Electricity'],
        'Activity': [250000, 150000, 400, 2000, 120000],
        'Emission_Factor': [0.18, 0.9, 9.0, 0.4, 0.42]
    })
else:
    uploaded = st.file_uploader("Upload your CSV file", type=['csv'])
    if uploaded:
        data = pd.read_csv(uploaded)
    else:
        data = pd.DataFrame()

if not data.empty:
    data['CO2e_tonnes'] = data['Activity'] * data['Emission_Factor'] / 1000
    st.dataframe(data, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Step 2: Model Your Emissions ---
if not data.empty:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.header("Step 2: Model and Adjust Your Emissions")

    col1, col2, col3 = st.columns(3)
    with col1:
        ev_share = st.slider("EV Share for Cars (%)", 0, 100, 30)
        plane_load = st.slider("Plane Load Factor (%)", 10, 100, 60)
    with col2:
        trip_reduction = st.slider("Trip Reduction for Cars (%)", 0, 50, 10)
        forklift_hours = st.slider("Forklift Optimization (%)", 0, 100, 15)
    with col3:
        renewable_share = st.slider("Renewable Electricity (%)", 0, 100, 40)
        subcontractor_emissions = st.number_input("Subcontractor CO₂ (t/year)", 0.0, 500.0, 45.0)

    optimized = data.copy()
    optimized.loc[optimized['Category'] == 'Cars', 'CO2e_tonnes'] *= (1 - ev_share/100 - trip_reduction/100)
    optimized.loc[optimized['Category'] == 'Planes', 'CO2e_tonnes'] *= (plane_load/100)
    optimized.loc[optimized['Category'] == 'Forklifts', 'CO2e_tonnes'] *= (1 - forklift_hours/100)
    optimized.loc[optimized['Category'] == 'Electricity', 'CO2e_tonnes'] *= (1 - renewable_share/100)
    optimized.loc[len(optimized)] = ['Subcontractors', subcontractor_emissions, 1, subcontractor_emissions]

    baseline_total = data['CO2e_tonnes'].sum()
    optimized_total = optimized['CO2e_tonnes'].sum()

    st.metric("Baseline Emissions (tonnes CO₂e)", f"{baseline_total:.1f}")
    st.metric("Optimized Emissions (tonnes CO₂e)", f"{optimized_total:.1f}")

    col4, col5 = st.columns(2)
    with col4:
        fig1 = px.bar(data, x='Category', y='CO2e_tonnes', title="Baseline CO₂ Emissions",
                      color='Category', color_discrete_sequence=px.colors.sequential.Greens)
        st.plotly_chart(fig1, use_container_width=True)
    with col5:
        fig2 = px.bar(optimized, x='Category', y='CO2e_tonnes', title="Optimized CO₂ Emissions",
                      color='Category', color_discrete_sequence=px.colors.sequential.Greens_r)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# --- Step 3: Sustainability Reports & Methodology ---
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header("Step 3: Sustainability Reports & Methodology")

st.subheader("Methodology & Data Integrity")
st.markdown("""
- Emission factors are derived from **DEFRA 2024** and **GLEC Framework** standards.  
- Includes Scope 1 (Direct), Scope 2 (Energy), and Scope 3 (Transport & Supply Chain).  
- Supports scenario modeling for **baseline vs optimized** emissions.  
- Built to align with **ISO 14083** and **corporate sustainability frameworks**.
""")

st.subheader("Future Enhancements")
st.markdown("""
- Integration with **Cozero** / **Climatiq APIs** for live emission factor updates.  
- Multi-business unit dashboards and regional reporting.  
- Automated **ESG report generation** aligned to GRI & CDP frameworks.  
- Predictive modeling for emission reduction goals.
""")

st.subheader("Sustainability Reports & Exports")
if not data.empty:
    csv = optimized.to_csv(index=False).encode('utf-8')
    st.download_button("📄 Download Optimized Emission Report (CSV)", csv, "optimized_emission_report.csv", "text/csv")
else:
    st.info("Upload or use sample data to generate reports.")
st.markdown('</div>', unsafe_allow_html=True)

# --- Step 4: Reporting & Compliance ---
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header("Step 4: Reporting & Compliance")
st.markdown("""
Data generated here can be directly integrated into:
- **Corporate Sustainability Reports (GRI 305)**  
- **CDP Disclosure** for greenhouse gas reporting  
- **ISO 14083 transport-specific emission reports**  
- Internal tracking dashboards for ESG metrics
""")
st.markdown('</div>', unsafe_allow_html=True)



