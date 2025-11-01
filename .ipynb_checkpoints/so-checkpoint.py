import streamlit as st
import pandas as pd
import numpy as np 


moves = pd.read_csv("moves.csv", index_col=0)

option = st.selectbox("Select", moves[moves["type"] == "Fire"]["name"])
st.write(option)