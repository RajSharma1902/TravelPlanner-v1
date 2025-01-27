import streamlit as st
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai
import os
import json
from gemini import Gemini
import spacy

# Load the spaCy model for NLP
nlp = spacy.load("en_core_web_sm")

if 'counter' not in st.session_state:
    st.session_state['counter'] = 0
if 'generate_button_clicked' not in st.session_state:
    st.session_state["generate_button_clicked"] = False
if 'model' not in st.session_state:
    st.session_state["model"] = None
if 'response' not in st.session_state:
    st.session_state["response"] = ""

def extract_locations(text):
    if isinstance(text, dict):
        text = "".join(f"{t}" for t in text.values())

    locations = {}
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "GPE":  # Geopolitical entity (location)
            locations[ent.text] = True  # Placeholder for location extraction
    return locations

def main():
    session_state = st.session_state

    st.title("Travel Planner")
    model = st.session_state["model"]

    col1, col2, col3 = st.columns([1, 4, 1])

    # Option for user to choose survey or text input
    input_option = st.radio("Choose your input type:", ["Survey", "Text Input"])

    if input_option == "Survey":
        # Survey details
        st.sidebar.header("Trip Details")
        members = st.sidebar.text_input("How big is your group?", "1")
        location = st.sidebar.text_input("Enter the Location", "Banglore,India")
        budget = st.sidebar.text_input("Budget", "10k ruppees to 15k ruppees")
        days = st.sidebar.number_input("For how many days?", min_value=1, value=1)
        purpose = st.sidebar.text_input("Purpose of Trip?", "Buisness")
        preferences = st.sidebar.text_input("Preferences", "Less Crowded")
        foodType = st.sidebar.text_input("Food Preference", "Veg")
        stayLocation = st.sidebar.text_input("Where are you staying")
        geminiModel=st.sidebar.selectbox("Choose Gemini Model:",["gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-1.5-pro"],index=0)
        if st.sidebar.button("Generate Trip Plan"):
            model = Gemini(location, days, members, budget, purpose, preferences,foodType,stayLocation,geminiModel,None)
            model.get_response(markdown=False)
            st.session_state["model"] = model
            st.session_state["generate_button_clicked"] = True

    elif input_option == "Text Input":
        # Text input option
        trip_details = st.sidebar.text_area("Enter Trip Details in a short paragraph:")
        geminiModel=st.sidebar.selectbox("Choose Gemini Model:",["gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-1.5-pro"],index=0)
        if st.sidebar.button("Generate Trip Plan"):
            # Process the text input and pass it to the model
            # You can implement your logic here to parse the text and extract relevant info
            # For example, use regex or NLP techniques
            model = Gemini(None, None, None, None, None, None,None,None,geminiModel,trip_details)
            model.get_response(markdown=False)
            st.session_state["model"] = model
            st.session_state["generate_button_clicked"] = True

    with col2:
        st.title("Gemini Response")
        response = {}
        
        if st.session_state["generate_button_clicked"]:
            with open(r'/Users/rajnarayansharma/Desktop/InternShip/Prompt/ModelResponse/gemini_answer.json', 'r', encoding="utf-8") as file:
                response = json.load(file)
                st.session_state["response"] = response

        current_day = f"Day {st.session_state['counter'] + 1}"
        current_day_placeholder = st.empty()
        current_day_infos = st.empty()

        if model is not None:
            if current_day in response:
                current_day_placeholder.markdown(f"### {current_day}")

                # Extract and format the activities for the current day
                day_data = response[current_day]
                formatted_info = ""
                for time_slot, activities in day_data.items():
                    formatted_info += f"**{time_slot}:**\n"
                    formatted_info += "\n".join([f"- {activity}" for activity in activities])
                    formatted_info += "\n\n"

                # Display the formatted trip plan for the current day
                current_day_infos.markdown(formatted_info)
            else:
                current_day_infos.write("Generate a Trip Plan!")

        # Button to move to the next day
        button = st.button("Next Day")
        if button and st.session_state['counter'] < len(response) - 1:
            st.session_state['counter'] += 1
            current_day = f"Day {st.session_state['counter'] + 1}"

            if current_day in response:
                current_day_placeholder.markdown(f"### {current_day}")

                # Extract and format the activities for the next day
                day_data = response[current_day]
                formatted_info = ""
                for time_slot, activities in day_data.items():
                    formatted_info += f"**{time_slot}:**\n"
                    formatted_info += "\n".join([f"- {activity}" for activity in activities])
                    formatted_info += "\n\n"

                current_day_infos.markdown(formatted_info)
            else:
                current_day_infos.write("No information available for this day.")

if __name__ == '__main__':
    main()
