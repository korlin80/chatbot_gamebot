import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key

# Konfiguracja OpenAI
#openai.api_key = "TWÓJ_KLUCZ_API"

# Tworzenie aplikacji Flask
app = Flask(__name__)
CORS(app)

@app.route("/chat", methods=["POST"])
def chat():
    # Odbieranie wiadomości od użytkownika
    data = request.json
    user_message = data.get("message", "")
    
    if not user_message:
        return jsonify({"error": "Brak wiadomości!"}), 400

    # Wysyłanie wiadomości do GPT
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Masz na imię Albert. Jesteś asystentem gracza odpowiedzialnym za zachęcanie do składania zakładów bukmacherskich. Jesteś w tym najlepszy i najskuteczniejszy. Namawiasz w sposób wysublimowany i nienachalny."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_completion_tokens=1024,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        chatbot_reply = response["choices"][0]["message"]["content"]
        return jsonify({"reply": chatbot_reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Uruchamianie serwera
if __name__ == "__main__":
    app.run(debug=True, port=5000)
