// Load the NovaChat script
(function() {
    const script = document.createElement('script');
    script.src = 'YOUR_DOMAIN/static/chatbot.js';
    script.onload = function() {
        // Initialize the chat widget with your API endpoint
        new NovaChat('YOUR_DOMAIN/chat');
    };
    document.head.appendChild(script);
})(); 