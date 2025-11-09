import pandas as pd
import numpy as np
import streamlit as st

col1, col2 = st.columns([1, 4]) # Adjust column ratios as needed

with col1:
    st.image("static/swords.jpg")

with col2:
    st.title("Pokemon Battle Simulator", )


@st.cache_data
def load_data():
    type_chart = pd.read_csv("Pokemon_Type_Chart.csv", index_col = 0)
    details = pd.read_csv("data_for_simulation.csv", index_col = 0)
    moves = pd.read_csv("pokemon_moves.csv", index_col=0)
    damaging_moves = moves.loc[moves["power"] > 0, :]
    return details, type_chart, damaging_moves
    

details, type_chart, moves = load_data()

def do_all_together(details, type_chart):
    with st.form(key = "pokemon"):
        name = st.text_input("Enter name of the Pokemon: ")
        name = name.title()
        submitted = st.form_submit_button("Submit")
        
    if submitted:
        
        def simulator(details, type_chart, name):
            """
            Parameters: 
            details - pd.DataFrame containg pokemon details scraped from bulbapedia
            type_chart - pd.DataFrame of pokemon damage type chart with attacking type 
            as index and defensing type as column names
            name - str of name of the particular pokemon you want to stimulate
            Returns:
            pd.DataFrame with columns name, outcome
            """
            
            details = details.copy()
        
            pokemon = details[details["name"].str.contains(name, case = False)]
            if len(pokemon) < 1:
                st.write(f"The given name: {name} is not a name of available pokemon")
                return None
        
            attack = pokemon["attack"].iloc[0]
            special_attack = pokemon["special_attack"].iloc[0]
            details["main_defense"] = np.where(attack >= special_attack, details["defense"], details["special_defense"])
            number = pokemon["number"].iloc[0]
            speed = pokemon["speed"].iloc[0]
            defense = pokemon["defense"].iloc[0]
            special_defense = pokemon["special_defense"].iloc[0]
            main_attack = pokemon["main_attack"].iloc[0]
            type1 = pokemon["type1"].iloc[0]
            type2 = pokemon["type2"].iloc[0]
            hp = pokemon["hp"].iloc[0]
            details["pokemon_defense"] = np.where(details["attack"] >= details["special_attack"],defense, special_defense)
        
                
            details["A/D_pokemon"] = main_attack / details["main_defense"]
            details["A/D_others"] = details["main_attack"] / details["pokemon_defense"]
            
            type11_offense = np.array([type_chart.loc[type1, :][x] for x in details["type1"]])
            type12_offense = np.array([type_chart.loc[type1, :][x] for x in details["type2"]])
            details["pokemon_type1_offense"] = type11_offense * type12_offense
        
            if type2 != "Nil":
                type21_offense = np.array([type_chart.loc[type2, :][x] for x in details["type1"]])
                type22_offense = np.array([type_chart.loc[type2, :][x] for x in details["type2"]])  
                details["pokemon_type2_offense"] = type21_offense * type22_offense
                details["pokemon_type_offense"] = np.maximum(details["pokemon_type1_offense"], 
                                                             details["pokemon_type2_offense"])
            else:
                details["pokemon_type_offense"] = details["pokemon_type1_offense"]
        
            type11_other_offense = np.array([type_chart.loc[x, :][type1] for x in details["type1"]])
            type12_other_offense = np.array([type_chart.loc[x, :][type1] for x in details["type2"]])
            details["others_type1_offense"] = type11_other_offense * type12_other_offense
        
            type21_other_offense = np.array([type_chart.loc[x, :][type2] for x in details["type1"]])
            type22_other_offense = np.array([type_chart.loc[x, :][type2] for x in details["type2"]])
            details["others_type2_offense"] = type21_other_offense * type22_other_offense
        
            if type2 != "Nil":
                details["others_type_offense"] = np.maximum(details["others_type1_offense"],
                                                            details["others_type2_offense"])
            else:
                details["others_type_offense"] = np.maximum(details["others_type1_offense"], 
                                                            details["others_type2_offense"])
            
            power = 80
            level = 50
            
            details["damage_dealt_pokemon"] = (((2*level/5+2)*power*details["A/D_pokemon"])/50+2)*details["pokemon_type_offense"]
            details["damage_dealt_others"] = (((2*level/5+2)*power*details["A/D_others"])/50+2)*details["others_type_offense"]
        
            details["chance"] = np.where(details["speed"] < speed, 1, 
                                         np.where(details["speed"] > speed, 2,
                                         np.random.randint(1, 3, len(details))))
            
            details["turns_to_win_pokemon"] = np.ceil(details["hp"] / details["damage_dealt_pokemon"])
            details["turns_to_win_others"] = np.ceil(hp / details["damage_dealt_others"])
            
            details["outcome"] = np.where(details["turns_to_win_pokemon"] < details["turns_to_win_others"], "win",
                                          np.where(details["turns_to_win_pokemon"] > details["turns_to_win_others"], "lose",
                                                   np.where(details["chance"] == 1, "win", "lose")))
            
            return details.loc[:, ["name", "outcome", "category"]], number

        try:
            result, number = simulator(details, type_chart, name)
            result_legendary = result.loc[(result["category"] == "legendary") | (result["category"] == "sub_legendary"), :]
            result_mythical = result.loc[result["category"] == "mythical", :]
            result_mega = result.loc[result["category"] == "mega_evolution", :]
            result_normal = result.loc[result["category"] == "normal", :]
            if number == None:
                st.error(f"Name of the Pokemon {name} not found please check the spelling")
            else:
                st.subheader(f"Pokedex Number is {number}")
                url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{number}.png"
                st.image(url)
                col3, col4= st.columns(2)
                with col3:
                    st.header("Overall Result")
                    st.metric("Total Wins", (result["outcome"] == "win").sum())
                    st.metric("Total Loses", (result["outcome"] == "lose").sum())
                    st.metric("Wins Against Normal Pokemon", (result_normal["outcome"] == "win").sum())
                    st.metric("Loses Against Normal Pokemon", (result_normal["outcome"] == "lose").sum())  
                    
                with col4:
                    st.header("Result Based on Specific Categories")
                    st.metric("Wins Against Legendary and Sub Legendary Pokemon", (result_legendary["outcome"] == "win").sum())
                    st.metric("Loses Against Legendary and Sub Legendary Pokemon", (result_legendary["outcome"] == "lose").sum())
                    st.metric("Wins Against Mythical Pokemon", (result_mythical["outcome"] == "win").sum())
                    st.metric("Loses Against Mythical Pokemon", (result_mythical["outcome"] == "lose").sum())
                    st.metric("Wins Against Mega Evolutions", (result_mega["outcome"] == "win").sum())
                    st.metric("Loses Against Mega Evolutions", (result_mega["outcome"] == "lose").sum())
        except Exception as e:
            st.error(f"An unexpected error {e} occured")


def do_one_vs_one(details, type_chart):
    with st.form(key="one"):
        for_ = st.text_input("Enter the name of Your Pokemon")
        against = st.text_input("Enter the name of the Opponent Pokemon")
        #level = st.slider("Select Level of Both The Pokemon", 1, 100, 50)
        submitted = st.form_submit_button("Submit")
    if submitted:
        def one_vs_one(details, type_chart, for_, against):
            """
            Parameters: details - pd.DataFrame() containing necessary details of Pokemon scraped from Bulbapedia
            type_chart: pd.DataFrame() containing Pokemon type chart with offensive typing as row index and defensive a column headings
            for_: str containing the name of the Pokemon you choose
            against: str containing the name of the Pokemon you want to play against
            return: a str containing "win", "lose" or "draw"
            """
            details = details.copy()
            
            for_ = for_.capitalize()
            against = against.capitalize()
            for_data = details[details["name"] == for_]
            against_data = details[details["name"] == against]

            if len(for_data) < 1 or len(against_data) < 1:
                st.error("Enter Valid Pokemon Names")
                return None
            
            for_attack = for_data["main_attack"].iloc[0]
            for_defense = np.where(against_data["attack"] >= against_data["special_attack"],
                                  for_data["defense"].iloc[0], for_data["special_defense"].iloc[0])
            for_speed = for_data["speed"].iloc[0]
            for_hp = for_data["hp"].iloc[0]
            for_type1 = for_data["type1"].iloc[0]
            for_type2 = for_data["type2"].iloc[0]

            for_number = for_data["number"].iloc[0]
            against_attack = against_data["main_attack"].iloc[0]
            against_defense = np.where(for_data["attack"] >= for_data["special_attack"],
                                      against_data["defense"].iloc[0], against_data["special_defense"].iloc[0])
            against_speed = against_data["speed"].iloc[0]
            against_hp = against_data["hp"].iloc[0]
            against_type1 = against_data["type1"].iloc[0]
            against_type2 = against_data["type2"].iloc[0]
            against_number = against_data["number"].iloc[0]
        
            for_ad = for_attack/against_defense
            against_ad = against_attack/for_defense
        
            for_offense_type11 = type_chart.loc[for_type1, :][against_type1]
            for_offense_type12 = type_chart.loc[for_type1, :][against_type2]
            for_offense_only_type1 = for_offense_type11 * for_offense_type12
            for_offense_type21 = type_chart.loc[for_type2, :][against_type1]
            for_offense_type22 = type_chart.loc[for_type2, :][against_type2]
            for_offense_only_type2 = for_offense_type21 * for_offense_type22
            for_offense = np.maximum(for_offense_only_type1, for_offense_only_type2)
        
            against_offense_type11 = type_chart.loc[against_type1, :][for_type1]
            against_offense_type12 = type_chart.loc[against_type1, :][for_type2]
            against_offense_only_type1 = against_offense_type11 * against_offense_type12
            against_offense_type21 = type_chart.loc[against_type2, :][for_type1]
            against_offense_type22 = type_chart.loc[against_type2, :][for_type2]
            against_offense_only_type2 = against_offense_type21 * against_offense_type22
            against_offense = np.maximum(against_offense_only_type1, against_offense_only_type2)
        
            power = 80
            level = 50
            damage_dealt_for = (((2*level/5+2)*power*for_ad)/50+2)*for_offense
            damage_dealt_against = (((2*level/5+2)*power*against_ad)/50+2)*against_offense
            
            turns_taken_for = np.ceil(against_hp/damage_dealt_for)
            turns_taken_against = np.ceil(for_hp/damage_dealt_against)
            if turns_taken_for[0] < turns_taken_against[0]:
                return "won", for_number, against_number
            elif turns_taken_for[0] == turns_taken_against[0]:
                if for_speed > against_speed:
                    return "won", for_number, against_number
                elif for_speed == against_speed:
                    return "draw", for_number, against_number
                else:
                    return "lose", for_number, against_number
            else:
                return "lose", for_number, against_number

        try:
            result, for_number, against_number = one_vs_one(details, type_chart, for_, against)
            if result == None: 
                st.error("Name of the Pokemon not found please check the spelling")
            else:
                url1 = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{for_number}.png"
                url2 = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{against_number}.png"
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader(for_)
                    st.image(url1)
                with col2:
                    st.subheader(against)
                    st.image(url2)
                if result == "won":
                    st.title(f"The Winner is {for_}")
                    st.balloons()
                elif result == "draw":
                    st.title(f"Same Strength just be Friends {for_} and {against}")
                else:
                    st.title(f"The winner is {against}")
        except Exception as e:
            st.error(f"An unexpected error {e} occured")
            
def do_simulation_based_on_moves(details, type_chart, moves):
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
        


tab1, tab2, tab3 = st.tabs(["All Together", "One Vs One", "One Vs One With Moves"])
with tab1:
    do_all_together(details, type_chart)
with tab2:
    do_one_vs_one(details, type_chart)
with tab3:
    do_simulation_based_on_moves(details, type_chart, moves)