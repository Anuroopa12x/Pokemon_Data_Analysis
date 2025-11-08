import streamlit as st
import pandas as pd
import numpy as np 


#@st.cache_resource
def load_data():
    details = pd.read_csv("data_for_stimulation.csv", index_col=0)
    pokemon_moves = pd.read_csv("pokemon_moves.csv", index_col=0)
    damaging_moves = pokemon_moves[pokemon_moves["power"] > 0]
    type_chart = pd.read_csv("Pokemon_Type_Chart.csv", index_col=0)
    return details, damaging_moves, type_chart
    
details, moves, type_chart = load_data() 

def stimulation_basedon_moves(details, type_chart, moves, for_, against):
    for_moves = moves[moves["name"] == for_]
    st.dataframe(for_moves)
    if not for_moves.empty:
        for_moves_names = []
        with st.form(key="get_moves"):
            move1 = st.selectbox("Select Move1", for_moves["moves"])
            move2 = st.selectbox("Select Move2", for_moves["moves"])
            move3 = st.selectbox("Select Move3", for_moves["moves"])
            move4 = st.selectbox("Select Move4", for_moves["moves"])
            submitted = st.form_submit_button("Submit")
            for_moves_names.append(move1)
            for_moves_names.append(move2)
            for_moves_names.append(move3)
            for_moves_names.append(move4)

        for_move_data = []
        
        for name in for_moves_names:
            move_data = for_moves[for_moves["moves"] == name]
            for_move_data.append({"move": name, "power": move_data["power"].iloc[0], "type": move_data["type"].iloc[0],
                                 "category": move_data["category"].iloc[0], "accuracy": move_data["accuracy"].iloc[0]})
        for_move_data = pd.DataFrame(for_move_data)

    else:
        with st.form(key="no_moves"):
            #st.write("No Move to choose from, will be using Struggle")
            submitted = st.form_submit_button("Submit")
        for_move_data = {"move": "Struggle", "power": 50, "type": "Normal",
                                      "category": "Physical", "accuracy": 100}
        for_move_data = pd.DataFrame(for_move_data, index=0)
        
    if submitted:
        if "for_move_data" not in st.session_state:
            st.session_state["for_move_data"] = for_move_data
        for_move_data = st.session_state["for_move_data"]
        
        against_moves = moves[moves["name"] == against]
    
        if not against_moves.empty:
            size = np.where(len(against_moves) > 4, 4, len(against_moves))
            against_moves_names = np.random.choice(against_moves["moves"], size=size, replace=False)
            against_move_data = []
            for name in against_moves_names:
                move_data = against_moves[against_moves["moves"] == name]
                against_move_data.append({"move": name, "power": move_data["power"].iloc[0], "type": move_data["type"].iloc[0],
                                     "category": move_data["category"].iloc[0], "accuracy": move_data["accuracy"].iloc[0]})
            against_move_data = pd.DataFrame(against_move_data)
        else:
            against_move_data = {"move": "Struggle", "power": 50, "type": "Normal", 
                                         "category": "Physical", "accuracy": 100}
            against_move_data = pd.DataFrame(against_move_data, index=[0])
    
        if "against_moves_data" not in st.session_state:
            st.session_state["against_move_data"] = against_move_data
        against_move_data = st.session_state["against_move_data"]
        
        for_data = details[details["name"] == for_]
        
        for_hp = for_data["hp"].iloc[0]
        for_attack = for_data["attack"].iloc[0]
        for_defense = for_data["defense"].iloc[0]
        for_special_attack = for_data["special_attack"].iloc[0]
        for_special_defense = for_data["special_defense"].iloc[0]
        for_speed = for_data["speed"].iloc[0]
        for_type1 = for_data["type1"].iloc[0]
        for_type2 = for_data["type2"].iloc[0]
        
        against_data = details[details["name"] == against]
        against_hp = against_data["hp"].iloc[0]
        against_attack = against_data["attack"].iloc[0]
        against_defense = against_data["defense"].iloc[0]
        against_special_attack = against_data["special_attack"].iloc[0]
        against_special_defense = against_data["special_defense"].iloc[0]
        against_speed = against_data["speed"].iloc[0]
        against_type1 = against_data["type1"].iloc[0]
        against_type2 = against_data["type2"].iloc[0]
        
        for_move_data["type1_against_dmg"] = np.array([type_chart.loc[x, :][against_type1] for x in for_move_data["type"]])
        for_move_data["type2_against_dmg"] = np.array([type_chart.loc[x, :][against_type2] for x in for_move_data["type"]])
        for_move_data["against_type_dmg"] = for_move_data["type1_against_dmg"] * for_move_data["type2_against_dmg"]
        for_move_data["for_attack"] = np.where(for_move_data["category"] == "Physical", 
                                               for_attack, for_special_attack)
        for_move_data["against_defense"] = np.where(for_move_data["category"] == "Physical",
                                                    against_defense, against_special_defense)
        for_move_data["stab"] = np.where((for_move_data["type"] == for_type1) | (for_move_data["type"] == for_type2),
                                        1.5, 1)    
        for_move_data["A/D"] = for_move_data["for_attack"] / for_move_data["against_defense"] 
        for_move_data["damage_dealt"] = (((2*50/5+2)*for_move_data["power"]*for_move_data["A/D"])/50+2)*for_move_data["against_type_dmg"]*for_move_data["stab"]
    
        against_move_data["type1_for_dmg"] = np.array([type_chart.loc[x, :][for_type1] for x in against_move_data["type"]])
        against_move_data["type2_for_dmg"] = np.array([type_chart.loc[x, :][for_type2] for x in against_move_data["type"]])
        against_move_data["for_type_dmg"] = against_move_data["type1_for_dmg"] * against_move_data["type2_for_dmg"]
        against_move_data["for_attack"] = np.where(against_move_data["category"] == "Physical", 
                                               against_attack, against_special_attack)
        against_move_data["against_defense"] = np.where(against_move_data["category"] == "Physical",
                                                    for_defense, for_special_defense)
        against_move_data["stab"] = np.where((against_move_data["type"] == against_type1) | (against_move_data["type"] == against_type2),
                                        1.5, 1)  
        against_move_data["A/D"] = against_move_data["for_attack"] / against_move_data["against_defense"] 
        against_move_data["damage_dealt"] = (((2*50/5+2)*against_move_data["power"]*against_move_data["A/D"])/50+2)*against_move_data["for_type_dmg"]*against_move_data["stab"]
    
        return for_move_data, for_speed, for_hp, against_move_data, against_speed, against_hp

state = st.radio("Select Mode", ["Preparation", "Gameplay"])
if state == "Preparation":
    try:
        for_ = st.text_input("Enter the Name of the Player Pokemon").title()
        against = st.text_input("Enter the Name of the Opponent Pokemon").title()

        # if (for_ or against) not in details["name"]:
            # st.warning("Invalid Pokemon Names")
        # else:
        for_move_data, for_speed, for_hp, against_move_data, against_speed, against_hp = stimulation_basedon_moves(details, type_chart, moves, for_, against)
        st.write(for_move_data, against_move_data)
        if "for_moves" and "for_hp" and "for_speed" not in st.session_state:
            st.session_state["for_moves"] = for_move_data
            st.session_state["for_hp"] = for_hp
            st.session_state["for_speed"] = for_speed
        if "against_moves" and "against_hp" and "against_speed" not in st.session_state:
            st.session_state["against_moves"] = against_move_data
            st.session_state["against_hp"] = against_hp
            st.session_state["against_speed"] = against_speed
    except TypeError:
        st.warning("Please Click The Submit Button")


def move_based_gameplay(for_move_data, for_hp, for_speed, against_move_data, against_hp, against_speed):
    def did_it_hit(move_data):
        return np.random.choice([True, False], 
                                p=[int(move_data["accuracy"].iloc[0])/100,
                                   (100-int(move_data["accuracy"].iloc[0]))/100])
                
    while (for_hp > 0) and (against_hp > 0):
        with st.form(key="game"):
            move = st.selectbox("Select Attack", for_move_data["move"])
            attack = st.form_submit_button("Attack")
        if attack:
            move_data = for_move_data[for_move_data["move"] == move]
            op_move_data = against_move_data[against_move_data["move"] == np.random.choice(against_move_data["move"])]
            op_move = op_move_data["move"].iloc[0]
            
            if for_speed > against_speed:
                if did_it_hit(move_data):
                    against_hp = max(0, against_hp - move_data["damage_dealt"].iloc[0])
                    st.write(f"For used {move}")
                if against_hp>0 and did_it_hit(op_move_data):
                    for_hp = max(0, for_hp - op_move_data["damage_dealt"].iloc[0])
                    st.write(f"Against used {op_move}")
                st.write(for_hp, against_hp)
                
            elif for_speed == against_speed:
                if np.random.choice([for_speed, against_speed]) == for_speed:
                    if did_it_hit(move_data):
                        against_hp = max(0, against_hp - move_data["damage_dealt"].iloc[0])
                        st.write(f"For used {move}")
                    if agaist_hp>0 and did_it_hit(op_move_data):
                        for_hp = max(0, for_hp - op_move_data["damage_dealt"].iloc[0])
                        st.write(f"Against used {op_move}")
                        st.write(for_hp, against_hp)
                        
                else:           
                    if did_it_hit(op_move_data):
                        for_hp = max(0, for_hp - op_move_data["damage_dealt"].iloc[0])
                        st.write(f"Against used {op_move}")    
                    if for_hp>0 and did_it_hit(move_data):
                        against_hp = max(0, against_hp - move_data["damage_dealt"].iloc[0])
                        st.write(f"For used {move}")
                    st.write(for_hp, against_hp)
                    
            else:
                if did_it_hit(op_move_data):
                    for_hp = max(0, for_hp - op_move_data["damage_dealt"].iloc[0])
                    st.write(f"Against used {op_move}")
                if for_hp>0 and did_it_hit(move_data):
                    against_hp = max(0, against_hp - move_data["damage_dealt"].iloc[0])
                    st.write(f"For used {move}")
                st.write(for_hp, against_hp)
        
        if for_hp <= 0:
            st.write("against wins")
        else:
            st.write("For wins")

#move_based_gameplay(for_move_data, for_hp, for_hp, against_move_data, against_hp, against_speed)

if state == "Gameplay":
    st.write(st.session_state["for_moves"])
    st.write(st.session_state["against_moves"])
    move_based_gameplay(st.session_state["for_moves"], st.session_state["for_hp"], st.session_state["for_speed"],
                       st.session_state["against_moves"], st.session_state["against_hp"], st.session_state["against_speed"])