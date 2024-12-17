import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import json
from dotenv import load_dotenv

# Ładowanie klucza OpenAI
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Tworzenie aplikacji Flask
app = Flask(__name__)
CORS(app)

# Przykładowa baza danych kont
def get_account_balance(user_id):
    accounts = {
        "123": {"balance": 1500.75, "currency": "PLN"},
        "456": {"balance": 250.00, "currency": "PLN"},
        "789": {"balance": 0.00, "currency": "PLN"},
    }
    return accounts.get(user_id, None)  # Zwracaj None, jeśli konto nie istnieje

# Funkcja dostępna dla GPT
functions = [
    {
        "name": "get_account_balance",
        "description": "Sprawdź aktualny stan konta użytkownika.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "ID użytkownika, dla którego chcesz sprawdzić stan konta."
                }
            },
            "required": ["user_id"]
        }
    }
]

@app.route("/chat", methods=["POST"])
def chat():
    # Odbieranie wiadomości od użytkownika
    data = request.json
    user_message = data.get("message", "").strip()
    user_id = data.get("user_id", "").strip()

    if not user_message or not user_id:
        return jsonify({"error": "Brak wiadomości lub ID użytkownika!"}), 400

    # Wysyłanie wiadomości do GPT
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "Jesteś asystentem gracza odpowiedzialnym za zachęcanie do składania zakładów bukmacherskich. Jesteś w tym najlepszy i najskuteczniejszy. Namawiasz w sposób wysublimowany i nienachalny. Masz na imię Albert. Wyrażasz się w sposób zwięzły i konkretny."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=100,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            functions=functions,
            function_call="auto"
        )

        chatbot_message = response["choices"][0]["message"]

        if "function_call" in chatbot_message:
            function_call = chatbot_message["function_call"]

            if function_call["name"] == "get_account_balance":
                # Pobranie parametrów funkcji
                arguments = json.loads(function_call["arguments"])
                user_id = user_id
                balance_info = get_account_balance(user_id)

                if balance_info:
                    # Zwrócenie stanu konta
                    return jsonify({
                        "reply": f"Stan Twojego konta wynosi {balance_info['balance']} {balance_info['currency']}."
                    })
                else:
                    return jsonify({
                        "reply": "Nie znaleziono konta dla podanego ID użytkownika."
                    })

        # Zwrócenie odpowiedzi GPT
        chatbot_reply = chatbot_message.get("content", "Brak odpowiedzi od GPT.")
        return jsonify({"reply": chatbot_reply})

    except json.JSONDecodeError as e:
        return jsonify({"error": "Błąd w parsowaniu argumentów funkcji: " + str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Uruchamianie serwera
if __name__ == "__main__":
    app.run(debug=True, port=5000)
