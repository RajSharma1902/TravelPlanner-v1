import google.generativeai as genai
import os
import streamlit as st
gemini_api_key = st.secrets["general"]["GEMINI_API_KEY"]
genai.configure(api_key=gemini_api_key)
import json
import textwrap

class Gemini:
    def __init__(self, location=None, days=None, members=None, budget=None, purpose=None, preferences=None, foodType=None, stayLocation=None, geminiModel=None, trip_details=None):
        # If text input is provided, use it instead of individual parameters
        self.trip_details = trip_details
        if trip_details:
            # Assuming you process the trip_details to extract the necessary values
            # Example: You can use NLP or regular expressions to parse the details from the text
            # For now, we'll just store the entire input
            self.trip_details = trip_details
            self.location = None
            self.days = None
            self.members = None
            self.budget = None
            self.preferences = None
            self.purpose = None
            self.foodType = None
            self.stayLocation = None
        else:
            # Use the parameters from the survey if no text input is provided
            self.location = location
            self.days = days
            self.members = members
            self.budget = budget
            self.preferences = preferences
            self.purpose = purpose
            self.foodType = foodType
            self.stayLocation = stayLocation

        # Use the selected Gemini model
        self.model = genai.GenerativeModel(f'{geminiModel}')
        
    @staticmethod    
    def to_markdown(text):
        text = text.replace('•', '  *')
        return textwrap.indent(text, '> ', predicate=lambda _: True)

    def parse_trip_plan(self, trip_plan, return_=True):
        # Split the trip plan into days, skipping the initial part
        days = trip_plan.split("**Day ")[1:]  
        trip_dict = {}
        
        for i, day in enumerate(days, start=1):
            day_num = f"Day {i}"
            
            # Split day content into Morning, Afternoon, and Evening parts
            parts = day.split("alphaMorning:")
            morning = parts[1].split("alphaAfternoon:")[0].strip().split("\n")
            afternoon = parts[1].split("alphaAfternoon:")[1].split("alphaEvening:")[0].strip().split("\n")
            evening = parts[1].split("alphaEvening:")[1].strip().split("\n")
            
            # Clean up and convert to lists
            morning = [item.strip() for item in morning if item.strip()]
            afternoon = [item.strip() for item in afternoon if item.strip()]
            evening = [item.strip() for item in evening if item.strip()]
            
            # Construct the dictionary for the day
            trip_dict[day_num] = {
                "Morning": morning,
                "Afternoon": afternoon,
                "Evening": evening
            }
        
        # Write the parsed trip plan into a JSON file
        file_path = os.path.join(os.getcwd(), "gemini_answer.json")  # This saves in the current working directory
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(trip_dict, json_file, indent=4, ensure_ascii=False)

        if return_:
            return trip_dict

    
    def get_response(self, markdown=True):
        if self.trip_details:
            prompt = f"""
                Generate a trip plan using the information provided in The text below:
                {self.trip_details}
                In Case the details provided are not enough Tell the user to provide the neccasry details that are missing accoridng to you(can be budget,food preferecne or anything else)
                Provide a detailed itinerary for each day in the **EXACT FORMAT BELOW**:
                ---
                **Day X:**  
                alphaMorning:  
                - [Place Name] (Brief description, duration to stay)  
                alphaAfternoon:  
                - [Place Name] (Brief description, duration to stay)  
                alphaEvening: 
                - [Place Name] (Brief description, duration to stay)  
                ---
                Provide UTF-8 encoded output with **NO deviations**. Each section (Morning, Afternoon, Evening) must include multiple bullet points. Ensure the structure is strictly followed. If Google Maps links can be added, include them in this format: https://www.google.com/maps?q=Location+Name.

                ---
            """
        else:
            prompt = f"""
                Generate a trip plan for {self.location}, {self.budget} spanning {self.days} days for a group of {self.members} with the purpose of {self.purpose} and preferences for {self.preferences}.
                The trip should include a mix of historical sightseeing, cultural experiences, and delicious food, along with peaceful places based on {self.preferences}.
                Food preference: {self.foodType}, Staying at: {self.stayLocation}.
                Provide a detailed itinerary for each day in the **EXACT FORMAT BELOW**:
                ---
                **Day X:**  
                alphaMorning:  
                - [Place Name] (Brief description, duration to stay)  
                alphaAfternoon:  
                - [Place Name] (Brief description, duration to stay)  
                alphaEvening: 
                - [Place Name] (Brief description, duration to stay)  
                ---
                Provide UTF-8 encoded output with **NO deviations**. Each section (Morning, Afternoon, Evening) must include multiple bullet points. Ensure the structure is strictly followed. If Google Maps links can be added, include them in this format: https://www.google.com/maps?q=Location+Name.
            ---
            """
        response = self.model.generate_content(prompt)
        if response.parts:
            response = response.parts[0].text
        
        if markdown:
            response = self.to_markdown(response)
        else:
            response = self.parse_trip_plan(response)
        return response