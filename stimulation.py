import pandas as pd
import numpy as np
import streamlit as st


@st.cache_data
def load_data():
    stats = pd.read_csv("stats.csv", index_col = 0)
    data = pd.read_csv("data.csv", index_col = 0)
    type_chart = pd.read_csv("Pokemon_Type_Chart.csv", index_col = 0)
    details = stats.merge(data)
    return details, type_chart
    

details, type_chart = load_data()
mode = st.radio("Select Mode",
               ["All Together", "One Vs One"], horizontal=True)

def do_all_together(details, type_chart):
    with st.form(key = "pokemon"):
        name = st.text_input("Enter name of the pokemon: ")
        name = name.capitalize()
        submitted = st.form_submit_button("Submit")
        
    if submitted:
        def stimulator(details, type_chart, name):
        
            details = details.copy()
            level = 50 
            
            details["hp"] = np.floor(((2 * details["hp"] + 31) * level) / 100) + level + 10
            details["attack"] = np.floor(((2 * details["attack"] + 31) * level) / 100) + 5
            details["defense"] = np.floor(((2 * details["defense"] + 31) * level) / 100) + 5
            details["special_attack"] = np.floor(((2 * details["special_attack"] + 31) * level) / 100) + 5
            details["special_defense"] = np.floor(((2 * details["special_defense"] + 31) * level) / 100) + 5
            details["speed"] = np.floor(((2 * details["speed"] + 31) * level) / 100) + 5
            details[["type1", "type2"]] = details["type"].str.split(" / ", expand = True)
            details["type2"] = details["type2"].fillna("Nil")
            
            details["main_attack"] = np.maximum(details["attack"], details["special_attack"])
            
            pokemon = details[details["name"].str.contains(name, case = False)]
            if len(pokemon) < 1:
                print(f"The given name: {name} is not a name of available pokemon")
                return None
        
            attack = pokemon["attack"].iloc[0]
            special_attack = pokemon["special_attack"].iloc[0]
            details["main_defense"] = np.where(attack >= special_attack, details["defense"], details["special_defense"])
        
            speed = pokemon["speed"].iloc[0]
            defense = pokemon["defense"].iloc[0]
            special_defense = pokemon["special_defense"].iloc[0]
            main_attack = pokemon["main_attack"].iloc[0]
            type1 = pokemon["type1"].iloc[0]
            type2 = pokemon["type2"].iloc[0]
            hp = pokemon["hp"].iloc[0]
            
            if pokemon["number"].iloc[0].startswith("#0"):
                number = pokemon["number"].iloc[0].replace("#0", "")
            else:
                number = pokemon["number"].iloc[0].replace("#", "")
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
        
            return details.loc[:, ["name", "outcome"]], number

        try:
            result, number = stimulator(details, type_chart, name)
            if number == None:
                st.error(f"Name of the Pokemon {name} not found please check the spelling")
            else:
                st.subheader(f"Pokedex Number is {number}")
                url = f"https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/full/{number}.png"
                st.image(url)
                st.metric("Wins", (result["outcome"] == "win").sum())
                st.metric("Loses", (result["outcome"] == "lose").sum())
        except Exception as e:
            st.error(f"An unexpected error {e} occured")


def do_one_vs_one(details, type_chart):
    with st.form(key="one"):
        for_ = st.text_input("Enter the name of Your Pokemon")
        against = st.text_input("Enter the name of the Opponent Pokemon")
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
            
            level = 50 
            
            details["hp"] = np.floor(((2 * details["hp"] + 31) * level) / 100) + level + 10
            details["attack"] = np.floor(((2 * details["attack"] + 31) * level) / 100) + 5
            details["defense"] = np.floor(((2 * details["defense"] + 31) * level) / 100) + 5
            details["special_attack"] = np.floor(((2 * details["special_attack"] + 31) * level) / 100) + 5
            details["special_defense"] = np.floor(((2 * details["special_defense"] + 31) * level) / 100) + 5
            details["speed"] = np.floor(((2 * details["speed"] + 31) * level) / 100) + 5
            details[["type1", "type2"]] = details["type"].str.split(" / ", expand = True)
            details["type2"] = details["type2"].fillna("Nil")
            
            details["main_attack"] = np.maximum(details["attack"], details["special_attack"])
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
            if for_data["number"].iloc[0].startswith("#0"):
                for_number = for_data["number"].iloc[0].replace("#0", "")
            else:
                for_number = for_data["number"].iloc[0].replace("#", "")
            against_attack = against_data["main_attack"].iloc[0]
            against_defense = np.where(for_data["attack"] >= for_data["special_attack"],
                                      against_data["defense"].iloc[0], against_data["special_defense"].iloc[0])
            against_speed = against_data["speed"].iloc[0]
            against_hp = against_data["hp"].iloc[0]
            against_type1 = against_data["type1"].iloc[0]
            against_type2 = against_data["type2"].iloc[0]
            if against_data["number"].iloc[0].startswith("#0"):
                against_number = against_data["number"].iloc[0].replace("#0", "")
            else:
                against_number = against_data["number"].iloc[0].replace("#", "")
        
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
                url1 = f"https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/full/{for_number}.png"
                url2 = f"https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/full/{against_number}.png"
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


if mode == "All Together":
    do_all_together(details, type_chart)
elif mode == "One Vs One":
    do_one_vs_one(details, type_chart)