import os
from flask import Flask, request, jsonify, stream_with_context, Response, render_template
#from flask_cors import CORS
import openai
import json
from dotenv import load_dotenv

# Ładowanie klucza OpenAI
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

def get_account_balance(user_id):

    #print("##### funkcja: get_account_balance ###")
    #print(user_id)

    accounts = {
        "123": {"balance": 1500.75, "currency": "PLN"},
        "456": {"balance": 250.00, "currency": "PLN"},
        "789": {"balance": 0.00, "currency": "PLN"},
    }

    return accounts.get(user_id, None)  # Zwracaj None, jeśli konto nie istnieje

def get_user_info(user_id):

    #print("##### funkcja: get_user_info ###")
    #print(user_id)

    users = {

        "123": {"name": "Pawel", "wiek": 90},
        "456": {"name": "Tomasz", "wiek": 20},
        "789": {"name": "Krzysztof", "wiek": 30},

    }
    return users.get(user_id, None)  # Zwracaj None, jeśli konto nie istnieje
def get_todays_games():
    games = [
        {"home_team": "Real Madrid", "away_team": "Barcelona", "time": "20:00"},
        {"home_team": "Liverpool", "away_team": "Manchester United", "time": "18:00"},
        {"home_team": "Juventus", "away_team": "Inter Milan", "time": "21:00"},
    ]
    return games



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
    },
    {
        "name": "get_user_info",
        "description": "Sprawdź informację o użytkowniku. Takie jak wiek, imię, itp.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "ID użytkownika, dla którego chcesz sprawdzić informacje."
                }
            },
            "required": ["user_id"]
        }
    },
    {
        "name": "get_todays_games",
        "description": "Pobierz listę dzisiejszych gier.",
        "parameters": {}
    }




]

# Strona główna

@app.route("/")

def index():
    return render_template("index.html")


# Endpoint do strumieniowania odpowiedzi

@app.route("/stream", methods=["POST"])
def stream():
    user_input = request.json.get("message", "").strip()
    user_id = request.json.get("user_id", "").strip()

    #print("User input :",user_input)
    #print("User Id :",user_id)

    # Sprawdź, czy użytkownik podał wiadomość i ID użytkownika
    if not user_input:
        return Response("Brak wiadomości", status=400)
    if not user_id:
        return Response("Brak user_id", status=400)

    # Funkcja generatora do przesyłania strumienia
    def generate():

        asistent_info = (
            "Jesteś asystentem gracza odpowiedzialnym za zachęcanie do składania zakładów bukmacherskich. "
            "Jesteś w tym najlepszy i najskuteczniejszy. Namawiasz w sposób wysublimowany i nienachalny. "
            "Masz na imię Albert. Wyrażasz się w sposób zwięzły i konkretny."
        )

        system_message = (asistent_info)         
        
        

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": system_message,
                    },
                    {"role": "user", "content": user_input},
                ],
                temperature=0.5,
                max_tokens=100,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                functions=functions,
                function_call="auto",
                stream=True,
            )

            for chunk in response:
                if "choices" in chunk and len(chunk["choices"]) > 0:
                    delta = chunk["choices"][0].get("delta", {})

                    # Obsługa zawartości odpowiedzi
                    if "content" in delta:
                        yield f"data: {delta['content']}\n\n"
                        #system_message += delta["content"]

                    # Obsługa funkcji (np. get_account_balance)
                    if "function_call" in delta:
                        function_call = delta.get("function_call", {})
                        #print("Function Call:", function_call)
                        # Upewnij się, że "name" istniejeo wieku
                        function_name = function_call.get("name","")
                        #print(function_name)
                        if function_name == "get_account_balance":

                            #arguments = json.loads(function_call.get("arguments", "{}"))
                            arguments = user_id
                            print("### Wywołano get_account_balance ###")
                            balance_info = get_account_balance(user_id)
                            if balance_info:
                                #system_message += f"Stan konta wynosi {balance_info['balance']} {balance_info['currency']}."
                                yield (
                                    f"data: Stan twojego konta wynosi {balance_info['balance']} "
                                    f"{balance_info['currency']}.\n\n"   
                                )
                            else:
                                yield f"data: Nie znaleziono konta dla podanego ID użytkownika.\n\n"

                        if function_name == "get_user_info":
                            arguments = user_id
                            print("### Wywołano get_user_info ###")
                            user_info = get_user_info(user_id)
                            if user_info:
                                yield (
                                    f"data: Nazywasz się {user_info['name']} "
                                    f"i masz {user_info['wiek'] } lat.\n\n"

                                )
                                #system_message += f"Użytkownik ma na imię {user_info['name']} i ma {user_info['wiek']} lat."
                            else:
                                yield f"data: Nie znaleziono użytkownika dla podanego ID.\n\n"
                        if function_name == "get_todays_games":
                            print("### Wywołano get_todays_games ###")
                            games = get_todays_games()
                            if games:
                                yield "data: Oto lista dzisiejszych gier:\n\n\n"
                                for game in games:
                                    yield (
                                        f"data: {game['home_team']} vs {game['away_team']} o godzinie {game['time']}.\n\n"
                                    )
                            else:
                                yield f"data: Brak dzisiejszych gier.\n\n"

        except Exception as e:
            app.logger.error(f"Error: {str(e)}")
            yield f"data: Błąd: {str(e)}\n\n"
    return Response(generate(), content_type="text/event-stream")

if __name__ == "__main__":
    app.run(debug=True)
