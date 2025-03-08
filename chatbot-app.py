# app.py
from flask import Flask, request, jsonify, render_template, send_from_directory
import os
from openai import OpenAI
import json

app = Flask(__name__)

# Route for serving the main HTML page
@app.route('/')
def index():
    return render_template('index.html')

# API endpoint for the chatbot
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    try:
        # Initialize the DeepSeek client
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            return jsonify({"error": "DEEPSEEK_API_KEY not set in environment variables"}), 500
            
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        
        # Call the DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are an expert assistant who provides concise, specific, high quality responses."},
                {"role": "user", "content": user_message},
            ],
            stream=False
        )
        
        bot_response = response.choices[0].message.content
        return jsonify({"response": bot_response})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Write the HTML to a file
    with open('templates/index.html', 'w') as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple Chatbot</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f7fb;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .chat-container {
            width: 90%;
            max-width: 600px;
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            height: 80vh;
        }
        .chat-header {
            background-color: #2c3e50;
            color: white;
            padding: 15px 20px;
            font-size: 1.2em;
            font-weight: bold;
        }
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px 15px;
            border-radius: 18px;
            max-width: 75%;
            word-wrap: break-word;
        }
        .user-message {
            background-color: #3498db;
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 5px;
        }
        .bot-message {
            background-color: #ecf0f1;
            color: #2c3e50;
            border-bottom-left-radius: 5px;
        }
        .chat-input {
            display: flex;
            padding: 15px;
            background-color: #f8f9fa;
            border-top: 1px solid #e9ecef;
        }
        #message-input {
            flex: 1;
            padding: 10px 15px;
            border: 1px solid #ced4da;
            border-radius: 20px;
            outline: none;
            font-size: 1em;
        }
        #send-button {
            background-color: #2c3e50;
            color: white;
            border: none;
            border-radius: 20px;
            padding: 10px 20px;
            margin-left: 10px;
            cursor: pointer;
            font-weight: bold;
        }
        #send-button:hover {
            background-color: #1a252f;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 10px;
            color: #666;
        }
        .dots {
            display: inline-block;
        }
        .dots span {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #666;
            margin: 0 2px;
            animation: dot-pulse 1.5s infinite;
        }
        .dots span:nth-child(2) {
            animation-delay: 0.2s;
        }
        .dots span:nth-child(3) {
            animation-delay: 0.4s;
        }
        @keyframes dot-pulse {
            0%, 100% {
                transform: scale(0.8);
                opacity: 0.6;
            }
            50% {
                transform: scale(1.2);
                opacity: 1;
            }
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">Posh AI</div>
        <div class="chat-messages" id="chat-messages">
            <div class="message bot-message">
                Hello! I'm an AI powered by Posh. How can I help you today?
            </div>
        </div>
        <div class="loading" id="loading">
            <div class="dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
        <div class="chat-input">
            <input type="text" id="message-input" placeholder="Type your message here..." autocomplete="off">
            <button id="send-button">Send</button>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const messageInput = document.getElementById('message-input');
            const sendButton = document.getElementById('send-button');
            const chatMessages = document.getElementById('chat-messages');
            const loadingIndicator = document.getElementById('loading');
            
            // Function to add a message to the chat
            function addMessage(message, isUser) {
                const messageElement = document.createElement('div');
                messageElement.classList.add('message');
                messageElement.classList.add(isUser ? 'user-message' : 'bot-message');
                messageElement.textContent = message;
                chatMessages.appendChild(messageElement);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            // Function to show loading indicator
            function showLoading() {
                loadingIndicator.style.display = 'block';
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            // Function to hide loading indicator
            function hideLoading() {
                loadingIndicator.style.display = 'none';
            }
            
            // Function to send a message to the backend
            async function sendMessage(message) {
                try {
                    showLoading();
                    
                    // Make the API call to our Flask backend
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ message: message })
                    });
                    
                    const data = await response.json();
                    
                    hideLoading();
                    
                    if (data.error) {
                        addMessage('Error: ' + data.error, false);
                    } else {
                        addMessage(data.response, false);
                    }
                    
                } catch (error) {
                    console.error('Error:', error);
                    hideLoading();
                    addMessage('Sorry, I encountered an error processing your request.', false);
                }
            }
            
            // Event listener for the send button
            sendButton.addEventListener('click', function() {
                const message = messageInput.value.trim();
                if (message) {
                    addMessage(message, true);
                    messageInput.value = '';
                    sendMessage(message);
                }
            });
            
            // Event listener for the Enter key
            messageInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    const message = messageInput.value.trim();
                    if (message) {
                        addMessage(message, true);
                        messageInput.value = '';
                        sendMessage(message);
                    }
                }
            });
            
            // Focus on the input field when the page loads
            messageInput.focus();
        });
    </script>
</body>
</html>''')
    
    print("Starting server on http://127.0.0.1:5000")
    app.run(debug=True)