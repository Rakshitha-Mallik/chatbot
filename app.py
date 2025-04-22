from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
import os
import sys, os

# Import chatbot components
from rag_chatbot import initialize_pinecone, create_qa_chain, create_guardrails, setup_logging

# Initialize Flask
app = Flask(__name__)
# Enable CORS for all routes (so the widget can iframe across domains)
CORS(app, resources={r"/*": {"origins": "*"}})
# Support for proxy servers (ngrok, Cloud Run etc.)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Setup logging and chatbot components
try:
    logger = setup_logging()
    vector_store = initialize_pinecone()
    qa_chain = create_qa_chain(vector_store)
    output_guard = create_guardrails()
    logger.info("Successfully initialized all components")
except Exception as e:
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to initialize components: {e}")

# Root: serve the chat UI
def home():
    return render_template('chat.html')

# Chat API endpoint
@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '')
        logger.info(f"User Input: {user_message}")

        # Invoke the QA chain
        result = qa_chain.invoke({"question": user_message})
        answer = result.get('answer', '')
        logger.info(f"Raw Response: {answer}")

        # Validate output via guardrails
        try:
            validated = output_guard.validate(answer)
            response = validated
            logger.info(f"Validated Response: {validated}")
        except Exception as validation_error:
            logger.warning(f"Guardrails validation failed: {validation_error}")
            response = answer

        return jsonify({"response": response})
    except Exception as e:
        logger.error(f"Error in /chat endpoint: {e}")
        return jsonify({"response": "I apologize, but I'm having trouble processing your request right now."})

# Widget test page to preview the floating icon locally
@app.route('/widget-test')
def widget_test():
    return render_template('widget-test.html')

# Register routes
app.add_url_rule('/', 'home', home)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('DEBUG', 'true').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug_mode, threaded=True)
