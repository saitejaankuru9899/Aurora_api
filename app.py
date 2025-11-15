from flask import Flask, request, jsonify
import requests

API_URL = "https://november7-730026606190.europe-west1.run.app/messages"

app = Flask(__name__)

def fetch_messages():
    try:
        url = requests.get(API_URL, timeout=5)
        url.raise_for_status()
        return url.json()
    except:
        return []

def question_answer(question, messages):
    words = question.split()
    name = None
    for word in words:
        if word[0].isupper():
            name = word
            break

    if name:
        matches = []
        for message in messages:
            text = str(message)
            if name.lower() in text.lower():
                matches.append(text)

        if matches:
            snippet = matches[0][:200]
            return f"I found something about {name}: {snippet}"

        return f"No messages found about {name}."

    # fallback if no name found
    return "I couldn't understand the question clearly."

@app.route("/ask")
def ask():
    question = request.args.get("question")
    if not question:
        return jsonify({"answer": "Please provide ?question=question"}), 400

    messages = fetch_messages()
    ans = question_answer(question, messages)
    return jsonify({"answer": ans})

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
