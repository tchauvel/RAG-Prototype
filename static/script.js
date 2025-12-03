document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const chatContainer = document.getElementById('chat-container');

    // Enable/disable send button based on input
    userInput.addEventListener('input', () => {
        sendBtn.disabled = userInput.value.trim() === '';
    });

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = userInput.value.trim();
        if (!query) return;

        // Add user message
        addMessage(query, 'user');
        userInput.value = '';
        sendBtn.disabled = true;

        // Show typing indicator
        const typingIndicator = showTypingIndicator();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query }),
            });

            const data = await response.json();

            // Remove typing indicator
            typingIndicator.remove();

            if (data.error) {
                addMessage(`Error: ${data.error}`, 'bot');
            } else {
                let messageText = data.answer;
                if (data.sources && data.sources.length > 0) {
                    messageText += '<br><br><small><strong>Sources:</strong> ' + data.sources.join(', ') + '</small>';
                }
                addMessage(messageText, 'bot');
            }
        } catch (error) {
            typingIndicator.remove();
            addMessage('Sorry, something went wrong. Please try again.', 'bot');
            console.error('Error:', error);
        }
    });

    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);

        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');

        // Auto-linkify URLs (improved regex to exclude trailing punctuation)
        const urlRegex = /(https?:\/\/[^\s.,;)]+)/g;
        const htmlContent = text.replace(urlRegex, '<a href="$1" target="_blank">$1</a>');

        // Use innerHTML to render links (be careful with XSS in production, but okay for this prototype)
        contentDiv.innerHTML = htmlContent;

        messageDiv.appendChild(contentDiv);
        chatContainer.appendChild(messageDiv);
        scrollToBottom();
    }

    function showTypingIndicator() {
        const indicatorDiv = document.createElement('div');
        indicatorDiv.classList.add('typing-indicator');

        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.classList.add('typing-dot');
            indicatorDiv.appendChild(dot);
        }

        chatContainer.appendChild(indicatorDiv);
        scrollToBottom();
        return indicatorDiv;
    }

    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
});
