import google.generativeai as genai
import os
def talk_to_gemini(query):
    # Call Gemini API
    genai.configure(os.getenv("GOOGLE_GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(query)
    # print(response.text)
    return response.text

print(talk_to_gemini("generate me a 10 days plan for weight loss in json format also only give json dont give any else description")) 