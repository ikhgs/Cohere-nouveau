from flask import Flask, request, jsonify
import cohere
from dotenv import load_dotenv
import os

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Initialisation de l'API Cohere
cohere_api_key = os.getenv('COHERE_API_KEY')
co = cohere.Client(api_key=cohere_api_key)

# Création de l'application Flask
app = Flask(__name__)

# Stockage de l'historique des conversations
conversations = {}

@app.route('/chat', methods=['GET'])
def chat():
    # Récupérer les paramètres de la requête
    user_message = request.args.get('message')
    user_id = request.args.get('userId')

    if not user_message or not user_id:
        return jsonify({"error": "Veuillez fournir à la fois un message et un userId en paramètre."}), 400

    # Initialiser ou récupérer l'historique de chat pour cet utilisateur
    if user_id not in conversations:
        conversations[user_id] = [
            {"role": "User", "message": "Bonjour qui es-tu ?"},
            {"role": "Chatbot", "message": "Bonjour ! Je suis Command R, un modèle de langage d'intelligence artificielle développé par Cohere."}
        ]
    
    chat_history = conversations[user_id]

    # Ajouter le nouveau message de l'utilisateur à l'historique
    chat_history.append({"role": "User", "message": user_message})

    # Appel à l'API Cohere pour générer une réponse
    stream = co.chat_stream(
        model='command-r-08-2024',
        message=user_message,
        temperature=0.3,
        chat_history=chat_history,
        prompt_truncation='AUTO',
        connectors=[{"id": "web-search"}]
    )

    # Collecter et retourner la réponse générée
    response = ""
    for event in stream:
        if event.event_type == "text-generation":
            response += event.text

    # Ajouter la réponse du chatbot à l'historique de l'utilisateur
    chat_history.append({"role": "Chatbot", "message": response})

    # Mettre à jour l'historique de la conversation de l'utilisateur
    conversations[user_id] = chat_history

    # Ajouter le titre au-dessus de la réponse
    full_response = f"🇲🇬Bot Madagascar🇲🇬\n\n{response}"

    return jsonify({"response": full_response})

# Lancer l'application Flask, accessible depuis 0.0.0.0
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
