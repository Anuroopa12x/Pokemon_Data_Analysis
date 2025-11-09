import streamlit as st
import pandas as pd
import numpy as np 


@st.cache_resource
def load_data():
    details = pd.read_csv("data_for_simulation.csv", index_col=0)
    pokemon_moves = pd.read_csv("pokemon_moves.csv", index_col=0)
    damaging_moves = pokemon_moves[pokemon_moves["power"] > 0]
    type_chart = pd.read_csv("Pokemon_Type_Chart.csv", index_col=0)
    return details, damaging_moves, type_chart
    
details, moves, type_chart = load_data() 

def preparation(details, type_chart, moves):
    if "for_" not in st.session_state:
        st.session_state.for_ = ""
    if "against" not in st.session_state:
        st.session_state.against = ""
        
    with st.form(key="player_and_opponent"):
        for_ = st.text_input("Enter the Name of the Player Pokemon").title().strip()
        against = st.text_input("Enter the Name of the Opponent Pokemon").title().strip()
        submit_names = st.form_submit_button("Submit")


    if submit_names:
        st.session_state.for_ = for_
        st.session_state.against = against

    for_ = st.session_state.for_
    against = st.session_state.against

    if for_ and against:
        def simulation_based_on_moves(details, type_chart, moves, for_, against):
            if for_ not in list(details["name"]) or against not in list(details["name"]):
                st.warning("Invalid Pokemon Names")
                return None
          
            for_data = details[details["name"] == for_]
            
            for_hp = for_data["hp"].iloc[0]
            for_attack = for_data["attack"].iloc[0]
            for_defense = for_data["defense"].iloc[0]
            for_special_attack = for_data["special_attack"].iloc[0]
            for_special_defense = for_data["special_defense"].iloc[0]
            for_speed = for_data["speed"].iloc[0]
            for_type1 = for_data["type1"].iloc[0]
            for_type2 = for_data["type2"].iloc[0]
            for_number = for_data["number"].iloc[0]
            
            against_data = details[details["name"] == against]
            
            against_hp = against_data["hp"].iloc[0]
            against_attack = against_data["attack"].iloc[0]
            against_defense = against_data["defense"].iloc[0]
            against_special_attack = against_data["special_attack"].iloc[0]
            against_special_defense = against_data["special_defense"].iloc[0]
            against_speed = against_data["speed"].iloc[0]
            against_type1 = against_data["type1"].iloc[0]
            against_type2 = against_data["type2"].iloc[0]
            against_number = against_data["number"].iloc[0]

            col1, col2, col3 = st.columns(3)

            with col1:
                st.image(f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{for_number}.png")
            with col2:
                st.image("static/vs.png")
            with col3:
                st.image(f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{against_number}.png")
                
            for_moves = moves[moves["name"] == for_]
            st.dataframe(for_moves.loc[:, ["moves", "type", "power", "accuracy"]], hide_index=True)
            against_moves = moves[moves["name"] == against]
            
            def get_players_moves(for_moves, against_moves):
                
                if not against_moves.empty:
                    size = min(4, len(against_moves))
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
                    
                if not for_moves.empty:
                    move1 = st.selectbox("Select Move1", for_moves["moves"], key="move1")
                    move2 = st.selectbox("Select Move2", for_moves["moves"], key="move2")
                    move3 = st.selectbox("Select Move3", for_moves["moves"], key="move3")
                    move4 = st.selectbox("Select Move4", for_moves["moves"], key="move4")
                    for_moves_names = [move1, move2, move3, move4]
                    for_move_data = []
                    
                    for name in for_moves_names:
                        move_data = for_moves[for_moves["moves"] == name]
                        for_move_data.append({"move": name, "power": move_data["power"].iloc[0], "type": move_data["type"].iloc[0],
                                             "category": move_data["category"].iloc[0], "accuracy": move_data["accuracy"].iloc[0]})
                    for_move_data = pd.DataFrame(for_move_data)
                    return for_move_data, against_move_data
                else:
                    st.write("No Move to choose from, will be using Struggle") 
                    for_move_data = {"move": "Struggle", "power": 50, "type": "Normal",
                                                  "category": "Physical", "accuracy": 100}
                    for_move_data = pd.DataFrame(for_move_data, index=[0])
                    return for_move_data, against_move_data

            for_move_data, against_move_data = get_players_moves(for_moves, against_moves)

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
        
            return for_move_data, for_speed, for_hp, for_number, against_move_data, against_speed, against_hp, against_number

        result = simulation_based_on_moves(details, type_chart, moves, for_, against)
        if result != None:
            #st.write(result)
            for_move_data, for_speed, for_hp, for_number, against_move_data, against_speed, against_hp, against_number = result
            st.session_state["for_moves"] = for_move_data
            st.session_state["for_hp"] = for_hp
            st.session_state["for_speed"] = for_speed
            st.session_state["for_number"] = for_number
            st.session_state["against_moves"] = against_move_data
            st.session_state["against_hp"] = against_hp
            st.session_state["against_speed"] = against_speed
            st.session_state["against_number"] = against_number
            
def move_based_gameplay(for_, for_move_data, for_speed, for_number, against, against_move_data, against_speed, against_number):
    def did_it_hit(move_data):
        return np.random.choice([True, False], 
                                p=[int(move_data["accuracy"].iloc[0])/100,
                                   (100-int(move_data["accuracy"].iloc[0]))/100])
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image(f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{for_number}.png")
        st.metric(f"{for_} HP", round(st.session_state.for_hp, 2))
    with col2:
        st.image("static/vs.png")
    with col3:
        st.image(f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{against_number}.png")
        st.metric(f"{against} HP", round(st.session_state.against_hp, 2))

    if st.session_state.for_hp <= 0:
        st.error(f"💀 {for_} Loses and {against} Wins")
        if st.button("Reset"):
            for key in ["for_", "for_hp", "for_moves", "for_speed", "for_number",
                        "against", "against_hp", "against_speed", "against_moves", "against_number"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        return
    elif st.session_state.against_hp <= 0:
        st.success(f"🎉 {for_} Wins!")
        if st.button("Reset"):
            for key in ["for_", "for_hp", "for_moves", "for_speed", "for_number",
                        "against", "against_hp", "against_speed", "against_moves", "against_number"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        return 
        
    st.write("### Select Your Move")

    st.dataframe(for_move_data.loc[:, ["move", "type", "power", "accuracy"]], hide_index=True)

    with st.form(key="battle"):
        move = st.selectbox("Select Attack", for_move_data["move"])
        attack = st.form_submit_button("⚔️ Attack")
    if attack:
        move_data = for_move_data[for_move_data["move"] == move]
        op_move = np.random.choice(against_move_data["move"])
        op_move_data = against_move_data[against_move_data["move"] == op_move]
        for_damage = move_data["damage_dealt"].iloc[0]
        op_damage = op_move_data["damage_dealt"].iloc[0]
        
        st.write("---")
        st.write("### Battle Log")
        
        if for_speed > against_speed:
            if did_it_hit(move_data):
                st.session_state.against_hp = max(0, st.session_state.against_hp - for_damage)
                st.write(f"✅ {for_} used **{move}** and dealt {for_damage:.1f} damage!")
            else:
                st.write(f"❌ {for_} used **{move}** but it missed!")
                
            if st.session_state.against_hp>0 and did_it_hit(op_move_data):
                st.session_state.for_hp = max(0, st.session_state.for_hp - op_damage)
                st.write(f"💥 {against} used **{op_move}** and dealt {op_damage:.1f} damage!")
            else:
                st.write(f"🛡️ {against} used **{op_move}** but it missed!")
                
        elif for_speed == against_speed:
            if np.random.choice([for_speed, against_speed]) == for_speed:
                if did_it_hit(move_data):
                    st.session_state.against_hp = max(0, st.session_state.against_hp - for_damage)
                    st.write(f"✅ {for_} used **{move}** and dealt {for_damage:.1f} damage!")
                else:
                    st.write(f"❌ {for_} used **{move}** but it missed!")
                    
                if st.session_state.against_hp>0 and did_it_hit(op_move_data):
                    st.session_state.for_hp = max(0, st.session_state.for_hp - op_damage)
                    st.write(f"💥 {against} used **{op_move}** and dealt {op_damage:.1f} damage!")
                else:
                    st.write(f"🛡️ {against} used **{op_move}** but it missed!")
                    
            else:           
                if did_it_hit(op_move_data):
                    st.session_state.for_hp = max(0, st.session_state.for_hp - op_damage)
                    st.write(f"💥 {against} used **{op_move}** and dealt {op_damage:.1f} damage!")  
                else:
                    st.write(f"🛡️ {against} used **{op_move}** but it missed!")
                    
                if st.session_state.for_hp>0 and did_it_hit(move_data):
                    st.session_state.against_hp = max(0, st.session_state.against_hp - for_damage)
                    st.write(f"✅ {for_} used **{move}** and dealt {for_damage:.1f} damage!")
                else:
                    st.write(f"❌ {for_} used **{move}** but it missed!")
        else:
            if did_it_hit(op_move_data):
                st.session_state.for_hp = max(0, st.session_state.for_hp - op_damage)
                st.write(f"💥 {against} used **{op_move}** and dealt {op_damage:.1f} damage!")  
            else:
                st.write(f"🛡️ {against} used **{op_move}** but it missed!")
                
            if st.session_state.for_hp>0 and did_it_hit(move_data):
                st.session_state.against_hp = max(0, st.session_state.against_hp - for_damage)
                st.write(f"✅ {for_} used **{move}** and dealt {for_damage:.1f} damage!")
            else:
                st.write(f"❌ {for_} used **{move}** but it missed!")
        st.write("---")
        col4, col5 = st.columns(2)
        with col4:
            st.metric(f"{for_} HP", round(st.session_state.for_hp, 2))
        with col5:
            st.metric(f"{against} HP", round(st.session_state.against_hp, 2))


state = st.radio("Select Mode", ["Preparation", "Gameplay"])

if state == "Preparation":
    preparation(details, type_chart, moves)

if state == "Gameplay":
    required_key = ["for_", "for_hp", "for_moves", "for_speed", "for_number",
                    "against", "against_hp", "against_speed", "against_moves", "against_number"]
    
    if all(key in st.session_state for key in required_key):
        move_based_gameplay(st.session_state.for_, st.session_state.for_moves, st.session_state.for_speed, st.session_state.for_number,
                           st.session_state.against, st.session_state.against_moves, st.session_state.against_speed, st.session_state.against_number)
    else:
        st.warning("⚠️ Please complete the Preparation phase first before starting gameplay!")
        st.info("Switch to 'Preparation' mode to select your Pokemon and moves.")
