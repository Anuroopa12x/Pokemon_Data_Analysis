import pandas as pd
import numpy as np
import streamlit as st
import requests
import urllib.request
import os

stats = pd.read_csv("/home/anuroopa/Desktop/Data_analysis_projects/Pokemon/stats.csv", index_col = 0)
details = pd.read_csv("/home/anuroopa/Desktop/Data_analysis_projects/Pokemon/data.csv", index_col = 0)
type_chart = pd.read_csv("/home/anuroopa/Desktop/Data_analysis_projects/Pokemon/Pokemon_Type_Chart.csv", index_col = 0)
details = stats.merge(details)

with st.form(key = "pokemon"):
    name = st.text_input("Enter name of the pokemon: ")
    name = name.capitalize()
    submit_name = st.form_submit_button("Submit")

if submit_name:
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

    result, number = stimulator(details, type_chart, name)
    st.write("Pokedex Number", number)
    url = f"https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/full/{number}.png"
    filename = "/home/anuroopa/Desktop/Data_analysis_projects/Pokemon/static/pokemon.png"
    try:
        urllib.request.urlretrieve(url, filename=filename)
    except Exception as e:
        st.write(f"Unable to retrieve image of {name}", e)

    st.image(os.path.join(os.getcwd(), "static", "pokemon.png"))
    st.metric("Wins", (result["outcome"] == "win").sum())
    st.metric("Loses", (result["outcome"] == "lose").sum())