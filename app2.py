import os
from flask import Flask, request, jsonify, stream_with_context, Response, render_template
#from flask_cors import CORS
import openai
#import json
from dotenv import load_dotenv

# Ładowanie klucza OpenAI
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


app = Flask(__name__)

# Strona główna
@app.route("/")
def index():
    return render_template("index.html")

# Endpoint do strumieniowania odpowiedzi
@app.route("/stream", methods=["POST"])
def stream():
    user_input = request.json.get("message")  # Pobieranie danych JSON
    if not user_input:
        return Response("Brak wiadomości", status=400)

    # Funkcja generatora do przesyłania strumienia
    def generate():
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                    {"role": "system",
                    "content": "Jesteś asystentem gracza odpowiedzialnym za zachęcanie do składania zakładów bukmacherskich. Jesteś w tym najlepszy i najskuteczniejszy. Namawiasz w sposób wysublimowany i nienachalny. Masz na imię Albert. Wyrażasz się w sposób zwięzły i konkretny."},
                    {"role": "user", "content": user_input}
                ],
            temperature=0.1,
            max_tokens=100,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
#            functions=functions,
#            function_call="auto",
            stream = True
        )
        for chunk in response:
            if "choices" in chunk and len(chunk["choices"]) > 0:
                delta = chunk["choices"][0].get("delta", {}).get("content", "")
                yield f"data: {delta}\n\n"  # SSE format

    return Response(generate(), content_type="text/event-stream")

if __name__ == "__main__":
    app.run(debug=True)
