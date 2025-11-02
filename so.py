import streamlit as st
import pandas as pd
import numpy as np 


#@st.cache_resource
def load_data():
    details = pd.read_csv("data_for_stimulation.csv", index_col=0)
    moves = pd.read_csv("moves.csv", index_col=0)
    damaging_moves = moves[moves["power"].str.isnumeric()]
    type_chart = pd.read_csv("Pokemon_Type_Chart.csv", index_col=0)
    return details, damaging_moves, type_chart
    
details, moves, type_chart = load_data()

with st.form(key="pokemon"):
    name = st.text_input("Enter name of the Pokemon")
    move1 = st.selectbox("Select Move 1", moves[moves["type"] == "Dark"])
    submitted = st.form_submit_button("Submit") 
if "move1" not in st.session_state:
    st.session_state.move1 = move1
if "power1" not in st.session_state:
    st.session_state.power1 = moves[moves["name"] == move1]["power"].iloc[0]
if submitted:
    st.write(st.session_state.move1)
    st.write(st.session_state.power1)