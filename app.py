import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Kamniški Vlak - Monitor Zamud", layout="wide")

st.title("🚉 Stanje na progi Ljubljana - Kamnik Graben")

# Gumb za ročni zajem
if st.button('Osveži podatke zdaj'):
    import subprocess
    subprocess.run(["python", "scraper.py"])
    st.success("Podatki osveženi!")

# Branje podatkov
if os.path.exists('zamude.csv'):
    df = pd.read_csv('zamude.csv')
    df['cas_zajema'] = pd.to_datetime(df['cas_zajema'])
    df['zamuda'] = pd.to_numeric(df['zamuda'], errors='coerce').fillna(0)

    # Metrike
    zadnja_zamuda = df.iloc[-1]['zamuda'] if not df.empty else 0
    povprecna_danes = df[df['cas_zajema'] > datetime.now() - timedelta(days=1)]['zamuda'].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Trenutna zadnja zamuda", f"{int(zadnja_zamuda)} min")
    col2.metric("Povprečje danes", f"{povprecna_danes:.1f} min")
    col3.metric("Število zapisov", len(df))

    # Grafi
    st.subheader("Vizualizacija zamud")
    tab1, tab2, tab3 = st.tabs(["Dnevno", "Tedensko", "Mesečno"])

    with tab1:
        dnevni_df = df[df['cas_zajema'] > datetime.now() - timedelta(days=1)]
        fig1 = px.line(dnevni_df, x='cas_zajema', y='zamuda', title="Zamude v zadnjih 24 urah", color_discrete_sequence=['#FF4B4B'])
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        tedenski_df = df[df['cas_zajema'] > datetime.now() - timedelta(days=7)]
        fig2 = px.bar(tedenski_df, x='cas_zajema', y='zamuda', title="Zamude v zadnjem tednu")
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        fig3 = px.histogram(df, x='cas_zajema', y='zamuda', histfunc='avg', nbins=30, title="Povprečne mesečne zamude")
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Surovi podatki")
    st.dataframe(df.sort_values(by='cas_zajema', ascending=False))
else:
    st.info("Podatkovna datoteka še ne obstaja. Kliknite 'Osveži podatke' za prvi zajem.")
