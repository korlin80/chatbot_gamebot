import os
from flask import Flask, request, jsonify, stream_with_context, Response, render_template, session
#from flask_cors import CORS
import openai
import json
from dotenv import load_dotenv

# Loading OpenAI key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")
openai.api_key = api_key

app = Flask(__name__)
app.secret_key = 'my_own_secret_key_haha'

def get_account_balance(user_id):

    #print("##### funkcja: get_account_balance ###")
    #print(user_id)

    accounts = {
        "123": {"balance": 1500.75, "currency": "PLN"},
        "456": {"balance": 250.00, "currency": "PLN"},
        "789": {"balance": 0.00, "currency": "PLN"},
    }

    return accounts.get(user_id, None)  # Return None if the account does not exist

def get_user_info(user_id):

    users = {

        "123": {"name": "Pawel", "age": 90},
        "456": {"name": "Tomasz", "age": 20},
        "789": {"name": "Krzysztof", "age": 30},
    }

    return users.get(user_id, None)  # Return None if the user does not exist

    
def get_todays_games():
    # Those values should be sended to model as json
    games = [
        {"home_team": "Real Madrid", "away_team": "Barcelona", "time": "20:00"},
        {"home_team": "Liverpool", "away_team": "Manchester United", "time": "18:00"},
        {"home_team": "Juventus", "away_team": "Inter Milan", "time": "21:00"},
    ]
    return games


# Functions handled by GPT

functions = [

    {
        "name": "get_account_balance",
        "description": "Check the current account balance of the user.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "User ID for which you want to check the account balance."
                }
            },
            "required": ["user_id"]
        }
    },
    {
        "name": "get_user_info",
        "description": "Check user information such as age, name, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "User ID for which you want to check the information."
                }
            },
            "required": ["user_id"]
        }
    },
    {
        "name": "get_todays_games",
        "description": "Get the list of today's games.",
        "parameters": {}
    }

]

def prepareInformationsForAssisten(user_id):
    # Function to prepare info about user as a string.
    user = get_user_info(user_id)
    if not user:
        return "User not found for the given ID."
    
    user_info_str = f"User's name is {user['name']} and he is {user['age']} years old."
    return user_info_str

def prepareAccoutnInformationForAssisten(user_id):
    acountInfo = get_account_balance(user_id)
    if not acountInfo:
        return "Account value not found for given ID."
    account_info= f"User's account balance is {acountInfo['balance']} {acountInfo['currency']}"
    return account_info


# Main page

@app.route("/")

# Endpoint for streaming responses

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    user_id = request.json.get("user_id", "").strip()
    if not user_id:
        return jsonify({"error": "Brak user_id"}), 400
    session['user_id'] = user_id
    return jsonify({"message": f"Zalogowano uzytkownika o ID {user_id}"}), 200

@app.route("/logout", methods=["GET"])
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Wylogowano pomyślnie"}), 200


@app.route("/stream", methods=["POST"])
def stream():

    user_input = request.json.get("message", "").strip()
    user_id = session.get("user_id", "")

    #print("User input :",user_input)
    #print("User Id :",user_id)

    # Check if the user provided a message and user ID
    if not user_input:
        return Response("Brak wiadomości", status=400)
    if not user_id:
        return Response("Brak user_id w sesji. Zaloguj się ponownie.", status=400)

    # Generator function for streaming
    def generate():

        asistent_info = (
            "You are a game assistant responsible for encouraging users to place bets. "
            "You are the best and most effective at this. You persuade in a subtle and non-intrusive way. "
            "Your name is Albert. You express yourself concisely and clearly."
        )

        system_message = (asistent_info)         
        #add info about player.
        #print("Zwrocona wartość: {prepareInformationsForAssisten}")
        system_message += prepareInformationsForAssisten(user_id)
        system_message += prepareAccoutnInformationForAssisten(user_id)

        print(get_account_balance(user_id))
        # get_user_info(user_id)

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

                    # Handle response content
                    if "content" in delta:
                        yield f"data: {delta['content']}\n\n"

                    # Handle functions (e.g., get_account_balance)
                    if "function_call" in delta:
                        function_call = delta.get("function_call", {})
                        function_name = function_call.get("name","")
                    #    arguments = json.loads(function_call.get("arguments", "{}"))

                        if function_name == "get_account_balance":

                            #user_id = arguments.get("user_id")
                            
                            print("### Called get_account_balance ###")
                            balance_info = get_account_balance(user_id)
                            if balance_info:

                                yield (
                                    f"data: Stan twojego konta wynosi {balance_info['balance']} "
                                    f"{balance_info['currency']}.\n\n"   
                                )
                            else:
                                yield f"data: Nie znaleziono konta dla podanego ID użytkownika.\n\n"

                        if function_name == "get_user_info":
                            #user_id = arguments.get("user_id")
                            print("### Called get_user_info ###")
                            user_info = get_user_info(user_id)
                            if user_info:
                                yield (
                                    f"data: Nazywasz się {user_info['name']} "
                                    f"i masz {user_info['age'] } lat.\n\n"

                                )

                            else:
                                yield f"data: Nie znaleziono użytkownika dla podanego ID.\n\n"
                        if function_name == "get_todays_games":
                            print("### Called get_todays_games ###")
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
            yield "data: Wystąpił błąd podczas przetwarzania Twojej prośby. Proszę spróbować ponownie później.\n\n"
    return Response(generate(), content_type="text/event-stream")

if __name__ == "__main__":
    app.run(debug=True)
