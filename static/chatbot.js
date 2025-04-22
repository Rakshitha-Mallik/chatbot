class NovaChat {
    constructor(apiUrl) {
        this.apiUrl = apiUrl;
        this.createChatWidget();
        this.isOpen = false;
    }

    createChatWidget() {
        // Create chat widget container
        const chatWidget = document.createElement('div');
        chatWidget.innerHTML = `
            <style>
                .nova-chat-widget {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    z-index: 1000;
                    font-family: Arial, sans-serif;
                }
                .nova-chat-button {
                    width: 60px;
                    height: 60px;
                    border-radius: 50%;
                    background: #2196F3;
                    cursor: pointer;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: transform 0.3s ease;
                }
                .nova-chat-button:hover {
                    transform: scale(1.1);
                }
                .nova-chat-window {
                    position: fixed;
                    bottom: 90px;
                    right: 20px;
                    width: 350px;
                    height: 500px;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                    display: none;
                    flex-direction: column;
                }
                .nova-chat-header {
                    padding: 15px;
                    background: #2196F3;
                    color: white;
                    border-radius: 10px 10px 0 0;
                }
                .nova-chat-messages {
                    flex-grow: 1;
                    padding: 15px;
                    overflow-y: auto;
                }
                .nova-chat-input {
                    padding: 15px;
                    border-top: 1px solid #eee;
                    display: flex;
                }
                .nova-chat-input input {
                    flex-grow: 1;
                    padding: 8px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    margin-right: 8px;
                }
                .nova-chat-input button {
                    padding: 8px 15px;
                    background: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }
                .message {
                    margin-bottom: 10px;
                    padding: 8px 12px;
                    border-radius: 15px;
                    max-width: 80%;
                }
                .user-message {
                    background: #E3F2FD;
                    margin-left: auto;
                }
                .bot-message {
                    background: #F5F5F5;
                }
            </style>
            <div class="nova-chat-widget">
                <div class="nova-chat-button">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                        <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
                    </svg>
                </div>
                <div class="nova-chat-window">
                    <div class="nova-chat-header">
                        Chat with Nova
                    </div>
                    <div class="nova-chat-messages"></div>
                    <div class="nova-chat-input">
                        <input type="text" placeholder="Type your message...">
                        <button>Send</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(chatWidget);

        // Add event listeners
        const button = chatWidget.querySelector('.nova-chat-button');
        const window = chatWidget.querySelector('.nova-chat-window');
        const input = chatWidget.querySelector('input');
        const sendButton = chatWidget.querySelector('button');
        const messagesContainer = chatWidget.querySelector('.nova-chat-messages');

        button.addEventListener('click', () => {
            this.isOpen = !this.isOpen;
            window.style.display = this.isOpen ? 'flex' : 'none';
            if (this.isOpen && !messagesContainer.querySelector('.message')) {
                this.addMessage("Hi! I'm Nova, your friendly AI assistant. How can I help you today?", false);
            }
        });

        const sendMessage = () => {
            const message = input.value.trim();
            if (message) {
                this.addMessage(message, true);
                this.sendToAPI(message);
                input.value = '';
            }
        };

        sendButton.addEventListener('click', sendMessage);
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }

    addMessage(text, isUser) {
        const messagesContainer = document.querySelector('.nova-chat-messages');
        const message = document.createElement('div');
        message.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        message.textContent = text;
        messagesContainer.appendChild(message);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    async sendToAPI(message) {
        try {
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message }),
            });

            const data = await response.json();
            if (data.response) {
                this.addMessage(data.response, false);
            } else {
                this.addMessage('Sorry, I encountered an error. Please try again.', false);
            }
        } catch (error) {
            console.error('Error:', error);
            this.addMessage('Sorry, I encountered an error. Please try again.', false);
        }
    }
} 