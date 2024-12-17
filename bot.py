import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key

#print(f"Twój klucz api to: {openai_api_key}")
def chat(content):
	response = openai.ChatCompletion.create(
		model="gpt-3.5-turbo",
		messages=[{
			"role":"user",
			"content":content
			}],
		)
	return response["choices"][0]["message"]["content"]

while True:
    user_input = input("Ty: ")
    if user_input.lower() in ["exit", "quit"]:
        break
    gpt_response = chat(user_input)
    print(f"ChatGPT: {gpt_response}")
