import pandas as pd
import numpy as np
import streamlit as st
import requests

stats = pd.read_csv("/home/user/Desktop/Data_analysis_projects/Pokemon/stats.csv", index_col = 0)
details = pd.read_csv("/home/user/Desktop/Data_analysis_projects/Pokemon/data.csv", index_col = 0)
type_chart = pd.read_csv("/home/user/Desktop/Data_analysis_projects/Pokemon/Pokemon_Type_Chart.csv", index_col = 0)
details = stats.merge(details)

with st.form(key = "pokemon"):
    name = st.text_input("Enter name of the pokemon: ")
    submit_name = st.form_submit_button("Submit")
if submit_name:
    def stimulator(details, type_chart, name):

        details = details.copy()
        details["hp"] = details["hp"] + 60
        details[["attack", "special_attack", "defense", "special_defense", "speed"]] += 5
        details["main_attack"] = np.where(details["attack"] >= details["special_attack"],details["attack"], details["special_attack"])
        details["main_defense"] = np.where(details["defense"] >= details["special_defense"], details["defense"], details["special_defense"])

        details[["type1", "type2"]] = details["type"].str.split(" / ", expand = True)
        details["type2"] = details["type2"].fillna("Nil")

        pokemon = details[details["name"].str.contains(name, case = False)]
        speed = pokemon["speed"].iloc[0]
        attack = pokemon["main_attack"].iloc[0]
        defense = pokemon["main_defense"].iloc[0]
        type1 = pokemon["type1"].iloc[0]
        type2 = pokemon["type2"].iloc[0]
        hp = pokemon["hp"].iloc[0]

        if len(pokemon) < 1:
            print(f"The given name: {name} is not a name of available pokemon")
            return None
        else:
            print(f"{name.capitalize()} is a pokemon")

        details["A/D_pokemon"] = attack / details["main_defense"]
        details["A/D_others"] = details["main_attack"] / defense
        type11_offense = np.array([type_chart.loc[type1, :][x] for x in details["type1"]])
        type12_offense = np.array([type_chart.loc[type1, :][x] for x in details["type2"]])
        # if type2 != "Nil":
        #     type21_offense = np.array([type_chart.loc[type2, :][x] for x in details["type1"]])
        #     type22_offense = np.array([type_chart.loc[type1, :][x] for x in details["type1"]])
        details["pokemon_type_offense"] = type11_offense * type12_offense 

        type11_other_offense = np.array([type_chart.loc[x, :][type1] for x in details["type1"]])

        if type2 != "Nil":
            type21_other_offense = np.array([type_chart.loc[x, :][type2] for x in details["type1"]])
            details["others_type_offense"] = type11_other_offense * type21_other_offense
        else:
            details["others_type_offense"] = type11_other_offense

        power = 80
        level = 50
        details["damage_dealt_pokemon"] = (((2*level+2)*power*details["A/D_pokemon"])+2)*details["pokemon_type_offense"]
        details["damage_dealt_others"] = (((2*level+2)*power*details["A/D_others"])+2)*details["others_type_offense"]

        #all_other= details.loc[details["name"].str.contains(name, case = False) == False, :]


        #details["chance"] = np.where(details["speed"] == speed, np.random.choice([1,2]), None)
        details["chance"] = np.where(details["speed"] < speed, 1, 
                                     np.where(details["speed"] > speed, 2,
                                    np.random.randint(1, 3, len(details))))

        details["turns_to_win_pokemon"] = np.ceil(details["hp"] / details["damage_dealt_pokemon"])
        details["turns_to_win_others"] = np. ceil(hp / details["damage_dealt_others"])

        #details["outcome"] = np.where((details["turns_to_win_pokemon"] == details["turns_to_win_others"]) &
                                      #(details["chance"] == 1), "win", "lose")
        details["outcome"] = np.where(details["turns_to_win_pokemon"] < details["turns_to_win_others"], "win",
                                      np.where(details["turns_to_win_pokemon"] > details["turns_to_win_others"], "lose",
                                              np.where(details["chance"] == 1, "win", "lose")))

        return details.loc[:, ["name", "outcome"]]


    st.dataframe(stimulator(details, type_chart, name))